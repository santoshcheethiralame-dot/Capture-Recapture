"""Simulated inputs for figure *layout previews* (never results).

    python paper/figures/preview_inputs.py --out <dir>      # e.g. the scratchpad

Builds fake worlds, fake SAE zoos and fake PROTOCOLS §10 histories, then
runs the project's real analysis scripts on them. The outputs have exactly
the format of the real runs, so `make_all.py --results <dir>/results
--preview` can lay out every planned figure before any data exists. Every
number this produces is simulated. Nothing here goes into results/ or the
paper.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from crsafety.histories import write_cell  # noqa: E402


def run(*args):
    p = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"failed: {' '.join(map(str, args))}\n{p.stderr[-1500:]}")


def fake_world(d, rng, n=600, dim=64, alpha=0.8):
    from safetensors.numpy import save_file
    T = rng.normal(size=(n, dim))
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    p = np.sort(np.arange(1, n + 1) ** -alpha)[::-1]
    p = 5e-4 + (0.4 - 5e-4) * (p - p.min()) / (p.max() - p.min())
    d.mkdir(parents=True, exist_ok=True)
    save_file({"feature_vectors": T.astype(np.float32), "firing_probabilities": p.astype(np.float32)},
              str(d / "synthetic_model.safetensors"))
    return T, p


def fake_sae(path, T, p, rng, width=220, strength=1.0, noise=0.25):
    """A decoder that recovers feature i with probability rising in p_i, plus junk latents."""
    from safetensors.numpy import save_file
    catch = 1 / (1 + np.exp(-(strength * (np.log(p) - np.log(np.median(p))) + 0.3)))
    idx = np.nonzero(rng.random(len(p)) < catch)[0][:width]
    W = T[idx] + noise * rng.normal(size=(idx.size, T.shape[1])) / np.sqrt(T.shape[1]) * 3
    junk = rng.normal(size=(width - idx.size, T.shape[1]))
    W = np.vstack([W, junk])
    path.mkdir(parents=True, exist_ok=True)
    save_file({"W_dec": W.astype(np.float32)}, str(path / "sae_weights.safetensors"))


def e02_e03(out, rng):
    T, p = fake_world(out / "world", rng)
    for ai, arch in enumerate(("standard", "batchtopk", "jumprelu")):
        for l0 in (15, 25, 35):
            for s in range(5):
                fake_sae(out / "zoo" / arch / f"l0-{l0}" / f"seed-{s}", T, p, rng, strength=0.8 + 0.2 * ai)
    run(ROOT / "analysis/e02/zoo.py", "histories", "--world", out / "world", "--zoo", out / "zoo", "--out", out / "e02")
    run(ROOT / "analysis/e02/evaluate.py", "--hist", out / "e02" / "histories", "--out",
        out / "results/E02/E02-R004", "--B", "200")
    run(ROOT / "analysis/e03/bakeoff.py", "--world", out / "world", "--zoo", out / "zoo", "--out",
        out / "results/E03/E03-R001")


def e06(out, rng):
    for ci, cell in enumerate(("base", "alpha0.5", "init-only")):
        T, p = fake_world(out / "e06" / cell / "world", rng, alpha=0.5 if cell == "alpha0.5" else 0.8)
        for s in range(24):
            fake_sae(out / "e06" / cell / "zoo" / cell / "l0-25" / f"seed-{s}", T, p, rng)
        run(ROOT / "analysis/e02/zoo.py", "histories", "--world", out / "e06" / cell / "world", "--zoo",
            out / "e06" / cell / "zoo", "--out", out / "e06" / cell, "--reference-from", "16")
    run(ROOT / "analysis/e06/analyse.py", "--root", out / "e06", "--out", out / "results/E06/E06-R014",
        "--subsets", "50", "--B", "200")


def cell(d, name, N, k_est, k_ref, p, rng, identity="oracle", catchers=None):
    K = k_est + k_ref
    X = (rng.random((N, K)) < p[:, None]).astype(int)
    runs = [dict(catcher=(catchers[j % len(catchers)] if catchers else "model"), seed=j,
                 role="estimation" if j < k_est else "reference", status="ok") for j in range(K)]
    ids = [f"q{i}" for i in range(N)]
    write_cell(d / name, name, X, ids, identity, runs=runs, items={i: {"planted": True} for i in ids})


def testbeds(out, rng):
    p16 = rng.uniform(0.05, 0.6, 16)
    for L in ("L0", "L1", "L2", "L3"):
        cell(out / "e08", L, 16, 8, 8, np.clip(p16 * (0.7 if L == "L0" else 1.0), 0, 1), rng, "judge:v1",
             catchers=["qwen-7b", "llama-8b", "gemma-9b"] if L == "L3" else None)
    run(ROOT / "analysis/e08/analyse.py", "--hist", out / "e08", "--out", out / "results/E08/E08-R005", "--B", "200")
    for T_ in ("T1", "T2", "T3"):
        cell(out / "e09", T_, 14, 8, 8, rng.uniform(0.0, 0.5, 14), rng)
    run(ROOT / "analysis/e09/analyse.py", "--hist", out / "e09", "--out", out / "results/E09/E09-R008", "--B", "200")
    for A in ("A1", "A2", "A4", "A5"):
        cell(out / "e10", A, 20, 12, 12, rng.uniform(0.02, 0.5, 20), rng, "instrumented")
    run(ROOT / "analysis/e10/analyse.py", "--hist", out / "e10", "--out", out / "results/E10/E10-R007", "--B", "100")
    run(ROOT / "analysis/e13/run.py", "--testbed", f"E06:{out}/e06/*/histories/oracle_tgt0.7/*",
        "--testbed", f"E09:{out}/e09/*", "--testbed", f"E10-A1:{out}/e10/A1",
        "--testbed", f"E10-A2:{out}/e10/A2:adaptive", "--perms", "20", "--B", "100", "--out",
        out / "results/E13/E13-R001")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    rng = np.random.default_rng(12345)
    e02_e03(out, rng)
    print("E02/E03 preview inputs done", flush=True)
    e06(out, rng)
    print("E06 preview inputs done", flush=True)
    testbeds(out, rng)
    print("E08/E09/E10/E13 preview inputs done; results under", out / "results")


if __name__ == "__main__":
    main()
