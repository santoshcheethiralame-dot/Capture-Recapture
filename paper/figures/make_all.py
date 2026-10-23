"""Every paper figure and table, generated from results/ (PAPER-PLAN "Figures").

    python paper/figures/make_all.py                       # real results -> paper/figures/out, paper/tables
    python paper/figures/make_all.py --preview --results <preview>/results --hist <preview> \
        --out <scratchpad>/figs                             # layout preview on simulated inputs

A figure whose inputs do not exist yet is skipped and listed, never faked.
With --preview every figure is stamped "PREVIEW: SIMULATED INPUTS, NOT
RESULTS" and file names end in _PREVIEW. The inputs then come from
`preview_inputs.py`, which runs the real analysis scripts on simulated
histories.

Figures (paper numbering; Fig. 1 is fig1_concept.py):
- fig2_coverage_error: Ĉ − C (95% interval) per cell/configuration and
  testbed, with the ±0.05 band. Sources: E02 cells.csv, E06 cells.json, E08
  levels.json, E09 configs.json, E10 arms.json (non-adaptive arms).
- fig3_counts: E01 Chao2 relative bias against N and N_LB under
  heterogeneity, and CI coverage of N vs N_LB; E02 Chao2 / |U| when present.
- fig4_identity: (a) E02 |Ĉ − C|, oracle vs matched identity, per cell;
  (b, c) E03 cluster count and pair F1 against the threshold for one cell,
  with the plateau interval.
- fig5_ladder: E08 Ĉ − C and n_eff / K by auditor-similarity level.
- fig6_arms: E10 discovery curves (A1 vs A2, from histories) and Ĉ − C by
  arm, including de-adapted A3a/A3b.
- fig7_tools: E09 organisms caught by each combination of tool
  configurations (from histories).
Tables: table1_testbeds (static), table2_stopping (E13).
"""

import argparse
import csv
import gzip
import json
from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402,F401
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# validated categorical slots (dataviz reference palette, light surface) and chrome
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, BAND, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#efeeea", "#fcfcfb"
TEXTW = 5.5  # NeurIPS text width, inches

plt.rcParams.update({
    "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 0, "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF, "pdf.fonttype": 42,
    "ps.fonttype": 42, "lines.linewidth": 1.6, "lines.solid_capstyle": "round", "legend.frameon": False,
    "axes.titlelocation": "left", "axes.titleweight": "bold", "axes.titlecolor": INK,
})

# where each figure reads its inputs, relative to --results (update when the runs exist)
INPUTS = dict(E01="E01/analysis", E02="E02/E02-R004", E03="E03/E03-R001", E06="E06/E06-R014",
              E08="E08/E08-R005", E09="E09/E09-R008", E10="E10/E10-R007", E13="E13/E13-R001")


class Ctx:
    def __init__(self, a):
        self.res = Path(a.results)
        self.hist = Path(a.hist) if a.hist else None
        self.out = Path(a.out)
        self.tables = Path(a.tables)
        self.preview = a.preview
        self.made, self.skipped = [], []

    def path(self, exp, name):
        p = self.res / INPUTS[exp] / name
        return p if p.exists() else None

    def save(self, fig, name):
        if self.preview:
            fig.text(0.5, 0.5, "PREVIEW: SIMULATED INPUTS, NOT RESULTS", rotation=18, ha="center", va="center",
                     fontsize=15, color="#c0bfb9", alpha=0.55, weight="bold", zorder=100)
            name += "_PREVIEW"
        self.out.mkdir(parents=True, exist_ok=True)
        for ext in ("pdf", "png"):
            fig.savefig(self.out / f"{name}.{ext}", dpi=220, bbox_inches="tight")
        plt.close(fig)
        self.made.append(name)


def read_csv(p):
    op = gzip.open if str(p).endswith(".gz") else open
    with op(p, "rt") as f:
        return list(csv.DictReader(f))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


def style_axis(ax, grid="x"):
    ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def band(ax, w=0.05, orient="v"):
    (ax.axvspan if orient == "v" else ax.axhspan)(-w, w, color=BAND, lw=0, zorder=0)
    (ax.axvline if orient == "v" else ax.axhline)(0, color=MUTED, lw=0.7, zorder=1)


