# E02: Coverage of SAEs on SynthSAEBench (released seed zoo)

| Field | Value |
|---|---|
| Status | registered |
| Tier | core |
| Stage | 2 confirmatory |
| Depends on | E00; E01 (freeze); data access to the zoo |
| Study hypotheses | PH1, PH2, PH3a |
| Testbed | SynthSAEBench-16k world (version: see Testbed) + `decoderesearch/synth-sae-bench-16k-v1-saes` |
| Compute | 1 small GPU or CPU; hours (activations from the generator) |
| Pre-registration | not frozen |

## 1. Question

Interpretability tools are one kind of safety audit. If we train the same
SAE several times, can the overlap between the runs tell us how much of the
model's feature mass we have found? Technical question: in a synthetic world
with 16,384 known features, do coverage and richness estimates from 5 seeds
match the truth, and how much of the error comes from matching rather than
from heterogeneity?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Test coverage and richness estimators against known truth on the released
zoo, and separate matching error from estimator error.

### Testbed
SynthSAEBench-16k: 16,384 unit-norm feature directions in d = 768.
- **Firing:** Zipfian, exponent 0.5, rescaled into p ∈ [5e-4, 0.4].
- **Structure:** a hierarchy (128 roots, branching 4, depth 3) and low-rank
  correlation (rank 25, scale 0.1).
- **Source of p_i:** the generator config (confirmed in code:
  `create_synth_bench_16k_model.py`).

The zoo has 5 architectures (standard L1, Matching Pursuit, BatchTopK,
Matryoshka BatchTopK, JumpReLU) × L0 ∈ {15, 20, …, 45} × 5 replicates at
width 4,096. That gives **35 cells × K = 5**, to be confirmed on download.

Facts that shape this experiment (from code inspection, 2026-10-22):
1. **The 5 replicates are uncontrolled.** The sweep script never passes the
   seed to the runner, so initialisation and the synthetic data stream both
   vary, jointly and unseeded. We treat them as independent replicates.
   They cannot separate initialisation effects from data effects (E06 does
   that).
2. **Misses here come from capacity, not sampling.** With p_min = 5e-4 and
   200M samples, even the rarest feature fires about 100,000 times in
   training. Missed features come from capacity (4,096 latents for 16,384
   features), absorption, hedging and splitting. So E02 tests the
   "structurally uncatchable" regime. The sampling-limited heavy-tail regime
   is tested in E06.
3. **World version.** v1 and v2 share feature directions, probabilities,
   correlation and hierarchy. They differ only in child magnitudes. The
   repo's sweep script trains on the v2-equivalent world (with
   `scale_children_by_parent=True`); the model card's naming suggests v1.
   **Decoder-based oracle histories are identical under both.** Any
   activation-based measure (M3 in E03, firing F1) is computed under both
   versions and reported with the version stated.

### Estimands
- **Catch rule (oracle).** True feature i is caught by SAE s if some decoder
  column has \|cos\| ≥ τ_gt = 0.7 with feature i's direction, under one-to-one
  Hungarian assignment (the GT-MCC procedure). Sensitivity values:
  τ_gt ∈ {0.5, 0.6, 0.8, 0.9}.
- **π_i** for each feature and cell is the empirical catch rate over the 5
  seeds. For the truth target only, it is also predicted from p_i by a
  logistic fit pooled across cells (exploratory; see analysis).
- **U (catchable).** Features caught by at least one SAE of the same
  architecture across all 7 L0 values × 5 seeds (35 SAEs, the reference
  pool). Also reported: N_in = 4,096 and N_all = 16,384.
- **True coverage C(K).** Σ_{caught in K seeds} π̃_i / Σ_{i∈U} π̃_i. Here π̃_i
  is estimated from the reference pool, which includes the K seeds being
  evaluated, so a leave-cell-out variant is also reported.
- **Δ(m).** Checked by leave-one-seed-out: from 4 seeds, predict the new
  features found by the 5th.

