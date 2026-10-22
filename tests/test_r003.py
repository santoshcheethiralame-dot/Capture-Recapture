"""Property tests for the estimators added in E00-R003 (H0c).

Log-linear models, the generalised Chao estimator and the R bridge.
Agreement with R is checked by validation/e00/run_r003.sh.
"""

import os
import shutil
import subprocess

import numpy as np
import pytest

import crsafety as cr
from crsafety import rbridge
from crsafety.estimators import IncidenceData
from crsafety.loglin import closedp, design, histories, history_counts, loglinear


def sim(seed, n=200, K=6, a=0.5, b=3.0):
    rng = np.random.default_rng(seed)
    p = rng.beta(a, b, n)
    X = (rng.random((n, K)) < p[:, None]).astype(int)
    return X[X.sum(axis=1) > 0]


MATRICES = [sim(s) for s in range(8)] + [sim(s, K=3) for s in range(4)] + [sim(s, K=9) for s in range(4)]


# ------------------------------------------------------------ histories and design

@pytest.mark.parametrize("K", [2, 3, 5, 8])
def test_histories_rcapture_order(K):
    H = histories(K)
    assert H.shape == (2**K - 1, K)
    assert (H[0] == 1).all() and (H[-1] == np.eye(K, dtype=int)[-1]).all()
    assert len({tuple(r) for r in H}) == 2**K - 1 and H.sum(axis=1).min() == 1


@pytest.mark.parametrize("X", MATRICES)
def test_history_counts_sum_to_S(X):
    Y = history_counts(X)
    assert Y.sum() == X.shape[0]
    H = histories(X.shape[1])
    assert (Y @ H == X.sum(axis=0)).all()  # per-run detections are recovered


def test_mb_columns_by_hand():
    cols, names = design(3, "Mb")
    assert names == ["beta1", "beta2"]
    # (1,1,1),(1,1,0),(1,0,1),(1,0,0),(0,1,1),(0,1,0),(0,0,1)
    assert cols[:, 0].tolist() == [0, 0, 0, 0, 1, 1, 2]   # runs before first detection
    assert cols[:, 1].tolist() == [2, 1, 1, 0, 1, 0, 0]   # detections after the first


# ------------------------------------------------------------ fits

@pytest.mark.parametrize("X", MATRICES)
def test_loglinear_mt_is_darroch(X):
    # The Poisson log-linear Mt fit and Darroch's conditional MLE give the same N.
    assert loglinear(X, "Mt")["N"] == pytest.approx(cr.darroch_mt(X), rel=1e-8)


@pytest.mark.parametrize("X", MATRICES)
def test_loglinear_m0_closed_form(X):
    # M0: N solves S = N (1 - (1 - U / (N K))^K); check the fit satisfies it.
    d = IncidenceData.from_matrix(X)
    N = loglinear(X, "M0")["N"]
    p = d.U / (N * d.K)
    assert d.S == pytest.approx(N * (1 - (1 - p) ** d.K), rel=1e-8)


@pytest.mark.parametrize("X", MATRICES)
@pytest.mark.parametrize("spec", [("M0", None), ("Mh", "Poisson"), ("Mh", "Darroch"),
                                  ("Mh", "Gamma"), ("Mh", "Chao"), ("Mt", None), ("Mth", "Poisson")])
def test_loglinear_permutation_invariance(X, spec):
    rng = np.random.default_rng(3)
    Xp = X[rng.permutation(X.shape[0])][:, rng.permutation(X.shape[1])]
    a, b = loglinear(X, *spec), loglinear(Xp, *spec)
    assert a["N"] == pytest.approx(b["N"], rel=1e-8)
    assert a["deviance"] == pytest.approx(b["deviance"], rel=1e-8, abs=1e-8)


