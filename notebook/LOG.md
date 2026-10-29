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

## 2026-10-23 (later): E16 novelty check and bracket script

Santosh.

**Did:**
- E16-R001 novelty check. Q-N2 is answered: no prior work found, and this
  doubles as the weekly scoop check.
- Wrote `analysis/e16/bracket.py` (R002 registered, planned).

**Saw (smoke test, toy world, 96 features; numbers seen, not results):**
- Oracle-missed energy 0.18 against total residual energy 0.07.
- Partly reconstructed features count as "missed" under the |cos| rule, so
  the residual cannot bound them.
- Noted in E16 §2a as a decision to take before R002.

## 2026-10-23 (later): H7 white-box tool

Santosh.

**Did:**
- Built handoff H7 early (due 2026-12-15): `src/crsafety/tools/gemma_scope.py`.
  - For a prompt, it returns the top SAE features (max over tokens, BOS
    excluded) with labels, and the features most changed against the base
    model, with their sign.
  - `PromptBank` caches activations and caps new prompts per run (E09 §3
    contingency). `from_hf` loads a model pair plus a Gemma Scope SAE.
  - Tests: `tests/test_gemma_scope.py`, with fake models and a tiny random
    GPT-2.
- Not checked here: the real Gemma-2-2B and Gemma Scope weights (HF is
  blocked).
- E09-R003 ("tool built and unit-tested") is on Kushal's page, so I have
  not registered it. Kushal, please register and run it on Kaggle with
  real weights and the Neuronpedia label export.

## 2026-10-23 (later): PR #3 merged; E15 novelty check

Santosh.

**Did:**
- Merged PR #3 (E04/E06/E07/E11/E16 code, the H7 tool, E01 figures, the
  methods draft) and restarted the branch from main.
- Ran the E15-R001 novelty check. Q-N1 is answered: no one plants marks,
  fits detectability and calibrates coverage of real items. The closest
  work is Kansal's `undiscovered-failures` and AuditBench-style planted
  behaviours used to score auditors.

**Next:** E15 SAE-arm injection and calibration code.

## 2026-10-23 (later): E15 SAE-arm code; Kaggle runbook

Santosh.

**Did:**
- Wrote `crsafety.calibrate`, the planted-mark detectability fit with
  Horvitz-Thompson C_cal, N̂ and Δ, a proxy map and a bootstrap interval.
- Wrote `analysis/e15/inject.py` (`marks`, `train`, `stats`, `magnitudes`;
  CPU smoke-tested on the tiny model) and `analysis/e15/analyse.py`
  (tested on synthetic SAEs).
