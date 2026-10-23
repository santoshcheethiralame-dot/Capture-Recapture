"""E01 runner: simulate the cells of one run and apply the estimator suite.

    python analysis/e01/run.py R001 [--workers 4] [--n-sim 500]

Cells, seeds and the R005 bootstrap subset are in configs/e01/cells.json.
Writes results/E01/E01-<run>/: manifest.json and replicates.csv.gz (one row
per cell x replicate: truths, frequency counts and every estimate). Failed
estimates (NaN, inf) are written as such and counted by analyse.py, never
dropped. R005 re-draws the same datasets as the cells' original runs (same
seeds) and adds bootstrap intervals for coverage and new items.
"""

import argparse
import csv
import gzip
import json
import sys
import time
import warnings
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import crsafety as cr
from crsafety import manifest
from crsafety.estimators import IncidenceData
from crsafety.sim import Cell, simulate

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs" / "e01" / "cells.json"


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def estimates(Xo, K, skip=()):
    """The E00 suite on one observed matrix (detected rows only)."""
    d = IncidenceData.from_matrix(Xo) if Xo.shape[0] else None
    out = dict(S_obs=0 if d is None else d.S, U_obs=0 if d is None else d.U)
    for k in range(1, 5):
        out[f"Q{k}"] = 0 if d is None else d.Q(k)
    if d is None:
        return out
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        est, se, lo, hi = cr.chao2_ci(d)
        out.update(
            coverage=_f(cr.coverage(d)), gt_coverage=_f(cr.good_turing_coverage(d)),
            delta_K=_f(cr.extrapolate(d, K)),
            chao2=_f(est), chao2_se=_f(se), chao2_lo=_f(lo), chao2_hi=_f(hi),
            chao2_bc=_f(cr.chao2(d, "bc")), ichao2=_f(cr.ichao2(d)),
            jack1=_f(cr.jackknife(d, 1)), jack2=_f(cr.jackknife(d, 2)), ice=_f(cr.ice(d)),
            mt=_f(cr.darroch_mt(d)),
        )
        if K >= 2:
            pairs = cr.chapman_pairs(d)
            out["chapman_all"] = _f(np.mean(pairs))
            a = K // 2
            cross = [cr.chapman(d, i, j) for i, j in combinations(range(K), 2) if i < a <= j]
            out["chapman_cross"] = _f(np.mean(cross))
        if 3 <= K <= 12 and (d.y > 1).any() and "mh_chao_ll" not in skip:
            try:
                out["mh_chao_ll"] = _f(cr.loglinear(d, "Mh", "Chao")["N"])
            except Exception:  # failures are data: recorded as NaN
                out["mh_chao_ll"] = np.nan
    return out


def bootstrap_cols(Xo, K, seed, B, level):
    if Xo.shape[0] < 2:
        return {}
    d = IncidenceData.from_matrix(Xo)
    s_cov, s_delta = seed.spawn(2)
    out = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for name, stat, s in (("coverage", cr.coverage, s_cov),
                              ("delta_K", lambda e: cr.extrapolate(e, K), s_delta)):
            b = cr.bootstrap(d, stat, B=B, level=level, seed=s)
            out.update({f"{name}_boot_se": b["se"],
                        f"{name}_ci_n_lo": b["normal_ci"][0], f"{name}_ci_n_hi": b["normal_ci"][1],
                        f"{name}_ci_p_lo": b["percentile_ci"][0], f"{name}_ci_p_hi": b["percentile_ci"][1],
                        f"{name}_boot_dropped": b["dropped"]})
    return out


def realized_cols(Xo, K, seed, B, level):
    if Xo.shape[0] < 2:
        return {}
    from scipy.stats import norm
    d = IncidenceData.from_matrix(Xo)
    s_cov, s_delta = seed.spawn(2)
    z2, z1 = norm.ppf(0.5 + level / 2), norm.ppf(level)
    out = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        c = cr.coverage_interval(d, B=B, level=level, seed=s_cov)
        dl = cr.delta_interval(d, B=B, level=level, seed=s_delta)
    for name, r in (("cov_rz", c), ("delta_rz", dl)):
        est, se, me = r["estimate"], r["se"], r["mean_error"]
        out.update({f"{name}_se": se, f"{name}_mean_error": me,
                    f"{name}_lo": est - z2 * se, f"{name}_hi": est + z2 * se,
                    f"{name}_bc_lo": est - me - z2 * se, f"{name}_bc_hi": est - me + z2 * se,
                    f"{name}_lo1": est - z1 * se, f"{name}_bc_lo1": est - me - z1 * se,
                    f"{name}_dropped": r["dropped"]})
    return out


