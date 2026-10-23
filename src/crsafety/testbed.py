"""Shared machinery for the confirmatory analyses of the planted-truth testbeds
(E08, E09, E10; handoff H5). Inputs are PROTOCOLS §10 cells only.

- :func:`load`: a cell as a planted-items x runs matrix (planted items never
  caught are zero rows), split into estimation and reference runs.
- :func:`true_pi`, :func:`true_coverage`: catch rate over all of a cell's runs
  (estimation + reference), and the coverage of the estimation runs under it,
  as the E08/E09 pre-registrations define them.
- :func:`neff`: Kish effective number of runs, K / (1 + (K - 1) rho), with rho
  the mean pairwise correlation of runs' detection indicators over items.
- :func:`overlap_ratio`: mean over run pairs of observed / expected overlap.
- :func:`boot_items`: bootstrap over items (organisms, blind spots).
- :func:`verdict`: PREREGISTRATION §7 rule.
"""

from dataclasses import dataclass
from itertools import combinations

import numpy as np

from .histories import read_cell


@dataclass
class Cell:
    cell_id: str
    items: list          # planted item ids, in row order
    X_est: np.ndarray    # items x estimation runs (run_idx order)
    X_ref: np.ndarray    # items x reference runs
    catchers_est: list   # catcher string per estimation run

    @property
    def X_all(self):
        return np.hstack([self.X_est, self.X_ref])


def _full(cell, items):
    pos = {i: k for k, i in enumerate(cell.item_ids)}
    X = np.zeros((len(items), cell.X.shape[1]), np.int8)
    for r, it in enumerate(items):
        if it in pos:
            X[r] = cell.X[pos[it]]
    return X


def load(directory, identity=None):
    est = read_cell(directory, role="estimation", identity=identity)
    ref = read_cell(directory, role="reference", identity=identity)
    items = sorted(k for k, v in est.items.items() if v["planted"]) if est.items else \
        sorted(set(est.item_ids) | set(ref.item_ids))
    stray = (set(est.item_ids) | set(ref.item_ids)) - set(items)
    if stray:
        raise ValueError(f"{directory}: detections of items not in items.csv: {sorted(stray)[:5]}")
    return Cell(est.cell_id, items, _full(est, items), _full(ref, items),
                [r["catcher"] for r in est.runs])


def true_pi(X_all):
    return X_all.mean(axis=1)


def true_coverage(X_est, pi):
    found = X_est.any(axis=1)
    tot = pi[pi > 0].sum()
    return float(pi[found & (pi > 0)].sum() / tot) if tot > 0 else np.nan


def neff(X):
    K = X.shape[1]
    rhos = []
    for a, b in combinations(range(K), 2):
        x, y = X[:, a].astype(float), X[:, b].astype(float)
        if x.std() > 0 and y.std() > 0:
            rhos.append(np.corrcoef(x, y)[0, 1])
    rho = float(np.mean(rhos)) if rhos else 0.0
    return K / (1 + (K - 1) * rho)


def overlap_ratio(X):
    N, K = X.shape
    vals = []
    for a, b in combinations(range(K), 2):
        exp = X[:, a].sum() * X[:, b].sum() / N
        if exp > 0:
            vals.append((X[:, a] & X[:, b]).sum() / exp)
    return float(np.mean(vals)) if vals else np.nan


def boot_items(stat, n_items, B=2000, seed=0):
    """Percentile 95% interval of ``stat(idx)`` over item resamples ``idx``."""
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(B):
        v = stat(rng.integers(0, n_items, n_items))
        if np.isfinite(v):
            vals.append(v)
    if not vals:
        return (np.nan, np.nan)
    return tuple(float(x) for x in np.quantile(vals, [0.025, 0.975]))


def verdict(est, ci, sup, notsup, higher_is_support=True):
    """PREREGISTRATION §7: supported if the estimate meets the support threshold
    and the interval does not cross the not-supported line; not supported if
    the estimate is on the wrong side and the interval excludes the support
    threshold; otherwise inconclusive. For "lower is support" thresholds pass
    ``higher_is_support=False``."""
    lo, hi = ci
    if not higher_is_support:
        est, lo, hi, sup, notsup = -est, -hi, -lo, -sup, -notsup
    if not np.isfinite(est):
        return "inconclusive"
    if est >= sup and (not np.isfinite(lo) or lo >= notsup):
        return "supported"
    if est < notsup and (not np.isfinite(hi) or hi < sup):
        return "not supported"
    return "inconclusive"