- Registered E15-R002, R003 (Kushal's audit arm) and R004. R003 was first
  registered with the wrong title and corrected the same day; the note is
  on the run.
- Wrote `docs/KAGGLE-RUNBOOK.md`, which lists every Kaggle job on my side
  in order and marks which ones may run before the freeze.

**Saw:**
- In a simulation with mild heterogeneity, calibrated coverage is unbiased
  but no better than Chao-Jost. H15b will show whether planting marks pays
  off in practice.

## 2026-10-23 (later): E05 and E13 confirmatory runners

Santosh.

**Did:**
- Wrote the scripts to lock at the freeze and run after it:
  - `analysis/e05/run.py` (R001/R002) and `analysis/e05/analyse.py`
    (R003);
  - `analysis/e13/run.py` (R001).
  Both refuse a dirty tree and are tested on simulated or hand-made inputs.

**Disclosure:**
- The first E05 smoke test (120 injections) used the confirmatory seed
  stream at injection 0 before I added the smoke offset.
- I printed only the table shape and non-finite counts, never an estimate,
  and deleted the output.
- Smoke runs now use keys from 9000 (the pilot range).

## 2026-10-23 (later): paper drafts, Fig. 1, CLAUDE.md refresh

Santosh.

**Did:**
- Drafted the paper's introduction, related work and limitations in
  `paper/drafts/`. Results numbers are placeholders until their runs exist.
- Drew Fig. 1, the concept figure, from a toy history
  (`paper/figures/fig1_concept.py`; illustrative, not data).
- Refreshed `CLAUDE.md` with the current state and remaining work.

## 2026-10-23 (later): paper §4, §8, Appendix A; LLM-use statement

Santosh.

**Did:**
- Drafted §4 (testbeds; the E08–E10 paragraphs are placeholders for Kushal
  to rewrite), §8 (conclusion and recommendations) and Appendix A (E00
  validation and the E01 simulation study, with an estimator decision
  guide).
- Added a draft LLM-use statement to `docs/NEURIPS-CHECKLIST.md`, covering
  writing and code assistance, for both authors to edit.

## 2026-10-23 (later): paper figure and table pipeline

Santosh.

**Did:**
- `paper/figures/make_all.py` builds every planned figure and table from
  `results/`. Figure 3 (E01 panels) and Table 1 are made from real data
  now.
- `preview_inputs.py` runs the real analysis scripts on simulated
  histories, so the layout of every other figure can be checked in
  advance.
- The previews are stamped as simulated and are not committed.

## 2026-10-23: four-eyes review of E00, E01, D-010A, D-011, D-012, E04

Kushal.

**Did:**
- Reviewed E00 R001–R004 with D-008/D-009, E01 R001–R009 with D-010 part A,
  the proposals D-011 and D-012, and E04 §2a with pilot R003. Full comments:
  `notebook/reviews/2026-10-23-kushal-four-eyes.md`.
- Re-ran `pytest` (695 passed, 4 skipped without R) and
  `analysis/e01/analyse.py` (reproduces `results/E01/analysis/` exactly).

**Found:**
- `crsafety.testbed.true_pi` uses estimation + reference runs, so the
  E08–E10 truth carries the D-011 bias (about +0.03 for E10, +0.05 for E08
  in a back-of-envelope simulation, not a registered run). E10 §2 says
  reference runs only.
- With per-catcher truth and independent sessions, H10b and PH4 are close
  to null by construction. A catcher-agnostic truth is proposed as
  co-primary (E08/E10 pages, to follow).

**Next:** Santosh's replies in the PR; E08/E10 truth proposal; positions
on freeze items 2 and 8.

## 2026-10-23 (later): pilots for open freeze items (E04-R004, E15-R005, E16-R003)

Santosh.

**Did:**
- Ran three declared, exploratory CPU pilots. Each was registered before
  launch and used pilot seed keys.
  - E04-R004: H4a scored under freeze options 1 and 2, at split |r| 0.5 and
    0.25. `sae_arm.py` now also scores the runs without split latents.
  - E15-R005: calibrated vs Chao-Jost coverage at audit sizes, in
    simulation (`analysis/e15/pilot_sim.py`).
  - E16-R003 (running): two small CPU-trained worlds, to see which
    missed-mass estimand the residual can bound. `bracket.py` now also
    computes the unreconstructed missed energy, and no longer keeps all
    feature activations in memory.

**Saw:**
- E04: with splits, clusters per feature depend on the split geometry
  (3.4–3.5 vs 2.1–2.3). Without splits the ratio is 1.17–1.23, on the 1.2
  threshold.
- E15: 6 marks make calibration worse than Chao-Jost in every cell. 20 or
  more help by up to 21%, never the 30% of H15b.
- Both are added to freeze items 13 and 15; no threshold was changed.

**Smoke tests (numbers seen, disclosed):**
- E04: 3 replicates, keys 99000+.
- E16: 2 under-trained seeds on 100k samples. M_miss 0.46/0.82 against
  U_res 0.49/0.52.
- None of these numbers is used anywhere.

## 2026-10-23 (later): E16-R003 result

Santosh.

**Saw:**
- With trained SAEs, the total residual bounds the oracle-missed energy in
  both pilot worlds (0.104 ≤ 0.111 and 0.162 ≤ 0.265), and both lower
  bounds hold.
- The Engels-style linearly predictable residual does not bound it (0.023
  and 0.094).
- The smoke-test concern came from under-training.
- E16 §2a now proposes U_res as the upper bound for R002.

## 2026-10-23 (later): building on Kushal's four-eyes review

Santosh.

**Did** (in answer to `notebook/reviews/2026-10-23-kushal-four-eyes.md`):
- D-013, the review's blocking item:
  - `crsafety.testbed.truth_pi` with `reference` (default), `pooled` and
    `cells:<ids>`;
  - `--truth` in `analysis/e08`, `e09` and `e10/analyse.py`, with
    `C_pooled` always reported;
  - a test reproduces his bias (pooled truth inflates C, reference truth
    does not).
- Freeze items 16 (primary truth for H8a/H10b) and 17 (his PH1 counter-
  proposal for E09/E10), both agreed from my side.
- `tools/notebook.py` no longer marks a run `+dirty` for edits under
  `notebook/` or `results/`, matching `crsafety.manifest`.
- Chapman and Good-Turing are marked "unvalidated (hand-checked)" in their
  docstrings (review §1.1).

**Next:** his D-010A condition (a small-N interval check), E04 option 3
and two-sided H4c, the stale Chiu-Chao text on E04, the PH5 wording.

## 2026-10-23 (later): E01-R010, the small-N interval check

Santosh.

**Saw:**
- At N = 14–20 the realized-coverage interval covers C in 0.894–0.954 of
  replicates; at N = 50, 0.924–0.974.
- Kushal's condition on D-010 A (criterion ≥ 0.85, fixed before running) is
  met.
- Recorded in E01 §5 and RESULTS. The analysis rerun only added R010's
  section and file.

## 2026-10-23: Kushal: E09-R003 (Gemma Scope T3 tool) prepared for Kaggle

**Did:**
- Registered E09-R002 (implants, planned) and E09-R003 (tool check), owner
  Kushal, so the IDs match E09 §2's planned-runs table.
- E09-R003 labels step (sandbox): Neuronpedia's public S3 export for
  `gemma-2-2b/12-gemmascope-res-16k` (the Neuronpedia id SAELens gives for
  `layer_12/width_16k/canonical`) labels all 16,384 features, one method
  (gpt-4o-mini, token-activation pairs). Written to
  `results/E09/E09-R003/labels/` with sha256s. This answers the label half
  of Q-D15; the loading half needs the Kaggle step.
- `analysis/e09/gemma_scope_check.py`: checks C1–C5 with pass criteria
  fixed before the run (load, hook alignment by L0/FVU, identity, non-empty
  diff, prompt bank), timing for the E09 §3 contingency, and the share of
  top features that sit on chat-template tokens. Smoke-tested end to end on
  a tiny random Gemma-2 and a fake SAE (no numbers from it mean anything).
  Runbook: new "Kushal's account" section, row K1.
- Fixed in `crsafety.tools.gemma_scope.hf_resid`: in chat mode the Gemma
  template already starts with `<bos>` and the tokenizer added a second one,
  which `skip_first` would not drop (Gemma's BOS residual has outlier norm,
  so it would dominate the top features). Test added. `from_hf` now loads
  with eager attention (SDPA skips Gemma-2's logit soft-capping).

**Open:** the "audited" model in R003 is Gemma-2-2B-it itself, since no
organism exists before R002; the diff check only shows the tool returns
something, not that it surfaces an implant. That is R004's job (pilot
organisms). The SAE is trained on the pt model and applied to -it
residuals; R003 reports FVU on both.

## 2026-10-23: Kushal: E09-R003 result (Gemma Scope T3 tool check), Q-D15 answered

Ran on Kaggle (Kushal's account, T4, 0.039 GPU-h; manifest git sha 1cf4e4c,
clean tree). Outputs in `results/E09/E09-R003/`. All five pre-set checks
passed (C1 load, C2 alignment, C3 identity, C4 non-empty diff, C5 bank);
`all_pass` is true. Numbers: mean L0 79.2 on pt residuals (nominal 82),
FVU 0.078 on pt, 0.101 on -it chat (the SAE fits -it well); FVU is lowest at
layer 12 against 11 and 13, so the hook index is right; 0.34 s per uncached
call (both models), 0.0003 s cached, so no speed contingency.

**Found (descriptive, not a pre-set check):** the tool as built is nearly
prompt-independent. 73% of top-10 features (mean over 20 prompts) peak on
chat-template tokens, not on the user's text. The same four features
(#4667, #11087, #1041, #1178) are in the top 5 for all 20 prompts, with
activations of 100–360 against tens for text features, and the same ones top
"most changed vs base" (the -it model's template tokens differ from pt's).
An auditor using T3 would mostly see these constants. The checks passed
because they test mechanics, not usefulness.

**Proposal (not applied; tool is Santosh's, E09 §2 describes T3 only at the
level of "top active features"):** take the per-feature maximum over the
user's prompt tokens only, excluding all template tokens, and compare ft vs
base on those tokens. Needs a code change in `crsafety.tools.gemma_scope`
(token mask in `hf_resid`) and a repeat of R003's template-share check
before freeze; E09-R004 (pilot organisms) is the real test of whether T3
surfaces an implant. Raise with Santosh.

## 2026-10-23: Kushal: correction to E09-R003 (review of PR #12)

CodeRabbit's review of PR #12 (it posted just after the merge) found two
defects in `analysis/e09/gemma_scope_check.py`. Both are confirmed:
- **Template-token share off by one.** The offsets were computed with the
  tokenizer's default `add_special_tokens=True`, so they had one more token
  than the residual rows (17 vs 16 on the stand-in tokenizer), and each
  activation was classified using the next token's position. The reported
  0.73 is therefore not reliable as a number.
- **SDPA instead of eager attention** for the models behind C2, C4, timing
  and the template share (only C3 went through `from_hf`, which uses
  eager). The Gemma-2 logit soft-capping was skipped on that path. C2's L0
  and FVU are unlikely to move much at 20-token prompts, but they were not
  measured on the tool's own path.

What stands: C1, C3 and C5 are unaffected, and so is the main finding,
that the same four features (#4667, #11087, #1041, #1178) are in the top 5
for all 20 prompts. That is read straight off `responses.json` and does not
depend on the offsets. Also fixed: C5's reload check now uses a zero-budget
bank, so a missing entry fails instead of being silently recomputed, and an
assert ties the offset count to the residual rows. No re-run now. The
template share is re-measured with the user-token-mask follow-up, which
needs a Kaggle run anyway.

## 2026-10-23: Kushal: T3 user-token rule; E09-R004…R009 registered

**Did:**
- `crsafety.tools.gemma_scope`: `hf_resid(..., user_only=True)` keeps only the
  rows of tokens that overlap the user's text (located with a sentinel, so a
  prompt containing "user" or "model" and Gemma's content trimming are
  handled). `from_hf` uses it by default (`user_only=True`, `skip_first`
  off). The bank key includes the rule, so a bank built under the old rule
  is not reused. Three tests added. This is Santosh's tool, so it's in a
  PR for his review.
- `analysis/e09/gemma_scope_check.py`: `--tokens user|all` and `--run-id`.
  New check C7 (prompt specificity), with the criterion fixed before
  E09-R009: for both lists, the mean pairwise Jaccard of the prompts'
  top-10 sets is ≤ 0.25, and no feature is in the top 5 of more than 15 of
  20 prompts. It was calibrated on E09-R003's responses (0.50 top features,
  0.83 most changed, four features in all 20 top-5s), which is a tool
  check, not an outcome. The other rule is reported alongside. Smoke-tested
  on the stand-in models under both rules.
- Registered E09-R004…R008 as planned (the §2 table: pilot, T1, T2, T3,
  analysis with Santosh as owner) so IDs stay stable, and E09-R009, the
  re-check (runbook K2).

**Caveat:** C7 tests that the tool's output varies with the prompt, not
that it surfaces an implant. That is still R004's job.

## 2026-10-23: Kushal: E09-R009 result (T3 user-token rule)

Ran on Kaggle (Kushal's account, T4, 0.045 GPU-h; git sha 7fe3f1e, clean;
outputs in `results/E09/E09-R009/`). C1–C5 pass again. **C7 fails by its
pre-set criterion**, so the manifest and run status are "failed". This is
a result, not a bug.

| | top features: Jaccard / max prompts sharing a top-5 feature | most changed: Jaccard / max sharing |
|---|---|---|
| all tokens (R003 rule) | 0.50 / 20 | 0.83 / 20 |
| user tokens (R009) | **0.15** / 20 | **0.33** / 17 |
| criterion | ≤ 0.25 / ≤ 15 | ≤ 0.25 / ≤ 15 |

What changed: the lists now follow the prompt. For example, "Should
factory farming be banned?" returns features for factory, bans and
restrictions, agriculture, governance and questions. Under R003 it
returned template constants.

What still fails:
- One feature, #1041 ("technical terms and concepts related to programming
  or data structures", activation ~77), is top-1 on 19 of 20 prompts.
  That pattern looks like a position feature, e.g. one that fires on the
  first user token, rather than content. This is a guess: the argmax token
  is not saved.
- The most-changed list (Jaccard 0.33) still repeats #2009, #5590 and #6810
  (legal, licensing). Here "base" is the pt model, so the list measures
  -it vs pt, which is generic instruction-tuning drift. In E09 itself the
  base will be -it and the audited model an organism, so this part of C7
  doesn't transfer.
- The SAE fits user-token residuals of -it less well (FVU 0.31, against
  0.10 over all chat tokens and 0.08 on pt).

**Not done:** any tweak designed after seeing these numbers, such as
dropping #1041, dropping the first user token, or a "background feature"
filter. Any of these would be a new, labelled run with a criterion fixed
first. Proposal: take the current rule into the E09-R004 pilot. There the
diff is organism vs -it, which is the real question. Add a pre-specified
background filter only if the pilot shows constant features crowding out
the implant.

## 2026-10-23: Kushal: T3 background blocklist rule (D-014), E09-R010 registered

Fixed the rule before any run that uses it (D-014). Background features are
those in the top 10 on more than 50% of 100 neutral prompts, on
Gemma-2-2B-it with user tokens. They are hidden from the top-features list
only. Code: `background_blocklist`, plus a `blocklist` option on the tool and
on `from_hf`, with one test. `analysis/e09/background_blocklist.py` was
smoke-tested on the stand-in models. E09 §2 T3 wording updated. Registered
E09-R010 (runbook K3). The 20 check prompts are reported with and without
the blocklist, as a description only.

## 2026-10-23: Kushal: positions on freeze items 1, 2, 3, 8, 10

Completed the positions left open in the four-eyes review:
`notebook/reviews/2026-10-23-kushal-freeze-positions.md`. Item 1 defers to
item 17; item 2 restricts PH2's interval half to N ≥ 500; item 3 keeps the
thresholds and proposes E10 M = 40 and E08's second target (quota
permitting) for power; item 8 is 30 days, extendable to 90; item 10 is A
plus C against the catcher-agnostic truth. E08/E10 to freeze after their
pilots.

