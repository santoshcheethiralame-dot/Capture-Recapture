"""Chao incidence bootstrap (Chao et al. 2014; iNEXT ``EstiBootComm.Sam``).

Builds a pseudo-population of detection probabilities from the observed
counts (shrinking the observed items' frequencies and adding ``ceil(f0)``
unseen items that share the undetected mass), then redraws each item's count
as Binomial(K, p). Replicates are counts-only (:class:`IncidenceData` without
``X``), so only estimators that work from counts can be bootstrapped.
"""

import numpy as np
from scipy.stats import norm

from .estimators import IncidenceData, _data, _f0_chao2, coverage, extrapolate


def pseudo_population(X):
    """Detection probabilities of the bootstrap population (iNEXT form)."""
    d = _data(X)
    K, Q1 = d.K, d.Q(1)
    f0 = _f0_chao2(d, "chao2014")
    A = K * f0 / (K * f0 + Q1) if Q1 > 0 else 1.0
    a = Q1 / K * A
    p_obs = d.y / K
    b = np.sum(p_obs * (1 - p_obs) ** K)
    w = 0.0 if f0 == 0 else a / b
    p_seen = p_obs * (1 - w * (1 - p_obs) ** K)
    n_unseen = int(np.ceil(f0))
    p_unseen = np.full(n_unseen, a / n_unseen) if n_unseen > 0 else np.empty(0)
    return np.concatenate([p_seen, p_unseen])


def bootstrap(X, stat, B=2000, level=0.95, seed=None):
    """Bootstrap a statistic of the counts.

    ``stat`` maps an :class:`IncidenceData` to a float. Returns a dict with
    the point estimate, the bootstrap SE, iNEXT's normal interval
    (estimate ± z·SE) and the percentile interval. Non-finite replicates are
    dropped and counted.
    """
    d = _data(X)
    rng = np.random.default_rng(seed)
    p = pseudo_population(d)
    est = float(stat(d))
    reps = np.empty(B)
    for b in range(B):
        y = rng.binomial(d.K, p)
        # replicates with no detections are dropped, as in iNEXT
        reps[b] = stat(IncidenceData.from_counts(y, d.K)) if y.any() else np.nan
    ok = np.isfinite(reps)
    reps = reps[ok]
    se = float(np.std(reps, ddof=1)) if reps.size > 1 else np.nan
    z = norm.ppf(0.5 + level / 2)
    alpha = 1 - level
    pct = np.quantile(reps, [alpha / 2, 1 - alpha / 2]) if reps.size else (np.nan, np.nan)
    return dict(
        estimate=est, se=se, normal_ci=(float(est - z * se), float(est + z * se)),
        percentile_ci=(float(pct[0]), float(pct[1])), B=B, dropped=int((~ok).sum()),
    )


def _realized(X, stat_err, B, level, seed, bias_correct):
    d = _data(X)
    rng = np.random.default_rng(seed)
    p = pseudo_population(d)
    K = d.K
    err = np.empty(B)
    for b in range(B):
        y = rng.binomial(K, p)
        found = y > 0
        err[b] = stat_err(IncidenceData.from_counts(y[found], K), p, found, rng) if found.any() else np.nan
    err = err[np.isfinite(err)]
    se = float(np.std(err, ddof=1)) if err.size > 1 else np.nan
    shift = float(err.mean()) if bias_correct and err.size else 0.0
    return se, shift, int(B - err.size), float(err.mean()) if err.size else np.nan


def coverage_interval(X, B=1000, level=0.95, seed=None, bias_correct=False):
    """Interval for the realized coverage C of *this* set of runs.

    C = sum of detection probabilities of the items found / total, is a
    property of the sample, so an interval must cover the error C_hat - C, not
    only the spread of C_hat. Each bootstrap sample is drawn from the Chao
    pseudo-population, whose probabilities p are known, so both C_hat* and the
    realized C* = sum_{found*} p / sum p are available; the interval is
    C_hat - shift ± z · sd(C_hat* - C*), with shift = mean(C_hat* - C*) if
    ``bias_correct`` else 0. (The iNEXT interval C_hat ± z · sd(C_hat*) covered
    the realized C in about 76% of E01-R005 replicates at nominal 95%.)

    Returns dict(estimate, se, interval, lower_one_sided, mean_error, dropped).
    ``lower_one_sided`` is the one-sided lower bound at ``level`` (for
    stopping rules). Clipped to [0, 1].
    """
    d = _data(X)
    est = float(coverage(d))
    err = lambda e, p, found, rng: coverage(e) - p[found].sum() / p.sum()
    se, shift, dropped, merr = _realized(d, err, B, level, seed, bias_correct)
    z2, z1 = norm.ppf(0.5 + level / 2), norm.ppf(level)
    lo, hi = est - shift - z2 * se, est - shift + z2 * se
    return dict(estimate=est, se=se, interval=(max(lo, 0.0), min(hi, 1.0)),
                lower_one_sided=max(est - shift - z1 * se, 0.0), mean_error=merr, dropped=dropped)


def delta_interval(X, m=None, B=1000, level=0.95, seed=None, bias_correct=False):
    """Interval for the number of new items that m more runs will find (default m = K).

    As :func:`coverage_interval`: each bootstrap sample also draws m further
    runs from the pseudo-population, so the realized number of new items Δ*
    is known and the interval covers the prediction error Δ_hat* − Δ*.
    """
    d = _data(X)
    m = d.K if m is None else m
    est = float(extrapolate(d, m))

    def err(e, p, found, rng):
        new = (rng.binomial(m, p) > 0) & ~found
        return extrapolate(e, m) - new.sum()

    se, shift, dropped, merr = _realized(d, err, B, level, seed, bias_correct)
    z2 = norm.ppf(0.5 + level / 2)
    lo, hi = est - shift - z2 * se, est - shift + z2 * se
    return dict(estimate=est, se=se, interval=(max(lo, 0.0), hi), mean_error=merr, dropped=dropped)
