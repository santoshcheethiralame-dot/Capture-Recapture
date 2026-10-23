"""E04-R001: SAE arm of the single-truth test (CPU).

    python analysis/e04/sae_arm.py --out results/E04/E04-R001 --world <SynthSAEBench world> \
        --noise <e02 out>/true_match_cosines.json --tau <E03 rule> [--reps 200] [--record]
    python analysis/e04/sae_arm.py ... --pilot     # declared pilot: spawn keys from 9000

Per E04 §2 (details fixed in §2a): for N_true in {1, 3, 10}, draw N_true true
features from the world and, for each of K = 8 runs, emit per feature
- a split pair with probability 0.2: lambda t + r and (1 - lambda) t - r,
  lambda ~ U(0.3, 0.7), r orthogonal to t with |r| = 0.5 (the two sum to t);
- an absorbed variant with probability 0.1: t + gamma t_j, gamma ~ U(0.3, 1),
  t_j a random world feature outside the N_true set;
- otherwise a plain copy;
then rotate every emitted direction away from its intended direction to
|cos| = sqrt(rho), rho drawn from the E02 cross-seed cosine distribution of
true matches (so two plain copies have cross-seed |cos| ~ rho). The E03
identity rule (`--tau` = a fixed threshold, or `plateau`) clusters the 8 runs.

Measures per replicate: clusters / N_true, Chao2 / N_true, C_hat (truth
C = 1), and Chao2 after the E05 ghost correction (b) with f_hat from <= 200
labelled candidate pairs (each latent's nearest latent in every other run,
stratified over |cos| bins); f_hat = true pairs not clustered together / all
true pairs. The oracle f (true share) is reported alongside.
H4a: mean clusters / N_true <= 1.2 supported, > 1.5 not supported (each
N_true level and pooled). H4c: corrected Chao2 / N_true <= 1.5 in the levels
where the uncorrected ratio is > 2; not supported if no improvement.
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
from crsafety import linkage as lk  # noqa: E402
from crsafety import matching as mt  # noqa: E402

MASTER = 20261026  # 20261022 + 4
K = 8
LEVELS = (1, 3, 10)
P_SPLIT, P_ABSORB = 0.2, 0.1  # E04 §2
SPLIT_R = 0.5  # E04 §2a: |r| of a split; pieces at lambda = 0.5 have |cos| 0.71 to t
TAUS = np.round(np.arange(0.30, 0.991, 0.01), 2)
BINS = (0.0, 0.3, 0.5, 0.6, 0.7, 0.8, 0.9, 1.01)


def unit(v):
    return v / np.linalg.norm(v)


def orth_unit(t, rng):
    u = rng.normal(size=t.size)
    u -= (u @ t) * t
    return unit(u)


def rotate(t, c, rng):
    """A unit vector at cosine c to the unit vector t, in a random direction."""
    return c * t + np.sqrt(max(1 - c * c, 0)) * orth_unit(t, rng)


class Noise:
    def __init__(self, path=None, fixed=None):
        if fixed is not None:
            self.q = None
            self.fixed = float(fixed)
        else:
            d = json.loads(Path(path).read_text())
            self.q, self.v = np.asarray(d["quantiles"]), np.asarray(d["pooled"])

    def draw(self, rng):
        rho = self.fixed if self.q is None else np.interp(rng.random(), self.q, self.v)
        return np.sqrt(np.clip(rho, 0, 1))


def emit(T, feats, rng, noise, p_split=P_SPLIT, p_absorb=P_ABSORB, split_r=SPLIT_R):
    """One run: (directions, true feature per latent, variant per latent)."""
    others = np.setdiff1d(np.arange(T.shape[0]), feats)
    dirs, lab, kind = [], [], []
    for f in feats:
        t = T[f]
        u = rng.random()
        if u < p_split:
            lam, r = rng.uniform(0.3, 0.7), split_r * orth_unit(t, rng)
            parts, k = [lam * t + r, (1 - lam) * t - r], "split"
        elif u < p_split + p_absorb and others.size:
            parts, k = [t + rng.uniform(0.3, 1.0) * T[rng.choice(others)]], "absorbed"
        else:
            parts, k = [t], "plain"
        for v in parts:
            dirs.append(rotate(unit(v), noise.draw(rng), rng))
            lab.append(int(f))
            kind.append(k)
    return np.array(dirs), np.array(lab), kind


def candidate_pairs(dirs, labels, cl):
    """Each latent's nearest latent in every other run: (|cos|, same true feature, same cluster)."""
    U = [mt.unit_rows(d) for d in dirs]
    s, t, linked = [], [], []
    for a in range(len(U)):
        for b in range(len(U)):
            if a == b:
                continue
            S = np.abs(U[a] @ U[b].T)
            j = S.argmax(axis=1)
            s += S[np.arange(S.shape[0]), j].tolist()
            t += (labels[a] == labels[b][j]).tolist()
            linked += (cl[a] == cl[b][j]).tolist()
    return np.array(s), np.array(t), np.array(linked)


