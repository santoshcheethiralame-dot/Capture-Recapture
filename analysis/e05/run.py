"""E05 confirmatory runner: error-injection grid with corrections (a)-(f).

    python analysis/e05/run.py R001 [--workers 4]                       # E01 base + ln2 worlds
    python analysis/e05/run.py R002 --histories <e02>/histories/oracle_tgt0.7 [--workers 4]
    python analysis/e05/run.py R001 --n-inj 2 --out <scratchpad>         # smoke test: no manifest, pilot seeds

Confirmatory: refuses a dirty tree and records the prereg version. Run only
after the v1 freeze. Grid (E05 §2):
- f in {0, .02, .05, .10, .20, .30} x g in {0, .01, .02, .05, .10}
  x pattern {uniform, score} x 200 injections per cell;
- R001 cells: the E01 base and ln2 (sigma = 2) worlds. Injection j uses a
  fresh world from E01's generator with this experiment's seed stream. The
  E01 replicate itself is not reused, so E05 never touches E01's seeds.
- R002 cells: the 35 E02 oracle cells (tau_gt = 0.7); p_i for the score
  pattern is the item's firing probability.

Seeds: SeedSequence(20261027, spawn_key=(source, cell, f, g, pattern, j)),
with level indices and source 0 = E01, 1 = E02. The pilot used keys from
9000 up, so the streams are disjoint.

Per injection the rows record:
- the truth (N, C for E01) and the oracle estimates (Chao2, Ĉ);
- naive (a);
- (b) at n_v in {50, 100, 200, 500};
- (d) breakaway_nof1;
- (e1) the free mixture and (e2) the labelled MI with n_v = 200;
- (f) Di Consiglio-Tuoto with n_v = 200;
- intervals: the Chao2 log-normal CI (naive, oracle), the MI Rubin interval,
  and the realized-coverage interval for naive and oracle Ĉ (B = 500).
R003 is the analysis of both (`analysis/e05/analyse.py`), per E05 §2a.
"""

import argparse
import csv
import gzip
import sys
import time
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm

import crsafety as cr
from crsafety import linkage as lk
from crsafety import manifest, rbridge, testbed
from crsafety.estimators import IncidenceData
from crsafety.sim import Cell, simulate

ROOT = Path(__file__).resolve().parents[2]
MASTER = 20261027
F = (0.0, 0.02, 0.05, 0.10, 0.20, 0.30)
G = (0.0, 0.01, 0.02, 0.05, 0.10)
PATTERNS = ("uniform", "score")
N_V = (50, 100, 200, 500)
M_IMP = 20
B_CI = 500
E01_CELLS = {"base": Cell(), "ln2": Cell(sigma=2.0)}
Z = norm.ppf(0.975)


def _world(task, cells):
    src, ci, cname, fi, gi, pi_, j = task
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(src, ci, fi, gi, pi_, j)))
    if src == 0:
        sim = simulate(E01_CELLS[cname], rng)
        return rng, sim["X"], sim["pi"], dict(N=sim["N"], C=sim["C"])
    X, p = cells[cname]
    return rng, X, p, dict(U=int(X.any(axis=1).sum()))


def one(task, cells=None):
    src, ci, cname, fi, gi, pi_, j = task
    f, g, pat = F[fi], G[gi], PATTERNS[pi_]
    rng, X, p, truth = _world(task, cells)
    det = X[X.any(axis=1)]
    oracle = IncidenceData.from_matrix(det)
    row = dict(cell=cname, f=f, g=g, pattern=pat, inj=j, spawn_key=f"{src} {ci} {fi} {gi} {pi_} {j}", **truth)
    oc2 = cr.chao2_ci(oracle)
    oci = cr.coverage_interval(det, B=B_CI, seed=rng.integers(2**63))
    row.update(oracle_chao2=oc2[0], oracle_chao2_lo=oc2[2], oracle_chao2_hi=oc2[3],
               oracle_coverage=oci["estimate"], oracle_cov_lo=oci["interval"][0], oracle_cov_hi=oci["interval"][1],
               oracle_overlap=testbed.overlap_ratio(det) if det.shape[1] > 1 else np.nan)
    L = lk.inject(X, f, g, rng, pattern=pat, p=p)
    d = IncidenceData.from_matrix(L.X)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nc2 = cr.chao2_ci(d)
        nci = cr.coverage_interval(L.X, B=B_CI, seed=rng.integers(2**63))
        row.update(naive_chao2=nc2[0], naive_chao2_lo=nc2[2], naive_chao2_hi=nc2[3],
                   naive_coverage=nci["estimate"], naive_cov_lo=nci["interval"][0], naive_cov_hi=nci["interval"][1],
                   naive_lp=lk.lp_corrected(L.X, 0.0), true_ghosts=int(L.is_ghost.sum()), n_merges=L.n_merges)
        labels = {}
        for nv in N_V:
            labels[nv] = lk.label_bins(L, nv, rng)
            fh, gh = lk.rates_from_bins(*labels[nv], n_rows=L.X.shape[0])
            c = lk.corrected_estimates(d, fh)
            row.update({f"b{nv}_f_hat": fh, f"b{nv}_g_hat": gh, f"b{nv}_chao2": c["chao2"],
                        f"b{nv}_coverage": c["coverage"], f"b{nv}_lp": lk.lp_corrected(L.X, fh)})
            if nv == 200:
                row["f200_dct"] = lk.dct_petersen(L.X, 1 - fh, gh)
        for name, lab in (("e1", None), ("e2", labels[200])):
            mi = lk.mi_estimates(L, M_IMP, rng, labelled=lab)
            se = np.sqrt(mi["chao2_var"])
            row.update({f"{name}_chao2": mi["chao2"], f"{name}_chao2_lo": mi["chao2"] - Z * se,
                        f"{name}_chao2_hi": mi["chao2"] + Z * se, f"{name}_coverage": mi["coverage"]})
    k_, q_ = rbridge.frequency_table(d)
    row["freq_index"], row["freq_count"] = " ".join(map(str, k_)), " ".join(map(str, q_))
    return row, d