### Methods
- **Two histories per cell:**
  - **oracle:** each SAE's latents mapped to true features by the catch rule;
  - **matched:** latents matched across seeds with no truth. Default matcher
    M1 is Hungarian on \|decoder cosine\| at τ = 0.7, with clusters formed as
    connected components across seeds. A cluster is a single item.
- **Estimators:** the primary set from E01, and Chapman for every seed pair.
- **Preprocessing:**
  - dead latents (never firing on 10^6 samples) are dropped;
  - duplicate latents within an SAE (\|cos\| ≥ 0.95, including antipodal
    pairs) are merged.

### Performance measures
- Ĉ − C;
- relative error of Chao2 against \|U\|, N_in and N_all;
- leave-one-out Δ prediction error;
- ratio of matched to oracle error.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H2a (→ PH1) | Oracle-history coverage is accurate | \|Ĉ − C\| per cell | ≤ 0.05† in ≥ 80% of 35 cells | < 70% of cells |
| H2b (→ PH2) | Chao2 is a lower bound for the catchable set and far from N_all | Chao2 vs \|U\| and N_all | Chao2 < \|U\| in ≥ 90% of cells and < 0.5 N_all in all cells | otherwise |
| H2c (→ PH3a) | Matching adds more error than heterogeneity | median \|err_matched\| / \|err_oracle\| for Ĉ | ≥ 2† | < 1.25 |
| H2d | Leave-one-seed-out prediction of new features is accurate | median relative error of Δ̂(1) | ≤ 20% | > 40% |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Download, checksum and inventory zoo; verify seeds, widths, L0; verify world version | 1 | < 1 h |
| R002 | Oracle histories, all cells, τ_gt sweep | 35 cells | 1 to 3 h |
| R003 | Matched histories (M1), all cells | 35 cells | 1 to 3 h |
| R004 | Estimators and evaluation | 35 cells | minutes |

### Sample size
Fixed by the zoo: 35 cells × 5 seeds. Cell-level shares get a Wilson 95%
interval. The bootstrap resamples seeds within cells.

### Analysis plan
- **Confirmatory:** H2a to H2d at τ_gt = 0.7 and M1 at τ = 0.7.
- **Secondary:** τ_gt sensitivity; results by architecture; the
  hierarchical (10,880) and non-hierarchical (5,504) features analysed
  separately.
- **Exploratory:** the catch-probability vs p_i curve (input to E07 and E15);
  whether Matching Pursuit SAEs, which exploit superposition noise, behave
  differently.

### Exclusions and missing data
Cells with fewer than 5 usable seeds (missing files) are analysed with the
seeds available and flagged. If more than 5 cells are incomplete, see the
contingencies.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Hugging Face is blocked here | Ask for `huggingface.co` to be allowed in the environment network settings, or download on another machine and upload to a storage bucket | No |
| The zoo has fewer seeds or cells than described | Run on what exists. If K < 4, merge into E06 (train our own seeds) and mark E02 `blocked` | Yes |
| The zoo's `stats.json` MCC does not match our recomputation under either world | Use whichever world reproduces `stats.json`, document it, and run activation-based measures only under that world | No |
| Only part of the zoo can be downloaded | Minimum viable subset: L0 = 25 for all 5 architectures (25 SAEs, about 0.6 GB). Report as 5 cells. | Yes |
| f2 = 0 in many cells (K = 5 too small) | Use bias-corrected forms, report failure rates, and lean on E06 (K = 16) for PH1 | No |
| Matching at τ = 0.7 gives almost no overlap | Report it. E03 picks the matcher; re-run R003 with the E03 winner as a declared secondary analysis | Yes, if used as primary |
| Gate G2 (with E03): no matcher reaches pair F1 ≥ 0.9 on frequent features | Phase 1 headline becomes "matching is the bottleneck". Shift the paper's weight to testbeds with identity by construction (E10, E09). | Decision record |

## 4. Runs

<!-- runs:start -->
| Run | Title | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|
| E02-R001 | Download, checksum and inventory zoo | planned |  |  | fa922b4+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
