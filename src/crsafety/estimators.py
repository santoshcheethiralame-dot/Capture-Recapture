"""Closed-population estimators for incidence data (items × runs).

Every estimator accepts either a binary detection matrix ``X`` (rows are
items, columns are runs) or an :class:`IncidenceData` object. Some estimators
only need the per-item detection counts ``y`` and the number of runs ``K``
(iNEXT's "incidence_freq" format); those also accept
``IncidenceData.from_counts``.

Notation follows Chao et al. (2014): ``T`` (here ``K``) sampling units,
``Q_k`` items detected in exactly ``k`` units, ``U`` total incidences,
``S`` items detected at least once.

Formulas are matched to reference implementations in E00:
- Chao2, its log-normal CI, coverage and extrapolation: R ``iNEXT``;
- jackknife: R ``vegan::specpool``;
- ICE and iChao2: SpadeR (Chao lab) ``SpecInciModelh`` / ``SpecInciiChao2``.
  ``fossil::ICE`` uses a different, non-standard formula and is not used;
- Darroch Mt: R ``Rcapture::closedp.t``;
- Huggins: R ``VGAM::vglm`` with ``posbernoulli.t(parallel.t = TRUE ~ z)``.
"""

from dataclasses import dataclass
from itertools import combinations

import numpy as np
from scipy.optimize import brentq, minimize


@dataclass(frozen=True)
class IncidenceData:
    """Per-item detection counts ``y`` (all > 0) over ``K`` runs.

    ``X`` is kept when available (needed by Chapman, Mt, ICE, Huggins).
    """

    y: np.ndarray
    K: int
    X: np.ndarray | None = None

    @classmethod
    def from_matrix(cls, X):
        X = np.asarray(X).astype(np.int8)
        if X.ndim != 2:
            raise ValueError("X must be items × runs")
        if not np.isin(X, (0, 1)).all():
            raise ValueError("X must be binary")
        X = X[X.sum(axis=1) > 0]
        return cls(y=X.sum(axis=1).astype(int), K=X.shape[1], X=X)

    @classmethod
    def from_counts(cls, y, K):
        y = np.asarray(y, dtype=int)
        y = y[y > 0]
        if (y > K).any():
            raise ValueError("a count exceeds K")
        return cls(y=y, K=int(K))

    @property
    def S(self):
        return int(self.y.size)

    @property
    def U(self):
        return int(self.y.sum())

    def Q(self, k):
        """Number of items detected in exactly k runs."""
        return int((self.y == k).sum())


def _data(X):
    return X if isinstance(X, IncidenceData) else IncidenceData.from_matrix(X)


def _need_matrix(d, name):
    if d.X is None:
        raise ValueError(f"{name} needs the detection matrix, not just counts")
    return d.X


# ---------------------------------------------------------------- two-list

def chapman(X, a=0, b=1):
    """Chapman's bias-corrected Lincoln-Petersen estimator on runs a and b."""
    M = _need_matrix(_data(X), "chapman")
    n1, n2 = int(M[:, a].sum()), int(M[:, b].sum())
    m = int((M[:, a] & M[:, b]).sum())
    return (n1 + 1) * (n2 + 1) / (m + 1) - 1


def chapman_pairs(X):
    """Chapman estimates for every pair of runs (a dependence diagnostic)."""
    d = _data(X)
    return np.array([chapman(d, a, b) for a, b in combinations(range(d.K), 2)])


# ---------------------------------------------------------------- multi-run models

def darroch_mt(X):
    """MLE of N under model Mt (run-specific, item-constant detection).

    Root of prod_j (1 - n_j / N) = 1 - S / N (Darroch 1958). Returns inf if
    there are no recaptures.
    """
    d = _data(X)
    M = _need_matrix(d, "darroch_mt")
    n, S = M.sum(axis=0), d.S
    if M.sum() == S:
        return np.inf
    if n.max() == S:  # some run found every detected item
        return float(S)
    g = lambda N: np.sum(np.log1p(-n / N)) - np.log1p(-S / N)
    lo, hi = S * (1 + 1e-12), S * 1e8
    if g(lo) * g(hi) > 0:
        return np.inf
    return brentq(g, lo, hi, xtol=1e-10, rtol=1e-14, maxiter=500)


# ---------------------------------------------------------------- Chao family

def _f0_chao2(d, form):
    K, Q1, Q2 = d.K, d.Q(1), d.Q(2)
    A = (K - 1) / K
    if form == "bc":
        return A * Q1 * (Q1 - 1) / (2 * (Q2 + 1))
    if form == "chao2014":  # iNEXT: classic when Q2 > 0, bias-corrected otherwise
        return A * Q1**2 / (2 * Q2) if Q2 > 0 else A * Q1 * (Q1 - 1) / 2
    raise ValueError("form must be 'chao2014' or 'bc'")


