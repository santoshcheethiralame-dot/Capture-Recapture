# E13: When can we stop auditing? A coverage stopping rule

| Field | Value |
|---|---|
| Status | registered |
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
_No runs yet._
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
