"""Simulated detection histories under the assumption violations of AI-safety tools.

Used by E01 (and by E05 and E13, which reuse E01 histories). A cell is a
:class:`Cell` configuration; :func:`simulate` draws one replicate and
returns the true detection matrix for K runs, the matrix for K *more* runs
of the same process, each item's detectability, and the matrix the analyst
sees after identity errors.

Estimand convention (E01 §2a): pi_i is the probability that one new,
independent run of the catcher class finds item i, unaffected by earlier
runs. True coverage is C = sum_{i found} pi_i / sum_{i in U} pi_i, with U the
items with pi_i > 0.
"""

from dataclasses import asdict, dataclass

import numpy as np
from scipy.optimize import brentq
from scipy.special import expit
from scipy.stats import norm

MEAN_P = 0.2
_GH_X, _GH_W = np.polynomial.hermite_e.hermegauss(80)  # probabilists' Gauss-Hermite
_GH_W = _GH_W / _GH_W.sum()


@dataclass(frozen=True)
class Cell:
    """One simulation configuration (defaults are the E01 base cell)."""

    N: int = 500
    K: int = 10
    het: str = "logitnormal"   # homog | logitnormal | zipf | mixture
    sigma: float = 1.0         # logit-normal s.d. (logitnormal, mixture)
    alpha: float = 1.0         # Zipf exponent
    families: int = 0          # > 0: runs share family-level item effects
    tau: float = 1.5           # s.d. of the family effect
    dep_or: float = 0.0        # > 0: odds ratio between run blocks A and B
    c: float = 1.0             # behavioural response after first detection
    nested_k: float = 0.0      # > 0: threshold (nested) runs with this slope
    ghost: float = 0.0         # false non-match rate per detection
    merge: float = 0.0         # false match rate per observed item

    def to_dict(self):
        return asdict(self)


def logit_mean_mu(sigma, mean=MEAN_P):
    """mu such that E[expit(mu + sigma Z)] = mean, Z ~ N(0, 1)."""
    if sigma == 0:
        return float(np.log(mean / (1 - mean)))
    f = lambda mu: np.sum(_GH_W * expit(mu + sigma * _GH_X)) - mean
    return brentq(f, -30, 30, xtol=1e-14)


def nested_cutoffs():
    """Six cut-offs whose limiting run detection rates are 0.35, 0.29, ..., 0.05 (mean 0.2)."""
    return norm.ppf(1 - np.linspace(0.35, 0.05, 6))


def _base_pi(cell, rng):
    N = cell.N
    if cell.het == "homog":
        return np.full(N, MEAN_P)
    if cell.het == "logitnormal":
        return expit(logit_mean_mu(cell.sigma) + cell.sigma * rng.standard_normal(N))
    if cell.het == "zipf":
        return np.maximum(0.9 * np.arange(1, N + 1, dtype=float) ** -cell.alpha, 0.001)
    if cell.het == "mixture":  # 20% uncatchable, the rest logit-normal with mean 0.2
        p = expit(logit_mean_mu(cell.sigma) + cell.sigma * rng.standard_normal(N))
        p[rng.permutation(N)[: int(round(0.2 * N))]] = 0.0
        return p
    raise ValueError(f"unknown heterogeneity {cell.het!r}")


def _bern(P, rng):
    return (rng.random(P.shape) < P).astype(np.int8)


def _independent(p, K, rng):
    return _bern(np.repeat(p[:, None], K, axis=1), rng)


def _families(cell, rng):
    """Run j belongs to family j mod F; runs of a family share item effects u_if."""
    N, K, F = cell.N, cell.K, cell.families
    s = np.sqrt(0.5**2 + cell.tau**2)
    mu = logit_mean_mu(s)
    z = 0.5 * rng.standard_normal(N)
    u = cell.tau * rng.standard_normal((N, F))
    fam = np.arange(2 * K) % F
    P = expit(mu + z[:, None] + u[:, fam])
    X = _bern(P, rng)
    # pi_i: a new run from a new family, i.e. averaged over the family effect
    pi = np.sum(_GH_W * expit(mu + z[:, None] + cell.tau * _GH_X[None, :]), axis=1)
    return X[:, :K], X[:, K:], pi


