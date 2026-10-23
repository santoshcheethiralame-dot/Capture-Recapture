"""E16-R002: bracket on missed feature mass in the E06 worlds (exploratory; CPU or GPU).

    python analysis/e16/bracket.py --cell-dir <e06 out>/<cell> --out results/E16/E16-R002/<cell>
        [--seeds 0-15] [--samples 200000] [--batch 8192] [--device cpu] [--seed 20261038]

<cell-dir> is what `analysis/e06/train.py` writes (world/ and zoo/). Choices
§2 leaves open (E16 §2a):
- **Truth.** M_miss = E||sum_{i missed} c_i d_i||^2 / E||sum_i c_i d_i||^2: the
  energy of the features no evaluation seed catches (oracle rule, |cos| >=
  0.7, as in E06), in hidden-space units. The per-feature energy share
  sum_{missed} E[c_i^2] / sum_i E[c_i^2] (§2's literal form) is reported too.
- **Lower bounds** (truth-free; denominator E||x - b_dec||^2, averaged over
  seeds). Ĉ is Chao-Jost coverage of the oracle history over the K seeds.
  L0 = 1 - Ĉ (catch-rate units, unconverted). L1 converts with observed
  latent energies: missed energy = (1 - Ĉ)/Ĉ * sum_j pi_j * r1, with
  pi_j = y_j / K and r1 = energy per unit pi among singletons (items caught
  by one seed), item energy = mean over catching seeds of E[f^2] ||w_dec||^2.
- **Upper bounds** (per seed; the tightest, i.e. smallest, over seeds is
  reported, since a feature missed by every seed is missed by each).
  U_res = E||x - x_hat||^2 / denominator. U_lin = energy of the linearly
  predictable part of the error, A x with A fitted by least squares (Engels
  et al. 2025) on the first half of the samples and evaluated on the second.
  U_lit = (residual - its linearly predictable part), §2's literal wording.
- Bracket valid if L <= M_miss <= U, and its width is U - L, for each pair.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "analysis" / "e02"))

import crsafety as cr  # noqa: E402
from crsafety import matching as mt  # noqa: E402


def seed_list(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def load(cell_dir, seeds, device):
    from sae_lens import SAE
    from sae_lens.synthetic import SyntheticModel
    import zoo
    world = SyntheticModel.load_from_source(str(Path(cell_dir) / "world"), device=device)
    idx = zoo.zoo_index(Path(cell_dir) / "zoo")
    saes = {}
    for (a, l, s), f in sorted(idx.items()):
        if s in seeds:
            saes[s] = SAE.load_from_disk(str(f.parent), device=device)
    if not saes:
        raise SystemExit(f"no SAEs for seeds {seeds} under {cell_dir}/zoo")
    return world, saes


@torch.no_grad()
def accumulate(world, saes, samples, batch, device):
    """Two passes over fresh samples: fit A (first half), then measure everything (second half)."""
    d = world.feature_dict.feature_vectors.shape[1]
    D = world.feature_dict.feature_vectors.double()
    bias = world.feature_dict.bias.double()
    fit = {s: (torch.zeros(d + 1, d + 1, dtype=torch.float64, device=device),
               torch.zeros(d + 1, d, dtype=torch.float64, device=device)) for s in saes}
    half = samples // 2

    def batches(n):
        done = 0
        while done < n:
            m = min(batch, n - done)
            yield world.sample_with_features(m)
            done += m

    for x, _ in batches(half):
        X1 = torch.cat([x.double(), torch.ones(x.shape[0], 1, dtype=torch.float64, device=device)], 1)
        for s, sae in saes.items():
            e = (x - sae.decode(sae.encode(x))).double()
            fit[s][0].add_(X1.T @ X1)
            fit[s][1].add_(X1.T @ e)
    A = {s: torch.linalg.lstsq(G, R).solution for s, (G, R) in fit.items()}
    nf = D.shape[0]
    feat_e = torch.zeros(nf, dtype=torch.float64, device=device)
    acc = {s: dict(res=0.0, lin=0.0, lit=0.0, den=0.0,
                   lat=torch.zeros(sae.cfg.d_sae, dtype=torch.float64, device=device)) for s, sae in saes.items()}
    tot_x = 0.0
    feats_all = []
    n = 0
    for x, c in batches(samples - half):
        c = c.to_dense() if c.is_sparse else c
        c = c.double()
        feat_e += (c ** 2).sum(0)
        tot_x += float(((x.double() - bias) ** 2).sum())
        feats_all.append(c)
        X1 = torch.cat([x.double(), torch.ones(x.shape[0], 1, dtype=torch.float64, device=device)], 1)
        for s, sae in saes.items():
            f = sae.encode(x)
            e = (x - sae.decode(f)).double()
            p = X1 @ A[s]
            a = acc[s]
            a["res"] += float((e ** 2).sum())
            a["lin"] += float((p ** 2).sum())
            a["lit"] += float(((e - p) ** 2).sum())
            a["den"] += float(((x.double() - sae.b_dec.double()) ** 2).sum())
            a["lat"] += (f.double() ** 2).sum(0)
        n += x.shape[0]
    return D, bias, feat_e / n, tot_x / n, torch.cat(feats_all), acc, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell-dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seeds", default="0-15")
    ap.add_argument("--samples", type=int, default=200_000)
    ap.add_argument("--batch", type=int, default=8192)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--seed", type=int, default=20261038)  # 20261022 + 16
    ap.add_argument("--tau-gt", type=float, default=0.7)
    a = ap.parse_args()
    torch.manual_seed(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    world, saes = load(a.cell_dir, seed_list(a.seeds), a.device)
    D, bias, feat_e, tot_x, C, acc, n = accumulate(world, saes, a.samples, a.batch, a.device)
    T = D.cpu().numpy()
    seeds = sorted(saes)
    K = len(seeds)
    # oracle history and the latent behind each catch
    X = np.zeros((T.shape[0], K), np.int8)
    lat_of = np.full((T.shape[0], K), -1)
    for k, s in enumerate(seeds):
        W = saes[s].W_dec.detach().double().cpu().numpy()
        caught, feat = mt.oracle_catch(W, T, a.tau_gt)
        X[caught, k] = 1
        for lt, ft in enumerate(feat):
            if ft >= 0:
                lat_of[ft, k] = lt
    missed = ~X.any(axis=1)
    # truth: hidden-space energy of the missed features' sum, and the per-feature energy share
    Cm = C[:, torch.as_tensor(missed, device=C.device)]
    Dm = D[torch.as_tensor(missed, device=D.device)]
    true_miss_hidden = float(((Cm @ Dm) ** 2).sum() / C.shape[0]) / float(((C @ D) ** 2).sum() / C.shape[0])
    fe = feat_e.cpu().numpy()
    true_miss_feat = float(fe[missed].sum() / fe.sum())
    # lower bounds
    det = X.any(axis=1)
    y = X[det].sum(axis=1)
    data = cr.IncidenceData.from_matrix(X[det])
    C_hat = cr.coverage(data) if det.sum() >= 2 else np.nan
    den = np.mean([acc[s]["den"] / n for s in seeds])
    item_e = []
    for i in np.nonzero(det)[0]:
        v = []
        for k, s in enumerate(seeds):
            if X[i, k]:
                lt = lat_of[i, k]
                w2 = float(saes[s].W_dec[lt].double().norm() ** 2)
                v.append(float(acc[s]["lat"][lt]) / n * w2)
        item_e.append(np.mean(v))
    item_e, pi = np.array(item_e), y / K
    single = y == 1
    r1 = item_e[single].sum() / pi[single].sum() if single.any() else np.nan
    L0 = 1 - C_hat
    L1 = (1 - C_hat) / C_hat * pi.sum() * r1 / den if np.isfinite(C_hat) and C_hat > 0 else np.nan
    if np.isfinite(C_hat) and not single.any():
        L1 = 0.0  # no singletons: C_hat = 1, nothing estimated missing
    # upper bounds: tightest seed
    per = {s: dict(U_res=acc[s]["res"] / acc[s]["den"], U_lin=acc[s]["lin"] / acc[s]["den"],
                   U_lit=acc[s]["lit"] / acc[s]["den"]) for s in seeds}
    U = {k: min(v[k] for v in per.values()) for k in ("U_res", "U_lin", "U_lit")}
    res = dict(cell=Path(a.cell_dir).name, K=K, samples_measured=n, n_features=int(T.shape[0]), S_obs=int(det.sum()),
               missed_features=int(missed.sum()), M_miss=true_miss_hidden, M_miss_feature_share=true_miss_feat,
               denominator_ratio=den / tot_x, C_hat=C_hat, Q1=int(single.sum()), r1=r1, L0=L0, L1=L1, **U,
               per_seed=per)
    res["brackets"] = {f"{l}-{u}": dict(valid=bool(res[l] <= true_miss_hidden <= res[u]), width=res[u] - res[l])
                       for l in ("L0", "L1") for u in ("U_res", "U_lin", "U_lit")}
    (out / "bracket.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "per_seed"}, indent=1, default=float))


if __name__ == "__main__":
    main()
