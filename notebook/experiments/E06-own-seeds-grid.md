# E06: Our own SAE seeds across worlds (K = 16)

| Field | Value |
|---|---|
| Status | registered |
| Owner | Santosh |
| Tier | important |
| Stage | 2 confirmatory |
| Depends on | E00, E01, E03 (identity rule) |
| Study hypotheses | PH1, PH2, PH4 (data-sharing dependence) |
| Testbed | SynthSAEBench generator (v2) in SAELens, our parameters |
| Compute | $0; Kaggle T4; about 20–40 GPU-hours with the scaled-down world (measured in R001; see `docs/COMPUTE.md`) |
| Pre-registration | not frozen |

## 1. Question

E02 has only 5 seeds and one world. This experiment asks how coverage
estimates behave with more runs (K = 16), and how they depend on:
- the tail of rare features;
- feature structure (hierarchy, correlation);
- SAE width;
- whether runs share data.

Shared data is the SAE version of "auditors built on the same base model".

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Test coverage and richness estimation at larger K across controlled worlds.
Measure the dependence that a shared data stream creates.

### Data-generating mechanism
SAELens synthetic generator (`sae_lens.synthetic`). **Scaled down for free
GPUs (D-007):** N_true = 4,096, d = 256, unless varied. Superposition is 16× (SynthSAEBench: about 21×). The width ratio stays at
0.25. Compute per SAE drops to roughly 1/12. The SynthSAEBench default world has Zipf exponent
0.5 and p_min = 5e-4. There, even the rarest feature fires about 10^5 times,
so it has **no sampling-limited tail** (see E02). Our base world therefore
uses a heavier tail and a lower floor, so that rare features are seen only a
few times in training.

**Base world:**
- Zipf exponent α = 1.0, p ∈ [1e-7, 0.4] (the rarest feature fires about 5 times in 50M samples);
- hierarchy and correlation **off**;
- width 1,024; BatchTopK at L0 = 25;
- 50M samples;
- initialisation and data stream seeded independently (both vary).

**One factor at a time:**

| Factor | Levels |
|---|---|
| Zipf α | 0.5 (the SynthSAEBench default), 1.0, 1.5 |
| p_min | 1e-7 (base), 5e-4 (SynthSAEBench default) |
| Structure | off/off; hierarchy on; correlation on; both on (the SynthSAEBench default) |
| Width / N_true | 0.25 (1,024, base), 1.0 (4,096) |
| Seed type | initialisation only (shared data stream); data only; both |
| Budget | 20M, 50M samples |

That is 11 cells. Each has 16 evaluation seeds plus 8 reference seeds: 24
per cell, 264 SAEs.

**Seeding** (SAELens does not seed training itself, per code inspection):
`torch.manual_seed(init_seed)` before constructing the runner (the SAE is
initialised in its constructor), then `torch.manual_seed(data_seed)` after
construction and before `runner.run()` (the activation generator uses the
global torch RNG). Before any grid run, R001 checks this by hashing `W_dec`
at step 0 and the first training batch for 4 seed combinations.

### Estimands
As in E02, with the oracle catch rule at τ_gt = 0.7. U is the union over the
16 evaluation seeds plus 8 reference seeds. The reference seeds are not used
by the estimators. True C(K) is computed for K ∈ {4, 8, 16}.

### Methods
Identity rule from E03 (winner + plateau rule). Correction from E05 if
needed. Primary estimators from E01. Both oracle and matched histories.

