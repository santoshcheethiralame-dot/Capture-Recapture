# E05: Identity-error injection and corrections

| Field | Value |
|---|---|
| Status | registered |
| Owner | Santosh |
| Tier | core |
| Stage | 2 confirmatory |
| Depends on | E00, E01, E02 (oracle histories) |
| Study hypotheses | PH3b |
| Testbed | E02 oracle histories + E01 simulated histories |
| Compute | CPU; hours |
| Pre-registration | not frozen |

## 1. Question

Every audit that clusters its findings makes some identity mistakes. If those
mistakes cannot be corrected, coverage claims are only as good as the
clustering. Technical questions:
- How much do known rates of false non-matches (ghosts) and false matches
  (merges) bias the estimates?
- Which correction recovers the truth, and how many hand-labelled pairs does
  it need?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Quantify the bias from identity errors, and compare corrections.

### Testbed
- Oracle histories from E02 (all 35 cells).
- Simulated histories from the E01 base cell and the σ = 2 cell.

### Data-generating mechanism (error injection)
- **False non-match rate** f ∈ {0, 0.02, 0.05, 0.10, 0.20, 0.30}: each
  recapture is independently unlinked and becomes a new singleton.
- **False match rate** g ∈ {0, 0.01, 0.02, 0.05, 0.10}: random pairs of items
  are merged.
- **Two error patterns:**
  - *uniform;*
  - *score-based:* f decreases with item frequency, as in the
    McClintock-style item-quality effect (f_i ∝ 1/√p_i, rescaled to the
    target mean).
- 200 injections per (cell, f, g, pattern).

### Estimands
The oracle-history estimates (no error) and the true C and \|U\|.

### Methods (corrections)
- (a) Naive, no correction.
- (b) Labelled-subset rates: estimate f and g from n_v ∈ {50, 100, 200, 500}
  labelled pairs (stratified by score bin); then apply the LP correction
  LP × (1 − f̂), and first-order frequency-count corrections for Chao2 and Ĉ.
- (c) Chiu-Chao singleton-corrected Chao2 (if validated in E00).
- (d) f1-free estimator (`breakaway_nof1` or ratio regression).
- (e) Multiple imputation over matchings: soft match probabilities from a
  two-component mixture on the score, 20 imputations, Rubin's rules.
- (f) Di Consiglio-Tuoto linkage-error-corrected Petersen (pairs only).

### Performance measures
- Relative bias and RMSE of Chao2 and Ĉ against the oracle values and the
  truth.
- Interval coverage.
- Residual bias as a function of n_v.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H5a (→ PH3b) | Some correction removes most ghost bias | best correction's \|rel. bias of Chao2\| vs naive at f = 0.10 | ≥ 50% reduction | < 25% |
| H5b | Coverage stays conservative under ghosts | sign of Ĉ − C at f ≥ 0.05 | negative in ≥ 90% of cells | positive in ≥ 20% |
| H5c | 200 labelled pairs suffice | residual \|bias\| at n_v = 200 vs n_v = 500 | within 0.02 (Ĉ) / 5% (Chao2) | otherwise |
| H5d | Merges matter most when overlap is small | bias at g = 0.05 in low- vs high-overlap cells | larger in low-overlap cells | not larger |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Injection grid on E01 histories | 200 per combination | < 1 h |
| R002 | Injection grid on E02 oracle histories | 200 per combination | 1 to 2 h |
| R003 | Corrections (a)–(f) | same | 2 to 4 h |

### Sample size
200 injections per combination. MCSE is reported.

### Analysis plan
- **Confirmatory:** H5a to H5d.
- **Output:** the recommended correction and labelling budget, recorded as a
  decision for E08 to E11.
- **Exploratory:** combined heterogeneity and misidentification (the
  confound flagged by the MARK book).

### Exclusions and missing data
None.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| No correction works (H5a fails) | Report it as a negative result. Recommend sensitivity bands (estimates across the plausible f, g range) instead of point corrections | No |
| Multiple imputation too slow on 16k-item histories | Use 10 imputations, or subsample items for the MI arm only | Yes (logged) |
| Chiu-Chao formula unavailable | Drop (c) | No |

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