def chao2(X, form="chao2014"):
    """Chao2 lower bound on the number of catchable items.

    ``form="chao2014"`` matches iNEXT (classic when Q2 > 0); ``form="bc"`` is
    the always-bias-corrected form used in the pilot.
    """
    d = _data(X)
    return d.S + _f0_chao2(d, form)


def chao2_ci(X, level=0.95):
    """Chao2 (iNEXT form) with its log-normal interval (Chao 1987).

    The interval is for the **lower bound**, not for N. Returns
    (estimate, se, lower, upper).
    """
    from scipy.stats import norm

    d = _data(X)
    S, K, Q1, Q2 = d.S, d.K, d.Q(1), d.Q(2)
    A = (K - 1) / K
    est = chao2(d)
    if Q1 > 0 and Q2 > 0:
        r = Q1 / Q2
        var = Q2 * (A / 2 * r**2 + A**2 * r**3 + A**2 / 4 * r**4)
    elif Q1 > 1 and Q2 == 0:
        var = A * Q1 * (Q1 - 1) / 2 + A**2 * Q1 * (2 * Q1 - 1) ** 2 / 4 - A**2 * Q1**4 / 4 / est
    else:
        # Too few singletons: iNEXT's fallback (estimate = S, Poisson-type CI).
        z = norm.ppf(0.5 + level / 2)
        Qk = np.bincount(d.y, minlength=K + 1)[1:]
        k = np.arange(1, K + 1)
        var = np.sum(Qk * (np.exp(-k) - np.exp(-2 * k))) - np.sum(k * np.exp(-k) * Qk) ** 2 / K
        P = np.sum(Qk * np.exp(-k)) / S
        sd = np.sqrt(max(var, 0.0))
        lo = max(S, S / (1 - P) - z * sd / (1 - P))
        hi = S / (1 - P) + z * sd / (1 - P)
        return float(S), float(sd), float(lo), float(hi)
    z = norm.ppf(0.5 + level / 2)
    t = est - S
    C = np.exp(z * np.sqrt(np.log(1 + var / t**2)))
    return est, float(np.sqrt(var)), float(S + t / C), float(S + t * C)


def ichao2(X):
    """Improved Chao2 (Chiu, Wang, Walther, Chao 2014). Needs K >= 4.

    Q4 = 0 is replaced by 1. Built on the iNEXT-form Chao2.
    """
    d = _data(X)
    K = d.K
    if K < 4:
        return np.nan
    Q1, Q2, Q3, Q4 = d.Q(1), d.Q(2), d.Q(3), max(d.Q(4), 1)
    extra = (K - 3) / (4 * K) * Q3 / Q4 * max(Q1 - (K - 3) / (2 * (K - 1)) * Q2 * Q3 / Q4, 0)
    return chao2(d) + extra


def jackknife(X, order=1):
    """Incidence jackknife (Burnham-Overton; vegan::specpool form)."""
    d = _data(X)
    K, S, Q1, Q2 = d.K, d.S, d.Q(1), d.Q(2)
    if order == 1:
        return S + Q1 * (K - 1) / K
    if order == 2:
        if K < 2:
            return np.nan
        return S + Q1 * (2 * K - 3) / K - Q2 * (K - 2) ** 2 / (K * (K - 1))
    raise ValueError("order must be 1 or 2")


def _coverage_A(d):
    """iNEXT/SpadeR term A = K f0 / (K f0 + Q1), with f0 the iNEXT Chao2 f0."""
    Q1 = d.Q(1)
    if Q1 == 0:
        return 1.0
    f0 = _f0_chao2(d, "chao2014")
    return d.K * f0 / (d.K * f0 + Q1)


def ice(X, cutoff=10):
    """Incidence-based coverage estimator, Chao lab (SpadeR) form.

    C_infreq = 1 - Q1 / N_infreq * A, and
    gamma^2 = max(S_infreq / C_infreq * K / (K - 1) * sum j(j-1) Q_j / (N_infreq (N_infreq - 1)) - 1, 0).
    """
    d = _data(X)
    y, K = d.y, d.K
    infr = y <= cutoff
    S_infr, S_freq = int(infr.sum()), int((~infr).sum())
    if S_infr == 0:
        return float(d.S)
    N_infr = int(y[infr].sum())
    Q1 = d.Q(1)
    C = 1 - Q1 / N_infr * _coverage_A(d)
    if C <= 0 or N_infr < 2:
        return np.inf
    j = np.arange(1, cutoff + 1)
    b1 = np.sum(j * (j - 1) * np.array([d.Q(k) for k in j]))
    gamma2 = max(S_infr / C * K / (K - 1) * b1 / (N_infr * (N_infr - 1)) - 1, 0.0)
    return S_freq + S_infr / C + Q1 / C * gamma2


