# E11: How much of a real model's features have our SAEs found?

| Field | Value |
|---|---|
| Status | proposed |
| Owner | Santosh |
| Tier | stretch |
| Stage | 3 application |
| Depends on | E03 (identity rule), E05 (correction), E06 (validated settings) |
| Study hypotheses | SH4 |
| Testbed | Pythia-70M (own seeds); Gemma Scope ladders; board-game SAEs; random-transformer null |
| Compute | $0; Kaggle T4; about 30–45 GPU-hours (see `docs/COMPUTE.md`) |
| Pre-registration | not frozen |

## 1. Question

Interpretability is used as evidence in safety cases ("we looked inside and
found no deception features"). How much of a real model's feature mass did
the SAE actually cover? Truth is unknown here, so the experiment relies on
validated settings from Phase 1, on checks that need no truth, and on one
partial-truth testbed.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Apply the validated pipeline to real models. Test invariance. Calibrate
against partial truth.

### Testbeds
1. **Replicate seeds (scaled for free GPUs, D-007):** Pythia-70M, layer 3
   residual, BatchTopK at width 8k and L0 = 32, 50M tokens. K = 8 seeds with
   independent data streams, plus 4 seeds sharing one data order, for the
   dependence comparison. Pythia-160M is dropped (it would move to E18 if
   funded).
2. **Nested ladder:** Gemma Scope on Gemma-2-2B (residual, one mid layer),
   widths 16k → 1M at a matched L0. These are treated as nested, dependent
   occasions.
3. **Partial truth:** the board-game SAEs of Karvonen et al. Researcher-
   specified board features act as a "marked" subpopulation.
4. **Null:** 4 SAE seeds trained on a randomly initialised Pythia-70M (Heap
   et al.).

**Seeding.** In SAELens 6.54, `LanguageModelSAERunnerConfig.seed` is not
read by the training runner (code inspection). So seed initialisation with
`torch.manual_seed`, and shuffle the token stream with an explicit seed for
each data order. R001 checks this by hashing `W_dec` at step 0 and the first
batch, as in E06.

### Estimands
- Coverage of activation-mass-weighted features above a firing-frequency
  floor f_min = 10^-6.
- Δ(K).
- For the board games: the share of researcher features found.

### Methods
Identity rule from E03, correction from E05, primary estimators.

### Performance measures and checks
- Invariance of Ĉ across sampling units: seeds vs width ladder, thresholds
  within the plateau, two layers.
- Agreement between Ĉ and board-feature coverage.
- Null recapture rate.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H11a (→ SH4) | Coverage is invariant to the sampling unit | max \|Ĉ_a − Ĉ_b\| over unit pairs | ≤ 0.05 | > 0.10 |
| H11b | Estimated coverage agrees with board-feature coverage | \|Ĉ − board coverage\| | ≤ 0.10 | > 0.20 |
| H11c | Real-model features recapture more than the random-model null | recapture rate trained vs random | higher, CI excludes 0 | not higher |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Seeding check (hashes of `W_dec` at step 0 and the first batch) | 4 short runs | minutes |
| R002 | Timing pilot, Pythia-70M | 1 | < 2 GPU-h |
| R003 | Pythia-70M seeds (8 + 4) | 12 | per COMPUTE.md |
| R004 | Gemma Scope ladder analysis | — | download + CPU/GPU |
| R005 | Board-game SAE analysis | — | download |
| R006 | Random-transformer null | 4 | |

### Sample size
As listed.

### Analysis plan
- **Confirmatory:** H11a to H11c.
- **Exploratory:** coverage within safety-relevant feature classes (refusal-
  and deception-related latents found through Neuronpedia labels or probes).

### Exclusions and missing data
As in E06.
<!-- prereg:end -->

## 2a. Implementation notes (2026-10-23)

- Seeding (E11 §2), as implemented in `analysis/e11/seeding_check.py`:
  `torch.manual_seed(init)` before constructing
  `LanguageModelSAETrainingRunner`; then
  `activations_store.shuffle_input_dataset(data)` and
  `torch.manual_seed(data)` before training.
- R001 passed on a tiny randomly initialised HookedTransformer (HF is
  blocked here). The check concerns the runner's RNG use, not the model's
  weights. The script's `--hf pythia-70m-deduped --dataset ...` mode
  repeats it on the real model at the start of R002 on Kaggle; that repeat
  is logged under R002.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Hugging Face blocked (Gemma Scope, board-game SAEs) | Ask for network access, or download elsewhere | No |
| Gemma-2-2B too large for the available GPU | Skip the Gemma ladder; use Pythia width ladders instead | Yes |
| H11a fails | That is the finding: report which unit causes drift | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E11-R001 | Seeding check (Q-D13 for the LM runner): W_dec and first-batch hashes, 4 combos + repeat, tiny local model | Santosh | succeeded | 2026-10-23 | 2026-10-23 | ca75db0+dirty | Passed: init seed controls W_dec, data seed (shuffle_input_dataset + torch.manual_seed) controls the first batch, repeat reproduces both (SAELens 6.54.12, tiny local model). Repeat on Pythia-70M at the start of R002 |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
