"""Planted-mark calibration of detectability (E15; SH2).

Marks are planted items whose properties x_j are known whether or not any
run finds them, so their per-run detectability can be fitted with the full
binomial likelihood: y_j ~ Binomial(K, pi(x_j)), with pi logistic in x
(:func:`fit_detectability`). For real items, only the found ones are seen;
their predicted pi_i turns into Horvitz-Thompson estimates
(:func:`calibrated`):

  N_hat = sum_found 1 / (1 - (1 - pi_i)^K)
  C_cal = sum_found pi_i / sum_found pi_i / (1 - (1 - pi_i)^K)
  Delta_cal(m) = sum_found (1 - pi_i)^K / (1 - (1 - pi_i)^K) * (1 - (1 - pi_i)^m)

C_cal is the share of detectability mass held by the found items, the same
estimand as Chao-Jost coverage. Real items' covariates are usually measured
with error (an SAE latent's firing frequency stands in for the feature's).
:func:`proxy_map` fits the mapping from observed to true covariates on the
found marks, where both are known, and applies it to real items.
:func:`calibrated_interval` bootstraps marks (refitting pi) and real items
together.
"""

import numpy as np
from scipy.optimize import minimize


def _design(Z):
    Z = np.asarray(Z, float)
    Z = Z[:, None] if Z.ndim == 1 else Z
    return np.column_stack([np.ones(Z.shape[0]), Z])


def fit_detectability(Z, y, K):
    """Logistic per-run detectability from marks: y_j found in K runs, covariates Z_j.

    Returns (beta, converged). Uses every mark, found or not."""
    D, y = _design(Z), np.asarray(y, float)

    def nll(b):
        eta = D @ b
        return -np.sum(y * -np.logaddexp(0, -eta) + (K - y) * -np.logaddexp(0, eta))

    def grad(b):
        p = 1 / (1 + np.exp(-(D @ b)))
        return -D.T @ (y - K * p)

    res = minimize(nll, np.zeros(D.shape[1]), jac=grad, method="BFGS", options=dict(gtol=1e-10))
    ok = bool(np.max(np.abs(grad(res.x))) <= 1e-6 * max(len(y), 1) * K)
    return res.x, ok


def predict(beta, Z):
    return 1 / (1 + np.exp(-(_design(Z) @ beta)))


def calibrated(pi, K, m=None):
    """Horvitz-Thompson N_hat, C_cal and (with m) Delta_cal(m) from the found items' pi."""
    pi = np.clip(np.asarray(pi, float), 1e-12, 1 - 1e-12)
    cap = -np.expm1(K * np.log1p(-pi))  # 1 - (1 - pi)^K
    out = dict(N_hat=float(np.sum(1 / cap)), C_cal=float(pi.sum() / np.sum(pi / cap)))
    if m is not None:
        miss = (1 - cap) / cap
        out["Delta_cal"] = float(np.sum(miss * -np.expm1(m * np.log1p(-pi))))
    return out


def proxy_map(Z_obs_marks, Z_true_marks):
    """Least-squares map from observed covariates to true ones, fitted on found marks.

    Returns a function Z_obs -> Z_true_hat."""
    A = _design(Z_obs_marks)
    T = np.asarray(Z_true_marks, float)
    T = T[:, None] if T.ndim == 1 else T
    W, *_ = np.linalg.lstsq(A, T, rcond=None)
    return lambda Z: _design(Z) @ W


def calibrated_interval(Z_marks, y_marks, K, Z_items, B=1000, level=0.95, seed=None, transform=None):
    """Percentile bootstrap of C_cal over marks (refit) and found items.

    ``transform`` (optional) maps item covariates before prediction; it is
    held fixed. Returns dict(estimate, interval, dropped)."""
    rng = np.random.default_rng(seed)
    Zm = np.asarray(Z_marks, float)
    Zi = np.asarray(Z_items, float)
    f = transform or (lambda z: z)
    beta, _ = fit_detectability(Zm, y_marks, K)
    est = calibrated(predict(beta, f(Zi)), K)["C_cal"]
    reps = []
    y_marks = np.asarray(y_marks)
    for _ in range(B):
        j = rng.integers(0, len(y_marks), len(y_marks))
        i = rng.integers(0, len(Zi), len(Zi))
        b, ok = fit_detectability(Zm[j], y_marks[j], K)
        if ok:
            reps.append(calibrated(predict(b, f(Zi[i])), K)["C_cal"])
    reps = np.array(reps)
    a = (1 - level) / 2
    iv = tuple(float(v) for v in np.quantile(reps, [a, 1 - a])) if reps.size else (np.nan, np.nan)
    return dict(estimate=est, interval=iv, dropped=B - reps.size)
