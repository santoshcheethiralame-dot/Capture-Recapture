# E05: Identity-error injection and corrections

| Field | Value |
|---|---|
| Status | registered; pilot done (R004, R005); design details in §2a for the freeze |
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

## 2a. Implementation choices (drafted 2026-10-22, before any confirmatory run; for the joint freeze)

§2 leaves these open. Code: `src/crsafety/linkage.py`, `analysis/e05/`.
Items marked **(after pilot)** were changed because of the declared pilot
E05-R004 (separate seeds); everything else was fixed before it ran.

**Record-level error model.** An item's first detection, in run order,
anchors it; every later detection is a *recapture*. Each recapture gets a
match score s ~ N(m_i, 1) and is linked iff s ≥ 0, with
m_i = Φ⁻¹(1 − f_i), so the ghost rate is exactly f_i. An unlinked recapture
becomes a singleton row whose best candidate is its true item (score s < 0).
A true singleton's best candidate is a random other row, scored
N(−2.5, 1) truncated below 0. Merges then join round(g · S) random pairs of
observed rows; each is a false link scored N(0.5, 1) truncated above 0.
- *Uniform pattern:* f_i = f.
- *Score-based pattern:* f_i ∝ 1/√p_i, rescaled so the share of all
  recaptures left unlinked is f, capped at 0.95. p_i is π_i (E01) or the
  generator's firing probability (E02).

**Histories.** R001: injection j uses E01 replicate j (j = 0..199) of the
base and ln2 cells, regenerated from E01's seeds. Seeds for injections:
`SeedSequence(20261027, spawn_key=(cell, f, g, pattern, j))` with level
indices; the pilot used spawn keys from 9000 up.

**Labelled pairs (b).** Candidate pairs are the linked recaptures, the false
links and each singleton's best candidate. n_v pairs are labelled, split
equally over the non-empty score bins (−∞, −2, −1, 0, 1, 2, ∞), and each
bin's true-match rate is weighted back by its size. f̂ = estimated true
matches below 0 / all true matches; ĝ = estimated false links / rows before
merging.

**Corrections.**
- (b) *First-order frequency-count correction* for ghosts:
  E[Q_obs] = A(f) Q + e₁ · f · (U − S), with A the thinning matrix (the
  anchor is never lost). Solved for Q ≥ 0 by non-negative least squares,
  then Chao2 and Ĉ are computed from the corrected counts. Merges are not
  corrected by (b). LP × (1 − f̂) is averaged over all run pairs.
- (c) Dropped: the Chiu-Chao formula is unavailable (contingency; Q-D10).
- (d) `breakaway_nof1` on the incidence frequency counts, through
  `crsafety.rbridge`. **Pilot finding:** at K = 10 it falls back to its
  Poisson model in 59% of injections and is biased (median −18% to −43%).
  It stays as specified; whether to add a ratio-regression f1-free
  estimator (E05 §2 allows one) is for the freeze. Adding one needs an E00
  validation run first.
- (e) Multiple imputation, 20 imputations. Each singleton is relinked to its
  best candidate with probability π. Chao2 uses Rubin's rules (log-normal
  s.e. as within-variance); Ĉ reports the MI mean and between-imputation
  variance.
  - (e1) π from a free two-component Gaussian mixture on the singletons'
    best-candidate scores (§2 as written).
  - (e2) **(after pilot)** π = the labelled true-match rate of the
    singleton's score bin (n_v = 200). In R004, (e1) relinked real
    singletons when there were no ghosts (Chao2 −26% at f = 0, g = 0.05,
    vs −6% naive); (e2) does not (−6%). Both are reported; (e2) is proposed
    as the primary MI variant.
- (f) Di Consiglio-Tuoto Petersen with λ = 1 − f̂ and β = ĝ, averaged over
  all run pairs.

