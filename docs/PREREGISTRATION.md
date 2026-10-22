# Study pre-registration

**Title:** How complete was the audit? Estimating what red teams, auditors and
interpretability tools miss.

**Version:** v0.2 (draft). **Status:** not frozen.

**Freeze plan.** v1.0 is frozen after the Stage 1 simulation study (E01) and
before any confirmatory data is collected (target: 6 November 2026). Git
timestamps are self-reported, so the freeze uses a chain of external
anchors:
1. Lock the Stage 2 experiment blocks whose pilots are complete (E02, E03,
   E05, E08, E10): `tools/notebook.py freeze EXX`, each reviewed by the
   other researcher. Experiments whose pilots come later (E06, E09, E13 and
   Stage 3) are frozen one by one, after their pilot and before any
   confirmatory run. Each lock is a later commit referring back to v1.0.
2. Commit with no results in the tree.
3. Annotated tag `prereg-v1.0` (signed if a key is available).
4. Create a GitHub Release on that tag. Zenodo archives the release and
   mints a DOI; the DOI exists only after the release.
5. Create an OSF registration citing the commit SHA and the Zenodo DOI.

Changes after the freeze go in
[`../notebook/DEVIATIONS.md`](../notebook/DEVIATIONS.md) and a new version
(`prereg-v1.1`). A frozen version is never edited.

Structure follows the OSF preregistration template plus the OSF
secondary-data questions on prior knowledge. Simulation parts follow ADEMP
(Morris, White and Crowther 2019; ADEMP-PreReg, Siepe et al. 2024).

## 0. Prior knowledge (what we had seen before freezing)

This is not a blind start. Before v1.0 we had seen:
- the pilot simulation results (`pilot/results.md`);
- published figures from Paulo and Belrose, Ghosh et al., Kansal's two
  studies, AuditBench (headline success rate only) and SLEIGHT-Bench.

We had **not** seen any SynthSAEBench SAE weights, any AuditBench run output,
or any output of the E10 monitor.

These design choices were informed by the prior knowledge:
- coverage, not N, as the primary estimand;
- K ≥ 6 runs;
- identity matching treated as measured;
- dependence and adaptivity built into the design.

Full record: [`../notebook/LOG.md`](../notebook/LOG.md) (2026-10-22).

**Guarding against biased comparisons** (Pawel, Kook and Reeve 2024):
- The grids, competitor estimators and performance measures are fixed
  before the confirmatory runs.
- Every estimator gets the same tuning budget (none).
- All cells are reported.
- The design includes scenarios where coverage is *expected* to fail:
  adaptive runs, same-model catchers, an uncatchable class, and identity
  errors.

---

## 1. Study information

### Research question

When a safety discovery tool (an alignment audit, a red team, an
interpretability method) is run several times, can the overlap between runs
tell us how much it has missed? Specifically:

1. Is **audit coverage** (the share of detectable failure mass already found)
   estimable accurately from repeated runs, where the **number** of missed
   failure modes is not?
2. What breaks the estimates in AI-safety settings: matching errors, catchers
   that share a base model, or adaptive search? Can each be detected and
   corrected?
3. Can the estimates support a practical decision: when to stop auditing?

### Why this matters

Labs and evaluators make deployment decisions on "we tested it and found N
issues". No current method says how complete that testing was. This study
validates a way to report "we found N, coverage is C, and K more runs would
find about m more", and maps when that report can be trusted.

## 2. Definitions

| Term | Definition |
|---|---|
| **Catcher** | One configuration of a discovery tool: SAE architecture and settings, auditor agent and its tools, red-team attacker and its prompt. |
| **Run** (occasion) | One independent execution of a catcher, producing a set of findings. |
| **Item** (individual) | A distinct failure mode, feature, behaviour or attack strategy, as defined by the identity rule. |
| **Identity rule** | The procedure that decides when findings from two runs are the same item (the matcher plus its threshold). |
| **Oracle history** | Item-by-run detection matrix built from the true identity (available only in testbeds with known truth). |
| **Matched history** | The same matrix built by the identity rule without access to the truth. |
| **Detection probability** π_i | Probability that one run of the catcher finds item i. |
| **Catchable population** U | Items with π_i > 0 for this catcher class at this budget. In testbeds, approximated by the union over a large reference pool of runs (at least 50) or known by construction. |
| **Audit coverage** C(K) | Σ_{i found in K runs} π_i / Σ_{i ∈ U} π_i: the probability that an item found by a new run was already found. Chao-Jost incidence coverage estimates this. |
| **New-item count** Δ(m) | Expected number of items first found when m more runs are added. |
| **Richness** N | \|U\|, the number of catchable items. Also reported: N_all, all items including uncatchable ones, when known. |
| **Lower-bound target** N_LB | The value of Chao2 computed from expected frequency counts. It is what Chao2 estimates, and is ≤ N under heterogeneity. |
| **Adaptive catcher** | A catcher whose later queries depend on earlier outcomes within a run (for example, it sees monitor verdicts). |

