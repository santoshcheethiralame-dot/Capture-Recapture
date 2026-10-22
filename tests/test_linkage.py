"""Tests for the E05 identity-error model and corrections (crsafety.linkage)."""

import numpy as np
import pytest

import crsafety as cr
from crsafety import linkage as lk
from crsafety.estimators import IncidenceData


def world(seed, N=600, K=8):
    rng = np.random.default_rng(seed)
    p = rng.beta(1, 4, N)
    return (rng.random((N, K)) < p[:, None]).astype(np.int8), p, rng


def test_no_errors_is_identity():
    X, p, rng = world(0)
    L = lk.inject(X, 0.0, 0.0, rng)
    assert (L.X == X[X.any(axis=1)]).all() and not L.is_ghost.any() and L.n_merges == 0


@pytest.mark.parametrize("pattern", ["uniform", "score"])
def test_ghost_rate_and_conservation(pattern):
    rates = []
    for seed in range(20):
        X, p, rng = world(100 + seed, N=2000)
        L = lk.inject(X, 0.10, 0.0, rng, pattern=pattern, p=p)
        det = X[X.any(axis=1)]
        assert L.X.sum() == X.sum()                    # ghosts conserve detections
        assert (L.X[L.is_ghost].sum(axis=1) == 1).all()
        rates.append(L.is_ghost.sum() / (det.sum() - det.shape[0]))
    assert np.mean(rates) == pytest.approx(0.10, abs=0.005)


def test_merges_reduce_rows():
    X, p, rng = world(2)
    S = X.any(axis=1).sum()
    L = lk.inject(X, 0.0, 0.05, rng)
    assert L.X.shape[0] == S - round(0.05 * S) and L.n_merges == round(0.05 * S)


def test_thinning_matrix_columns_sum_to_one():
    A = lk.thinning_matrix(6, 0.2)
    assert A.sum(axis=0) == pytest.approx(np.ones(6))
    assert A[0, 0] == 1 and A[1, 1] == pytest.approx(0.8)


def test_correct_Q_inverts_expected_counts():
    K, f = 8, 0.15
    Q_true = np.array([120, 60, 40, 25, 15, 8, 4, 2], float)
    U = (np.arange(1, K + 1) * Q_true).sum()
    obs = lk.thinning_matrix(K, f) @ Q_true
    obs[0] += f * (U - Q_true.sum())
    assert lk.correct_Q(obs, U, K, f) == pytest.approx(Q_true, rel=1e-8)


def test_estimate_rates_with_full_labels():
    X, p, rng = world(3, N=3000)
    L = lk.inject(X, 0.10, 0.0, rng)
    f_hat, _ = lk.estimate_rates(L, n_v=10**9, rng=rng)   # every pair labelled: exact
    linked = L.pairs_true.sum() - L.is_ghost.sum()
    assert f_hat == pytest.approx(L.is_ghost.sum() / (L.is_ghost.sum() + linked), rel=1e-12)
    L = lk.inject(X, 0.0, 0.03, rng)
    _, g_hat = lk.estimate_rates(L, n_v=10**9, rng=rng)
    assert g_hat == pytest.approx(L.n_merges / (L.X.shape[0] + L.n_merges), rel=1e-12)


def test_estimate_rates_with_200_labels_is_close():
    errs = []
    for seed in range(30):
        X, p, rng = world(200 + seed, N=1500)
        L = lk.inject(X, 0.10, 0.0, rng)
        errs.append(lk.estimate_rates(L, n_v=200, rng=rng)[0] - 0.10)
    assert abs(np.mean(errs)) < 0.02


def test_ghost_correction_reduces_chao2_bias():
    est_naive, est_corr, truth = [], [], []
    for s in range(30):
        X, p, rng = world(10 + s, N=1500)
        L = lk.inject(X, 0.10, 0.0, rng)
        d = IncidenceData.from_matrix(L.X)
        est_naive.append(cr.chao2(d))
        est_corr.append(lk.corrected_estimates(d, 0.10)["chao2"])
        truth.append(cr.chao2(X))
    naive = abs(np.mean(est_naive) / np.mean(truth) - 1)
    corr = abs(np.mean(est_corr) / np.mean(truth) - 1)
    assert naive > 0.10 and corr < naive / 2


def test_lp_correction_and_dct_agree_without_false_links():
    X, p, rng = world(4)
    assert lk.dct_petersen(X, 0.9, 0.0) == pytest.approx(lk.lp_corrected(X, 0.1))
    assert lk.dct_petersen(X, 0.9, 0.0, 0, 1) == pytest.approx(lk.lp_corrected(X, 0.1, 0, 1))
    K = X.shape[1]
    pairs = [lk.lp_corrected(X, 0.0, i, j) for i in range(K) for j in range(i + 1, K)]
    assert lk.lp_corrected(X, 0.0) == pytest.approx(np.mean(pairs))


def test_mi_runs_and_moves_toward_truth():
    X, p, rng = world(5, N=1500)
    L = lk.inject(X, 0.15, 0.0, rng)
    naive = cr.chao2(L.X)
    mi = lk.mi_estimates(L, M=5, rng=rng)
    assert abs(mi["chao2"] - cr.chao2(X)) < abs(naive - cr.chao2(X))
    assert mi["chao2_var"] > 0
