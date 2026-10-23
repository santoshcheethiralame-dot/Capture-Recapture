# E07: Covariates of detectability (Huggins, Böhning)

| Field | Value |
|---|---|
| Status | proposed |
| Owner | Santosh |
| Tier | stretch |
| Stage | 3 |
| Depends on | E02, E06 |
| Study hypotheses | SH3 |
| Testbed | E02/E06 histories with known p_i |
| Compute | CPU |
| Pre-registration | not frozen |

## 1. Question

Rare failure modes are hard to find, and we can often measure how rare a
finding is. Can that measurement correct for the failures we never saw?
Technical question: do conditional-likelihood estimators with detectability
covariates beat Chao2? Covariates are firing frequency, activation norm,
nearest-neighbour cosine, and for audits, behaviour type.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Test covariate models with oracle, noisy and observed covariates.

### Testbed
E02 and E06 oracle histories. Covariates:
- **x1 (oracle):** log p_i, the true firing probability.
- **x2 (noisy):** log p_i plus N(0, s²), s ∈ {0.5, 1}.
- **x3 (observed):** log firing frequency of the matched latents on 10^6
  samples. Available for caught features only, which is what Huggins
  requires.
- **x4 (observed):** mean activation and the max cosine to another latent in
  the same SAE.

### Estimands
\|U\|, and the population of features above a firing threshold.

### Methods
- Huggins conditional likelihood with a logistic link and Horvitz-Thompson
  N̂ (VGAM or our implementation).
- Böhning generalised Chao.
- Comparators: Chao2, iChao2.

### Performance measures
Relative bias and RMSE against \|U\|; CI coverage.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H7a | Oracle covariate removes most heterogeneity bias | \|rel. bias\| of Huggins with x1 | ≤ 10% in ≥ 80% of cells | > 20% in most cells |
| H7b | Observed covariates help vs Chao2 | \|rel. bias\| x3/x4 vs Chao2 | lower in ≥ 70% of cells | lower in < 50% |
| H7c | Misspecification overshoots | sign of bias with x2 at s = 1 | report (no direction pre-specified) | — |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | All covariate models on E02 + E06 | all cells | CPU hours |

### Sample size
Fixed by E02/E06.

### Analysis plan
Confirmatory: H7a, H7b. Exploratory: catch-probability curve shape (input to
E15).

### Exclusions and missing data
Non-converging fits are counted and reported.
<!-- prereg:end -->

## 2a. Implementation notes (2026-10-23, before any E07 run)

- Script: `analysis/e07/analyse.py` (R001), tested on simulated §10 cells
  (`tests/test_e07.py`). Inputs: E02 oracle histories at τ_gt = 0.7 and the
  E06 cells, written by `analysis/e02/zoo.py histories --fire-counts`.
- Observed covariates are recorded per run in items.csv (`log_freq`,
  `mean_act`, `max_cos`, keyed by run seed). `fire_counts.py` now also sums
  activations. An item's covariate is the mean over the estimation runs that
  caught it, so reference runs never inform the fit. Covariates are
  standardised (N̂ unchanged). x2 noise is seeded per cell and s from master
  20261029.
- Huggins interval: `crsafety.huggins_ci` (Huggins 1989 variance; matches
  VGAM `SE.N.hat` on the E00 datasets, `tests/test_huggins_ci.py`), with a
  log-normal interval on N̂ − S. Generalised Chao has no interval here.
- **For the freeze** (`docs/FREEZE-V1.md`):
  1. The firing threshold for "population above a firing threshold" is not
     set in §2. Proposed: the smallest p among U (`--p-threshold auto`).
  2. Huggins estimates every item with detection probability > 0, which is
     N_true in a planted world, not the finite union |U|. Relative bias
     against |U| therefore penalises a correct extrapolation past U.
     Proposed: keep |U| as primary (as pre-registered) and report N_thr
     alongside.
  3. H7b names "x3/x4". The script tests them separately (H7b-x3, H7b-x4).
     Proposed: supported if either is supported, reporting both.
  4. Failed fits count as not meeting the criterion (conservative).
- §3 contingency is computed in advance: every Huggins fit records its
  largest Horvitz-Thompson weight and N̂ with weights truncated at 100.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Fits unstable (extreme Horvitz-Thompson weights) | Truncate weights at 1/π ≤ 100 and report both | Yes (logged) |
| E06 not run | Use E02 only and say so | Yes |

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
