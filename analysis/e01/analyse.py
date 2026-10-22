"""E01 analysis: performance measures, hypotheses H1a-H1f, decision guide.

    python analysis/e01/analyse.py

Reads results/E01/E01-R00[1-5]/replicates.csv.gz and writes
results/E01/analysis/: performance.csv (cell x estimator x target),
hypotheses.csv, and summary.md. Analysis sets and verdict rules are the ones
fixed in E01 §2a before the first run.
"""

import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results" / "E01"
CFG = json.loads((ROOT / "configs" / "e01" / "cells.json").read_text())
BASE = dict(N=500, K=10, het="logitnormal", sigma=1.0, alpha=1.0, families=0, tau=1.5,
            dep_or=0.0, c=1.0, nested_k=0.0, ghost=0.0, merge=0.0, mean_p=0.2)
PREREG_RUNS = ("R001", "R002", "R003", "R004")  # R006 is an exploratory addition (§5)
RICHNESS = ["chao2", "chao2_bc", "ichao2", "jack1", "jack2", "ice", "mt", "chapman_all",
            "chapman_cross", "mh_chao_ll"]
LABEL = dict(chao2="Chao2", chao2_bc="Chao2-bc", ichao2="iChao2", jack1="Jack1", jack2="Jack2",
             ice="ICE", mt="Mt", chapman_all="Chapman (all pairs)", chapman_cross="Chapman (cross-block)",
             mh_chao_ll="Mh Chao (LB) log-linear")


def load(run):
    p = RES / f"E01-{run}" / "replicates.csv.gz"
    if not p.exists():
        return []
    with gzip.open(p, "rt") as f:
        return list(csv.DictReader(f))


def num(rows, key):
    return np.array([float(r[key]) if r.get(key) not in (None, "") else np.nan for r in rows])


def applicable(est, K):
    """Estimators undefined by design are 'not applicable', not failures:
    iChao2 needs K >= 4 (PROTOCOLS §1) and the log-linear fit is run for K <= 12."""
    if est == "ichao2":
        return K >= 4
    if est == "mh_chao_ll":
        return 3 <= K <= 12
    return True


def params(cell):
    return {**BASE, **cell["params"]}


def mean_mcse(x):
    x = x[np.isfinite(x)]
    if x.size == 0:
        return np.nan, np.nan, 0
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(x.size)) if x.size > 1 else np.nan, x.size


