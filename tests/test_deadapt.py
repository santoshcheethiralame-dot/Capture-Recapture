"""Tests for de-adaptation (crsafety.deadapt; E10 A3, handoff H8)."""

import numpy as np
import pytest

import crsafety as cr
from crsafety import deadapt as da


def iid(seed, t=400, S=300, a=0.3, b=8):
    rng = np.random.default_rng(seed)
    p = rng.beta(a, b, S)
    return (rng.random((t, S)) < p[None, :]).astype(np.int8), p  # rows = units, columns = items


def test_chao_rate_matches_one_step_extrapolation():
    W, _ = iid(0, t=20)
    d = cr.estimators.IncidenceData.from_matrix(W.T)  # items x units
    r = da.chao_rate(d.Q(1), d.Q(2), d.K, add_one=False)
    # Chao et al.'s U_hat(t) is close to the one-step new-item prediction
    assert r == pytest.approx(cr.extrapolate(d, 1), rel=0.1)


def test_rate_to_coverage_identity():
    W, _ = iid(1, t=30)
    d = cr.estimators.IncidenceData.from_matrix(W.T)
    assert d.Q(2) > 0
    r = da.chao_rate(d.Q(1), d.Q(2), d.K, add_one=False)
    assert da.rate_to_coverage(r, W) == pytest.approx(cr.coverage(d), abs=1e-12)


def test_liyanage_points_follow_algorithm_1():
    # identical rows make the shuffle irrelevant; alpha = 0.5, t0 = 5:
    # i=2: s=1 (rows 1-2) -> t = 1, 2; i=3: s=1 -> t = 1, 2, 3; i=4: s=2 -> t = 2, 3, 4;
    # i=5: s=2 -> t = 2..5 (i=1 is skipped because s = e)
    W = np.tile(np.array([[1, 0, 1, 0]]), (5, 1))
    _, pts = da.liyanage(W, alpha=0.5, beta=0.5, seed=0, return_points=True)
    assert pts["t"].tolist() == [1, 2, 1, 2, 3, 2, 3, 4, 2, 3, 4, 5]
    # j = 1 prefixes give U_hat = 0 ((j - 1) = 0) and are left out of the fit; others are positive
    assert (pts["U"][pts["t"] >= 2] >= 0).all() and pts["n_fit"] > 0


def test_liyanage_deterministic_with_seed_and_points():
    W, _ = iid(3, t=60)
    a = da.liyanage(W, seed=7, return_points=True)
    b = da.liyanage(W, seed=7, return_points=True)
    assert a[0] == b[0] and a[1]["n_fit"] > 2 and np.isfinite(a[1]["slope"])


def test_reset_rate_by_hand():
    W = np.array([[1, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 0]])
    # p_reset=1: reset after unit 2 (new item 1); since then units 3-4 saw item 1 once
    assert da.reset_rate(W, p_reset=1.0, seed=0) == pytest.approx(1 / 2)
    assert np.isnan(da.reset_rate(np.array([[1, 1]]), p_reset=1.0))


def test_deadapted_coverage_in_range():
    W, _ = iid(5, t=12, S=40, a=0.5, b=3)
    for m in ("A3a", "A3b"):
        c = da.deadapted_coverage(W, method=m, seed=0)
        assert 0 <= c <= 1
