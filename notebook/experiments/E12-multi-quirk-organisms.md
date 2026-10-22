# E12: Model organisms with many planted quirks

| Field | Value |
|---|---|
| Status | proposed |
| Owner | Kushal |
| Tier | stretch |
| Stage | 3 |
| Depends on | E09 harness; fine-tuning access |
| Study hypotheses | PH1 (extension), PH2 |
| Testbed | own organisms: Q = 8 quirks planted in one 7–8B model |
| Compute | $0; QLoRA on Kaggle T4 + local open-model auditors |
| Pre-registration | not frozen |

## 1. Question

Real models do not have exactly one hidden problem. An audit that finds 3
quirks needs to know whether there are 4 or 40. AuditBench plants one
behaviour per model, so it cannot test this. Here we build organisms with
several planted quirks, so that "how many are left?" has a known answer per
model.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Validate per-model richness and coverage when several failures coexist.

### Testbed
4 organisms. Each is an open 7–8B instruct model with Q = 8 quirks implanted
by synthetic-document fine-tuning (the AuditBench method), graded easy (3),
medium (3) and hard (2). Quirks come from the AuditBench behaviour list plus
4 new ones. Implant success is verified with direct behavioural tests before
auditing; an implant passes if the behaviour shows in ≥ 30% of triggering
prompts.

### Estimands
Per organism: 8 items; true π_i from 8 reference runs; C(K).

### Methods
The E08 interview scaffold with a local open-model auditor, plus Petri and Bloom if they run with open models (decided in the pilot). K = 16 runs each. Primary
estimators.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H12a | Per-organism coverage is estimable | \|Ĉ − C\| | ≤ 0.10 for ≥ 3 of 4 organisms | ≤ 1 of 4 |
| H12b | Chao2 lower bound ≤ 8 and ≥ the number found | per organism | in every organism | — (check) |
| H12c | Tool families are complementary | union recall of 3 tools vs best single tool | higher | not higher |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Implant + verification, 4 organisms | 4 | GPU-hours |
| R002 | Interview-scaffold audits (local auditor) | 4 × 24 | Kaggle GPU |
| R003 | Petri runs (if they run with open models) | 4 × 24 | Kaggle GPU |
| R004 | Bloom runs (if they run with open models) | 4 × 24 | Kaggle GPU |

### Sample size
4 organisms are few. This experiment is a feasibility demonstration with
known truth, not a precise estimate.

### Analysis plan
Confirmatory: H12a to H12c. Exploratory: interference between quirks.

### Exclusions and missing data
Quirks that fail implant verification are removed before auditing, so they
are not part of the truth. The count is reported.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Implants interfere (quirks suppress each other) | Reduce to Q = 5 per organism and re-verify | Yes (pre-audit) |
| No fine-tuning compute | Use system-prompt organisms (E08 fallback) as a weaker substitute | Yes |

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
