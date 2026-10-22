"""E00-R001 step 1: write synthetic detection matrices, including edge cases.

Each file is an items × runs binary matrix with header r1..rK. Bundled R
datasets are exported by reference.R into the same directory. Covariate
datasets for the Huggins check go to <out>/huggins/ (columns y1..yK, z1..).

    python validation/e00/make_synthetic.py results/E00/E00-R001/data
"""

import sys
from pathlib import Path

import numpy as np


def beta_world(seed, n, K, a, b):
    rng = np.random.default_rng(seed)
    p = rng.beta(a, b, n)
    X = (rng.random((n, K)) < p[:, None]).astype(int)
    return X[X.sum(axis=1) > 0]


def zipf_world(seed, n, K, s=1.1, scale=0.6):
    """Safety-like: a few easy findings, a long tail of rare ones."""
    rng = np.random.default_rng(seed)
    p = np.minimum(scale / np.arange(1, n + 1) ** s, 0.95)
    X = (rng.random((n, K)) < p[:, None]).astype(int)
    return X[X.sum(axis=1) > 0]


def from_counts(y, K):
    """A matrix with the given per-item counts (runs filled left to right, cyclically)."""
    X = np.zeros((len(y), K), dtype=int)
    for i, c in enumerate(y):
        X[i, [(i + j) % K for j in range(c)]] = 1
    return X


def datasets():
    yield "syn_beta_K5", beta_world(1, 400, 5, 0.3, 3)
    yield "syn_beta_K10", beta_world(2, 400, 10, 0.3, 3)
    yield "syn_beta_K20", beta_world(3, 400, 20, 0.2, 4)
    yield "syn_beta_K8_easy", beta_world(4, 150, 8, 2, 2)
    yield "syn_zipf_K6", zipf_world(5, 500, 6)
    yield "syn_zipf_K12", zipf_world(6, 500, 12)
    yield "syn_K3", beta_world(7, 200, 3, 0.5, 2)
    yield "syn_K2", beta_world(8, 200, 2, 0.5, 2)
    yield "edge_Q2_zero", from_counts([1, 1, 1, 1, 3, 4, 5, 6], 6)
    yield "edge_Q1_one", from_counts([1, 2, 2, 3, 4, 5], 6)
    yield "edge_Q1_zero", from_counts([2, 2, 3, 4, 5, 6], 6)
    yield "edge_Q4_zero", from_counts([1] * 6 + [2] * 4 + [3] * 3 + [5] * 2, 8)
    yield "edge_small", from_counts([1, 1, 2, 3], 5)


def huggins_worlds():
    """Covariate datasets for the Huggins check: (name, X, Z)."""
    specs = [("hug_one_cov", 9, 1500, 5, [-2.0, 1.0]), ("hug_two_cov", 10, 2500, 6, [-2.5, 0.8, -0.5]),
             ("hug_noise_cov", 11, 1000, 4, [-1.5, 0.0])]
    for name, seed, N, K, beta in specs:
        rng = np.random.default_rng(seed)
        Z = rng.normal(size=(N, len(beta) - 1))
        p = 1 / (1 + np.exp(-(beta[0] + Z @ np.array(beta[1:]))))
        X = (rng.random((N, K)) < p[:, None]).astype(int)
        keep = X.sum(axis=1) > 0
        yield name, X[keep], Z[keep]


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, X in datasets():
        header = ",".join(f"r{j + 1}" for j in range(X.shape[1]))
        np.savetxt(out / f"{name}.csv", X, fmt="%d", delimiter=",", header=header, comments="")
        print(f"{name}: {X.shape[0]} items x {X.shape[1]} runs")
    (out / "huggins").mkdir(exist_ok=True)
    for name, X, Z in huggins_worlds():
        header = [f"y{j + 1}" for j in range(X.shape[1])] + [f"z{j + 1}" for j in range(Z.shape[1])]
        np.savetxt(out / "huggins" / f"{name}.csv", np.column_stack([X, Z]), fmt="%.17g",
                   delimiter=",", header=",".join(header), comments="")
        print(f"{name}: {X.shape[0]} detected items x {X.shape[1]} runs, {Z.shape[1]} covariates")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/E00/E00-R001/data")
