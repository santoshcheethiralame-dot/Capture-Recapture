# Paper figures and tables

Run everything from `results/`:

```bash
python paper/figures/fig1_concept.py      # Fig. 1 (concept; toy history, illustrative)
python paper/figures/make_all.py          # Figs 2–7 and Tables 1–2 -> paper/figures/out, paper/tables
python analysis/e01/figures.py            # appendix Figs A.1, A.2 -> results/E01/analysis/figures
```

`make_all.py` skips any figure whose inputs do not exist yet and lists it.
Input paths per experiment are in `INPUTS` at the top of the script; update
a run ID there when its run finishes.

**Layout previews.** To see every figure before the data exists:

```bash
python paper/figures/preview_inputs.py --out <scratch>     # runs the real analysis scripts on simulated histories
python paper/figures/make_all.py --preview --results <scratch>/results --hist <scratch> --out <scratch>/figs
```

Previews are stamped "PREVIEW: SIMULATED INPUTS, NOT RESULTS", end in
`_PREVIEW`, and are never committed.

| Output | Content | Inputs | Status (2026-10-23) |
|---|---|---|---|
| fig1_concept | two toy audits, agreement → coverage | none | done |
| fig2_coverage_error | Ĉ − C (95% interval) by testbed, ±0.05 band | E02, E06, E08, E09, E10 | waits on data |
| fig3_counts | Chao2 bias vs N / N_LB and CI coverage (E01); Chao2 / \|U\| (E02) | E01 (+E02) | E01 panels real |
| fig4_identity | oracle vs matched \|Ĉ − C\|; threshold sweep with plateau | E02, E03 | waits on data |
| fig5_ladder | Ĉ − C and n_eff / K by auditor-similarity level | E08 | waits on data |
| fig6_arms | discovery curves A1 vs A2; Ĉ − C by arm incl. A3 | E10 (+histories) | waits on data |
| fig7_tools | organisms caught by each tool combination (UpSet) | E09 histories | waits on data |
| table1_testbeds | testbed, run, identity rule, K, reference runs, truth | static | done |
| table2_stopping | E13 success, runs saved, undershoot by rule and target | E13 | waits on data |

Style: validated two-to-three-hue palette, one axis per panel, error bars as
95% intervals or ±2 MCSE (stated in each label), selective direct labels,
recessive grid, sized for a 5.5-inch text width; PDF fonts embedded (Type 42).