def cell_performance(cell, rows):
    p = params(cell)
    K = p["K"]
    n = len(rows)
    out = dict(cell=cell["id"], block=cell["block"], run=cell["run"], n_sim=n, K=K,
               N=float(np.mean(num(rows, "N"))), N_all=float(np.mean(num(rows, "N_all"))),
               C=float(np.mean(num(rows, "C"))), Delta=float(np.mean(num(rows, "Delta"))),
               S_obs=float(np.mean(num(rows, "S_obs"))), S_true=float(np.mean(num(rows, "S_true"))))
    q1, q2 = np.mean(num(rows, "Qt1")), np.mean(num(rows, "Qt2"))
    out["N_LB"] = float(out["S_true"] + (K - 1) / K * q1**2 / (2 * q2)) if q2 > 0 else np.nan
    perf = []

    def add(est, target, err, kind):
        fin = np.isfinite(err)
        m, se, k = mean_mcse(err)
        rmse = float(np.sqrt(np.mean(err[fin] ** 2))) if fin.any() else np.nan
        perf.append(dict(cell=cell["id"], block=cell["block"], estimator=est, target=target, kind=kind,
                         bias=m, mcse=se, rmse=rmse, n_finite=k, failure_rate=float(1 - fin.mean())))

    C = num(rows, "C")
    for est in ("coverage", "gt_coverage"):
        add(est, "C", num(rows, est) - C, "absolute")
    D, Dh = num(rows, "Delta"), num(rows, "delta_K")
    add("delta_K", "Delta(K)", Dh - D, "absolute")
    if out["Delta"] > 0:
        add("delta_K", "Delta(K)", (Dh - D) / out["Delta"], "relative")
    targets = dict(N=num(rows, "N"))
    if np.isfinite(out["N_LB"]):
        targets["N_LB"] = np.full(n, out["N_LB"])
    if p["het"] == "mixture":
        targets["N_all"] = num(rows, "N_all")
    for est in RICHNESS:
        if est not in rows[0] or not applicable(est, K):
            continue
        e = num(rows, est)
        for t, tv in targets.items():
            add(est, t, e / tv - 1, "relative")
    lo, hi = num(rows, "chao2_lo"), num(rows, "chao2_hi")
    for t, tv in targets.items():
        ok = np.isfinite(lo) & np.isfinite(hi)
        cov = ((lo <= tv) & (tv <= hi))[ok]
        pr = float(cov.mean()) if cov.size else np.nan
        out[f"chao2_ci_cover_{t}"] = pr
        out[f"chao2_ci_cover_{t}_mcse"] = float(np.sqrt(pr * (1 - pr) / cov.size)) if cov.size else np.nan
    out["chao2_ci_width_median"] = float(np.nanmedian(hi - lo))
    if "coverage_ci_n_lo" in rows[0]:
        for est, tgt in (("coverage", C), ("delta_K", D)):
            for kind in ("n", "p"):
                l, h = num(rows, f"{est}_ci_{kind}_lo"), num(rows, f"{est}_ci_{kind}_hi")
                ok = np.isfinite(l) & np.isfinite(h)
                cov = ((l <= tgt) & (tgt <= h))[ok]
                pr = float(cov.mean()) if cov.size else np.nan
                out[f"{est}_ci_{kind}_cover"] = pr
                out[f"{est}_ci_{kind}_cover_mcse"] = float(np.sqrt(pr * (1 - pr) / cov.size)) if cov.size else np.nan
                out[f"{est}_ci_{kind}_width_median"] = float(np.nanmedian(h - l))
                out[f"{est}_ci_{kind}_n"] = int(ok.sum())
    return out, perf


def analysis_sets(cells):
    """The H1a / H1b cell sets, as fixed in E01 §2a."""
    lit, clean = [], []
    for c in cells:
        p = params(c)
        if c["run"] not in PREREG_RUNS:
            continue
        if p["ghost"] == 0 and p["merge"] == 0 and p["c"] == 1.0 and p["K"] >= 5:
            lit.append(c["id"])
            if p["families"] == 0 and p["dep_or"] in (0.0, 1.0) and p["nested_k"] == 0:
                clean.append(c["id"])
    h1b = [c["id"] for c in cells if c["id"] in clean and params(c)["het"] in ("logitnormal", "mixture")
           and params(c)["sigma"] >= 1]
    return lit, clean, h1b


def verdict(sup, notsup):
    return "supported" if sup else ("not supported" if notsup else "inconclusive")