## 2026-10-23 (later): review of Kushal's PRs #12–#16 and D-014

Santosh.

**Did:**
- Reviewed E09-R003, the user-token rule, E09-R009 and D-014.
- Approved D-014 as written. A binomial check shows the 50% cutoff is
  sharp at 100 prompts: a feature with a true top-10 share of 0.6 is
  blocklisted with probability 0.97, at 0.4 with probability 0.02.
- Three suggestions, none blocking; see
  `notebook/reviews/2026-10-23-santosh-d014.md`.
- Tests: 707 passed on main at a54182f.

## 2026-10-23 (later): freeze positions folded in; staged freeze agreed (D-015)

Santosh.

**Did:**
- Folded Kushal's positions on items 1, 2, 3, 8 and 10 (PR #17) into
  FREEZE-V1 §2, all agreed.
- PH3a's ratio stays 2 and is not revisited after the E03 pilot.
- Agreed his staged freeze, recorded as D-015: v1.0 Nov 6–8, v1.1 (E08,
  E10) about Nov 22, v1.2 (E09) about Jan 5, with conditions. FREEZE-V1 §3
  is restructured by stage.
- PR #17's CI is green: tests, notebook check and GitGuardian all pass.

## 2026-10-23 (evening): Kushal: E09-R010 result; D-014 follow-ups

