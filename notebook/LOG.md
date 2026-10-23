# Lab log

Append-only. Newest entry at the bottom. Corrections are new entries
("Correction to 2026-11-03: ..."), never edits. Template:
[`templates/entries.md`](templates/entries.md).

---

## 2026-10-22: Project set-up; prior knowledge on record

**Did:**
- Chose idea 3 from "Six Research Ideas in AI Safety" (15 Oct 2026).
- Ran the literature survey (11 agent reports, about 400 searches; see
  `research/`).
- Wrote and ran the pilot simulation (`pilot/`, commits dc6a0a7 and
  a6ff751).
- Built this notebook and the study pre-registration (v0.1, not frozen).

**Prior knowledge (what we had already seen before any pre-registration was
frozen).** This matters for the confirmatory status of later experiments,
so it is listed in full:
- **Pilot results** (`pilot/results.md`), all on simulated data:
  - Chao2 matches its population bound;
  - coverage error ≤ 0.02 under heavy tails;
  - Δ prediction within 2 to 13% (Zipf) and about 20% low (logit-normal
    σ = 2);
  - 15% ghosts → Chao2 +42%;
  - family-shared effects: Chao2 −21% with 1 family vs −2% with 6.
- **Published numbers we know:**
  - Paulo and Belrose: 30 to 42% of latents shared across seeds.
  - Ghosh et al.: 2% → 29% strict matches as training data grows.
  - Kansal's two studies: the unseen share is estimable, counts are lower
    bounds; label-error intervals 102 to 797 for a truth of 181.
  - AuditBench: about 37% default success *(secondary source)*.
  - SLEIGHT-Bench: 20 of 40 attacks never caught.
- **Not seen:** any SynthSAEBench SAE weights, any AuditBench run output,
  any E10 monitor run. The confirmatory experiments (E02 onwards) start
  blind to their own outcome data.

**Design choices informed by the prior knowledge:**
- coverage, not N, as the primary estimand;
- K ≥ 6 (validation K = 10 to 20);
- matching treated as a measured quantity;
- dependence and adaptivity built into the design.

**Next:** E00 (estimator library). Resolve the open questions blocking E02
and E09 (data access) in `docs/OPEN-QUESTIONS.md`.

## 2026-10-22 (later): Documentation and feasibility check

**Did:** Wrote the study pre-registration (v0.1), pre-registrations for E00
to E17 with contingencies, the supporting docs (`docs/`) and the notebook
tool. Two research agents checked documentation best practice (I1) and
testbed feasibility (I2).

**Saw (from reading testbed code; no experiment outcomes):**
- **SynthSAEBench default world has a mild tail.** Zipf exponent 0.5 and
  p_min = 5e-4, so every feature fires about 10^5 times in training. Misses
  there come from capacity and absorption, not sampling. → E02 tests the
  structurally uncatchable regime; E06's base world uses α = 1.0 and
  p_min = 1e-6.
- **Zoo seeds are uncontrolled.** Initialisation and data vary jointly and
  unseeded. SAELens does not seed training. → E06 and E11 seed explicitly,
  with an R001 hash check.
- **AuditBench:** repo `safety-research/auditing-agents`; per-run
  `quirks/*.md` outputs; 70B targets need 2–4 × 80 GB GPUs; a GPU-free
  system-prompt suite (16 quirks) exists; the investigator is hard-wired to
  Claude. → E08 now uses Petri, which can run any model family as the
  auditor, on the system-prompt organisms.
- **Tooling:** R + Rcapture + iNEXT + breakaway install in this sandbox via
  conda-forge. There is no GPU and no Docker daemon here.

**Next:** Owner decisions on budget (Q-B1), licences (D-006) and the
disclosure notice window. Then E00.

## 2026-10-22 (evening): $0 plan and team split

**Decided:**
- **D-007:** run everything at $0, with open models on the sandbox CPU and
  free Kaggle GPUs. Frontier replication moves to E18 (only if credits
  arrive).
- **Team:** Santosh owns statistics, estimators and the SAE track; Kushal
  owns the safety testbeds (E08–E10), LLM infrastructure and judges. Each
  runs the confirmatory analysis on the other's data. See `docs/TEAM.md`.