def work(task):
    cell_id, idx, params, master, reps, boot, skip, realized = task
    offset = realized.get("rep_offset", 0) if realized else 0
    cell = Cell(**params)
    rows = []
    for r in (r + offset for r in reps):
        rng = np.random.default_rng(np.random.SeedSequence(master, spawn_key=(idx, r)))
        sim = simulate(cell, rng)
        X = sim["X"]
        y = X.sum(axis=1)
        row = dict(cell=cell_id, cell_idx=idx, rep=r, cell_seed=f"{master}:{idx}",
                   C=sim["C"], Delta=sim["Delta"], N=sim["N"], N_all=sim["N_all"],
                   S_true=int((y > 0).sum()), **{f"Qt{k}": int((y == k).sum()) for k in range(1, 5)})
        row.update(estimates(sim["X_obs"], cell.K, skip))
        if boot:
            seed = np.random.SeedSequence(master, spawn_key=(idx, r, 1))
            row.update(bootstrap_cols(sim["X_obs"], cell.K, seed, boot["B"], boot["level"]))
        if realized:
            seed = np.random.SeedSequence(master, spawn_key=(idx, r, 2))
            row.update(realized_cols(sim["X_obs"], cell.K, seed, realized["B"], realized["level"]))
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", help="R001 ... R005")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--n-sim", type=int, default=None, help="override n_sim (smoke tests only)")
    ap.add_argument("--out", default=None, help="output directory (default results/E01/E01-<run>)")
    args = ap.parse_args()
    cfg = json.loads(CONFIG.read_text())
    n_sim = args.n_sim or cfg["n_sim"]
    run_id = f"E01-{args.run}"
    boot = realized = None
    if args.run in ("R007", "R008", "R010"):
        rc = cfg[args.run]
        cells = [c for c in cfg["cells"] if c["id"] in rc["cells"]]
        realized = dict(B=rc["B"], level=rc["level"], rep_offset=rc.get("rep_offset", 0))
    elif args.run == "R005":
        cells = [c for c in cfg["cells"] if c["id"] in cfg["R005"]["cells"]]
        boot = dict(B=cfg["R005"]["B"], level=cfg["R005"]["level"])
    else:
        cells = [c for c in cfg["cells"] if c["run"] == args.run]
    if not cells:
        sys.exit(f"no cells for {args.run}")
    out_dir = Path(args.out) if args.out else ROOT / "results" / "E01" / run_id
    smoke = args.n_sim is not None or args.out is not None
    m = None
    if not smoke:
        page = (ROOT / "notebook" / "experiments" / "E01-simulation-study.md").read_text()
        block = page.split("<!-- prereg:start -->")[1].split("<!-- prereg:end -->")[0]
        block = "\n".join(l.rstrip() for l in block.strip().splitlines())
        m = manifest.start(
            run_id, "E01", " ".join(sys.argv), dict(cells=cells, n_sim=n_sim, bootstrap=boot, realized=realized,
                                                    config_file=str(CONFIG.relative_to(ROOT))),
            seeds=dict(master=cfg["master_seed"], rule=cfg["seed_rule"],
                       cells={c["id"]: c["idx"] for c in cells}),
            prereg=dict(frozen=False, block_sha256=manifest.sha256_bytes(block.encode()),
                        note="Stage 1 exploratory; run before the v1 freeze"),
            inputs=[CONFIG])
    out_dir.mkdir(parents=True, exist_ok=True)
    chunk = 50
    tasks = [(c["id"], c["idx"], c["params"], cfg["master_seed"], range(s, min(s + chunk, n_sim)), boot,
              tuple(c.get("skip", ())), realized)
             for c in cells for s in range(0, n_sim, chunk)]
    t0 = time.time()
    rows = []
    with Pool(args.workers) as pool:
        for i, part in enumerate(pool.imap(work, tasks)):
            rows.extend(part)
            if (i + 1) % max(1, len(tasks) // 10) == 0:
                print(f"{i + 1}/{len(tasks)} tasks, {time.time() - t0:.0f}s", flush=True)
    rows.sort(key=lambda r: (r["cell_idx"], r["rep"]))
    fields = []
    for r in rows:
        fields += [k for k in r if k not in fields]
    path = out_dir / "replicates.csv.gz"
    with gzip.open(path, "wt", newline="") as f:
        w = csv.DictWriter(f, fields, restval="")
        w.writeheader()
        w.writerows(rows)
    elapsed = time.time() - t0
    print(f"{len(rows)} replicates in {elapsed:.0f}s -> {path}")
    if m is not None:
        manifest.finish(m, outputs=[path.relative_to(ROOT)], cpu_seconds_wall=round(elapsed, 1),
                        replicates_sha256=manifest.sha256_file(path))


if __name__ == "__main__":
    main()
