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
| 1 | † thresholds of PH1 | **Agreed (Kushal, Santosh):** keep 0.05 in ≥ 80% of cells for E02/E06, which carry PH1. The E09/E10 part is replaced by item 17 | D-010 B; E01-R006; Kushal's positions |
| 2 | PH2 at small N | **Agreed:** restrict the "intervals miss N" half to testbeds with N ≥ 500 (E02, E06); keep "Chao2 < N" everywhere; H9b stays descriptive. The prereg states that the restriction comes from E01 H1b (D-005, prior knowledge) | D-010 B; E01 H1b; Kushal's positions |
| 3 | PH3a ratio, PH4, PH5 | **Agreed:** keep 2, 0.05 and 0.05. PH4/PH5 are read against the catcher-agnostic truth (item 16). Power: E10 planted blind spots M = 20 → 40; a second E08 target model if Q-B3 allows; report the minimal detectable effect next to each verdict. PH3a's ratio stays 2 and is **not** revisited after the E03 pilot (Santosh), since E03 freezes at v1.0 | D-010 B; Kushal's positions |
| 4 | Truth for E02 and E06 | Leave-cell-out truth as primary (the pooled truth is biased by up to +0.07) | D-011 |
| 5 | E05 MI variant | Labelled-calibrated MI (e2) primary; free mixture (e1) reported | E05 §2a; pilots R004/R005 |
| 6 | E05 f1-free estimator | Keep `breakaway_nof1` as specified and report its failure; do not add another. Both it and a truncated beta-binomial alternative (`crsafety.betabinomial_nof1`, tried on the pilot's stored frequency tables) are unusable at K = 10: medians −18% to −43% and +8% to +220% respectively, with blow-ups on heavy-tailed worlds | E05 §2a; LOG 2026-10-22 |
| 7 | Licences | Code MIT; docs and released data CC BY 4.0 | D-006 (repository owner) |
| 8 | Disclosure notice window | **Agreed:** 30 days, extendable to 90 on the provider's request with the reason logged. Kushal owns it, including the pre-release check that no E10 blind spot mirrors a deployed product's weakness (before M4) | `DISCLOSURE.md`; Kushal's positions |
| 9 | E01 H1c design flaw | Note in the paper that the dependence factor sat on σ = 1 heterogeneity; no re-run (E01 is not frozen, but its verdicts stand as run) | E01 §5 |
| 10 | E10 arm A3 (de-adaptation) | **Agreed:** D-012 option A (faithful algorithm, expect H10c to fail) plus C (design-based secondary), both scored against the catcher-agnostic truth (item 16); attempt-level A3 (option B) exploratory only | D-012; E01-R009; Kushal's positions |
| 11 | E06 H6e horizon | Amend H6e to Δ̂(8) against the 8 reference seeds (the only observable horizon), or train 16 reference seeds (+88 SAEs) | E06 §2a |
| 12 | E07 open points | Firing threshold = smallest p in U; \|U\| primary with N_thr reported; H7b supported if x3 or x4 is; failed fits count against | E07 §2a |
| 13 | E04 split variants | **Option 3 (Kushal's review, agreed):** split geometry and recurrence from E02; H4c two-sided 0.67–1.5; options 1 and 2 secondary. Pilots: H4a fails under every option-1/3 setting (R003–R005: 2.4–3.6 clusters per feature, 2.4 even at full recurrence); without splits 1.17–1.23 (R004) | E04 §2a; E04-R003–R005; review §6 |
| 14 | E11 estimand | Unweighted Ĉ over latents above f_min = 10⁻⁶ (the activation-mass-weighted estimand has no validated estimator); weighted version exploratory | E11 §2a |
| 15 | E15 SAE arm | Pooled-12 truth for marks; observed covariates via proxy map primary; H15c compares marks conditional on ≥ 1 catch; **pilot R005: 6 marks make calibration worse than Chao-Jost, ≥ 20 needed; H15b's 30% unlikely where Chao-Jost holds** | E15 §2a; E15-R005 |
| 16 | E08/E10 primary truth (Kushal's review) | D-013 code supports both. Kushal proposes the catcher-agnostic truth (`cells:L3` for E08, `cells:A1,A5` or all arms for E10) as co-primary for H8a/H10b; own-reference truth secondary. Santosh agrees | D-013; review §5 |
| 17 | PH1 † for E09/E10 (Kushal's counter-proposal) | Pool Ĉ − C over cells and items with a bootstrap CI: supported if the CI lies within ±0.10; not supported if it excludes 0 by > 0.05; state that E09/E10 are underpowered for PH1 and E02/E06 carry it. Santosh agrees; replaces D-010 B's E09/E10 part | review, positions |
| 18 | PH5 wording (Kushal's review §2.1) | Reword PH5 so the direction follows the adaptation: cross-run revisiting overstates coverage, steering to new holes understates it (E01 H1d: +0.07 vs −0.15); within-run adaptation is tested against the catcher-agnostic truth (item 16) | review §2.1, §5 |

## 3. Staged freeze (D-015): pages to lock at v1.0, v1.1 and v1.2

Proposed by Kushal, agreed by Santosh. Each stage uses the same four-eyes
review and the same chain (section 4), with its own tag. No confirmatory run
starts before its page is frozen.

| Stage | When | What locks |
|---|---|---|
| **v1.0** | Nov 6–8 | `PREREGISTRATION.md` (hypotheses and every threshold, including items 16–18), the decisions in section 2, and the pages E02, E03, E05, E13 |
| **v1.1** | about Nov 22 | E08 and E10, after their pilots (R001, R002) and the judge check (H4, Nov 12). E10's monitor is rebuilt for M = 40 before its R001 |
| **v1.2** | about Jan 5 | E09, after the R004 pilot (Dec 18) and before the T1 runs (Jan 17). The T3 tool (D-014) is final by then |

Conditions (Santosh):
- Thresholds and hypotheses lock at v1.0. v1.1 and v1.2 lock testbed
  details only, so no pilot can move a threshold.
- Each frozen analysis script locks with its page, with its `--truth` value
  named in the frozen command: `analysis/e08`/`e10/analyse.py` at v1.1,
  `analysis/e09/analyse.py` at v1.2.
- Pilot results that shape a v1.1/v1.2 page are cited in it as prior
  knowledge (D-005).
- E02 and E03 can only lock at v1.0 if E02-R001, the zoo inventory (Kaggle,
  pre-freeze OK), has run. If it hasn't, they move to v1.1.

| Page | Stage | Owner → reviewer | Pilot | Ready? |
|---|---|---|---|---|
| E02 | v1.0 | Santosh → Kushal | R001 inventory on Kaggle (allowed before the freeze) | code ready (`analysis/e02/`); run R001 first |
| E03 | v1.0 | Santosh → Kushal | uses E02-R001 | code ready (`analysis/e03/bakeoff.py`) |
| E05 | v1.0 | Santosh → Kushal | R004, R005 done | §2a drafted; decisions 5–6; confirmatory scripts ready: `analysis/e05/run.py`, `analyse.py` |
| E13 | v1.0 | Santosh → Kushal | R003 (simulated) done | confirmatory runner ready: `analysis/e13/run.py`; data from E02/E06/E09/E10 later |
| E08 | v1.1 | Kushal → Santosh | R001, R002; judge check H4 | frozen analysis script ready: `analysis/e08/analyse.py` (`--truth`, D-013) |
| E10 | v1.1 | Kushal → Santosh | R001 (monitor, M = 40), R002 (difficulty) | frozen analysis script ready: `analysis/e10/analyse.py`; decision 10 |
| E09 | v1.2 | Kushal → Santosh | R004 (pilot organisms, Dec 18) | frozen analysis script ready: `analysis/e09/analyse.py`; T3 tool per D-014 |

## 4. Freeze chain (after sections 1–3)

1. Apply the agreed changes to `PREREGISTRATION.md` (version v1.0,
   changelog row) and to the experiment pages.
2. `python tools/notebook.py freeze EXX --note "prereg v1; reviewed by <name>"`
   for each page in section 3.
3. Commit with no results in the tree for the frozen experiments.
4. Annotated tag `prereg-v1.0` (later `prereg-v1.1`, `prereg-v1.2`); GitHub
   release; Zenodo DOI; OSF registration citing the commit and the DOI.
5. LOG entry by both.
