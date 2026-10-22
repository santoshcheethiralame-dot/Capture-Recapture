# E04: The single-truth test ("how many failure modes is one failure mode?")

| Field | Value |
|---|---|
| Status | registered |
| Owner | Santosh (SAE arm); Kushal (attack arm) |
| Tier | important |
| Stage | 2 confirmatory |
| Depends on | E00, E03 (default matcher), E10 identity pipeline (attack arm) |
| Study hypotheses | PH3 (supporting) |
| Testbed | synthetic re-expressions of known items |
| Compute | $0; CPU + a local open model on Kaggle (attack arm) |
| Pre-registration | not frozen |

## 1. Question

A pipeline that splits one real failure mode into many apparent ones will
report a long tail of "unseen" failures that does not exist. This happened in
microbiology: sequencing one E. coli template "found" many species (Kunin et
al. 2010). Technical question: when the true number of items is 1 (or 3, or
10), what does our full identity-plus-estimation pipeline report?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Measure spurious splitting by the identity pipeline in a setting where the
answer is known and tiny.

### Testbed
- **SAE arm.** Take N_true ∈ {1, 3, 10} true features from the SynthSAEBench
  world. For each of K = 8 synthetic runs, emit a noisy copy of each
  feature's direction. Noise is drawn from the empirical distribution of
  cross-seed cosine between true matches in E02 (oracle). Also emit split
  variants (two latents summing to the feature) with probability 0.2 and
  absorbed variants with probability 0.1.
- **Attack arm.** Take N_true ∈ {1, 3, 10} attack strategies from the E10
  rubric. For each of K = 8 runs, an LLM writes a fresh concrete attack
  implementing each strategy (different wording, payload and order).
  Distractors are added: near-miss attacks that do not implement any
  strategy, at 20% of findings.

### Estimands
N_true, and true coverage C = 1 (every item is found in every run by
construction).

### Methods
- SAE arm: the default identity rule from E03.
- Attack arm: the E10 judge-based identity pipeline (rubric labelling plus
  embedding clustering).
- Estimators: the primary set, plus the Chiu-Chao corrected f1 and an f1-free
  estimator (if validated in E00).

### Performance measures
Number of clusters / N_true; Chao2 / N_true; Ĉ; share of distractors
absorbed into real clusters.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H4a | The SAE identity rule does not invent items | mean clusters / N_true | ≤ 1.2 | > 1.5 |
| H4b | The attack identity pipeline does not invent items | mean clusters / N_true | ≤ 1.2 | > 1.5 |
| H4c | Singleton correction repairs residual splitting | Chao2 / N_true with correction | ≤ 1.5 when uncorrected > 2 | no improvement |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | SAE arm, N_true ∈ {1, 3, 10} | 200 replicates each | minutes |
| R002 | Attack arm, N_true ∈ {1, 3, 10} | 20 replicates each | ~1–3k LLM calls |

### Sample size
R001: 200 replicates per level gives MCSE of the cluster ratio < 0.02.
R002: limited by Kaggle GPU time; reported with bootstrap CIs.

### Analysis plan
- **Confirmatory:** H4a to H4c.
- **Exploratory:** which kinds of variant cause splits.

### Exclusions and missing data
LLM generations that fail to implement the strategy (checked by a second
judge) are counted and excluded from the "real" set. The exclusion rate is
reported.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| H4a or H4b fails (the pipeline invents items) | This is a key finding. Tighten the rule and re-run as a **new, separately registered** version (E04b). Report both. Any downstream experiment using the failed rule must apply E05 corrections. | No (new registration) |
| LLM generations are too similar (trivially matched) | Raise the paraphrase temperature and add a "use a different surface form" instruction. Measure diversity (mean pairwise embedding cosine) and report it | No |

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
