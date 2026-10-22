"""Property tests for the estimator library (E00-R002, hypothesis H0c).

Agreement with the R references is checked separately by
validation/e00/ (E00-R001); these tests pin down the properties the
pre-registration lists plus a few hand-computed values.
"""

import numpy as np
import pytest

import crsafety as cr
from crsafety.estimators import IncidenceData
from crsafety.histories import read_cell, write_cell


def sim(seed, n=300, K=8, a=0.3, b=3.0):
    rng = np.random.default_rng(seed)
    p = rng.beta(a, b, n)
    return (rng.random((n, K)) < p[:, None]).astype(int)


MATRICES = [sim(s) for s in range(20)] + [sim(s, K=3) for s in range(5)] + [sim(s, K=20) for s in range(5)]
COUNT_ESTIMATORS = [cr.chao2, lambda X: cr.chao2(X, "bc"), cr.ichao2, cr.jackknife,
                    lambda X: cr.jackknife(X, 2), cr.ice, cr.coverage, cr.good_turing_coverage,
                    lambda X: cr.extrapolate(X, 5)]


# ------------------------------------------------------------ hand-computed values

def test_counts_and_chao2_by_hand():
    # y = (1,1,1,2,2,3,5), K = 5: Q1 = 3, Q2 = 2, S = 7, U = 15
    d = IncidenceData.from_counts([1, 1, 1, 2, 2, 3, 5], 5)
    assert (d.S, d.U, d.Q(1), d.Q(2)) == (7, 15, 3, 2)
    assert cr.chao2(d) == pytest.approx(7 + 0.8 * 9 / 4)
    assert cr.chao2(d, "bc") == pytest.approx(7 + 0.8 * 3 * 2 / 6)
    assert cr.jackknife(d) == pytest.approx(7 + 3 * 0.8)
    assert cr.jackknife(d, 2) == pytest.approx(7 + 3 * 7 / 5 - 2 * 9 / 20)
    assert cr.coverage(d) == pytest.approx(1 - 3 / 15 * (4 * 3) / (4 * 3 + 4))
    assert cr.good_turing_coverage(d) == pytest.approx(1 - 3 / 15)


def test_chapman_by_hand():
    X = np.array([[1, 1], [1, 0], [1, 0], [0, 1], [1, 1]])
    assert cr.chapman(X) == pytest.approx(5 * 4 / 3 - 1)


def test_darroch_two_runs_is_lincoln_petersen():
    X = np.array([[1, 1]] * 4 + [[1, 0]] * 6 + [[0, 1]] * 4)
    # n1 = 10, n2 = 8, m = 4: the Mt MLE with K = 2 is n1 n2 / m = 20
    assert cr.darroch_mt(X) == pytest.approx(20.0, rel=1e-8)


# ------------------------------------------------------------ properties

@pytest.mark.parametrize("X", MATRICES)
@pytest.mark.parametrize("est", COUNT_ESTIMATORS)
def test_permutation_invariance(X, est):
    rng = np.random.default_rng(0)
    Xp = X[rng.permutation(X.shape[0])][:, rng.permutation(X.shape[1])]
    a, b = est(X), est(Xp)
    assert a == pytest.approx(b) or (np.isnan(a) and np.isnan(b))


@pytest.mark.parametrize("X", MATRICES)
def test_mt_and_report_permutation_invariant(X):
    rng = np.random.default_rng(1)
    Xp = X[rng.permutation(X.shape[0])][:, rng.permutation(X.shape[1])]
    assert cr.darroch_mt(X) == pytest.approx(cr.darroch_mt(Xp))


@pytest.mark.parametrize("X", MATRICES)
def test_ordering_and_ranges(X):
    d = IncidenceData.from_matrix(X)
    assert d.S <= cr.chao2(d) <= cr.ichao2(d) or d.K < 4
    assert d.S <= cr.chao2(d, "bc")
    assert d.S <= cr.jackknife(d)
    assert 0 <= cr.coverage(d) <= 1
    assert 0 <= cr.good_turing_coverage(d) <= 1
    est, se, lo, hi = cr.chao2_ci(d)
    assert d.S <= lo <= est <= hi
    assert se >= 0


@pytest.mark.parametrize("X", MATRICES)
def test_extrapolation_monotone_and_bounded(X):
    d = IncidenceData.from_matrix(X)
    vals = [cr.extrapolate(d, m) for m in range(0, 4 * d.K + 1)]
    assert vals[0] == 0
    assert all(v >= 0 for v in vals)
    assert all(b >= a - 1e-12 for a, b in zip(vals, vals[1:]))
    # as m -> infinity the new items approach the Chao2 f0
    assert vals[-1] <= cr.chao2(d) - d.S + 1e-9


def test_no_singletons_means_full_coverage():
    d = IncidenceData.from_counts([2, 2, 3, 4], 4)
    assert cr.coverage(d) == 1.0
    assert cr.chao2(d) == d.S
    assert cr.extrapolate(d, 10) == 0.0
    assert cr.chao2_ci(d)[0] == d.S


