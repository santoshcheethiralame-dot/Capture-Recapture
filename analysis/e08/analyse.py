"""E08-R007: frozen confirmatory analysis of the auditor-similarity ladder (Santosh runs it).

    python analysis/e08/analyse.py --hist <dir> --out results/E08/E08-R007 [--B 2000]

<dir> holds one PROTOCOLS §10 cell per ladder level (cell ids L0, L1, L2, L3),
each with 8 estimation and 8 reference runs over the 16 planted quirks
(items.csv), judge identity. Per E08 §2:
- true pi_i per level = catch rate over all 16 runs; C(8) = coverage of the
  estimation runs under it;
- C_hat with the realized-coverage interval (D-010); Chao2 vs 16; n_eff/K;
  observed/expected overlap; union recall at K = 8;
- L3: log-linear model Mt + one shared interaction for pairs of runs from the
  same model family (family from the run's ``catcher``, matched by --families);
- H8a: (C_hat - C)_L0 - (C_hat - C)_L3, bootstrapped over organisms;
- H8b: Spearman rho of n_eff/K over L0 -> L1 -> L3;
- H8c: union recall at K = 8, L3 vs L0.
"""

import argparse
import json
import re
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety import testbed as tb  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402
from crsafety.loglin import _poisson_fit, design, history_counts, histories  # noqa: E402

LEVELS = ("L0", "L1", "L2", "L3")


def family_loglinear(X, fams):
    """Mt plus one parameter on the number of caught same-family run pairs."""
    K = X.shape[1]
    H = histories(K).astype(float)
    same = [(a, b) for a, b in combinations(range(K), 2) if fams[a] == fams[b]]
    if not same:
        return dict(N=np.nan, lambda_family=np.nan)
    col = sum(H[:, a] * H[:, b] for a, b in same)
    cols, _ = design(K, "Mt")
    D = np.column_stack([np.ones(H.shape[0]), cols, col])
    det = X[X.any(axis=1)]
    Y = history_counts(det)
    beta, cov, mu, conv, keep = _poisson_fit(Y, D)
    lam_i = int(np.sum(keep)) - 1
    return dict(N=float(det.shape[0] + np.exp(beta[0])), lambda_family=float(beta[lam_i]),
                lambda_se=float(np.sqrt(cov[lam_i, lam_i])), converged=bool(conv))


def level_stats(c, B, seed, families):
    pi = tb.true_pi(c.X_all)
    det = c.X_est[c.X_est.any(axis=1)]
    d = IncidenceData.from_matrix(det)
    ci = cr.coverage_interval(d, B=B, seed=seed)
    K = c.X_est.shape[1]
    out = dict(level=c.cell_id, K=K, N_planted=len(c.items), S=d.S, Q1=d.Q(1), Q2=d.Q(2),
               C=tb.true_coverage(c.X_est, pi), C_hat=ci["estimate"], C_lo=ci["interval"][0],
               C_hi=ci["interval"][1], chao2=cr.chao2(d), neff_over_K=tb.neff(c.X_est) / K,
               overlap=tb.overlap_ratio(c.X_est), union_recall=float(c.X_est.any(axis=1).mean()))
    if c.cell_id == "L3":
        fams = [next((f for f in families if re.search(f, s, re.I)), s) for s in c.catchers_est]
        out["family_loglinear"] = family_loglinear(c.X_est, fams)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hist", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--identity", default=None, help="identity rule to read (default: the only one present)")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--families", default="qwen,llama,gemma,mistral,phi,olmo")
    ap.add_argument("--seed", type=int, default=20261030)  # 20261022 + 8
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fam = a.families.split(",")
    cells = {L: tb.load(Path(a.hist) / L, a.identity) for L in LEVELS if (Path(a.hist) / L).exists()}
    ss = np.random.SeedSequence(a.seed).spawn(len(cells) + 3)
    stats = {L: level_stats(c, a.B, ss[k], fam) for k, (L, c) in enumerate(cells.items())}

    def err(c, idx):
        Xe, Xa = c.X_est[idx], c.X_all[idx]
        det = Xe[Xe.any(axis=1)]
        if det.shape[0] < 2:
            return np.nan
        return cr.coverage(det) - tb.true_coverage(Xe, tb.true_pi(Xa))

    H = []
    if "L0" in cells and "L3" in cells:
        n = len(cells["L0"].items)
        diff = stats["L0"]["C_hat"] - stats["L0"]["C"] - (stats["L3"]["C_hat"] - stats["L3"]["C"])
        ci = tb.boot_items(lambda i: err(cells["L0"], i) - err(cells["L3"], i), n, a.B, ss[-1])
        H.append(dict(id="H8a", estimate=diff, ci=ci, verdict=tb.verdict(diff, ci, 0.05, 0.02),
                      measure="(C_hat - C) at L0 minus at L3"))
        rec = stats["L3"]["union_recall"] - stats["L0"]["union_recall"]
        rci = tb.boot_items(lambda i: cells["L3"].X_est[i].any(axis=1).mean() - cells["L0"].X_est[i].any(axis=1).mean(),
                            n, a.B, ss[-2])
        H.append(dict(id="H8c", estimate=rec, ci=rci, measure="union recall at K = 8, L3 minus L0",
                      verdict="supported" if rec > 0 else ("not supported" if rec < 0 else "inconclusive")))
    order = [L for L in ("L0", "L1", "L3") if L in stats]
    if len(order) >= 3:
        rho = spearmanr(range(len(order)), [stats[L]["neff_over_K"] for L in order]).statistic
        H.append(dict(id="H8b", estimate=float(rho), ci=(np.nan, np.nan), measure="Spearman rho of n_eff/K over L0, L1, L3",
                      verdict="supported" if rho > 0 else ("not supported" if rho < 0 else "inconclusive")))
    (out / "levels.json").write_text(json.dumps(stats, indent=2, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2, default=float) + "\n")
    L = ["# E08 analysis", "", "| level | K | S | C | Ĉ (95% CI) | Chao2 (lower bound) | n_eff/K | overlap o/e | union recall |",
         "|---|---|---|---|---|---|---|---|---|"]
    for s in stats.values():
        L.append(f"| {s['level']} | {s['K']} | {s['S']} | {s['C']:.3f} | {s['C_hat']:.3f} ({s['C_lo']:.3f}–{s['C_hi']:.3f}) | "
                 f"{s['chao2']:.1f} | {s['neff_over_K']:.2f} | {s['overlap']:.2f} | {s['union_recall']:.2f} |")
    L += ["", "| ID | measure | estimate (95% CI) | verdict |", "|---|---|---|---|"]
    for h in H:
        L.append(f"| {h['id']} | {h['measure']} | {h['estimate']:+.3f} ({h['ci'][0]:+.3f}, {h['ci'][1]:+.3f}) | **{h['verdict']}** |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
