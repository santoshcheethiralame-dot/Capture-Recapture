"""Identity errors with match scores, and corrections for them (E05).

Record-level model (E05 §2a). Each item's first detection (in run order)
anchors it. Every later detection (a *recapture*) gets a match score
s ~ N(m_i, 1) and is linked to its item iff s >= 0; m_i = Phi^-1(1 - f_i), so
the false non-match ("ghost") rate is exactly f_i. An unlinked recapture
becomes a singleton row whose best candidate is its true item, at score s < 0.
A true singleton's best candidate is a non-match, at a score drawn from
N(m_0, 1) truncated below 0. Merges join round(g * S) random pairs of
observed rows; each merge is a false link with score N(0.5, 1) truncated
above 0.

Corrections take the observed matrix plus what an analyst could know:
scores, and truth labels for a sample of candidate pairs.
"""

from dataclasses import dataclass

import numpy as np
from scipy.optimize import nnls
from scipy.special import comb
from scipy.stats import norm, truncnorm

from .estimators import IncidenceData, chao2, chao2_ci, coverage

M0 = -2.5      # mean score of a non-match candidate
M_MERGE = 0.5  # mean score of a false link


@dataclass
class Linked:
    X: np.ndarray        # observed rows x K
    truth: np.ndarray    # true item of each observed row (-1 never; ghosts keep their item)
    is_ghost: np.ndarray  # row is an unlinked recapture
    cand: np.ndarray     # singleton rows: row index of the best candidate (-1 otherwise)
    cand_score: np.ndarray  # singleton rows: score of the best candidate (nan otherwise)
    pairs_score: np.ndarray  # every candidate pair's score (links, then singleton candidates)
    pairs_true: np.ndarray   # whether each candidate pair is a true match
    n_merges: int


def inject(X, f, g, rng, pattern="uniform", p=None):
    """Apply ghosts (per recapture) then merges (per observed row) with scores.

    ``X`` is the true items x runs matrix (undetected rows allowed). With
    ``pattern="score"``, f_i is proportional to 1 / sqrt(p_i) (``p`` aligned
    with the rows of X), rescaled so that the share of all recaptures left
    unlinked is f, and capped at 0.95.
    """
    det = X.any(axis=1)
    X = X[det].astype(np.int8)
    p = None if p is None else np.asarray(p, float)[det]
    S, K = X.shape
    first = X.argmax(axis=1)
    recap = X.copy()
    recap[np.arange(S), first] = 0  # recaptures only
    n_rec = recap.sum(axis=1)
    if pattern == "uniform" or f == 0:
        fi = np.full(S, float(f))
    else:
        w = 1 / np.sqrt(np.maximum(p if p is not None else np.ones(S), 1e-6))
        fi = np.minimum(w * f * n_rec.sum() / max((w * n_rec).sum(), 1e-12), 0.95)
    m = norm.ppf(1 - np.clip(fi, 1e-12, 1 - 1e-12))
    rows, truth, ghost, cand, cscore = [], [], [], [], []
    link_scores, link_true = [], []
    main = X.copy()
    for i, j in zip(*np.nonzero(recap)):
        s = rng.normal(m[i])
        if s >= 0:
            link_scores.append(s)
            link_true.append(True)
        else:
            main[i, j] = 0
            r = np.zeros(K, np.int8)
            r[j] = 1
            rows.append(r)
            truth.append(i)
            ghost.append(True)
            cand.append(i)
            cscore.append(s)
    Xo = np.vstack([main] + ([np.array(rows)] if rows else []))
    truth = np.concatenate([np.arange(S), np.array(truth, int)])
    is_ghost = np.concatenate([np.zeros(S, bool), np.array(ghost, bool)])
    cand_arr = np.full(Xo.shape[0], -1)
    cand_score = np.full(Xo.shape[0], np.nan)
    if rows:
        cand_arr[S:] = cand
        cand_score[S:] = cscore
    single = (Xo.sum(axis=1) == 1) & ~is_ghost
    idx = np.nonzero(single)[0]
    if idx.size:
        others = rng.integers(0, Xo.shape[0] - 1, idx.size)
        cand_arr[idx] = others + (others >= idx)
        cand_score[idx] = truncnorm.rvs(-np.inf, 0 - M0, loc=M0, size=idx.size, random_state=rng)
    n_merge = int(round(g * Xo.shape[0]))
    merge_scores = []
    if n_merge:
        pick = rng.permutation(Xo.shape[0])[: 2 * n_merge].reshape(-1, 2)
        Xo[pick[:, 0]] |= Xo[pick[:, 1]]
        merge_scores = truncnorm.rvs(-M_MERGE, np.inf, loc=M_MERGE, size=n_merge, random_state=rng).tolist()
        keep = np.ones(Xo.shape[0], bool)
        keep[pick[:, 1]] = False
        remap = np.cumsum(keep) - 1
        # a candidate that was merged away now points at the row it joined
        target = np.arange(Xo.shape[0])
        target[pick[:, 1]] = pick[:, 0]
        has = cand_arr >= 0
        cand_arr[has] = remap[target[cand_arr[has]]]
        Xo, truth, is_ghost = Xo[keep], truth[keep], is_ghost[keep]
        cand_arr, cand_score = cand_arr[keep], cand_score[keep]
        single_now = Xo.sum(axis=1) == 1
        cand_arr[~single_now], cand_score[~single_now] = -1, np.nan
    single_now = Xo.sum(axis=1) == 1
    cs = cand_score[single_now & np.isfinite(cand_score)]
    ct = is_ghost[single_now & np.isfinite(cand_score)]
    pairs_score = np.concatenate([link_scores, merge_scores, cs])
    pairs_true = np.concatenate([np.ones(len(link_scores), bool), np.zeros(len(merge_scores), bool), ct])
    return Linked(Xo, truth, is_ghost, cand_arr, cand_score, pairs_score, pairs_true, n_merge)


