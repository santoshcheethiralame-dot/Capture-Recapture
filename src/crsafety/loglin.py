"""Log-linear closed-population models (Fienberg 1972; Cormack 1989; Rivest 2011).

A Poisson regression on the 2^K - 1 observable detection-history counts.
The unobservable all-zero history has expected count exp(intercept), so
N_hat = S + exp(intercept). Matched exactly to R ``Rcapture`` (E00-R003):

- ``closedp.t`` models M0, Mt, Mb, Mbh, and Mh / Mth with heterogeneity of
  type Chao (LB), Poisson (theta = 2), Darroch and Gamma (theta = 3.5);
- ``closedpCI.t`` with an ``mX`` formula: run main effects plus chosen
  interactions between runs, i.e. explicit list dependence.

History order, design columns and the "drop negative eta" refits for the
Chao (LB) models follow Rcapture's ``histpos.t``, ``Xclosedp`` and
``Chao.neg``. Use these models when runs may be dependent: an interaction
term absorbs the dependence between the runs it names (Sun et al. 2023 for
robust intervals). Heterogeneity models are still lower bounds when
detectability is uneven in ways the model does not describe.
"""

from itertools import combinations

import numpy as np
from scipy.special import gammaln

from .estimators import IncidenceData, _data, _need_matrix

HETEROGENEITY = ("Chao", "Poisson", "Darroch", "Gamma")
CLOSEDP_MODELS = ("M0", "Mt", "Mh Chao (LB)", "Mh Poisson2", "Mh Darroch", "Mh Gamma3.5",
                  "Mth Chao (LB)", "Mth Poisson2", "Mth Darroch", "Mth Gamma3.5", "Mb", "Mbh")


def histories(K):
    """All 2^K - 1 non-empty detection histories, in Rcapture ``histpos.t`` order.

    Row r has run j (0-based) detected iff bit (K - 1 - j) of r is 0, so the
    first row is all ones and the last is (0, ..., 0, 1).
    """
    r = np.arange(2**K - 1)[:, None]
    return 1 - ((r >> (K - 1 - np.arange(K))) & 1)


def history_counts(X):
    """Number of items with each history, aligned with :func:`histories`."""
    M = _need_matrix(_data(X), "history_counts")
    K = M.shape[1]
    idx = ((1 - M) * (2 ** (K - 1 - np.arange(K)))).sum(axis=1)
    return np.bincount(idx, minlength=2**K)[: 2**K - 1].astype(float)


def _heterogeneity_columns(h, nbcap, K, theta):
    if h == "Chao":
        if K < 3:
            return np.zeros((nbcap.size, 1)), ["eta"]
        return (np.column_stack([np.maximum(nbcap - j + 1, 0) for j in range(3, K + 1)]),
                [f"eta{j}" for j in range(3, K + 1)])
    if h == "Poisson":
        col = theta**nbcap - 1.0
    elif h == "Darroch":
        col = nbcap**2 / 2.0
    elif h == "Gamma":
        col = -np.log(theta + nbcap) + np.log(theta)
    else:
        raise ValueError(f"heterogeneity must be one of {HETEROGENEITY}")
    return col[:, None].astype(float), ["tau"]


def design(K, model="Mt", heterogeneity=None, theta=None, interactions=()):
    """Design matrix (without intercept) and column names, as Rcapture builds it.

    ``model`` is "M0", "Mt", "Mb", "Mbh", or "none" (no main effects; only
    useful with ``interactions``). ``interactions`` is a list of tuples of
    0-based run indices, each adding the product column of those runs
    (``closedpCI.t`` formula terms such as ``c1:c2``). Lower-order terms are
    not added automatically.
    """
    H = histories(K).astype(float)
    nbcap = H.sum(axis=1)
    if model in ("M0", "Mh"):
        cols, names = nbcap[:, None], ["beta"]
    elif model in ("Mt", "Mth"):
        cols, names = H, [f"beta{j + 1}" for j in range(K)]
    elif model in ("Mb", "Mbh"):
        before = np.repeat(K - np.arange(K, 0, -1), 2 ** (np.arange(K, 0, -1) - 1)).astype(float)
        cols, names = np.column_stack([before, nbcap - 1]), ["beta1", "beta2"]
        if model == "Mbh":
            cols, names = np.column_stack([1 - H[:, 0], cols]), ["eta"] + names
    elif model == "none":
        cols, names = np.empty((H.shape[0], 0)), []
    else:
        raise ValueError(f"unknown model {model!r}")
    extra = []
    for term in interactions:
        term = tuple(sorted(term))
        extra.append(np.prod(H[:, term], axis=1))
        names = names + ["lambda" + "".join(str(j + 1) for j in term)]
    if extra:
        cols = np.column_stack([cols] + extra)
    if heterogeneity is not None:
        hc, hn = _heterogeneity_columns(heterogeneity, nbcap, K, theta)
        cols, names = np.column_stack([cols, hc]), names + hn
    return cols, names


