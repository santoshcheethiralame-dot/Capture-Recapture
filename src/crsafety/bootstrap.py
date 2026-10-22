"""Chao incidence bootstrap (Chao et al. 2014; iNEXT ``EstiBootComm.Sam``).

Builds a pseudo-population of detection probabilities from the observed
counts (shrinking the observed items' frequencies and adding ``ceil(f0)``
unseen items that share the undetected mass), then redraws each item's count
as Binomial(K, p). Replicates are counts-only (:class:`IncidenceData` without
``X``), so only estimators that work from counts can be bootstrapped.
"""

import numpy as np
from scipy.stats import norm

from .estimators import IncidenceData, _data, _f0_chao2


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
