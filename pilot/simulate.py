"""Pilot simulation: how do standard estimators behave under the assumption
violations we expect from SAE runs, red teams and auditors?

Each scenario draws a population of N individuals (features, attacks,
behaviours), gives each a per-occasion capture probability, simulates K
occasions (runs), and reports the median relative error N_hat / N - 1 over
replicates. Run: python pilot/simulate.py > pilot/results.md
"""

import numpy as np

from estimators import ESTIMATORS, coverage, extrapolate, population_chao2_bound

N, REPS = 2000, 200
rng = np.random.default_rng(0)


def logit_normal(mu, sigma, size):
    return 1 / (1 + np.exp(-(mu + sigma * rng.standard_normal(size))))


def capture(P):
    """P has shape (N, K): independent Bernoulli captures."""
    return (rng.random(P.shape) < P).astype(np.int8)


def heterogeneity_p(sigma, mu=-1.5):
    return logit_normal(mu, sigma, N)


def zipf_p(alpha, p_max=0.9):
    # Catchability falls off with rank, like feature frequency in a real model.
    return p_max * np.arange(1, N + 1) ** (-alpha)


def repeat(p, K):
    return capture(np.repeat(p[:, None], K, axis=1))


def families(n_families, K, tau=1.5, mu=-1.5, sigma=0.5):
    # Occasions from the same "family" (same base model, same prompt style)
    # share an individual-level effect, so they tend to find the same things.
    # With one family this is just extra heterogeneity; with several it is
    # heterogeneity that differs between groups of occasions.
    z = sigma * rng.standard_normal(N)
    u = tau * rng.standard_normal((N, n_families))
    fam = np.arange(K) % n_families
    P = 1 / (1 + np.exp(-(mu + z[:, None] + u[:, fam])))
    return capture(P)


def misid(ghost_rate, merge_rate, K, sigma=1.0):
    X = repeat(heterogeneity_p(sigma), K)
    # False non-matches: a capture is recorded as a brand-new individual.
    ghosts = (rng.random(X.shape) < ghost_rate) & (X == 1)
    X[ghosts] = 0
    G = np.zeros((ghosts.sum(), K), dtype=np.int8)
    G[np.arange(len(G)), np.nonzero(ghosts)[1]] = 1
    X = np.vstack([X, G])
    # False matches: pairs of individuals are merged into one record.
    n_merge = int(merge_rate * N)
    idx = rng.permutation(N)[: 2 * n_merge].reshape(-1, 2)
    X[idx[:, 0]] |= X[idx[:, 1]]
    X = np.delete(X, idx[:, 1], axis=0)
    return X


def run(name, make, bound=None):
    errs = {k: [] for k in ESTIMATORS}
    seen = []
    for _ in range(REPS):
        X = make()
        X = X[X.sum(axis=1) > 0]
        seen.append(len(X) / N)
        for k, f in ESTIMATORS.items():
            errs[k].append(f(X) / N - 1)
    cells = []
    for k in ESTIMATORS:
        e = np.array(errs[k], dtype=float)
        cells.append("n/a" if np.all(np.isnan(e)) else f"{np.nanmedian(e):+.0%}")
    b = "" if bound is None else f"{bound / N - 1:+.0%}"
    print(f"| {name} | {np.median(seen):.0%} | {b} | " + " | ".join(cells) + " |")


def header(title):
    print(f"\n### {title}\n")
    print("| Scenario | Seen (S/N) | Chao2 bound | " + " | ".join(ESTIMATORS) + " |")
    print("|---" * (len(ESTIMATORS) + 3) + "|")


def coverage_rows(name, p, K, reps=100):
    est, true, new_true, new_pred, frac = [], [], [], [], []
    for _ in range(reps):
        X = repeat(p, 2 * K)
        first, seen = X[:, :K], X[:, :K].sum(axis=1) > 0
        frac.append(seen.mean())
        est.append(coverage(first))
        true.append(p[seen].sum() / p.sum())
        new_true.append((X.sum(axis=1) > 0).sum() - seen.sum())
        new_pred.append(extrapolate(first, K))
    print(
        f"| {name}, K={K} | {np.mean(frac):.0%} | {np.mean(est):.3f} | {np.mean(true):.3f} "
        f"| {np.mean(new_true):.0f} | {np.mean(new_pred):.0f} |"
    )


if __name__ == "__main__":
    print(f"N = {N}, {REPS} replicates. Cells show median N_hat/N - 1.")
    print("'Chao2 bound' is Chao2 computed from expected frequency counts with no")
    print("sampling noise: the most Chao2 can deliver. Blank where it does not apply.")

    header("1. Heterogeneous catchability (logit-normal, mean p about 0.2)")
    for sigma in (0.0, 1.0, 2.0):
        p_ref = heterogeneity_p(sigma)
        for K in (2, 5, 10):
            run(
                f"sigma={sigma}, K={K}",
                lambda: repeat(heterogeneity_p(sigma), K),
                population_chao2_bound(p_ref, K) if K > 2 else None,
            )

    header("2. Heavy tail (Zipf-like catchability, p_i = 0.9 i^-alpha)")
    for alpha in (0.5, 1.0):
        p = zipf_p(alpha)
        for K in (5, 10, 20):
            run(f"alpha={alpha}, K={K}", lambda: repeat(p, K), population_chao2_bound(p, K))

    header("3. Catcher families (K=6, family-shared individual effects, tau=1.5)")
    for nf in (1, 2, 3, 6):
        run(f"{nf} famil{'y' if nf == 1 else 'ies'}", lambda: families(nf, 6))

    header("4. Identity errors (K=6, sigma=1)")
    for g, m in ((0, 0), (0.05, 0), (0.15, 0), (0, 0.05), (0, 0.15)):
        run(f"ghosts={g:.0%}, merges={m:.0%}", lambda: misid(g, m, 6))

    print("\n### 5. Coverage and short-range extrapolation (100 replicates)\n")
    print("Coverage = share of total detection mass held by individuals already seen.")
    print("'New items' = individuals first seen when K more runs are added.\n")
    print("| Scenario | Seen (S/N) | Coverage (est.) | Coverage (true) | New items (true) | New items (pred.) |")
    print("|---|---|---|---|---|---|")
    for name, p in (
        ("logit-normal sigma=2", heterogeneity_p(2.0)),
        ("Zipf alpha=0.5", zipf_p(0.5)),
        ("Zipf alpha=1", zipf_p(1.0)),
    ):
        for K in (5, 10):
            coverage_rows(name, p, K)