**Changed (pre-freeze, not deviations):**
- E06: scaled-down world.
- E08: open-model auditor ladder.
- E09: AuditBench-lite (fine-tuned Gemma-2-2B organisms; Gemma Scope
  white-box tool).
- E10: open attackers with a harmless proxy goal.
- E11: Pythia-70M only.
- New page: E18.
- `tools/notebook.py` now requires `--owner` on every run.
- Detection-history format: PROTOCOLS §10.
- CI checks the notebook on every push.

**Next:** Santosh: E00. Kushal: Kaggle LLM stack and model pinning (Q-D14),
E10 monitor (E10-R001). Freeze target: 8 November.

## 2026-10-22 (night): E00 estimator library validated against R

**Did:**
- Built `src/crsafety` (commit f792c71). It contains the estimators,
  the Chao bootstrap and detection-history I/O (PROTOCOLS §10).
- Wrote 377 property tests.
- Wrote `validation/e00/`, which compares the library against iNEXT,
  vegan, SpadeR, Rcapture and VGAM on 34 datasets.
- Ran E00-R001 and E00-R002 from the clean commit.

**Saw:**
- All 437 reference comparisons pass. Deterministic quantities agree to
  2.8e-10 or better. Bootstrap s.e. agree within Monte Carlo error.
- All 377 property tests pass.
- Three formula findings came from reading the reference source; each was
  matched to the reference:
  - coverage when Q2 = 0 uses iNEXT's bias-corrected f0;
  - the Chao2 interval falls back to a Poisson-type interval when Q1 ≤ 1;
  - ICE follows SpadeR, because `fossil::ICE` does not implement the
    published formula.
- Two code fixes came from the tests:
  - Darroch Mt returned infinity when one run found every item; the MLE
    there is S;
  - Huggins now uses an analytic gradient and tighter tolerance. It matches
    VGAM to 3e-10 (was 3e-8).
- Sandbox R is now 4.5.3 with iNEXT 3.0.2. The E00 contingency table names
  older versions.

**Decided:** D-008, formula conventions.

**Next:**
- Kushal reviews `results/E00/E00-R001/summary.md` and the D-008
  conventions (four-eyes rule).
- E00-R003, the remaining estimators: Chiu-Chao is needed before E05.
- E01 simulation study on top of `crsafety`, frozen by 5 November.

## 2026-10-22 (late night): E00-R003 remaining estimators validated

Santosh.

**Did:**
- Ported Rcapture's log-linear models to `crsafety.loglinear` /
  `crsafety.closedp` (12 `closedp.t` models; run interactions as in
  `closedpCI.t`, with or without heterogeneity).
- Added `generalized_chao` (Böhning et al. 2013, binomial form) and
  `crsafety.rbridge.breakaway_nof1` (R through `Rscript`).
- Wrote `validation/e00/run_r003.sh` and 218 property tests.
- Ran E00-R003 (reference comparison) and E00-R004 (pytest) from commit
  ba80724.

**Saw:**
- All 1,744 comparisons pass on 29 datasets; max relative difference
  3.0e-12 (log-linear s.e.), ≤ 5e-13 for N, deviance, AIC and BIC.
- Rcapture's printed s.e. differs from ours by up to 2.3e-6 relative. Cause:
  glm's `vcov()` uses the IRLS weights from the iteration before
  convergence. Recomputing the information at Rcapture's own MLE matches us
  to 3e-12. Rcapture's Chao (LB) refits also drop the user's glm tolerance;
  the reference script forces it.
- The harness was debugged on trial runs before R003 (not registered as
  runs, as they tested the harness, not the estimators). Issues found
  there, all on the reference side or at boundaries: iNEXT's rounded
  output, glm `vcov()` precision, N̂ = S fits with an arbitrary s.e., and one
  diverging Mh Chao fit (syn_zipf_K12), which made our IRLS fail until it
  used least-squares steps like R.
- `breakaway_nof1` predicts f1 too, so adding singletons leaves its
  estimate unchanged (my first test assumed a shift; the test was wrong).
- With an oracle covariate, `generalized_chao` has median error < 1% but an
  unstable mean under heavy tails (Horvitz-Thompson weights): relevant to
  E07.
