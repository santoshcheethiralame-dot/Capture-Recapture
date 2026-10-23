"""E15-R004: calibration analysis for the SAE arm (CPU).

    python analysis/e15/analyse.py --dir <inject.py out> --out results/E15/E15-R004 \
        [--latent-stats stats.json] [--truth pooled|reference] [--B 1000]

Seeds 0-7 are estimation runs (K = 8) and seeds 8-11 are held-out seeds (the
Δ check). Choices fixed in E15 §2a:
- A mark is caught by a seed under the oracle rule: one-to-one assignment of
  latents to marks with |cos| >= 0.7.
- True detectability pi_j is the catch rate over all 12 seeds (``pooled``)
  or over the 4 held-out seeds (``reference``). True coverage of the
  held-out marks is the pi-share of those found by the 8 estimation seeds.
- Detectability is fitted on the 300 training marks: logistic in
  (log p_j, log m_j), using every training mark.
- Held-out marks are then treated as unknown items. C_cal uses their
  covariates as an analyst would see them, in two variants:
  (a) ``observed``: the matched latents' log firing frequency and log
      contribution magnitude, mapped to the true scale by `proxy_map`
      fitted on the found training marks (needs --latent-stats);
  (b) ``oracle``: their true (log p, log m) (upper bound on calibration).
  C_uncal is Chao-Jost on the held-out marks' history.
- H15a: |C_cal - C| <= 0.05 supported, > 0.10 not supported (primary:
  observed if available, else oracle, labelled).
- H15b: error reduction (|C_uncal - C| - |C_cal - C|) / |C_uncal - C| >= 30%
  supported; <= 0 not supported.
- H15c: per-seed catch rate against firing-frequency band (4 log bands of
  1e-6 to 1e-2), marks vs real items, with Wilson 95% CIs. Real items are
  M1-matched clusters at the plateau threshold; a real item's catch rate is
  its share of seeds and its frequency the mean over those seeds.
  Supported if the CIs overlap in >= 3 of 4 bands (needs --latent-stats).
- Δ: C_cal-based Δ_cal(4) for held-out marks vs the held-out marks first
  found by seeds 8-11.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "analysis" / "e02"))

import crsafety as cr  # noqa: E402
from crsafety import calibrate as cb  # noqa: E402
from crsafety import matching as mt  # noqa: E402

BANDS = np.log(np.array([1e-6, 1e-5, 1e-4, 1e-3, 1e-2]))
TAUS = np.round(np.arange(0.30, 0.951, 0.01), 2)


def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (float(c - h), float(c + h))


def load(d):
    import zoo
    z = np.load(Path(d) / "marks.npz")
    marks = {k: z[k] for k in z.files}
    saes = {}
    for f in sorted(Path(d).glob("zoo/*/l0-*/seed-*/sae_weights.safetensors")):
        t = zoo.load_tensors(f)
        saes[int(f.parent.name.split("-")[1])] = t[next(x for x in t if x.endswith("W_dec"))].astype(np.float64)
    return marks, saes


def latent_obs(stats, k, lat, W):
    """(log firing frequency, log contribution magnitude) of latent ``lat`` in seed k."""
    s = stats[f"seed-{k}"]
    c, a = np.asarray(s["counts"], float)[lat], np.asarray(s["act_sums"], float)[lat]
    n = float(s["tokens"])
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.log(c / n), np.log(a / c * np.linalg.norm(W[lat], axis=-1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--latent-stats")
    ap.add_argument("--truth", choices=["pooled", "reference"], default="pooled")
    ap.add_argument("--B", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261037)
    ap.add_argument("--tau-gt", type=float, default=0.7)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    marks, saes = load(a.dir)
    stats = json.loads(Path(a.latent_stats).read_text()) if a.latent_stats else None
    seeds = sorted(saes)
    est, ref = [s for s in seeds if s < 8], [s for s in seeds if s >= 8]
    U, p, mag, held = marks["U"].astype(np.float64), marks["p"], marks["magnitude"], marks["held_out"].astype(bool)
    Mn = len(p)
    X = np.zeros((Mn, len(seeds)), np.int8)
    lat = np.full((Mn, len(seeds)), -1)
    for c, s in enumerate(seeds):
        caught, feat = mt.oracle_catch(saes[s], U, a.tau_gt)
        X[caught, c] = 1
        for l, j in enumerate(feat):
            if j >= 0:
                lat[j, c] = l
    ie = [seeds.index(s) for s in est]
    ir = [seeds.index(s) for s in ref]
    Ke = len(ie)
    Xe = X[:, ie]
    pi = X.mean(axis=1) if a.truth == "pooled" else X[:, ir].mean(axis=1)
    Zt = np.column_stack([np.log(p), np.log(mag)])
    tr = ~held
    beta, ok = cb.fit_detectability(Zt[tr], Xe[tr].sum(axis=1), Ke)
    hfound = held & Xe.any(axis=1)
    tot = pi[held].sum()
    C = float(pi[hfound].sum() / tot) if tot > 0 else np.nan
    Xh = Xe[hfound]
    C_unc = float(cr.coverage(Xh)) if Xh.shape[0] >= 2 else np.nan
    res = dict(K_est=Ke, K_ref=len(ir), marks=int(Mn), held_out=int(held.sum()), truth=a.truth, fit_converged=ok,
               beta=beta.tolist(), held_found=int(hfound.sum()), C_true=C, C_uncal=C_unc)
    variants = {"oracle": Zt[hfound]}
    if stats is not None:
        def obs_of(js):
            rows = []
            for j in js:
                v = [latent_obs(stats, seeds[c], lat[j, c], saes[seeds[c]]) for c in ie if Xe[j, ie.index(c)]]
                rows.append(np.nanmean(np.array(v), axis=0))
            return np.array(rows)
        ftr = np.nonzero(tr & Xe.any(axis=1))[0]
        f = cb.proxy_map(obs_of(ftr), Zt[ftr])
        variants["observed"] = f(obs_of(np.nonzero(hfound)[0]))
        res["proxy_fit_marks"] = int(ftr.size)
    ss = np.random.SeedSequence(a.seed)
    for name, Z in variants.items():
        c = cb.calibrated(cb.predict(beta, Z), Ke, m=len(ir))
        ci = cb.calibrated_interval(Zt[tr], Xe[tr].sum(axis=1), Ke, Z, B=a.B, seed=ss.spawn(1)[0])
        res[f"C_cal_{name}"] = c["C_cal"]
        res[f"C_cal_{name}_ci"] = ci["interval"]
        res[f"Delta_cal_{name}"] = c["Delta_cal"]
    res["Delta_true_heldout_marks"] = int((held & X[:, ir].any(axis=1) & ~Xe.any(axis=1)).sum())
    prim = "observed" if "observed" in variants else "oracle"
    e_cal, e_unc = abs(res[f"C_cal_{prim}"] - C), abs(C_unc - C)
    red = (e_unc - e_cal) / e_unc if e_unc > 0 else np.nan
    H = [dict(id="H15a", estimate=f"|C_cal - C| = {e_cal:.3f} ({prim} covariates)",
              verdict="supported" if e_cal <= 0.05 else ("not supported" if e_cal > 0.10 else "inconclusive")),
         dict(id="H15b", estimate=f"error reduction {red:+.0%} (|C_uncal - C| = {e_unc:.3f})",
              verdict="supported" if red >= 0.30 else ("not supported" if red <= 0 else "inconclusive"))]
    if prim == "oracle":
        H[0]["note"] = H[1]["note"] = "no --latent-stats: oracle covariates only (not the confirmatory variant)"
    if stats is not None:
        # H15c: per-seed catch rate by frequency band, marks (true p) vs real items (observed frequency)
        bands = []
        mb = np.digitize(np.log(p), BANDS[1:-1])
        dirs = [saes[s][~np.isin(np.arange(saes[s].shape[0]), lat[:, c][lat[:, c] >= 0])] for c, s in enumerate(seeds)]
        sw = mt.sweep(dirs, TAUS)
        tau = mt.plateau(TAUS, [sw[float(x)][0].shape[0] for x in TAUS])
        if tau is None:
            res["H15c_status"] = "no plateau for real-item matching"
        else:
            Xr, labels = mt.cluster_seeds(dirs, tau)
            freq = np.full(Xr.shape[0], np.nan)
            acc = [[] for _ in range(Xr.shape[0])]
            for c, s in enumerate(seeds):
                keep = np.nonzero(~np.isin(np.arange(saes[s].shape[0]), lat[:, c][lat[:, c] >= 0]))[0]
                lf, _ = latent_obs(stats, s, keep, saes[s])
                for item, v in zip(labels[c], lf):
                    acc[item].append(v)
            freq = np.array([np.nanmean(v) if v else np.nan for v in acc])
            rb = np.digitize(freq, BANDS[1:-1])
            K = len(seeds)
            overl = 0
            for b in range(4):
                km, nm = int(X[mb == b].sum()), int((mb == b).sum() * K)
                inb = (rb == b) & np.isfinite(freq)
                kr, nr = int(Xr[inb].sum()), int(inb.sum() * K)
                cm, crr = wilson(km, nm), wilson(kr, nr)
                o = bool(nm and nr and cm[0] <= crr[1] and crr[0] <= cm[1])
                overl += o
                bands.append(dict(band=b, marks=dict(rate=km / nm if nm else np.nan, ci=cm),
                                  real=dict(rate=kr / nr if nr else np.nan, ci=crr, items=int(inb.sum())), overlap=o))
            res["H15c_bands"] = bands
            res["real_items"] = dict(tau=tau, n=int(Xr.shape[0]))
            H.append(dict(id="H15c", estimate=f"CIs overlap in {overl}/4 bands (real items: plateau tau {tau:.2f})",
                          verdict="supported" if overl >= 3 else "not supported",
                          note="real items' catch rate is among matched clusters, which exist only once found"))
    res["hypotheses"] = H
    (out / "summary.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    print(json.dumps(res, indent=2, default=float))


if __name__ == "__main__":
    main()
