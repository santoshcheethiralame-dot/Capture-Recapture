"""E05-R003: H5a-H5d and interval coverage from the R001/R002 injection grids.

    python analysis/e05/analyse.py [--inputs results/E05/E05-R001 results/E05/E05-R002] [--out results/E05/E05-R003]

Definitions (E05 §2a; fixed before R001 runs):
- Relative bias of a Chao2 variant = mean over injections of
  est / oracle Chao2 - 1, per (cell, f, g, pattern) "combination"; MCSE
  alongside.
- H5a: at f = 0.10, g = 0, average |relative bias| over cells and patterns,
  for naive and each correction (b at each n_v, d nof1, e1, e2). Reduction =
  1 - |corrected| / |naive|. The best reduction >= 50% supports; < 25% does
  not.
- H5b: per combination with f >= 0.05, the sign of mean(Ĉ_naive - C). C is
  the realized coverage for E01 worlds; for E02 cells the reference is the
  oracle Ĉ. Negative in >= 90% of combinations supports; positive in >= 20%
  does not.
- H5c: for (b), mean over combinations with f > 0 of
  |bias at n_v = 200| - |bias at n_v = 500|. Supported if <= 0.02 for Ĉ
  (absolute) and <= 0.05 for Chao2 (relative); not supported otherwise.
- H5d: |relative bias| of naive Chao2 at f = 0, g = 0.05. Cells are split at
  the median of their mean oracle overlap ratio. Supported if larger in the
  low-overlap half; not supported otherwise.
- Interval coverage: Chao2 CIs (naive, oracle, e1, e2) covering N (E01) and
  the oracle Chao2; the realized-coverage interval for naive and oracle Ĉ
  covering C (E01).
"""

import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORR = ["b50", "b100", "b200", "b500", "nof1", "e1", "e2"]


def load(dirs):
    rows = []
    for d in dirs:
        p = Path(d) / "injections.csv.gz"
        if not p.exists():
            continue
        with gzip.open(p, "rt") as fh:
            for r in csv.DictReader(fh):
                r["source"] = "E01" if r.get("N") not in (None, "") else "E02"
                rows.append(r)
    return rows


def num(r, k):
    v = r.get(k, "")
    try:
        return float(v)
    except (TypeError, ValueError):
        return np.nan


def chao_key(c):
    return "nof1" if c == "nof1" else f"{c}_chao2"


def mean_mcse(v):
    v = np.asarray(v, float)
    fin = v[np.isfinite(v)]
    if fin.size == 0:
        return np.nan, np.nan, v.size
    return float(fin.mean()), float(fin.std(ddof=1) / np.sqrt(fin.size)) if fin.size > 1 else np.nan, int(v.size - fin.size)


def by_combo(rows):
    g = defaultdict(list)
    for r in rows:
        g[(r["source"], r["cell"], float(r["f"]), float(r["g"]), r["pattern"])].append(r)
    return g


