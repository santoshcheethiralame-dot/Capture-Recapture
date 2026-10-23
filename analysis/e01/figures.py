"""E01 paper figures, generated from results/E01/analysis/ (run analyse.py first).

    python analysis/e01/figures.py [--out results/E01/analysis/figures]

fig1_coverage_vs_count.{pdf,png}: per pre-registered cell (small-N block
excluded: exploratory), bias of C_hat against realized coverage C (left,
+-2 MCSE, G1 band +-0.03) next to the relative bias of Chao2 against N
(right). Two panels, never two y-scales.
fig2_interval_coverage.{pdf,png}: 95% interval coverage of realized C per
cell, iNEXT normal interval (R005) vs realized-coverage bootstrap (R008,
fresh datasets), with the nominal 0.95.
Sources: performance.csv (R001-R004), realized_bootstrap_R008.csv.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MISSPECIFIED = ("fam1", "beh2", "ghost0.15")  # R008 cells chosen as failure cases (E01 §5)
A = ROOT / "results" / "E01" / "analysis"
# validated categorical slots 1-2 (light surface); ink and chrome
S1, S2, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "pdf.fonttype": 42})


def save(fig, out, name):
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig1(out):
    p = pd.read_csv(A / "performance.csv")
    p = p[p.block != "small N (exploratory)"]
    cov = p[(p.estimator == "coverage") & (p.target == "C")].set_index("cell")
    ch = p[(p.estimator == "chao2") & (p.target == "N")].set_index("cell")
    order = list(cov.index)
    y = range(len(order))[::-1]
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.8, 0.16 * len(order) + 1.0), sharey=True)
    a.axvspan(-0.03, 0.03, color=GRID, lw=0)
    a.axvline(0, color=INK2, lw=0.8)
    a.errorbar(cov.loc[order, "bias"], list(y), xerr=2 * cov.loc[order, "mcse"], fmt="o", ms=3.5,
               color=S1, ecolor=S1, elinewidth=1, capsize=0)
    a.set_xlabel("bias of Ĉ against realized C (±2 MCSE; band ±0.03)")
    a.set_yticks(list(y), order)
    b.axvline(0, color=INK2, lw=0.8)
    b.errorbar(ch.loc[order, "bias"], list(y), xerr=2 * ch.loc[order, "mcse"], fmt="o", ms=3.5,
               color=S1, ecolor=S1, elinewidth=1, capsize=0)
    b.set_xlabel("relative bias of Chao2 against N")
    for ax in (a, b):
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
    a.set_title("Coverage is estimable", loc="left", color=INK, fontsize=9)
    b.set_title("Counts are lower bounds", loc="left", color=INK, fontsize=9)
    save(fig, out, "fig1_coverage_vs_count")


def fig2(out):
    r = pd.read_csv(A / "realized_bootstrap_R008.csv").set_index("cell")
    order = list(r.index)
    y = list(range(len(order)))[::-1]
    fig, ax = plt.subplots(figsize=(5.0, 0.22 * len(order) + 1.0))
    ax.axvline(0.95, color=INK2, lw=0.8, ls=(0, (3, 2)), label="nominal 0.95")
    mis = [i for i, c in enumerate(order) if c in MISSPECIFIED]
    if mis:  # misspecified cells: C_hat is biased (fig. 1), so no interval covers C
        cut = len(order) - min(mis) - 0.5
        ax.axhline(cut, color=INK2, lw=0.6)
        ax.text(0.25, cut - 0.25, "misspecified cells: Ĉ biased (fig. 1), both intervals at 0", color=INK2, va="top", fontsize=7)
    ax.hlines(y, r.loc[order, "inext_normal_cover"], r.loc[order, "cover_realized"], color=GRID, lw=2)
    ax.plot(r.loc[order, "inext_normal_cover"], y, "s", ms=4.5, color=S2, label="iNEXT normal interval",
            mec=SURF, mew=1)
    ax.errorbar(r.loc[order, "cover_realized"], y, xerr=2 * r.loc[order, "cover_realized_mcse"], fmt="o", ms=4.5,
                color=S1, elinewidth=1, capsize=0, label="realized-coverage bootstrap", mec=SURF, mew=1)
    ax.set_yticks(y, order)
    ax.set_xlabel("share of replicates whose 95% interval contains realized C")
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=7, labelcolor=INK,
              handletextpad=0.4, columnspacing=1.0)
    save(fig, out, "fig2_interval_coverage")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(A / "figures"))
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    fig1(out)
    fig2(out)
    print("written to", out)


if __name__ == "__main__":
    main()
