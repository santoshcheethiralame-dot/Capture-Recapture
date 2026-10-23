"""E09-R008: frozen confirmatory analysis of AuditBench-lite (Santosh runs it).

    python analysis/e09/analyse.py --hist <dir> --out results/E09/E09-R008 [--tol 0.05] [--B 2000]

<dir> holds one PROTOCOLS §10 cell per tool configuration (cell ids T1, T2,
T3), each with 8 estimation and 8 reference runs over the planted organisms
(items.csv; organisms excluded at implant verification are simply absent).
Per E09 §2:
- Design A per configuration: true pi from ``--truth`` (D-013; default the
  configuration's 8 reference runs; ``pooled`` = all 16, always reported as
  C_pooled; ``cells:T1,T2,T3`` = all configurations' reference runs), C(8);
  C_hat with the realized-coverage interval (D-010); Chao2 vs N and |U_c|
  (organisms caught by any run of any configuration); leave-half-out:
  Delta_hat(8) from runs 1-8 vs organisms first found in runs 9-16.
- Design B: the 3 configurations as lists (caught in the 8 estimation runs);
  log-linear Mt + lambda_12 + one shared interaction lambda_{(12)3} on
  (c1 c3 + c2 c3); Wald 95% interval.
- H9a: |C_hat - C| <= tol in >= 2 of 3 configurations (supported), 0 of 3
  (not supported). ``--tol`` defaults to the pre-registered 0.05 (D-010 B
  proposes a different criterion for small N; decided at the freeze).
- H9b: Chao2 < N for every configuration where |U_c| < N (descriptive).
- H9c: |Delta_hat - Delta| / max(Delta, 1) <= 0.5 for >= 2 of 3.
- H9d: lambda_{(12)3} < 0 with the interval excluding 0.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety import testbed as tb  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402
from crsafety.loglin import _poisson_fit, design, history_counts, histories  # noqa: E402

CONFIGS = ("T1", "T2", "T3")


def design_b(L):
    """L: organisms x 3 lists (T1, T2, T3). Returns lambda_{(12)3}, its s.e., and N_hat."""
    H = histories(3).astype(float)
    cols, _ = design(3, "Mt")
    D = np.column_stack([np.ones(H.shape[0]), cols, H[:, 0] * H[:, 1], H[:, 0] * H[:, 2] + H[:, 1] * H[:, 2]])
    det = L[L.any(axis=1)]
    beta, cov, mu, conv, keep = _poisson_fit(history_counts(det), D)
    if not keep.all():
        return dict(lambda_12_3=np.nan, se=np.nan, N=np.nan, converged=False, note="design not of full rank")
    return dict(lambda_12_3=float(beta[-1]), se=float(np.sqrt(cov[-1, -1])),
                N=float(det.shape[0] + np.exp(beta[0])), converged=bool(conv))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hist", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--identity", default=None)
    ap.add_argument("--tol", type=float, default=0.05)
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261031)  # 20261022 + 9
    ap.add_argument("--truth", default="reference", help="reference | pooled | cells:T1,T2,T3 (D-013)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cells = {T: tb.load(Path(a.hist) / T, a.identity) for T in CONFIGS if (Path(a.hist) / T).exists()}
    items = cells[next(iter(cells))].items
    if any(c.items != items for c in cells.values()):
        sys.exit("configurations must share the same planted organisms")
    N = len(items)
    Uc = np.zeros(N, bool)
    for c in cells.values():
        Uc |= c.X_all.any(axis=1)
    ss = np.random.SeedSequence(a.seed).spawn(len(cells))
    rows = {}
    for k, (T, c) in enumerate(cells.items()):
        pi = tb.truth_pi(cells, T, a.truth)
        det = c.X_est[c.X_est.any(axis=1)]
        d = IncidenceData.from_matrix(det)
        ci = cr.coverage_interval(d, B=a.B, seed=ss[k])
        delta = int((c.X_ref.any(axis=1) & ~c.X_est.any(axis=1)).sum())
        dhat = cr.extrapolate(d, c.X_ref.shape[1])
        rows[T] = dict(config=T, K=c.X_est.shape[1], S=d.S, C=tb.true_coverage(c.X_est, pi), truth=a.truth,
                       C_pooled=tb.true_coverage(c.X_est, tb.true_pi(c.X_all)), C_hat=ci["estimate"],
                       C_lo=ci["interval"][0], C_hi=ci["interval"][1], chao2=cr.chao2(d), N=N, U_c=int(Uc.sum()),
                       delta=delta, delta_hat=dhat, delta_rel_err=abs(dhat - delta) / max(delta, 1))
    n_ok = sum(abs(r["C_hat"] - r["C"]) <= a.tol for r in rows.values())
    H = [dict(id="H9a", estimate=f"{n_ok} of {len(rows)} configurations with |C_hat - C| <= {a.tol}",
              verdict="supported" if n_ok >= 2 else ("not supported" if n_ok == 0 else "inconclusive"))]
    chk = [r["chao2"] < N for r in rows.values() if r["U_c"] < N]
    H.append(dict(id="H9b", estimate=f"Chao2 < {N} in {sum(chk)} of {len(chk)} configurations with |U_c| < N "
                  f"(|U_c| = {int(Uc.sum())})", verdict=("descriptive: holds" if all(chk) else "descriptive: does not hold")
                  if chk else "descriptive: |U_c| = N, not applicable"))
    n_c = sum(r["delta_rel_err"] <= 0.5 for r in rows.values())
    H.append(dict(id="H9c", estimate=f"{n_c} of {len(rows)} with |Delta_hat - Delta| / max(Delta, 1) <= 0.5",
                  verdict="supported" if n_c >= 2 else ("not supported" if n_c == 0 else "inconclusive")))
    if len(cells) == 3:
        Lmat = np.column_stack([cells[T].X_est.any(axis=1) for T in CONFIGS]).astype(np.int8)
        b = design_b(Lmat)
        lo, hi = b["lambda_12_3"] - 1.96 * b["se"], b["lambda_12_3"] + 1.96 * b["se"]
        v = "inconclusive" if not np.isfinite(lo) else ("supported" if hi < 0 else ("not supported" if lo > 0 else "inconclusive"))
        H.append(dict(id="H9d", estimate=f"lambda_(12)3 = {b['lambda_12_3']:+.3f} (95% CI {lo:+.3f}, {hi:+.3f})",
                      verdict=v, design_b=b))
    (out / "configs.json").write_text(json.dumps(rows, indent=2, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2, default=float) + "\n")
    L = ["# E09 analysis", "", f"N = {N} organisms; tolerance {a.tol}.", "",
         "| config | S | C | Ĉ (95% CI) | Chao2 (lower bound) | Δ (runs 9–16) | Δ̂(8) |", "|---|---|---|---|---|---|---|"]
    for r in rows.values():
        L.append(f"| {r['config']} | {r['S']} | {r['C']:.3f} | {r['C_hat']:.3f} ({r['C_lo']:.3f}–{r['C_hi']:.3f}) | "
                 f"{r['chao2']:.1f} | {r['delta']} | {r['delta_hat']:.2f} |")
    L += ["", "| ID | estimate | verdict |", "|---|---|---|"] + [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
