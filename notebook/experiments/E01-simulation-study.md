# E01: Simulation study of estimators under AI-safety violations

| Field | Value |
|---|---|
| Status | analysed (R001–R008; awaiting Kushal's review) |
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

## 2a. Implementation choices fixed before the first run (2026-10-22)

§2 leaves these open. They were fixed in code (`src/crsafety/sim.py`,
`configs/e01/cells.json`, `analysis/e01/`) and committed before E01-R001
started. They are not changes to §2.

**Data-generating mechanisms**
- *Logit-normal "mean 0.2":* μ is solved (80-point Gauss-Hermite) so that
  E[π] = 0.2 at every σ; σ = 0 is the homogeneous cell π = 0.2.
- *Zipf:* π_i = max(0.9 i^−α, 0.001), as in the pilot.
- *Mixture:* 20% of items (rounded) have π = 0; the rest are logit-normal,
  σ = 1, mean 0.2. N = |U| = 400; N_all = 500 is also reported.
- *Families (F):* run j belongs to family j mod F. Logit π_ij = μ + z_i +
  u_{i,f(j)}, z_i ~ N(0, 0.5²), u ~ N(0, τ² = 1.5²), μ such that the
  marginal mean is 0.2 (pilot structure). With K = 10 and F = 3 or 6,
  families have unequal sizes.
- *List dependence (odds ratio θ):* block A = runs 1..K/2, block B = the
  rest. Runs in A are independent Bernoulli(π_i); runs in B have their
  detection odds multiplied by θ for items found in block A. The achieved
  odds ratio is reported.
- *Behavioural response (c):* after an item's first detection its detection
  probability in later runs is min(cπ_i, 1).
- *Nested runs:* u_i ~ N(0, 1); six cut-offs c_j = Φ⁻¹(1 − r_j),
  r = 0.35, 0.29, …, 0.05 (mean 0.2); π_ij = expit(k(u_i − c_j)); K = 6.
- *Identity errors:* ghosts move each detection, with probability f, onto
  a new singleton row; merges then OR round(g · S_obs) random pairs of
  observed rows.
- *Δ(K):* new true items found by K more runs of the same process. Families
  continue with the same families; adaptive runs continue from the items
  found; dependent and nested runs repeat their block or ladder structure.

**Estimands**
- π_i is the probability that one new, independent run of the catcher class
  finds item i, unaffected by earlier runs. For families this means a run
  from a *new* family, so π_i is averaged over the family effect. For
  adaptive and dependent cells it is the base π_i. For nested cells it is
  the mean over the six cut-offs. C = Σ_{found} π_i / Σ_{U} π_i.
- N_LB is Chao2 computed from the expected frequency counts of the *true*
  histories, estimated by their mean over the 500 replicates (S̄ +
  (K−1)/K · Q̄1²/(2Q̄2)).

**Estimators** (E00 suite; validated): Chao-Jost coverage, Turing
coverage 1 − Q1/U, Δ̂(K), Chao2 (iNEXT form) with its log-normal CI,
Chao2-bc, iChao2, jackknife 1 and 2, ICE, Darroch Mt, Chapman (mean over
all pairs and over cross-block pairs i < K/2 ≤ j), and Mh Chao (LB)
log-linear (3 ≤ K ≤ 12). `breakaway_nof1` needs R and is used in E05,
not here.

**Interaction grids** (levels §2 does not list): heterogeneity × ghosts
uses σ ∈ {0, 1, 2} × f ∈ {0, 0.05, 0.15}; shared families × K uses
F ∈ {1, 2, 3, 6} × K ∈ {6, 10, 12}. A cell already defined in an earlier
run (e.g. σ = 1, K = 10 is the base cell) is reused, not re-simulated.
40 distinct cells in R001–R004.

**R005 cells** (§2 says "a subset of 12"): base, N50, N5000, K5, K20,
homog, ln2, zipf1.0, mix20, fam1, beh2, ghost0.15. R005 re-draws the same
datasets (same seeds) and adds iNEXT-style bootstrap intervals (B = 500;
normal and percentile) for C and Δ(K).

**Seeds:** cell idx (its position in `configs/e01/cells.json`) uses
`SeedSequence(20261022, spawn_key=(idx,))`, i.e.
`SeedSequence(20261022).spawn(n)[idx]`; replicate r uses
`spawn_key=(idx, r)`; its bootstrap uses `spawn_key=(idx, r, 1)`.

**Analysis sets for H1a and H1b** (the wording "without identity error or
adaptivity" could include dependent runs):
- *H1a, literal set:* every cell with f = g = 0, c = 1 and K ≥ 5. This
  includes the family, dependence and nested cells.
- *H1a, clean set:* the literal set restricted to independent runs from a
  fixed π (no families, θ ∈ {none, 1}, no nesting). **Gate G1 uses the
  clean set** ("clean simulation cells", ROADMAP). Both verdicts are
  reported.
- *H1b set:* clean cells with logit-normal σ ≥ 1, including the mixture
  cell (target N = |U|).
- H1c uses Chapman averaged over cross-block pairs. H1f compares
  mean(Ĉ − C) between fam1 and fam6, with MCSE √(MCSE₁² + MCSE₆²).
- Verdicts use the point estimates against the §2 thresholds. MCSE is
  reported beside each estimate.

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
| E01-R001 | Base cell + N, K, heterogeneity blocks | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 7765a22 | 11 cells x 500: |bias of C_hat| <= 0.009 at K >= 5 (0.013 at K=3); Delta_hat(K) -3% to -11%; Chao2 log-normal CI covers N in 0.00 (N5000) to 0.92 (N50) of replicates; covers N_LB 0.88-0.95 |
| E01-R002 | Family, dependence, adaptivity, nested blocks | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 7765a22+dirty | 13 cells: C_hat bias fam1 +0.225 / fam6 +0.028; dep1/3 -0.080, dep3 +0.053; beh2 +0.071, beh0.5 -0.148; nest10 -0.017; Chapman cross-block at OR 1/3 -18.5% (vs -35% at OR 1) |
| E01-R003 | Identity-error blocks | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 7765a22+dirty | ghost f=0.05: C_hat -0.053, Chao2 +16%; f=0.15: C_hat -0.158, Chao2 +81%; merge g=0.05: C_hat +0.011, Chao2 -15% (all vs N) |
| E01-R004 | Two-way interactions | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 7765a22+dirty | 13 new interaction cells: clean cells |bias of C_hat| <= 0.006; fam1K6 +0.262; N50K5 80th pct |C_hat - C| 0.122 (only 35% of replicates within 0.05) |
| E01-R005 | Bootstrap interval coverage subset | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 7765a22+dirty | iNEXT-style normal 95% bootstrap CI for C_hat covers the realized C in 0.73-0.91 of replicates in clean cells (base 0.760, MCSE 0.019); percentile CI 0.008-0.84; Delta normal CI 0.32-0.87; bootstrap s.e. underestimates sd(C_hat) (0.0095 vs 0.0123, base) |
| E01-R006 | Exploratory: small-N calibration of the PH1 tolerance (E09/E10 sizes) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | dc94c94+dirty | Exploratory, 24 small-N cells: C_hat unbiased (|bias| <= 0.013) but |C_hat - C| <= 0.05 in only 33-73% of replicates at N=14, K=8 (p 0.2-0.4); 80th pct |C_hat - C| 0.06-0.14 at N=14-20, 0.02-0.08 at N=50 |
| E01-R007 | Exploratory: realized-coverage bootstrap intervals on the R005 datasets | Santosh | succeeded | 2026-10-22 | 2026-10-22 | dc94c94+dirty | Exploratory: realized-coverage bootstrap 95% interval covers C in 0.89-0.97 of replicates in clean cells (base 0.922) vs 0.73-0.91 for the iNEXT interval on the same datasets; one-sided 95% lower bound holds in 0.89-0.94; Delta bias-corrected interval 0.89-0.95 |
| E01-R008 | Exploratory: realized-coverage bootstrap replicated on fresh datasets | Santosh | succeeded | 2026-10-22 | 2026-10-22 | b136211+dirty | Exploratory replication on fresh datasets: realized-coverage interval covers C in 0.896-0.950 of replicates in clean cells; base 0.906 (MCSE 0.013) meets the pre-set >= 0.90 criterion; Delta bias-corrected 0.898-0.954 |
<!-- runs:end -->

## 5. Results

Code: `src/crsafety/sim.py`, `analysis/e01/` (R001–R005 from commit
7765a22; R006–R007 from dc94c94; R008 from b136211; every manifest records a
clean tree). Analysis: `python analysis/e01/analyse.py` →
`results/E01/analysis/` (`summary.md` has every table; `performance.csv`,
`cells.csv`, `hypotheses.csv`, `bootstrap_cells.csv`,
`realized_bootstrap_R00{7,8}.csv`). 40 pre-registered cells × 500
replicates (R001–R004), plus the R005 bootstrap subset. Bias of Ĉ is
mean(Ĉ − C) over replicates; MCSE in parentheses.

### Hypotheses (evaluated as written in §2 and §2a)

| ID | Verdict | Estimate | Runs |
|---|---|---|---|
| H1a, clean set (**gate G1**) | **supported** | max \|bias of Ĉ\| over 14 clean cells = 0.009 (MCSE 0.003), in zipf1.0; ≤ 0.006 in every other clean cell | R001, R002, R004 |
| H1a, literal set | **not supported** | shared-family cells reach +0.26 (fam1K6); dependence ±0.05–0.08; nested −0.017 | R001, R002, R004 |
| H1b (→ PH2) | **not supported** | Chao2 CI covers N in 0.92 (N50) and 0.88 (N50K5) of replicates; 0.79 at K = 20; < 0.50 only when N ≥ 500 and K ≤ 10 | R001, R002, R004 |
| H1c | **not supported** | Chapman (cross-block) at odds ratio 1/3: −18.5% (MCSE 0.3%); at odds ratio 1: −34.9% | R002 |
| H1d (→ PH5) | **supported** | bias of Ĉ at c = 2: +0.071 (MCSE 0.001); at c = 0.5: −0.148 | R002 |
| H1e | **supported** | f = 0.15: Ĉ −0.158 (MCSE 0.001); Chao2 +81% vs N (MCSE 0.6%) | R003 |
| H1f (→ PH4) | **supported** | mean(Ĉ − C), 1 family minus 6 families: +0.197 (MCSE 0.001); fam1 +0.225, fam2 +0.123, fam3 +0.081, fam6 +0.028 | R002 |

**Gate G1 passes**: coverage is accurate in clean cells, so Stage 2 can go
ahead.

**Decision rule 1 (primary estimators).** Chao-Jost Ĉ meets the bias rule
in the base cell (+0.001). Its pre-registered interval does **not** meet the
coverage rule: the iNEXT-style normal bootstrap interval covers the
realized C in 0.760 (MCSE 0.019) of base-cell replicates (R005), and in
0.73–0.91 across the clean R005 cells. The percentile version is worse
(0.008 at N = 5000). The interval explored in R007/R008 does meet the rule
(0.906–0.922 in the base cell); see below and D-010.

**Decision rule 2 († thresholds):** proposals in D-010, for the joint v1
freeze. Nothing in `docs/PREREGISTRATION.md` has been changed.

### Main observations (R001–R005)

- **Coverage is the right headline.** In every clean cell Ĉ is unbiased to
  within 0.01, including Zipf α = 1 where the runs see 8% of the items and
  every richness estimator is 58–96% low. Turing's 1 − Q1/U is biased low
  (−0.004 to −0.067 in clean cells; −0.12 at K = 3); Chao-Jost's correction
  matters.
- **Δ̂(K) is mildly conservative**: −3% to −11% in clean heterogeneous
  cells, +2% when detectability is homogeneous.
- **Counts are lower bounds and reach their bound.** Chao2 is within 1–3
  points of N_LB in the clean cells with N ≥ 500 (e.g. ln2: both −26%),
  except Zipf α = 1 (−66% vs −72%); at N = 50 it sits above the bound
  (N50K5: −12% vs −18%). Its CI covers N_LB in 0.88–0.95 of replicates in
  the clean cells.
  Whether it also covers N depends on N: at N = 50 the interval is wide
  enough to cover N (0.92), so the "intervals miss N" half of PH2 holds only
  for large N (H1b).
- **What breaks coverage, and in which direction:**

  | Violation | Ĉ − C | Note |
  |---|---|---|
  | one shared family (K = 10) | +0.23 | worst failure; shrinks with more families (6 families: +0.03) but only slowly with K (one family: +0.26, +0.23, +0.21 at K = 6, 10, 12) |
  | adaptive "revisit" (c = 2) | +0.07 | overstates completeness (PH5 mechanism) |
  | positive list dependence (θ = 3) | +0.05 | overstates |
  | negative list dependence (θ = 1/3) | −0.08 | understates |
  | adaptive "avoid found" (c = 0.5) | −0.15 | understates |
  | ghosts f = 0.05 / 0.15 | −0.05 / −0.16 | understates (conservative), while Chao2 inflates +16% / +81% |
  | merges g = 0.05 | +0.01 | small |
  | nested runs (k = 10) | −0.02 | small |

- **H1c failed because of a design choice in §2, not the estimator.** The
  dependence factor sits on top of σ = 1 heterogeneity. Heterogeneity alone
  gives a marginal odds ratio of 2.6 between blocks, which cancels the
  designed θ = 1/3 (marginal OR 0.97). Chapman's shift from θ = 1 to 1/3 is
  +16.5 points, but from a −35% baseline.

### Exploratory (labelled; added after results were seen)

- **R006: PH1's tolerance at E09/E10 sizes.** Ĉ stays unbiased at N = 14–50
  (|bias| ≤ 0.013), but one cell's |Ĉ − C| is large: at N = 14, K = 8 and
  mean detectability 0.2, only 33% of replicates are within 0.05 (80th
  percentile 0.14); at mean detectability 0.4, 70–73%. A per-cell 0.05
  tolerance cannot be met by E09 (14 behaviours) or E10 (20 blind spots)
  however good the estimator. Proposal in D-010.
- **R007/R008: an interval for the realized coverage.** The iNEXT interval
  estimates the spread of Ĉ, but C is a property of the sample: sd(Ĉ − C)
  is 0.016 in the base cell, while sd(Ĉ) is 0.012 and the bootstrap s.e. is
  0.0095. `crsafety.coverage_interval` bootstraps the error Ĉ* − C* from the
  Chao pseudo-population, whose probabilities are known. Its 95% interval
  covers C in 0.89–0.97 (R007, same datasets as R005) and 0.896–0.950 (R008,
  fresh datasets) of replicates in clean cells, against 0.73–0.91 for the
  iNEXT interval; base cell 0.922 and 0.906. Its one-sided 95% lower bound
  holds in 0.886–0.952. It is still slightly anti-conservative (about
  0.91–0.93 for a nominal 0.95). For Δ the bias-corrected version is better
  (0.886–0.954 in clean cells vs 0.51–0.98 uncorrected).
- Under the violations (families, c = 2, ghosts) no interval helps: the
  bias is larger than the interval width.

## 6. Deviations

None: nothing in E01 is frozen. R006–R008 are exploratory additions, made
after R001–R005 were seen, and labelled as such in `runs.csv`, here and in
`results/E01/analysis/summary.md`.
