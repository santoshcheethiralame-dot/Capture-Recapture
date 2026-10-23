"""E11 analysis on synthetic decoders (shared directions vs random null)."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def write(d, W):
    from safetensors.numpy import save_file
    d.mkdir(parents=True, exist_ok=True)
    save_file({"W_dec": W.astype(np.float32)}, str(d / "sae_weights.safetensors"))


def test_e11_end_to_end(tmp_path):
    pytest.importorskip("safetensors")
    rng = np.random.default_rng(0)
    dim, n_feat, width = 48, 120, 60
    T = rng.normal(size=(n_feat, dim))
    p = np.linspace(1, 0.05, n_feat)  # uneven detectability
    for k in range(12):
        pick = rng.random(n_feat) < p
        idx = np.nonzero(pick)[0][:width]
        W = T[idx] + 0.05 * rng.normal(size=(idx.size, dim))
        write(tmp_path / "seeds" / "m" / "l0-32" / f"seed-{k}", W)
    for k in range(4):
        write(tmp_path / "null" / "m" / "l0-32" / f"seed-{k}", rng.normal(size=(width, dim)))
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "analysis/e11/analyse.py"), "--root", str(tmp_path), "--model", "m",
                    "--out", str(out), "--B", "50"], check=True, capture_output=True)
    r = json.loads((out / "summary.json").read_text())
    assert r["n_independent"] == 8 and r["n_shared"] == 4
    assert r["H11c"]["verdict"] == "supported" and r["H11c"]["recapture_null"] < 0.1
    assert 0 < r["units"][next(iter(r["units"]))]["estimate"] <= 1
    assert (out / "histories" / "seeds_tau-mid" / "detections.csv").exists()
