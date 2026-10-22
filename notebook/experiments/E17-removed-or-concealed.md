# E17: Removed or concealed? Detection-corrected survival of traits across safety training

| Field | Value |
|---|---|
| Status | proposed (pending novelty check, Q-N3) |
| Owner | Kushal |
| Tier | stretch (links to idea 1) |
| Stage | 3 |
| Depends on | E09 or E12 harness; E01 simulation code |
| Study hypotheses | exploratory |
| Testbed | simulation first; then organisms trained to remove vs suppress a quirk |
| Compute | $0; QLoRA on Kaggle T4 + local auditors |
| Pre-registration | not frozen |

## 1. Question

After safety training, an audit stops finding a bad trait. Was the trait
removed, or did the model learn to hide it? A naive before/after comparison
treats "not found" as "gone". Open-population capture-recapture models
(Cormack-Jolly-Seber) estimate survival while correcting for imperfect
detection. Applied to repeated audits before and after training, they
separate "detection fell" from "the trait is gone".

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Test whether detection-corrected survival separates removal from concealment.

### Testbed
1. **Simulation.** Traits with known survival φ and detection p before and
   after an intervention. Concealment means p drops while the trait
   survives; removal means φ drops.
2. **Organisms.** For each of 3 quirks, two variants of the same model:
   - *(a) removed:* the quirk is trained out on data that covers its trigger
     contexts;
   - *(b) concealed:* the model is trained to hide the quirk when probed in
     audit-like contexts, but keeps it in deployment-like contexts.

   Truth is verified by deployment-context behavioural tests that auditors
   never see.

### Estimands
Per-trait survival φ (0 for removed, 1 for concealed) and post-training
detection probability.

### Methods
Repeated audits (K = 12) at three time points: before training, after one
epoch, after training. Fit Cormack-Jolly-Seber with detection probability
varying by time, and compare with naive survival (found after / found
before).

### Hypotheses and decision rules
Exploratory. Report whether CJS φ̂ separates (a) from (b) where the naive
comparison does not.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Novelty check | — | — |
| R002 | Simulation | 500 per cell | CPU |
| R003 | Organisms + audits | 6 organisms × 3 time points × 12 | Kaggle GPU |

### Sample size
Simulation n_sim = 500. The organism study is small and exploratory.

### Analysis plan
Exploratory only.

### Exclusions and missing data
None.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Concealment organisms cannot be built reliably | Report the simulation only | Yes |
| The idea overlaps with idea 1's project | Coordinate scope; merge if the same person runs both | Decision record |

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
