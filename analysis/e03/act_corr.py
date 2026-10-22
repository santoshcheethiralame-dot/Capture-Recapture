"""E03-R002: matcher M3, activation correlation between seeds (GPU on Kaggle).

    python analysis/e03/act_corr.py --out m3/ [--world DIR|REPO] [--zoo DIR|REPO]
        [--samples 1000000] [--batch 8192] [--device cuda] [--seed 20261025]

For each cell (arch, L0), every seed is run on the same generator samples.
For each pair of seeds (a < b) the Pearson correlation between every latent
of a and every latent of b is accumulated in one pass, then the Hungarian
assignment on |corr| is computed. Only the assignment is saved
(``<out>/<arch>_l0-<L0>/<a>_<b>.npz`` with raw latent indices and scores), so
`bakeoff.py --m3 <out>` can threshold it like M1. Latents that never fire have
zero variance and correlation 0. Needs sae-lens (6.54.12) and torch.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment

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
    ap.add_argument("--seed", type=int, default=20261025)  # 20261022 + 3
    a = ap.parse_args()
    from sae_lens import SAE
    from sae_lens.synthetic import SyntheticModel

    world = SyntheticModel.load_from_source(str(zoo.local_dir(a.world)), device=a.device)
    idx = zoo.zoo_index(zoo.local_dir(a.zoo))
    out = Path(a.out)
    for arch, l0 in sorted({(x, l) for x, l, _ in idx}):
        seeds = sorted(s for x, l, s in idx if (x, l) == (arch, l0))
        saes = [SAE.load_from_disk(str(idx[(arch, l0, s)].parent), device=a.device) for s in seeds]
        torch.manual_seed(a.seed)  # every cell sees the same samples
        n = 0
        s1 = [torch.zeros(m.cfg.d_sae, dtype=torch.float64, device=a.device) for m in saes]
        s2 = [torch.zeros_like(v) for v in s1]
        cross = {}
        with torch.no_grad():
            while n < a.samples:
                b = min(a.batch, a.samples - n)
                x = world.sample(b)
                acts = [m.encode(x).double() for m in saes]
                for k, z in enumerate(acts):
                    s1[k] += z.sum(0)
                    s2[k] += (z * z).sum(0)
                for i in range(len(saes)):
                    for j in range(i + 1, len(saes)):
                        cross[(i, j)] = cross.get((i, j), 0) + acts[i].T @ acts[j]
                n += b
        mean = [v / n for v in s1]
        sd = [torch.sqrt(torch.clamp(q / n - m * m, min=0)) for q, m in zip(s2, mean)]
        cdir = out / f"{arch}_l0-{l0}"
        cdir.mkdir(parents=True, exist_ok=True)
        for (i, j), c in cross.items():
            cov = c / n - torch.outer(mean[i], mean[j])
            den = torch.outer(sd[i], sd[j])
            corr = torch.where(den > 0, cov / torch.where(den > 0, den, 1), 0).abs().cpu().numpy()
            r, cc = linear_sum_assignment(-corr)
            np.savez_compressed(cdir / f"{seeds[i]}_{seeds[j]}.npz", a=r, b=cc, score=corr[r, cc],
                                samples=n, seed=a.seed)
        print(f"{arch} L0={l0}: {len(cross)} seed pairs", flush=True)


if __name__ == "__main__":
    main()