def rel_bias(rs, key):
    return mean_mcse([num(r, key) / num(r, "oracle_chao2") - 1 for r in rs])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", default=[str(ROOT / "results/E05/E05-R001"), str(ROOT / "results/E05/E05-R002")])
    ap.add_argument("--out", default=str(ROOT / "results/E05/E05-R003"))
    a = ap.parse_args()
    rows = load(a.inputs)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    combos = by_combo(rows)
    table = []
    for (src, cell, f, g, pat), rs in sorted(combos.items()):
        t = dict(source=src, cell=cell, f=f, g=g, pattern=pat, n=len(rs))
        for c in ["naive"] + CORR:
            t[f"{c}_chao2_relbias"], t[f"{c}_chao2_mcse"], t[f"{c}_chao2_failed"] = rel_bias(rs, chao_key(c))
        ref = "C" if src == "E01" else "oracle_coverage"
        for c in ("naive", "b50", "b100", "b200", "b500", "e1", "e2"):
            t[f"{c}_cov_bias"], t[f"{c}_cov_mcse"], _ = mean_mcse([num(r, f"{c}_coverage") - num(r, ref) for r in rs])
        t["oracle_overlap"] = float(np.nanmean([num(r, "oracle_overlap") for r in rs]))
        if src == "E01":
            for c in ("naive", "oracle", "e1", "e2"):
                t[f"{c}_chao2_ci_covers_N"] = float(np.nanmean([num(r, f"{c}_chao2_lo") <= num(r, "N") <= num(r, f"{c}_chao2_hi") for r in rs]))
            for c in ("naive", "oracle"):
                t[f"{c}_cov_ci_covers_C"] = float(np.nanmean([num(r, f"{c}_cov_lo") <= num(r, "C") <= num(r, f"{c}_cov_hi") for r in rs]))
        for c in ("naive", "e1", "e2"):
            t[f"{c}_chao2_ci_covers_oracle"] = float(np.nanmean([num(r, f"{c}_chao2_lo") <= num(r, "oracle_chao2") <= num(r, f"{c}_chao2_hi") for r in rs]))
        table.append(t)
    H = []
    # H5a
    sel = [t for t in table if t["f"] == 0.10 and t["g"] == 0.0]
    nb = np.nanmean([abs(t["naive_chao2_relbias"]) for t in sel]) if sel else np.nan
    red = {c: 1 - np.nanmean([abs(t[f"{c}_chao2_relbias"]) for t in sel]) / nb for c in CORR} if sel else {}
    best = max(red, key=lambda c: red[c] if np.isfinite(red[c]) else -np.inf) if red else None
    H.append(dict(id="H5a", estimate=f"naive |rel. bias| {nb:.3f}; best correction {best} reduces it by {red.get(best, np.nan):.0%}; "
                  + ", ".join(f"{c} {v:.0%}" for c, v in red.items()),
                  verdict="supported" if best and red[best] >= 0.5 else ("not supported" if best and red[best] < 0.25 else "inconclusive")))
    # H5b
    sel = [t for t in table if t["f"] >= 0.05]
    s = np.array([np.sign(t["naive_cov_bias"]) for t in sel if np.isfinite(t["naive_cov_bias"])])
    neg, pos = (s < 0).mean() if s.size else np.nan, (s > 0).mean() if s.size else np.nan
    H.append(dict(id="H5b", estimate=f"Ĉ − C negative in {neg:.0%}, positive in {pos:.0%} of {s.size} combinations with f ≥ 0.05",
                  verdict="supported" if neg >= 0.9 else ("not supported" if pos >= 0.2 else "inconclusive")))
    # H5c
    sel = [t for t in table if t["f"] > 0]
    dc = np.nanmean([abs(t["b200_cov_bias"]) - abs(t["b500_cov_bias"]) for t in sel]) if sel else np.nan
    dn = np.nanmean([abs(t["b200_chao2_relbias"]) - abs(t["b500_chao2_relbias"]) for t in sel]) if sel else np.nan
    H.append(dict(id="H5c", estimate=f"|bias| at n_v = 200 minus n_v = 500: Ĉ {dc:+.3f}, Chao2 {dn:+.3f}",
                  verdict="supported" if dc <= 0.02 and dn <= 0.05 else "not supported"))
    # H5d
    cells = defaultdict(list)
    for t in table:
        if t["f"] == 0.0 and t["g"] == 0.05:
            cells[(t["source"], t["cell"])].append(t)
    ov = {k: np.nanmean([t["oracle_overlap"] for t in v]) for k, v in cells.items()}
    bias = {k: np.nanmean([abs(t["naive_chao2_relbias"]) for t in v]) for k, v in cells.items()}
    if len(ov) >= 2:
        med = np.median(list(ov.values()))
        low = [bias[k] for k in ov if ov[k] < med] or [bias[min(ov, key=ov.get)]]
        high = [bias[k] for k in ov if ov[k] >= med]
        lo_b, hi_b = float(np.mean(low)), float(np.mean(high))
        H.append(dict(id="H5d", estimate=f"|rel. bias| of naive Chao2 at g = 0.05: low-overlap cells {lo_b:.3f} vs high {hi_b:.3f} ({len(ov)} cells)",
                      verdict="supported" if lo_b > hi_b else "not supported"))
    (out / "combinations.json").write_text(json.dumps(table, indent=1, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(H, indent=2) + "\n")
    L = ["# E05-R003: identity-error corrections", "", f"{len(rows)} injections, {len(table)} combinations.", "",
         "| ID | estimate | verdict |", "|---|---|---|"] + [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H]
    e01 = [t for t in table if t["source"] == "E01" and t["f"] == 0.10 and t["g"] == 0.0]
    if e01:
        L += ["", "## E01 worlds at f = 0.10, g = 0 (interval coverage of N and C)", "",
              "| cell | pattern | naive Chao2 CI ∋ N | e2 CI ∋ N | naive Ĉ CI ∋ C | oracle Ĉ CI ∋ C |", "|---|---|---|---|---|---|"]
        for t in e01:
            L.append(f"| {t['cell']} | {t['pattern']} | {t['naive_chao2_ci_covers_N']:.2f} | {t['e2_chao2_ci_covers_N']:.2f} | "
                     f"{t['naive_cov_ci_covers_C']:.2f} | {t['oracle_cov_ci_covers_C']:.2f} |")
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
