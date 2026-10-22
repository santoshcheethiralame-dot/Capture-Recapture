# E00: Estimator library and reference validation

| Field | Value |
|---|---|
| Status | analysed (R001–R004 succeeded; awaiting Kushal's review) |
| Owner | Santosh |
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
(ported from `Rcapture`, validated against it); `breakaway_nof1` (called in R
through `Rscript`; see D-009); Chao incidence bootstrap.

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
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E00-R001 | Reference comparison against R packages and worked examples | Santosh | succeeded | 2026-10-22 | 2026-10-22 | f792c71 | 437/437 comparisons pass on 34 datasets: deterministic max rel. diff 2.8e-10 (H0a); bootstrap s.e. within 3 MCSE (H0b) |
| E00-R002 | Property tests (pytest) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | f792c71 | 377/377 property tests pass (H0c) |
| E00-R003 | Remaining estimators: Chiu-Chao singleton correction, log-linear (Rcapture), breakaway_nof1, Böhning generalised Chao | Santosh | succeeded | 2026-10-22 | 2026-10-22 | ba80724 | 1744/1744 comparisons pass on 29 datasets: log-linear N, s.e., deviance, AIC, BIC vs Rcapture (12 closedp.t models + 5 interaction designs) max rel. diff 3.0e-12; generalised Chao vs glm 3.7e-15 and = iNEXT Chao2 without covariates; breakaway_nof1 bridge exact (H0a). Chiu-Chao not implemented (contingency; Q-D10) |
| E00-R004 | Property tests incl. R003 estimators (pytest) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | ba80724+dirty | 595/595 pytest cases pass (377 original + 218 for log-linear models, generalised Chao and the R bridge) (H0c) |
<!-- runs:end -->

## 5. Results

Library: `src/crsafety/` (commit f792c71). Formula conventions: D-008.
Outputs: `results/E00/E00-R001/` (`summary.md`, `comparison.csv`,
`reference.json`, input data).

### Confirmatory

| Hypothesis | Verdict | Evidence |
|---|---|---|
| H0a: deterministic estimators match the reference (rel. diff ≤ 1e-6) | **supported** for every estimator compared | E00-R001: 381 comparisons on 34 datasets. Max rel. diff 4e-15 for the Chao2 family, coverage, ICE and jackknife; 3e-13 for extrapolation; 2.4e-10 for Darroch Mt; 2.8e-10 for Huggins. |
| H0b: bootstrap s.e. match the reference within 3 MCSE (B = 2,000 each side) | **supported** | E00-R001: 56 comparisons (s.e. of S + new items at 2K, and of coverage). All within 3 MCSE. Largest relative gap 6%, consistent with MC error at B = 2,000. |
| H0c: stated properties hold | **supported** | E00-R002: 377 / 377 pytest cases pass. |

| Quantity | Reference | Datasets | Max rel. diff |
|---|---|---|---|
| Chao2, s.e., log-normal interval | `iNEXT::ChaoRichness` (and `vegan::specpool` for Chao2) | 31 | 4.0e-15 |
| Coverage at K | `iNEXT:::Chat.Sam` | 31 | 7.1e-16 |
| New items after K and 2K more runs | `iNEXT:::TD.m.est_inc` | 31 | 3.4e-13 |
| iChao2 | SpadeR `SpecInciiChao2` | 29 | 2.9e-15 |
| ICE | SpadeR `SpecInciModelh` | 30 | 3.1e-15 |
| Jackknife 1, 2 | `vegan::specpool` | 26 | 3.1e-15 |
| Darroch Mt | `Rcapture::closedp.t` | 17 | 2.4e-10 |
| Huggins N and coefficients | `VGAM::vglm`, `posbernoulli.t` | 3 | 2.8e-10 |
| Bootstrap s.e. | `iNEXT:::iNEXT.Sam` | 31 | within 3 MCSE |

Datasets: 13 synthetic (heterogeneous, heavy-tailed, K = 2 to 20, and the
edge cases Q1 = 0, Q1 = 1, Q2 = 0, Q4 = 0, tiny data), 3 Huggins covariate
worlds, and 18 bundled with R packages (iNEXT `ant` ×5, `ciliates` ×3;
Rcapture `hare`, `mvole`, `bunting`, `duck`, `HIV`, `lesbian`, `rbvole`;
vegan `dune`, `mite`, `BCI`).

**Scope delivered against the plan in §2.** Validated in R001: Chapman and
Good-Turing (hand-computed values in tests; no R reference), Darroch Mt,
Chao2 (both forms), iChao2, jackknife 1 and 2, ICE, coverage,
extrapolation, Huggins, Chao bootstrap. Validated in R003: log-linear
models, Böhning generalised Chao, `breakaway_nof1` (see below). **Not
implemented:** the Chiu-Chao singleton correction (contingency applied;
see below and D-009).

### E00-R003: remaining estimators (2026-10-22)

Code: `src/crsafety/loglin.py`, `generalized_chao` in
`src/crsafety/estimators.py`, `src/crsafety/rbridge.py` (commit ba80724).
Harness: `validation/e00/run_r003.sh`. Outputs: `results/E00/E00-R003/`.
References: R 4.5.3, Rcapture 1.4.4, breakaway 5.0.1 (built from
`github.com/adw96/breakaway`), iNEXT 3.0.2. Same 29 datasets as R001 where
the estimator applies (log-linear models need K ≤ 12 and at least one
recapture).

| Quantity | Reference | Comparisons | Max rel. diff | Verdict (H0a) |
|---|---|---|---|---|
| Log-linear N, all 12 `closedp.t` models (M0, Mt, Mh/Mth × Chao (LB), Poisson2, Darroch, Gamma3.5, Mb, Mbh) | `Rcapture::closedp.t` | 195 | 4.2e-13 | supported |
| Same, s.e. | Fisher information at Rcapture's MLE, Rcapture's formulas | 194 | 2.9e-12 | supported |
| Same, deviance / AIC / BIC | `Rcapture::closedp.t` | 585 | 3.9e-14 | supported |
| Interaction models (Mt + c1:c2; + Chao, Poisson2, Darroch heterogeneity; Mt + all pairs of runs 1–3) N, s.e., deviance, AIC, BIC | `Rcapture::closedpCI.t` | 388 | 3.0e-12 | supported |
| Generalised Chao, no covariates | logistic fit by `stats::glm`; also `iNEXT::ChaoRichness` (classic Chao2) | 46 | 3.7e-15 | supported |
| Generalised Chao with covariates: N and coefficients | `stats::glm` (binomial, offset) | 10 | 2.3e-14 | supported |
| `breakaway_nof1` through the bridge: estimate and s.e. | `breakaway::breakaway_nof1` called directly in R | 52 | 0 | supported |

E00-R004: 595 / 595 pytest cases pass (H0c), including 218 new property
tests (history order, Mt = Darroch MLE, M0 likelihood equation,
permutation invariance, bounds, generalised Chao = Chao2 without
covariates and ≈ unbiased with an oracle covariate, breakaway_nof1
unaffected by added singletons).

**Notes for users of these estimators:**
- The s.e. that Rcapture prints uses glm's `vcov()`, evaluated at the IRLS
  weights of the previous iteration, so it carries O(√ε) error (up to
  2.3e-6 relative here). `crsafety` evaluates the information at the MLE.
  Rcapture's Chao (LB) refits also ignore the user's glm tolerance; the
  reference script forces a tight tolerance on every fit.
- When N̂ = S exactly (the intercept diverges to −∞, e.g. `Mt+pairs123` on
  two edge datasets), the s.e. is numerical noise near 0 in both
  implementations; it is compared in absolute terms.
- `breakaway_nof1` predicts f1 as well as f0, so its estimate does not
  change when singletons are added or removed. It is applied to incidence
  frequency counts as if they were abundance counts; it is a sensitivity
  check, not a primary estimator.
- The generalised Chao estimator is the binomial (incidence) form of
  Böhning et al. (2013): logistic regression of "found twice" vs "found
  once" with offset log((K − 1)/2); f0 = Σ 1/(Kθ_i + K(K − 1)θ_i²/2).
  No published implementation exists for the binomial form; R003 checks
  the fit against `glm` and the exact reduction to Chao2. With an oracle
  covariate its median error was < 1% in 200 simulated worlds, but its
  Horvitz-Thompson weights make the mean unstable under heavy tails (see
  E07's weight-truncation contingency).

**Chiu-Chao singleton correction: not implemented (contingency row 3).**
The formula (Chiu and Chao 2016, PeerJ 4:e1634) could not be read from this
environment: peerj.com, PubMed Central and arXiv are blocked, and no Chao
lab package on GitHub (SpadeR, iNEXT, iNEXT.3D, iNEXT.4steps,
iNEXT.beta3D) implements it. Following the contingency, `breakaway_nof1`
is the f1-free option. Q-D10 stays open; if someone reads the paper,
implementing and validating the correction is a new E00 run.

### Exploratory

- **`fossil::ICE` does not implement the published ICE.** It sums
  i·Q_i where the formula has i(i−1)·Q_i, drops the K/(K−1) factor, and
  uses the uncorrected sample coverage. We use the Chao lab (SpadeR) form
  (D-008).
- **SpadeR's iChao2 crashes when Q4 = 0.** The failure is in its variance
  code; its point estimate is fine and matches ours.
- **iNEXT 3.x writes extrapolation differently from Chao et al. (2014)**,
  as obs + (asy − obs)(1 − (1 − β)^m). For q = 0 this is algebraically the
  same: rarefaction to K − 1 units gives S − Q1/K, so β = Q1/(K f0 + Q1).
  The numbers agree to 3e-13.
- **Coverage when Q2 = 0.** iNEXT uses the bias-corrected f0 inside the
  coverage formula, so it differs from the Chao-Jost (2012) expression,
  which is written for Q2 > 0. We follow iNEXT.
- **Speed:** the full Python comparison, including 2 × 34 bootstraps at
  B = 2,000, takes about 8 s on the sandbox CPU. The R side takes 3.5 min.

## 6. Deviations

_None._
