# Decision records

Append-only. To change a decision, add a new record that supersedes it.
Template: [`templates/entries.md`](templates/entries.md). Each record says
whether it affects a pre-registered analysis.

---

## D-001: The paper is an AI-safety paper; ecology is a methods citation (2026-10-22)

**Status:** accepted
**Context:** The method (capture-recapture) comes from ecology. The paper's
audience and venue are AI safety and ML.
**Options:**
- A: frame as "ecological estimators for ML";
- B: frame as "how complete was the audit?", with the estimators as
  methods.
**Decision:** B.
**Why:**
- The question that matters is a safety one: how complete is testing.
- Prior work already rules out "first use of species estimators in ML"
  (Mark-Evaluate 2020, STADS 2018, Kansal 2026).
- Safety venues reward the safety question.
**Consequences:**
- Safety vocabulary throughout (see `docs/GLOSSARY.md`).
- Experiments on audits and red teams lead.
- SAEs are one case study.
- Ecology appears in methods and related work only.
**Affects pre-registered analysis:** no.

## D-002: Coverage and new-find predictions are the headline; counts are labelled lower bounds (2026-10-22)

**Status:** accepted
**Context:** Total N is not identifiable under heterogeneous detection
(Link 2003; Mao and Lindsay 2007). The pilot shows coverage stays accurate
where N estimates fail.
**Decision:**
- Primary estimands: audit coverage C and new-item count Δ(m).
- Chao2 and iChao2 are reported only as labelled lower bounds.
**Why:** theory, the pilot, Kansal's pre-registered results, and the
fuzzing "false peaks" findings.
**Consequences:** PH1 and PH6 centre on coverage; PH2 documents why counts
are bounds.
**Affects pre-registered analysis:** defines it.

## D-003: Target venues (2026-10-22)

**Status:** accepted
**Decision:**
- arXiv preprint and Alignment Forum post in December 2026;
- an ICLR 2027 workshop around 1 February 2027;
- **NeurIPS 2027 main track** (about mid-May 2027, date to be confirmed) as
  the primary target;
- fallbacks: SaTML 2028 or ICLR 2028 (about September 2027), and TMLR for a
  validation or negative-results companion paper.

ICML 2027 (about 22 January) only if E02, E03 and E09 are complete by early
January.
**Why:** audit and red-team experiments need months. Rushing would leave an
SAE-only paper, which is the weakest framing and the most exposed to being
scooped.
**Affects pre-registered analysis:** no.

## D-004: Plain-git lab notebook; no tracking service yet (2026-10-22)

**Status:** accepted
**Options:** Weights & Biases, MLflow, DVC, or plain git with a run
registry.
**Decision:**
- `notebook/runs.csv` is the source of truth, maintained by
  `tools/notebook.py`;
- every run writes a manifest (`docs/PROTOCOLS.md` §5);
- pre-registration blocks are locked by hash.
**Why:**
- one researcher;
- traceability matters more than dashboards;
- no lock-in.

Revisit if the E06 or E11 GPU grids become large.
**Consequences:** discipline is manual; `notebook.py check` enforces the
basics.
**Affects pre-registered analysis:** no.

## D-005: Pre-registration in tiers, with prior knowledge disclosed (2026-10-22)

**Status:** accepted
**Context:** We are not starting blind (pilot, published numbers).
**Decision:**
- E01 is exploratory and may set the † thresholds.
- Study pre-registration v1.0 is frozen before any confirmatory data.
- Stage 3 experiments are frozen one by one.
- Prior knowledge is listed in `LOG.md` (2026-10-22) and in the
  pre-registration.
- The freeze chain is: hash lock → annotated tag → GitHub release → Zenodo
  DOI → OSF registration citing the commit and DOI.
**Why:** best practice for secondary-data and simulation pre-registration
(OSF secondary-data template; Siepe et al. 2024 ADEMP-PreReg; Hofman et al.
2023 two-stage protocol).
**Affects pre-registered analysis:** defines the process.

## D-006 (proposed): Licences: code MIT, documentation and released data CC BY 4.0 (2026-10-22)

