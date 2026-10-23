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

## 2a. Implementation notes (2026-10-23; SAE arm, before any confirmatory run)

Code: `analysis/e04/sae_arm.py`, tests `tests/test_e04.py`. §2 leaves these
open; they are fixed here and go to the joint freeze (`docs/FREEZE-V1.md`).
- **Noise.** `zoo.py histories` writes `true_match_cosines.json`: |cos|
  between latents of two seeds that the oracle assigns to the same true
  feature (both ≥ 0.7), pooled over cells as 1,001 quantiles. Each emitted
  latent is rotated to |cos| = √ρ from its intended direction, with ρ drawn
  from that distribution. Two plain copies then have cross-seed |cos| ≈ ρ.
- **Split variant** (probability 0.2 per feature and run): the pieces are
  λt + r and (1 − λ)t − r, with λ ~ U(0.3, 0.7), r ⊥ t and |r| = 0.5. They
  sum to t; at λ = 0.5 each piece has |cos| 0.71 to t.
- **Absorbed variant** (probability 0.1): t + γ t_j, with γ ~ U(0.3, 1) and
  t_j a random world feature outside the N_true set.
- **Identity rule.** `--tau` takes the E03 winner (a fixed threshold, or
  `plateau`). It is unknown until E03, so R001 waits for it.
- **Singleton correction (H4c).** Chiu-Chao is dropped (D-009, Q-D10), so
  the correction is E05's first-order count correction (b). f̂ comes from
  ≤ 200 labelled candidate pairs: each latent's nearest latent in every
  other run, stratified over |cos| bins. The oracle-f correction is also
  reported.
- Seeds: `SeedSequence(20261026, spawn_key=(level, replicate))`; pilots use
  replicate keys from 9000.

**Pilot E04-R003 (declared; random directions, d = 768, fixed ρ = 0.9,
τ = 0.7 placeholder).** Under the generator as written, clusters / N_true is
3.4–3.6 at every level. From a regression on the stored replicates, each
split adds about 1.5 clusters and each absorbed variant about 0.2. Neither
piece of a split is close enough to t for a one-to-one matcher, so split
pieces become their own items. H4a therefore cannot be supported by any
one-to-one identity rule at these settings: as written, it tests the
generator's split geometry more than the rule. The ghost correction brings
Chao2 / N_true from 6–32 down to 0.72–0.75. It over-corrects because splits
add detections, which the correction assumes are conserved.
Options for the freeze (no change is made here):
1. keep §2 as written and report H4a as a lower bound on splitting;
2. score H4a only on plain and absorbed latents, reporting splits separately
   (they are real SAE behaviour);
3. fix the split geometry from E02 (cos of split children to the parent).

Proposed: option 2, plus option 1's numbers as a secondary result.

**Pilot E04-R004 (declared, exploratory; keys 9200–9599; same placeholders
as R003).** Each of the 1,200 replicates is scored both ways, at split
|r| = 0.5 and 0.25:
- Option 1 (all latents): clusters / N_true is 3.36–3.50 at |r| = 0.5 and
  2.11–2.25 at |r| = 0.25. It depends on the split geometry, which §2 does
  not fix.
- Option 2 (split latents excluded): 1.17–1.23 at both geometries, so it
  does not depend on that geometry. It sits on the 1.2 threshold because
  absorbed variants alone add about 0.2 clusters per feature (R003).
- The ghost-corrected Chao2 / N_true is 0.74–0.76 at |r| = 0.5 and
  0.99–1.26 at |r| = 0.25.

For the freeze: option 2 makes H4a a test of the identity rule rather than
of the generator. Its threshold of 1.2 is borderline at τ = 0.7. The real
test uses the E03 rule and the E02 noise, so this pilot sets no threshold
(none is changed).

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| H4a or H4b fails (the pipeline invents items) | This is a key finding. Tighten the rule and re-run as a **new, separately registered** version (E04b). Report both. Any downstream experiment using the failed rule must apply E05 corrections. | No (new registration) |
| LLM generations are too similar (trivially matched) | Raise the paraphrase temperature and add a "use a different surface form" instruction. Measure diversity (mean pairwise embedding cosine) and report it | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E04-R001 | SAE arm, N_true in {1,3,10}, 200 replicates (confirmatory; after freeze, E02 noise, E03 rule) | Santosh | planned |  |  | 96bfa69 |  |
| E04-R002 | Attack arm, N_true in {1,3,10}, 20 replicates (Kaggle LLM) | Kushal | planned |  |  | 96bfa69+dirty |  |
| E04-R003 | Pilot (declared, separate seeds): SAE-arm mechanics, random directions d=768, fixed noise rho=0.9 | Santosh | succeeded | 2026-10-23 | 2026-10-23 | 96bfa69+dirty | Pilot, 600 replicates, 17 s: under the pre-registered generator clusters / N_true = 3.4-3.6 at every N_true (regression on counts: each split adds ~1.5 clusters, each absorbed variant ~0.2; impure clusters 0); Chao2 / N_true 6-32, ghost-corrected 0.72-0.75; C_hat 0.74-0.81 vs truth 1 |
| E04-R004 | Pilot (declared, exploratory): H4a under freeze options 1 and 2, split |r| in {0.5, 0.25}, 200 reps per level | Santosh | succeeded | 2026-10-23 | 2026-10-23 | 3b58eb4+dirty | Pilot, 1200 replicates: clusters / N_true 3.36-3.50 at |r| = 0.5 and 2.11-2.25 at |r| = 0.25 (option 1); without split latents (option 2) 1.17-1.23 at both, i.e. on the 1.2 threshold, from absorbed variants alone; ghost-corrected Chao2 / N_true 0.74-0.76 (|r| 0.5) and 0.99-1.26 (|r| 0.25) |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
