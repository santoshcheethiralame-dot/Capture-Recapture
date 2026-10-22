# E13: When can we stop auditing? A coverage stopping rule

| Field | Value |
|---|---|
| Status | registered; pilot done (R003); confirmatory R001 needs E02, E06, E09, E10 |
| Owner | Santosh |
| Tier | core |
| Stage | 2 confirmatory (uses data from E02, E06, E09, E10) |
| Depends on | E02, E06, E09, E10 |
| Study hypotheses | PH6 |
| Testbed | resampled campaigns from completed runs; no new runs |
| Compute | CPU |
| Pre-registration | not frozen |

## 1. Question

The practical question for a lab: when is it safe to stop adding audit or
red-team runs? A rule that stops when estimated coverage reaches a target is
only useful if it reaches the target in most campaigns, not just on average.
Technology-assisted document review uses Chao's estimator in exactly this
way: mean recall met its target, but only about 70% of individual reviews
did.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Evaluate coverage-based stopping rules for reliability and runs saved.

### Testbed
Campaigns are built by drawing run orders at random (1,000 permutations)
from the evaluation and reference runs of E02, E06, E09 (each configuration)
and E10 (arms A1 and A2). The truth C(k) after k runs uses the reference
π_i.

### Rules
- **R-point:** stop at the first k ≥ 3 where Ĉ(k) ≥ c*.
- **R-lower:** stop at the first k ≥ 3 where the lower 95% bootstrap bound
  of Ĉ(k) ≥ c*.
- **R-fixed:** always run K_max (the maximum available).
- Targets c* ∈ {0.8, 0.9}.

### Performance measures
- Success rate: share of campaigns with true C ≥ c* at stopping.
- Runs saved vs R-fixed.
- Undershoot when the rule fails.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H13a (→ PH6) | R-lower is reliable | success rate at c* = 0.9, pooled over testbeds with non-adaptive runs | ≥ 0.80 | < 0.70 |
| H13b (→ PH6) | R-lower saves effort | median runs saved | ≥ 30% | < 10% |
| H13c | R-point is not reliable enough | success rate at c* = 0.9 | < R-lower's | ≥ R-lower's |
| H13d | Adaptive campaigns break the rule | success rate, E10 A2 vs A1 | lower for A2 | not lower |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | All rules × testbeds | 1,000 permutations each | CPU hours |

### Sample size
1,000 permutations per testbed. These permutations are not independent of
each other, so intervals use a bootstrap over the underlying items or cells.

### Analysis plan
Confirmatory: H13a to H13d. Exploratory: an adaptive-aware rule using the A3
correction.

### Exclusions and missing data
Testbeds where K_max < 6 (e.g. E02) are reported separately and excluded from
the pooled H13a figure.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| A source experiment is missing | Evaluate on what exists and say so | Yes |
| R-lower never stops (bound too wide) | Report that. It is a usable negative: the budget is too small for the target | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E13-R001 | All rules x testbeds | Santosh | planned |  |  | 5d46498 |  |
| E13-R002 | Pilot (declared): rules on simulated campaigns | Santosh | failed | 2026-10-22 | 2026-10-22 | 5d46498+dirty | Bug: crashed before any campaign finished (stop_lower rejected a SeedSequence seed). Fixed with a test; re-run as E13-R003 |
| E13-R003 | Pilot (declared): rules on simulated campaigns (retry of E13-R002 after bug fix) | Santosh | succeeded | 2026-10-22 | 2026-10-22 | 5870a84+dirty | Pilot, 200 simulated campaigns x 6 worlds: R-lower (D-010 bound) success 0.93-0.985 where the target is reachable, median runs saved 19-69%; R-point 0.50-0.79; both fail with one shared family (0%); Zipf 0.5 never reaches 0.8 within K=16 (rules correctly do not stop) |
<!-- runs:end -->

## 5. Results

**R-lower's bound (D-010).** The "lower 95% bootstrap bound of Ĉ(k)" is the
one-sided lower bound of `crsafety.coverage_interval` (realized-coverage
bootstrap, B = 1,000), because E01 showed that the iNEXT interval
under-covers the realized coverage. Code: `crsafety.stopping`.

**Pilot (declared; simulated campaigns, not the E13 testbeds; not evidence
for H13a–H13d).** E13-R003 (E13-R002 crashed on a seeding bug before any
campaign finished, and was fixed and re-run). 200 fresh simulated campaigns
per world, K_max = 16 (12 for N = 20), B = 500.

| world | target | R-point success | R-lower success | R-lower median runs saved |
|---|---|---|---|---|
| homogeneous | 0.9 | 0.79 | 0.985 | 25% |
| logit-normal σ = 1 | 0.9 | 0.60 | 0.945 | 19% |
| logit-normal σ = 2 | 0.9 | 0.56 | 0.930 | 31% |
| N = 20, K = 12, p̄ = 0.4 | 0.9 | 0.50 | 0.965 | 33% |
| Zipf α = 0.5 | 0.8 / 0.9 | 0 | 0 (never stops; target unreachable by K = 16) | 0% |
| one shared family | 0.9 | 0 | 0 | 25% |

Full table: `results/E13/E13-R003/summary.md`. The pilot suggests R-lower
can meet H13a where runs are independent, and that shared-family
dependence breaks every rule, as H13d anticipates for adaptivity.

### Confirmatory

### Exploratory

## 6. Deviations

_None._
