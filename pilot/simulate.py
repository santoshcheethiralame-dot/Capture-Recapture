"""Pilot simulation: how do standard estimators behave under the assumption
violations we expect from SAE runs, red teams and auditors?

Each scenario draws a population of N individuals (features, attacks,
behaviours), gives each a per-occasion capture probability, simulates K
occasions (runs), and reports the median relative error N_hat / N - 1 over
replicates. Run: python pilot/simulate.py > pilot/results.md
"""

import numpy as np

from estimators import ESTIMATORS

N, REPS = 2000, 200
rng = np.random.default_rng(0)


def logit_normal(mu, sigma, size):
    return 1 / (1 + np.exp(-(mu + sigma * rng.standard_normal(size))))


def capture(P):
    """P has shape (N, K): independent Bernoulli captures."""
    return (rng.random(P.shape) < P).astype(np.int8)


def heterogeneity(sigma, K, mu=-1.5):
    p = logit_normal(mu, sigma, N)
    return capture(np.repeat(p[:, None], K, axis=1))


def zipf_tail(alpha, K, p_max=0.9):
    # Catchability falls off with rank, like feature frequency in a real model.
    p = p_max * np.arange(1, N + 1) ** (-alpha)
    return capture(np.repeat(p[:, None], K, axis=1))


def families(n_families, K, tau=1.5, mu=-1.5, sigma=0.5):
    # Occasions from the same "family" (same base model, same prompt style)
    # share an individual-level effect, so they tend to find the same things.
    z = sigma * rng.standard_normal(N)
    u = tau * rng.standard_normal((N, n_families))
    fam = np.arange(K) % n_families
    P = 1 / (1 + np.exp(-(mu + z[:, None] + u[:, fam])))
    return capture(P)


def misid(ghost_rate, merge_rate, K, sigma=1.0):
    X = heterogeneity(sigma, K)
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


def run(name, make):
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
    print(f"| {name} | {np.median(seen):.0%} | " + " | ".join(cells) + " |")


def header(title):
    print(f"\n### {title}\n")
    print("| Scenario | Seen (S/N) | " + " | ".join(ESTIMATORS) + " |")
    print("|---" * (len(ESTIMATORS) + 2) + "|")


if __name__ == "__main__":
    print(f"N = {N}, {REPS} replicates. Cells show median N_hat/N - 1.")

    header("1. Heterogeneous catchability (logit-normal, mean p about 0.2)")
    for sigma in (0.0, 1.0, 2.0):
        for K in (2, 5, 10):
            run(f"sigma={sigma}, K={K}", lambda: heterogeneity(sigma, K))

    header("2. Heavy tail (Zipf-like catchability, p_i = 0.9 i^-alpha)")
    for alpha in (0.5, 1.0):
        for K in (5, 10, 20):
            run(f"alpha={alpha}, K={K}", lambda: zipf_tail(alpha, K))

    header("3. Dependent catchers (K=6, family-shared effects, tau=1.5)")
    for nf in (1, 2, 3, 6):
        run(f"{nf} famil{'y' if nf == 1 else 'ies'}", lambda: families(nf, 6))

    header("4. Identity errors (K=6, sigma=1)")
    for g, m in ((0, 0), (0.05, 0), (0.15, 0), (0, 0.05), (0, 0.15)):
        run(f"ghosts={g:.0%}, merges={m:.0%}", lambda: misid(g, m, 6))
