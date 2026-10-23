"""De-adaptation of discovery-rate and coverage estimates (E10 arm A3; handoff H8).

An adaptive campaign (a greybox fuzzer, a red team that sees verdicts) changes
its own detection probabilities as it finds things, so the sampling units are
not i.i.d. and Good-Turing/Chao estimates are biased. ``W`` is the incidence
matrix of the campaign in time order: rows are sampling units (attempts, or
runs), columns are items (blind spots); W[t, i] = 1 if unit t found item i.

- :func:`liyanage` (A3a): Algorithm 1 of Liyanage, Lee, Tantithamthavorn and
  Böhme, "Extrapolating Coverage Rate in Greybox Fuzzing", ICSE 2024 (read
  from the paper, 2026-10-22). For every time i, the local window
  W[floor(i^(1 - alpha)) .. i] is shuffled into a "blackbox" campaign, whose
  discovery rate is estimated at every prefix length j with Chao et al.'s
  U_hat(j) = f1/j * (j-1) f1 / ((j-1) f1 + 2 f2). log U_hat is regressed on
  log t over t in [floor(t0^(1 - beta)), t0], and the fit is evaluated at
  t0 + m t0. Defaults alpha = 0.11, beta = 0.5 (the paper's RQ1 settings) and
  the paper's "add 1" to f1 and f2.
- :func:`reset_rate` (A3b): the "reset" estimator of Böhme, Liyanage and
  Wüstholz (ESEC/FSE 2021; artefact Adaptive-Bias/fse21_paper270): Good-Turing
  on the units since the last reset, f1' / (n - t_reset), where the counts are
  reset at a new discovery with probability ``p_reset`` (1 or 0.1 in the
  artefact).
- :func:`rate_to_coverage`: Chao-Jost incidence coverage satisfies
  1 - C_hat = U_hat(t) * t / U (U = total incidences), so a de-adapted rate
  gives a de-adapted coverage.
"""

import numpy as np


def chao_rate(f1, f2, t, add_one=True):
    """Chao et al. estimate of the expected number of new items in the next unit."""
    if add_one:
        f1, f2 = f1 + 1, f2 + 1
    if t <= 1 or f1 == 0:
        return f1 / max(t, 1)
    return f1 / t * ((t - 1) * f1 / ((t - 1) * f1 + 2 * f2))


def liyanage(W, m=0.0, alpha=0.11, beta=0.5, seed=None, add_one=True, return_points=False):
    """A3a: Liyanage et al. (ICSE 2024) Algorithm 1. Returns U_hat(t0 + m t0)."""
    W = np.asarray(W, dtype=np.int64)
    t0 = W.shape[0]
    rng = np.random.default_rng(seed)
    ts, us = [], []
    for i in range(1, t0 + 1):
        s = int(np.floor(i ** (1 - alpha)))
        e = i
        if s == e:
            continue
        Wp = W[s - 1:e]                       # rows s..e (1-indexed, inclusive)
        Wb = Wp[rng.permutation(Wp.shape[0])]  # blackbox approximation
        Y = np.cumsum(Wb, axis=0)
        f1 = (Y == 1).sum(axis=1)
        f2 = (Y == 2).sum(axis=1)
        for j in range(1, Wb.shape[0] + 1):
            ts.append(s + j - 1)
            us.append(chao_rate(int(f1[j - 1]), int(f2[j - 1]), j, add_one))
    ts, us = np.array(ts, float), np.array(us, float)
    sb = int(np.floor(t0 ** (1 - beta)))
    keep = (ts >= sb) & (ts <= t0) & (us > 0)
    if keep.sum() < 2 or np.unique(ts[keep]).size < 2:
        out = np.nan
        slope = intercept = np.nan
    else:
        slope, intercept = np.polyfit(np.log(ts[keep]), np.log(us[keep]), 1)
        out = float(np.exp(intercept + slope * np.log(t0 + m * t0)))
    if return_points:
        return out, dict(t=ts, U=us, slope=slope, intercept=intercept, n_fit=int(keep.sum()))
    return out


def reset_rate(W, p_reset=1.0, seed=None):
    """A3b: Good-Turing on the units since the last reset (Böhme et al. 2021)."""
    W = np.asarray(W, dtype=np.int64)
    rng = np.random.default_rng(seed)
    seen = np.zeros(W.shape[1], bool)
    since = np.zeros(W.shape[1], np.int64)
    t_reset = 0
    for t in range(W.shape[0]):
        row = W[t].astype(bool)
        new = row & ~seen
        seen |= row
        since += row
        if new.any() and rng.random() < p_reset:
            since[:] = 0
            t_reset = t + 1  # counting restarts after this unit
    n = W.shape[0] - t_reset
    return float((since == 1).sum() / n) if n > 0 else np.nan


def rate_to_coverage(rate, W):
    """De-adapted coverage 1 - rate * t / U, clipped to [0, 1]."""
    W = np.asarray(W)
    U = W.sum()
    if not np.isfinite(rate) or U == 0:
        return np.nan
    return float(min(max(1 - rate * W.shape[0] / U, 0.0), 1.0))


def deadapted_coverage(W, method="A3a", seed=None, **kw):
    """Coverage of the campaign W after de-adaptation (A3a or A3b)."""
    r = liyanage(W, seed=seed, **kw) if method == "A3a" else reset_rate(W, seed=seed, **kw)
    return rate_to_coverage(r, W)
