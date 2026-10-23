"""Tests for the SAE identity rules (crsafety.matching)."""

import numpy as np
import pytest

from crsafety import matching as mt


def world(seed=0, N=120, d=48, K=4, keep=0.7, noise=0.15, junk=10):
    """True unit directions; each seed is a noisy, sign-flipped, shuffled copy of a
    random subset of them plus junk latents."""
    rng = np.random.default_rng(seed)
    T = mt.unit_rows(rng.standard_normal((N, d)))
    seeds, truth = [], []
    for _ in range(K):
        idx = np.nonzero(rng.random(N) < keep)[0]
        W = T[idx] * rng.choice([-1, 1], (idx.size, 1)) + noise / np.sqrt(d) * rng.standard_normal((idx.size, d))
        W = np.vstack([W, rng.standard_normal((junk, d))])
        lab = np.concatenate([idx, -np.ones(junk, int)])
        perm = rng.permutation(W.shape[0])
        seeds.append(W[perm])
        truth.append(lab[perm])
    return T, seeds, truth


def test_abs_cos_and_antipodes():
    A = np.array([[1.0, 0], [0, 2.0]])
    assert mt.abs_cos(A, -A) == pytest.approx(np.eye(2))


def test_preprocess_merges_duplicates_and_drops_dead():
    W = np.array([[1.0, 0, 0], [-1.0, 0.01, 0], [0, 1.0, 0], [0, 0, 1.0]])
    kept, _ = mt.preprocess(W, fire_counts=[5, 3, 0, 1])
    assert kept.tolist() == [0, 3]


def test_hungarian_recovers_identity():
    T, seeds, truth = world()
    pairs, s = mt.hungarian(seeds[0], seeds[1], 0.7)
    a, b = truth[0][pairs[:, 0]], truth[1][pairs[:, 1]]
    assert np.mean(a == b) > 0.97 and (s >= 0.7).all()


def test_mutual_nn_and_strict_are_subsets_of_good_matches():
    T, seeds, truth = world(1)
    p, _ = mt.mutual_nn(seeds[0], seeds[1], 0.7)
    assert np.mean(truth[0][p[:, 0]] == truth[1][p[:, 1]]) > 0.97
    p2, _ = mt.strict(seeds[0], seeds[1], seeds[0], seeds[1], 0.7)
    p1, _ = mt.hungarian(seeds[0], seeds[1], 0.7)
    assert {tuple(x) for x in p2} <= {tuple(x) for x in p1}


@pytest.mark.parametrize("mode", ["components", "star"])
def test_cluster_seeds_matches_oracle_history(mode):
    T, seeds, truth = world(2)
    X, labels = mt.cluster_seeds(seeds, 0.7, mode=mode)
    assert X.shape[1] == 4 and X.sum() == sum(s.shape[0] for s in seeds)
    s = mt.pair_scores(labels, truth)
    # star cannot link items missing from the reference seed (a known weakness)
    assert s["precision"] > 0.99 and s["recall"] > (0.95 if mode == "components" else 0.8)
    O = mt.oracle_history(seeds, T)
    real = X[X.sum(axis=1) > 0]
    # components: junk latents become singletons and true items recover the oracle counts
    if mode == "components":
        assert abs((real.sum(axis=1) >= 2).sum() - (O.sum(axis=1) >= 2).sum()) <= 3


def test_oracle_catch():
    T, seeds, truth = world(3)
    caught, feat = mt.oracle_catch(seeds[0], T)
    present = np.zeros(T.shape[0], bool)
    present[truth[0][truth[0] >= 0]] = True
    assert (caught == present).mean() > 0.98
    ok = feat >= 0
    assert (feat[ok] == truth[0][ok]).mean() > 0.98


def test_plateau_rule():
    taus = np.round(np.arange(0.30, 0.96, 0.05), 2)
    counts = [900, 700, 520, 500, 495, 492, 490, 470, 400, 300, 250, 200, 150, 100]
    # [0.45, 0.60]: counts 500..490, range 2% of 500; adding 0.40 (520) or 0.65 (470) breaks 5%
    assert mt.plateau(taus, counts) == pytest.approx((0.45 + 0.60) / 2)
    assert mt.plateau(taus, np.linspace(1000, 100, taus.size)) is None


def test_pair_scores_and_ari_by_hand():
    pred = [np.array([0, 1, 2]), np.array([0, 1, 3])]
    true = [np.array([0, 1, 2]), np.array([0, 2, 1])]
    s = mt.pair_scores(pred, true)
    # predicted cross pairs: (0,0),(1,1); true: (0,0),(1,2),(2,1)
    assert s["precision"] == 0.5 and s["recall"] == pytest.approx(1 / 3)
    assert mt.error_rates(pred, true)["ghost"] == pytest.approx(2 / 3)
    assert mt.ari([0, 0, 1, 1], [5, 5, 7, 7]) == 1.0
    assert mt.ari([0, 0, 1, 1], [0, 1, 0, 1]) == pytest.approx(-0.5)


def test_sweep_equals_separate_clusterings():
    T, seeds, truth = world(4)
    taus = [0.3, 0.5, 0.7, 0.9]
    sw = mt.sweep(seeds, taus)
    for t in taus:
        X, lab = mt.cluster_seeds(seeds, t)
        assert (sw[t][0] == X).all()
    counts = [sw[t][0].shape[0] for t in taus]
    assert counts == sorted(counts)  # higher thresholds never merge more


def test_plateau_interval():
    taus = np.round(np.arange(0.3, 0.96, 0.05), 2)
    counts = [100, 90, 60, 50, 50, 50, 50, 51, 70, 90, 100, 110, 120, 130]
    lo, mid, hi = mt.plateau(taus, counts, return_interval=True)
    assert lo <= mid <= hi and np.isclose(mid, mt.plateau(taus, counts)) and hi - lo >= 0.10