# ---------------------------------------------------------------- coverage

def good_turing_coverage(X):
    """Turing's estimate 1 - Q1/U (incidence)."""
    d = _data(X)
    return 1.0 if d.U == 0 else 1 - d.Q(1) / d.U


def coverage(X):
    """Chao-Jost (2012) incidence sample coverage. **Primary estimand.**

    Estimated share of total detection mass held by items already found:
    the probability that an item detected in a new run is already known.
    """
    d = _data(X)
    if d.U == 0:
        return 1.0
    # Equals 1 - Q1/U * (K-1)Q1 / ((K-1)Q1 + 2 Q2) when Q2 > 0; uses the
    # bias-corrected f0 when Q2 = 0 (iNEXT ``Chat.Sam`` at t = K).
    return 1 - d.Q(1) / d.U * _coverage_A(d)


def extrapolate(X, m):
    """Expected number of NEW items if m more runs are added.

    Chao et al. (2014) incidence extrapolation with the iNEXT Chao2 f0.
    Reliable only for m up to about K (Orlitsky, Suresh and Wu 2016).
    """
    d = _data(X)
    K, Q1 = d.K, d.Q(1)
    f0 = _f0_chao2(d, "chao2014")
    if Q1 == 0 or f0 <= 0 or m <= 0:
        return 0.0
    return float(f0 * (1 - (1 - Q1 / (K * f0 + Q1)) ** m))


# ---------------------------------------------------------------- covariates

def huggins(X, Z):
    """Huggins (1989) / Alho (1990) conditional likelihood with item covariates.

    ``Z`` has one row per **detected** item (same order as the rows of X after
    removing undetected rows) and no intercept column (one is added).
    Detection is logistic in Z and constant across runs. Returns
    (N_hat, beta, converged). N_hat is the Horvitz-Thompson sum.
    """
    d = _data(X)
    Z = np.asarray(Z, dtype=float)
    if Z.ndim == 1:
        Z = Z[:, None]
    if Z.shape[0] != d.S:
        raise ValueError("Z needs one row per detected item")
    D = np.column_stack([np.ones(d.S), Z])
    y, K = d.y, d.K

    def nll(beta):
        eta = D @ beta
        logp = -np.logaddexp(0, -eta)
        log1mp = -np.logaddexp(0, eta)
        logcap = np.log(-np.expm1(K * log1mp))  # log(1 - (1-p)^K)
        return -np.sum(y * logp + (K - y) * log1mp - logcap)

    def grad(beta):
        eta = D @ beta
        p = 1 / (1 + np.exp(-eta))
        logqK = -K * np.logaddexp(0, eta)  # log (1-p)^K
        return -D.T @ (y - K * p - K * p * np.exp(logqK) / -np.expm1(logqK))

    res = minimize(nll, np.zeros(D.shape[1]), jac=grad, method="BFGS", options=dict(gtol=1e-9))
    p = 1 / (1 + np.exp(-(D @ res.x)))
    N_hat = float(np.sum(1 / (1 - (1 - p) ** K)))
    # BFGS often stops with "precision loss" at the optimum when gtol is this
    # tight, so convergence is judged by the score itself.
    converged = bool(np.max(np.abs(grad(res.x))) <= 1e-6 * d.S)
    return N_hat, res.x, converged


def generalized_chao(X, Z=None):
    """Böhning et al. (2013) generalised Chao estimator, incidence (binomial) form.

    Uses only items found once or twice. Under a binomial model over K runs
    with odds theta_i = p_i / (1 - p_i), P(found twice | found once or twice)
    has logit log((K - 1) / 2) + log theta_i, so log theta_i = [1, Z_i] beta
    is fitted by logistic regression with that offset. Then
    f0 = sum over those items of 1 / (K theta_i + K (K - 1) / 2 theta_i^2).
    Without covariates this equals classic Chao2 exactly.

    ``Z`` has one row per detected item (as in :func:`huggins`), or None.
    Returns (N_hat, beta, converged); NaN when Q1 = 0 or Q2 = 0 (no finite MLE).
    """
    d = _data(X)
    K, y = d.K, d.y
    if K < 2:
        return np.nan, np.array([]), False
    D = np.ones((d.S, 1))
    if Z is not None:
        Z = np.asarray(Z, dtype=float)
        Z = Z[:, None] if Z.ndim == 1 else Z
        if Z.shape[0] != d.S:
            raise ValueError("Z needs one row per detected item")
        D = np.column_stack([D, Z])
    low = (y == 1) | (y == 2)
    D, r = D[low], (y[low] == 2).astype(float)
    if r.sum() == 0 or r.sum() == r.size:
        return np.nan, np.full(D.shape[1], np.nan), False
    offset = np.log((K - 1) / 2)
    beta = np.zeros(D.shape[1])
    beta[0] = np.log(r.mean() / (1 - r.mean())) - offset
    converged = False
    for _ in range(100):  # Newton-Raphson for the logistic likelihood
        pr = 1 / (1 + np.exp(-(D @ beta + offset)))
        step = np.linalg.solve(D.T @ (D * (pr * (1 - pr))[:, None]), D.T @ (r - pr))
        beta += step
        if np.max(np.abs(step)) < 1e-12 * (1 + np.max(np.abs(beta))):
            converged = True
            break
    theta = np.exp(D @ beta)
    f0 = np.sum(1 / (K * theta + K * (K - 1) / 2 * theta**2))
    return float(d.S + f0), beta, converged