def _poisson_fit(Y, D, tol=1e-13, maxit=200):
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        return _poisson_fit_(Y, D, tol, maxit)


def _poisson_fit_(Y, D, tol, maxit):
    """Poisson GLM by Newton-Raphson (IRLS) with log link; D includes the intercept.

    Columns that are exactly collinear with earlier ones are dropped (as R
    does by returning NA). Returns (coef, cov, mu, converged, kept columns).
    """
    r = np.linalg.qr(D, mode="r")
    keep = np.abs(np.diag(r)) > 1e-7 * np.abs(np.diag(r)).max()
    A = D[:, keep]
    # R's starting values for poisson: mu = y + 0.1, eta = log(mu); one WLS step from there.
    mu = Y + 0.1
    z = np.log(mu)
    beta = np.linalg.lstsq(A * np.sqrt(mu)[:, None], z * np.sqrt(mu), rcond=None)[0]
    dev_old, converged = np.inf, False
    for _ in range(maxit):
        eta = A @ beta
        mu = np.exp(np.minimum(eta, 700))
        dev = 2 * np.sum(np.where(Y > 0, Y * np.log(np.where(Y > 0, Y, 1) / mu), 0.0) - (Y - mu))
        if abs(dev - dev_old) <= tol * (abs(dev) + 0.1):
            converged = True
            break
        dev_old = dev
        # Weighted least squares step. lstsq (not solve) keeps going when some
        # fitted cells head to 0, as R's glm does for counts that are all 0.
        sw = np.sqrt(mu)
        beta = np.linalg.lstsq(A * sw[:, None], (eta + (Y - mu) / mu) * sw, rcond=None)[0]
    mu = np.exp(A @ beta)
    cov = np.linalg.pinv(A.T @ (A * mu[:, None]), hermitian=True)
    return beta, cov, mu, converged, keep


def _fit_summary(Y, beta, mu, n):
    dev = 2 * np.sum(np.where(Y > 0, Y * np.log(np.where(Y > 0, Y, 1) / mu), 0.0) - (Y - mu))
    loglik = np.sum(Y * np.log(mu) - mu - gammaln(Y + 1))
    k = beta.size
    return dict(deviance=float(dev), df=int(Y.size - k), aic=float(-2 * loglik + 2 * k),
                bic=float(-2 * loglik + np.log(n) * k))


