"""Tests for the H5 analyses (crsafety.testbed; analysis/e08, e09, e10) on fake histories."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from crsafety import testbed as tb
from crsafety.histories import check_cell, write_cell

ROOT = Path(__file__).resolve().parents[1]


def fake_cell(d, cell, N, k_est, k_ref, p, rng, identity="oracle", catchers=None):
    K = k_est + k_ref
    X = (rng.random((N, K)) < p[:, None]).astype(int)
    runs = [dict(catcher=(catchers[j % len(catchers)] if catchers else "qwen-7b"), seed=j,
                 role="estimation" if j < k_est else "reference", status="ok") for j in range(K)]
    ids = [f"q{i}" for i in range(N)]
    write_cell(d / cell, cell, X, ids, identity, runs=runs, items={i: {"planted": True} for i in ids})
    assert check_cell(d / cell) == []


def test_verdict_rule():
    assert tb.verdict(0.08, (0.03, 0.12), 0.05, 0.02) == "supported"
    assert tb.verdict(0.08, (0.01, 0.12), 0.05, 0.02) == "inconclusive"
    assert tb.verdict(0.01, (-0.02, 0.04), 0.05, 0.02) == "not supported"
    assert tb.verdict(0.03, (0.0, 0.06), 0.05, 0.10, higher_is_support=False) == "supported"
    assert tb.verdict(0.2, (0.15, 0.3), 0.05, 0.10, higher_is_support=False) == "not supported"
    # a failed or unbounded interval never gives a verdict on its side
    nan, inf = float("nan"), float("inf")
    assert tb.verdict(0.08, (nan, nan), 0.05, 0.02) == "inconclusive"
    assert tb.verdict(0.08, (-inf, 0.12), 0.05, 0.02) == "inconclusive"
    assert tb.verdict(0.01, (-0.02, inf), 0.05, 0.02) == "inconclusive"
    assert tb.verdict(0.03, (nan, 0.06), 0.05, 0.10, higher_is_support=False) == "inconclusive"


def test_neff_and_overlap():
    rng = np.random.default_rng(0)
    ind = (rng.random((400, 8)) < 0.3).astype(int)
    same = np.repeat(ind[:, :1], 8, axis=1)
    assert tb.neff(ind) == pytest.approx(8, rel=0.1) and tb.neff(same) == pytest.approx(1)
    assert tb.overlap_ratio(ind) == pytest.approx(1, abs=0.15) and tb.overlap_ratio(same) > 2


def run(script, *args):
    p = subprocess.run([sys.executable, str(ROOT / script), *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr[-2000:]
    return p.stdout


def test_e08_e09_e10_end_to_end(tmp_path):
    rng = np.random.default_rng(1)
    p16 = rng.uniform(0.05, 0.6, 16)
    h8 = tmp_path / "e08"
    for L in ("L0", "L1", "L3"):
        fake_cell(h8, L, 16, 8, 8, p16, rng, "judge:v1",
                  catchers=["qwen-7b", "llama-8b", "gemma-9b"] if L == "L3" else None)
    run("analysis/e08/analyse.py", "--hist", str(h8), "--out", str(tmp_path / "o8"), "--B", "200")
    H = {h["id"]: h for h in json.loads((tmp_path / "o8" / "hypotheses.json").read_text())}
    assert set(H) == {"H8a", "H8b", "H8c"}
    assert "family_loglinear" in json.loads((tmp_path / "o8" / "levels.json").read_text())["L3"]

    h9 = tmp_path / "e09"
    for T in ("T1", "T2", "T3"):
        fake_cell(h9, T, 14, 8, 8, rng.uniform(0.0, 0.5, 14), rng)
    run("analysis/e09/analyse.py", "--hist", str(h9), "--out", str(tmp_path / "o9"), "--B", "200")
    H = {h["id"] for h in json.loads((tmp_path / "o9" / "hypotheses.json").read_text())}
    assert H == {"H9a", "H9b", "H9c", "H9d"}

    h10 = tmp_path / "e10"
    for A in ("A1", "A2", "A4", "A5"):
        fake_cell(h10, A, 20, 12, 12, rng.uniform(0.02, 0.5, 20), rng, "instrumented")
    run("analysis/e10/analyse.py", "--hist", str(h10), "--out", str(tmp_path / "o10"), "--B", "100")
    H = {h["id"] for h in json.loads((tmp_path / "o10" / "hypotheses.json").read_text())}
    assert H == {"H10a", "H10b", "H10c", "H10d"}


def test_truth_modes(tmp_path):
    rng = np.random.default_rng(5)
    p = rng.uniform(0.05, 0.5, 20)
    for A in ("A1", "A2"):
        fake_cell(tmp_path, A, 20, 12, 12, p, rng, "instrumented")
    cells = {A: tb.load(tmp_path / A) for A in ("A1", "A2")}
    assert np.allclose(tb.truth_pi(cells, "A1", "reference"), cells["A1"].X_ref.mean(axis=1))
    assert np.allclose(tb.truth_pi(cells, "A1", "pooled"), cells["A1"].X_all.mean(axis=1))
    both = np.hstack([cells["A1"].X_ref, cells["A2"].X_ref]).mean(axis=1)
    assert np.allclose(tb.truth_pi(cells, "A2", "cells:A1,A2"), both)
    with pytest.raises(ValueError):
        tb.truth_pi(cells, "A1", "cells:A9")
    with pytest.raises(ValueError):
        tb.truth_pi(cells, "A1", "nonsense")


def test_pooled_truth_inflates_coverage_reference_does_not():
    """Kushal's review (2026-10-23): pooling the evaluated runs into the truth biases C upwards."""
    rng = np.random.default_rng(6)
    d_pool, d_ref = [], []
    for _ in range(1500):
        pi = rng.beta(1, 3, 20)
        X = (rng.random((20, 24)) < pi[:, None]).astype(int)
        Xe, Xr = X[:, :12], X[:, 12:]
        C = tb.true_coverage(Xe, pi)
        d_pool.append(tb.true_coverage(Xe, tb.true_pi(X)) - C)
        d_ref.append(tb.true_coverage(Xe, tb.true_pi(Xr)) - C)
    assert np.mean(d_pool) > 0.015
    assert abs(np.mean(d_ref)) < 0.005


