"""E02 analysis (R004): estimators and evaluation on the zoo histories.

    python analysis/e02/evaluate.py --hist results/E02/E02-R00X/histories --out results/E02/E02-R004 \
        [--tau-gt 0.7] [--tau 0.70] [--B 1000] [--N-in 4096]

Implements E02 §2 (with D-010 intervals):
- U per architecture: features caught (oracle, tau_gt) by at least one SAE of
  that architecture over all its L0 cells (the reference pool); pi~_i = catch
  rate over the pool. Leave-cell-out variant: the pool without the cell.
- True C(K) of a cell = sum of pi~ over features caught by the cell's seeds /
  sum over U.
- Per cell and history type (oracle; matched M1 at tau): C_hat with its
  realized-coverage interval, Chao2 against |U|, N_in and N_all, leave-one-
  seed-out Delta_hat(1) against the features first found by the held-out
  seed (oracle only), Chapman for every seed pair.
- H2a-H2d, with Wilson 95% intervals for cell shares.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402
from crsafety.histories import read_cell  # noqa: E402


def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - h, c + h)


def oracle_matrix(cell, n_features):
    """Full features x seeds matrix (features never caught are zero rows)."""
    X = np.zeros((n_features, cell.X.shape[1]), np.int8)
    X[[int(i) for i in cell.item_ids]] = cell.X
    return X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hist", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tau-gt", type=float, default=0.7)
    ap.add_argument("--tau", default="0.70")
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--N-in", type=int, default=4096)
    ap.add_argument("--seed", type=int, default=20261024)  # 20261022 + 2
    a = ap.parse_args()
    hist, out = Path(a.hist), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    odir = hist / f"oracle_tgt{a.tau_gt}"
    mdir = hist / f"matched_M1_tau{a.tau}"
    cells = sorted(p.name for p in odir.iterdir() if p.is_dir())
    first = read_cell(odir / cells[0])
    n_all = len(first.items) if first.items else None
    if n_all is None:
        sys.exit("oracle cells need items.csv (all true features)")
    orc = {c: oracle_matrix(read_cell(odir / c), n_all) for c in cells}
    arch = {c: c.split("_l0-")[0] for c in cells}
    rows = []
    ss = np.random.SeedSequence(a.seed)
    seeds = dict(zip(cells, ss.spawn(len(cells))))
    for c in cells:
        pool = [orc[x] for x in cells if arch[x] == arch[c]]
        pool_lco = [orc[x] for x in cells if arch[x] == arch[c] and x != c]
        X = orc[c]
        K = X.shape[1]
        r = dict(cell=c, arch=arch[c], K=K, N_all=n_all, N_in=a.N_in)
        for tag, P in (("", pool), ("_lco", pool_lco)):
            if not P:
                continue
            Pm = np.hstack(P)
            pit = Pm.mean(axis=1)
            U = pit > 0
            found = X.any(axis=1)
            r[f"U{tag}"] = int(U.sum())
            r[f"C{tag}"] = float(pit[found & U].sum() / pit[U].sum())
        s_cov, s_m = seeds[c].spawn(2)
        for kind, M in (("oracle", X[X.any(axis=1)]), ("matched", None)):
            if kind == "matched":
                if not (mdir / c).exists():
                    continue
                M = read_cell(mdir / c).X
                M = M[M.any(axis=1)]
            d = IncidenceData.from_matrix(M)
            ci = cr.coverage_interval(d, B=a.B, seed=s_cov if kind == "oracle" else s_m)
            est, se, lo, hi = cr.chao2_ci(d)
            r.update({f"{kind}_S": d.S, f"{kind}_Q1": d.Q(1), f"{kind}_Q2": d.Q(2),
                      f"{kind}_C_hat": ci["estimate"], f"{kind}_C_lo": ci["interval"][0],
                      f"{kind}_C_hi": ci["interval"][1], f"{kind}_chao2": est,
                      f"{kind}_chao2_lo": lo, f"{kind}_chao2_hi": hi,
                      f"{kind}_jack2": cr.jackknife(d, 2), f"{kind}_ichao2": cr.ichao2(d),
                      f"{kind}_chapman_min": float(np.min(cr.chapman_pairs(d))) if K > 1 else np.nan,
                      f"{kind}_chapman_max": float(np.max(cr.chapman_pairs(d))) if K > 1 else np.nan})
        # leave-one-seed-out Delta_hat(1) (oracle identity)
        errs = []
        for k in range(K):
            rest = np.delete(X, k, axis=1)
            seen = rest.any(axis=1)
            new = int((X[:, k].astype(bool) & ~seen).sum())
            pred = cr.extrapolate(IncidenceData.from_matrix(rest[seen]), 1)
            errs.append((pred - new) / max(new, 1))
        r["loo_delta_rel_err_median"] = float(np.median(errs))
        r["loo_delta_rel_err_abs_median"] = float(np.median(np.abs(errs)))
        rows.append(r)

    with open(out / "cells.csv", "w", newline="") as f:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(f, keys, restval="")
        w.writeheader()
        w.writerows(rows)

    n = len(rows)
    err_o = np.array([r["oracle_C_hat"] - r["C"] for r in rows])
    ok_a = int((np.abs(err_o) <= 0.05).sum())
    lo_a, hi_a = wilson(ok_a, n)
    h2b_u = int(sum(r["oracle_chao2"] < r["U"] for r in rows))
    h2b_all = all(r["oracle_chao2"] < 0.5 * r["N_all"] for r in rows)
    have_m = [r for r in rows if "matched_C_hat" in r]
    ratio = (np.median([abs(r["matched_C_hat"] - r["C"]) / max(abs(r["oracle_C_hat"] - r["C"]), 1e-12)
                        for r in have_m]) if have_m else np.nan)
    loo = float(np.median([r["loo_delta_rel_err_abs_median"] for r in rows]))
    H = [
        dict(id="H2a", estimate=f"{ok_a}/{n} cells with |C_hat - C| <= 0.05 (Wilson {lo_a:.2f}-{hi_a:.2f})",
             verdict="supported" if ok_a / n >= 0.8 else ("not supported" if ok_a / n < 0.7 else "inconclusive")),
        dict(id="H2b", estimate=f"Chao2 < |U| in {h2b_u}/{n}; Chao2 < 0.5 N_all in all cells: {h2b_all}",
             verdict="supported" if (h2b_u / n >= 0.9 and h2b_all) else "not supported"),
        dict(id="H2c", estimate=f"median |err matched| / |err oracle| = {ratio:.2f} ({len(have_m)} cells)",
             verdict="supported" if ratio >= 2 else ("not supported" if ratio < 1.25 else "inconclusive")),
        dict(id="H2d", estimate=f"median |relative error| of leave-one-out Delta_hat(1) = {loo:.3f}",
             verdict="supported" if loo <= 0.2 else ("not supported" if loo > 0.4 else "inconclusive")),
    ]
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2) + "\n")
    L = ["# E02 evaluation", "", f"{n} cells; tau_gt = {a.tau_gt}; matched = M1 at tau = {a.tau}.", "",
         "| ID | Estimate | Verdict |", "|---|---|---|"] + \
        [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H] + \
        ["", "| cell | K | |U| | C | Ĉ oracle (95% CI) | Ĉ matched | Chao2 oracle | Chao2 matched |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['cell']} | {r['K']} | {r['U']} | {r['C']:.3f} | {r['oracle_C_hat']:.3f} "
                 f"({r['oracle_C_lo']:.3f}–{r['oracle_C_hi']:.3f}) | {r.get('matched_C_hat', np.nan):.3f} | "
                 f"{r['oracle_chao2']:.0f} | {r.get('matched_chao2', np.nan):.0f} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:9]))


if __name__ == "__main__":
    main()
