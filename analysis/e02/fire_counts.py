"""Per-latent firing counts on generator samples (E02 dead-latent removal; GPU on Kaggle).

    python analysis/e02/fire_counts.py --out fires.json [--world DIR|REPO] [--zoo DIR|REPO]
        [--samples 1000000] [--batch 8192] [--device cuda] [--seed 20261024]

Draws ``--samples`` activations from the SynthSAEBench world with SAELens
(`SyntheticModel.sample`) and counts, for every SAE in the zoo, how often each
latent is active (encoder output > 0). All SAEs see the same samples. The
output feeds `zoo.py histories --fire-counts`. Needs `sae-lens` (tested with
6.54.12) and torch.
"""

import argparse
import json
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis" / "e02"))
import zoo  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--world", default=zoo.WORLD_REPO)
    ap.add_argument("--zoo", default=zoo.ZOO_REPO)
    ap.add_argument("--samples", type=int, default=1_000_000)
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--seed", type=int, default=20261024)
    a = ap.parse_args()
    from sae_lens import SAE
    from sae_lens.synthetic import SyntheticModel

    torch.manual_seed(a.seed)
    world = SyntheticModel.load_from_source(str(zoo.local_dir(a.world)), device=a.device)
    idx = zoo.zoo_index(zoo.local_dir(a.zoo))
    saes = {f"{arch}/l0-{l}/seed-{s}": SAE.load_from_disk(str(f.parent), device=a.device)
            for (arch, l, s), f in idx.items()}
    counts = {k: torch.zeros(sae.cfg.d_sae, dtype=torch.long, device=a.device) for k, sae in saes.items()}
    done = 0
    with torch.no_grad():
        while done < a.samples:
            n = min(a.batch, a.samples - done)
            x = world.sample(n)
            for k, sae in saes.items():
                counts[k] += (sae.encode(x.to(sae.dtype if hasattr(sae, "dtype") else x.dtype)) > 0).sum(dim=0)
            done += n
    out = {k: v.cpu().tolist() for k, v in counts.items()}
    Path(a.out).write_text(json.dumps(dict(samples=a.samples, seed=a.seed, counts=out)) + "\n")
    dead = {k: sum(c == 0 for c in v) for k, v in out.items()}
    print(f"{len(out)} SAEs, {a.samples} samples; dead latents per SAE: min {min(dead.values())}, "
          f"max {max(dead.values())}")


if __name__ == "__main__":
    main()