### Performance measures
Ĉ − C at K ∈ {4, 8, 16}; Chao2 against \|U\| and N_true; Δ̂(K) against the
reference seeds; n_eff and pairwise overlap ratios.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H6a (→ PH1) | Coverage is accurate at K ≥ 8 (oracle) | \|Ĉ − C\| | ≤ 0.05† in ≥ 80% of cells at K = 8 and 16 | < 70% |
| H6b | Structure degrades accuracy | \|Ĉ − C\|, both-on vs off/off | larger with structure on | not larger |
| H6c (→ PH4 analogue) | Shared data order overstates coverage | Ĉ − C, initialisation-only vs both | ≥ 0.03 higher with initialisation-only | < 0.01 |
| H6d (→ PH2) | Chao2 stays far below N_true when width < N_true | Chao2 / N_true at width 0.25 | < 0.5 | ≥ 0.8 |
| H6e | Δ̂ predicts the reference seeds | median relative error of Δ̂(16) | ≤ 20% | > 40% |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Seeding check: 4 seed combinations, hash `W_dec` at step 0 and the first batch | 4 short runs | minutes |
| R002 | Timing pilot: 2 SAEs in the base world | 2 | < 2 GPU-h |
| R003 | Base cell, 24 seeds | 24 | per COMPUTE.md (measured in R002) |
| R004–R013 | One run per varied cell (24 seeds each) | 24 each | per COMPUTE.md |
| R014 | Histories and estimators | all | CPU hours |

### Sample size
16 evaluation seeds + 8 reference seeds per cell. Subsampled K curves use
200 random seed subsets.

### Analysis plan
- **Confirmatory:** H6a to H6e.
- **Secondary:** oracle vs matched comparison (feeds PH3a).
- **Exploratory:** accumulation curves; rate-distortion "bounce" comparator
  (Anthropic, May 2023) on the width sweep.

### Exclusions and missing data
SAEs that diverge (loss NaN or explained variance < 0.5) are re-trained once
with the same seed. If they fail again they are excluded, and the count is
reported.
<!-- prereg:end -->

## 2a. Implementation notes (2026-10-22, before any E06 training)

- Cells as SAELens configurations: `analysis/e06/worlds.py`. World settings
  that §2 does not name are copied from SynthSAEBench-16k (magnitudes
  5.0 → 4.0, folded-normal std, bias 0.5, orthogonalization, correlation
  rank 25 / scale 0.1). The hierarchy is scaled with the feature count
  (32 roots for 4,096 features). World seed 20261028.
- Seeds: seed k of a cell has (init, data) from
  `SeedSequence(20261028, spawn_key=(cell, k))`; "init-only" shares one data
  seed and "data-only" one init seed (`spawn_key=(cell, 999)`).
- R001 seeding check: passed as E06-R015 (R001 crashed while writing its
  manifest after the check had passed; recorded as a bug). Q-D13 resolved
  for the synthetic runner.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| The timing pilot says the grid exceeds the compute budget | Pre-declared cuts, in order: drop budget = 20M; drop α = 1.5; drop p_min = 5e-4; cut evaluation seeds to 12 | Yes (logged) |
| R001 shows seeds do not control initialisation or data as intended | Fix the seeding (seed CUDA generators; seed the dataset shuffle) and re-run R001. No grid run before R001 passes | No |
| The generator API differs from what we expect (SAELens version drift) | Pin the SAELens version used by SynthSAEBench; record it in `docs/DATA.md` | No |
| Width 1.0 SAEs are too slow | Run width 1.0 only for the base world | Yes |
| Kaggle quota runs out mid-grid | Split cells between both accounts (Santosh and Kushal). Seeds are deterministic, so either account can run any cell | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E06-R001 | Seeding check: hash W_dec at step 0 and first batch | Santosh | failed | 2026-10-22 | 2026-10-22 | b9e073c | Bug: crashed while closing the manifest (relative output path); the check itself completed and passed. Fixed; re-run as E06-R015 |
| E06-R002 | Timing pilot: 2 SAEs in the base world (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R003 | Base cell, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R004 | alpha0.5, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R005 | alpha1.5, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R006 | pmin5e-4, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R007 | hier, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R008 | corr, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R009 | hier+corr, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R010 | width1.0, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R011 | init-only, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R012 | data-only, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R013 | budget20M, 24 seeds (Kaggle) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R014 | Histories and estimators (CPU) | Santosh | planned |  |  | b9e073c+dirty |  |
| E06-R015 | Seeding check (retry of E06-R001 after bug fix) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 764bcb5+dirty | Passed: torch.manual_seed(init) before constructing SyntheticSAERunner fixes W_dec at step 0; torch.manual_seed(data) afterwards fixes the first batch; a repeat reproduces both (4 combos + repeat, SAELens 6.54.12). SyntheticSAERunnerConfig has no seed field (Q-D13) |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