def dot(ax, x, y, lo=None, hi=None, color=S1, marker="o", label=None, ms=4.2):
    if lo is not None:
        ax.hlines(y, lo, hi, color=color, lw=1.1, alpha=0.55, zorder=2)
    ax.plot(x, y, marker, ms=ms, color=color, mec=SURF, mew=1.0, zorder=3, label=label, ls="none")


# ------------------------------------------------------------------ fig 2

def fig2(c):
    groups = []  # (testbed label, [(row label, err, lo, hi)])
    if (p := c.path("E02", "cells.csv")):
        rows = read_csv(p)
        g = []
        for r in rows:
            C = fnum(r.get("C_lco", r.get("C")))
            e = fnum(r["oracle_C_hat"]) - C
            g.append((r["cell"].replace("_l0-", " L0="), e, fnum(r["oracle_C_lo"]) - C, fnum(r["oracle_C_hi"]) - C))
        groups.append(("SynthSAEBench zoo (E02), K = 5", sorted(g, key=lambda t: t[0])))
    if (p := c.path("E06", "cells.json")):
        d = json.loads(p.read_text())
        groups.append(("Seeded SAE grid (E06), K = 16", [(k, v["C_hat16"] - v["C16"], v["C_lo"] - v["C16"],
                                                            v["C_hi"] - v["C16"]) for k, v in sorted(d.items())]))
    for exp, fname, title, keyf in (("E08", "levels.json", "Auditor ladder (E08), K = 8", None),
                                    ("E09", "configs.json", "Audit tools (E09), K = 8", None),
                                    ("E10", "arms.json", "Red team, non-adaptive arms (E10)", ("A1", "A5"))):
        if (p := c.path(exp, fname)):
            d = json.loads(p.read_text())
            rows = [(k, v["C_hat"] - v["C"], (v.get("C_lo", np.nan) - v["C"]), (v.get("C_hi", np.nan) - v["C"]))
                    for k, v in d.items() if keyf is None or k in keyf]
            groups.append((title, rows))
    if not groups:
        c.skipped.append("fig2_coverage_error (no E02/E06/E08/E09/E10 outputs)")
        return
    n = sum(len(g) + 1.6 for _, g in groups)
    fig, ax = plt.subplots(figsize=(TEXTW * 0.62, 0.15 * n + 0.7))
    band(ax)
    y, ticks, labels = 0.0, [], []
    for title, g in groups:
        ax.text(-0.02, y, title, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7.5,
                color=INK, weight="bold")
        y -= 1.0
        for lab, e, lo, hi in g:
            ok = np.isfinite(lo) and np.isfinite(hi)
            dot(ax, e, y, lo if ok else None, hi if ok else None)
            ticks.append(y)
            labels.append(lab)
            y -= 1.0
        y -= 0.6
    ax.set_yticks(ticks, labels)
    ax.set_ylim(y + 0.4, 0.8)
    ax.set_xlabel("Ĉ − C (estimated minus true coverage; band ±0.05)")
    style_axis(ax)
    ax.spines["left"].set_visible(False)
    c.save(fig, "fig2_coverage_error")


# ------------------------------------------------------------------ fig 3

HET = [("homog", "homogeneous"), ("base", "logit-normal σ=1"), ("ln2", "logit-normal σ=2"),
       ("zipf0.5", "Zipf α=0.5"), ("zipf1.0", "Zipf α=1"), ("mix20", "20% uncatchable")]