## 3. Hypotheses

### Primary (confirmatory)

Thresholds marked † are provisional. They may be revised once, after E01, and
fixed at the v1.0 freeze. Each revision and its reason goes in the changelog
below.

| ID | Hypothesis | Experiments | Supported if | Not supported if |
|---|---|---|---|---|
| **PH1** | **Coverage is estimable.** With independent, non-adaptive runs and oracle identity, estimated coverage is close to true coverage. | E02, E06, E09, E10 (non-adaptive arm) | \|Ĉ − C\| ≤ 0.05† in ≥ 80%† of pre-specified evaluation cells (lower 95% bound of the share ≥ 70%) | Upper 95% bound of the share < 80% |
| **PH2** | **Counts are only lower bounds.** Under heterogeneous detection, richness estimators fall below N, and their standard intervals do not cover N. | E01, E02, E06, E09 | Chao2 < N in ≥ 90% of cells with CV(π) ≥ 1, **and** log-normal Chao2 95% CIs cover N in < 50% of those cells | Either condition fails |
| **PH3** | **Identity errors dominate, and can be partly corrected.** (a) Matched histories give larger coverage and richness errors than oracle histories. (b) At least one correction recovers most of the injected-error bias. | E02, E03, E05 | (a) median ratio \|error_matched\| / \|error_oracle\| ≥ 2† at the default matcher; (b) a correction cuts \|relative bias\| of Chao2 by ≥ 50% at false non-match rate 0.10 | (a) ratio < 1.25; (b) no correction reaches 25% |
| **PH4** | **Same-model catchers overstate completeness.** Runs that share a base model overlap more than runs from different model families, so they overestimate coverage. | E08 (and E01 simulation) | mean(Ĉ − C) at ladder level L0 (same model, seeds only) exceeds L3 (different families) by ≥ 0.05†, and n_eff/K is lower at L0 | Difference < 0.02 or reversed |
| **PH5** | **Adaptive red teams overstate completeness; de-adaptation corrects it.** | E10 | Adaptive arm: Ĉ − C ≥ 0.05†; de-adapted estimate reduces \|Ĉ − C\| by ≥ 50% | Adaptive bias < 0.02, or reduction < 25% |
| **PH6** | **A coverage stopping rule is reliable.** Stopping when the lower 95% bound of Ĉ reaches the target gives true coverage at or above the target. | E13 (on E02, E06, E09, E10 data) | True C ≥ 0.9 at stopping in ≥ 80% of campaigns for target 0.9; median runs saved vs a fixed maximum K ≥ 30% | Success rate < 70% |

### Secondary

| ID | Hypothesis | Experiment |
|---|---|---|
| SH1 | Tool types are complementary. In AuditBench, white-box and black-box tool configurations find partly disjoint sets of targets (log-linear interaction between tool families < 0). | E09 |
| SH2 | Planting known items into a real system calibrates detectability. Coverage calibrated with planted marks is within ±0.05 of the truth on held-out marks. | E15 |
| SH3 | Covariates help only when they explain detectability: Huggins/Böhning beat Chao2 with an oracle covariate, not with a noisy one. | E07 |
| SH4 | On real SAEs, coverage estimates are invariant (±0.05) to the sampling unit (seed vs width ladder, threshold within the plateau). | E11 |

Everything else is exploratory and labelled so.

## 4. Design plan

- **Stage 0 (infrastructure):** E00 estimator library, validated against
  reference implementations.
- **Stage 1 (exploratory simulation):** E01. Its results may set the †
  thresholds and choose the primary estimators, before the freeze.
