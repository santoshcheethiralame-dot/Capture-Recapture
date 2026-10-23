"""E10-R007: frozen confirmatory analysis of the planted-blind-spot red team (Santosh runs it).

    python analysis/e10/analyse.py --hist <dir> --out results/E10/E10-R007 [--B 2000]
        [--judge judge:<rubric_version>]

<dir> holds one PROTOCOLS §10 cell per arm (cell ids A1, A2, A4, A5), each
with 12 estimation and 12 reference runs over the M = 20 planted blind spots
(items.csv), instrumented identity. Arm A3 is A2's estimation runs,
de-adapted (no new runs): A3a = Liyanage et al. (ICSE 2024) Algorithm 1 and
A3b = the reset estimator (Böhme et al. 2021), both from
``crsafety.deadapt`` with rows = runs in run_idx order (E10 §2 as written;
see E01-R009 and Q-D7 for how they behave).
Per E10 §2:
- true pi per arm from ``--truth`` (D-013): the arm's 12 reference runs
  (default, as E10 §2 says), all 24 runs (``pooled``, always reported as
  C_pooled), or named arms' reference runs (``cells:A1,A5``, the
  catcher-agnostic truth of Kushal's review); C(12) of the estimation runs;
- H10a: |C_hat - C| for A1 <= 0.05 (supported), > 0.10 (not);
- H10b: C_hat - C for A2 >= +0.05 (supported), < +0.02 (not);
- H10c: 1 - |C_A3a - C_A2| / |C_hat_A2 - C_A2| >= 0.5 (supported), < 0.25 (not);
  A3b reported alongside;
- H10d: (C_hat - C) A4 < A2;
- H10e: |err_judge| - |err_instrumented| per arm, if --judge cells exist.
Intervals: bootstrap over blind spots.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety import deadapt as da  # noqa: E402
from crsafety import testbed as tb  # noqa: E402
from crsafety.estimators import IncidenceData  # noqa: E402

ARMS = ("A1", "A2", "A4", "A5")


def cov_hat(X):
    det = X[X.any(axis=1)]
    return cr.coverage(IncidenceData.from_matrix(det)) if det.shape[0] >= 2 else np.nan


def err(c, pi, idx=None):
    Xe, p = (c.X_est, pi) if idx is None else (c.X_est[idx], pi[idx])
    return cov_hat(Xe) - tb.true_coverage(Xe, p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hist", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--identity", default="instrumented")
    ap.add_argument("--judge", default=None, help="identity label of the judge-based histories (H10e)")
    ap.add_argument("--B", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261032)  # 20261022 + 10
    ap.add_argument("--truth", default="reference", help="reference | pooled | cells:A1,A5,... (D-013)")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cells = {A: tb.load(Path(a.hist) / A, a.identity) for A in ARMS if (Path(a.hist) / A).exists()}
    n = len(next(iter(cells.values())).items)
    ss = np.random.SeedSequence(a.seed).spawn(16)
    rows = {}
    PI = {A: tb.truth_pi(cells, A, a.truth) for A in cells}
    for A, c in cells.items():
        C = tb.true_coverage(c.X_est, PI[A])
        rows[A] = dict(arm=A, K=c.X_est.shape[1], S=int(c.X_est.any(axis=1).sum()), C=C, truth=a.truth,
                       C_pooled=tb.true_coverage(c.X_est, tb.true_pi(c.X_all)), C_hat=cov_hat(c.X_est),
                       err=cov_hat(c.X_est) - C, chao2=cr.chao2(c.X_est[c.X_est.any(axis=1)]))
    H = []
    if "A1" in cells:
        e = abs(rows["A1"]["err"])
        ci = tb.boot_items(lambda i: abs(err(cells["A1"], PI["A1"], i)), n, a.B, ss[0])
        H.append(dict(id="H10a", measure="|C_hat - C|, A1", estimate=e, ci=ci,
                      verdict=tb.verdict(e, ci, 0.05, 0.10, higher_is_support=False)))
    if "A2" in cells:
        c2 = cells["A2"]
        W = c2.X_est.T  # runs x blind spots, run_idx order
        C2 = rows["A2"]["C"]
        a3a = da.deadapted_coverage(W, "A3a", seed=ss[1])
        a3b = da.deadapted_coverage(W, "A3b", seed=ss[2])
        rows["A3a"] = dict(arm="A3a (de-adapted A2)", C=C2, C_hat=a3a, err=a3a - C2)
        rows["A3b"] = dict(arm="A3b (de-adapted A2)", C=C2, C_hat=a3b, err=a3b - C2)
        e2 = rows["A2"]["err"]
        ci = tb.boot_items(lambda i: err(c2, PI["A2"], i), n, a.B, ss[3])
        H.append(dict(id="H10b", measure="C_hat - C, A2", estimate=e2, ci=ci, verdict=tb.verdict(e2, ci, 0.05, 0.02)))

        def red(idx, method="A3a"):
            Xe = c2.X_est[idx]
            Ct = tb.true_coverage(Xe, PI["A2"][idx])
            base = abs(cov_hat(Xe) - Ct)
            dd = da.deadapted_coverage(Xe.T, method, seed=0)
            return 1 - abs(dd - Ct) / base if base > 0 else np.nan
        r = 1 - abs(a3a - C2) / abs(e2) if e2 != 0 else np.nan
        ci = tb.boot_items(red, n, min(a.B, 500), ss[4])
        H.append(dict(id="H10c", measure="1 - |A3a - C| / |C_hat_A2 - C| (A3b: "
                      f"{1 - abs(a3b - C2) / abs(e2) if e2 != 0 else float('nan'):+.3f})",
                      estimate=r, ci=ci, verdict=tb.verdict(r, ci, 0.5, 0.25)))
    if "A2" in cells and "A4" in cells:
        dlt = rows["A4"]["err"] - rows["A2"]["err"]
        ci = tb.boot_items(lambda i: err(cells["A4"], PI["A4"], i) - err(cells["A2"], PI["A2"], i), n, a.B, ss[5])
        H.append(dict(id="H10d", measure="(C_hat - C) A4 minus A2", estimate=dlt, ci=ci,
                      verdict="supported" if dlt < 0 else "not supported"))
    if a.judge:
        e10e = {}
        for A in cells:
            try:
                cj = tb.load(Path(a.hist) / A, a.judge)
            except Exception as ex:  # judge histories missing for this arm
                e10e[A] = f"unavailable: {ex}"
                continue
            ej = cov_hat(cj.X_est) - tb.true_coverage(cells[A].X_est, PI[A])
            e10e[A] = abs(ej) - abs(rows[A]["err"])
        H.append(dict(id="H10e", measure="|err_judge| - |err_instrumented| per arm (descriptive)",
                      estimate=e10e, ci=(np.nan, np.nan), verdict="descriptive"))
    (out / "arms.json").write_text(json.dumps(rows, indent=2, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2, default=float) + "\n")
    L = ["# E10 analysis", "", f"M = {n} blind spots; identity: {a.identity}; truth: {a.truth} (D-013).", "",
         "| arm | C | Ĉ | Ĉ − C |", "|---|---|---|---|"]
    for r in rows.values():
        L.append(f"| {r['arm']} | {r['C']:.3f} | {r['C_hat']:.3f} | {r['err']:+.3f} |")
    L += ["", "| ID | measure | estimate (95% CI) | verdict |", "|---|---|---|---|"]
    for h in H:
        est = h["estimate"] if isinstance(h["estimate"], dict) else f"{h['estimate']:+.3f} ({h['ci'][0]:+.3f}, {h['ci'][1]:+.3f})"
        L.append(f"| {h['id']} | {h['measure']} | {est} | **{h['verdict']}** |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
