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

