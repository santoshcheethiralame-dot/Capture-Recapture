"""huggins_ci against VGAM 1.1.14 (posbernoulli.t, parallel.t = TRUE ~ z) on
the E00 Huggins datasets, and interval coverage on simulated data."""

from pathlib import Path

import numpy as np
import pytest

from crsafety import huggins_ci

DATA = Path(__file__).resolve().parents[1] / "results" / "E00" / "E00-R003" / "data" / "huggins"
# fit@extra$N.hat, fit@extra$SE.N.hat (Rscript, VGAM 1.1.14, epsilon 1e-12)
VGAM = {"hug_noise_cov": (1028.8626557184, 61.3885553886),
        "hug_one_cov": (1467.9705548852, 110.2244924986),
        "hug_two_cov": (2628.9244784675, 219.3630423510)}


@pytest.mark.parametrize("name", sorted(VGAM))
def test_matches_vgam(name):
    import csv
    rows = list(csv.DictReader(open(DATA / f"{name}.csv")))
    X = np.array([[int(r[k]) for k in r if k.startswith("y")] for r in rows])
    Z = np.array([[float(r[k]) for k in r if k.startswith("z")] for r in rows])
    N, se, lo, hi, ok = huggins_ci(X, Z)
    assert ok
    assert N == pytest.approx(VGAM[name][0], rel=1e-7)
    assert se == pytest.approx(VGAM[name][1], rel=1e-6)
    assert X.shape[0] <= lo < N < hi


def test_interval_coverage():
    rng = np.random.default_rng(7)
    N, K, hits, n = 600, 6, 0, 300
    for _ in range(n):
        z = rng.normal(size=N)
        p = 1 / (1 + np.exp(-(-2.0 + 1.0 * z)))
        X = (rng.random((N, K)) < p[:, None]).astype(int)
        det = X.any(axis=1)
        _, _, lo, hi, ok = huggins_ci(X[det], z[det])
        hits += ok and lo <= N <= hi
    assert 0.90 <= hits / n <= 0.99


def test_no_detection_gap():
    X = np.ones((20, 5), int)
    X[:10, 0] = 0
    N, se, lo, hi, ok = huggins_ci(X, np.linspace(0, 1, 20))
    assert N >= 20 and lo >= 20
