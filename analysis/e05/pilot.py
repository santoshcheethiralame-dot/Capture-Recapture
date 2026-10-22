"""E05 pilot (declared; separate seeds): feasibility and cost of the corrections.

    python analysis/e05/pilot.py [--n-inj 20] [--workers 4]

Seeds: SeedSequence(20261027, spawn_key=(9000 + cell, combo, injection)),
disjoint from E05's confirmatory streams (spawn keys below 9000) and from
E01's master seed. Worlds are the E01 base and ln2 cells. Writes
results/E05/E05-R004/ (manifest.json, pilot.csv.gz, summary.md). The summary
reports cost and failure counts per correction, and the pilot's bias table,
labelled as pilot output.
"""

import argparse
import csv
import gzip
import itertools
import sys
import time
import warnings
from multiprocessing import Pool
from pathlib import Path

import numpy as np

import crsafety as cr
from crsafety import linkage as lk
from crsafety import manifest, rbridge
from crsafety.estimators import IncidenceData
from crsafety.sim import Cell, simulate

ROOT = Path(__file__).resolve().parents[2]
MASTER = 20261027
CELLS = {"base": Cell(), "ln2": Cell(sigma=2.0)}
COMBOS = [(f, g, pat) for f, g in ((0.10, 0.0), (0.10, 0.05), (0.0, 0.05), (0.30, 0.0))
          for pat in ("uniform", "score")]
N_V = (50, 200)
M_IMP = 20


