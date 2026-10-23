# E15: Calibrating detectability by planting known items in real systems

| Field | Value |
|---|---|
| Status | proposed (pending novelty check, `docs/OPEN-QUESTIONS.md` Q-N1) |
| Owner | Santosh (SAE arm); Kushal (audit arm) |
| Tier | important (novelty upgrade) |
| Stage | 3 |
| Depends on | E02/E06 (synthetic validation), E09/E11 (real testbeds) |
| Study hypotheses | SH2 |
| Testbed | SAE arm: Pythia-70M activations with injected directions; audit arm: real model plus planted quirks |
| Compute | $0; Kaggle T4 (SAE seeds, QLoRA, local auditors) |
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
| R003 | Audit arm: implant + verify + 16 audits | 16 | Kaggle GPU |
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

## 2a. Implementation notes (2026-10-23; SAE arm, before R002)

- R001 (novelty) is done: nothing prior does the full design
  (`research/notes/J2-e15-novelty.md`).
- Estimator: `crsafety.calibrate`, tested in `tests/test_calibrate.py`.
  - Detectability is fitted on *all* training marks with the full binomial
    likelihood; found and unfound marks are both known.
  - Real items get Horvitz-Thompson C_cal, N̂ and Δ_cal from their
    predicted π.
  - `proxy_map` maps observed covariates (latent firing frequency,
    contribution magnitude) to the true scale, fitted on found training
    marks.
  - The interval is a bootstrap over marks (refit) and items.
  - In a simulation with mild heterogeneity, C_cal is unbiased, but
    Chao-Jost is about as accurate. Calibration pays only where Chao-Jost
    fails, which is the question H15b asks.
- SAE arm: `analysis/e15/inject.py` (`marks`, `train`, `stats`). Master
  seed 20261037.
  - Marks: random unit directions; p_j on the log-uniform grid
    10⁻⁶–10⁻², randomly assigned; 25% held out.
  - Magnitudes are drawn from real latent contribution magnitudes (from
    E11-R003 SAEs) when available.
  - The marks are added by a permanent TransformerLens hook on
    `blocks.3.hook_resid_post`, with their own generator reseeded per SAE.
    Seeding is otherwise as in E11-R001.
  - Smoke-tested on CPU with the tiny local model (all three commands).
- R004: `analysis/e15/analyse.py`, tested on synthetic SAEs
  (`tests/test_e15.py`). Seeds 0–7 are estimation seeds; 8–11 are held-out
  seeds for the Δ check.
- **For the freeze:**
  1. True π of a mark: the catch rate over all 12 seeds (pooled, proposed)
     or over the 4 held-out seeds. This is the same issue as D-011.
  2. Primary covariates for H15a/b: observed, through `proxy_map`
     (proposed); oracle covariates reported as a ceiling.
  3. H15c compares marks (by true p) with matched real clusters (by observed
     frequency). Real items enter only once found, so their catch rates are
     conditional on at least one catch. Proposed: compare marks
     conditional on ≥ 1 catch as well.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| The novelty check finds this already done | Cite it. Keep E15 as a replication and extension if still useful; otherwise drop it and record a decision | Decision record |
| Injected marks distort the real features (interference) | Reduce M to 100 and the magnitude by half; report the interference | Yes |
| H15c fails (marks are easier than real features) | Report it. It shows where planted-truth validation misleads, which is itself a contribution | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E15-R001 | Novelty check (Q-N1): planted marks to calibrate detectability in a real ML system | Santosh | succeeded |  | 2026-10-23 | 854a1ad | Q-N1: no prior plant-fit-calibrate-validate design found (4 searches); closest Kansal undiscovered-failures (planted failures, no transfer to real items), AuditBench / RL auditors (planted behaviours score auditors), error seeding, privacy canaries. Notes: research/notes/J2-e15-novelty.md |
| E15-R002 | SAE arm: 400 marks injected into Pythia-70M L3, 12 SAE seeds + latent stats (Kaggle) | Santosh | planned |  |  | d4c14b1+dirty |  |
| E15-R003 | Audit arm: implant 6 graded quirks + verify + 16 audits (Kaggle; Kushal) | Kushal | planned |  |  | d4c14b1+dirty |  |
| E15-R004 | Calibration analysis, SAE arm (CPU) | Santosh | planned |  |  | 8cc0c13+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
