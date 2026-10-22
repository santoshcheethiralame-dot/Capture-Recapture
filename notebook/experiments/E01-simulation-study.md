# E01: Simulation study of estimators under AI-safety violations

| Field | Value |
|---|---|
| Status | registered |
| Owner | Santosh |
| Tier | core |
| Stage | 1 exploratory (sets † thresholds before the v1 freeze) |
| Depends on | E00 |
| Study hypotheses | PH2 (also informs PH1, PH4, PH5 thresholds) |
| Testbed | simulated detection histories (extends `pilot/`) |
| Compute | CPU; about 1 to 3 hours on 8 cores |
| Pre-registration | not frozen |

## 1. Question

Before testing on audits and red teams, we need to know how each estimator
behaves when the assumptions break in the ways AI-safety tools break them:
- uneven detectability;
- heavy tails of rare failures;
- catchers that share a base model;
- searches that steer away from earlier finds;
- adaptive search;
- nested runs;
- matching errors;
- small numbers of items.

Technical question: under each violation, what are the bias, RMSE and
interval coverage for N, N_LB and C, and the prediction error of Δ(m)?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Map estimator performance across violations, choose the primary estimators,
and set the † thresholds of the study pre-registration.

### Data-generating mechanism (ADEMP "D")
Items i = 1..N have per-run detection probabilities π_i. K runs produce a
binary detection matrix.

**Base cell:** N = 500, K = 10, π_i logit-normal with mean 0.2 and σ = 1,
independent runs, oracle identity.

**One factor at a time from the base cell:**

| Factor | Levels |
|---|---|
| N | 50, 500, 5000 |
| K | 3, 5, 10, 20 |
| Heterogeneity | homogeneous π = 0.2; logit-normal σ ∈ {1, 2}; Zipf α ∈ {0.5, 1.0} with floor π ≥ 0.001; mixture with a 20% uncatchable class (π = 0) |
| Shared-family effect | 1, 2, 3 or 6 families sharing individual effects (τ = 1.5), as in the pilot |
| True list dependence | log-linear pairwise interaction between two blocks of runs, odds ratio ∈ {1/3, 1, 3} (negative, none, positive) |
| Behavioural response (adaptivity) | after an item's first detection, its π is multiplied by c ∈ {0.5 ("avoid found"), 1, 2 ("revisit found")} for later runs |
| Nested runs | threshold model π_ij = sigmoid(k(u_i − c_j)), k ∈ {3, 10}, six ordered cut-offs |
| Ghosts (false non-match) | f ∈ {0, 0.05, 0.15} per detection |
| Merges (false match) | g ∈ {0, 0.05} per item |

**Two-way interactions:**
- heterogeneity σ ∈ {1, 2} × K ∈ {5, 10, 20};
- heterogeneity × ghosts;
- N ∈ {50, 500} × K ∈ {5, 10};
- shared-family × K.

### Estimands (ADEMP "E")
- N;
- N_LB (population Chao2 bound);
- C(K) as defined in the study pre-registration;
- Δ(K), the new items found by K more runs (simulated by actually drawing K
  more runs).

### Methods (ADEMP "M")
The E00 estimator suite. Intervals: the Chao2 log-normal CI, and the
bootstrap for C and Δ.

### Performance measures (ADEMP "P")
For each estimator × estimand:
- bias and relative bias, with MCSE;
- RMSE;
- coverage of the 95% interval, with MCSE;
- median interval width;
- failure rate (NaN or infinity).

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H1a | Coverage is accurate without identity error or adaptivity | \|bias of Ĉ\| | ≤ 0.03 in every such cell with K ≥ 5 | > 0.05 in any such cell |
| H1b (→ PH2) | Chao2 intervals do not cover N under heterogeneity | CI coverage of N | < 50% in every cell with σ ≥ 1 | ≥ 80% in any such cell |
| H1c | Negative dependence makes Chapman overestimate | relative bias, odds ratio 1/3 | > +20% | < +5% |
| H1d (→ PH5) | Behavioural response c = 2 makes Ĉ overstate coverage | bias of Ĉ | ≥ +0.05 | < +0.02 |
| H1e | Ghosts make coverage conservative and Chao2 too high | bias at f = 0.15 | Ĉ bias < 0 and Chao2 bias > 0 | either sign wrong |
| H1f (→ PH4) | Shared-family runs overstate coverage relative to independent families | Ĉ − C, 1 family vs 6 | difference ≥ 0.05 | < 0.02 |

**Decision rules for the freeze:**
1. Primary estimators for Stage 2 are those with \|bias of Ĉ\| ≤ 0.03 and CI
   coverage ≥ 0.90 in the base cell. Default primaries: Chao-Jost coverage,
   Chao et al. (2014) Δ(m), Chao2 as a labelled lower bound.
2. Each † threshold in PREREGISTRATION.md is set to the value that E01 says
   is achievable in the matching clean cell, rounded to the nearest 0.01.
   It may not be loosened beyond twice that value. The change and its run ID
   go in the changelog.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Base cell + N, K, heterogeneity blocks | 500 per cell | < 30 min |
| R002 | Family, dependence, adaptivity, nested blocks | 500 per cell | < 30 min |
| R003 | Identity-error blocks | 500 per cell | < 15 min |
| R004 | Two-way interactions | 500 per cell | < 1 h |
| R005 | Bootstrap interval coverage (B = 500 inside each replicate) on a subset of 12 cells | 500 per cell | 1 to 2 h |

### Sample size and Monte Carlo error
n_sim = 500 gives an MCSE of about 0.01 for 95% interval coverage. MCSE is
reported for every bias and coverage figure. Seeds come from
`numpy.random.SeedSequence(20261022).spawn(...)`, one stream per cell.

### Analysis plan
- Confirmatory within E01: H1a to H1f (exploratory status for the study,
  but evaluated as written).
- Output: one table per block, as in `pilot/results.md`, plus the
  "estimator decision guide" table (which estimator and which bias direction
  for each violation) for the paper's appendix.

### Exclusions and missing data
None. Estimator failures are counted, not dropped.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| R005 bootstrap too slow | Cut B to 200, then n_sim to 200 for R005 only, and report the larger MCSE | Yes (logged) |
| Coverage estimator fails H1a in clean cells | **Gate G1 fails.** Stop. Check E00 first. If the implementation is right, the paper's core claim is in trouble: re-scope to "coverage fails too; here is why", and discuss before any Stage 2 work. | Yes |
| The negative-dependence generator cannot hit odds ratio 1/3 exactly | Report the achieved odds ratio | No |
| Results contradict the pilot | Trust E01 (more replicates, validated code); explain the difference in `LOG.md` | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E01-R001 | Base cell + N, K, heterogeneity blocks | Santosh | planned |  |  | fa922b4+dirty |  |
| E01-R002 | Family, dependence, adaptivity, nested blocks | Santosh | planned |  |  | fa922b4+dirty |  |
| E01-R003 | Identity-error blocks | Santosh | planned |  |  | fa922b4+dirty |  |
| E01-R004 | Two-way interactions | Santosh | planned |  |  | fa922b4+dirty |  |
| E01-R005 | Bootstrap interval coverage subset | Santosh | planned |  |  | fa922b4+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