def test_scripts_accept_catcher_agnostic_truth(tmp_path):
    rng = np.random.default_rng(7)
    p16 = rng.uniform(0.05, 0.6, 16)
    for L in ("L0", "L3"):
        fake_cell(tmp_path / "e08", L, 16, 8, 8, p16, rng, "judge:v1")
    run("analysis/e08/analyse.py", "--hist", str(tmp_path / "e08"), "--out", str(tmp_path / "o8"), "--B", "50",
        "--truth", "cells:L3")
    lv = json.loads((tmp_path / "o8" / "levels.json").read_text())
    assert lv["L0"]["truth"] == "cells:L3" and "C_pooled" in lv["L0"]
    for A in ("A1", "A2", "A5"):
        fake_cell(tmp_path / "e10", A, 20, 12, 12, rng.uniform(0.02, 0.5, 20), rng, "instrumented")
    run("analysis/e10/analyse.py", "--hist", str(tmp_path / "e10"), "--out", str(tmp_path / "o10"), "--B", "50",
        "--truth", "cells:A1,A5")
    arms = json.loads((tmp_path / "o10" / "arms.json").read_text())
    assert arms["A2"]["truth"] == "cells:A1,A5"


def test_cluster_bootstrap_resamples_whole_groups():
    seen = []
    tb.boot_items(lambda idx: seen.append(np.sort(idx)) or 0.0, 6, B=50, seed=1, groups=[0, 0, 0, 1, 1, 2])
    for idx in seen:
        # every resample is a union of whole groups: items 0-2 come together, 3-4 together
        for g in ([0, 1, 2], [3, 4]):
            counts = [np.sum(idx == j) for j in g]
            assert len(set(counts)) == 1


def test_e10_cluster_by_family(tmp_path):
    rng = np.random.default_rng(8)
    for A in ("A1", "A2"):
        d = tmp_path / "e10" / A
        p = rng.uniform(0.05, 0.5, 12)
        X = (rng.random((12, 24)) < p[:, None]).astype(int)
        runs = [dict(catcher="m", seed=j, role="estimation" if j < 12 else "reference", status="ok") for j in range(24)]
        ids = [f"b{i}" for i in range(12)]
        items = {i: dict(planted=True, covariates=dict(family=["caesar", "hex", "b64"][k % 3])) for k, i in enumerate(ids)}
        write_cell(d, A, X, ids, "instrumented", runs=runs, items=items)
    run("analysis/e10/analyse.py", "--hist", str(tmp_path / "e10"), "--out", str(tmp_path / "o"), "--B", "50")
    assert json.loads((tmp_path / "o" / "arms.json").read_text())["A1"]["bootstrap_unit"] == "family"
    run("analysis/e10/analyse.py", "--hist", str(tmp_path / "e10"), "--out", str(tmp_path / "o2"), "--B", "50",
        "--cluster", "none")
    assert json.loads((tmp_path / "o2" / "arms.json").read_text())["A1"]["bootstrap_unit"] == "blind spot"
