"""E13 pilot (declared; simulated campaigns, not the E13 testbeds).

    python analysis/e13/pilot.py [--n 200] [--workers 4]

Each campaign is a fresh simulated world with K_max independent runs taken in
order (E13 proper permutes the runs of real testbeds). Seeds:
SeedSequence(20261035, spawn_key=(9000 + world, campaign)). Writes
results/E13/<run>/ (manifest.json, campaigns.csv.gz, summary.md).
"""

import argparse
import csv
import gzip
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from crsafety import manifest
from crsafety.sim import Cell, simulate
from crsafety.stopping import campaign

ROOT = Path(__file__).resolve().parents[2]
MASTER = 20261035
WORLDS = {
    "homog_K16": Cell(het="homog", sigma=0.0, K=16),
    "base_K16": Cell(K=16),
    "ln2_K16": Cell(sigma=2.0, K=16),
    "zipf0.5_K16": Cell(het="zipf", alpha=0.5, K=16),
    "base_K12_N20": Cell(N=20, K=12, mean_p=0.4),
    "fam1_K16": Cell(families=1, K=16),
}
B = 500


def one(task):
    wi, name, j = task
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(9000 + wi, j)))
    s = simulate(WORLDS[name], rng)
    rows = campaign(s["X"], s["pi"], range(WORLDS[name].K), B=B,
                    seed=np.random.SeedSequence(MASTER, spawn_key=(9000 + wi, j, 1)))
    for r in rows:
        r.update(world=name, campaign=j)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--run", default="E13-R003")
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / "results" / "E13" / a.run
    out.mkdir(parents=True, exist_ok=True)
    m = None
    if a.out is None:
        m = manifest.start(a.run, "E13", " ".join(sys.argv),
                           dict(worlds={k: v.to_dict() for k, v in WORLDS.items()}, n=a.n, B=B, pilot=True),
                           seeds=dict(master=MASTER, rule="spawn_key=(9000 + world, campaign[, 1])"),
                           prereg=dict(frozen=False, note="declared pilot on simulated campaigns"))
    t0 = time.time()
    tasks = [(wi, name, j) for wi, name in enumerate(WORLDS) for j in range(a.n)]
    with Pool(a.workers) as pool:
        rows = [r for part in pool.map(one, tasks, chunksize=4) for r in part]
    with gzip.open(out / "campaigns.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    L = [f"# {a.run} pilot (declared; simulated campaigns)", "",
         f"{a.n} campaigns per world; B = {B}; wall {time.time() - t0:.0f} s. Success = true C ≥ target at "
         "stopping; saved = share of K_max not run. Pilot output only.", "",
         "| world | target | rule | success | median runs saved | mean undershoot when failing |",
         "|---|---|---|---|---|---|"]
    for name in WORLDS:
        for t in (0.8, 0.9):
            for rule in ("R-point", "R-lower", "R-fixed"):
                rs = [r for r in rows if r["world"] == name and r["target"] == t and r["rule"] == rule]
                succ = np.mean([r["success"] for r in rs])
                fails = [r["undershoot"] for r in rs if not r["success"]]
                L.append(f"| {name} | {t} | {rule} | {succ:.3f} | {np.median([r['saved'] for r in rs]):.2f} | "
                         f"{np.mean(fails) if fails else 0:.3f} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if m is not None:
        manifest.finish(m, outputs=[(out / "campaigns.csv.gz").relative_to(ROOT),
                                    (out / "summary.md").relative_to(ROOT)],
                        wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
