"""Identity rules for SAE features (PROTOCOLS §2; E02, E03, E06, E11).

Decoder (or encoder) directions are rows of a (latents x d) matrix. All
similarities are |cosine|, so antipodal latents count as the same direction.

- :func:`preprocess`: drop dead latents, merge within-SAE duplicates.
- Matchers between two SAEs: M1 :func:`hungarian` on |decoder cos|; M2
  :func:`strict` (encoder and decoder Hungarian assignments must agree);
  M4 :func:`mutual_nn`. (M3, activation correlation, is M1 applied to an
  activation-correlation matrix: pass it to :func:`hungarian_from_sim`.)
- :func:`cluster_seeds`: match every pair of seeds, take connected
  components of the accepted-match graph as items, return the detection
  matrix (items x seeds). ``mode="star"`` matches every seed to a reference.
- :func:`oracle_catch`: one-to-one Hungarian assignment of latents to true
  features; feature i is caught if its assigned latent has |cos| >= tau_gt.
- :func:`plateau`: the truth-free threshold rule of E03.
- :func:`pair_scores`, :func:`ari`, :func:`error_rates`: E03's performance
  measures against true identity.
"""

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components


def unit_rows(W):
    W = np.asarray(W, dtype=np.float64)
    n = np.linalg.norm(W, axis=1, keepdims=True)
    return W / np.where(n == 0, 1, n)


def abs_cos(A, B):
    """|cosine| between every row of A and every row of B."""
    return np.abs(unit_rows(A) @ unit_rows(B).T)


def preprocess(W, fire_counts=None, dup_tau=0.95):
    """Indices of the latents kept: live ones (fire_counts > 0 when given) with
    within-SAE duplicates (|cos| >= dup_tau, antipodal included) merged into
    the first of each duplicate group. Returns (kept indices, group label per
    live latent)."""
    live = np.arange(W.shape[0]) if fire_counts is None else np.nonzero(np.asarray(fire_counts) > 0)[0]
    C = abs_cos(W[live], W[live])
    np.fill_diagonal(C, 0)
    i, j = np.nonzero(np.triu(C >= dup_tau))
    n = live.size
    g = coo_matrix((np.ones(i.size), (i, j)), shape=(n, n))
    _, lab = connected_components(g, directed=False)
    first = {}
    for k, l in enumerate(lab):
        first.setdefault(l, k)
    kept = np.array(sorted(first.values()), dtype=int)
    return live[kept], lab


def hungarian_from_sim(S, tau):
    """Maximum-weight one-to-one assignment on a similarity matrix; keep pairs >= tau."""
    r, c = linear_sum_assignment(-S)
    ok = S[r, c] >= tau
    return np.column_stack([r[ok], c[ok]]), S[r[ok], c[ok]]


def hungarian(A, B, tau):
    """M1: Hungarian on |decoder cosine|."""
    return hungarian_from_sim(abs_cos(A, B), tau)


def mutual_nn(A, B, tau):
    """M4: pairs that are each other's nearest neighbour, with |cos| >= tau."""
    S = abs_cos(A, B)
    ab, ba = S.argmax(axis=1), S.argmax(axis=0)
    i = np.nonzero(ba[ab] == np.arange(S.shape[0]))[0]
    pairs = np.column_stack([i, ab[i]])
    s = S[pairs[:, 0], pairs[:, 1]]
    ok = s >= tau
    return pairs[ok], s[ok]


def strict(A_dec, B_dec, A_enc, B_enc, tau):
    """M2: keep decoder-Hungarian pairs that the encoder-Hungarian assignment
    also makes, both with |cos| >= tau; the score is the smaller of the two."""
    pd, sd = hungarian(A_dec, B_dec, tau)
    pe, se = hungarian(A_enc, B_enc, tau)
    enc = {(int(a), int(b)): s for (a, b), s in zip(pe, se)}
    keep = [(k, min(s, enc[(int(a), int(b))])) for k, ((a, b), s) in enumerate(zip(pd, sd))
            if (int(a), int(b)) in enc]
    if not keep:
        return np.empty((0, 2), int), np.empty(0)
    idx, sc = zip(*keep)
    return pd[list(idx)], np.array(sc)


def _seed_pairs(dirs, mode, reference):
    K = len(dirs)
    if mode == "components":
        return [(a, b) for a in range(K) for b in range(a + 1, K)]
    if mode == "star":
        ref = int(np.argmax([d.shape[0] for d in dirs])) if reference is None else reference
        return [(ref, b) for b in range(K) if b != ref]
    raise ValueError("mode must be 'components' or 'star'")


def pairwise_matches(dirs, matcher=hungarian, mode="components", reference=None, tau=-np.inf):
    """{(a, b): (pairs, scores)} for the seed pairs used by ``mode``. With the
    default tau = -inf every assigned pair is kept, so a threshold sweep can
    reuse one assignment per seed pair (Hungarian and mutual-NN assignments do
    not depend on tau)."""
    return {(a, b): matcher(dirs[a], dirs[b], tau) for a, b in _seed_pairs(dirs, mode, reference)}


