"""Tests for the E01 data-generating mechanisms (crsafety.sim)."""

import numpy as np
import pytest
from scipy.special import expit

from crsafety.sim import Cell, identity_errors, logit_mean_mu, nested_cutoffs, simulate


@pytest.mark.parametrize("sigma", [0.0, 1.0, 2.0, 3.0])
def test_logit_normal_mean_is_calibrated(sigma):
    z = np.random.default_rng(0).standard_normal(400_000)
    assert expit(logit_mean_mu(sigma) + sigma * z).mean() == pytest.approx(0.2, abs=0.002)


def test_nested_cutoffs_limiting_rates():
    from scipy.stats import norm
    assert (1 - norm.cdf(nested_cutoffs())).tolist() == pytest.approx(np.linspace(0.35, 0.05, 6).tolist())


CELLS = [Cell(), Cell(het="homog", sigma=0), Cell(het="zipf", alpha=1.0), Cell(het="mixture"),
         Cell(families=1), Cell(families=6), Cell(dep_or=3.0), Cell(dep_or=1 / 3), Cell(c=2.0),
         Cell(c=0.5), Cell(K=6, nested_k=10.0), Cell(ghost=0.15), Cell(merge=0.05), Cell(N=50, K=3)]


@pytest.mark.parametrize("cell", CELLS)
def test_replicate_shapes_and_truths(cell):
    s = simulate(cell, np.random.default_rng(1))
    assert s["X"].shape == (cell.N, cell.K) == s["X_more"].shape
    assert 0 <= s["C"] <= 1
    assert s["N_all"] == cell.N and s["N"] == int((s["pi"] > 0).sum())
    found = s["X"].any(axis=1)
    assert s["Delta"] == int((s["X_more"].any(axis=1) & ~found).sum())
    if not (cell.ghost or cell.merge):
        assert (s["X_obs"] == s["X"][found]).all()


@pytest.mark.parametrize("cell", CELLS)
def test_deterministic_given_seed(cell):
    a = simulate(cell, np.random.default_rng(np.random.SeedSequence(5, spawn_key=(2, 7))))
    b = simulate(cell, np.random.default_rng(np.random.SeedSequence(5, spawn_key=(2, 7))))
    assert (a["X_obs"] == b["X_obs"]).all() and a["C"] == b["C"]


def test_mixture_uncatchable_share():
    s = simulate(Cell(het="mixture"), np.random.default_rng(0))
    assert s["N"] == 400 and not s["X"][s["pi"] == 0].any()


def test_family_marginal_pi_mean():
    s = [simulate(Cell(families=6, N=5000), np.random.default_rng(i))["pi"].mean() for i in range(3)]
    assert np.mean(s) == pytest.approx(0.2, abs=0.01)


def test_dependence_direction():
    # With odds ratio 3 between blocks, block-B runs find block-A finds more often.
    rng = np.random.default_rng(3)
    ratios = []
    for orr in (1 / 3, 1.0, 3.0):
        s = simulate(Cell(N=5000, het="homog", sigma=0, dep_or=orr), rng)
        A, B = s["X"][:, :5].any(axis=1), s["X"][:, 5]
        ratios.append(B[A].mean() / B[~A].mean())
    assert ratios[0] < 1 < ratios[2] and abs(ratios[1] - 1) < 0.1


def test_identity_errors_conserve_detections():
    rng = np.random.default_rng(4)
    X = (rng.random((300, 8)) < 0.3).astype(np.int8)
    Xg = identity_errors(X, 0.15, 0.0, rng)
    assert Xg.sum() == X.sum() and Xg.shape[0] > X.any(axis=1).sum()
    Xm = identity_errors(X, 0.0, 0.05, rng)
    assert Xm.shape[0] == X.any(axis=1).sum() - round(0.05 * X.any(axis=1).sum())


def test_adaptive_revisits_found_items():
    rng = np.random.default_rng(5)
    rep = {c: simulate(Cell(N=3000, het="homog", sigma=0, c=c), rng)["X"] for c in (0.5, 2.0)}
    per_item = {c: X[X.any(axis=1)].sum(axis=1).mean() for c, X in rep.items()}
    assert per_item[2.0] > per_item[0.5]