def _one_e02(args):
    return one(args[0], args[1])


def load_e02(hdir):
    from crsafety.histories import read_cell
    cells = {}
    for c in sorted(Path(hdir).glob("*")):
        if not (c / "runs.csv").exists():
            continue
        cell = read_cell(c, role=None)
        ids = sorted(k for k, v in cell.items.items() if v["planted"]) if cell.items else list(cell.item_ids)
        pos = {i: r for r, i in enumerate(cell.item_ids)}
        X = np.zeros((len(ids), cell.X.shape[1]), np.int8)
        for r, i in enumerate(ids):
            if i in pos:
                X[r] = cell.X[pos[i]]
        p = np.array([cell.items[i]["covariates"].get("p", np.nan) for i in ids], float)
        cells[c.name] = (X, p)
    return cells


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run", choices=["R001", "R002"])
    ap.add_argument("--histories")
    ap.add_argument("--n-inj", type=int, default=200)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out")
    a = ap.parse_args()
    run_id = f"E05-{a.run}"
    out = Path(a.out) if a.out else ROOT / "results" / "E05" / run_id
    out.mkdir(parents=True, exist_ok=True)
    src = 0 if a.run == "R001" else 1
    cells = E01_CELLS if src == 0 else load_e02(a.histories)
    m = None
    if a.out is None:
        m = manifest.start(run_id, "E05", " ".join(sys.argv),
                           dict(source="E01" if src == 0 else a.histories, F=F, G=G, patterns=PATTERNS, n_v=N_V,
                                imputations=M_IMP, B_ci=B_CI, n_inj=a.n_inj, cells=sorted(cells)),
                           seeds=dict(master=MASTER, rule="spawn_key=(source, cell, f, g, pattern, injection)"),
                           confirmatory=True, prereg=dict(version="v1.0"))
    j0 = 0 if a.out is None else 9000  # smoke tests (--out) never touch the confirmatory streams
    tasks = [(src, ci, cname, fi, gi, pi_, j0 + j) for ci, cname in enumerate(sorted(cells))
             for fi in range(len(F)) for gi in range(len(G)) for pi_ in range(len(PATTERNS)) for j in range(a.n_inj)]
    t0 = time.time()
    with Pool(a.workers) as pool:
        if src == 0:
            res = pool.map(one, tasks, chunksize=16)
        else:
            res = pool.map(_one_e02, [(t, {t[2]: cells[t[2]]}) for t in tasks], chunksize=16)
    rows = [r for r, _ in res]
    try:
        nof1 = rbridge.breakaway_nof1(*[d for _, d in res])  # (d), one R session
        for r, b in zip(rows, nof1):
            r["nof1"], r["nof1_model"] = b.get("estimate"), b.get("model")
    except Exception as e:  # recorded, never silent: (d) counts as failed for every row
        for r in rows:
            r["nof1"], r["nof1_model"] = np.nan, f"error: {type(e).__name__}"
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with gzip.open(out / "injections.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, fields, restval="")
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} injections in {time.time() - t0:.0f} s -> {out}")
    if m is not None:
        manifest.finish(m, outputs=[(out / "injections.csv.gz").relative_to(ROOT)],
                        wall_seconds=round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
