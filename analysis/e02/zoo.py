"""E02: SynthSAEBench zoo -> inventory, oracle and matched detection histories.

Runs on Kaggle (Hugging Face access) or on any machine with a local copy.

    python analysis/e02/zoo.py inventory  --out results/E02/E02-R001      # R001 (pre-freeze OK)
    python analysis/e02/zoo.py histories  --out results/E02/E02-R00X      # R002/R003 (after the freeze)
    options: --world DIR|REPO  --zoo DIR|REPO  (default: the Hugging Face repos)

Layout assumed (read from SAELens 6.54 and synth-sae-bench-experiments,
2026-10-22; R001 checks it):
- world repo: ``synthetic_model.safetensors`` with ``feature_vectors``
  [n_features x d] and ``firing_probabilities`` [n_features];
- zoo repo: ``<arch>/l0-<L0>/seed-<s>/sae_weights.safetensors`` (+ cfg.json),
  with a ``W_dec`` tensor [d_sae x d] (either orientation is accepted).

Histories follow PROTOCOLS §10: one cell per (arch, L0), K = number of seeds.
Oracle: GT-MCC catch at tau_gt in {0.5, 0.6, 0.7, 0.8, 0.9}; item_id is the
true feature index (stable across cells). Matched: M1 (Hungarian on |decoder
cos|) over the E03 threshold grid; item_id is the cluster label (meaningful
within a cell only). Folding JumpReLU thresholds into the decoder (PROTOCOLS
§2) only rescales rows, so it does not change |cos| matching.
Preprocessing (E02 §2): within-SAE duplicates (|cos| >= 0.95, antipodal
included) are merged; dead latents are dropped when ``--fire-counts`` points
to the JSON written by `fire_counts.py` ({"<arch>/l0-<L0>/seed-<s>": [count
per latent]}, under "counts"), computed on 10^6 generator samples. Without it no
latent is treated as dead, and the summary says so.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from crsafety import matching as mt  # noqa: E402
from crsafety.histories import check_cell, write_cell  # noqa: E402

WORLD_REPO = "decoderesearch/synth-sae-bench-16k-v1"
ZOO_REPO = "decoderesearch/synth-sae-bench-16k-v1-saes"
SAE_RE = re.compile(r"(?:^|/)(?P<arch>[^/]+)/l0-(?P<l0>\d+)/seed-(?P<seed>\d+)/sae_weights\.safetensors$")
TAU_GT = (0.5, 0.6, 0.7, 0.8, 0.9)
TAU_M = tuple(np.round(np.arange(0.30, 0.951, 0.05), 2))


def local_dir(src, repo_type="model"):
    """A local directory for a repo id or path (downloads with huggingface_hub)."""
    p = Path(src)
    if p.exists():
        return p
    from huggingface_hub import snapshot_download
    return Path(snapshot_download(src, repo_type=repo_type))


def load_tensors(path):
    from safetensors.numpy import load_file
    return load_file(str(path))


def load_world(d):
    f = next(Path(d).rglob("synthetic_model.safetensors"))
    t = load_tensors(f)
    return t["feature_vectors"].astype(np.float32), t["firing_probabilities"].astype(np.float64), f


def zoo_index(d):
    out = {}
    for f in sorted(Path(d).rglob("sae_weights.safetensors")):
        m = SAE_RE.search(f.relative_to(d).as_posix())
        if m:
            out[(m["arch"], int(m["l0"]), int(m["seed"]))] = f
    return out


def decoder(f, d_model):
    t = load_tensors(f)
    key = next(k for k in t if k.endswith("W_dec"))
    W = t[key].astype(np.float32)
    return W if W.shape[1] == d_model else W.T


def inventory(args):
    world_dir, zoo_dir = local_dir(args.world), local_dir(args.zoo)
    T, p, wf = load_world(world_dir)
    idx = zoo_index(zoo_dir)
    archs = sorted({a for a, _, _ in idx})
    l0s = sorted({l for _, l, _ in idx})
    seeds = sorted({s for _, _, s in idx})
    widths = {}
    for key, f in idx.items():
        widths[key] = decoder(f, T.shape[1]).shape[0]
    missing = [(a, l, s) for a in archs for l in l0s for s in seeds if (a, l, s) not in idx]
    inv = dict(world_file=str(wf.relative_to(world_dir)), n_features=int(T.shape[0]), d=int(T.shape[1]),
               p_min=float(p.min()), p_max=float(p.max()), archs=archs, l0=l0s, seeds=seeds,
               n_saes=len(idx), widths=sorted(set(widths.values())), missing=missing,
               cells=len(archs) * len(l0s), expected=dict(archs=5, l0=7, seeds=5, width=4096))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "inventory.json").write_text(json.dumps(inv, indent=2) + "\n")
    print(json.dumps(inv, indent=2))


def histories(args):
    world_dir, zoo_dir = local_dir(args.world), local_dir(args.zoo)
    T, p, _ = load_world(world_dir)
    idx = zoo_index(zoo_dir)
    fires = json.loads(Path(args.fire_counts).read_text()) if args.fire_counts else {}
    fires = fires.get("counts", fires)  # fire_counts.py nests them under "counts"
    pre = {}
    out = Path(args.out) / "histories"
    cells = sorted({(a, l) for a, l, _ in idx})
    problems = 0
    for a, l in cells:
        seeds = sorted(s for aa, ll, s in idx if (aa, ll) == (a, l))
        Ws = []
        for s in seeds:
            W = decoder(idx[(a, l, s)], T.shape[1])
            fc = fires.get(f"{a}/l0-{l}/seed-{s}")
            kept, _ = mt.preprocess(W, fire_counts=fc)
            pre[f"{a}/l0-{l}/seed-{s}"] = dict(width=int(W.shape[0]), kept=int(kept.size),
                                               dead_checked=fc is not None)
            Ws.append(W[kept])
        cell = f"{a}_l0-{l}"
        runs = [dict(catcher=f"{a} L0={l} (zoo seed {s})", seed=s, role="estimation", status="ok")
                for s in seeds]
        # oracle: one Hungarian per SAE, thresholded at each tau_gt
        S = [mt.abs_cos(W, T) for W in Ws]
        assign = []
        for Si in S:
            from scipy.optimize import linear_sum_assignment
            r, c = linear_sum_assignment(-Si)
            assign.append((r, c, Si[r, c]))
        for tg in TAU_GT:
            X = np.zeros((T.shape[0], len(Ws)), np.int8)
            for k, (r, c, s) in enumerate(assign):
                X[c[s >= tg], k] = 1
            items = {str(i): dict(planted=True, covariates=dict(p=float(p[i]))) for i in range(T.shape[0])}
            d = out / f"oracle_tgt{tg}" / cell
            write_cell(d, cell, X, [str(i) for i in range(T.shape[0])], "oracle", runs=runs, items=items)
            problems += bool(check_cell(d))
        # matched: M1 sweep from one assignment per seed pair
        sw = mt.sweep(Ws, TAU_M)
        for tau, (X, _) in sw.items():
            d = out / f"matched_M1_tau{tau:.2f}" / cell
            write_cell(d, cell, X, [f"c{i}" for i in range(X.shape[0])], f"matched:M1@{tau:.2f}", runs=runs)
            problems += bool(check_cell(d))
        print(cell, "done", flush=True)
    (Path(args.out) / "preprocessing.json").write_text(json.dumps(pre, indent=1) + "\n")
    if not fires:
        print("WARNING: no --fire-counts given: dead latents were not removed (E02 §2 asks for it)")
    print(f"{len(cells)} cells written to {out}; cells failing check_cell: {problems}")
    return 1 if problems else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["inventory", "histories"])
    ap.add_argument("--world", default=WORLD_REPO)
    ap.add_argument("--zoo", default=ZOO_REPO)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fire-counts", default=None, help="JSON of per-latent firing counts (dead-latent removal)")
    a = ap.parse_args()
    sys.exit(inventory(a) if a.step == "inventory" else histories(a))


if __name__ == "__main__":
    main()
