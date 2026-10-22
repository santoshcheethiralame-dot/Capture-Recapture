"""E00-R003 step 3: compare the R003 estimators with their R references (H0a).

    python validation/e00/compare_r003.py results/E00/E00-R003

Reads <dir>/data/*.csv and <dir>/reference.json; writes <dir>/comparison.csv
and <dir>/summary.md. Exits non-zero if any comparison fails.

Tolerance: relative difference <= 1e-6 (H0a). Deviance, AIC and BIC are
compared relative to max(|reference|, 1), since a deviance can be ~0.
Log-linear standard errors are compared with the s.e. computed in R from the
Fisher information at Rcapture's fitted coefficients (Rcapture's formulas);
the s.e. Rcapture prints uses glm's vcov(), which is evaluated at the IRLS
weights of the previous iterate, and is compared as information only
(tolerance 1e-4). Fits where N_hat = S (the intercept diverges to -inf)
have a numerically arbitrary s.e. near 0; their s.e. is compared in absolute
terms.
breakaway_nof1 is called through crsafety.rbridge and compared with the
same function called directly in R, which checks the bridge (frequency
table, argument passing, output parsing), not the method.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

import crsafety as cr
from crsafety import rbridge
from crsafety.estimators import IncidenceData
from crsafety.loglin import loglinear

TOL = 1e-6
CLOSEDP = {
    "M0": ("M0", None), "Mt": ("Mt", None),
    "Mh Chao (LB)": ("Mh", "Chao"), "Mh Poisson2": ("Mh", "Poisson"),
    "Mh Darroch": ("Mh", "Darroch"), "Mh Gamma3.5": ("Mh", "Gamma"),
    "Mth Chao (LB)": ("Mth", "Chao"), "Mth Poisson2": ("Mth", "Poisson"),
    "Mth Darroch": ("Mth", "Darroch"), "Mth Gamma3.5": ("Mth", "Gamma"),
    "Mb": ("Mb", None), "Mbh": ("Mbh", None),
}


def rel(a, b, floor=0.0):
    return abs(a - b) / max(abs(b), floor) if max(abs(b), floor) > 0 else abs(a - b)


def load(path):
    X = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2).astype(int)
    return path.stem, IncidenceData.from_matrix(X)


def row(dataset, quantity, reference, ours, theirs, floor=0.0):
    r = rel(ours, theirs, floor)
    return dict(dataset=dataset, quantity=quantity, reference=reference, ours=ours, ref=theirs,
                abs_diff=abs(ours - theirs), rel_diff=r, tolerance=TOL, hypothesis="H0a",
                passed=bool(r <= TOL))


def main(run_dir):
    run_dir = Path(run_dir)
    ref = json.load(open(run_dir / "reference.json"))
    rows, data = [], {}
    for path in sorted((run_dir / "data").glob("*.csv")):
        name, d = load(path)
        data[name] = d
        r = ref["datasets"][name]
        assert (r["K"], r["S"], r["U"]) == (d.K, d.S, d.U), name
        for model, rr in (r.get("loglinear") or {}).items():
            if rr is None or rr.get("N") is None:
                continue
            if model in CLOSEDP:
                m, h = CLOSEDP[model]
                ours = loglinear(d, m, h)
                src = "Rcapture::closedp.t"
            else:
                ours = loglinear(d, "Mt", None if rr["h"] is None else rr["h"],
                                 interactions=[tuple(p) for p in rr["pairs"]])
                src = "Rcapture::closedpCI.t"
            tag = f"loglinear[{model}]"
            rows.append(row(name, tag + ".N", src, ours["N"], rr["N"]))
            boundary = rr["N"] - d.S < 1e-6  # N_hat = S: intercept diverges, s.e. is ~0 noise
            if rr.get("se") is not None:
                rows.append(row(name, tag + ".se", src + " (Fisher information at the MLE)",
                                ours["se"], rr["se"], floor=1.0 if boundary else 0.0))
            if rr.get("se_printed") is not None:
                r_ = row(name, tag + ".se_printed", src + " (printed; glm vcov)", ours["se"],
                         rr["se_printed"], floor=1.0 if boundary else 0.0)
                r_["hypothesis"], r_["tolerance"] = "info", 1e-4
                r_["passed"] = bool(r_["rel_diff"] <= 1e-4)
                rows.append(r_)
            for q in ("deviance", "aic", "bic"):
                rows.append(row(name, f"{tag}.{q}", src, ours[q], rr[q], floor=1.0))
            if rr.get("df") is not None and ours["df"] != rr["df"]:
                rows.append(row(name, tag + ".df", src, ours["df"], rr["df"]))
        if r.get("gen_chao") is not None:
            ours = cr.generalized_chao(d)[0]
            rows.append(row(name, "generalized_chao", "stats::glm (binomial, offset)", ours,
                            r["gen_chao"]["N"]))
            if r.get("inext_chao2") is not None:
                rows.append(row(name, "generalized_chao=chao2", "iNEXT::ChaoRichness", ours,
                                r["inext_chao2"]))
    for name, h in (ref.get("gen_chao_cov") or {}).items():
        M = np.loadtxt(run_dir / "data" / "huggins" / f"{name}.csv", delimiter=",", skiprows=1, ndmin=2)
        cols = open(run_dir / "data" / "huggins" / f"{name}.csv").readline().strip().split(",")
        ny = sum(c.startswith("y") for c in cols)
        N, beta, _ = cr.generalized_chao(M[:, :ny].astype(int), M[:, ny:])
        rows.append(row(name, "generalized_chao_cov", "stats::glm (binomial, offset)", N, h["N"]))
        for b, rb in zip(beta, h["beta"]):
            rows.append(row(name, "generalized_chao_cov.beta", "stats::glm (binomial, offset)", b, rb))

    names = [n for n in data if ref["datasets"][n].get("breakaway_nof1")]
    bridged = rbridge.breakaway_nof1(*[data[n] for n in names])
    for n, b in zip(names, bridged):
        rr = ref["datasets"][n]["breakaway_nof1"]
        for q in ("estimate", "error"):
            if rr.get(q) is not None and b.get(q) is not None:
                rows.append(row(n, f"breakaway_nof1.{q}", "breakaway::breakaway_nof1 (direct call)",
                                b[q], rr[q]))

    with open(run_dir / "comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    def family(q):
        if q.startswith("loglinear["):
            model = q[len("loglinear["):q.index("]")]
            return ("closedp.t " if model in CLOSEDP else "closedpCI.t ") + q[q.index("]") + 2:]
        return q
    fams = {}
    for r_ in rows:
        fams.setdefault(family(r_["quantity"]), []).append(r_)
    m = ref["meta"]
    lines = ["# E00-R003 comparison\n",
             f"References: {m['R']}; Rcapture {m['Rcapture']}; breakaway {m['breakaway']}; "
             f"iNEXT {m['iNEXT']}.\n",
             f"Datasets: {len({r_['dataset'] for r_ in rows})}. Comparisons: {len(rows)}.\n",
             "| Quantity | Reference | Hypothesis | Comparisons | Datasets | Max rel. diff | Failures |",
             "|---|---|---|---|---|---|---|"]
    for q, sub in fams.items():
        lines.append(f"| {q} | {sub[0]['reference']} | {sub[0]['hypothesis']} | {len(sub)} | "
                     f"{len({s['dataset'] for s in sub})} | "
                     f"{max(s['rel_diff'] for s in sub):.2e} | {sum(not s['passed'] for s in sub)} |")
    failed = [r_ for r_ in rows if not r_["passed"] and r_["hypothesis"] == "H0a"]
    lines.append("")
    lines.append("All comparisons passed." if not failed else f"**{len(failed)} comparisons failed:**")
    for r_ in failed:
        lines.append(f"- {r_['dataset']} {r_['quantity']}: ours {r_['ours']:.10g}, "
                     f"reference {r_['ref']:.10g} (rel. diff {r_['rel_diff']:.2e})")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results/E00/E00-R003"))