def cluster_from_matches(sizes, matches, tau):
    """Connected components of the matches with score >= tau. Returns (X, labels)
    as :func:`cluster_seeds`."""
    K = len(sizes)
    off = np.cumsum([0] + list(sizes))
    rows, cols = [], []
    for (a, b), (m, sc) in matches.items():
        ok = sc >= tau
        rows.append(m[ok, 0] + off[a])
        cols.append(m[ok, 1] + off[b])
    n = off[-1]
    r = np.concatenate(rows).astype(int) if rows else np.empty(0, int)
    c = np.concatenate(cols).astype(int) if cols else np.empty(0, int)
    _, lab = connected_components(coo_matrix((np.ones(r.size), (r, c)), shape=(n, n)), directed=False)
    _, item = np.unique(lab, return_inverse=True)
    X = np.zeros((item.max() + 1 if n else 0, K), np.int8)
    labels = []
    for k in range(K):
        it = item[off[k]:off[k + 1]]
        X[it, k] = 1
        labels.append(it)
    return X, labels


def cluster_seeds(dirs, tau, matcher=hungarian, mode="components", reference=None):
    """Items across K seeds from pairwise matches.

    ``dirs`` is a list of (latents x d) arrays, one per seed (already
    preprocessed). ``mode="components"`` matches every pair of seeds and
    takes connected components; ``mode="star"`` matches each seed to
    ``reference`` (default: the seed with the most latents) only.
    Returns (X, labels): X is the items x seeds detection matrix; labels[k]
    gives the item of each latent of seed k.
    """
    matches = pairwise_matches(dirs, matcher, mode, reference, tau)
    return cluster_from_matches([d.shape[0] for d in dirs], matches, tau)


def sweep(dirs, taus, matcher=hungarian, mode="components", reference=None):
    """Cluster counts and (X, labels) at every tau, from one assignment per seed pair."""
    matches = pairwise_matches(dirs, matcher, mode, reference)
    sizes = [d.shape[0] for d in dirs]
    return {float(t): cluster_from_matches(sizes, matches, t) for t in taus}


def oracle_catch(W, true_dirs, tau_gt=0.7):
    """GT-MCC catch rule: one-to-one Hungarian assignment of latents (rows of W)
    to true features; returns (caught feature mask, feature of each latent or -1)."""
    S = abs_cos(W, true_dirs)
    r, c = linear_sum_assignment(-S)
    ok = S[r, c] >= tau_gt
    caught = np.zeros(true_dirs.shape[0], bool)
    caught[c[ok]] = True
    feat = np.full(W.shape[0], -1)
    feat[r[ok]] = c[ok]
    return caught, feat


def oracle_history(Ws, true_dirs, tau_gt=0.7):
    """True features x seeds detection matrix under :func:`oracle_catch`."""
    return np.column_stack([oracle_catch(W, true_dirs, tau_gt)[0] for W in Ws]).astype(np.int8)


def plateau(taus, counts, min_width=0.10, max_change=0.05):
    """E03 plateau rule: the widest tau-interval of width >= min_width over which
    the cluster count changes by < max_change, i.e. (max - min) / max of the
    counts inside the interval < max_change. Returns its midpoint, or None
    ("no trustworthy threshold"). Ties go to the lowest interval."""
    taus, counts = np.asarray(taus, float), np.asarray(counts, float)
    best = None
    for i in range(taus.size):
        for j in range(i + 1, taus.size):
            c = counts[i:j + 1]
            if (c.max() - c.min()) >= max_change * max(c.max(), 1):
                break
            width = taus[j] - taus[i]
            if width >= min_width - 1e-12 and (best is None or width > best[1] - best[0] + 1e-12):
                best = (taus[i], taus[j])
    return None if best is None else float((best[0] + best[1]) / 2)


def _same_pairs(labels_by_seed):
    """Set of cross-seed latent pairs ((seed, idx), (seed', idx')) that share a label (label >= 0)."""
    groups = {}
    for k, lab in enumerate(labels_by_seed):
        for i, l in enumerate(lab):
            if l >= 0:
                groups.setdefault(int(l), []).append((k, i))
    out = set()
    for members in groups.values():
        for x in range(len(members)):
            for y in range(x + 1, len(members)):
                a, b = members[x], members[y]
                if a[0] != b[0]:
                    out.add((a, b) if a < b else (b, a))
    return out


def pair_scores(pred_labels, true_labels):
    """Cross-seed pair precision, recall and F1 of a clustering against true identity.

    Both arguments are lists (one per seed) of per-latent labels; a true label
    of -1 (latent maps to no true feature) never forms a true pair.
    """
    P, T = _same_pairs(pred_labels), _same_pairs(true_labels)
    tp = len(P & T)
    prec = tp / len(P) if P else 1.0
    rec = tp / len(T) if T else 1.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return dict(precision=prec, recall=rec, f1=f1, true_pairs=len(T), predicted_pairs=len(P))


def error_rates(pred_labels, true_labels):
    """Ghost rate f = share of true cross-seed pairs left unlinked (1 - recall);
    merge rate g = share of predicted pairs that are false (1 - precision)."""
    s = pair_scores(pred_labels, true_labels)
    return dict(ghost=1 - s["recall"], merge=1 - s["precision"])


def ari(a, b):
    """Adjusted Rand index between two labelings of the same objects."""
    a, b = np.asarray(a), np.asarray(b)
    _, ai = np.unique(a, return_inverse=True)
    _, bi = np.unique(b, return_inverse=True)
    M = coo_matrix((np.ones(a.size), (ai, bi))).toarray()
    comb2 = lambda x: x * (x - 1) / 2
    s = comb2(M).sum()
    sa, sb = comb2(M.sum(axis=1)).sum(), comb2(M.sum(axis=0)).sum()
    n2 = comb2(a.size)
    exp = sa * sb / n2 if n2 else 0.0
    mx = (sa + sb) / 2
    return 1.0 if mx == exp else float((s - exp) / (mx - exp))
