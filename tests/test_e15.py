"""E15 analysis on synthetic SAEs: marks caught with logistic probability in log p."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_e15_end_to_end(tmp_path):
    pytest.importorskip("safetensors")
    from safetensors.numpy import save_file
    sys.path.insert(0, str(ROOT / "analysis" / "e15"))
    import inject
    rng = np.random.default_rng(0)
    d = 96
    mk = inject.make_marks(d)
    np.savez(tmp_path / "marks.npz", **mk)
    lp = np.log(mk["p"])
    catch = 1 / (1 + np.exp(-(1.0 + 0.6 * (lp - np.log(1e-4)))))  # per-seed catch prob of each mark
    real = rng.normal(size=(150, d))
    real /= np.linalg.norm(real, axis=1, keepdims=True)
    real_p = np.exp(rng.uniform(np.log(1e-5), np.log(1e-2), 150))
    real_catch = 1 / (1 + np.exp(-(1.0 + 0.6 * (np.log(real_p) - np.log(1e-4)))))
    stats = {}
    for k in range(12):
        mi = np.nonzero(rng.random(len(lp)) < catch)[0]
        ri = np.nonzero(rng.random(150) < real_catch)[0]
        W = np.vstack([mk["U"][mi], real[ri]]) + 0.02 * rng.normal(size=(mi.size + ri.size, d))
        sd = tmp_path / "zoo" / "m" / "l0-32" / f"seed-{k}"
        sd.mkdir(parents=True)
        save_file({"W_dec": W.astype(np.float32)}, str(sd / "sae_weights.safetensors"))
        n = 10**6
        freq = np.concatenate([mk["p"][mi], real_p[ri]]) * np.exp(rng.normal(0, 0.1, W.shape[0]))
        counts = np.maximum(np.round(freq * n), 1)
        acts = counts * np.concatenate([mk["magnitude"][mi], rng.uniform(1, 10, ri.size)])
        stats[f"seed-{k}"] = dict(tokens=n, counts=counts.tolist(), act_sums=acts.tolist())
    (tmp_path / "stats.json").write_text(json.dumps(stats))
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "analysis/e15/analyse.py"), "--dir", str(tmp_path), "--out", str(out),
                    "--latent-stats", str(tmp_path / "stats.json"), "--B", "30"], check=True, capture_output=True)
    r = json.loads((out / "summary.json").read_text())
    assert r["K_est"] == 8 and r["held_out"] == 100 and r["fit_converged"]
    assert abs(r["C_cal_oracle"] - r["C_true"]) < 0.1 and abs(r["C_cal_observed"] - r["C_true"]) < 0.1
    assert [h["id"] for h in r["hypotheses"]] == ["H15a", "H15b", "H15c"]
    assert len(r["H15c_bands"]) == 4