def loglinear(X, model="Mt", heterogeneity=None, theta=None, interactions=(), neg=True):
    """Fit one log-linear model and return N_hat with its standard error.

    ``heterogeneity``: None, "Chao" (Chao's lower-bound model, with negative
    eta parameters removed one at a time as in Rcapture when ``neg``),
    "Poisson" (theta default 2), "Darroch", or "Gamma" (theta default 3.5).

    Returns a dict with N, se, deviance, df, aic, bic, coef (named),
    converged and, for Chao models, the eta parameters removed. For "Mb" and
    "Mbh", N and its s.e. use Rcapture's closed forms.
    """
    d = _data(X)
    M = _need_matrix(d, "loglinear")
    K, n = M.shape[1], d.S
    if heterogeneity == "Poisson" and theta is None:
        theta = 2.0
    if heterogeneity == "Gamma" and theta is None:
        theta = 3.5
    Y = history_counts(d)
    cols, names = design(K, model, heterogeneity, theta, interactions)
    D = np.column_stack([np.ones(Y.size), cols])
    names = ["Intercept"] + names
    beta, cov, mu, conv, keep = _poisson_fit(Y, D)
    removed = []
    if heterogeneity == "Chao" and neg:
        n_het = sum(nm.startswith("eta") for nm in names) - (model == "Mbh")
        nca = len(names) - n_het  # intercept + all non-heterogeneity columns (Rcapture's nca)
        while True:
            kept_names = [nm for nm, k in zip(names, keep) if k]
            etas = [(i, nm) for i, nm in enumerate(kept_names) if i >= nca and beta[i] < 0]
            if not etas:
                break
            removed.append(etas[0][1])
            idx = [i for i, nm in enumerate(names) if nm != etas[0][1]]
            D, names = D[:, idx], [names[i] for i in idx]
            beta, cov, mu, conv, keep = _poisson_fit(Y, D)
    kept_names = [nm for nm, k in zip(names, keep) if k]
    out = _fit_summary(Y, beta, mu, n)
    b = dict(zip(kept_names, beta))
    if model == "Mb":
        e1, e2, e3 = np.exp(beta[:3])
        N = e1 * (1 + e3) ** K / (1 + e3 - e2)
        v = N * np.array([1, e2 / (1 + e3 - e2), K * e3 / (1 + e3) - e3 / (1 + e3 - e2)])
        se = np.sqrt(v @ cov @ v - N)
    elif model == "Mbh":
        a, eta, b1, b2 = beta[:4]  # intercept, eta, beta1, beta2
        den = 1 + np.exp(b2) - np.exp(b1)
        scale = np.exp(a) * (1 + np.exp(b2)) ** (K - 1)
        N = scale * (1 + np.exp(eta + b1) / den)
        v = scale * np.array([
            1 + np.exp(eta + b1) / den,
            np.exp(eta + b1) / den,
            np.exp(eta + b1) / den + np.exp(eta + 2 * b1) / den**2,
            (K - 1) * np.exp(b2) / (1 + np.exp(b2)) - np.exp(eta + b1 + b2) / den**2,
        ])
        se = np.sqrt(v @ cov @ v - N)
    else:
        f0 = np.exp(beta[0])
        N = n + f0
        se = np.sqrt(f0 + f0**2 * cov[0, 0])
    out.update(N=float(N), se=float(se), coef=b, converged=bool(conv), eta_removed=removed,
               not_estimable=[nm for nm, k in zip(names, keep) if not k])
    return out


def closedp(X):
    """All Rcapture ``closedp.t`` models (M0, Mt, Mb only when K = 2).

    Returns {model name: result dict} with names as in Rcapture.
    """
    d = _data(X)
    K = _need_matrix(d, "closedp").shape[1]
    specs = {
        "M0": ("M0", None), "Mt": ("Mt", None),
        "Mh Chao (LB)": ("Mh", "Chao"), "Mh Poisson2": ("Mh", "Poisson"),
        "Mh Darroch": ("Mh", "Darroch"), "Mh Gamma3.5": ("Mh", "Gamma"),
        "Mth Chao (LB)": ("Mth", "Chao"), "Mth Poisson2": ("Mth", "Poisson"),
        "Mth Darroch": ("Mth", "Darroch"), "Mth Gamma3.5": ("Mth", "Gamma"),
        "Mb": ("Mb", None), "Mbh": ("Mbh", None),
    }
    names = ("M0", "Mt", "Mb") if K == 2 else CLOSEDP_MODELS
    out = {}
    for nm in names:
        m, h = specs[nm]
        try:
            out[nm] = loglinear(d, m, h)
        except (np.linalg.LinAlgError, FloatingPointError) as e:
            out[nm] = dict(N=np.nan, se=np.nan, error=str(e))
    return out


def pairwise_terms(K, pairs=None):
    """Helper: all run pairs (or the given ones) as interaction terms."""
    return list(combinations(range(K), 2)) if pairs is None else [tuple(p) for p in pairs]
