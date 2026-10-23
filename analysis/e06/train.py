"""E06 R002-R013: train a cell's seeded SAEs (Kaggle GPU).

    python analysis/e06/train.py --cell base --out /kaggle/working/e06 [--seeds 0-23] [--device cuda]
        [--tiny]   # CPU smoke test: 256 features, d = 32, width 64, 20k samples

Writes <out>/<cell>/world/ (the cell's synthetic world, saved once) and
<out>/<cell>/zoo/<cell>/l0-<L0>/seed-<k>/ (SAELens output), the layout
`analysis/e02/zoo.py` reads. Seeding follows E06 §2, checked in E06-R015:
torch.manual_seed(init) before constructing the runner, torch.manual_seed(data)
before training. Seeds 0-15 are evaluation seeds, 16-23 reference seeds
(`zoo.py histories --reference-from 16`). Seeds already trained are skipped,
so a cut Kaggle session can resume.
"""

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent))
import worlds  # noqa: E402


def seed_list(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", required=True, choices=[c.id for c in worlds.CELLS])
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="0-23")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--tiny", action="store_true")
    a = ap.parse_args()
    from sae_lens.config import LoggingConfig
    from sae_lens.synthetic import SyntheticModel, SyntheticSAERunner, SyntheticSAERunnerConfig

    cell = next(c for c in worlds.CELLS if c.id == a.cell)
    if a.tiny:
        cell = replace(cell, n_true=256, d=32, width=64 if cell.width == 1024 else 256, l0=8, samples=20_000)
    base = Path(a.out) / cell.id
    wdir = base / "world"
    if not (wdir / "synthetic_model.safetensors").exists():
        SyntheticModel(worlds.world_config(cell), device=a.device).save(wdir)
    log = []
    for k in seed_list(a.seeds):
        sdir = base / "zoo" / cell.id / f"l0-{cell.l0}" / f"seed-{k}"
        if (sdir / "sae_weights.safetensors").exists():
            continue
        init, data = worlds.seeds(cell, k)
        t0 = time.time()
        torch.manual_seed(init)
        cfg = SyntheticSAERunnerConfig(synthetic_model=str(wdir), sae=worlds.sae_config(cell),
                                       training_samples=cell.samples, batch_size=1024, lr=3e-4,
                                       device=a.device, output_path=str(sdir),
                                       logger=LoggingConfig(log_to_wandb=False),
                                       autocast_sae=a.device == "cuda", autocast_data=a.device == "cuda")
        runner = SyntheticSAERunner(cfg)
        torch.manual_seed(data)
        runner.run()
        log.append(dict(seed=k, init=init, data=data, seconds=round(time.time() - t0, 1)))
        print(log[-1], flush=True)
    (base / f"train_log_{int(time.time())}.json").write_text(json.dumps(dict(cell=cell.__dict__, runs=log), indent=1) + "\n")


if __name__ == "__main__":
    main()