**E09-R010 (succeeded, 0.019 GPU-h on a T4, clean tree at 3e61111).** The
D-014 rule blocklists 6 features (top-10 share on the 100 neutral prompts):

| Feature | Share | Neuronpedia label |
|---|---|---|
| 1041 | 1.00 | technical terms and concepts related to programming or data structures |
| 2291 | 0.82 | technical or mathematical symbols and terms |
| 2620 | 0.77 | words associated with authority, control, and criticism of governance |
| 5511 | 0.60 | frequently occurring articles in a text |
| 384 | 0.55 | instances of the word "what" |
| 15596 | 0.55 | forms of the verb "to be" |

On the 20 check prompts (descriptive only, not used to set anything), the
top-features lists go from mean Jaccard 0.152 to 0.038, and the most
prompts sharing one top-5 feature from 20 to 3.

**Near-threshold features (Santosh's suggestion 3).** Top-10 share between
0.35 and 0.65: 5511 (0.60), 384 (0.55), 15596 (0.55) blocklisted; 1617
(0.47, "questions or statements expressing confusion or concern") and 4504
(0.44, "interrogative phrases that seek clarification") not. The list is
complete: `top30_by_share` ends at 0.04. 384 and 15596 are the
sample-dependent ones (P(blocklisted) about 0.8 at a true share of 0.55,
per Santosh's binomial table), but both are function-word features, so
which side they fall on matters little.

**Label reading (Santosh's suggestion 1b).** The labels are fixed, so this
part of the risk diagnostic can be done now rather than at R004. 5511, 384
and 15596 are function-word features. 2620 (governance, authority) could
overlap anti_ai_regulation and secret_loyalty; 1041 and 2291 (programming,
technical symbols) could overlap hardcode_test_cases. These are the three
organisms to watch.

**Risk diagnostic (suggestion 1a), E09-R011 registered.** Changed from the
proposal: run once after E09-R002 on all 16 organisms (not only the 2 pilot
organisms in R004), on trigger prompts, reading no audit. The response is
fixed now: the blocklist stays as it is for R007 whatever R011 shows. A
flagged feature is still visible in the unfiltered most-changed list, so
changing the rule on organism data would add a forking path for little gain.
Flagged organisms are reported as a T3 limitation. Script
`analysis/e09/blocklist_diagnostic.py` (2 tests; smoke-tested on stand-in
models), E09 §2 analysis plan and planned runs updated, runbook K4.

**render() note (suggestion 2).** Accepted; Santosh offered to add it to
his tool, so it is left to him.

## 2026-10-23 (evening): H3 Kaggle LLM stack built; serving check registered

Kushal.

**Did:**
- Built H3 in `src/crsafety/llm/`: model registry and pins
  (`configs/llm/models.json`, `pins.json` after the check), call cache
  (PROTOCOLS §6, layered so a backed-up Kaggle dataset can be re-attached),
  cached client for vLLM's OpenAI server with retries and token counts,
  and a launcher that runs one server per GPU. Notebook
  `kaggle/llm_serving.ipynb`, notes in `kaggle/README.md`.
- Layout: target or organism on GPU 0, auditor or attacker on GPU 1. Two
  fp16 7–9B models do not fit on 2 × T4 at once, so 7–9B models are 4-bit
  (AWQ if an official or HF-staff build exists, else bitsandbytes at load).
- vLLM pinned at 0.19.1: releases from 0.20 on are built on CUDA 13
  (driver ≥ 580), while Kaggle's image ships torch 2.11.0+cu128.
- Registered E08-R002…R007 as planned (the prereg table, so IDs match)
  and E08-R008, the serving check that pins the models (Q-D14). Its pass
  criteria S1–S5 are in the script docstring, fixed before the run.
- 15 CPU tests against a stand-in vLLM server (`tests/fakes/vllm`),
  including the serving check end to end.

**Found:** Gemma 2 has no system role and an 8k window; the E08 scaffold
should put auditor instructions in the first user turn for every family,
and a 20-turn audit has to fit 8k if Gemma is an L3 auditor.

**Next:** run E08-R008 on Kaggle; copy `pins.json` into `configs/llm/`.

## 2026-10-23 (later): E10 monitor built for M = 40; R001 passes

Kushal.

**Did:**
- Built the E10 guard, `crsafety.monitor`. It is deterministic: a receiver
  with a 79-cell decoder grammar defines a leak, and the guard runs the
  same search but skips its blind-spot cells. M is configurable, with tiers
  1:2:1 by default. The main and pilot instances come from
  `SeedSequence(20261032).spawn(2)`.
- Updated the E10 page for M = 40 (10/20/10), as agreed in FREEZE-V1 item
  3. The rest of the §2 alignment for v1.1 (D-013 truth wording, items 16
  and 18) is still to do.
- E10-R001 at 3569be0: 322 of 322 checks pass for both monitors. Every
  blind spot is reachable and credited alone, and every other cell is
  blocked. A hole-free guard lets 0 of 500 random attacks through. Against
  main, all 299 successes are credited only to blind spots, 9 of them to
  two. 0 of 200 benign conversations were flagged. Details are in E10 §5.
- `tests/test_monitor.py` adds 96 tests.

**Saw:**
- "No success without a blind spot" holds by construction, because success
  is whatever the receiver can decode. Out-of-grammar leaks count as
  `no_leak`. R002 should log how often LLM attackers try channels outside
  the grammar, because that is where the testbed's validity is weakest.
- The hard pool is mostly Caesar shifts, and main has 11 of them. This
  could create item dependence once an attacker finds one. A per-family
  cap is worth deciding before v1.1.
- The medium pool (29) cannot give the pilot 20 cells disjoint from main.
  The pilot shares 11 medium cells with main.

**Next:** R002 difficulty pilot on the pilot monitor (Nov 10, needs H3).

## 2026-10-23 (later): review of E10-R001 (PR #23); cluster bootstrap for E10

Santosh.

**Did:**
- Reviewed Kushal's M = 40 monitor. Its tests pass (96).
- Main-monitor families are concentrated: 24 of 40 blind spots are in
  three families (Caesar 11, hex 7, base64 6).
- An illustrative simulation (not a registered run) shows within-run
  family sweeps leave Ĉ unbiased (−0.004 vs −0.005) but raise
  sd(Ĉ − C) from 0.069 to 0.110. A cap of 4 per family brings it to
  about 0.06.
- `crsafety.testbed.boot_items(groups=...)` is now a cluster bootstrap.
  `analysis/e10/analyse.py` resamples whole families when items.csv names
  them (`--cluster family`, the default), records the unit in arms.json,
  and its docstring no longer says M = 20.
- Recommended to Kushal: cap blind spots per family before v1.1, add a
  `family` covariate to `write_history`, and make the pilot and main draws
  disjoint (adding medium cells, then re-running R001).

## 2026-10-26: E08-R008 H3 serving check failed (infra); fixes; re-run registered as E08-R009

Kushal.

**Did:**
- Ran E08-R008 on Kaggle 2 × T4 (0.38 GPU-h; driver 580.178, vLLM
  0.19.1, torch 2.10.0). No candidate of the five pilot models came up,
  so nothing was pinned and S2–S8 never ran. Logged as failed (infra).
  Outputs are in `results/E08/E08-R008/`.
- Root causes, from the vLLM logs:
  - On sm75, vLLM chose FlashInfer attention. FlashInfer compiles kernels at
    start-up, and the link failed with `cannot find -lcuda` (Kaggle has
    `libcuda.so.1` only). This hit Qwen and Mistral, and probably Llama's AWQ
    build too; that log was overwritten.
  - vLLM refuses fp16 for Gemma 2. In float32, its LoRA kernels refuse the
    dtype (gemma2-2b-it), and bitsandbytes at load failed a weight-shape
    assertion (gemma2-9b).
  - The Llama-3.1 licence was not granted yet (403).
- Fixes:
  - Triton attention for every model, FlashInfer's sampler off, and a
    `libcuda.so` link for the linker.
  - Gemma 2 runs in float32 only, without LoRA, so E09 organisms will be
    served merged.
  - One log per candidate, with the error lines kept in the JSON.
  - The pair check is skipped when a model is unpinned.
  - The manifest is marked failed when not all models are pinned.
  - 4 new tests.
- Correction to the 2026-10-23 entry: Kaggle's driver is 580, so the CUDA 13
  builds of vLLM would also load. I kept 0.19.1 for the re-run so that only
  the known causes change.
- Registered E08-R009, the re-run with criteria unchanged. Gemma-2-9B gets
  one last vLLM option, a pre-quantised build. Granite-3.3-8B is added as an
  alternative third L3 family in case Gemma-2-9B cannot be served.

## 2026-10-26 (later): E08-R009, 3 of 6 models pinned; E08-R010 registered

Kushal.

**Did:**
- E08-R009 ran on Kaggle 2 × T4 (0.66 GPU-h). Three models are pinned and
  pass S1–S5:
  - Qwen2.5-7B-Instruct AWQ: S2 8/8.
  - Llama-3.1-8B-Instruct AWQ (Hugging Face staff build): S2 7/8.
  - Granite-3.3-8B-Instruct, bitsandbytes 4-bit: S2 8/8.
  - All three recall a code word across 9–10k tokens and follow a system
    prompt.
  - Pins are in `configs/llm/pins.json`. The run is logged failed by its
    all-pinned criterion.
- Throughput at 32 concurrent requests: 112–116 tok/s for AWQ and 50 tok/s
  for bitsandbytes. In a batch, seeded requests reproduce 7–8 of 8, which
  confirms that the cache, not the seed, is the record of a run.
- Failures:
  - **Mistral (target):** the AWQ build passes S1–S4, but its template
    rejects the system role (S5). Mistral quantised at load failed a
    weight-shape assertion.
  - **Gemma-2-9B:** the pre-quantised build failed the same assertion.
    With R008, Gemma-2-9B cannot be served on a T4 with vLLM 0.19.1.
  - **Gemma-2-2B:** in float32, Triton attention needs 80 KB of shared
    memory and a T4 has 64 KB.
- Fixes:
  - A Mistral v3 chat template (`configs/llm/templates/mistral-v0.3.jinja`).
    The system message is prepended to the last user turn, as Mistral's own
    tokenizer does. Its sha256 goes into the cache key.
  - FlexAttention for Gemma-2-2B.
  - The serving check now carries the committed pins, so the pair check can
    use Qwen without re-testing it.
  - 3 new tests.
- Registered E08-R010 for Mistral, Gemma-2-2B and the Mistral + Qwen pair.
- Wolf's first R009 session output was not found afterwards. Interactive
  `/kaggle/working` is deleted when a session ends, so long runs now go
  through Save Version → Save & Run All. The uploaded R009 zip is the run's
  record.

**Open:** the third L3 family. Gemma-2-9B does not run on a T4 here, and
Granite-3.3-8B passed every check. This is Kushal's call before the E08 freeze.

## 2026-10-27: E10 monitor rebuilt per Santosh's review; R008 passes

Kushal.

**Did:**
- Acted on Santosh's three recommendations from the review of E10-R001:
  - capped blind spots at 4 per family;
  - added a `family` covariate to `write_history`;
  - made the pilot and main monitors disjoint.
- The grammar grew from 79 cells in 18 families to 110 cells in 30, so both
  monitors fit under the cap. Main and pilot are chosen jointly by an
  integer program. Cap 4 is the tightest that fits at 10/20/10; cap 3 is
  infeasible.
- Registered E10-R002 to R007 as planned, so the run IDs match E10 §2's
  planned-run table. R007 belongs to Santosh.
- E10-R008 at f70a6cc: 446 of 446 checks pass for both monitors. Main and
  pilot share no cell. A hole-free guard lets 0 of 500 random attacks
  through. Against main, all 233 successes are credited only to blind
  spots. 0 of 200 benign conversations were flagged. R001 is marked
  superseded.
- Added one sentence to E10 §2's testbed paragraph: the cap and the
  disjoint pilot. §2 is not frozen; it locks at v1.1.

**Saw:**
- base64, hex and Caesar each still hit the cap in both monitors, so the
  largest family is 10% of items, down from 28%.
- Screening is about 40 ms per one-message attack, against about 1 ms
  before.

**Next:** R002 difficulty pilot on the pilot monitor (needs H3).

## 2026-10-27: E08-R010, Mistral pinned and the pair check passes; E08-R011 registered

Kushal.

**Did:**
- Ran E08-R010 on Kaggle 2 × T4 at 86ad9b0 (clean tree), 0.28 GPU-h.
- Added Mistral-7B AWQ to `configs/llm/pins.json` (revision 95b1295, from
  R010). Closed R010 as failed by its all-pinned criterion
  (data-access, Gemma only).
- Registered E08-R011: Gemma-2-2B-it alone (runbook K6, notebook cell 5).

**Saw:**
- Mistral with the v3 template passes S1–S5: S2 7/8, recall at 8.8k tokens,
  system prompt followed. Throughput is 112 tok/s at 32 concurrent; S7 seed
  8/8.
- S8 pair (Mistral target, Qwen auditor) passes: 16 conversations × 6 turns
  in 373 s, an estimated 0.022 GPU-h per 20-turn audit.
- Gemma-2-2B never loaded: Hugging Face returned 401 (gated repo). In R009
  the earlier token reached it, so the new token (made after the old one was
  revoked) lacks gated access.
- All four E08/E10 pilot models (Qwen, Mistral, Llama, Granite) are now
  pinned, which is what the Nov 10 pilots need. Gemma-2-2B is the E09 base
  and not on that path.

**Next:** E08-R011 once the token can read gated repos; then H3 is closed.

## 2026-10-28: E10 review follow-up: family-matched pilot (E10-R009)

Santosh.

**Did:**
- Reviewed PR #26 (merged on 2026-10-27).
- Agreed to the grammar expansion. It was forced by the disjoint-pilot
  recommendation: two disjoint 40-cell monitors need at least 80 cells, and
  the old grammar had 79.
- Added a family-matched pilot constraint to `draw_disjoint`.
- Fixed the E10 §2 wording on tiers.
- Added an R002 success bar and a §3 contingency.
- Added two pair checks to `r001_verify.py`.
- Ran E10-R009 at 986b1f7 (clean tree): 448 of 448 checks pass. R008 is
  marked superseded.

**Saw:**
- The R008 pilot missed four of main's families (oct, regional, rot47,
  uesc). The matched draw covers all 20.
- 14 of main's blind spots are new cells, including 7 of its 10 hard ones.
  Their tier labels are guesses, which is why the R002 bar matters.
- The grammar has 31 families, not 30 as written on 2026-10-27.

**Reviewed:** D-016 (#25) is agreed. Note for the limitations: L3 mixes AWQ
(Qwen, Llama) with bitsandbytes (Granite), so family is partly confounded
with quantisation method.

**Next:** Kushal reviews this PR (four-eyes rule). Then R002 runs on the new
pilot.


## 2026-10-29: E08-R011, vLLM cannot serve Gemma 2 on a T4; transformers backend; E08-R012 registered

Kushal.

**Did:**
- Ran E08-R011 on Kaggle at 5d14e24 (clean tree), 0.02 GPU-h, after fixing
  the HF_TOKEN secret (it held notebook code, hence R010's 401).
- Closed R011 as failed (design). Added `crsafety.llm.hf_server`: an
  OpenAI-compatible server on transformers (eager attention), batching
  requests that arrive together. The registry's Gemma-2-2B candidate is now
  `"backend": "transformers"`, and `Server` starts the right server. The
  client, cache and scaffolds are unchanged. The backend goes into the cache
  identity only when it is not vLLM, so existing keys stay valid.
- Tested on CPU with a 2-layer random Gemma 2 that has the soft caps:
  greedy alone equals greedy in a batch, logprobs, a system role gives a 400,
  and an over-long prompt gives a 400.
- Registered E08-R012: the same serving check for Gemma-2-2B on the new
  backend (runbook K7, notebook cell 5).

**Saw:**
- Gemma-2-2B downloaded and loaded in fp32, then vLLM stopped:
  "FlexAttention does not support logits soft cap yet".
- With R008/R009 (fp16 refused; Triton fp32 needs 80 KB of shared memory)
  and FlashInfer having no fp32, no vLLM 0.19.1 attention backend serves
  Gemma 2 on a T4.

**Next:** E08-R012 on Kaggle, then pin Gemma-2-2B. Its S6 throughput says
whether the E09 interview budget fits on transformers. Not on the Nov 10
path.

## 2026-10-29: E08-R012, Gemma-2-2B pinned on the transformers backend; H3 done for the pilots and the E09 base

Kushal.

**Did:**
- Ran E08-R012 on Kaggle at 0c9f8f1 (clean tree, PR #29 merged), 0.05
  GPU-h. It succeeded.
- Added Gemma-2-2B-it to `configs/llm/pins.json`: revision 299a856, fp32,
  `backend: transformers`, transformers 5.16.1.

**Saw:**
- Loads in 58 s at 10.2 GB. S2 7/8 with finite logprobs. The S3 cache
  replay was identical. S4 recalled the code word at 4.4k tokens.
- S5: the system role is refused (HTTP 400). This is expected for Gemma 2
  and not required for the organism base.
- S6: 121 tok/s at 32 concurrent, on par with vLLM AWQ 7B (112–116), thanks
  to batching.
- S7: 0/8 seeded sampled requests reproduce across batches (one seed per
  batch), against 7–8/8 on vLLM. For E09 the cache is the only record of a
  generation.
- Pinned now: Qwen2.5-7B, Mistral-7B, Llama-3.1-8B, Granite-3.3-8B and
  Gemma-2-2B-it. That covers the E08-R001 and E10-R002 pilots (Nov 10) and
  the E09 base, ahead of H3's Nov 5 due date.

**Next:** pin the judge (Phi-4, Phi-4-mini or OLMo-2-7B) before the E08
judge κ check. E09 organisms use the same backend as merged checkpoints.
