"""E04 SAE-arm generator and analysis (analysis/e04/sae_arm.py)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis" / "e04"))
import sae_arm as sa  # noqa: E402


def T(n=200, d=64, seed=0):
    return sa.mt.unit_rows(np.random.default_rng(seed).normal(size=(n, d)))


def test_rotate_hits_cosine():
    rng = np.random.default_rng(1)
    t = T()[0]
    for c in (0.3, 0.7, 0.95):
        v = sa.rotate(t, c, rng)
        assert np.isclose(np.linalg.norm(v), 1) and np.isclose(v @ t, c)


def test_split_pieces_sum_to_feature():
    rng = np.random.default_rng(2)
    W = T()
    dirs, lab, kind = sa.emit(W, np.array([5]), rng, sa.Noise(fixed=1.0), p_split=1.0, p_absorb=0.0)
    assert kind == ["split", "split"] and (lab == 5).all()
    # no noise: the two unit pieces are positive multiples of lam t + r and (1 - lam) t - r
    assert np.all(dirs @ W[5] > 0) and np.isclose(np.linalg.norm(dirs, axis=1), 1).all()


def test_clean_runs_give_one_cluster_per_feature():
    rng = np.random.default_rng(3)
    for n in (1, 3, 10):
        r = sa.replicate(T(), n, rng, sa.Noise(fixed=0.95), 0.7, 200, p_split=0.0, p_absorb=0.0)
        assert r["clusters"] == n and r["ratio"] == 1 and r["impure_clusters"] == 0
        assert r["Q"][-1] == n and r["f_oracle"] == 0


def test_splits_create_items_and_correction_reduces_them():
    rng = np.random.default_rng(4)
    rows = [sa.replicate(T(), 10, rng, sa.Noise(fixed=0.9), 0.7, 200, p_split=0.3, p_absorb=0.0) for _ in range(10)]
    assert np.mean([r["ratio"] for r in rows]) > 1.2
    assert np.mean([r["chao2_corr_ratio"] for r in rows]) < np.mean([r["chao2_ratio"] for r in rows])
    lev, H = sa.summarise(rows)
    assert lev[10]["reps"] == 10 and any(h["id"].startswith("H4a") for h in H)


def test_plateau_rule_runs():
    r = sa.replicate(T(), 3, np.random.default_rng(5), sa.Noise(fixed=0.95), "plateau", 200, p_split=0.0, p_absorb=0.0)
    assert r["status"] in ("ok", "no plateau")
    if r["status"] == "ok":
        assert r["clusters"] == 3