def main():
    out_dir = RES / "analysis"
    out_dir.mkdir(parents=True, exist_ok=True)
    by_cell = defaultdict(list)
    boot = defaultdict(list)
    for run in PREREG_RUNS + ("R006",):
        for r in load(run):
            by_cell[r["cell"]].append(r)
    for r in load("R005"):
        boot[r["cell"]].append(r)
    rz = defaultdict(list)
    for r in load("R007"):
        rz[r["cell"]].append(r)
    rz8 = defaultdict(list)
    for r in load("R008"):
        rz8[r["cell"]].append(r)
    cells = [c for c in CFG["cells"] if c["id"] in by_cell]
    summ, perf = {}, []
    for c in cells:
        s, p = cell_performance(c, by_cell[c["id"]])
        summ[c["id"]] = s
        perf += p
    bsumm = {}
    for cid, rows in boot.items():
        c = next(x for x in CFG["cells"] if x["id"] == cid)
        bsumm[cid], _ = cell_performance(c, rows)

    P = {(r["cell"], r["estimator"], r["target"], r["kind"]): r for r in perf}

    def g(cell, est, target, kind="relative", key="bias"):
        r = P.get((cell, est, target, kind))
        return np.nan if r is None else r[key]

    with open(out_dir / "performance.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(perf[0]))
        w.writeheader()
        w.writerows(perf)
    with open(out_dir / "cells.csv", "w", newline="") as f:
        keys = []
        for s in summ.values():
            keys += [k for k in s if k not in keys]
        w = csv.DictWriter(f, keys, restval="")
        w.writeheader()
        w.writerows(summ.values())
    if bsumm:
        with open(out_dir / "bootstrap_cells.csv", "w", newline="") as f:
            keys = []
            for s in bsumm.values():
                keys += [k for k in s if k not in keys]
            w = csv.DictWriter(f, keys, restval="")
            w.writeheader()
            w.writerows(bsumm.values())

    # ------------------------------------------------------------ hypotheses
    lit, clean, h1b = analysis_sets(cells)
    H = []
    dep_or = {}
    for c in cells:
        p = params(c)
        if p["dep_or"]:
            from crsafety.sim import Cell, simulate
            t = np.zeros((2, 2))
            for r in range(100):
                rng = np.random.default_rng(np.random.SeedSequence(CFG["master_seed"], spawn_key=(c["idx"], r)))
                X = simulate(Cell(**c["params"]), rng)["X"]
                a = X[:, : p["K"] // 2].any(axis=1)
                for j in range(p["K"] // 2, p["K"]):
                    t += np.array([[np.sum(a & (X[:, j] == 1)), np.sum(a & (X[:, j] == 0))],
                                   [np.sum(~a & (X[:, j] == 1)), np.sum(~a & (X[:, j] == 0))]])
            dep_or[c["id"]] = (p["dep_or"], t[0, 0] * t[1, 1] / (t[0, 1] * t[1, 0]))

    def cov_bias(cid):
        return g(cid, "coverage", "C", "absolute"), g(cid, "coverage", "C", "absolute", "mcse")

    for name, S in (("H1a (literal set)", lit), ("H1a (clean set; gate G1)", clean)):
        b = {c: cov_bias(c) for c in S}
        worst = max(S, key=lambda c: abs(b[c][0]))
        sup = all(abs(v[0]) <= 0.03 for v in b.values())
        ns = any(abs(v[0]) > 0.05 for v in b.values())
        H.append(dict(id=name, measure="max |bias of C_hat| over the set",
                      estimate=f"{b[worst][0]:+.4f} (MCSE {b[worst][1]:.4f}) in {worst}",
                      cells=len(S), detail="; ".join(f"{c} {v[0]:+.3f}" for c, v in b.items()),
                      verdict=verdict(sup, ns)))
    cv = {c: (summ[c]["chao2_ci_cover_N"], summ[c]["chao2_ci_cover_N_mcse"]) for c in h1b}
    worst = max(h1b, key=lambda c: cv[c][0])
    H.append(dict(id="H1b", measure="max Chao2 CI coverage of N over sigma >= 1 cells",
                  estimate=f"{cv[worst][0]:.3f} (MCSE {cv[worst][1]:.3f}) in {worst}", cells=len(h1b),
                  detail="; ".join(f"{c} {v[0]:.3f}" for c, v in cv.items()),
                  verdict=verdict(all(v[0] < 0.5 for v in cv.values()), any(v[0] >= 0.8 for v in cv.values()))))
    if "dep1/3" in summ:
        b, se = g("dep1/3", "chapman_cross", "N"), g("dep1/3", "chapman_cross", "N", key="mcse")
        H.append(dict(id="H1c", measure="relative bias of Chapman (cross-block pairs), odds ratio 1/3",
                      estimate=f"{b:+.3f} (MCSE {se:.3f})", cells=1,
                      detail=f"dep1 {g('dep1', 'chapman_cross', 'N'):+.3f}; dep3 {g('dep3', 'chapman_cross', 'N'):+.3f}",
                      verdict=verdict(b > 0.20, b < 0.05)))
    if "beh2" in summ:
        b, se = cov_bias("beh2")
        H.append(dict(id="H1d", measure="bias of C_hat at c = 2", estimate=f"{b:+.4f} (MCSE {se:.4f})",
                      cells=1, detail=f"beh0.5 {cov_bias('beh0.5')[0]:+.4f}; base {cov_bias('base')[0]:+.4f}",
                      verdict=verdict(b >= 0.05, b < 0.02)))
    if "ghost0.15" in summ:
        bc, sc = cov_bias("ghost0.15")
        bn, sn = g("ghost0.15", "chao2", "N"), g("ghost0.15", "chao2", "N", key="mcse")
        H.append(dict(id="H1e", measure="sign of C_hat bias and of Chao2 bias (vs N) at f = 0.15",
                      estimate=f"C_hat {bc:+.4f} (MCSE {sc:.4f}); Chao2 {bn:+.3f} (MCSE {sn:.3f})", cells=1,
                      detail="", verdict=verdict(bc < 0 and bn > 0, not (bc < 0 and bn > 0))))
    if "fam1" in summ and "fam6" in summ:
        b1, s1 = cov_bias("fam1")
        b6, s6 = cov_bias("fam6")
        d = b1 - b6
        H.append(dict(id="H1f", measure="mean(C_hat - C): 1 family minus 6 families",
                      estimate=f"{d:+.4f} (MCSE {np.hypot(s1, s6):.4f})", cells=2,
                      detail=f"fam1 {b1:+.4f}; fam2 {cov_bias('fam2')[0]:+.4f}; fam3 {cov_bias('fam3')[0]:+.4f}; fam6 {b6:+.4f}",
                      verdict=verdict(d >= 0.05, d < 0.02)))
    with open(out_dir / "hypotheses.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(H[0]))
        w.writeheader()
        w.writerows(H)

    # ------------------------------------------------------------ summary.md
    L = ["# E01 analysis", "",
         f"Runs: {', '.join(sorted({c['run'] for c in cells}))}"
         f"{' + R005 (bootstrap)' if bsumm else ''}. Cells: {len(cells)}. "
         f"Replicates per cell: {min(s['n_sim'] for s in summ.values())}.",
         "Bias of coverage and Δ is mean(estimate − truth) per replicate; richness bias is mean(N̂/target − 1). "
         "MCSE in parentheses. Failures (NaN or inf) are counted, not dropped from the failure rate; "
         "bias is over finite values.", "",
         "## Hypotheses", "", "| ID | Measure | Estimate | Cells | Verdict |", "|---|---|---|---|---|"]
    for h in H:
        L.append(f"| {h['id']} | {h['measure']} | {h['estimate']} | {h['cells']} | **{h['verdict']}** |")
    L += ["", "Per-cell values: `hypotheses.csv` (detail column). '—' in the tables below means "
          "not applicable by design (iChao2 needs K ≥ 4; the log-linear fit is run for 3 ≤ K ≤ 12).", ""]

    def fmt(x, pct=False, d=3):
        if x is None or not np.isfinite(x):
            return "n/a"
        return f"{x:+.0%}" if pct else f"{x:+.{d}f}"

    blocks = defaultdict(list)
    for c in cells:
        if c["run"] in PREREG_RUNS:
            blocks[c["block"]].append(c["id"])
    L += ["## Coverage and new-item prediction by cell", "",
          "| Block | Cell | S/N | C (true) | Ĉ bias (MCSE) | Ĉ RMSE | Δ(K) true | Δ̂ rel. bias (MCSE) | Turing 1−Q1/U bias |",
          "|---|---|---|---|---|---|---|---|---|"]
    for blk, ids in blocks.items():
        for cid in ids:
            s = summ[cid]
            L.append(f"| {blk} | {cid} | {s['S_true'] / s['N_all']:.2f} | {s['C']:.3f} | "
                     f"{fmt(g(cid, 'coverage', 'C', 'absolute'), d=4)} ({g(cid, 'coverage', 'C', 'absolute', 'mcse'):.4f}) | "
                     f"{g(cid, 'coverage', 'C', 'absolute', 'rmse'):.4f} | {s['Delta']:.1f} | "
                     f"{fmt(g(cid, 'delta_K', 'Delta(K)'), True)} ({g(cid, 'delta_K', 'Delta(K)', key='mcse'):.3f}) | "
                     f"{fmt(g(cid, 'gt_coverage', 'C', 'absolute'), d=4)} |")
    L += ["", "## Calibration of the PH1 tolerance (exploratory; input to the v1 freeze)", "",
          "Share of replicates with |Ĉ − C| ≤ 0.05, and the 80th percentile of |Ĉ − C|, in the "
          "clean cells (H1a clean set). PH1 asks for |Ĉ − C| ≤ 0.05† in ≥ 80%† of evaluation cells.", "",
          "| Cell | K | N | share ≤ 0.05 | P80 \\|Ĉ − C\\| |", "|---|---|---|---|---|"]
    for cid in clean:
        e = np.abs(num(by_cell[cid], "coverage") - num(by_cell[cid], "C"))
        e = e[np.isfinite(e)]
        L.append(f"| {cid} | {summ[cid]['K']} | {summ[cid]['N']:.0f} | {np.mean(e <= 0.05):.3f} | "
                 f"{np.quantile(e, 0.8):.4f} |")
    if dep_or:
        L += ["", "Dependence cells: the item-level odds ratio between 'found in block A' and a "
              "block-B detection equals θ by construction. The marginal odds ratio (pooled over "
              "items, so it includes heterogeneity) from 100 regenerated replicates:", "",
              "| Cell | θ (design) | marginal OR |", "|---|---|---|"]
        for cid, (theta, orr) in dep_or.items():
            L.append(f"| {cid} | {theta:.3f} | {orr:.3f} |")
    L += ["", "## Richness estimators: relative bias against N (catchable items)", "",
          "| Cell | N_LB/N − 1 | " + " | ".join(LABEL[e] for e in RICHNESS) + " | Chao2 CI covers N | covers N_LB |",
          "|---" * (len(RICHNESS) + 4) + "|"]
    for blk, ids in blocks.items():
        for cid in ids:
            s = summ[cid]
            cells_txt = []
            for e in RICHNESS:
                if not applicable(e, summ[cid]["K"]):
                    cells_txt.append("—")
                    continue
                b, fr = g(cid, e, "N"), g(cid, e, "N", key="failure_rate")
                t = fmt(b, True)
                if np.isfinite(fr) and fr > 0:
                    t += f" (fail {fr:.0%})"
                cells_txt.append(t)
            L.append(f"| {cid} | {fmt(s['N_LB'] / s['N'] - 1, True)} | " + " | ".join(cells_txt) +
                     f" | {s['chao2_ci_cover_N']:.2f} | {s.get('chao2_ci_cover_N_LB', np.nan):.2f} |")
    if any("N_all" in k for k in P if k[0] == "mix20"):
        L += ["", f"mix20 against N_all (all items, 20% uncatchable): Chao2 {fmt(g('mix20', 'chao2', 'N_all'), True)}, "
              f"Jack2 {fmt(g('mix20', 'jack2', 'N_all'), True)}."]
    small = [c["id"] for c in cells if c["run"] == "R006"]
    if small:
        L += ["", "## R006 (exploratory, added after R001–R004): PH1 tolerance at E09/E10 sizes", "",
              "Logit-normal detectability; N items, K runs, mean detectability p̄. Not pre-registered.", "",
              "| Cell | N | K | σ | p̄ | S/N | Ĉ bias (MCSE) | share \\|Ĉ − C\\| ≤ 0.05 | ≤ 0.10 | P80 \\|Ĉ − C\\| | Δ̂ rel. bias |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for cid in small:
            pp, rows = params(next(c for c in cells if c["id"] == cid)), by_cell[cid]
            e = np.abs(num(rows, "coverage") - num(rows, "C"))
            e = e[np.isfinite(e)]
            L.append(f"| {cid} | {pp['N']} | {pp['K']} | {pp['sigma']:g} | {pp['mean_p']:g} | "
                     f"{summ[cid]['S_true'] / summ[cid]['N_all']:.2f} | "
                     f"{fmt(g(cid, 'coverage', 'C', 'absolute'), d=4)} ({g(cid, 'coverage', 'C', 'absolute', 'mcse'):.4f}) | "
                     f"{np.mean(e <= 0.05):.3f} | {np.mean(e <= 0.10):.3f} | {np.quantile(e, 0.8):.4f} | "
                     f"{fmt(g(cid, 'delta_K', 'Delta(K)'), True)} |")
    if bsumm:
        L += ["", "## R005: bootstrap intervals (B = 500 per replicate)", "",
              "| Cell | Ĉ normal CI covers C | Ĉ percentile CI covers C | median width | Δ̂ normal CI covers Δ | Δ̂ percentile CI covers Δ | median width |",
              "|---|---|---|---|---|---|---|"]
        for cid, s in bsumm.items():
            L.append(f"| {cid} | {s['coverage_ci_n_cover']:.3f} ({s['coverage_ci_n_cover_mcse']:.3f}) | "
                     f"{s['coverage_ci_p_cover']:.3f} ({s['coverage_ci_p_cover_mcse']:.3f}) | "
                     f"{s['coverage_ci_n_width_median']:.3f} | {s['delta_K_ci_n_cover']:.3f} ({s['delta_K_ci_n_cover_mcse']:.3f}) | "
                     f"{s['delta_K_ci_p_cover']:.3f} ({s['delta_K_ci_p_cover_mcse']:.3f}) | {s['delta_K_ci_n_width_median']:.1f} |")
    for tag, rzd in (("R007", rz), ("R008", rz8)):
      if rzd:
        rz = rzd
        L += ["", f"## {tag} (exploratory, added after R005{'; fresh datasets, replicates 10000+' if tag == 'R008' else ''}): realized-coverage bootstrap", "",
              "`crsafety.coverage_interval` / `delta_interval`, B = 500, on "
              + ("fresh datasets (the R005 column is from the other datasets, for reference). "
                 if tag == "R008" else "the same datasets as R005. ") +
              "Two-sided 95% intervals (uncorrected; bias-corrected by the mean bootstrap error) and the "
              "one-sided 95% lower bound used by stopping rules. MCSE in parentheses.", "",
              "| Cell | R005 iNEXT normal: covers C | realized: covers C | bias-corrected: covers C | "
              "P(C ≥ one-sided lower bound) | median width | Δ realized: covers Δ | Δ bias-corrected |",
              "|---|---|---|---|---|---|---|---|"]
        rzs = []
        for cid, rows in rz.items():
            C, D = num(rows, "C"), num(rows, "Delta")

            def cover(lo, hi, t):
                lo, hi = num(rows, lo), num(rows, hi)
                ok = np.isfinite(lo) & np.isfinite(hi)
                p_ = float(np.mean((np.maximum(lo, 0) <= t) & (t <= np.minimum(hi, 1 if t is C else np.inf))[ok]))
                return p_, float(np.sqrt(p_ * (1 - p_) / ok.sum()))

            def txt(v):
                return f"{v[0]:.3f} ({v[1]:.3f})"

            a, b = cover("cov_rz_lo", "cov_rz_hi", C), cover("cov_rz_bc_lo", "cov_rz_bc_hi", C)
            lo1 = num(rows, "cov_rz_lo1")
            one = float(np.mean((C >= lo1)[np.isfinite(lo1)]))
            da, db = cover("delta_rz_lo", "delta_rz_hi", D), cover("delta_rz_bc_lo", "delta_rz_bc_hi", D)
            w = float(np.nanmedian(np.minimum(num(rows, "cov_rz_hi"), 1) - np.maximum(num(rows, "cov_rz_lo"), 0)))
            ref = bsumm.get(cid, {}).get("coverage_ci_n_cover", np.nan)
            L.append(f"| {cid} | {ref:.3f} | {txt(a)} | {txt(b)} | {one:.3f} | {w:.3f} | {txt(da)} | {txt(db)} |")
            rzs.append(dict(cell=cid, cover_realized=a[0], cover_realized_mcse=a[1], cover_bc=b[0],
                            cover_bc_mcse=b[1], one_sided=one, width_median=w, delta_cover=da[0],
                            delta_cover_bc=db[0], inext_normal_cover=ref))
        with open(out_dir / f"realized_bootstrap_{tag}.csv", "w", newline="") as f:
            wr = csv.DictWriter(f, list(rzs[0]))
            wr.writeheader()
            wr.writerows(rzs)
    (out_dir / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:12 + len(H)]))


if __name__ == "__main__":
    main()
