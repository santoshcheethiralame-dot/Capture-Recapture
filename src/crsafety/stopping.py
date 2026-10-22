"""Coverage stopping rules for audit campaigns (E13; PH6).

A campaign adds runs one at a time in a given order. After k runs:
- R-point stops at the first k >= k_min with C_hat(k) >= target;
- R-lower stops at the first k >= k_min where the one-sided lower bound of
  the realized coverage (:func:`crsafety.coverage_interval`, D-010) is
  >= target;
- R-fixed always runs all K_max runs.
A rule that never fires stops at K_max. The lower bound is computed only
when C_hat(k) >= target, since the bound never exceeds the estimate.
"""

import warnings

import numpy as np

from .bootstrap import coverage_interval
from .estimators import IncidenceData, coverage


def true_coverage(X, pi, k):
    """C(k) = sum of pi over items found in the first k columns / sum over pi > 0."""
    found = X[:, :k].any(axis=1)
    return float(pi[found].sum() / pi[pi > 0].sum())


def _data(X, k):
    Xk = X[:, :k]
    Xk = Xk[Xk.any(axis=1)]
    return IncidenceData.from_matrix(Xk) if Xk.shape[0] else None


def stop_point(X, target, k_min=3):
    for k in range(k_min, X.shape[1] + 1):
        d = _data(X, k)
        if d is not None and coverage(d) >= target:
            return k
    return X.shape[1]


def stop_lower(X, target, k_min=3, level=0.95, B=1000, seed=None):
    ss = np.random.SeedSequence(seed)
    seeds = ss.spawn(X.shape[1] + 1)
    for k in range(k_min, X.shape[1] + 1):
        d = _data(X, k)
        if d is None or coverage(d) < target:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lo = coverage_interval(d, B=B, level=level, seed=seeds[k])["lower_one_sided"]
        if lo >= target:
            return k
    return X.shape[1]


def campaign(X, pi, order, targets=(0.8, 0.9), k_min=3, level=0.95, B=1000, seed=None):
    """Apply every rule to one run order. Returns a list of dicts, one per
    (rule, target): k_stop, true C at stop, success, runs saved vs R-fixed,
    undershoot (target - C when it fails, else 0)."""
    Xo = X[:, list(order)]
    K = Xo.shape[1]
    out = []
    for t in targets:
        for rule in ("R-point", "R-lower", "R-fixed"):
            if rule == "R-point":
                k = stop_point(Xo, t, k_min)
            elif rule == "R-lower":
                k = stop_lower(Xo, t, k_min, level, B, seed)
            else:
                k = K
            C = true_coverage(Xo, pi, k)
            out.append(dict(rule=rule, target=t, k_stop=k, C_at_stop=C, success=C >= t,
                            saved=(K - k) / K, undershoot=max(t - C, 0.0)))
    return out