- Chiu-Chao: the paper (PeerJ, PMC, arXiv) is unreachable from the sandbox,
  and none of the Chao-lab GitHub packages implement it. Contingency
  applied (D-009). Q-D10 stays open.
- Environment: micro.mamba.pm, CRAN and peerj.com are blocked; conda-forge
  and `git clone` from GitHub work. conda-forge's `r-breakaway` is 3.0 and
  pins R 4.1.3, so breakaway 5.0.1 was built from GitHub into an R 4.5.3
  environment (same versions as R001; breakaway from adw96/breakaway commit 35f83d4).
  rpy2 3.6 does not load against it.

**Decided:** D-009.

**Next:** Kushal reviews E00 (R001–R004) and D-008/D-009. Santosh: E01
simulation study.

## 2026-10-22 (night, later): E01 code and pre-run choices

Santosh.

**Did:**
- Wrote `src/crsafety/sim.py` (the E01 data-generating mechanisms),
  `src/crsafety/manifest.py` (run manifests, PROTOCOLS §5),
  `configs/e01/cells.json` (40 cells, seeds, R005 subset),
  `analysis/e01/run.py` and `analysis/e01/analyse.py`, plus 38 tests.
- Added `requirements.lock` (uv pip compile); installed the locked NumPy
  2.5.4 / SciPy 1.18.1.
- Fixed every choice §2 leaves open in E01 §2a, before any E01 run.

**Disclosure:** a 3-replicate smoke test of each run, written to the
scratch directory, checked that the code runs (R001–R005 take seconds at
n_sim = 3). The analysis printout of that test showed the H1e and H1f lines
on those 3 replicates, which are the first 3 replicates of the real runs.
The analysis sets and rules were already in code and were not changed after
that. E01 is Stage 1 (exploratory), so this does not affect any confirmatory
claim.

**Next:** run E01-R001 to R005 from the committed code; analyse.

## 2026-10-22 (night, last): E01 run and analysed; gate G1 passed

Santosh.

**Did:**
- Ran E01-R001 to R005 (40 cells × 500 replicates, plus the bootstrap
  subset) from commit 7765a22; every manifest records a clean tree.
- Fixed one presentation bug in the analysis after the first look:
  estimators undefined by design (iChao2 at K = 3, the log-linear fit at
  K = 20) were shown as "fail 100%". They are now "not applicable". No
  number changed.
- Added three exploratory runs, labelled as such: R006 (small-N
  calibration), R007 (a new bootstrap interval, on the R005 datasets) and
  R008 (the same on fresh datasets, criterion fixed beforehand).
- Wrote E01 §5, D-010, RESULTS rows; PREREGISTRATION v0.2 (draft): interval
  method only.
- Added `crsafety.histories.check_cell` (H2 handoff validator).

**Saw:**
- Gate G1 passes: max |bias of Ĉ| over the 14 clean cells is 0.009.
- H1d, H1e and H1f are supported; H1a (literal set), H1b and H1c are not
  (E01 §5 has the numbers).
- Surprise 1: the pre-registered bootstrap interval for Ĉ covers the
  realized C in only 76% of base-cell replicates. It measures the spread of
  Ĉ, but C itself varies from sample to sample. Bootstrapping Ĉ* − C*
  fixes most of it: 0.906 on fresh datasets (R008).
- Surprise 2: H1c failed because the dependence factor sits on σ = 1
  heterogeneity, whose marginal odds ratio (2.6) cancels θ = 1/3. Chapman
  moved 16.5 points, but from −35%.
- Surprise 3: at E09/E10 sizes (14–20 items) an unbiased Ĉ is often more
  than 0.05 from C. PH1's per-cell tolerance will need changing for those
  testbeds (proposal in D-010, for the freeze).
- Shared families are the worst violation (+0.23 with one family at
  K = 10) and more runs barely help (+0.21 at K = 12). This supports E08's
  design: diversity of catchers matters more than their number.

