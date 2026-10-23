"""E15-R005 pilot (declared, exploratory): does planted-mark calibration beat Chao-Jost at audit sizes?

    python analysis/e15/pilot_sim.py [--reps 500] [--out results/E15/E15-R005] [--record]

Simulated audits with known truth:
- Each real item has a covariate x ~ N(0, 1) (e.g. subtlety) and per-run
  detectability pi = expit(b0 + b1 x), with b1 in {1, 2} (heterogeneity) and
  b0 set so that the mean pi is about 0.25.
- K = 8 runs. N_real in {14, 20, 50}. M marks drawn from the same law, with
  M in {6, 20, 100} (6 is the E15 audit-arm design).
- The covariate of real items is seen exactly or with noise sd 0.5.
- C is the realized coverage of the found real items. C_cal comes from
  `crsafety.calibrate` (fit on marks, Horvitz-Thompson on the found real
  items) and C_CJ is Chao-Jost on the real items' history.
Seeds: SeedSequence(20261037, spawn_key=(9000 + cell, replicate)).
Reports per cell: mean |C_cal - C| and |C_CJ - C| with MCSE, the error
reduction (the H15b measure), the share of replicates where calibration is
closer, and failures (fit not converged, no singletons or doubletons).
"""

import argparse
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety import calibrate as cb  # noqa: E402

MASTER = 20261037
K = 8
GRID = list(itertools.product((14, 20, 50), (6, 20, 100), (1.0, 2.0), (0.0, 0.5)))  # N, M, b1, cov noise


def b0_for(b1, target=0.25):
    x = np.random.default_rng(0).normal(size=200_000)
    lo, hi = -10.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if (1 / (1 + np.exp(-(mid + b1 * x)))).mean() < target else (lo, mid)
    return (lo + hi) / 2


def one(cell, rep, N, M, b1, noise, b0):
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(9000 + cell, rep)))
    pi_of = lambda x: 1 / (1 + np.exp(-(b0 + b1 * x)))  # noqa: E731
    xr = rng.normal(size=N)
    pr = pi_of(xr)
    Xr = (rng.random((N, K)) < pr[:, None]).astype(int)
    found = Xr.any(axis=1)
    C = pr[found].sum() / pr.sum()
    xm = rng.normal(size=M)
    ym = rng.binomial(K, pi_of(xm))
    out = dict(C=C, S=int(found.sum()))
    out["cj"] = cr.coverage(Xr[found]) if found.sum() >= 1 else np.nan
    beta, ok = cb.fit_detectability(xm, ym, K)
    if ok and found.any():
        z = xr[found] + rng.normal(0, noise, found.sum()) if noise else xr[found]
        out["cal"] = cb.calibrated(cb.predict(beta, z), K)["C_cal"]
    else:
        out["cal"] = np.nan
    out["fit_ok"] = bool(ok)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--out", default=str(ROOT / "results/E15/E15-R005"))
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = None
    if a.record:
        from crsafety import manifest
        m = manifest.start(out.name, "E15", " ".join(sys.argv), dict(grid=GRID, K=K, reps=a.reps),
                           seeds=dict(master=MASTER, rule="spawn_key=(9000 + cell, replicate)"),
                           prereg=dict(frozen=False, note="declared exploratory pilot"))
    t0 = time.time()
    b0 = {b1: b0_for(b1) for b1 in (1.0, 2.0)}
    rows = []
    for ci, (N, M, b1, noise) in enumerate(GRID):
        R = [one(ci, j, N, M, b1, noise, b0[b1]) for j in range(a.reps)]
        ec = np.array([abs(r["cal"] - r["C"]) for r in R])
        ej = np.array([abs(r["cj"] - r["C"]) for r in R])
        both = np.isfinite(ec) & np.isfinite(ej)
        mc, mj = ec[both].mean(), ej[both].mean()
        rows.append(dict(N=N, M=M, b1=b1, cov_noise=noise, reps=a.reps, both_finite=int(both.sum()),
                         fit_failed=int(sum(not r["fit_ok"] for r in R)),
                         abs_err_cal=float(mc), abs_err_cal_mcse=float(ec[both].std(ddof=1) / np.sqrt(both.sum())),
                         abs_err_cj=float(mj), abs_err_cj_mcse=float(ej[both].std(ddof=1) / np.sqrt(both.sum())),
                         bias_cal=float(np.mean([r["cal"] - r["C"] for r in R if np.isfinite(r["cal"])])),
                         bias_cj=float(np.mean([r["cj"] - r["C"] for r in R if np.isfinite(r["cj"])])),
                         reduction=float((mj - mc) / mj), share_cal_closer=float((ec[both] < ej[both]).mean())))
    (out / "cells.json").write_text(json.dumps(rows, indent=1) + "\n")
    L = ["# E15-R005 pilot (declared, exploratory): calibration vs Chao-Jost at audit sizes", "",
         f"K = {K}, {a.reps} replicates per cell, mean detectability about 0.25. Mean |error| (MCSE); "
         "reduction = 1 − |cal| / |CJ| (the H15b measure, ≥ 30% supports).", "",
         "| N real | M marks | slope b1 | cov. noise | \\|C_cal − C\\| | \\|C_CJ − C\\| | reduction | cal closer | bias cal | bias CJ | fit failed |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['N']} | {r['M']} | {r['b1']:.0f} | {r['cov_noise']} | {r['abs_err_cal']:.3f} ({r['abs_err_cal_mcse']:.3f}) | "
                 f"{r['abs_err_cj']:.3f} ({r['abs_err_cj_mcse']:.3f}) | {r['reduction']:+.0%} | {r['share_cal_closer']:.2f} | "
                 f"{r['bias_cal']:+.3f} | {r['bias_cj']:+.3f} | {r['fit_failed']} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"{time.time() - t0:.0f} s")
    if m is not None:
        manifest.finish(m, outputs=[(out / x).resolve().relative_to(ROOT) for x in ("cells.json", "summary.md")],
                        status="succeeded", wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