# ---------------------------------------------------------------- error-rate estimation

BINS = (-np.inf, -2, -1, 0, 1, 2, np.inf)


def label_bins(L, n_v, rng, bins=BINS):
    """Label n_v candidate pairs, in equal numbers per score bin (stratified).

    Returns (bin edges, pairs per bin, estimated true-match rate per bin).
    """
    s, t = L.pairs_score, L.pairs_true
    b = np.digitize(s, bins[1:-1])
    nb = np.bincount(b, minlength=len(bins) - 1)
    per = max(1, n_v // max((nb > 0).sum(), 1))
    rate = np.zeros(len(nb))
    for k in np.nonzero(nb)[0]:
        members = np.nonzero(b == k)[0]
        lab = rng.choice(members, size=min(per, members.size), replace=False)
        rate[k] = t[lab].mean()
    return np.asarray(bins), nb, rate


def estimate_rates(L, n_v, rng, bins=BINS):
    """Estimate (f, g) from n_v labelled candidate pairs (:func:`label_bins`),
    weighted back by bin size.

    f_hat = estimated true matches among unlinked pairs / all true matches;
    g_hat = estimated false links / rows before merging.
    """
    return rates_from_bins(*label_bins(L, n_v, rng, bins), n_rows=L.X.shape[0])


def rates_from_bins(bins, nb, rate, n_rows):
    true_est = nb * rate
    false_est = nb * (1 - rate)
    linked = np.array([lo >= 0 for lo in bins[:-1]])
    f_hat = true_est[~linked].sum() / max(true_est.sum(), 1e-12)
    merges = false_est[linked].sum()
    return float(f_hat), float(merges / max(n_rows + merges, 1))


# ---------------------------------------------------------------- corrections

def thinning_matrix(K, f):
    """A[j-1, k-1] = P(an item with k detections keeps j | each recapture kept w.p. 1 - f).

    The first detection always stays, so j >= 1."""
    A = np.zeros((K, K))
    for k in range(1, K + 1):
        r = k - 1
        for kept in range(r + 1):
            A[kept, k - 1] = comb(r, kept) * (1 - f) ** kept * f ** (r - kept)
    return A


def correct_Q(Q, U, K, f_hat):
    """First-order ghost correction of frequency counts Q = (Q_1..Q_K).

    Ghosts conserve detections (U is the true total), and
    E[observed Q] = A(f) Q_true + e_1 * f * (U - S_true): every true
    recapture is lost with probability f and becomes a singleton. Solved for
    Q_true >= 0 by non-negative least squares, iterating on S_true.
    """
    Q = np.asarray(Q, float)
    if f_hat <= 0:
        return Q.copy()
    A = thinning_matrix(K, f_hat)
    S_true = Q.sum()
    for _ in range(100):
        rhs = Q.copy()
        rhs[0] -= f_hat * (U - S_true)
        Qt, _ = nnls(A, rhs)
        if abs(Qt.sum() - S_true) < 1e-10:
            break
        S_true = Qt.sum()
    return Qt


def correct_counts(d, f_hat):
    """:func:`correct_Q` applied to an :class:`IncidenceData`."""
    Q = np.bincount(d.y, minlength=d.K + 1)[1:]
    return correct_Q(Q, d.U, d.K, f_hat)


def counts_to_data(Q, K):
    """Fractional counts -> per-item counts for the count-based estimators (rounded)."""
    Qr = np.round(Q).astype(int)
    y = np.repeat(np.arange(1, K + 1), np.maximum(Qr, 0))
    return IncidenceData.from_counts(y, K)


def corrected_estimates(d, f_hat):
    """Chao2 and coverage from ghost-corrected frequency counts (correction b)."""
    Qt = correct_counts(d, f_hat)
    e = counts_to_data(Qt, d.K)
    return dict(chao2=chao2(e), coverage=coverage(e), S=float(Qt.sum()))


def _over_pairs(fn, X, a, b):
    if a is not None:
        return fn(a, b)
    K = X.shape[1]
    vals = [fn(i, j) for i in range(K) for j in range(i + 1, K)]
    return float(np.mean(vals))


def lp_corrected(X, f_hat, a=None, b=None):
    """Lincoln-Petersen with the ghost correction LP * (1 - f_hat)
    (Di Consiglio and Tuoto 2015 with no false links). On runs a, b, or
    averaged over all run pairs (default; E05 §2a)."""
    def one(i, j):
        n1, n2 = X[:, i].sum(), X[:, j].sum()
        m = (X[:, i] & X[:, j]).sum()
        return np.inf if m == 0 else n1 * n2 / m * (1 - f_hat)
    return _over_pairs(one, X, a, b)


def dct_petersen(X, lam, beta, a=None, b=None):
    """Di Consiglio-Tuoto linkage-error-corrected Petersen:
    E[m*] = lam m + beta (n2 - m)  =>  m = (m* - beta n2) / (lam - beta).
    On runs a, b, or averaged over all run pairs (default)."""
    def one(i, j):
        n1, n2 = X[:, i].sum(), X[:, j].sum()
        ms = (X[:, i] & X[:, j]).sum()
        m = (ms - beta * n2) / (lam - beta)
        return np.inf if m <= 0 else n1 * n2 / m
    return _over_pairs(one, X, a, b)


def _mixture_posterior(s, iters=200):
    """Two-component Gaussian mixture by EM; posterior of the higher-mean component."""
    s = np.asarray(s, float)
    if s.size < 4:
        return np.zeros(s.size)
    mu = np.quantile(s, [0.25, 0.9])
    sd = np.full(2, s.std() + 1e-6)
    w = np.array([0.5, 0.5])
    for _ in range(iters):
        dens = w * norm.pdf(s[:, None], mu, sd)
        r = dens / np.maximum(dens.sum(axis=1, keepdims=True), 1e-300)
        nk = r.sum(axis=0) + 1e-12
        w = nk / nk.sum()
        mu_new = (r * s[:, None]).sum(axis=0) / nk
        sd = np.sqrt((r * (s[:, None] - mu_new) ** 2).sum(axis=0) / nk) + 1e-6
        if np.allclose(mu_new, mu, atol=1e-10):
            mu = mu_new
            break
        mu = mu_new
    hi = int(np.argmax(mu))
    dens = w * norm.pdf(s[:, None], mu, sd)
    return dens[:, hi] / np.maximum(dens.sum(axis=1), 1e-300)


def mi_estimates(L, M, rng, labelled=None):
    """Multiple imputation over matchings (correction e).

    Each observed singleton is relinked to its best candidate with its
    probability of being a true match: by default from a two-component
    mixture on the singletons' best-candidate scores (E05 §2 (e)); with
    ``labelled`` (the output of :func:`label_bins`), from the labelled
    true-match rate of the singleton's score bin (E05 §2a, after the pilot). Returns Rubin's-rules mean and
    total variance for Chao2 (log-normal se as within-variance) and the mean
    and between-imputation variance for coverage.
    """
    X = L.X
    single = np.nonzero((X.sum(axis=1) == 1) & (L.cand >= 0))[0]
    if labelled is None:
        post = _mixture_posterior(L.cand_score[single])
    else:  # (bins, nb, rate) from label_bins: calibrated match probability per score bin
        bins, _, rate = labelled
        post = rate[np.digitize(L.cand_score[single], bins[1:-1])]
    ests, wvar, covs = [], [], []
    for _ in range(M):
        Xi = X.copy()
        relink = single[rng.random(single.size) < post]
        drop = np.zeros(X.shape[0], bool)
        for r in relink:
            c = L.cand[r]
            if not drop[c]:
                Xi[c] |= Xi[r]
                drop[r] = True
        e = IncidenceData.from_matrix(Xi[~drop])
        est, se, _, _ = chao2_ci(e)
        ests.append(est)
        wvar.append(se**2)
        covs.append(coverage(e))
    ests, covs = np.array(ests), np.array(covs)
    B = ests.var(ddof=1) if M > 1 else 0.0
    return dict(chao2=float(ests.mean()), chao2_var=float(np.mean(wvar) + (1 + 1 / M) * B),
                coverage=float(covs.mean()), coverage_between_var=float(covs.var(ddof=1)) if M > 1 else 0.0,
                mean_posterior=float(post.mean()) if post.size else 0.0)