- **Stage 2 (confirmatory, known truth):** E02, E03, E04, E05, E06, E08, E09,
  E10, E13.
- **Stage 3 (application and stretch):** E07, E11, E12, E14, E15, E16, E17.
  Each is frozen separately before it runs.

No human participants are involved, apart from the two researchers
hand-labelling findings to validate the judges.

**Compute:** every confirmatory experiment runs at $0 on open-weight models,
using this sandbox's CPU and free Kaggle GPUs (decision D-007). Auditors,
attackers, targets and judges are open 7–9B instruct models (or smaller),
pinned at the freeze. Replication with frontier API models is an optional
extension (E18), with its own pre-registration.

## 5. Sampling plan

- **Simulation cells:** n_sim = 500 replicates per cell. The Monte Carlo
  standard error (MCSE) of a 95% coverage probability is then
  √(0.95 × 0.05 / 500) ≈ 0.01. MCSE of bias is SD(θ̂)/√n_sim, and is
  reported with every bias.
- **Synthetic SAE cells:** K = 5 seeds (released zoo) and K = 16 seeds (our
  own). Cells are listed in E02 and E06.
- **Audits:** K = 16 runs per target per configuration (8 for estimation, 8
  as the reference pool). E08: 16 system-prompt organisms × 3 auditor
  levels. E09 (AuditBench-lite): 14 fine-tuned organisms × 3 tool
  configurations.
- **Red teams:** K = 12 attacker runs per arm, with M = 20 planted blind
  spots. The budget per run is fixed in E10 after a declared difficulty pilot
  on separate seeds.
- **Stopping rule:** evaluated on campaigns resampled from the runs above. No
  new data.

## 6. Variables

- **Estimators** (fixed in E00): Chapman (pairs), Darroch Mt, Chao2
  (bias-corrected), iChao2, jackknife 1 and 2, ICE, Chao-Jost incidence
  coverage, Chao et al. (2014) extrapolation. Also, where named in an
  experiment: Huggins / Böhning covariate models, log-linear models,
  f1-free estimators, and singleton corrections.
- **Intervals:** for coverage and Δ(m), the realized-coverage bootstrap
  (`crsafety.coverage_interval`, `delta_interval`; B = 1,000), which
  bootstraps the error Ĉ* − C* from the Chao pseudo-population (D-010). Log-normal Chao interval for Chao2. Dependence-robust interval
  (Sun et al. 2023) where named.
- **Primary outcomes:** coverage error Ĉ − C; relative error of Δ̂(m); Chao2
  relative to N, N_LB and N_all; CI coverage of each target.

## 7. Analysis plan

- Each primary hypothesis is evaluated exactly as stated in its experiment
  page.
- Verdicts:
  - **supported:** the point estimate meets the threshold and the 95%
    interval (bootstrap over replicates or cells) does not cross the
    "not supported" line;
  - **not supported:** the estimate is on the wrong side and its interval
    excludes the threshold;
  - **inconclusive:** otherwise.
- All six primary hypotheses are reported whatever the outcome. No
  correction for multiplicity is applied to the verdicts, since they are
  estimation thresholds, not significance tests. The paper says so.
- Estimator failures (NaN or infinity) are counted and reported as a
  performance measure. They are not dropped.
- **Exploratory analyses** are reported in a separate, labelled section.
  They are never used to support a primary claim.

## 8. Inference criteria and transparency

- Every reported number links to a run ID in
  [`../notebook/runs.csv`](../notebook/runs.csv).
- Negative and null results are reported in the paper with the same
  prominence as positive ones.
- Code, configs, and the per-run detection matrices will be released.
  Attack payloads are not released (see [`DISCLOSURE.md`](DISCLOSURE.md)).

## Changelog

| Version | Date | Change | Reason |
|---|---|---|---|
| v0.1 | 2026-10-22 | First draft | — |
| v0.2 (draft) | 2026-10-22 | Interval method for C and Δ(m): realized-coverage bootstrap. † thresholds unchanged; proposals for the v1 freeze in D-010 (PH1 tolerance for E09/E10; PH2 at small N) | E01-R005: the iNEXT interval covers C in 0.76 of base-cell replicates (fails E01 decision rule 1); E01-R007/R008: 0.906–0.922. E01-R006: per-cell 0.05 unattainable at N = 14–20 |