def one(task):
    ci, cname, k, (f, g, pat), j = task
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(9000 + ci, k, j)))
    sim = simulate(CELLS[cname], rng)
    X, pi = sim["X"], sim["pi"]
    oracle = IncidenceData.from_matrix(X[X.any(axis=1)])
    row = dict(cell=cname, f=f, g=g, pattern=pat, inj=j, N=sim["N"], C=sim["C"],
               oracle_chao2=cr.chao2(oracle), oracle_coverage=cr.coverage(oracle))
    t = {}
    t0 = time.perf_counter()
    L = lk.inject(X, f, g, rng, pattern=pat, p=pi)
    t["inject"] = time.perf_counter() - t0
    d = IncidenceData.from_matrix(L.X)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        row.update(naive_chao2=cr.chao2(d), naive_coverage=cr.coverage(d),
                   naive_lp=lk.lp_corrected(L.X, 0.0), true_ghosts=int(L.is_ghost.sum()),
                   n_merges=L.n_merges)
        labels = {}
        for nv in N_V:
            t0 = time.perf_counter()
            labels[nv] = lk.label_bins(L, nv, rng)
            f_hat, g_hat = lk.rates_from_bins(*labels[nv], n_rows=L.X.shape[0])
            c = lk.corrected_estimates(d, f_hat)
            row.update({f"b{nv}_f_hat": f_hat, f"b{nv}_g_hat": g_hat, f"b{nv}_chao2": c["chao2"],
                        f"b{nv}_coverage": c["coverage"], f"b{nv}_lp": lk.lp_corrected(L.X, f_hat),
                        f"f{nv}_dct": lk.dct_petersen(L.X, 1 - f_hat, g_hat)})
            t[f"b{nv}"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        mi = lk.mi_estimates(L, M_IMP, rng)
        t["mi"] = time.perf_counter() - t0
        t0 = time.perf_counter()
        mil = lk.mi_estimates(L, M_IMP, rng, labelled=labels[200])
        t["mi_labelled"] = time.perf_counter() - t0
        row.update(mil200_chao2=mil["chao2"], mil200_coverage=mil["coverage"])
    row.update(mi_chao2=mi["chao2"], mi_coverage=mi["coverage"], mi_chao2_var=mi["chao2_var"],
               mi_mean_posterior=mi["mean_posterior"], **{f"sec_{k}": v for k, v in t.items()})
    k_, q_ = rbridge.frequency_table(d)
    row["freq_index"], row["freq_count"] = " ".join(map(str, k_)), " ".join(map(str, q_))
    return row, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-inj", type=int, default=20)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=None)
    ap.add_argument("--run", default="E05-R004")
    a = ap.parse_args()
    out = Path(a.out) if a.out else ROOT / "results" / "E05" / a.run
    out.mkdir(parents=True, exist_ok=True)
    m = None
    if a.out is None:
        m = manifest.start(a.run, "E05", " ".join(sys.argv),
                           dict(cells={k: v.to_dict() for k, v in CELLS.items()}, combos=COMBOS,
                                n_v=N_V, imputations=M_IMP, n_inj=a.n_inj, pilot=True),
                           seeds=dict(master=MASTER, rule="spawn_key=(9000 + cell, combo, injection)"),
                           prereg=dict(frozen=False, note="declared pilot on separate seeds"))
    tasks = [(ci, cname, k, combo, j) for ci, cname in enumerate(CELLS)
             for k, combo in enumerate(COMBOS) for j in range(a.n_inj)]
    t0 = time.time()
    with Pool(a.workers) as pool:
        res = pool.map(one, tasks, chunksize=4)
    rows = [r for r, _ in res]
    t1 = time.time()
    nof1 = rbridge.breakaway_nof1(*[d for _, d in res])  # (d) f1-free, one R call
    sec_nof1 = (time.time() - t1) / max(len(res), 1)
    for r, b in zip(rows, nof1):
        r["nof1"] = b.get("estimate")
        r["nof1_model"] = b.get("model")
        r["sec_nof1"] = sec_nof1
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with gzip.open(out / "pilot.csv.gz", "wt", newline="") as fh:
        w = csv.DictWriter(fh, fields, restval="")
        w.writeheader()
        w.writerows(rows)
    write_summary(rows, out, time.time() - t0)
    if m is not None:
        manifest.finish(m, outputs=[(out / "pilot.csv.gz").relative_to(ROOT), (out / "summary.md").relative_to(ROOT)],
                        wall_seconds=round(time.time() - t0, 1))


def write_summary(rows, out, wall):
    def col(rs, k):
        return np.array([float(r[k]) if r.get(k) not in (None, "") else np.nan for r in rs])

    L = [f"# {out.name} pilot (declared; separate seeds)", "",
         f"{len(rows)} injections ({len(rows) // (len(CELLS) * len(COMBOS))} per cell x combination); "
         f"wall time {wall:.0f} s on 4 workers. Pilot output: informs feasibility and cost only.", "",
         "## Cost per injection (seconds, mean)", "",
         "| Step | mean s | max s |", "|---|---|---|"]
    for k in [k for k in rows[0] if k.startswith("sec_")]:
        v = col(rows, k)
        L.append(f"| {k[4:]} | {np.nanmean(v):.4f} | {np.nanmax(v):.4f} |")
    L += ["", "## Failures (non-finite estimates)", "", "| Estimate | failures |", "|---|---|"]
    for k in ("naive_chao2", "b50_chao2", "b200_chao2", "mi_chao2", "nof1", "naive_lp", "b200_lp", "f200_dct"):
        v = col(rows, k)
        L.append(f"| {k} | {int((~np.isfinite(v)).sum())} / {v.size} |")
    L += ["", "## Pilot bias of Chao2 relative to the oracle Chao2 (mean of est/oracle − 1)", "",
          "| cell | f | g | pattern | naive | b (n_v=50) | b (n_v=200) | MI (mixture) | MI (labelled, n_v=200) | nof1 (median) | f̂ (n_v=200) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for cname in CELLS:
        for f, g, pat in COMBOS:
            rs = [r for r in rows if r["cell"] == cname and r["f"] == f and r["g"] == g and r["pattern"] == pat]
            o = col(rs, "oracle_chao2")

            def rb(k):
                v = col(rs, k) / o - 1
                return f"{np.nanmean(v):+.0%}"
            med = np.nanmedian(col(rs, "nof1") / o - 1) if "nof1" in rs[0] else np.nan
            L.append(f"| {cname} | {f} | {g} | {pat} | {rb('naive_chao2')} | {rb('b50_chao2')} | "
                     f"{rb('b200_chao2')} | {rb('mi_chao2')} | {rb('mil200_chao2')} | {med:+.0%} | "
                     f"{np.nanmean(col(rs, 'b200_f_hat')):.3f} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
