"""E11 analysis: matched histories of real-model SAEs, H11a (invariance) and H11c (null).

    python analysis/e11/analyse.py --root <train.py out> --out results/E11/E11-R00X \
        [--model pythia-70m-deduped] [--fire-counts fires.json] [--tau plateau|<x>] \
        [--layer2-root <root of a second layer>] [--ladder-chat <json {"C_hat": x}>] [--B 1000]

Reads `<root>/seeds/<model>/l0-32/seed-<k>` (0-7 independent, 8-11 shared
data order) and `<root>/null/<model>/l0-32/seed-<k>`. Latents are
preprocessed (dead latents dropped with --fire-counts, within-SAE duplicates
merged) and matched with M1 (Hungarian on |decoder cos|) and components over
all seed pairs, at --tau or the plateau rule (E03; TAUS 0.30-0.95 by 0.01).
- Histories (PROTOCOLS §10) are written to <out>/histories/<unit>/.
- Units for H11a: the 8 independent seeds at the plateau midpoint, at the
  plateau's two ends, a second layer (if given) and the Gemma Scope ladder
  (if given, from R004). H11a: max |C_hat_a - C_hat_b| <= 0.05 supported,
  > 0.10 not supported.
- Dependence (secondary): C_hat of the 4 shared-order seeds vs the mean C_hat
  over all 4-subsets of the independent seeds.
- H11c: recapture rate (share of a seed's latents matched in another seed at
  the same tau), averaged over seed pairs, trained vs random-model null;
  95% CI of the difference by bootstrap over seeds. Supported if higher
  with the CI excluding 0.
The E11 §2 estimand weights coverage by activation mass above f_min = 1e-6.
This script reports the unweighted C_hat and drops latents firing below
f_min when --fire-counts gives counts (E11 §2a).
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "analysis" / "e02"))

import crsafety as cr  # noqa: E402
from crsafety import matching as mt  # noqa: E402
from crsafety.histories import check_cell, write_cell  # noqa: E402

TAUS = np.round(np.arange(0.30, 0.951, 0.01), 2)
F_MIN = 1e-6


def load_set(d, fires=None, n_samples=None):
    import zoo
    out = {}
    for f in sorted(Path(d).glob("seed-*/sae_weights.safetensors")):
        k = int(f.parent.name.split("-")[1])
        t = zoo.load_tensors(f)
        W = t[next(x for x in t if x.endswith("W_dec"))].astype(np.float64)
        fc = (fires or {}).get(str(f.parent.relative_to(Path(d).parents[2])))
        if fc is not None and n_samples:
            fc = np.where(np.asarray(fc) / n_samples >= F_MIN, fc, 0)
        kept, _ = mt.preprocess(W, fire_counts=fc)
        out[k] = W[kept]
    return out


def cluster(dirs, tau):
    if tau == "plateau":
        sw = mt.sweep(dirs, TAUS)
        iv = mt.plateau(TAUS, [sw[float(x)][0].shape[0] for x in TAUS], return_interval=True)
        if iv is None:
            return None
        lo, mid, hi = iv
        X = {n: mt.cluster_seeds(dirs, t)[0] for n, t in (("lo", lo), ("mid", mid), ("hi", hi))}
        return dict(mid=mid, lo=lo, hi=hi, X=X)
    X, _ = mt.cluster_seeds(dirs, float(tau))
    return dict(mid=float(tau), lo=float(tau), hi=float(tau), X={"mid": X, "lo": X, "hi": X})


def chat(X, B, seed):
    det = X[X.any(axis=1)]
    if det.shape[0] < 2:
        return dict(estimate=np.nan, interval=(np.nan, np.nan))
    ci = cr.coverage_interval(det, B=B, seed=seed) if B else dict(estimate=cr.coverage(det), interval=(np.nan,) * 2)
    return dict(estimate=float(ci["estimate"]), interval=[float(v) for v in ci["interval"]])


def recapture(dirs, tau):
    keys = sorted(dirs)
    rates = {}
    for a, b in combinations(keys, 2):
        m, sc = mt.hungarian(dirs[a], dirs[b], tau)
        rates[(a, b)] = len(m) / min(dirs[a].shape[0], dirs[b].shape[0])
    return rates


def boot_diff(rt, rn, keys_t, keys_n, B, rng):
    def mean_rate(rates, keys):
        v = [rates[(min(a, b), max(a, b))] for a, b in combinations(keys, 2) if a != b]
        return np.mean(v) if v else np.nan
    d = []
    for _ in range(B):
        kt = rng.choice(keys_t, len(keys_t), replace=True)
        kn = rng.choice(keys_n, len(keys_n), replace=True)
        d.append(mean_rate(rt, kt) - mean_rate(rn, kn))
    d = np.array(d, float)
    d = d[np.isfinite(d)]
    return [float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))] if d.size else [np.nan, np.nan]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="pythia-70m-deduped")
    ap.add_argument("--fire-counts")
    ap.add_argument("--tau", default="plateau")
    ap.add_argument("--layer2-root")
    ap.add_argument("--ladder-chat")
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261033)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    raw = json.loads(Path(a.fire_counts).read_text()) if a.fire_counts else {}
    fires, ns = raw.get("counts", raw), raw.get("samples")
    ss = np.random.SeedSequence(a.seed)
    sub = lambda root, s: Path(root) / s / a.model / "l0-32"  # noqa: E731
    trained = load_set(sub(a.root, "seeds"), fires, ns)
    ind = {k: v for k, v in trained.items() if k < 8}
    shared = {k: v for k, v in trained.items() if k >= 8}
    res = dict(n_independent=len(ind), n_shared=len(shared))
    cl = cluster([ind[k] for k in sorted(ind)], a.tau)
    if cl is None:
        res["status"] = "no plateau: no trustworthy threshold (E03 rule)"
        (out / "summary.json").write_text(json.dumps(res, indent=2) + "\n")
        print(res)
        return
    tau = cl["mid"]
    res.update(tau=tau, plateau=[cl["lo"], cl["hi"]])
    units = {}
    for name in ("mid", "lo", "hi"):
        X = cl["X"][name]
        d = out / "histories" / f"seeds_tau-{name}"
        write_cell(d, f"E11_seeds_{name}", X, [f"c{i}" for i in range(X.shape[0])], f"matched:M1@{cl[name]:.2f}",
                   runs=[dict(catcher=f"{a.model} SAE seed {k}", seed=k, status="ok", role="estimation")
                         for k in sorted(ind)])
        assert not check_cell(d)
        units[f"seeds @ tau {name} ({cl[name]:.2f})"] = chat(X, a.B, ss.spawn(1)[0])
    if a.layer2_root:
        l2 = load_set(sub(a.layer2_root, "seeds"), fires, ns)
        X2, _ = mt.cluster_seeds([l2[k] for k in sorted(l2) if k < 8], tau)
        units["second layer"] = chat(X2, a.B, ss.spawn(1)[0])
    if a.ladder_chat:
        units["Gemma Scope ladder (R004)"] = dict(estimate=json.loads(Path(a.ladder_chat).read_text())["C_hat"])
    est = {k: v["estimate"] for k, v in units.items() if np.isfinite(v["estimate"])}
    gap = max((abs(x - y) for x, y in combinations(est.values(), 2)), default=np.nan)
    res["units"] = units
    res["H11a"] = dict(max_gap=gap, verdict="supported" if gap <= 0.05 else
                       ("not supported" if gap > 0.10 else "inconclusive"),
                       note="only threshold units present" if len(est) <= 3 else "")
    if len(shared) >= 2:
        Xs, _ = mt.cluster_seeds([shared[k] for k in sorted(shared)], tau)
        c4 = [chat(mt.cluster_seeds([ind[k] for k in s], tau)[0], 0, None)["estimate"]
              for s in combinations(sorted(ind), len(shared))]
        res["dependence"] = dict(C_hat_shared_order=chat(Xs, 0, None)["estimate"],
                                 C_hat_independent_subsets_mean=float(np.nanmean(c4)) if c4 else np.nan,
                                 K=len(shared))
    nd = sub(a.root, "null")
    if nd.exists():
        null = load_set(nd, fires, ns)
        rt, rn = recapture(ind, tau), recapture(null, tau)
        mt_, mn = float(np.mean(list(rt.values()))), float(np.mean(list(rn.values())))
        ci = boot_diff(rt, rn, sorted(ind), sorted(null), 2000, np.random.default_rng(ss.spawn(1)[0]))
        res["H11c"] = dict(recapture_trained=mt_, recapture_null=mn, diff=mt_ - mn, ci95=ci,
                           verdict="supported" if mt_ > mn and ci[0] > 0 else "not supported")
    (out / "summary.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    print(json.dumps(res, indent=2, default=float))


if __name__ == "__main__":
    main()
