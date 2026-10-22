# E14: Coverage estimates vs tail forecasting

| Field | Value |
|---|---|
| Status | proposed |
| Owner | Kushal |
| Tier | stretch |
| Stage | 3 |
| Depends on | E10 |
| Study hypotheses | exploratory |
| Testbed | E10 planted-blind-spot monitor |
| Compute | $0; Kaggle T4 (more attacker runs at larger budget) |
| Pre-registration | not frozen |

## 1. Question

Other methods forecast the rate of failure at deployment scale: Jones et al.
(2025), and the power-law scaling of Best-of-N jailbreaking. These forecast
how often a *known* bad event happens. Coverage estimates say how many
*kinds* of failure remain. A lab may want both. Does each predict what a 10×
larger red team actually finds?

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Compare predictions of success at 10× budget from:
1. coverage and Δ(m) estimates;
2. a Best-of-N power-law fit, −log(ASR) = a·N^(−b);
3. a Jones-style extreme-value forecast of the largest elicitation
   probability.

### Testbed
The E10 monitor. 4 attacker runs at 10× budget, per arm A1 and A2, give the
"future" truth.

### Estimands
New blind spots found at 10× budget, and the attack success rate at 10×
budget.

### Methods
As above, all fitted on the E10 evaluation runs only.

### Performance measures
Relative prediction error for each target quantity.

### Hypotheses and decision rules
Exploratory. No confirmatory thresholds. Results are reported as a
comparison table.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | 10× budget runs, A1 and A2 | 4 + 4 | per COMPUTE.md |
| R002 | Fits and comparison | — | CPU |

### Sample size
Small. Exploratory only.

### Analysis plan
Exploratory comparison only.

### Exclusions and missing data
None.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| 10× runs unaffordable | Use 4× budget and say so | Yes |

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
