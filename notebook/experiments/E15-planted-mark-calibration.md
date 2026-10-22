# E15: Calibrating detectability by planting known items in real systems

| Field | Value |
|---|---|
| Status | proposed (pending novelty check, `docs/OPEN-QUESTIONS.md` Q-N1) |
| Tier | important (novelty upgrade) |
| Stage | 3 |
| Depends on | E02/E06 (synthetic validation), E09/E11 (real testbeds) |
| Study hypotheses | SH2 |
| Testbed | SAE arm: Pythia-70M activations with injected directions; audit arm: real model plus planted quirks |
| Compute | 1 GPU + API |
| Pre-registration | not frozen |

## 1. Question

Planted failures are often easier to find than real ones. Kansal's label-error
study found exactly this, which weakens any validation that uses planted
truth. Our answer is to plant known items *into the real system*, alongside
its real, unknown failures, at controlled rarity and strength. How often the
planted items are found then measures detectability in the real population.
We use that to correct coverage estimates for the real failures.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Estimate a detectability curve from planted items in a real system, use it to
calibrate coverage for real items, and test the calibration on held-out
planted items.

### Testbed
- **SAE arm.** Into the residual-stream activations of Pythia-70M (layer 3)
  used for SAE training, add M = 400 synthetic unit directions. Each fires
  with probability p_j on a log-uniform grid from 10^-6 to 10^-2, with
  magnitude matched to real latent activations. This is applied to the
  training data only; model behaviour is untouched. Train K = 12 SAE seeds.
- **Audit arm.** Into a model with real, unknown behaviours (an open 8B
  instruct model), plant M = 6 extra quirks of graded subtlety by
  fine-tuning, then run K = 16 audits (E09 harness).

### Estimands
- Detection probability of planted items as a function of their properties
  (frequency, magnitude, subtlety).
- **Held-out check:** a random 25% of planted items are hidden from the
  calibration fit and treated as "unknown". Their true coverage is the
  target.

### Methods
1. Fit a detectability model π(x) on the 75% training marks: logistic in
   log p_j and magnitude; ordinal subtlety for audits.
2. Combine it with real items' observed covariates in a Horvitz-Thompson
   estimate of unseen mass and calibrated coverage.
3. Compare with uncalibrated Chao-Jost coverage.

### Performance measures
\|Ĉ_calibrated − C\| and \|Ĉ_uncalibrated − C\| on held-out marks;
Δ-prediction on held-out seeds.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H15a (→ SH2) | Calibration is accurate on held-out marks | \|Ĉ_cal − C\| | ≤ 0.05 | > 0.10 |
| H15b | Calibration beats the uncalibrated estimate | error reduction | ≥ 30% | none |
| H15c | Injected marks behave like real features | catch rate vs frequency curve, marks vs real (matched by frequency band) | overlapping CIs in ≥ 3 of 4 bands | otherwise |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Novelty check (literature) before anything else | — | — |
| R002 | SAE arm: injection + 12 seeds | 12 | per COMPUTE.md |
| R003 | Audit arm: implant + verify + 16 audits | 16 | GPU + API |
| R004 | Calibration analysis | — | CPU |

### Sample size
400 marks (300 for fitting, 100 held out) give a detection-curve SE of about
0.03 per band.

### Analysis plan
Confirmatory: H15a to H15c. Exploratory: whether marks change the real
features learned (interference), measured by recapture of real features with
and without injection.

### Exclusions and missing data
None planned.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| The novelty check finds this already done | Cite it. Keep E15 as a replication and extension if still useful; otherwise drop it and record a decision | Decision record |
| Injected marks distort the real features (interference) | Reduce M to 100 and the magnitude by half; report the interference | Yes |
| H15c fails (marks are easier than real features) | Report it. It shows where planted-truth validation misleads, which is itself a contribution | No |

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