**Cost (pilot).** 0.03 s per injection for (a), (b), (e1), (e2) and (f);
0.12–0.4 s per dataset for (d) through R. R001 (24,000 injections) takes
about 15 min plus 1–2.5 h for (d).

**Confirmatory scripts (2026-10-23, before the freeze; to be locked with
it).**
- `analysis/e05/run.py R001|R002` writes the injection grid with every
  correction. It refuses a dirty tree and records prereg v1.0. Smoke tests
  (`--out`) use the pilot keys from 9000.
- `analysis/e05/analyse.py` is R003: H5a–H5d plus interval coverage; tested
  in `tests/test_e05_analyse.py`. Definitions fixed in its docstring:
  - relative bias vs the oracle Chao2;
  - H5b's reference is the realized C for E01 worlds and the oracle Ĉ for
    E02 cells;
  - H5d splits cells at the median oracle overlap.
- R001 measured cost: about 0.23 s per injection, about 1.5–2.5 h for
  24,000.
- On 2026-10-23 a first smoke run (120 injections) drew from the
  confirmatory stream (keys < 9000, injection 0) before the offset existed.
  Its output was deleted unread: only shape and non-finite counts were
  printed. Logged in LOG.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| No correction works (H5a fails) | Report it as a negative result. Recommend sensitivity bands (estimates across the plausible f, g range) instead of point corrections | No |
| Multiple imputation too slow on 16k-item histories | Use 10 imputations, or subsample items for the MI arm only | Yes (logged) |
| Chiu-Chao formula unavailable | Drop (c) | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E05-R001 | Injection grid on E01 histories | Santosh | planned |  |  | 999589e |  |
| E05-R002 | Injection grid on E02 oracle histories | Santosh | planned |  |  | 999589e+dirty |  |
| E05-R003 | Corrections (a)-(f) | Santosh | planned |  |  | 999589e+dirty |  |
| E05-R004 | Pilot (declared, separate seeds): feasibility and cost of corrections | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 999589e+dirty | Pilot, 320 injections, 40 s: no failures; MI 0.018 s/injection (20 imputations OK); first-order count correction removes ghost bias (base f=0.10: Chao2 +35% -> 0%); free-mixture MI relinks real singletons (-26% at f=0, g=0.05); breakaway_nof1 falls back to Poisson in 59% of injections (median -34%) |
| E05-R005 | Pilot v2 (declared, same separate seeds): adds labelled-calibrated MI | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 87d6193+dirty | Pilot v2, 320 injections: labelled-calibrated MI (n_v=200) Chao2 -0% at f=0.10 and -6% at f=0, g=0.05 (= naive merge effect; free mixture -26%); count correction b +0 to +18%; breakaway_nof1 median -18% to -43% |
<!-- runs:end -->

## 5. Results

**Pilot (declared; separate seeds; not evidence for H5a–H5d).** E05-R004
and E05-R005: 320 injections each on the E01 base and ln2 worlds, f ∈ {0,
0.1, 0.3}, g ∈ {0, 0.05}, both patterns. No estimator failed. Mean Chao2
error relative to the oracle Chao2:

| world | f, g, pattern | naive | (b) n_v = 200 | (e1) mixture MI | (e2) labelled MI | (d) nof1 (median) |
|---|---|---|---|---|---|---|
| base | 0.10, 0, uniform | +35% | +0% | +7% | −0% | −18% |
| base | 0, 0.05, uniform | −6% | −6% | −26% | −6% | −21% |
| base | 0.30, 0, score | +169% | +10% | +34% | +8% | −20% |
| ln2 | 0.10, 0, uniform | +59% | −1% | +9% | −1% | −39% |
| ln2 | 0.30, 0, score | +316% | +18% | +63% | +12% | −43% |

Full tables: `results/E05/E05-R00{4,5}/summary.md`. Design consequences are
in §2a, marked "after pilot". The confirmatory runs R001–R003 wait for the
v1 freeze.

### Confirmatory

### Exploratory

## 6. Deviations

_None._
