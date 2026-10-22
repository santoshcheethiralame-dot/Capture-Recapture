# E03: Matcher bake-off and threshold diagnostics

| Field | Value |
|---|---|
| Status | registered |
| Owner | Santosh |
| Tier | core |
| Stage | 2 confirmatory |
| Depends on | E00, E02-R001/R002 (zoo and oracle histories) |
| Study hypotheses | PH3a |
| Testbed | SynthSAEBench zoo (as in E02) |
| Compute | CPU/GPU; hours |
| Pre-registration | not frozen |

## 1. Question

Before an audit can say "we found the same failure twice", it needs a rule
for "same". For SAE features that rule is a matcher plus a threshold, and it
can move the estimate by orders of magnitude. Technical questions:
- Which matcher identifies the same true feature across seeds most
  accurately?
- Can a diagnostic computed **without** the truth pick a threshold whose
  downstream estimate is close to the best possible?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Score matchers against true identity. Validate a truth-free threshold
diagnostic.

### Testbed
The zoo cells from E02. True identity of each latent is taken from the
oracle catch rule (τ_gt = 0.7). Latents with no true feature are "unmatched
truth".

### Estimands
- **Pairwise truth:** two latents from different seeds are a true match if
  they map to the same true feature.
- **Downstream truth:** C and \|U\| from E02.

### Methods
**Matchers:**
- M1: Hungarian assignment on \|decoder cosine\|.
- M2: strict rule; encoder and decoder Hungarian matchings must agree.
- M3: activation correlation on 10^6 generator samples, then Hungarian.
- M4: mutual nearest neighbour on decoder cosine.
- M5: semantic optimal transport (2605.28567), only if public code exists;
  otherwise dropped, not replaced.

**Thresholds:** τ ∈ {0.30, 0.35, …, 0.95}.

**Clustering across K seeds:** connected components. A sensitivity variant
uses star matching to the seed with the most live latents.

**Truth-free diagnostic (the "plateau rule"):** the largest τ-interval of
width ≥ 0.10 over which the cluster count changes by < 5%. Choose its
midpoint. If no plateau exists, the diagnostic returns "no trustworthy
threshold".

### Performance measures
- Pair precision, recall and F1, overall and by frequency quartile of p_i.
- Cluster ARI against true identity.
- Ghost rate f(τ): the share of true recaptures left unlinked.
- Merge rate g(τ).
- Downstream \|Ĉ − C\| and Chao2 error at each τ.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H3a | Some matcher identifies frequent features well | pair F1, top two frequency quartiles | ≥ 0.90 for at least one matcher | < 0.80 for all |
| H3b | The plateau rule picks a good threshold | \|Ĉ − C\| at plateau τ minus best-τ error | ≤ 0.03 in ≥ 80% of cells where a plateau exists | ≤ 0.03 in < 60% of those cells |
| H3c | Absence of a plateau flags bad cells | Ĉ error in no-plateau cells vs plateau cells | median error higher in no-plateau cells | lower or equal |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | M1, M2, M4 over τ grid, all cells | 35 cells | 1 to 2 h |
| R002 | M3 (needs activations) | 35 cells | 2 to 4 h GPU |
| R003 | M5 if code exists | 35 cells | unknown |
| R004 | Plateau rule + downstream evaluation | 35 cells | minutes |

### Sample size
Fixed by the zoo.

### Analysis plan
- **Confirmatory:** H3a to H3c.
- **Output:** the winning matcher and the plateau rule become the default
  identity rule for E05, E06 and E11. This is recorded as a decision
  (`D-` entry).
- **Exploratory:** matcher failures concentrated in hierarchy siblings
  (absorption and hedging).

### Exclusions and missing data
None.
<!-- prereg:end -->

## 2a. Implementation notes (2026-10-22, before any E03 data)

- Code: `analysis/e03/bakeoff.py` (R001 + R004 in one pass: M1, M2, M4
  over the τ grid; plateau rule; H3a–H3c), using `crsafety.matching` and
  the E02 zoo reader. Tested on a fake zoo; it runs on Kaggle like E02.
- True identity of a latent = its oracle feature (GT-MCC at τ_gt = 0.7).
  Latents with no true feature never form true pairs.
- Frequency quartiles are taken over the firing probabilities of the
  caught features (all seeds of the cell).
- Downstream truth C follows D-011 (default: leave-cell-out; `--truth
  pooled` for the §2 variant).
- M3 (activation correlation) needs the generator's activations (R002, GPU);
  M5 depends on public code existing (R003).

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| No matcher reaches H3a | Gate G2: report it. Move to soft matching with multiple imputation (E05) as the default. Re-weight the paper toward testbeds with identity by construction. | Decision record |
| M3 activations too costly | Use 10^5 samples; report the precision lost | Yes (logged) |
| No plateau anywhere | Report that. It is the expected failure signal. Use E05 corrections | No |
| M5 has no code | Drop M5; do not re-implement it within this experiment | No |

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
