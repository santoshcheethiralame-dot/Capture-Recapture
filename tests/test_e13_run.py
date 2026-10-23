"""E13-R001 runner on simulated PROTOCOLS §10 cells."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from crsafety.histories import write_cell

ROOT = Path(__file__).resolve().parents[1]


def cell(d, rng, K_est, K_ref, N=300, sigma=1.0):
    pi = 1 / (1 + np.exp(-(rng.normal(-1.5, sigma, N))))
    X = (rng.random((N, K_est + K_ref)) < pi[:, None]).astype(np.int8)
    runs = [dict(catcher=f"r{k}", seed=k, status="ok", role="estimation" if k < K_est else "reference")
            for k in range(K_est + K_ref)]
    items = {str(i): dict(planted=True, covariates={}) for i in range(N)}
    write_cell(d, d.name, X, [str(i) for i in range(N)], "oracle", runs=runs, items=items)


def test_e13_runner(tmp_path):
    rng = np.random.default_rng(0)
    for i in range(3):
        cell(tmp_path / "e06" / f"c{i}", rng, 12, 6)
    cell(tmp_path / "a1" / "a1", rng, 10, 5)
    cell(tmp_path / "a2" / "a2", rng, 10, 5, sigma=2.0)
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "analysis/e13/run.py"),
                    "--testbed", f"E06:{tmp_path}/e06/*", "--testbed", f"E10-A1:{tmp_path}/a1/*",
                    "--testbed", f"E10-A2:{tmp_path}/a2/*:adaptive",
                    "--perms", "4", "--B", "40", "--workers", "2", "--out", str(out)], check=True, capture_output=True)
    s = json.loads((out / "summary.json").read_text())
    assert [h["id"] for h in s["hypotheses"]] == ["H13a", "H13b", "H13c", "H13d"]
    assert s["meta"]["E06"]["pi_from"] == ["reference"] * 3 and s["meta"]["E10-A2"]["adaptive"]
    assert (out / "campaigns.csv.gz").exists()