def f_hat(s, t, linked, n_v, rng):
    """Share of true pairs left unclustered, from n_v labelled pairs stratified
    over |cos| bins and weighted back by bin size (E05 §2a, by analogy)."""
    b = np.digitize(s, BINS[1:-1])
    per = max(1, n_v // max(np.unique(b).size, 1))
    true_tot, true_unl = 0.0, 0.0
    for k in np.unique(b):
        m = np.nonzero(b == k)[0]
        lab = rng.choice(m, size=min(per, m.size), replace=False)
        true_tot += m.size * t[lab].mean()
        true_unl += m.size * (t[lab] & ~linked[lab]).mean()
    return float(true_unl / true_tot) if true_tot > 0 else 0.0


def cluster(dirs, tau):
    if tau == "plateau":
        sw = mt.sweep(dirs, TAUS)
        counts = [sw[float(x)][0].shape[0] for x in TAUS]
        tp = mt.plateau(TAUS, counts)
        if tp is None:
            return None, None, None
        X, labels = mt.cluster_seeds(dirs, tp)
        return X, labels, tp
    X, labels = mt.cluster_seeds(dirs, float(tau))
    return X, labels, float(tau)


def replicate(T, n_true, rng, noise, tau, n_v, **variants):
    feats = rng.choice(T.shape[0], n_true, replace=False)
    runs = [emit(T, feats, rng, noise, **variants) for _ in range(K)]
    dirs = [r[0] for r in runs]
    X, cl, tau_used = cluster(dirs, tau)
    out = dict(n_true=n_true, n_latents=int(sum(d.shape[0] for d in dirs)),
               n_split=int(sum(k.count("split") for _, _, k in runs)) // 2,
               n_absorbed=int(sum(k.count("absorbed") for _, _, k in runs)), tau=tau_used)
    if X is None:
        out.update(status="no plateau")
        return out
    d = cr.IncidenceData.from_matrix(X)
    labels = [r[1] for r in runs]
    s, t, linked = candidate_pairs(dirs, labels, cl)
    fh = f_hat(s, t, linked, n_v, rng)
    f_or = float((t & ~linked).sum() / max(t.sum(), 1))
    ch = cr.chao2(d)
    # cluster purity: clusters whose latents come from more than one true feature
    lab_all, cl_all = np.concatenate(labels), np.concatenate(cl)
    impure = sum(np.unique(lab_all[cl_all == c]).size > 1 for c in np.unique(cl_all))
    out.update(status="ok", clusters=int(X.shape[0]), ratio=X.shape[0] / n_true, chao2=ch, chao2_ratio=ch / n_true,
               C_hat=cr.coverage(d) if d.S >= 1 else np.nan, f_hat=fh, f_oracle=f_or, impure_clusters=int(impure),
               chao2_corr_ratio=lk.corrected_estimates(d, fh)["chao2"] / n_true,
               chao2_corr_oracle_ratio=lk.corrected_estimates(d, f_or)["chao2"] / n_true,
               Q=np.bincount(d.y, minlength=K + 1)[1:].tolist())
    # freeze option 2 (E04 §2a): the same runs without split latents, scored on plain + absorbed only
    dirs2 = [r[0][[k != "split" for k in r[2]]] for r in runs]
    X2, _, _ = cluster(dirs2, tau_used)
    if X2 is not None:
        d2 = cr.IncidenceData.from_matrix(X2)
        out.update(clusters_nosplit=int(X2.shape[0]), ratio_nosplit=X2.shape[0] / n_true,
                   chao2_ratio_nosplit=cr.chao2(d2) / n_true, C_hat_nosplit=cr.coverage(d2) if d2.S >= 1 else np.nan)
    return out


def load_truth(world):
    p = Path(world)
    if p.suffix == ".npy":
        return mt.unit_rows(np.load(p))
    import zoo
    T, _, _ = zoo.load_world(zoo.local_dir(world))
    return mt.unit_rows(T)


def mcse(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return float(x.std(ddof=1) / np.sqrt(x.size)) if x.size > 1 else np.nan


def summarise(rows):
    lev = {}
    for n in LEVELS:
        R = [r for r in rows if r["n_true"] == n and r["status"] == "ok"]
        if not R:
            continue
        g = lambda k: np.array([r.get(k, np.nan) for r in R], float)  # noqa: E731
        lev[n] = dict(reps=len(R), failed=sum(r["n_true"] == n and r["status"] != "ok" for r in rows),
                      **{f"{k}_mean": float(np.nanmean(g(k))) for k in
                         ("ratio", "chao2_ratio", "chao2_corr_ratio", "chao2_corr_oracle_ratio", "C_hat", "f_hat",
                          "f_oracle", "impure_clusters", "ratio_nosplit", "chao2_ratio_nosplit", "C_hat_nosplit")
                         if any(k in r for r in R)},
                      ratio_mcse=mcse(g("ratio")), chao2_ratio_mcse=mcse(g("chao2_ratio")),
                      chao2_corr_ratio_mcse=mcse(g("chao2_corr_ratio")),
                      chao2_inf=int(np.sum(~np.isfinite(g("chao2_ratio")))))
    H = []
    for n, v in lev.items():
        m = v["ratio_mean"]
        H.append(dict(id=f"H4a (N_true = {n})", estimate=f"mean clusters / N_true = {m:.3f} (MCSE {v['ratio_mcse']:.3f})",
                      verdict="supported" if m <= 1.2 else ("not supported" if m > 1.5 else "inconclusive")))
    for n, v in lev.items():
        if "ratio_nosplit_mean" in v:
            m = v["ratio_nosplit_mean"]
            H.append(dict(id=f"H4a, freeze option 2 (N_true = {n})",
                          estimate=f"mean clusters / N_true without split latents = {m:.3f}",
                          verdict="supported" if m <= 1.2 else ("not supported" if m > 1.5 else "inconclusive")))
    pooled = float(np.mean([r["ratio"] for r in rows if r["status"] == "ok"])) if rows else np.nan
    H.append(dict(id="H4a (pooled)", estimate=f"mean clusters / N_true = {pooled:.3f}",
                  verdict="supported" if pooled <= 1.2 else ("not supported" if pooled > 1.5 else "inconclusive")))
    bad = {n: v for n, v in lev.items() if v["chao2_ratio_mean"] > 2}
    if not bad:
        H.append(dict(id="H4c", estimate="uncorrected Chao2 / N_true <= 2 at every level: condition not met",
                      verdict="not applicable"))
    for n, v in bad.items():
        u, c = v["chao2_ratio_mean"], v["chao2_corr_ratio_mean"]
        H.append(dict(id=f"H4c (N_true = {n})", estimate=f"Chao2 / N_true {u:.2f} uncorrected, {c:.2f} corrected",
                      verdict="supported" if c <= 1.5 else ("not supported" if c >= u else "inconclusive")))
    return lev, H


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--world", required=True, help="SynthSAEBench world (dir or HF repo), or a .npy of directions")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--noise", help="true_match_cosines.json from zoo.py histories (E02)")
    g.add_argument("--noise-fixed", type=float, help="constant cross-seed |cos| (pilots and tests only)")
    ap.add_argument("--tau", required=True, help="E03 identity threshold, or 'plateau'")
    ap.add_argument("--reps", type=int, default=200)
    ap.add_argument("--n-v", type=int, default=200)
    ap.add_argument("--p-split", type=float, default=P_SPLIT)
    ap.add_argument("--p-absorb", type=float, default=P_ABSORB)
    ap.add_argument("--split-r", type=float, default=SPLIT_R)
    ap.add_argument("--pilot", action="store_true", help="spawn keys from 9000 (declared pilot)")
    ap.add_argument("--key-offset", type=int, default=None, help="pilot replicate key offset (default 9000)")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = None
    if a.record:
        from crsafety import manifest
        m = manifest.start(out.name, "E04", " ".join(sys.argv), vars(a), seeds=dict(master=MASTER, pilot=a.pilot),
                           packages=("numpy", "scipy", "crsafety"))
    T = load_truth(a.world)
    noise = Noise(a.noise, a.noise_fixed)
    rows = []
    for li, n in enumerate(LEVELS):
        for j in range(a.reps):
            off = (a.key_offset if a.key_offset is not None else 9000) if a.pilot else 0
            ss = np.random.SeedSequence(MASTER, spawn_key=(li, j + off))
            r = replicate(T, n, np.random.default_rng(ss), noise, a.tau, a.n_v,
                          p_split=a.p_split, p_absorb=a.p_absorb, split_r=a.split_r)
            r.update(level=li, rep=j, seed_spawn_key=[li, j + off])
            rows.append(r)
        print(f"N_true = {n} done", flush=True)
    lev, H = summarise(rows)
    with open(out / "replicates.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, default=float) + "\n")
    (out / "summary.json").write_text(json.dumps(dict(levels=lev, hypotheses=H, pilot=a.pilot), indent=2, default=float) + "\n")
    L = ["# E04 SAE arm" + (" (PILOT)" if a.pilot else ""), "", f"K = {K}, {a.reps} replicates per level, tau = {a.tau}, p_split = {a.p_split}, "
         f"p_absorb = {a.p_absorb}, |r| = {a.split_r}.", "",
         "| N_true | clusters / N_true | without splits | Chao2 / N_true | corrected (f̂) | corrected (oracle f) | Ĉ | f̂ | f oracle | Chao2 inf |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for n, v in lev.items():
        L.append(f"| {n} | {v['ratio_mean']:.3f} ± {v['ratio_mcse']:.3f} | {v.get('ratio_nosplit_mean', float('nan')):.3f} | "
                 f"{v['chao2_ratio_mean']:.2f} | "
                 f"{v['chao2_corr_ratio_mean']:.2f} | {v['chao2_corr_oracle_ratio_mean']:.2f} | {v['C_hat_mean']:.3f} | "
                 f"{v['f_hat_mean']:.3f} | {v['f_oracle_mean']:.3f} | {v['chao2_inf']} |")
    L += ["", "| ID | estimate | verdict |", "|---|---|---|"] + \
        [f"| {h['id']} | {h['estimate']} | **{h['verdict']}** |" for h in H]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if m is not None:
        manifest.finish(m, outputs=[(out / x).resolve().relative_to(ROOT) for x in
                                    ("replicates.jsonl", "summary.json", "summary.md")], status="succeeded")


if __name__ == "__main__":
    main()
