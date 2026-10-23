"""E07 analysis script on simulated PROTOCOLS §10 cells (E02 layout)."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from crsafety.histories import write_cell

ROOT = Path(__file__).resolve().parents[1]


def make(tmp, N=600, K=5):
    rng = np.random.default_rng(3)
    p = np.exp(rng.uniform(np.log(1e-4), np.log(0.3), N))
    pc = 1 / (1 + np.exp(-(1.0 + 0.9 * np.log(p / 0.01))))  # catch prob logistic in log p
    for arch in ("A", "B"):
        for l0 in (20, 40):
            X = (rng.random((N, K)) < pc[:, None]).astype(np.int8)
            items = {}
            for i in range(N):
                c = dict(p=float(p[i]))
                for k in np.nonzero(X[i])[0]:
                    c.setdefault("log_freq", {})[str(k)] = float(np.log(p[i]) + rng.normal(0, 0.3))
                    c.setdefault("mean_act", {})[str(k)] = float(rng.gamma(2.0))
                    c.setdefault("max_cos", {})[str(k)] = float(rng.uniform(0.1, 0.6))
                items[str(i)] = dict(planted=True, covariates=c)
            runs = [dict(catcher=f"{arch} seed {k}", seed=k, status="ok", role="estimation") for k in range(K)]
            write_cell(tmp / "h" / f"{arch}_l0-{l0}", f"{arch}_l0-{l0}", X, [str(i) for i in range(N)],
                       "oracle", runs=runs, items=items)
    return p


def test_e07_end_to_end(tmp_path):
    make(tmp_path)
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "analysis/e07/analyse.py"), "--out", str(out),
                    "--e02", str(tmp_path / "h")], check=True, capture_output=True)
    rows = json.loads((out / "cells.json").read_text())
    H = json.loads((out / "hypotheses.json").read_text())
    assert len(rows) == 4 and [h["id"] for h in H["hypotheses"]] == ["H7a", "H7b (x3)", "H7b (x4)", "H7c"]
    for r in rows:
        assert r["huggins_x1_status"] == "ok" and r["huggins_x3_status"] == "ok"
        assert r["S_obs"] <= r["U"] <= r["N_true"]
        # the oracle covariate gets closer to the truth than Chao2 (detection logistic in log p)
        assert abs(r["huggins_x1"] / r["N_true"] - 1) < abs(r["chao2"] / r["N_true"] - 1)
    assert (out / "summary.md").read_text().count("| H7") == 4