**Scoop check (week of 2026-10-19; Santosh's turn).** Searched arXiv,
OpenReview and the Alignment Forum through a web search tool for
capture-recapture with LLM audits, red teams or SAEs; "audit coverage";
unseen failure modes; and the near-miss authors. **No scoop found.** Worth
citing:
- METR, "Alignment assessment proposal" (2026-10-14): asks whether the
  assessor's search "missed some serious misalignment incidents", without
  an estimator. Good motivation for the introduction.
- Three June 2026 SAE seed-stability papers relevant to E06/E11:
  "Ablating Archetypes" (arXiv 2606.02061) says reported stability comes
  from identical initialisation across runs; "Aligned Training"
  (2605.18629) and L2 weight regularisation (2603.04198, ICML 2026)
  improve cross-seed stability. E06's initialisation-only vs data-only
  seed cells speak to the first.
- arXiv 2609.15803 uses "auditing robust coverage" for a different
  (complexity-theoretic) notion; avoid the name clash in the paper.

**Next:**
- Kushal reviews E00 (R001–R004), E01 (R001–R008), D-008, D-009, D-010.
- Joint: decide D-010 part B at the v1 freeze (6–8 Nov).
- Santosh: E05-R001 (injection grid on E01 histories, which regenerate
  from the E01 seeds) and preparation for E02 (blocked on Hugging Face
  access, Q-D1).

## 2026-10-22 (night, E05): error model, corrections and pilot

Santosh.

**Did:**
- Built `crsafety.linkage`, a record-level identity-error model with match
  scores. It covers ghosts per recapture (uniform or score-based rates),
  merges, labelled-pair estimation of f and g, and corrections (b) first-order
  count correction, (e) multiple imputation, and (f) Di Consiglio-Tuoto.
  Also `analysis/e05/pilot.py` and 13 tests.
- Registered E05-R001 to R003 as planned (confirmatory, after the freeze).
  Ran the declared pilots E05-R004 and R005 on separate seeds.
- Wrote E05 §2a: every implementation choice §2 leaves open, marking which
  ones changed after the pilot.

**Saw (pilot only):**
- Every correction runs without failure. MI costs 0.02 s per injection, so
  the "too slow" contingency is not needed. R001 needs about 15 min plus
  1–2.5 h for `breakaway_nof1`.
- The count correction removes most ghost bias (Chao2 +35% → 0% at
  f = 0.10 on the base world; +316% → +18% at f = 0.30 with score-based
  errors on ln2).
- The free-mixture MI in §2 relinks real singletons when there are no
  ghosts (−26%). A variant using labelled bin rates does not (−6%, the
  merge effect). Both will be reported; the labelled one is proposed as
  primary.
- `breakaway_nof1` is not usable on K = 10 incidence counts: Poisson
  fallback in 59% of injections, median −18% to −43%.

**Next:** Kushal reviews E05 §2a with the other Stage 2 pages before the
freeze. Open for the freeze: whether to add a ratio-regression f1-free
estimator (needs an E00 run).

## 2026-10-22 (night): matching library; E13 stopping rules and pilot

Santosh.

**Did:**
- Wrote `crsafety.matching`: the SAE identity rules for E02, E03, E06 and
  E11, with 10 tests. Timed at E02 scale: about 25 min of CPU for all 35
  cells.
- Wrote `crsafety.stopping` (R-point; R-lower with the D-010 bound;
  R-fixed) and a declared pilot on simulated campaigns.
- E13-R002 crashed at once: `stop_lower` rejected a SeedSequence seed. My
  command chain also hid the failing smoke test, which is why the run got
  registered. Marked failed (bug), fixed with a test, re-run as E13-R003.

**Saw (pilot):**
- R-lower reaches the target in 0.93–0.985 of campaigns where the target
  is reachable, saving 19–69% of runs; R-point only 0.50–0.79.
- One shared family defeats every rule (0% success).

**Next:** the same as the previous entry. Before the freeze: review of
E02/E03/E05/E13 pages with Kushal.

## 2026-10-22 (night, late): M3 matcher; an f1-free alternative tried and rejected

Santosh.

**Did:**
- Wrote `analysis/e03/act_corr.py` (M3, activation correlation), plus the
  `bakeoff.py --m3` and `--fire-counts` options. Tested M1–M4 end to end on
  SAEs trained by SAELens's own runner.
- Built `crsafety.betabinomial_nof1`, a beta-binomial fitted to items found
  at least twice, as a candidate replacement for `breakaway_nof1` in E05
  (d). It recovers N to 3e-5 from expected beta-binomial counts (test).
- Exploratory, on the stored frequency tables of pilot E05-R005 (no new
  run): compared it with `breakaway_nof1` against the oracle Chao2.

**Saw:** the beta-binomial alternative is worse, not better. Medians were
+8% to +220%. Means exploded (up to +10^6%) on the σ = 2 world, where the
fit runs to a → 0. Extrapolating from counts ≥ 2 down to f1 and f0 is barely
identified at K = 10. **Recommendation for the freeze (FREEZE-V1 item 6):**
keep (d) as specified and report its failure; do not add another f1-free
estimator. The function stays in the library, marked "not recommended".

## 2026-10-22 (late): H8 de-adaptation, H5 analysis scripts, E01-R009

Santosh.

**Did:**
- Resolved Q-D7. The ICSE'24 paper is in the authors' GitHub pages repo,
  which git can clone although the website is blocked here. The FSE'21
  reset estimator is in their artefact repo. Implemented both in
  `crsafety.deadapt` (handoff H8), with tests.
- Wrote the frozen-analysis scripts for Kushal's experiments (handoff H5):
  `analysis/e08/analyse.py`, `analysis/e09/analyse.py`,
  `analysis/e10/analyse.py`, with shared code in `crsafety.testbed` and an
  end-to-end test on fake PROTOCOLS §10 histories.
- Ran E01-R009 (exploratory): how de-adaptation behaves.

**Saw:**
- E10 §2's reconstruction of A3a was a no-op: shuffling a window does not
  change Ĉ at its end. The real algorithm works on every prefix of every
  shuffled window.
- Faithfully implemented, both methods over-correct at our scale (numbers
  in E01 §5 and the R009 run summary). A3b is undefined at the run level
  because every run finds something new. Proposed D-012 for the freeze;
  E10 itself is Kushal's page.

**Next:** E06 simulation side (seeding check, configs, analysis), then
E04's SAE arm and E07 code.


## 2026-10-23: E06 training and analysis scripts; E07 covariate models

Santosh.

**Did:**
- E06: training script (`analysis/e06/train.py`, resumable, Kaggle GPU)
  and the R014 analysis (`analysis/e06/analyse.py`). `zoo.py histories
  --reference-from` marks reference seeds. Tiny CPU run end to end
  (2 cells × 24 seeds); smoke output only, no numbers kept.
- E07: `crsafety.huggins_ci` (SE equals VGAM's to 1e-7 on the E00
  datasets) and `analysis/e07/analyse.py`. `zoo.py` now writes the observed
  latent covariates per run into items.csv. `fire_counts.py` also sums
  activations; it had a bug in the first version, caught in the smoke test.

**Saw:**
- E06 H6e names Δ̂(16), but only 8 reference seeds exist.
- E07's |U| target and the Huggins estimand differ.
- Both are added to the freeze packet (items 11, 12).

**Next:** E04 SAE arm, E01 figures, E16 novelty check.

## 2026-10-23 (later): E04 SAE arm and pilot R003

Santosh.

**Did:**
- Wrote the E04 SAE arm (`analysis/e04/sae_arm.py`) and its tests.
  `zoo.py` now saves the cross-seed cosine distribution of true matches,
  which is E04's noise model.
- Registered R001 (confirmatory, planned) and R002 (Kushal's attack arm,
  planned). Ran the declared pilot R003: random directions and fixed noise,
  spawn keys 9000+.

**Saw:**
- As written, split variants make H4a fail for any one-to-one identity rule
  (clusters / N_true 3.5).
- The ghost correction over-corrects to 0.73 because splits add detections.
- Freeze item 13 proposes scoring H4a without splits and reporting them
  separately.

**Next:** E01 figures, E16 novelty check, CLAUDE.md refresh.

## 2026-10-23 (later): E01 figures

Santosh.

**Did:**
- `analysis/e01/figures.py` draws two figures from the committed E01
  analysis tables (no new runs). Output: `results/E01/analysis/figures/`.
  - Fig. 1: Ĉ bias next to Chao2's relative bias, per cell.
  - Fig. 2: interval coverage, iNEXT normal (R005) vs the realized-coverage
    bootstrap (R008).
- Colours are two validated categorical slots; the second series also uses
  a different marker.