@pytest.mark.parametrize("X", MATRICES)
def test_loglinear_bounds_and_df(X):
    S, K = X.shape
    for name, r in closedp(X).items():
        assert r["N"] >= S - 1e-9, name
        assert r["se"] >= 0 or np.isnan(r["se"]), name
        assert 0 <= r["df"] <= 2**K - 2, name
    assert set(closedp(X[:, :2])) == {"M0", "Mt", "Mb"}


@pytest.mark.parametrize("X", [m for m in MATRICES if m.shape[1] >= 3])
def test_interaction_follows_runs(X):
    # The interaction term names runs, so permuting runs must permute the term.
    perm = np.array([2, 0, 1] + list(range(3, X.shape[1])))
    a = loglinear(X, "Mt", interactions=[(0, 1)])
    b = loglinear(X[:, perm], "Mt", interactions=[(1, 2)])   # old runs 0,1 are new 1,2
    assert a["N"] == pytest.approx(b["N"], rel=1e-8)
    assert loglinear(X, "Mt", interactions=[(1, 0)])["N"] == pytest.approx(a["N"])


def test_chao_lb_drops_negative_etas():
    X = sim(11, n=400, K=8, a=0.2, b=4)
    r = loglinear(X, "Mh", "Chao")
    assert all(v >= 0 for k, v in r["coef"].items() if k.startswith("eta"))


# ------------------------------------------------------------ generalised Chao

@pytest.mark.parametrize("X", MATRICES)
def test_generalized_chao_without_covariates_is_chao2(X):
    d = IncidenceData.from_matrix(X)
    if d.Q(1) == 0 or d.Q(2) == 0:
        assert np.isnan(cr.generalized_chao(X)[0])
    else:
        assert cr.generalized_chao(X)[0] == pytest.approx(cr.chao2(X), rel=1e-10)


def test_generalized_chao_permutation_and_bound():
    X = sim(5, n=300, K=7)
    z = np.random.default_rng(0).normal(size=X.shape[0])
    perm = np.random.default_rng(1).permutation(X.shape[0])
    a = cr.generalized_chao(X, z)
    b = cr.generalized_chao(X[perm], z[perm])
    assert a[0] == pytest.approx(b[0], rel=1e-10) and a[2]
    assert a[0] >= X.shape[0]


def test_generalized_chao_recovers_n_with_oracle_covariate():
    # With log-odds as the covariate the estimator is close to unbiased (median of 200).
    rng = np.random.default_rng(2)
    est = []
    for _ in range(200):
        p = rng.beta(2, 8, 400)
        X = (rng.random((400, 10)) < p[:, None]).astype(int)
        det = X.sum(axis=1) > 0
        est.append(cr.generalized_chao(X[det], np.log(p[det] / (1 - p[det])))[0])
    assert abs(np.median(est) / 400 - 1) < 0.03


# ------------------------------------------------------------ R bridge

def test_frequency_table():
    k, q = rbridge.frequency_table(IncidenceData.from_counts([1, 1, 2, 5, 5, 5], 6))
    assert (k, q) == ([1, 2, 5], [2, 1, 3])


def _have_breakaway():
    exe = shutil.which(rbridge.rscript()) or (os.path.exists(rbridge.rscript()) and rbridge.rscript())
    if not exe:
        return False
    p = subprocess.run([rbridge.rscript(), "-e", "library(breakaway); library(jsonlite)"],
                       capture_output=True)
    return p.returncode == 0


@pytest.mark.skipif(not _have_breakaway(), reason="Rscript with breakaway not available")
def test_breakaway_nof1_ignores_singletons():
    X = sim(7, n=500, K=10, a=0.3, b=2)
    d = IncidenceData.from_matrix(X)
    more = np.vstack([X, np.eye(10, dtype=int)])  # ten extra singletons
    a, b = rbridge.breakaway_nof1(d, more)
    assert a["estimate"] is not None and np.isfinite(a["estimate"])
    # f1 is not an input and is itself predicted, so extra singletons change nothing
    assert b["estimate"] == pytest.approx(a["estimate"], rel=1e-12)
