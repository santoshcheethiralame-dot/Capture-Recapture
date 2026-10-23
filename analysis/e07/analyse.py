"""E07-R001: covariate models on the E02 and E06 oracle histories (CPU).

    python analysis/e07/analyse.py --out results/E07/E07-R001 \
        --e02 <e02>/histories/oracle_tgt0.7 [--e06 <e06 root>] [--p-threshold auto]

Inputs are PROTOCOLS §10 cells written by `analysis/e02/zoo.py histories`
(with `--fire-counts`, so items.csv carries the observed covariates). Per
E07 §2, for each cell (estimation runs only):
- x1 = log p_i (oracle); x2 = log p_i + N(0, s^2), s in {0.5, 1} (seeded per
  cell and s); x3 = log firing frequency of the matched latent; x4 = (mean
  activation, max |cos| to another latent of the same SAE). x3 and x4 are
  per run; an item gets the mean over the estimation runs that caught it.
  All covariates are standardised over the detected items (N_hat unchanged).
- Huggins (logistic, Horvitz-Thompson; `crsafety.huggins_ci`) and Böhning
  generalised Chao with each covariate set; Chao2 and iChao2 as comparators.
- Targets: |U| (E02: features caught by any SAE of the architecture, all L0
  and seeds; E06: by any of the cell's 24 seeds) and N_thr, the planted
  features with p >= the threshold (``auto``: the smallest p in U; E07 §2a).
- H7a: |rel. bias| of Huggins-x1 vs |U| <= 0.10 in >= 80% of cells
  (supported), > 0.20 in more than half (not supported). H7b, for x3 and
  for x4 separately: |rel. bias| lower than Chao2's in >= 70% of cells
  (supported), < 50% (not supported). H7c: sign of the bias of Huggins-x2 at
  s = 1 (reported). Non-converging fits are counted, never dropped silently:
  a cell where a model failed counts as not meeting its criterion.
- E07 §3 contingency: every Huggins fit also records its largest
  Horvitz-Thompson weight and N_hat with weights truncated at 100.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import crsafety as cr  # noqa: E402
from crsafety.histories import read_cell  # noqa: E402

MASTER = 20261029  # 20261022 + 7
NOISE = (0.5, 1.0)


def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (float(c - h), float(c + h))


def load(cdir):
    """(item ids, p, X_est, X_all, estimation run seeds, covariate dicts) for planted items."""
    est, allr = read_cell(cdir, role="estimation"), read_cell(cdir, role=None)
    ids = sorted((k for k, v in allr.items.items() if v["planted"]), key=lambda s: (len(s), s))

    def full(c):
        pos = {i: r for r, i in enumerate(c.item_ids)}
        X = np.zeros((len(ids), c.X.shape[1]), np.int8)
        for r, i in enumerate(ids):
            if i in pos:
                X[r] = c.X[pos[i]]
        return X

    cov = [allr.items[i]["covariates"] for i in ids]
    p = np.array([c["p"] for c in cov], float)
    return ids, p, full(est), full(allr), [str(r["seed"]) for r in est.runs], cov


def run_mean(cov, name, seeds, Xrow):
    v = [cov[name][s] for s, hit in zip(seeds, Xrow) if hit and s in cov.get(name, {})]
    return float(np.mean(v)) if v else np.nan


def designs(p, X, seeds, cov, rng):
    det = X.any(axis=1)
    lp = np.log(p[det])
    Zs = {"x1": lp[:, None]}
    for s in NOISE:
        Zs[f"x2_s{s}"] = (lp + rng[s].normal(0, s, lp.size))[:, None]
    dc = [c for c, d in zip(cov, det) if d]
    Xd = X[det]
    Zs["x3"] = np.array([[run_mean(c, "log_freq", seeds, x)] for c, x in zip(dc, Xd)])
    Zs["x4"] = np.array([[run_mean(c, "mean_act", seeds, x), run_mean(c, "max_cos", seeds, x)]
                         for c, x in zip(dc, Xd)])
    out = {}
    for k, Z in Zs.items():
        if Z.size == 0 or np.isnan(Z).any():
            out[k] = None  # covariate not recorded (e.g. no fire counts): counted as unavailable
            continue
        sd = Z.std(axis=0)
        out[k] = (Z - Z.mean(axis=0)) / np.where(sd > 0, sd, 1)
    return Xd, out


def analyse_cell(name, p, X, seeds, cov, U, N_thr, rng):
    Xd, Zs = designs(p, X, seeds, cov, rng)
    r = dict(cell=name, K=X.shape[1], S_obs=int(Xd.shape[0]), U=int(U), N_thr=int(N_thr), N_true=len(p))
    if Xd.shape[0] < 2:
        return r
    d = cr.IncidenceData.from_matrix(Xd)
    est, lo, hi = {}, {}, {}
    c2 = cr.chao2_ci(d)
    est["chao2"], lo["chao2"], hi["chao2"] = c2[0], c2[2], c2[3]
    est["ichao2"] = cr.ichao2(d)
    for k, Z in Zs.items():
        if Z is None:
            est[f"huggins_{k}"] = est[f"gchao_{k}"] = np.nan
            r[f"huggins_{k}_status"] = r[f"gchao_{k}_status"] = "unavailable"
            continue
        if np.ptp(Z, axis=0).min() == 0:
            Z = Z[:, np.ptp(Z, axis=0) > 0]
        try:
            N, se, l_, h_, ok = cr.huggins_ci(d, Z) if Z.shape[1] else (np.nan,) * 4 + (False,)
        except (np.linalg.LinAlgError, FloatingPointError, ValueError):
            N, l_, h_, ok = np.nan, np.nan, np.nan, False
        est[f"huggins_{k}"], lo[f"huggins_{k}"], hi[f"huggins_{k}"] = N, l_, h_
        r[f"huggins_{k}_status"] = "ok" if ok else "not converged"
        if ok:  # E07 §3 contingency: Horvitz-Thompson weights truncated at 1/pi <= 100
            _, beta, _ = cr.huggins(d, Z)
            pr = 1 / (1 + np.exp(-(np.column_stack([np.ones(len(Z)), Z]) @ beta)))
            w = 1 / (1 - (1 - pr) ** d.K)
            r[f"huggins_{k}_max_weight"] = float(w.max())
            r[f"huggins_{k}_trunc100"] = float(np.minimum(w, 100).sum())
        try:
            G, _, okg = cr.generalized_chao(d, Z)
        except (np.linalg.LinAlgError, ValueError):
            G, okg = np.nan, False
        est[f"gchao_{k}"] = G if okg else np.nan
        r[f"gchao_{k}_status"] = "ok" if okg else "not converged"
    for k, v in est.items():
        r[f"{k}"] = float(v)
        r[f"{k}_relbias_U"] = float(v / U - 1) if U else np.nan
        r[f"{k}_relbias_Nthr"] = float(v / N_thr - 1) if N_thr else np.nan
        if k in lo:
            r[f"{k}_ci"] = [float(lo[k]), float(hi[k])]
            r[f"{k}_ci_covers_U"] = bool(lo[k] <= U <= hi[k]) if np.isfinite(lo[k]) else None
    return r


def collect(a):
    """[(name, p, X_est, seeds, cov, U-mask)] over the E02 and E06 cells."""
    out = []
    if a.e02:
        cells = sorted(Path(a.e02).glob("*"))
        loaded = {c.name: load(c) for c in cells if (c / "runs.csv").exists()}
        archs = {n.split("_l0-")[0] for n in loaded}
        for arch in sorted(archs):
            Uarch = np.any([v[3].any(axis=1) for n, v in loaded.items() if n.split("_l0-")[0] == arch], axis=0)
            out += [(f"E02:{n}", v[1], v[2], v[4], v[5], Uarch) for n, v in loaded.items()
                    if n.split("_l0-")[0] == arch]
    if a.e06:
        for c in sorted(Path(a.e06).glob("*/histories/oracle_tgt0.7/*")):
            v = load(c)
            out.append((f"E06:{c.parent.parent.parent.name}", v[1], v[2], v[4], v[5], v[3].any(axis=1)))
    return out


def share(rows, ok):
    vals = [ok(r) for r in rows]
    k, n = sum(bool(v) for v in vals), len(vals)
    return k, n, (k / n if n else np.nan), wilson(k, n)


def hypotheses(rows):
    H = []
    k, n, s, ci = share(rows, lambda r: abs(r.get("huggins_x1_relbias_U", np.nan)) <= 0.10)
    k2, _, s2, _ = share(rows, lambda r: not abs(r.get("huggins_x1_relbias_U", np.nan)) <= 0.20)
    H.append(dict(id="H7a", estimate=f"Huggins-x1 within 10% of |U| in {k}/{n} cells ({s:.2f}, Wilson {ci[0]:.2f}–{ci[1]:.2f}); "
                  f"beyond 20% (or failed) in {k2}/{n}",
                  verdict="supported" if s >= 0.8 else ("not supported" if s2 > 0.5 else "inconclusive")))
    for x in ("x3", "x4"):
        k, n, s, ci = share(rows, lambda r: abs(r.get(f"huggins_{x}_relbias_U", np.nan))
                            < abs(r.get("chao2_relbias_U", np.nan)))
        H.append(dict(id=f"H7b ({x})", estimate=f"Huggins-{x} closer to |U| than Chao2 in {k}/{n} cells "
                      f"({s:.2f}, Wilson {ci[0]:.2f}–{ci[1]:.2f})",
                      verdict="supported" if s >= 0.7 else ("not supported" if s < 0.5 else "inconclusive")))
    b = np.array([r.get("huggins_x2_s1.0_relbias_U", np.nan) for r in rows], float)
    fin = b[np.isfinite(b)]
    H.append(dict(id="H7c", estimate=f"Huggins-x2 (s = 1) rel. bias vs |U|: median {np.median(fin) if fin.size else np.nan:+.3f}, "
                  f"positive in {(fin > 0).sum()}/{fin.size} cells ({b.size - fin.size} failed)", verdict="reported"))
    return H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--e02", help="<e02>/histories/oracle_tgt0.7")
    ap.add_argument("--e06", help="E06 root (<root>/<cell>/histories/oracle_tgt0.7/<cell>_l0-*)")
    ap.add_argument("--p-threshold", default="auto")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (name, p, X, seeds, cov, Umask) in enumerate(collect(a)):
        thr = float(p[Umask].min()) if a.p_threshold == "auto" and Umask.any() else float(a.p_threshold)
        rng = {s: np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(i, j)))
               for j, s in enumerate(NOISE)}
        r = analyse_cell(name, p, X, seeds, cov, Umask.sum(), (p >= thr).sum(), rng)
        r.update(cell_index=i, p_threshold=thr)
        rows.append(r)
        print(name, "done", flush=True)
    H = hypotheses(rows)
    models = sorted({k[:-len("_status")] for r in rows for k in r if k.endswith("_status")})
    fails = {m: sum(r.get(f"{m}_status") != "ok" for r in rows) for m in models}
    (out / "cells.json").write_text(json.dumps(rows, indent=1, default=float) + "\n")
    (out / "hypotheses.json").write_text(json.dumps(dict(hypotheses=H, failures=fails), indent=2) + "\n")
    cols = ["chao2", "ichao2", "huggins_x1", "huggins_x2_s1.0", "huggins_x3", "huggins_x4", "gchao_x1", "gchao_x4"]
    L = ["# E07 covariate models", "", f"{len(rows)} cells. Relative bias against |U| (median over cells; "
         "share of cells within 10%; CI coverage of |U| where an interval exists).", "",
         "| estimator | median rel. bias | within 10% | CI covers \\|U\\| | failed |", "|---|---|---|---|---|"]
    for c in cols:
        b = np.array([r.get(f"{c}_relbias_U", np.nan) for r in rows], float)
        cov = [r.get(f"{c}_ci_covers_U") for r in rows if r.get(f"{c}_ci_covers_U") is not None]
        L.append(f"| {c} | {np.nanmedian(b) if np.isfinite(b).any() else np.nan:+.3f} | "
                 f"{np.mean(np.abs(b) <= 0.1):.2f} | {np.mean(cov) if cov else float('nan'):.2f} | "
                 f"{fails.get(c, int(np.isnan(b).sum()))} |")
    L += ["", "| ID | estimate | verdict |", "|---|---|---|"] + \
        [f"| {h['id']} | {h['estimate'].replace('|', chr(92) + '|')} | **{h['verdict']}** |" for h in H]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