def _dependent(p, K, odds_ratio, rng):
    """Runs [0, K//2) form block A; runs in block B have their detection odds
    multiplied by ``odds_ratio`` for items found in block A."""
    a = K // 2
    A = _independent(p, a, rng)
    found = A.any(axis=1)
    odds = p / (1 - p) * np.where(found, odds_ratio, 1.0)
    pB = odds / (1 + odds)
    B = _bern(np.repeat(pB[:, None], K - a, axis=1), rng)
    return np.hstack([A, B])


def _adaptive(p, K, c, rng, found=None):
    """After an item's first detection its detection probability is min(c p, 1)."""
    N = p.size
    found = np.zeros(N, bool) if found is None else found.copy()
    X = np.zeros((N, K), np.int8)
    for j in range(K):
        pj = np.where(found, np.minimum(c * p, 1.0), p)
        X[:, j] = rng.random(N) < pj
        found |= X[:, j].astype(bool)
    return X


def _nested(cell, rng):
    N, k = cell.N, cell.nested_k
    u = rng.standard_normal(N)
    cuts = nested_cutoffs()
    P = expit(k * (u[:, None] - cuts[None, :]))
    X1, X2 = _bern(P, rng), _bern(P, rng)
    return X1, X2, P.mean(axis=1)


def identity_errors(X, ghost, merge, rng):
    """Apply false non-matches (ghosts) then false matches (merges) to the
    observed detection matrix (rows with no detection are dropped first).

    A ghost moves one detection off its item onto a new singleton row; a merge
    ORs one observed row into another and deletes it.
    """
    X = X[X.any(axis=1)].copy()
    K = X.shape[1]
    if ghost > 0:
        g = (rng.random(X.shape) < ghost) & (X == 1)
        X[g] = 0
        G = np.zeros((int(g.sum()), K), np.int8)
        G[np.arange(G.shape[0]), np.nonzero(g)[1]] = 1
        X = np.vstack([X[X.any(axis=1)], G])
    if merge > 0:
        n = int(round(merge * X.shape[0]))
        idx = rng.permutation(X.shape[0])[: 2 * n].reshape(-1, 2)
        X[idx[:, 0]] |= X[idx[:, 1]]
        X = np.delete(X, idx[:, 1], axis=0)
    return X


def simulate(cell, rng):
    """One replicate. Returns a dict with:

    X (N x K true detections), X_more (N x K continuation of the same
    process), pi (length N), X_obs (what the analyst sees: detected rows only,
    after identity errors), and the truths C, Delta (new items in the K more
    runs), N (catchable items) and N_all.
    """
    K = cell.K
    if cell.families:
        X, X_more, pi = _families(cell, rng)
    elif cell.nested_k:
        X, X_more, pi = _nested(cell, rng)
    else:
        pi = _base_pi(cell, rng)
        if cell.dep_or:
            X, X_more = _dependent(pi, K, cell.dep_or, rng), _dependent(pi, K, cell.dep_or, rng)
        elif cell.c != 1.0:
            X = _adaptive(pi, K, cell.c, rng)
            X_more = _adaptive(pi, K, cell.c, rng, found=X.any(axis=1))
        else:
            X, X_more = _independent(pi, K, rng), _independent(pi, K, rng)
    found = X.any(axis=1)
    catchable = pi > 0
    X_obs = identity_errors(X, cell.ghost, cell.merge, rng) if (cell.ghost or cell.merge) else X[found]
    return dict(
        X=X, X_more=X_more, pi=pi, X_obs=X_obs,
        C=float(pi[found].sum() / pi[catchable].sum()),
        Delta=int((X_more.any(axis=1) & ~found).sum()),
        N=int(catchable.sum()), N_all=int(pi.size),
    )
