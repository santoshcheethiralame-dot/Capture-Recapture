# E00: Estimator library and reference validation

| Field | Value |
|---|---|
| Status | registered |
| Tier | core |
| Stage | 0 infra |
| Depends on | none |
| Study hypotheses | none directly; every experiment depends on it |
| Testbed | reference datasets shipped with R packages; published worked examples |
| Compute | CPU, minutes |
| Pre-registration | not frozen |

## 1. Question

Every number in the paper passes through these estimators. Before trusting
any coverage figure for an audit, we need to know that the code computes
what the literature defines. Technical question: do our Python
implementations agree with the reference implementations (R `Rcapture`,
`iNEXT`, `SpadeR`, `breakaway`, `VGAM`) and with published worked examples?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Build `src/crsafety/estimators/` (growing from `pilot/estimators.py`) and
show that each estimator matches a reference.

### Data-generating mechanism / testbed
1. Incidence datasets bundled with `iNEXT` / `SpadeR` (e.g. the `ant` and
   `ciliates` incidence data) and capture-history datasets bundled with
   `Rcapture` (e.g. `hare`, `mvole`, `bunting`). Exact names are confirmed
   when R is installed.
2. Worked examples printed in the source papers (Chao 1987; Chao et al. 2014;
   Chao and Jost 2012; Chiu et al. 2014).
3. Synthetic edge cases: f2 = 0; all items singletons; one item; K = 2;
   every item caught on every run.

### Estimands
The reference outputs themselves.

### Methods
Estimators: Chapman; Darroch Mt (MLE); Chao2 bias-corrected and classic;
iChao2; jackknife 1 and 2; ICE; Chao-Jost incidence coverage; Chao et al.
(2014) incidence extrapolation Δ(m); Good-Turing f1/U; Huggins conditional
likelihood with Horvitz-Thompson; Böhning generalised Chao; log-linear models
(through `rpy2` to `Rcapture`); `breakaway_nof1` (through `rpy2`); Chao
incidence bootstrap.

### Performance measures
Absolute and relative difference from the reference. Bootstrap outputs are
compared within Monte Carlo error. Tests also check the stated properties
(below).

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H0a | Deterministic estimators match the reference | max relative difference | ≤ 1e-6 on every dataset | any dataset > 1e-4 |
| H0b | Bootstrap intervals match the reference | endpoint difference | within 3 MCSE (B = 2,000 each side) | larger |
| H0c | Properties hold | unit tests | all pass | any fail |

Properties tested:
- invariance to permuting runs and items;
- S_obs ≤ Chao2;
- 0 ≤ Ĉ ≤ 1;
- Δ(m) ≥ 0 and non-decreasing in m;
- documented behaviour when f2 = 0 (bias-corrected form) and when there are
  no recaptures (Chapman finite, Mt returns infinity and is flagged).

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Reference comparison, all datasets | 1 | minutes |
| R002 | Property tests (pytest) | 1 | minutes |

### Sample size and Monte Carlo error
Bootstrap comparisons use B = 2,000 on both sides.

### Analysis plan
- Confirmatory: H0a to H0c. Any failure blocks every Stage 1+ experiment
  until fixed.
- Exploratory: speed benchmarks.

### Exclusions and missing data
An estimator with no available reference is validated against a published
worked example. If neither exists, it is marked "unvalidated" in the
library and may not be a primary estimator.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| R cannot be installed | Not expected: on 2026-10-22 an agent installed R 4.1.3 + Rcapture 1.4.4 + iNEXT 3.0.0 + breakaway 3.0 in this sandbox via micromamba/conda-forge. CRAN-only packages (SpadeR, SPECIES, LCMCR, dga, SparseMSE) can be built from the `github.com/cran/<pkg>` mirror. If that fails, validate against worked examples and run the R comparison elsewhere before the v1 freeze. | No |
| An estimator disagrees with the reference | Find out which side is wrong: re-derive from the paper, check a second reference. Log the finding in `LOG.md`. If the reference is wrong, record it as a decision (`DECISIONS.md`). | No |
| Chiu-Chao singleton-correction formula cannot be confirmed from the paper | Leave it out of the library; use `breakaway_nof1` as the f1-free option | No |
| Huggins fit does not converge on the reference data | Use `VGAM` through `rpy2` for that estimator | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|
| E00-R001 | Reference comparison against R packages and worked examples | planned |  |  | fa922b4+dirty |  |
| E00-R002 | Property tests (pytest) | planned |  |  | fa922b4+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
