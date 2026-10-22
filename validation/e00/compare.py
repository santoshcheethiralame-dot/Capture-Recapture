"""E00-R001 step 3: compare crsafety with the R references (H0a, H0b).

    python validation/e00/compare.py results/E00/E00-R001

Reads <dir>/data/*.csv and <dir>/reference.json; writes <dir>/comparison.csv
and <dir>/summary.md. Exits non-zero if any comparison fails.
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

import crsafety as cr
from crsafety.estimators import IncidenceData

H0A_TOL = 1e-6  # max relative difference for deterministic estimators
B = 2000
SEED = 20261022

DETERMINISTIC = {
    # quantity: (function of IncidenceData, reference key, needs matrix)
    "chao2": (lambda d: cr.chao2(d), "chao2", False),
    "chao2_vegan": (lambda d: cr.chao2(d), "vegan_chao2", False),
    "chao2_se": (lambda d: cr.chao2_ci(d)[1], "chao2_se", False),
    "chao2_lo": (lambda d: cr.chao2_ci(d)[2], "chao2_lo", False),
    "chao2_hi": (lambda d: cr.chao2_ci(d)[3], "chao2_hi", False),
    "coverage": (lambda d: cr.coverage(d), "coverage", False),
    "new_items_1xK": (lambda d: cr.extrapolate(d, d.K), "ext_1xK", False),
    "new_items_2xK": (lambda d: cr.extrapolate(d, 2 * d.K), "ext_2xK", False),
    "ichao2": (lambda d: cr.ichao2(d), "ichao2", False),
    "ice": (lambda d: cr.ice(d), "ice", False),
    "jackknife1": (lambda d: cr.jackknife(d, 1), "jack1", False),
    "jackknife2": (lambda d: cr.jackknife(d, 2), "jack2", False),
    "darroch_mt": (lambda d: cr.darroch_mt(d), "darroch_mt", True),
}
REFERENCE_OF = {
    "chao2": "iNEXT::ChaoRichness", "chao2_vegan": "vegan::specpool",
    "chao2_se": "iNEXT::ChaoRichness", "chao2_lo": "iNEXT::ChaoRichness",
    "chao2_hi": "iNEXT::ChaoRichness", "coverage": "iNEXT:::Chat.Sam",
    "new_items_1xK": "iNEXT:::TD.m.est_inc", "new_items_2xK": "iNEXT:::TD.m.est_inc",
    "ichao2": "SpadeR::SpecInciiChao2", "ice": "SpadeR::SpecInciModelh",
    "jackknife1": "vegan::specpool", "jackknife2": "vegan::specpool",
    "darroch_mt": "Rcapture::closedp.t (Mt)",
    "huggins_N": "VGAM::vglm posbernoulli.t", "huggins": "VGAM::vglm posbernoulli.t (coefficients)",
    "boot_se_S2K": "iNEXT:::iNEXT.Sam bootstrap", "boot_se_cov": "iNEXT:::iNEXT.Sam bootstrap",
}


def load(path):
    if path.name.endswith(".freq.csv"):
        spec = [int(r["y"]) for r in csv.DictReader(open(path))]
        return path.name[: -len(".freq.csv")], IncidenceData.from_counts(spec[1:], spec[0])
    X = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2).astype(int)
    return path.stem, IncidenceData.from_matrix(X)


def rel(a, b):
    """Relative difference; absolute when the reference is exactly 0."""
    return abs(a - b) / abs(b) if b != 0 else abs(a - b)


def main(run_dir):
    run_dir = Path(run_dir)
    ref = json.load(open(run_dir / "reference.json"))
    rows = []
    for path in sorted((run_dir / "data").glob("*.csv")):
        name, d = load(path)
        r = ref["datasets"][name]
        assert (r["K"], r["S"], r["U"]) == (d.K, d.S, d.U), name
        for q, (f, key, needs_X) in DETERMINISTIC.items():
            if r.get(key) is None or (needs_X and d.X is None):
                continue
            ours, theirs = float(f(d)), float(r[key])
            rows.append(dict(dataset=name, quantity=q, reference=REFERENCE_OF[q], ours=ours,
                             ref=theirs, abs_diff=abs(ours - theirs), rel_diff=rel(ours, theirs),
                             tolerance=H0A_TOL, hypothesis="H0a",
                             passed=rel(ours, theirs) <= H0A_TOL))
        # H0b: bootstrap s.e. agree within 3 Monte Carlo s.e. of the difference
        boots = {
            "boot_se_S2K": lambda e: e.S + cr.extrapolate(e, e.K),
            "boot_se_cov": cr.coverage,
        }
        for key, stat in boots.items():
            se_ref = r.get(key)
            if se_ref is None or se_ref == 0 or (key == "boot_se_cov" and r.get("boot_cov_clipped")):
                continue
            se = cr.bootstrap(d, stat, B=B, seed=SEED)["se"]
            mcse = np.sqrt(se**2 / (2 * (B - 1)) + se_ref**2 / (2 * (B - 1)))
            rows.append(dict(dataset=name, quantity=key, reference=REFERENCE_OF[key], ours=se,
                             ref=se_ref, abs_diff=abs(se - se_ref), rel_diff=rel(se, se_ref),
                             tolerance=3 * mcse, hypothesis="H0b",
                             passed=abs(se - se_ref) <= 3 * mcse))

    for path in sorted((run_dir / "data" / "huggins").glob("*.csv")):
        M = np.loadtxt(path, delimiter=",", skiprows=1, ndmin=2)
        cols = open(path).readline().strip().split(",")
        ny = sum(c.startswith("y") for c in cols)
        N_hat, beta, _ = cr.huggins(M[:, :ny].astype(int), M[:, ny:])
        h = ref["huggins"][path.stem]
        pairs = [("huggins_N", N_hat, h["N_hat"])] + [
            (f"huggins_beta{j}", b, rb) for j, (b, rb) in enumerate(zip(beta, h["beta"]))]
        for q, ours, theirs in pairs:
            rows.append(dict(dataset=path.stem, quantity=q.split("_beta")[0] if "beta" in q else q,
                             reference="VGAM::vglm posbernoulli.t", ours=float(ours), ref=float(theirs),
                             abs_diff=abs(ours - theirs), rel_diff=rel(ours, theirs),
                             tolerance=H0A_TOL, hypothesis="H0a", passed=rel(ours, theirs) <= H0A_TOL))

    with open(run_dir / "comparison.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    lines = [f"# E00-R001 comparison\n",
             f"References: R {ref['meta']['R']}; iNEXT {ref['meta']['iNEXT']}; "
             f"vegan {ref['meta']['vegan']}; VGAM {ref['meta']['VGAM']}; Rcapture {ref['meta']['Rcapture']}; SpadeR (github.com/cran/SpadeR).\n",
             f"Datasets: {len({r['dataset'] for r in rows})}. Comparisons: {len(rows)}.\n",
             "| Quantity | Reference | Hypothesis | Datasets | Max rel. diff | Failures |",
             "|---|---|---|---|---|---|"]
    for q in list(DETERMINISTIC) + ["huggins_N", "huggins", "boot_se_S2K", "boot_se_cov"]:
        sub = [r for r in rows if r["quantity"] == q]
        if not sub:
            continue
        lines.append(f"| {q} | {REFERENCE_OF[q]} | {sub[0]['hypothesis']} | {len(sub)} | "
                     f"{max(r['rel_diff'] for r in sub):.2e} | {sum(not r['passed'] for r in sub)} |")
    failed = [r for r in rows if not r["passed"]]
    lines.append("")
    lines.append("All comparisons passed." if not failed else f"**{len(failed)} comparisons failed:**")
    for r in failed:
        lines.append(f"- {r['dataset']} {r['quantity']}: ours {r['ours']:.10g}, "
                     f"reference {r['ref']:.10g} (rel. diff {r['rel_diff']:.2e}, tol {r['tolerance']:.2e})")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "results/E00/E00-R001"))