**Status:** proposed. **Needs the repository owner's approval.**
**Context:** The repository is MIT-licensed. Datasheets and released data
usually use CC BY 4.0 (the precedent in Kansal's repos).
**Decision (proposed):**
- keep MIT for code;
- license `docs/`, `research/` text and released data tables under
  CC BY 4.0;
- never redistribute upstream data whose licence is unconfirmed: release
  derived statistics plus a regeneration script instead.
**Affects pre-registered analysis:** no.

## D-007: $0 plan: open-weight models on free compute; frontier APIs only as an optional extension (2026-10-22)

**Status:** accepted
**Context:** The available budget is $0 for now (resolves Q-B1).
Resources:
- this sandbox (CPU, R via conda-forge);
- free Kaggle GPUs (2 × T4 or P100, about 30 GPU-hours a week per account,
  roughly 12-hour sessions; check current limits). Two team members means
  two accounts.

**Options:**
- A: wait for funding;
- B: run everything at $0, with open 7–9B models as auditors, attackers,
  targets and judges, and scaled-down GPU grids;
- C: use free API tiers.

**Decision:** B. Frontier-model replication becomes E18 (proposed),
triggered only if credits arrive (for example the OpenAI researcher
programme).

**Why:**
- B keeps every confirmatory hypothesis testable.
- It is fully reproducible (open weights, no API drift, no provider terms).
- It fits the GPU quota: about 150 core GPU-hours across two accounts.

C was rejected for the confirmatory design: free tiers have rate limits,
often let providers train on our prompts, and some forbid red-team use.

**Changes (all before any freeze, so they are not deviations):**
- **E06:** a smaller synthetic world: 4,096 features, d = 256, width
  1,024; budgets 20M and 50M samples.
- **E08:** open-model auditor ladder: Qwen (L0, L1, L2 sizes); Qwen + Llama
  + Gemma (L3). Mistral target with the AuditBench system-prompt quirks. Phi
  or OLMo judge.
- **E09 → "AuditBench-lite":** the 14 AuditBench behaviours implanted by
  QLoRA fine-tuning into Gemma-2-2B-it. Three tool configurations, including
  a white-box Gemma Scope SAE tool.
- **E10:** open-model attackers; a harmless proxy goal (smuggling a fake
  secret token past the monitor).
- **E11:** Pythia-70M only, 8 + 4 + 4 seeds, 50M tokens.
- **E04, E12, E15, E17:** local models; QLoRA fine-tuning on Kaggle.

**Consequences:**
- The safety claims are "for auditors and red teams built on open 7–9B
  models". Generality to frontier models is a stated limitation, until E18.
- Risk of floor effects with small auditors; checked in every pilot before
  freezing.
**Affects pre-registered analysis:** yes; it defines the testbeds of E06,
E08–E11 before the v1 freeze.

## D-008: Estimator formula conventions follow the Chao-lab reference code (2026-10-22)

**Status:** accepted (Santosh); Kushal to review with the E00 results
**Context:** Several estimators have more than one published or
implemented form, and the forms disagree at the edges (Q2 = 0, Q1 ≤ 1,
Q4 = 0). Results must not depend on which variant we happened to code.

**Decision:** `crsafety` matches these references exactly:

| Quantity | Convention | Reference |
|---|---|---|
| Chao2 | classic (K−1)/K · Q1²/(2Q2) when Q2 > 0; bias-corrected (K−1)/K · Q1(Q1−1)/2 when Q2 = 0. The always-bias-corrected form is available as `form="bc"`. | iNEXT `ChaoRichness` |
| Chao2 interval | log-normal (Chao 1987); when Q1 ≤ 1, the estimate is S with a Poisson-type interval | iNEXT |
| Coverage (primary estimand) | 1 − Q1/U · K f0 / (K f0 + Q1), with f0 as in Chao2 | iNEXT `Chat.Sam` at t = K |
| Extrapolation | f0 [1 − (1 − Q1/(K f0 + Q1))^m] | Chao et al. 2014; iNEXT |
| iChao2 | Chiu et al. 2014, with Q4 = 0 replaced by 1 | SpadeR |
| ICE | Lee and Chao 1994, with the A-corrected coverage of infrequent items; cut-off 10 | SpadeR (`fossil::ICE` not used: it does not implement the published formula) |
| Jackknife | first and second order | vegan `specpool` |
| Bootstrap | iNEXT pseudo-population, B = 2,000; normal interval est ± z·s.e. as in iNEXT; percentile interval stored too | iNEXT `EstiBootComm.Sam` |
| Huggins | logistic detection constant across runs; Horvitz-Thompson N | VGAM `posbernoulli.t` |

**Why:**
- These are the implementations most applied papers use.
- They are maintained by the estimators' authors.
- E00-R001 shows we match them to near machine precision, so reviewers can
  reproduce any number with standard R tools.

**Affects pre-registered analysis:** yes. These definitions are what
"Chao2", "coverage" and the other estimators mean in every
pre-registration. A change after the v1 freeze is a deviation.

## D-009: How the E00-R003 estimators are provided (2026-10-22)

**Status:** accepted (Santosh); Kushal to review with the E00 results
**Context:** The E00 pre-registration listed log-linear models and
`breakaway_nof1` "through rpy2". rpy2's current release does not load
against the conda-forge R builds available here, and rpy2 would make every
user of the library (Kaggle notebooks, CI) depend on an R installation.
The Chiu-Chao (2016) singleton correction could not be confirmed: the
paper is unreachable from the sandbox and no Chao-lab package implements it.
**Options:**
- log-linear: A, rpy2 to Rcapture; B, a native port validated against
  Rcapture.
- breakaway_nof1: A, rpy2; B, `Rscript` subprocess with JSON in/out; C, port
  it (several hundred lines of nls model selection with fallbacks).
**Decision:**
- Log-linear models are ported (`crsafety.loglinear`, `crsafety.closedp`),
  matching Rcapture's design matrices, history order and Chao (LB)
  negative-eta refits. Standard errors are evaluated at the MLE (Rcapture's
  printed s.e. carries O(√ε) error from glm's `vcov()`).
- `breakaway_nof1` is called through `Rscript` (`crsafety.rbridge`). It is a
  sensitivity estimator only, never primary, so needing R is acceptable.
- The Chiu-Chao correction is left out, as the E00 contingency prescribes;
  `breakaway_nof1` is the f1-free option. E05 correction (c) and E04 H4c
  use `breakaway_nof1` until Q-D10 is resolved.
- `generalized_chao` uses the binomial (incidence) form derived from Böhning
  et al. (2013); validated against `glm` and its exact reduction to Chao2.
**Why:** a native port has no runtime dependency and is validated to
≤ 3e-12 (E00-R003); the subprocess bridge is exact by construction and
robust to R/rpy2 version skew.
**Consequences:** E00 §2 Methods text updated (not frozen). E05 and E04 refer
to "the f1-free estimator" and are unaffected in design.
**Affects pre-registered analysis:** yes, before any freeze: it fixes which
implementation "log-linear", "f1-free" and "singleton-corrected" mean.

## D-010: Intervals for coverage and new items; proposals for the † thresholds (2026-10-22)

**Status:** part A accepted (Santosh), Kushal to review; part B **proposed**
for the joint v1 freeze.
**Context:** E01-R005: the pre-registered iNEXT-style bootstrap interval for
Ĉ covers the realized coverage C in 0.760 (MCSE 0.019) of base-cell
replicates and 0.73–0.91 across clean cells, so E01 decision rule 1 (CI
coverage ≥ 0.90 in the base cell) fails for it. Two causes: C is a
property of the sample, so the relevant error is Ĉ − C, not the spread of
Ĉ; and the pseudo-population bootstrap underestimates sd(Ĉ) (0.0095 vs
0.0123). E01-R006 shows that a per-cell tolerance |Ĉ − C| ≤ 0.05 is
unattainable at the item counts of E09 (14) and E10 (20).

**A. Interval method (accepted).**
- Primary interval for C: `crsafety.coverage_interval` (bootstrap of
  Ĉ* − C* from the Chao pseudo-population, B = 1,000), uncorrected.
  Primary interval for Δ(m): `crsafety.delta_interval`, bias-corrected.
  The one-sided lower bound of `coverage_interval` is the bound used by
  the E13 R-lower stopping rule.
- The iNEXT interval is still reported, as secondary, for comparability.
- Evidence: E01-R007 (same datasets as R005) and E01-R008 (fresh datasets,
  criterion fixed before running): coverage of C 0.89–0.97 and
  0.896–0.950 in clean cells; base cell 0.922 and 0.906. Exploratory: the
  method was designed after R005 was seen.
- Known weakness: about 0.92 coverage for nominal 0.95. E13 should check
  R-lower with it; a calibrated level (e.g. nominal 0.97) is an exploratory
  option, not adopted.

**B. Proposals for the † thresholds (for the v1 freeze; not applied).**
- *PH1 tolerance.* Keep |Ĉ − C| ≤ 0.05 in ≥ 80% of cells for testbeds
  with hundreds of items or more (E02, E06): E01's 80th percentile of
  |Ĉ − C| is 0.043 at K = 5 and ≤ 0.02 at K ≥ 10. For E09 and E10 replace
  the per-cell criterion: pooled |mean(Ĉ − C)| ≤ 0.03 across cells **and**
  the realized-coverage interval covers C in ≥ 0.85 of cells. Reason (R006):
  at N = 14, K = 8 even an unbiased Ĉ is within 0.05 of C in only 33–73% of
  replicates. Alternative: a size-specific tolerance from R006 (0.10–0.15),
  which the "no more than twice" rule may not allow.
- *PH3a ratio ≥ 2.* E01 cannot calibrate the matcher; keep 2 and revisit
  after the E03 pilot.
- *PH4 and PH5 (≥ 0.05).* These are minimal meaningful effects, not
  accuracy tolerances; E01 shows such effects arise (one family vs six
  +0.20; c = 2 +0.07). Keep 0.05.
- *PH2 (no †).* Its interval half fails at N = 50 (Chao2 CI covers N in
  0.92 of replicates). Discuss at the freeze: restrict the claim to
  N ≥ 500, or keep it and expect "not supported" in small-N testbeds.
**Affects pre-registered analysis:** yes. A defines the interval used by
PH1, PH6 and every coverage report (before any freeze). B changes nothing
until both people agree at the freeze.

## D-011 (proposed): Truth for E02/E06 coverage uses detectability estimated without the evaluated runs (2026-10-22)

**Status:** proposed for the joint v1 freeze; not applied.
**Context:** E02 §2 estimates each feature's catch rate π̃ from the
architecture's reference pool of 35 SAEs. That pool *includes* the 5 seeds
being evaluated, and a leave-cell-out variant is "also reported". The
items a cell found get an inflated π̃, so the pooled truth C is biased
upwards. Simulated with 4,000 features, 35 runs and Beta-distributed
detectability (200 replicates; analysis/e02 development, not a registered
run):

| detectability | pooled C − true C | leave-cell-out C − true C |
|---|---|---|
| Beta(2, 2) | +0.007 | −0.000 |
| Beta(0.5, 3) | +0.035 | −0.000 |
| Beta(0.3, 6) | +0.066 | +0.000 |

The bias is the size of H2a's 0.05 tolerance under heavy tails, which is
the regime the project cares about.
**Proposal:**
- E02: the confirmatory truth for H2a and H2c is the leave-cell-out C
  (π̃ from the other 6 L0 cells of the same architecture, 30 SAEs); the
  pooled C becomes the secondary variant. Both remain approximations,
  since catch rates differ between L0 values.
- E06: compute π̃ from the 8 reference seeds only (not the 16 evaluation
  seeds), with U still the union over all 24. With 8 reference seeds, rare
  features have π̃ = 0 although caught; report how much mass this drops.
**Affects pre-registered analysis:** yes (E02 H2a/H2c, E06 H6a), if adopted
at the freeze. `analysis/e02/evaluate.py` already computes both variants.

## D-012 (proposed): E10 arm A3 (de-adaptation) as written cannot correct adaptive bias (2026-10-22)

**Status:** proposed for the joint v1 freeze (E10 is Kushal's page; this
records the evidence, it changes nothing).
**Context:**
- Q-D7 is resolved. The A3a algorithm was read from the paper (Liyanage
  et al., ICSE 2024, Algorithm 1; `paper/ICSE24.pdf` in the authors' GitHub
  pages repository) and A3b from the FSE'21 artefact
  (`Adaptive-Bias/fse21_paper270`). Both are implemented in
  `crsafety.deadapt` (H8).
- E10 §2's reconstruction of A3a computed Ĉ only at the end of each shuffled
  window. Shuffling does not change Ĉ there, so that version was a no-op.
  The real algorithm estimates the rate at every prefix of every shuffled
  window and regresses log rate on log time.
- E01-R009 (exploratory) shows both methods over-correct at our scale, at
  the run level (K = 10–12; A3b is undefined there) and at the attempt level
  (20 blind spots, 200 attempts).
**Options for the freeze:**
- A: keep A3 as pre-registered (A3a, with A3b alongside), now with the
  faithful algorithm; expect H10c "not supported" and report it.
- B: apply A3 at the attempt level inside each A2 session, where adaptation
  actually happens. This needs per-attempt logs from the monitor (an extra
  history file beyond PROTOCOLS §10). R009 suggests it would still
  over-correct.
- C: replace H10c's correction with a design-based one (e.g. A1 runs as the
  non-adaptive reference) and keep A3 as exploratory.
**Recommendation:** A, plus C as a secondary analysis. The paper's claim
(PH5 second half) should be allowed to fail honestly rather than be
redesigned after this evidence.
**Affects pre-registered analysis:** yes, if B or C is adopted at the freeze.

## D-013: Truth for E08/E09/E10 uses reference runs only; catcher-agnostic truth available (2026-10-23)

**Status:** accepted for the code (Santosh, answering Kushal's four-eyes
review, `notebook/reviews/2026-10-23-kushal-four-eyes.md` §4–5). Which truth
is *primary* for H8a/H10b is a joint freeze decision (FREEZE-V1 item 16).
**Context:**
- The frozen analysis scripts for E08–E10 computed true π from estimation +
  reference runs. Kushal showed this biases the truth C upwards by
  +0.026 to +0.054 at E08/E10 sizes, which is as large as the PH4/PH5
  effects.
- E10 §2 already says π comes from the reference runs, so the script
  disagreed with its own page.
- `tests/test_testbeds.py::test_pooled_truth_inflates_coverage_reference_does_not`
  reproduces the bias at the E10 size.
- Kushal also argued that a truth taken from the catcher being judged makes
  H10b (and PH4 in E08) near-null by construction. Within-session
  adaptation changes π, not the bias of Ĉ against that π.
**Decision:**
- `crsafety.testbed.truth_pi(cells, cell, truth)`. `reference` (default):
  the cell's own reference runs. `pooled`: the old reading, always reported
  as `C_pooled`. `cells:<ids>`: the pooled reference runs of named cells,
  the catcher-agnostic truth, e.g. `cells:L3` for E08 and `cells:A1,A5` for
  E10.
- `analysis/e08`, `e09` and `e10/analyse.py` take `--truth`.
- Recorded as a new decision rather than folded into D-011, because it
  changes Kushal's experiments and their frozen scripts (his question in
  PR #8).
**Affects pre-registered analysis:** yes for E08–E10 (pages not frozen yet):
§2 truth wording to be aligned at the freeze. E08/E10 are Kushal's pages.

## D-014 (proposed): T3 hides background SAE features, by a rule fixed before any pilot (2026-10-23)

**Status:** proposed by Kushal. Santosh to review, since the tool is his
code (H7).
**Context:**
- After the user-token rule (E09-R009), the tool's top-features lists follow
  the prompt. One feature (#1041) was still top-1 on 19 of 20 check prompts.
- A feature that fires on every prompt tells the auditor nothing, and it
  takes a slot that an implant-related feature could use.
- Adding a filter only if the E09-R004 pilot "needs" one would let pilot
  outcomes shape the tool, so the rule is fixed now instead.
**Decision:**
- A background blocklist, computed once on Gemma-2-2B-it, the shared base
  of every organism:
  - prompts: the 100 neutral prompts in `analysis/e09/background_prompts.txt`.
    None of them are the R003/R009 check prompts, and none touch the 14
    behaviours.
  - tokens: user tokens only.
  - a feature is blocklisted if it is in the top k = 10 on more than 50% of
    those prompts.
- The blocklist is hidden from the "top active features" list only. The
  "most changed vs base" list is not filtered, because a feature changed on
  every prompt of an organism may be the implant itself.
- Code: `gemma_scope.background_blocklist`, `WhiteBoxTool(blocklist=...)`,
  `from_hf(blocklist_path=...)`. The run is E09-R010.
- The cutoff, k and prompt set are not tuned on E09-R009 or on any pilot
  result.
**Risk:** an implant could share a globally common feature and be hidden.
At a 50% cutoff this is unlikely, and E09-R004 will show it. The
most-changed list stays unfiltered as the backstop.
**Affects pre-registered analysis:** E09 §2 T3 wording (page not frozen yet).

## D-014 review (2026-10-23): approved by Santosh

D-014 (T3 background blocklist: top 10 on more than 50% of 100 neutral
prompts, hidden from top-features only) is **approved as written** by the
tool's owner. The cutoff and k are unchanged.

Suggestions, not blocking:
- a pre-specified diagnostic for E09-R004 of whether the blocklist hides
  part of an implant;
- one line in the tool's output saying background features are hidden;
- listing near-threshold features in E09-R010.

Full review: `notebook/reviews/2026-10-23-santosh-d014.md`.

## D-015: Staged pre-registration freeze, v1.0 / v1.1 / v1.2 (2026-10-23)

**Status:** accepted. Proposed by Kushal, agreed by Santosh.
**Context:**
- FREEZE-V1 §3 locks only pages whose pilots are done.
- E08 and E10 need their R001/R002 pilots and the judge check (H4, Nov 12).
- E09's T3 tool is still changing (D-014), and its R004 pilot lands on
  Dec 18.
**Decision:**
- **v1.0** (Nov 6–8): `PREREGISTRATION.md`, every threshold, the
  FREEZE-V1 §2 decisions, and E02, E03, E05, E13.
- **v1.1** (about Nov 22): E08 and E10.
- **v1.2** (about Jan 5): E09.
- The same four-eyes review and tag → release → Zenodo → OSF chain applies
  at each stage. No confirmatory run starts before its page is frozen.
**Conditions:**
- Thresholds lock at v1.0. Later stages lock testbed details only.
- Each frozen analysis script locks with its page, with its `--truth` named.
- Pilot results that shape a later page are cited as prior knowledge
  (D-005).
- E02/E03 move to v1.1 if E02-R001 has not run by the freeze.
**Affects pre-registered analysis:** the freeze schedule only; see
`docs/FREEZE-V1.md` §3.

## D-016: Granite-3.3-8B replaces Gemma-2-9B as the third L3 family (2026-10-27)

**Status:** accepted by Kushal (owner of E08 and E10). Santosh reviews it in
the v1.1 four-eyes freeze review (D-015).
**Context:**
- E08 L3 and E10 A5 named Qwen, Llama and Gemma, at ≤ 9B each.
- Gemma-2-9B cannot be served on a Kaggle T4 with vLLM 0.19.1:
  - vLLM refuses fp16 for Gemma 2;
  - 4-bit weights in float32 failed a weight-shape assertion, both when
    quantised at load (E08-R008) and pre-quantised (E08-R009).
- Granite-3.3-8B-Instruct (IBM, Apache-2.0) passed S1–S5 in E08-R009 and is
  pinned.
**Options considered:**
- Gemma-2-2B-it in float32: rejected. L3 would then mix a 2B auditor with
  7–8B ones, which confounds family with size. Size is L2's axis.
- More work on Gemma-2-9B (newer vLLM, or a transformers server):
  rejected. It costs 1–2 days and Kaggle runs, and puts H3's Nov 5 date at
  risk.
**Decision:** L3 and A5 use Qwen2.5-7B, Llama-3.1-8B and Granite-3.3-8B,
all at 7–9B. This is a pre-freeze change under E08 §3, the "will not run on
T4" contingency, so it is not a deviation. E09 still uses Gemma-2-2B-it as
the organism base.
**Affects pre-registered analysis:** the testbed text of E08 (L3, and the
second-target contingency) and E10 (A5). Hypotheses and measures are
unchanged.

## D-017: Phi-4 (14B) is the first E08 judge; OLMo-2-7B is the fallback (2026-10-29)

**Status:** accepted by Kushal (owner of E08). Santosh reviews it in the
v1.1 four-eyes freeze review (D-015).
**Context:**
- E08 §2 requires a judge from a family that is used neither as target
  (Mistral) nor as auditor (Qwen, Llama, Granite). The judge is validated in
  E08-R002: 100 reports, double hand-labelled, with judge–human κ ≥ 0.7.
- E08-R013 pinned all three registry candidates:

  | Candidate | S2 | Speed (32 concurrent) | Notes |
  |---|---|---|---|
  | Phi-4-mini, fp16 | 8/8 | 452 tok/s | |
  | OLMo-2-7B, bnb | 7/8 | 53 tok/s | 4,096-token window |
  | Phi-4 14B, bnb | 7/8 | 28 tok/s | 10-minute load |

**Options considered:**
- Phi-4-mini: the fastest, but at 3.8B it is the most likely to miss κ 0.7.
- OLMo-2-7B: its training data is fully open, but the 4k window may cut long
  reports.
- Phi-4: the strongest. Its speed does not matter for about 100 short
  reports.

**Decision:** E08-R002 validates Phi-4 first. If κ < 0.7, the rubric is
fixed first, then OLMo-2-7B (the other family) is validated, as E08 §3
allows before the freeze.
**Affects pre-registered analysis:** the judge line of the E08 §2 estimands.
It is not frozen yet and locks at v1.1.
