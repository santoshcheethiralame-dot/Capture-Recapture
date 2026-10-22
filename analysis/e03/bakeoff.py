"""E03 matcher bake-off and plateau diagnostic (R001 + R004; M3 needs activations, R002).

    python analysis/e03/bakeoff.py --out results/E03/E03-R00X [--world DIR|REPO] [--zoo DIR|REPO]
        [--truth leave-cell-out|pooled] [--B 0]

For every cell (arch, L0) of the SynthSAEBench zoo and matcher (M1 Hungarian
on |decoder cos|; M2 strict encoder+decoder agreement; M4 mutual nearest
neighbour) over tau in {0.30, ..., 0.95}:
- true identity of each latent: its oracle feature (GT-MCC at tau_gt = 0.7);
- pair precision / recall / F1 (overall and by quartile of the true
  feature's firing probability among caught features), ARI over latents with
  a true feature, ghost and merge rates, cluster count;
- downstream: C_hat from the matched history at each tau vs true C (D-011
  truth option), and Chao2.
Then the plateau rule picks tau per (cell, matcher) and H3a-H3c are evaluated.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "analysis" / "e02"))

import crsafety as cr  # noqa: E402
from crsafety import matching as mt  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402
import zoo  # noqa: E402

TAUS = tuple(np.round(np.arange(0.30, 0.951, 0.05), 2))


def load_cells(world, zoo_src, tau_gt):
    T, p, _ = zoo.load_world(zoo.local_dir(world))
    zdir = zoo.local_dir(zoo_src)
    idx = zoo.zoo_index(zdir)
    cells = {}
    for a, l, s in sorted(idx):
        from safetensors.numpy import load_file
        t = load_file(str(idx[(a, l, s)]))
        Wd = zoo.decoder(idx[(a, l, s)], T.shape[1])
        ek = next((k for k in t if k.endswith("W_enc")), None)
        We = None
        if ek is not None:
            We = t[ek].astype(np.float32)
            We = We.T if We.shape[0] == T.shape[1] else We
        kept, _ = mt.preprocess(Wd)
        Wd = Wd[kept]
        We = We[kept] if We is not None and We.shape[0] >= kept.max() + 1 else None
        caught, feat = mt.oracle_catch(Wd, T, tau_gt)
        cells.setdefault((a, l), []).append(dict(seed=s, dec=Wd, enc=We, feat=feat, caught=caught))
    return T, p, cells


def truth_C(cells, key, mode):
    """True coverage of a cell (E02 §2 / D-011): pi~ from the architecture pool,
    with or without the cell itself."""
    a, _ = key
    pool = [s["caught"] for k, ss in cells.items() if k[0] == a and (mode == "pooled" or k != key) for s in ss]
    if not pool:
        return np.nan
    pit = np.column_stack(pool).mean(axis=1)
    found = np.column_stack([s["caught"] for s in cells[key]]).any(axis=1)
    U = pit > 0
    return float(pit[found & U].sum() / pit[U].sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--world", default=zoo.WORLD_REPO)
    ap.add_argument("--zoo", default=zoo.ZOO_REPO)
    ap.add_argument("--tau-gt", type=float, default=0.7)
    ap.add_argument("--truth", choices=["leave-cell-out", "pooled"], default="leave-cell-out")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    T, p, cells = load_cells(a.world, a.zoo, a.tau_gt)
    rows = []
    for key, seeds in sorted(cells.items()):
        C = truth_C(cells, key, a.truth)
        dirs = [s["dec"] for s in seeds]
        true_lab = [s["feat"] for s in seeds]
        fp = np.concatenate([p[s["feat"][s["feat"] >= 0]] for s in seeds])
        qs = np.quantile(fp, [0.25, 0.5, 0.75]) if fp.size else np.zeros(3)
        matchers = {"M1": mt.hungarian, "M4": mt.mutual_nn}
        if all(s["enc"] is not None for s in seeds):
            encs = [s["enc"] for s in seeds]
            pos = {id(d): k for k, d in enumerate(dirs)}
            matchers["M2"] = lambda A, B, tau: mt.strict(A, B, encs[pos[id(A)]], encs[pos[id(B)]], tau)
        for mname, fn in matchers.items():
            sw = mt.sweep(dirs, TAUS, matcher=fn)
            for tau, (X, lab) in sw.items():
                sc = mt.pair_scores(lab, true_lab)
                quart = {}
                for qi in range(4):
                    lo = -np.inf if qi == 0 else qs[qi - 1]
                    hi = np.inf if qi == 3 else qs[qi]
                    tl = [np.where((f >= 0) & (p[np.maximum(f, 0)] >= lo) & (p[np.maximum(f, 0)] < hi), f, -1)
                          for f in true_lab]
                    pl = [np.where(t >= 0, l, -1 - np.arange(l.size)) for t, l in zip(tl, lab)]
                    quart[f"f1_q{qi + 1}"] = mt.pair_scores(pl, tl)["f1"]
                has = np.concatenate([f >= 0 for f in true_lab])
                ari = mt.ari(np.concatenate(lab)[has], np.concatenate(true_lab)[has]) if has.any() else np.nan
                Xo = X[X.any(axis=1)]
                d = IncidenceData.from_matrix(Xo)
                rows.append(dict(cell=f"{key[0]}_l0-{key[1]}", matcher=mname, tau=tau, n_clusters=int(X.shape[0]),
                                 precision=sc["precision"], recall=sc["recall"], f1=sc["f1"], **quart, ari=ari,
                                 ghost=1 - sc["recall"], merge=1 - sc["precision"], C=C,
                                 C_hat=cr.coverage(d), cov_err=abs(cr.coverage(d) - C), chao2=cr.chao2(d)))
        print(key, "done", flush=True)
    with open(out / "sweep.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    # plateau rule and hypotheses
    res = []
    for cell in sorted({r["cell"] for r in rows}):
        for m in sorted({r["matcher"] for r in rows if r["cell"] == cell}):
            rs = sorted([r for r in rows if r["cell"] == cell and r["matcher"] == m], key=lambda r: r["tau"])
            tp = mt.plateau([r["tau"] for r in rs], [r["n_clusters"] for r in rs])
            best = min(r["cov_err"] for r in rs)
            at = None if tp is None else min(rs, key=lambda r: abs(r["tau"] - tp))
            res.append(dict(cell=cell, matcher=m, plateau_tau=tp, err_at_plateau=None if at is None else at["cov_err"],
                            best_err=best, f1_top2=float(np.mean([max(r["f1_q3"], 0) for r in rs if r["tau"] == 0.7] +
                                                                 [max(r["f1_q4"], 0) for r in rs if r["tau"] == 0.7]))))
    by_m = {}
    for r in res:
        by_m.setdefault(r["matcher"], []).append(r)
    h3a = {m: float(np.median([r["f1_top2"] for r in rs])) for m, rs in by_m.items()}
    plat = [r for r in res if r["plateau_tau"] is not None and r["matcher"] == "M1"]
    nop = [r for r in res if r["plateau_tau"] is None and r["matcher"] == "M1"]
    share = np.mean([(r["err_at_plateau"] - r["best_err"]) <= 0.03 for r in plat]) if plat else np.nan
    H = [dict(id="H3a", estimate=f"median pair F1 (top two frequency quartiles, tau = 0.7) by matcher: {h3a}",
              verdict="supported" if max(h3a.values()) >= 0.9 else ("not supported" if max(h3a.values()) < 0.8 else "inconclusive")),
         dict(id="H3b", estimate=f"M1: plateau within 0.03 of best-tau error in {share:.2f} of {len(plat)} plateau cells",
              verdict="supported" if share >= 0.8 else ("not supported" if share < 0.6 else "inconclusive")),
         dict(id="H3c", estimate=(f"median C_hat error: no-plateau {np.median([r['best_err'] for r in nop]) if nop else float('nan'):.3f} "
                                  f"vs plateau {np.median([r['err_at_plateau'] for r in plat]) if plat else float('nan'):.3f}"),
              verdict="n/a (no cells without plateau)" if not nop or not plat else
              ("supported" if np.median([r['best_err'] for r in nop]) > np.median([r['err_at_plateau'] for r in plat]) else "not supported"))]
    (out / "plateau.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2) + "\n")
    print("\n".join(f"{h['id']}: {h['estimate']} -> {h['verdict']}" for h in H))


if __name__ == "__main__":
    main()
