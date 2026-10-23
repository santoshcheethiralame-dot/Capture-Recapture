"""E06-R014: histories -> estimators and H6a-H6e (CPU).

    python analysis/e06/analyse.py --root <dir> --out results/E06/E06-R014 [--truth reference|pooled]
        [--subsets 200] [--B 1000]

<dir>/<cell>/histories/oracle_tgt0.7/<cell>_l0-<L0>/ are the PROTOCOLS §10
cells written by `analysis/e02/zoo.py histories --reference-from 16` (16
evaluation + 8 reference seeds). Per E06 §2:
- U = features caught by any of the 24 seeds; N_true = all planted features.
- pi~: catch rate over the 8 reference seeds (``--truth reference``, D-011
  proposal; default) or over all 24 seeds (``pooled``, the E02-style §2
  reading). True C(K) for K in {4, 8, 16}: K = 16 uses all evaluation seeds,
  K = 4 and 8 use ``--subsets`` random subsets of them.
- C_hat (realized-coverage interval at K = 16), Chao2 vs |U| and N_true,
  Delta_hat(m) from the 16 evaluation seeds vs the features first found by the
  m = 8 reference seeds (§2 says Delta_hat(16), but only 8 reference seeds
  exist; see E06 §2a), n_eff/K and overlap at K = 16.
- H6a: |C_hat - C| <= 0.05 in >= 80% of cells at K = 8 (median over subsets)
  and at K = 16; < 70% not supported. H6b: |C_hat - C| hier+corr vs base.
  H6c: (C_hat - C) init-only minus base >= 0.03 (< 0.01 not). H6d: Chao2 /
  N_true in base < 0.5 (>= 0.8 not). H6e: median |rel. error of Delta_hat|
  <= 0.2 (> 0.4 not).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety import testbed as tb  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402


def chat(X):
    det = X[X.any(axis=1)]
    return cr.coverage(IncidenceData.from_matrix(det)) if det.shape[0] >= 2 else np.nan


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--truth", choices=["reference", "pooled"], default="reference")
    ap.add_argument("--subsets", type=int, default=200)
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261028)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ss = np.random.SeedSequence(a.seed)
    rows = {}
    for cdir in sorted(Path(a.root).glob("*/histories/oracle_tgt0.7/*")):
        c = tb.load(cdir)
        cid = cdir.parent.parent.parent.name
        Xe, Xr = c.X_est, c.X_ref
        pi = tb.true_pi(Xr if a.truth == "reference" else c.X_all)
        U = c.X_all.any(axis=1)
        rng = np.random.default_rng(ss.spawn(1)[0])
        r = dict(cell=cid, K_eval=Xe.shape[1], K_ref=Xr.shape[1], N_true=len(c.items), U=int(U.sum()),
                 truth=a.truth, mass_dropped=float(((pi == 0) & U).mean()))
        for K in (4, 8, 16):
            if K > Xe.shape[1]:
                continue
            subs = [np.arange(K)] if K == Xe.shape[1] else \
                [rng.choice(Xe.shape[1], K, replace=False) for _ in range(a.subsets)]
            errs = np.array([chat(Xe[:, s]) - tb.true_coverage(Xe[:, s], pi) for s in subs])
            r[f"err_K{K}_mean"] = float(np.nanmean(errs))
            r[f"abs_err_K{K}_median"] = float(np.nanmedian(np.abs(errs)))
        det = Xe[Xe.any(axis=1)]
        d = IncidenceData.from_matrix(det)
        ci = cr.coverage_interval(d, B=a.B, seed=ss.spawn(1)[0])
        new = int((Xr.any(axis=1) & ~Xe.any(axis=1)).sum())
        dh = cr.extrapolate(d, Xr.shape[1])
        r.update(C16=tb.true_coverage(Xe, pi), C_hat16=ci["estimate"], C_lo=ci["interval"][0], C_hi=ci["interval"][1],
                 chao2=cr.chao2(d), chao2_over_U=cr.chao2(d) / max(U.sum(), 1), chao2_over_Ntrue=cr.chao2(d) / len(c.items),
                 delta_ref=new, delta_hat=dh, delta_rel_err=(dh - new) / max(new, 1),
                 neff_over_K=tb.neff(Xe) / Xe.shape[1], overlap=tb.overlap_ratio(Xe))
        rows[cid] = r
    n = len(rows)
    share8 = np.mean([r.get("abs_err_K8_median", np.nan) <= 0.05 for r in rows.values()])
    share16 = np.mean([abs(r["C_hat16"] - r["C16"]) <= 0.05 for r in rows.values()])
    H = [dict(id="H6a", estimate=f"share of cells within 0.05: K=8 {share8:.2f}, K=16 {share16:.2f} ({n} cells)",
              verdict="supported" if min(share8, share16) >= 0.8 else ("not supported" if min(share8, share16) < 0.7 else "inconclusive"))]
    g = lambda c, k: rows[c][k] if c in rows else np.nan
    if "base" in rows and "hier+corr" in rows:
        b, s = abs(g("base", "C_hat16") - g("base", "C16")), abs(g("hier+corr", "C_hat16") - g("hier+corr", "C16"))
        H.append(dict(id="H6b", estimate=f"|C_hat - C| at K=16: hier+corr {s:.3f} vs base {b:.3f}",
                      verdict="supported" if s > b else "not supported"))
    if "base" in rows and "init-only" in rows:
        dlt = g("init-only", "err_K16_mean") - g("base", "err_K16_mean")
        H.append(dict(id="H6c", estimate=f"(C_hat - C) init-only minus base = {dlt:+.3f}",
                      verdict="supported" if dlt >= 0.03 else ("not supported" if dlt < 0.01 else "inconclusive")))
    if "base" in rows:
        v = g("base", "chao2_over_Ntrue")
        H.append(dict(id="H6d", estimate=f"Chao2 / N_true in base = {v:.3f}",
                      verdict="supported" if v < 0.5 else ("not supported" if v >= 0.8 else "inconclusive")))
    med = float(np.nanmedian([abs(r["delta_rel_err"]) for r in rows.values()]))
    H.append(dict(id="H6e", estimate=f"median |relative error| of Delta_hat(8) = {med:.3f}",
                  verdict="supported" if med <= 0.2 else ("not supported" if med > 0.4 else "inconclusive")))
    (out / "cells.json").write_text(json.dumps(rows, indent=1, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2) + "\n")
    L = ["# E06 analysis", "", f"{n} cells; truth = {a.truth}.", "",
         "| cell | |U| | C(16) | Ĉ(16) (95% CI) | median \\|Ĉ−C\\| K=8 | Chao2/N_true | Δ (8 ref seeds) | Δ̂ | n_eff/K |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows.values():
        L.append(f"| {r['cell']} | {r['U']} | {r['C16']:.3f} | {r['C_hat16']:.3f} ({r['C_lo']:.3f}–{r['C_hi']:.3f}) | "
                 f"{r.get('abs_err_K8_median', float('nan')):.3f} | {r['chao2_over_Ntrue']:.2f} | {r['delta_ref']} | "
                 f"{r['delta_hat']:.1f} | {r['neff_over_K']:.2f} |")
    L += ["", "| ID | estimate | verdict |", "|---|---|---|"] + [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
