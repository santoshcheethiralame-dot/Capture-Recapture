"""Fig. 1 (concept): repeated runs, their overlap, and coverage.

    python paper/figures/fig1_concept.py      # writes fig1_concept.{pdf,png} next to this file

Illustrative only (a fixed toy history, not data). Two audits of different
completeness: in A most failure modes are found by several runs (few
singletons, high coverage); in B most are found once (many singletons, low
coverage). The numbers are computed with crsafety.coverage from the toy
histories.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "src"))
from crsafety import coverage  # noqa: E402

S1, S2, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 8, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "pdf.fonttype": 42, "axes.edgecolor": INK2, "text.color": INK})

A = np.array([[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [1, 0, 1, 1], [0, 1, 1, 1], [1, 1, 0, 0],
              [0, 1, 1, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]])
B = np.array([[1, 1, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0],
              [0, 1, 0, 0], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 1, 0]])


def panel(ax, X, title):
    n, K = X.shape
    y = X.sum(axis=1)
    for i in range(n):
        for k in range(K):
            if X[i, k]:
                ax.add_patch(plt.Circle((k, n - 1 - i), 0.28, color=S2 if y[i] == 1 else S1, lw=0))
            else:
                ax.add_patch(plt.Circle((k, n - 1 - i), 0.08, color=GRID, lw=0))
        ax.text(K - 0.2, n - 1 - i, f"{y[i]}", va="center", ha="left", color=INK2, fontsize=7)
    ax.set_xlim(-0.6, K + 0.4)
    ax.set_ylim(-0.9, n - 0.3)
    ax.set_aspect("equal")
    ax.set_xticks(range(K), [str(k + 1) for k in range(K)], fontsize=7, color=INK2)
    ax.set_xlabel("run", fontsize=7, color=INK2, labelpad=2)
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    q1 = int((y == 1).sum())
    ax.set_title(f"{title}\n{n} failure modes found, {q1} by one run only\ncoverage Ĉ = {coverage(X):.2f}",
                 loc="left", fontsize=8, color=INK)


fig, (a, b) = plt.subplots(1, 2, figsize=(5.2, 3.6))
panel(a, A, "A: runs mostly agree")
panel(b, B, "B: runs mostly disagree")
fig.text(0.02, 0.01, "rows: failure modes found; dots: found by that run; right: number of runs that found it.\n"
         "Orange: found by one run only. Few such singletons means later runs are unlikely to find anything new.",
         fontsize=6.5, color=INK2)
fig.subplots_adjust(bottom=0.16, wspace=0.25)
for ext in ("pdf", "png"):
    fig.savefig(HERE / f"fig1_concept.{ext}", dpi=200, bbox_inches="tight")
print("written", HERE)