def test_f2_zero_uses_bias_corrected_form():
    d = IncidenceData.from_counts([1, 1, 1, 1, 3], 6)
    assert cr.chao2(d) == pytest.approx(5 + 5 / 6 * 4 * 3 / 2)
    assert cr.chao2(d) == pytest.approx(cr.chao2(d, "bc"))
    est, se, lo, hi = cr.chao2_ci(d)
    assert np.isfinite([se, lo, hi]).all() and lo <= est <= hi


def test_single_singleton_falls_back_to_observed():
    d = IncidenceData.from_counts([1, 3, 4], 5)
    est, se, lo, hi = cr.chao2_ci(d)
    assert est == d.S and lo >= d.S and hi >= lo


def test_all_singletons():
    X = np.eye(6, dtype=int)  # 6 items, each found once, K = 6
    assert cr.coverage(X) < 0.1  # 1 - A, with A from the bias-corrected f0
    assert np.isfinite(cr.chao2(X))
    assert cr.darroch_mt(X) == np.inf  # no recaptures: Mt is flagged as infinite
    assert np.isfinite(cr.chapman(X))  # Chapman stays finite


def test_every_item_on_every_run():
    X = np.ones((10, 5), dtype=int)
    assert cr.chao2(X) == 10 and cr.coverage(X) == 1.0 and cr.ice(X) == 10
    assert cr.darroch_mt(X) == pytest.approx(10, rel=1e-6)


def test_single_item():
    X = np.array([[1, 0, 1]])
    assert cr.chao2(X) == 1 and cr.coverage(X) == 1.0


def test_input_validation():
    with pytest.raises(ValueError):
        IncidenceData.from_matrix([[0, 2]])
    with pytest.raises(ValueError):
        IncidenceData.from_counts([4], 3)
    with pytest.raises(ValueError):
        cr.chapman(IncidenceData.from_counts([1, 2], 3))


def test_undetected_rows_are_ignored():
    X = sim(3)
    Xz = np.vstack([X, np.zeros((50, X.shape[1]), dtype=int)])
    assert cr.report(X)["chao2_lower_bound"] == cr.report(Xz)["chao2_lower_bound"]


# ------------------------------------------------------------ Huggins

def test_huggins_recovers_N_on_constant_detection():
    rng = np.random.default_rng(7)
    N, K = 2000, 6
    X = (rng.random((N, K)) < 0.15).astype(int)
    det = X[X.sum(axis=1) > 0]
    Z = rng.normal(size=det.shape[0])  # pure noise covariate
    N_hat, beta, ok = cr.huggins(det, Z)
    assert ok and abs(N_hat - N) / N < 0.05 and abs(beta[1]) < 0.15


def test_huggins_uses_informative_covariate():
    rng = np.random.default_rng(8)
    N, K = 3000, 5
    z = rng.normal(size=N)
    p = 1 / (1 + np.exp(-(-2.0 + 1.0 * z)))
    X = (rng.random((N, K)) < p[:, None]).astype(int)
    keep = X.sum(axis=1) > 0
    N_hat, beta, ok = cr.huggins(X[keep], z[keep])
    assert ok and abs(beta[1] - 1.0) < 0.2 and abs(N_hat - N) / N < 0.1


# ------------------------------------------------------------ bootstrap

def test_bootstrap_reproducible_and_sane():
    X = sim(11)
    a = cr.bootstrap(X, cr.chao2, B=300, seed=5)
    b = cr.bootstrap(X, cr.chao2, B=300, seed=5)
    assert a == b
    assert a["se"] > 0 and a["dropped"] == 0
    lo, hi = a["percentile_ci"]
    assert lo < hi


def test_pseudo_population_mass():
    from crsafety.bootstrap import pseudo_population

    d = IncidenceData.from_matrix(sim(12))
    p = pseudo_population(d)
    assert (p > 0).all() and (p <= 1).all()
    assert p.size == d.S + int(np.ceil(cr.chao2(d) - d.S))


# ------------------------------------------------------------ histories I/O

def test_histories_roundtrip(tmp_path):
    X = sim(4, n=40, K=5)
    X = X[X.sum(axis=1) > 0]
    ids = [f"item{i:03d}" for i in range(X.shape[0])]
    runs = [dict(role="estimation")] * 4 + [dict(role="reference")]
    write_cell(tmp_path, "L0", X, ids, "oracle", runs=runs,
               items={i: dict(planted=True, covariates={"p": 0.1}) for i in ids})
    est = read_cell(tmp_path)
    assert est.run_idx == [1, 2, 3, 4]
    # items seen only in the reference run become zero rows and are dropped by data()
    assert cr.chao2(est.data()) == pytest.approx(cr.chao2(X[:, :4]))
    allruns = read_cell(tmp_path, role=None)
    assert allruns.X.shape == X.shape
    assert allruns.items[ids[0]]["planted"] and allruns.items[ids[0]]["covariates"] == {"p": 0.1}


def test_histories_reject_mixed_identity(tmp_path):
    write_cell(tmp_path, "c", np.array([[1, 0]]), ["a"], "oracle")
    with open(tmp_path / "detections.csv", "a") as f:
        f.write("c,2,b,judge:v1,,0.9\n")
    with pytest.raises(ValueError):
        read_cell(tmp_path)
    assert read_cell(tmp_path, identity="judge:v1").X.tolist() == [[0, 1]]