def betabinomial_nof1(X, return_details=False):
    """f1-free richness estimate: a beta-binomial fitted to items found >= 2 times.

    Detection counts of items found at least twice are modelled as
    Beta-Binomial(K, a, b) truncated to y >= 2 (maximum likelihood over the
    logit of the mean and the log of a + b, bounded). With P0, P1 the model probabilities of 0 and 1 detections,
    N_hat = S_{>=2} / (1 - P0 - P1); the predicted singletons are N_hat * P1.
    The observed singleton count is never used, so ghosts (spurious
    singletons) do not affect it. Exact in expectation when detectability is
    Beta-distributed. Needs K >= 4 and at least two distinct counts >= 2;
    otherwise NaN. Built as a candidate for E05 correction (d) and **not
    recommended**: on the E05 pilot worlds (K = 10) it overshoots (median
    +8% to +220% vs the oracle Chao2) and diverges toward a -> 0 on
    heavy-tailed worlds (LOG 2026-10-22). Not validated in an E00 run; do not
    use in an experiment.
    """
    from scipy.special import betaln, gammaln

    d = _data(X)
    K = d.K
    y = d.y[d.y >= 2]
    nan = (np.nan, dict()) if return_details else np.nan
    if K < 4 or y.size < 3 or np.unique(y).size < 2:
        return nan
    k = np.arange(K + 1)
    lc = gammaln(K + 1) - gammaln(k + 1) - gammaln(K - k + 1)

    def logpmf(t):  # t = (logit of the mean a / (a + b), log of a + b)
        m, c = 1 / (1 + np.exp(-t[0])), np.exp(t[1])
        a, b = m * c, (1 - m) * c
        return lc + betaln(k + a, K - k + b) - betaln(a, b)

    cnt = np.bincount(y, minlength=K + 1).astype(float)

    def nll(t):
        lp = logpmf(t)
        trunc = np.logaddexp.reduce(lp[2:])  # log P(y >= 2), computed stably
        return -(cnt[2:] * (lp[2:] - trunc)).sum()

    best = None
    for start in ((-1.5, 0.0), (-1.5, 2.0), (-0.5, 1.0), (-3.0, -1.0)):
        r = minimize(nll, np.array(start), method="L-BFGS-B", bounds=[(-12, 12), (-8, 10)])
        if best is None or r.fun < best.fun:
            best = r
    lp = logpmf(best.x)
    p0, p1 = np.exp(lp[0]), np.exp(lp[1])
    m, c = 1 / (1 + np.exp(-best.x[0])), np.exp(best.x[1])
    N = y.size / max(1 - p0 - p1, 1e-12)
    if not return_details:
        return float(d.S - d.Q(1) + N * p1 + N * p0)
    return float(d.S - d.Q(1) + N * p1 + N * p0), dict(a=float(m * c), b=float((1 - m) * c),
                                                      f1_hat=float(N * p1), f0_hat=float(N * p0),
                                                      converged=bool(best.success))


# ---------------------------------------------------------------- report

def report(X):
    """The reporting recipe (PROTOCOLS §8) as a dict, without intervals."""
    d = _data(X)
    est, se, lo, hi = chao2_ci(d)
    out = dict(
        K=d.K, S_obs=d.S, U=d.U, Q1=d.Q(1), Q2=d.Q(2), Q3=d.Q(3), Q4=d.Q(4),
        coverage=coverage(d), new_items_1xK=extrapolate(d, d.K),
        new_items_2xK=extrapolate(d, 2 * d.K),
        chao2_lower_bound=est, chao2_lb_ci=(lo, hi), ichao2=ichao2(d),
        jackknife2=jackknife(d, 2),
    )
    if d.X is not None and d.K >= 2:
        pairs = chapman_pairs(d)
        out["chapman_pairs_range"] = (float(pairs.min()), float(pairs.max()))
    return out