def fig3(c):
    perf, cells = c.path("E01", "performance.csv"), c.path("E01", "cells.csv")
    if not (perf and cells):
        c.skipped.append("fig3_counts (no E01 analysis)")
        return
    P = read_csv(perf)
    Cc = {r["cell"]: r for r in read_csv(cells)}
    get = lambda cell, tgt: next((r for r in P if r["cell"] == cell and r["estimator"] == "chao2"  # noqa: E731
                                  and r["target"] == tgt), None)
    e02 = c.path("E02", "cells.csv")
    ncol = 3 if e02 else 2
    fig, axes = plt.subplots(1, ncol, figsize=(TEXTW, 2.15),
                             gridspec_kw=dict(wspace=0.32 if ncol == 2 else 0.5, width_ratios=[1.2, 1, 0.8][:ncol]))
    ax = axes[0]
    ys = np.arange(len(HET))[::-1]
    for (cell, lab), y in zip(HET, ys):
        for tgt, col, mk, off in (("N", S1, "o", 0.13), ("N_LB", S2, "s", -0.13)):
            r = get(cell, tgt)
            if r:
                b, m = fnum(r["bias"]), fnum(r["mcse"])
                dot(ax, b, y + off, b - 2 * m, b + 2 * m, color=col, marker=mk,
                    label=("against N" if tgt == "N" else "against N_LB") if y == ys[0] else None)
    ax.axvline(0, color=MUTED, lw=0.7)
    ax.set_yticks(ys, [l for _, l in HET])
    ax.set_xlabel("relative bias of Chao2")
    ax.set_title("a  Chao2 bias")
    style_axis(ax)
    fig.legend(*ax.get_legend_handles_labels(), loc="lower center", bbox_to_anchor=(0.5, -0.17), ncol=2,
               handletextpad=0.2, columnspacing=1.2)
    ax = axes[1]
    for (cell, lab), y in zip(HET, ys):
        r = Cc.get(cell)
        if not r:
            continue
        for k, col, mk, off in (("chao2_ci_cover_N", S1, "o", 0.13), ("chao2_ci_cover_N_LB", S2, "s", -0.13)):
            v, m = fnum(r[k]), fnum(r[k + "_mcse"])
            dot(ax, v, y + off, v - 2 * m, v + 2 * m, color=col, marker=mk)
    ax.axvline(0.95, color=INK2, lw=0.8, ls=(0, (3, 2)))
    ax.set_yticks(ys, [])
    ax.set_xlim(-0.03, 1.03)
    ax.set_xlabel("95% CI coverage (dashed: 0.95)")
    ax.set_title("b  Chao2 interval")
    style_axis(ax)
    if e02:
        ax = axes[2]
        rows = read_csv(e02)
        v = np.array([fnum(r["oracle_chao2"]) / fnum(r["U"]) for r in rows])
        w = np.array([fnum(r["oracle_chao2"]) / fnum(r["N_all"]) for r in rows])
        for i, (vals, lab, col, mk) in enumerate(((v, "Chao2 / |U|", S1, "o"), (w, "Chao2 / N_all", S2, "s"))):
            jitter = np.random.default_rng(i).uniform(-0.18, 0.18, vals.size)
            ax.plot(vals, i + jitter, mk, ms=3.2, color=col, mec=SURF, mew=0.6, ls="none")
        ax.axvline(1, color=MUTED, lw=0.7)
        ax.set_yticks([0, 1], ["÷ |U|", "÷ N_all"])
        ax.set_ylim(-0.6, 1.6)
        ax.set_xlabel("Chao2 ratio, per cell")
        ax.set_title("c  SAE zoo (E02)")
        style_axis(ax)
    c.save(fig, "fig3_counts")


# ------------------------------------------------------------------ fig 4

