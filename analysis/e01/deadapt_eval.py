"""E01-R009 (exploratory): how de-adaptation (A3a, A3b) behaves, before E10 uses it.

    python analysis/e01/deadapt_eval.py [--n 500] [--workers 4] [--out DIR]

Part 1, run level: the E01 cells base, beh0.5 and beh2 (same datasets as
E01-R001/R002, regenerated from their seeds). Rows of W are runs. Compares
naive C_hat, A3a and A3b (p_reset = 1) coverage with the true C.

Part 2, attempt level (the E10 situation: adaptation inside one red-team
session): M = 20 blind spots with per-attempt discovery probabilities 5 x
0.05, 10 x 0.015, 5 x 0.004; B = 200 attempts. Adaptive sessions multiply a
blind spot's probability by c (capped at 0.9) once it has been found ("exploit
what worked"). Truth: the probability that the next attempt finds a new blind
spot, sum of q_i over unfound blind spots. Estimators: Chao's rate on the
attempt incidence matrix, A3a, A3b. Seeds for part 2:
SeedSequence(20261022, spawn_key=(9100 + arm, session)).
"""

import argparse
import csv
import gzip
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import crsafety as cr
from crsafety import deadapt as da
from crsafety import manifest
from crsafety.estimators import IncidenceData
from crsafety.sim import Cell, simulate

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "configs" / "e01" / "cells.json").read_text())
MASTER = CFG["master_seed"]
RUN_CELLS = ("base", "beh0.5", "beh2")
ARMS = {"non-adaptive": 1.0, "adaptive c=3": 3.0, "adaptive c=10": 10.0}
Q = np.array([0.05] * 5 + [0.015] * 10 + [0.004] * 5)
B = 200


def run_level(task):
    cid, r = task
    c = next(x for x in CFG["cells"] if x["id"] == cid)
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(c["idx"], r)))
    s = simulate(Cell(**c["params"]), rng)
    W = s["X"].T  # runs x items (rows in run order)
    W = W[:, W.any(axis=0)]
    d = IncidenceData.from_matrix(W.T)
    return dict(part="run", cell=cid, rep=r, C=s["C"], naive=cr.coverage(d),
                A3a=da.deadapted_coverage(W, "A3a", seed=r),
                A3b=da.deadapted_coverage(W, "A3b", seed=r))


def session(task):
    ai, arm, j = task
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(9100 + ai, j)))
    c = ARMS[arm]
    q = Q.copy()
    found = np.zeros(Q.size, bool)
    W = np.zeros((B, Q.size), np.int8)
    for t in range(B):
        hit = rng.random(Q.size) < q
        W[t] = hit
        new = hit & ~found
        found |= hit
        if c != 1.0 and new.any():
            q[new] = np.minimum(q[new] * c, 0.9)
    truth = float(Q[~found].sum())
    cols = W[:, W.any(axis=0)]
    d = IncidenceData.from_matrix(cols.T) if cols.size else None
    naive = da.chao_rate(d.Q(1), d.Q(2), B, add_one=True) if d else np.nan
    return dict(part="attempt", cell=arm, rep=j, truth=truth, naive=naive,
                A3a=da.liyanage(W, seed=j), A3b=da.reset_rate(W, seed=j), found=int(found.sum()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / "results" / "E01" / "E01-R009"
    out.mkdir(parents=True, exist_ok=True)
    m = None
    if a.out is None:
        m = manifest.start("E01-R009", "E01", " ".join(sys.argv),
                           dict(run_cells=RUN_CELLS, arms=ARMS, q=Q.tolist(), B=B, n=a.n,
                                alpha=0.11, beta=0.5, exploratory=True),
                           seeds=dict(master=MASTER, rule="run level: E01 cell seeds; attempt level: spawn_key=(9100 + arm, session)"),
                           prereg=dict(frozen=False, note="exploratory addition (de-adaptation, H8)"))
    t0 = time.time()
    tasks1 = [(c, r) for c in RUN_CELLS for r in range(a.n)]
    tasks2 = [(ai, arm, j) for ai, arm in enumerate(ARMS) for j in range(a.n)]
    with Pool(a.workers) as pool:
        rows = pool.map(run_level, tasks1, chunksize=10) + pool.map(session, tasks2, chunksize=10)
    with gzip.open(out / "replicates.csv.gz", "wt", newline="") as f:
        keys = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(f, keys, restval="")
        w.writeheader()
        w.writerows(rows)
    L = ["# E01-R009 (exploratory): de-adaptation A3a / A3b", "",
         f"{a.n} replicates per cell or arm; wall {time.time() - t0:.0f} s.", "",
         "## Run level: coverage, mean(estimate − C) (MCSE)", "",
         "| cell | naive Ĉ | A3a | A3b |", "|---|---|---|---|"]
    for cid in RUN_CELLS:
        rs = [r for r in rows if r["part"] == "run" and r["cell"] == cid]
        C = np.array([r["C"] for r in rs])
        cells = []
        for k in ("naive", "A3a", "A3b"):
            e = np.array([r[k] for r in rs]) - C
            e = e[np.isfinite(e)]
            cells.append(f"{e.mean():+.4f} ({e.std(ddof=1) / np.sqrt(e.size):.4f})")
        L.append(f"| {cid} | " + " | ".join(cells) + " |")
    L += ["", "## Attempt level: discovery rate of the next attempt, median log(estimate / truth) [10th, 90th pct]", "",
          "| arm | blind spots found (mean) | Chao (naive) | A3a | A3b |", "|---|---|---|---|---|"]
    for arm in ARMS:
        rs = [r for r in rows if r["part"] == "attempt" and r["cell"] == arm]
        tr = np.array([r["truth"] for r in rs])
        cells = []
        for k in ("naive", "A3a", "A3b"):
            v = np.array([r[k] for r in rs], float)
            ok = np.isfinite(v) & (v > 0) & (tr > 0)
            lr = np.log(v[ok] / tr[ok])
            cells.append(f"{np.median(lr):+.2f} [{np.quantile(lr, .1):+.2f}, {np.quantile(lr, .9):+.2f}] (n={ok.sum()})")
        L.append(f"| {arm} | {np.mean([r['found'] for r in rs]):.1f} | " + " | ".join(cells) + " |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if m is not None:
        manifest.finish(m, outputs=[(out / "replicates.csv.gz").relative_to(ROOT), (out / "summary.md").relative_to(ROOT)],
                        wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
