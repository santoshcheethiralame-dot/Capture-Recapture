# E18: Frontier-model replication (only if credits arrive)

| Field | Value |
|---|---|
| Status | proposed (triggered only by funding; see D-007) |
| Owner | Kushal |
| Tier | stretch |
| Stage | 3 |
| Depends on | E08, E09, E10 completed on open models |
| Study hypotheses | PH4, PH5 (replication); SH1 |
| Testbed | E08 ladder, E10 monitor and the original AuditBench, with frontier API models as auditors and attackers |
| Compute | API credits (e.g. OpenAI researcher programme, up to $1,000) + rented GPUs for the original AuditBench |
| Pre-registration | not frozen; written in full only when funding is confirmed |

## 1. Question

Do the open-model results hold when the auditors and red teams are frontier
models, as labs actually use them? The $0 design (D-007) states this as a
limitation. E18 removes it if funding allows.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Replicate H8a (same-model auditors overstate coverage) and H10b/H10c
(adaptive bias and its correction) with frontier models. If GPUs are
available, run the original AuditBench (E09's full design: 56 Llama-3.3-70B
organisms, Haiku 4.5 investigator).

### Design (sketch; frozen in full only when funded)
- **E08 ladder:** frontier models replace the open models at every level.
  L0 is one frontier model with different seeds; L3 mixes frontier families.
- **E10:** frontier attackers on the same monitor and blind spots.
- **Original AuditBench** (`safety-research/auditing-agents`):
  `--max-tokens 25000`, 16 runs per target, tool configurations chosen
  before freezing.
- Same estimators, judges and thresholds as the open-model versions, so the
  results are directly comparable.

### Hypotheses and decision rules
The same as H8a, H10b and H10c. A replication is "consistent" if the
frontier estimate lies within the open-model 95% CI, or on the same side of
the threshold.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Budget-matched pilot | — | ≤ 10% of credits |

### Sample size
Set by the credits available, at freeze time.

### Analysis plan
Comparison with the open-model results.

### Exclusions and missing data
As in E08, E09 and E10.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Credits smaller than needed | Replicate E08's L0 and L3 only (the core of PH4) | No (decided at freeze) |
| Provider terms forbid the red-team arm | Run only E08 (auditing); E10 stays open-model only | No |

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
