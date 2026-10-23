"""E05-R003 analysis on a hand-made injection table."""

import csv
import gzip
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_e05_analyse(tmp_path):
    rng = np.random.default_rng(0)
    rows = []
    for cell, ov in (("base", 1.0), ("ln2", 0.6)):
        for f in (0.0, 0.05, 0.10):
            for g in (0.0, 0.05):
                for j in range(5):
                    oc = 600.0
                    naive = oc * (1 + 2 * f + (0.3 if ov < 1 else 0.1) * (g > 0))
                    r = dict(cell=cell, f=f, g=g, pattern="uniform", inj=j, N=650, C=0.9, oracle_chao2=oc,
                             oracle_overlap=ov + rng.normal(0, 0.01), naive_chao2=naive, nof1=oc * 0.8,
                             naive_coverage=0.9 - f, oracle_coverage=0.9, naive_cov_lo=0.8, naive_cov_hi=1.0,
                             oracle_cov_lo=0.85, oracle_cov_hi=0.95)
                    for nv in (50, 100, 200, 500):
                        r[f"b{nv}_chao2"] = oc * (1 + 0.2 * f)
                        r[f"b{nv}_coverage"] = 0.9 - 0.1 * f
                    for e in ("e1", "e2", "naive", "oracle"):
                        r[f"{e}_chao2_lo"], r[f"{e}_chao2_hi"] = 500, 700
                    r["e1_chao2"], r["e2_chao2"] = oc * (1 + f), oc
                    r["e1_coverage"] = r["e2_coverage"] = 0.9
                    rows.append(r)
    d = tmp_path / "E05-R001"
    d.mkdir()
    with gzip.open(d / "injections.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "analysis/e05/analyse.py"), "--inputs", str(d), "--out", str(out)],
                   check=True, capture_output=True)
    H = {h["id"]: h for h in json.loads((out / "hypotheses.json").read_text())}
    assert H["H5a"]["verdict"] == "supported" and "e2 100%" in H["H5a"]["estimate"]
    assert H["H5b"]["verdict"] == "supported"
    assert H["H5c"]["verdict"] == "supported"
    assert H["H5d"]["verdict"] == "supported"
