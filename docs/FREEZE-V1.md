# Pre-registration v1.0 freeze packet

Target: 6–8 November 2026 (ROADMAP M2). Procedure:
[`PREREGISTRATION.md`](PREREGISTRATION.md) "Freeze plan" and
[`TEAM.md`](TEAM.md) rule 1 (four-eyes: each page is approved by the person
who did not write it, in a PR, and the reviewer is named in the freeze
note). This page lists what has to be reviewed or decided first. Tick items
off in the PR, not here.

Status on 2026-10-22: the study pre-registration is draft v0.2. Nothing is
frozen.

## 1. Results the freeze builds on (Kushal reviews)

| Item | Where | What to check |
|---|---|---|
| E00 estimator library: R001–R004 | `notebook/experiments/E00-estimator-library.md` §5, `results/E00/` | 437 + 1,744 R comparisons pass; formula conventions D-008; D-009 (log-linear ported, breakaway via Rscript, Chiu-Chao left out) |
| E01 simulation study: R001–R008 | E01 §5, `results/E01/analysis/summary.md` | Verdicts H1a–H1f; gate G1 passed; exploratory runs R006–R008 labelled as such |
| D-010 part A: interval method | `notebook/DECISIONS.md` | The realized-coverage bootstrap replaces the iNEXT interval (0.906 vs 0.760 coverage in the base cell) |

## 2. Decisions to take together

| # | Question | Proposal | Source |
|---|---|---|---|
| 1 | † thresholds of PH1 | Keep 0.05 / 80% for E02 and E06; for E09/E10 use pooled \|bias\| ≤ 0.03 plus interval coverage ≥ 0.85 | D-010 B; E01-R006 |
| 2 | PH2 at small N | Restrict the "intervals miss N" half to N ≥ 500, or keep it and expect "not supported" for E09/E10 | D-010 B; E01 H1b |
| 3 | PH3a ratio, PH4, PH5 | Keep 2, 0.05 and 0.05 | D-010 B |
| 4 | Truth for E02 and E06 | Leave-cell-out truth as primary (the pooled truth is biased by up to +0.07) | D-011 |
| 5 | E05 MI variant | Labelled-calibrated MI (e2) primary; free mixture (e1) reported | E05 §2a; pilots R004/R005 |
| 6 | E05 f1-free estimator | Keep `breakaway_nof1` as specified and report its failure; do not add another. Both it and a truncated beta-binomial alternative (`crsafety.betabinomial_nof1`, tried on the pilot's stored frequency tables) are unusable at K = 10: medians −18% to −43% and +8% to +220% respectively, with blow-ups on heavy-tailed worlds | E05 §2a; LOG 2026-10-22 |
| 7 | Licences | Code MIT; docs and released data CC BY 4.0 | D-006 (repository owner) |
| 8 | Disclosure notice window | 30 days (proposed) | `DISCLOSURE.md` |
| 9 | E01 H1c design flaw | Note in the paper that the dependence factor sat on σ = 1 heterogeneity; no re-run (E01 is not frozen, but its verdicts stand as run) | E01 §5 |
| 10 | E10 arm A3 (de-adaptation) | Keep as pre-registered with the faithful algorithm and expect H10c to fail; add a design-based secondary analysis | D-012; E01-R009 |
| 11 | E06 H6e horizon | Amend H6e to Δ̂(8) against the 8 reference seeds (the only observable horizon), or train 16 reference seeds (+88 SAEs) | E06 §2a |
| 12 | E07 open points | Firing threshold = smallest p in U; \|U\| primary with N_thr reported; H7b supported if x3 or x4 is; failed fits count against | E07 §2a |
| 13 | E04 split variants | Score H4a on plain and absorbed latents, splits reported separately; as written H4a fails for any one-to-one rule (pilot R003: clusters / N_true 3.5) | E04 §2a |
| 14 | E11 estimand | Unweighted Ĉ over latents above f_min = 10⁻⁶ (the activation-mass-weighted estimand has no validated estimator); weighted version exploratory | E11 §2a |

## 3. Pages to lock at v1.0

Per the freeze plan: Stage 2 pages whose pilots are complete. Others are
frozen one by one later.

| Page | Owner → reviewer | Pilot | Ready? |
|---|---|---|---|
| E02 | Santosh → Kushal | R001 inventory on Kaggle (allowed before the freeze) | code ready (`analysis/e02/`); run R001 first |
| E03 | Santosh → Kushal | uses E02-R001 | code ready (`analysis/e03/bakeoff.py`) |
| E05 | Santosh → Kushal | R004, R005 done | §2a drafted; decisions 5–6 |
| E08 | Kushal → Santosh | R001 (floor/ceiling, scaffold) | Kushal; frozen analysis script ready: `analysis/e08/analyse.py` (H5) |
| E09 | Kushal → Santosh | R004 (pilot organisms) | later (gate G3); frozen analysis script ready: `analysis/e09/analyse.py` |
| E10 | Kushal → Santosh | R001 (monitor), R002 (difficulty) | Kushal; frozen analysis script ready: `analysis/e10/analyse.py`; decision 10 |
| E13 | Santosh → Kushal | R003 (simulated) done | needs E02/E06/E09/E10 data; can freeze now or with E09 |

## 4. Freeze chain (after sections 1–3)

1. Apply the agreed changes to `PREREGISTRATION.md` (version v1.0,
   changelog row) and to the experiment pages.
2. `python tools/notebook.py freeze EXX --note "prereg v1; reviewed by <name>"`
   for each page in section 3.
3. Commit with no results in the tree for the frozen experiments.
4. Annotated tag `prereg-v1.0`; GitHub release; Zenodo DOI; OSF
   registration citing the commit and the DOI.
5. LOG entry by both.