def fig4(c):
    e02, sw, pl = c.path("E02", "cells.csv"), c.path("E03", "sweep.csv"), c.path("E03", "plateau.json")
    if not (e02 or sw):
        c.skipped.append("fig4_identity (no E02/E03 outputs)")
        return
    fig = plt.figure(figsize=(TEXTW, 2.3))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.15], height_ratios=[1, 1], wspace=0.45, hspace=0.25)
    if e02:
        ax = fig.add_subplot(gs[:, 0])
        rows = sorted(read_csv(e02), key=lambda r: r["cell"])
        ys = np.arange(len(rows))[::-1]
        for r, y in zip(rows, ys):
            C = fnum(r.get("C_lco", r["C"]))
            o, m = abs(fnum(r["oracle_C_hat"]) - C), abs(fnum(r["matched_C_hat"]) - C)
            ax.hlines(y, min(o, m), max(o, m), color=GRID, lw=1.6, zorder=1)
            dot(ax, o, y, color=S1, label="oracle identity" if y == ys[0] else None, ms=3.8)
            dot(ax, m, y, color=S2, marker="s", label="matched identity" if y == ys[0] else None, ms=3.8)
        ax.set_yticks(ys, [r["cell"].replace("_l0-", " L0=") for r in rows], fontsize=6)
        ax.set_xlabel("|Ĉ − C|")
        ax.set_title("a  Oracle vs matched identity")
        ax.legend(loc="upper center", bbox_to_anchor=(0.4, -0.2), ncol=2, handletextpad=0.2, columnspacing=1.0)
        style_axis(ax)
    if sw:
        rows = [r for r in read_csv(sw) if r["matcher"] == "M1"]
        cells = sorted({r["cell"] for r in rows})
        cell = cells[len(cells) // 2]
        rs = sorted((r for r in rows if r["cell"] == cell), key=lambda r: fnum(r["tau"]))
        t = np.array([fnum(r["tau"]) for r in rs])
        a1, a2 = fig.add_subplot(gs[0, 1]), fig.add_subplot(gs[1, 1])
        plat = None
        if pl:
            P = json.loads(pl.read_text())
            plat = next((p for p in P if p["cell"] == cell and p["matcher"] == "M1"), None)
        for ax in (a1, a2):
            if plat and plat.get("plateau_tau") is not None and np.isfinite(fnum(plat["plateau_tau"])):
                ax.axvline(fnum(plat["plateau_tau"]), color=INK2, lw=0.8, ls=(0, (3, 2)))
            style_axis(ax, "both")
        a1.plot(t, [fnum(r["n_clusters"]) for r in rs], color=S1, lw=1.6)
        a1.set_ylabel("failure modes\n(clusters)")
        a1.set_title(f"b  Threshold sweep, {cell.replace('_l0-', ' L0=')}")
        a1.tick_params(labelbottom=False)
        a2.plot(t, [fnum(r["f1"]) for r in rs], color=S3, lw=1.6)
        a2.set_ylim(0, 1.02)
        a2.set_ylabel("pair F1\n(vs truth)")
        a2.set_xlabel("matching threshold τ (|decoder cos|); dashed: plateau rule")
    c.save(fig, "fig4_identity")


# ------------------------------------------------------------------ fig 5

def fig5(c):
    p = c.path("E08", "levels.json")
    if not p:
        c.skipped.append("fig5_ladder (no E08 output)")
        return
    d = json.loads(p.read_text())
    levels = [k for k in ("L0", "L1", "L2", "L3") if k in d]
    names = dict(L0="L0\n1 prompt", L1="L1\n8 prompts", L2="L2\n3 sizes", L3="L3\n3 families")
    fig, (a, b) = plt.subplots(1, 2, figsize=(TEXTW * 0.8, 1.8), gridspec_kw=dict(wspace=0.35))
    x = np.arange(len(levels))
    band(a, orient="h")
    for i, L in enumerate(levels):
        v = d[L]
        e = v["C_hat"] - v["C"]
        a.vlines(i, v["C_lo"] - v["C"], v["C_hi"] - v["C"], color=S1, lw=1.1, alpha=0.55)
        a.plot(i, e, "o", ms=4.5, color=S1, mec=SURF, mew=1)
        b.plot(i, v["neff_over_K"], "o", ms=4.5, color=S1, mec=SURF, mew=1)
    b.plot(x, [d[L]["neff_over_K"] for L in levels], color=S1, lw=1.2, alpha=0.5)
    for ax, lab, tt in ((a, "Ĉ − C (95% interval)", "a  Coverage error by level"),
                        (b, "n_eff / K", "b  Effective number of runs")):
        ax.set_xticks(x, [names[L] for L in levels], fontsize=6.3)
        ax.set_ylabel(lab)
        ax.set_title(tt)
        style_axis(ax, "y")
    b.set_ylim(0, 1.05)
    c.save(fig, "fig5_ladder")


# ------------------------------------------------------------------ fig 6

def discovery_curve(X, rng, n=200):
    K = X.shape[1]
    curves = np.empty((n, K))
    for i in range(n):
        o = rng.permutation(K)
        curves[i] = np.cumsum(np.diff(np.concatenate([[0], np.maximum.accumulate(X[:, o], axis=1).sum(axis=0)])))
    return curves.mean(axis=0)


def fig6(c):
    p = c.path("E10", "arms.json")
    if not p:
        c.skipped.append("fig6_arms (no E10 output)")
        return
    d = json.loads(p.read_text())
    hist = c.hist / "e10" if c.hist and (c.hist / "e10").exists() else None
    fig, axes = plt.subplots(1, 2 if hist else 1, figsize=(TEXTW, 2.0),
                             gridspec_kw=dict(wspace=0.95, width_ratios=[1, 0.8]) if hist else {}, squeeze=False)
    axes = axes[0]
    if hist:
        from crsafety import testbed as tb
        ax = axes[0]
        for arm, col in (("A1", S1), ("A2", S2)):
            if (hist / arm).exists():
                X = tb.load(hist / arm).X_est
                cur = discovery_curve(X, np.random.default_rng(0))
                ax.plot(np.arange(1, cur.size + 1), cur, color=col, lw=1.8)
                ax.text(cur.size + 0.4, cur[-1], {"A1": "A1 non-adaptive", "A2": "A2 adaptive"}[arm],
                        va="center", fontsize=6.8, color=INK2)
                ax.plot(cur.size, cur[-1], "o", ms=4, color=col, mec=SURF, mew=1)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.set_xlabel("runs")
        ax.set_ylabel("distinct blind spots found")
        ax.set_title("a  Discovery curves")
        ax.set_xlim(0.5, ax.get_xlim()[1] + 4.5)
        ax.spines["right"].set_visible(False)
        style_axis(ax, "both")
    ax = axes[-1]
    order = [k for k in ("A1", "A5", "A2", "A4", "A3a", "A3b") if k in d]
    lab = dict(A1="A1 non-adaptive", A5="A5 mixed families", A2="A2 adaptive", A4="A4 diversity prompt",
               A3a="A3a de-adapted", A3b="A3b reset estimator")
    ys = np.arange(len(order))[::-1]
    band(ax)
    for k, y in zip(order, ys):
        v = d[k]
        e = v.get("err", v["C_hat"] - v["C"])
        dot(ax, e, y, color=S2 if k in ("A2", "A4") else (S3 if k.startswith("A3") else S1))
    ax.set_yticks(ys, [lab[k] for k in order])
    ax.set_xlabel("Ĉ − C")
    ax.set_title(("b  " if hist else "") + "Coverage error by arm")
    style_axis(ax)
    c.save(fig, "fig6_arms")


# ------------------------------------------------------------------ fig 7

def fig7(c):
    hist = c.hist / "e09" if c.hist and (c.hist / "e09").exists() else None
    if not hist:
        c.skipped.append("fig7_tools (needs E09 histories: --hist)")
        return
    from crsafety import testbed as tb
    caught = {}
    for T in ("T1", "T2", "T3"):
        if (hist / T).exists():
            cl = tb.load(hist / T)
            caught[T] = {i for i, r in zip(cl.items, cl.X_est) if r.any()}
    names = list(caught)
    allitems = set().union(*caught.values()) if caught else set()
    N = len(tb.load(hist / names[0]).items)
    combos = []
    for r in range(len(names), 0, -1):
        for s in combinations(names, r):
            only = {i for i in allitems if all(i in caught[t] for t in s) and not any(i in caught[t] for t in names if t not in s)}
            combos.append((s, len(only)))
    combos.append(((), N - len(allitems)))
    fig = plt.figure(figsize=(TEXTW * 0.6, 2.0))
    gs = fig.add_gridspec(2, 1, height_ratios=[2.2, 1], hspace=0.08)
    a = fig.add_subplot(gs[0])
    b = fig.add_subplot(gs[1], sharex=a)
    x = np.arange(len(combos))
    a.bar(x, [n for _, n in combos], width=0.55, color=[S1 if s else MUTED for s, _ in combos], lw=0)
    for i, (_, n) in enumerate(combos):
        a.text(i, n + 0.15, str(n), ha="center", va="bottom", fontsize=6.5, color=INK2)
    a.set_ylabel("organisms")
    a.set_title("Organisms caught by each combination of tools")
    a.tick_params(labelbottom=False)
    style_axis(a, "y")
    for j, t in enumerate(names):
        for i, (s, _) in enumerate(combos):
            b.plot(i, j, "o", ms=5, color=INK if t in s else GRID, mec=SURF, mew=0.8)
        b.text(-0.8, j, {"T1": "T1 chat", "T2": "T2 sampling", "T3": "T3 white-box"}.get(t, t), ha="right",
               va="center", fontsize=6.8, color=INK2)
    for i, (s, _) in enumerate(combos):
        if len(s) > 1:
            js = [names.index(t) for t in s]
            b.vlines(i, min(js), max(js), color=INK, lw=1.2)
    b.set_yticks([])
    b.set_xticks([])
    b.set_ylim(-1.3, len(names) - 0.4)
    for sp in b.spines.values():
        sp.set_visible(False)
    b.text(len(combos) - 1, -0.75, "none", ha="center", va="top", fontsize=6.3, color=INK2)
    c.save(fig, "fig7_tools")


# ------------------------------------------------------------------ tables

TABLE1 = [
    ("SynthSAEBench zoo (E02)", "planted SAE feature", "one trained SAE", "oracle |cos| ≥ 0.7; matched M1", "5", "pool of 35 SAEs", "generator"),
    ("Seeded SAE grid (E06)", "planted SAE feature", "one seeded SAE", "as E02", "16", "8 seeds", "generator"),
    ("Pythia-70M SAEs (E11)", "SAE feature", "one seeded SAE", "M1 at plateau τ", "8", "—", "partial (board games)"),
    ("Planted marks (E15)", "injected direction", "one seeded SAE", "|cos| ≥ 0.7", "8", "4 seeds", "injection"),
    ("Auditor ladder (E08)", "implanted quirk", "one audit", "validated judge", "8", "8 audits", "implant"),
    ("Audit tools (E09)", "fine-tuned behaviour", "one audit", "validated judge", "8", "8 audits", "implant"),
    ("Red-team monitor (E10)", "planted blind spot", "one attacker session", "monitor log", "12", "12 sessions", "instrumented"),
]


def table1(c):
    head = ["Testbed", "Failure mode", "Run", "Identity rule", "K", "Reference runs", "Truth from"]
    md = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in TABLE1]
    tex = ["\\begin{tabular}{lllllll}", "\\toprule", " & ".join(head) + " \\\\", "\\midrule"] + \
          [" & ".join(x.replace("≥", "$\\geq$").replace("|cos|", "$|\\cos|$").replace("τ", "$\\tau$") for x in r) + " \\\\"
           for r in TABLE1] + ["\\bottomrule", "\\end{tabular}"]
    write_table(c, "table1_testbeds", md, tex)


