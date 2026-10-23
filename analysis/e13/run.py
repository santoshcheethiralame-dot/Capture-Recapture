"""E13-R001: stopping rules on the testbeds' run histories (CPU; after the v1 freeze).

    python analysis/e13/run.py --testbed E02:<e02>/histories/oracle_tgt0.7/* \
        --testbed E06:<e06>/*/histories/oracle_tgt0.7/* --testbed E09:<dir>/* \
        --testbed E10-A1:<dir> --testbed E10-A2:<dir>:adaptive [--perms 1000] [--B 1000] [--workers 4]
    ... --out <scratchpad> --perms 3 --B 50           # smoke test: no manifest, pilot seed keys

Each --testbed is NAME:GLOB[:adaptive]; every directory the glob matches is a
PROTOCOLS §10 cell. Choices E13 §2 leaves open (E13 §2a):
- A campaign is a random order of the cell's *estimation* runs (K_max = their
  number).
- True detectability pi_i is the catch rate over the cell's *reference*
  runs, as §2 says. Cells without reference runs (E02) use the catch rate
  over all their runs and are flagged.
- The rules come from `crsafety.stopping` (R-point, R-lower with the
  realized-coverage lower bound, R-fixed), with targets 0.8 and 0.9 and
  k >= 3.
- Seeds: SeedSequence(20261035, spawn_key=(testbed, cell, permutation)).
  Smoke tests add 9000 to the permutation key.
Summary (H13a-d):
- H13a: R-lower success at c* = 0.9, pooled over non-adaptive testbeds with
  K_max >= 6, with a 95% CI from a bootstrap over cells.
- H13b: median runs saved by R-lower at 0.9 on the same set.
- H13c: R-point vs R-lower success on the same set.
- H13d: R-lower success at 0.9, E10-A2 vs E10-A1.
"""

import argparse
import csv
import gzip
import json
import sys
import time
from glob import glob
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from crsafety import manifest, testbed
from crsafety.stopping import campaign

ROOT = Path(__file__).resolve().parents[2]
MASTER = 20261035
TARGETS = (0.8, 0.9)


def parse(spec):
    parts = spec.split(":")
    name, pattern = parts[0], parts[1]
    return name, sorted(p for p in glob(pattern) if (Path(p) / "runs.csv").exists()), "adaptive" in parts[2:]


def one(task):
    ti, tname, ci, cdir, X, pi, perm_key, B = task
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(ti, ci, perm_key)))
    order = rng.permutation(X.shape[1])
    res = campaign(X, pi, order, targets=TARGETS, B=B, seed=np.random.SeedSequence(MASTER, spawn_key=(ti, ci, perm_key, 1)))
    return [dict(testbed=tname, cell=cdir, perm=perm_key, K_max=X.shape[1], **r) for r in res]


def boot_cells(rows, stat, B=2000, seed=0):
    cells = sorted({r["cell"] for r in rows})
    by = {c: [r for r in rows if r["cell"] == c] for c in cells}
    rng = np.random.default_rng(seed)
    v = []
    for _ in range(B):
        pick = rng.choice(len(cells), len(cells), replace=True)
        v.append(stat([r for i in pick for r in by[cells[i]]]))
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]


def summarise(rows, meta):
    sel = lambda rule, t, ok: [r for r in rows if r["rule"] == rule and r["target"] == t and ok(r)]  # noqa: E731
    pooled = lambda r: not meta[r["testbed"]]["adaptive"] and r["K_max"] >= 6  # noqa: E731
    succ = lambda rs: float(np.mean([r["success"] for r in rs])) if rs else np.nan  # noqa: E731
    H = []
    lo = sel("R-lower", 0.9, pooled)
    pt = sel("R-point", 0.9, pooled)
    if lo:
        s = succ(lo)
        H.append(dict(id="H13a", estimate=f"R-lower success at 0.9 = {s:.3f} (95% CI {boot_cells(lo, succ)}) over "
                      f"{len({r['cell'] for r in lo})} cells", verdict="supported" if s >= 0.8 else
                      ("not supported" if s < 0.7 else "inconclusive")))
        med = float(np.median([r["saved"] for r in lo]))
        H.append(dict(id="H13b", estimate=f"median runs saved by R-lower at 0.9 = {med:.0%}",
                      verdict="supported" if med >= 0.3 else ("not supported" if med < 0.1 else "inconclusive")))
        sp = succ(pt)
        H.append(dict(id="H13c", estimate=f"success at 0.9: R-point {sp:.3f} vs R-lower {s:.3f}",
                      verdict="supported" if sp < s else "not supported"))
    a1 = sel("R-lower", 0.9, lambda r: r["testbed"] == "E10-A1")
    a2 = sel("R-lower", 0.9, lambda r: r["testbed"] == "E10-A2")
    if a1 and a2:
        H.append(dict(id="H13d", estimate=f"R-lower success at 0.9: A2 {succ(a2):.3f} vs A1 {succ(a1):.3f}",
                      verdict="supported" if succ(a2) < succ(a1) else "not supported"))
    per = {}
    for tb_ in sorted({r["testbed"] for r in rows}):
        for rule in ("R-point", "R-lower", "R-fixed"):
            for t in TARGETS:
                rs = sel(rule, t, lambda r, tb_=tb_: r["testbed"] == tb_)
                per[f"{tb_}|{rule}|{t}"] = dict(success=succ(rs), median_saved=float(np.median([r["saved"] for r in rs])),
                                                mean_undershoot_when_failed=float(np.mean([r["undershoot"] for r in rs if not r["success"]] or [0])))
    return H, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testbed", action="append", required=True)
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / "results" / "E13" / "E13-R001"
    out.mkdir(parents=True, exist_ok=True)
    k0 = 0 if a.out is None else 9000
    meta, tasks = {}, []
    for ti, spec in enumerate(a.testbed):
        name, dirs, adaptive = parse(spec)
        meta[name] = dict(adaptive=adaptive, cells=dirs, pi_from=[])
        for ci, d in enumerate(dirs):
            c = testbed.load(d)
            X = c.X_est
            pi = testbed.true_pi(c.X_ref) if c.X_ref.shape[1] else testbed.true_pi(c.X_all)
            meta[name]["pi_from"].append("reference" if c.X_ref.shape[1] else "all runs (no reference runs)")
            tasks += [(ti, name, ci, d, X, pi, k0 + j, a.B) for j in range(a.perms)]
    m = None
    if a.out is None:
        m = manifest.start("E13-R001", "E13", " ".join(sys.argv), dict(testbeds=a.testbed, perms=a.perms, B=a.B,
                           targets=TARGETS), seeds=dict(master=MASTER, rule="spawn_key=(testbed, cell, permutation)"),
                           confirmatory=True, prereg=dict(version="v1.0"))
    t0 = time.time()
    with Pool(a.workers) as pool:
        rows = [r for rs in pool.map(one, tasks, chunksize=8) for r in rs]
    with gzip.open(out / "campaigns.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    H, per = summarise(rows, meta)
    (out / "summary.json").write_text(json.dumps(dict(hypotheses=H, per_testbed=per, meta=meta), indent=1, default=float) + "\n")
    L = ["# E13-R001 stopping rules", "", f"{len(tasks)} campaigns in {time.time() - t0:.0f} s.", "",
         "| ID | estimate | verdict |", "|---|---|---|"] + [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if m is not None:
        manifest.finish(m, outputs=[(out / x).relative_to(ROOT) for x in ("campaigns.csv.gz", "summary.json", "summary.md")],
                        wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
