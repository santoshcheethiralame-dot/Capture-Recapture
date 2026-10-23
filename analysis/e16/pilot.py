"""E16-R003 pilot (declared, exploratory): which missed-mass estimand can the residual bound? (CPU)

    python analysis/e16/pilot.py --out results/E16/E16-R003 --work <scratch dir> [--record]

Two small SynthSAEBench-style worlds, trained on CPU, stand in for E06 (the
real E06 worlds need Kaggle):
- 512 features, d = 64, Zipf exponent 1.0 or 0.5, p in [1e-3, 0.4];
- BatchTopK SAEs of width 256 at L0 = 8, trained on 2M samples;
- 6 seeds per world, with init/data seeds from
  SeedSequence(20261038, spawn_key=(9000 + world, seed)) and the E06/E11
  seeding.
`bracket.py` then measures, per world:
- (a) M_miss, the energy of the oracle-missed features;
- (b) M_unrec, the part of that energy left in each seed's residual;
- the lower bounds L0 and L1 and the upper bounds U_res, U_lin and U_lit.
The question for E16 §2a: does residual energy bound (a), or only (b)?
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "analysis" / "e06"))
import worlds  # noqa: E402

MASTER = 20261038
WORLDS = {"zipf1.0": 1.0, "zipf0.5": 0.5}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", required=True, help="where worlds and SAEs are written (not committed)")
    ap.add_argument("--seeds", type=int, default=6)
    ap.add_argument("--samples", type=int, default=2_000_000)
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    from crsafety import manifest
    from sae_lens.config import LoggingConfig
    from sae_lens.saes.batchtopk_sae import BatchTopKTrainingSAEConfig
    from sae_lens.synthetic import SyntheticModel, SyntheticSAERunner, SyntheticSAERunnerConfig

    out, work = Path(a.out), Path(a.work)
    out.mkdir(parents=True, exist_ok=True)
    m = manifest.start(out.name, "E16", " ".join(sys.argv), dict(worlds=WORLDS, seeds=a.seeds, samples=a.samples,
                                                                  n_features=512, d=64, width=256, l0=8),
                       seeds=dict(master=MASTER, rule="spawn_key=(9000 + world, seed)"),
                       packages=("numpy", "torch", "sae-lens", "crsafety"),
                       prereg=dict(frozen=False, note="declared exploratory pilot")) if a.record else None
    t0 = time.time()
    summary = {}
    for wi, (name, alpha) in enumerate(WORLDS.items()):
        cell = replace(worlds.BASE, id=name, alpha=alpha, n_true=512, d=64, width=256, l0=8, p_min=1e-3)
        base = work / name
        wdir = base / "world"
        if not (wdir / "synthetic_model.safetensors").exists():
            SyntheticModel(worlds.world_config(cell, world_seed=MASTER + wi), device="cpu").save(wdir)
        for k in range(a.seeds):
            sdir = base / "zoo" / name / "l0-8" / f"seed-{k}"
            if (sdir / "sae_weights.safetensors").exists():
                continue
            init, data = (int(v) for v in np.random.SeedSequence(MASTER, spawn_key=(9000 + wi, k)).generate_state(2))
            torch.manual_seed(init)
            cfg = SyntheticSAERunnerConfig(synthetic_model=str(wdir), sae=BatchTopKTrainingSAEConfig(k=8, d_in=64, d_sae=256),
                                           training_samples=a.samples, batch_size=1024, lr=1e-3, device="cpu",
                                           output_path=str(sdir), logger=LoggingConfig(log_to_wandb=False))
            runner = SyntheticSAERunner(cfg)
            torch.manual_seed(data)
            runner.run()
            print(name, "seed", k, f"{time.time() - t0:.0f} s", flush=True)
        bo = out / name
        subprocess.run([sys.executable, str(ROOT / "analysis/e16/bracket.py"), "--cell-dir", str(base), "--seeds",
                        f"0-{a.seeds - 1}", "--out", str(bo), "--samples", "200000", "--device", "cpu"],
                       check=True, capture_output=True)
        summary[name] = json.loads((bo / "bracket.json").read_text())
    L = ["# E16-R003 pilot (declared, exploratory): residual bounds vs two missed-mass estimands", "",
         "| world | missed features | (a) M_miss | (b) M_unrec (mean over seeds) | L0 | L1 | U_res | U_lin | U_lit | "
         "(a) within [L1, U_res] | (b) share of seeds within [L1, U_res] | (b) within [L1, U_lin] |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in summary.items():
        L.append(f"| {name} | {r['missed_features']}/{r['n_features']} | {r['M_miss']:.3f} | {r['M_miss_unrec_mean']:.3f} | "
                 f"{r['L0']:.3f} | {r['L1']:.3f} | {r['U_res']:.3f} | {r['U_lin']:.3f} | {r['U_lit']:.3f} | "
                 f"{r['brackets']['L1-U_res']['valid']} | {r['brackets_unrec']['L1-U_res']['valid_share']:.2f} | "
                 f"{r['brackets_unrec']['L1-U_lin']['valid_share']:.2f} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if m is not None:
        outs = [(out / "summary.md").resolve().relative_to(ROOT)] + \
               [(out / n / "bracket.json").resolve().relative_to(ROOT) for n in summary]
        manifest.finish(m, outputs=outs, status="succeeded", wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
