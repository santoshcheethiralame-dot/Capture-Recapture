"""Closed-population estimators for incidence (detection-history) data.

`X` is a binary matrix of shape (n_observed, K): X[i, j] = 1 if individual i
was caught on occasion j. Rows that are all zero are ignored.
"""

import numpy as np
from scipy.optimize import brentq


def _freq_counts(X):
    X = X[X.sum(axis=1) > 0]
    f = np.bincount(X.sum(axis=1), minlength=X.shape[1] + 1)
    return X, f  # f[k] = number of individuals caught exactly k times


def chapman(X, a=0, b=1):
    """Chapman's bias-corrected Lincoln-Petersen estimator on occasions a and b."""
    n1, n2 = X[:, a].sum(), X[:, b].sum()
    m = (X[:, a] & X[:, b]).sum()
    return (n1 + 1) * (n2 + 1) / (m + 1) - 1


def darroch_mt(X):
    """MLE under model Mt (occasion-varying capture probability, no heterogeneity)."""
    X, _ = _freq_counts(X)
    S, n = X.shape[0], X.sum(axis=0)
    if X.sum() == S:  # no recaptures at all
        return np.inf
    g = lambda N: np.prod(1 - n / N) - (1 - S / N)
    hi = S * 1e6
    return brentq(g, S + 1e-9, hi) if g(S + 1e-9) * g(hi) < 0 else np.inf


def chao2(X):
    """Bias-corrected Chao2 lower-bound estimator."""
    X, f = _freq_counts(X)
    K, S = X.shape[1], X.shape[0]
    return S + (K - 1) / K * f[1] * (f[1] - 1) / (2 * (f[2] + 1))


def ichao2(X):
    """Improved Chao2 (Chiu et al. 2014); needs K >= 4."""
    X, f = _freq_counts(X)
    K = X.shape[1]
    if K < 4:
        return np.nan
    q1, q2, q3, q4 = f[1], f[2], f[3], max(f[4], 1)
    extra = (K - 3) / (4 * K) * q3 / q4 * max(q1 - (K - 3) / (2 * (K - 1)) * q2 * q3 / q4, 0)
    return chao2(X) + extra


def jackknife(X, order=1):
    """Burnham-Overton jackknife (first or second order) for model Mh."""
    X, f = _freq_counts(X)
    K, S = X.shape[1], X.shape[0]
    if order == 1:
        return S + f[1] * (K - 1) / K
    return S + f[1] * (2 * K - 3) / K - f[2] * (K - 2) ** 2 / (K * (K - 1))


ESTIMATORS = {
    "Chapman (2 occ.)": chapman,
    "Mt (Darroch)": darroch_mt,
    "Chao2": chao2,
    "iChao2": ichao2,
    "Jackknife-1": lambda X: jackknife(X, 1),
    "Jackknife-2": lambda X: jackknife(X, 2),
}
