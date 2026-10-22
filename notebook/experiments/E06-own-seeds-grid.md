# E06: Our own SAE seeds across worlds (K = 16)

| Field | Value |
|---|---|
| Status | registered |
| Tier | important |
| Stage | 2 confirmatory |
| Depends on | E00, E01, E03 (identity rule) |
| Study hypotheses | PH1, PH2, PH4 (data-sharing dependence) |
| Testbed | SynthSAEBench generator (v2) in SAELens, our parameters |
| Compute | 1 small GPU; see `docs/COMPUTE.md` (on the order of tens of GPU-hours) |
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
SAELens synthetic generator (`sae_lens.synthetic`), N_true = 16,384,
d = 768, unless varied. The SynthSAEBench default world has Zipf exponent
0.5 and p_min = 5e-4. There, even the rarest feature fires about 10^5 times,
so it has **no sampling-limited tail** (see E02). Our base world therefore
uses a heavier tail and a lower floor, so that rare features are seen only a
few times in training.

**Base world:**
- Zipf exponent α = 1.0, p ∈ [1e-6, 0.4];
- hierarchy and correlation **off**;
- width 4,096; BatchTopK at L0 = 25;
- 200M samples;
- initialisation and data stream seeded independently (both vary).

**One factor at a time:**

| Factor | Levels |
|---|---|
| Zipf α | 0.5 (the SynthSAEBench default), 1.0, 1.5 |
| p_min | 1e-6 (base), 5e-4 (SynthSAEBench default) |
| Structure | off/off; hierarchy on; correlation on; both on (the SynthSAEBench default) |
| Width / N_true | 0.25 (4,096, base), 1.0 (16,384) |
| Seed type | initialisation only (shared data stream); data only; both |
| Budget | 50M, 200M samples |

That is 11 cells. Each has 16 evaluation seeds plus 8 reference seeds: 24
per cell, 264 SAEs.

**Seeding** (SAELens does not seed training itself, per code inspection):
`torch.manual_seed(init_seed)` before constructing the runner (the SAE is
initialised in its constructor), then `torch.manual_seed(data_seed)` after
construction and before `runner.run()` (the activation generator uses the
global torch RNG). Before any grid run, R000 checks this by hashing `W_dec`
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
| R000 | Seeding check: 4 seed combinations, hash `W_dec` at step 0 and the first batch | 4 short runs | minutes |
| R001 | Timing pilot: 2 SAEs in the base world | 2 | < 2 GPU-h |
| R002 | Base cell, 24 seeds | 24 | per COMPUTE.md (~15–20 H100-min per SAE) |
| R003–R012 | One run per varied cell (24 seeds each) | 24 each | per COMPUTE.md |
| R013 | Histories and estimators | all | CPU hours |

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

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| The timing pilot says the grid exceeds the compute budget | Pre-declared cuts, in order: drop budget = 50M; drop α = 1.5; drop p_min = 5e-4; cut evaluation seeds to 12 | Yes (logged) |
| R000 shows seeds do not control initialisation or data as intended | Fix the seeding (seed CUDA generators; seed the dataset shuffle) and re-run R000. No grid run before R000 passes | No |
| The generator API differs from what we expect (SAELens version drift) | Pin the SAELens version used by SynthSAEBench; record it in `docs/DATA.md` | No |
| Width 1.0 SAEs are too slow | Run width 1.0 only for the base world | Yes |

## 4. Runs

<!-- runs:start -->
_No runs yet._
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