def table2(c):
    p = c.path("E13", "summary.json")
    if not p:
        c.skipped.append("table2_stopping (no E13 output)")
        return
    per = json.loads(p.read_text())["per_testbed"]
    rows = []
    for key, v in per.items():
        tb_, rule, t = key.split("|")
        rows.append((tb_, rule, t, f"{v['success']:.2f}", f"{v['median_saved']:.0%}", f"{v['mean_undershoot_when_failed']:.3f}"))
    head = ["Testbed", "Rule", "Target c*", "Success", "Median runs saved", "Mean undershoot (failures)"]
    md = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
    tex = ["\\begin{tabular}{lllrrr}", "\\toprule", " & ".join(head) + " \\\\", "\\midrule"] + \
          [" & ".join(r).replace("%", "\\%") + " \\\\" for r in rows] + ["\\bottomrule", "\\end{tabular}"]
    write_table(c, "table2_stopping", md, tex)


def write_table(c, name, md, tex):
    if c.preview:
        name += "_PREVIEW"
        md = ["> PREVIEW: SIMULATED INPUTS, NOT RESULTS", ""] + md
        tex = ["% PREVIEW: SIMULATED INPUTS, NOT RESULTS"] + tex
    c.tables.mkdir(parents=True, exist_ok=True)
    (c.tables / f"{name}.md").write_text("\n".join(md) + "\n")
    (c.tables / f"{name}.tex").write_text("\n".join(tex) + "\n")
    c.made.append(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--hist", default=None, help="root holding e09/ and e10/ history cells (figs 6a, 7)")
    ap.add_argument("--out", default=str(ROOT / "paper" / "figures" / "out"))
    ap.add_argument("--tables", default=None)
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    a.tables = a.tables or (str(Path(a.out) / "tables") if a.preview else str(ROOT / "paper" / "tables"))
    c = Ctx(a)
    for f in (fig2, fig3, fig4, fig5, fig6, fig7, table1, table2):
        f(c)
    print("made:", ", ".join(c.made))
    print("skipped:", "; ".join(c.skipped) or "none")


if __name__ == "__main__":
    main()
