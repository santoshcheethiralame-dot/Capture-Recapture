"""Planted-mark calibration (crsafety.calibrate)."""

import numpy as np

from crsafety import calibrate as cb
from crsafety import coverage


def world(rng, n, K, b0=-1.0, b1=1.2):
    x = rng.normal(size=n)
    pi = 1 / (1 + np.exp(-(b0 + b1 * x)))
    y = rng.binomial(K, pi)
    return x, pi, y


def test_fit_recovers_logistic():
    rng = np.random.default_rng(0)
    x, _, y = world(rng, 4000, 8)
    beta, ok = cb.fit_detectability(x, y, 8)
    assert ok and np.allclose(beta, [-1.0, 1.2], atol=0.08)


def test_calibrated_is_unbiased_for_realized_coverage():
    # whether it beats Chao-Jost is E15's H15b, an empirical question, not a property
    rng = np.random.default_rng(1)
    K = 8
    errs_cal, errs_cj = [], []
    for _ in range(30):
        xm, _, ym = world(rng, 300, K, b0=-2.5, b1=1.5)       # marks
        xr, pir, yr = world(rng, 2000, K, b0=-2.5, b1=1.5)    # real items, same detectability law
        found = yr > 0
        C = pir[found].sum() / pir.sum()
        beta, _ = cb.fit_detectability(xm, ym, K)
        c = cb.calibrated(cb.predict(beta, xr[found]), K, m=K)
        errs_cal.append(c["C_cal"] - C)
        Xr = np.zeros((found.sum(), K), int)
        for r, k in enumerate(yr[found]):
            Xr[r, rng.choice(K, k, replace=False)] = 1
        errs_cj.append(coverage(Xr) - C)
    assert abs(np.mean(errs_cal)) < 0.02
    assert np.mean(np.abs(errs_cal)) < 0.03 and np.mean(np.abs(errs_cj)) < 0.03


def test_exact_ht_identities():
    pi = np.array([0.5, 0.2, 0.9])
    c = cb.calibrated(pi, 4, m=4)
    cap = 1 - (1 - pi) ** 4
    assert np.isclose(c["N_hat"], (1 / cap).sum())
    assert np.isclose(c["C_cal"], pi.sum() / (pi / cap).sum())
    assert np.isclose(c["Delta_cal"], ((1 - cap) / cap * cap).sum())


def test_proxy_map_and_interval():
    rng = np.random.default_rng(2)
    K = 8
    xm, _, ym = world(rng, 400, K, b0=-2.0, b1=1.0)
    obs = 0.8 * xm + 0.3 + rng.normal(0, 0.05, xm.size)   # observed covariate = noisy affine of truth
    f = cb.proxy_map(obs[ym > 0], xm[ym > 0])
    assert np.allclose(f(obs[ym > 0]).ravel(), xm[ym > 0], atol=0.2)
    xr, pir, yr = world(rng, 1500, K, b0=-2.0, b1=1.0)
    found = yr > 0
    ci = cb.calibrated_interval(xm, ym, K, 0.8 * xr[found] + 0.3, B=200, seed=3, transform=lambda z: f(z).ravel())
    C = pir[found].sum() / pir.sum()
    assert ci["interval"][0] <= ci["estimate"] <= ci["interval"][1]
    assert abs(ci["estimate"] - C) < 0.05
