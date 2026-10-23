# E16: Two-sided bounds on what an SAE missed

| Field | Value |
|---|---|
| Status | proposed (pending novelty check, Q-N2) |
| Owner | Santosh |
| Tier | stretch (novelty upgrade) |
| Stage | 3 |
| Depends on | E02, E06, E11 |
| Study hypotheses | exploratory |
| Testbed | SynthSAEBench worlds (truth), then Pythia (E11) |
| Compute | CPU/GPU |
| Pre-registration | not frozen |

## 1. Question

Overlap-based estimates only give a floor: "at least this much is missing".
For SAEs there is extra information that ecology never has. Missed features
must live in the reconstruction error. So the part of the error that is not
explained by known noise or linear "dark matter" gives a ceiling on the mass
of missed features. A floor plus a ceiling would bracket the answer.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Build an upper bound on missed feature mass from the SAE residual. Combine it
with the coverage-based lower bound. Check that the bracket contains the
truth in synthetic worlds.

### Testbed
- **Synthetic:** the E06 worlds, where the true missed mass is known.
- **Real:** Pythia-70M (E11).

### Estimands
Missed feature mass M_miss: the share of total activation energy (Σ p_i E[c_i²])
carried by features not caught by any of K seeds.

### Methods
- **Lower bound:** 1 − Ĉ, converted to energy units with observed per-latent
  energies.
- **Upper bound:** residual energy minus its linearly predictable part
  (Engels et al. 2024 decomposition), divided by total energy.

### Performance measures
Bracket validity (lower ≤ M_miss ≤ upper) and bracket width.

### Hypotheses and decision rules
Exploratory. Report validity rate and width across worlds. A bracket is
"useful" if it is valid in ≥ 90% of cells and narrower than 0.2.

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Novelty check | — | — |
| R002 | Synthetic worlds | E06 cells | CPU/GPU hours |
| R003 | Pythia-70M | E11 seeds | GPU hours |

### Sample size
As in E06 and E11.

### Analysis plan
Exploratory only.

### Exclusions and missing data
None.
<!-- prereg:end -->

## 2a. Implementation notes (2026-10-23, before R002)

- R001 (novelty check) is done: nothing prior found
  (`research/notes/J-e16-novelty.md`).
- R002 script: `analysis/e16/bracket.py`, run per E06 cell on the
  `train.py` output. §2 leaves these choices open; they are fixed here
  (details in the script docstring):
  - truth in hidden-space energy, with §2's per-feature share alongside;
  - two lower bounds: L0 = 1 − Ĉ unconverted, and L1 converted with
    singleton latent energies;
  - three upper bounds, each the tightest over seeds: total residual,
    Engels-style linearly predictable residual, and §2's literal "residual
    minus its linearly predictable part".
  §2's wording of the upper bound reads as the nonlinear error, which is the
  part Engels et al. attribute to SAE error, not to missing features. Both
  readings are reported.
- **Concern before R002 (from a CPU smoke test on a toy world, 96
  features, 6 seeds; smoke output, not a result).** The oracle catch rule
  (|cos| ≥ 0.7) counts a feature as missed even when other latents
  reconstruct it in part. In the toy world, the energy of the "missed"
  features (0.18) was above the total residual energy (0.07), so no
  residual-based quantity could bound it. If this holds in E06 worlds, the
  estimand should be the *unreconstructed* energy of missed features (their
  share of the residual) rather than their total energy. R002 reports both;
  the choice is made before R002 runs and logged as a deviation if it
  changes §2.

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| The upper bound is trivially loose (≥ 0.5) | Report it and drop the idea from the main paper | No |
| Already published | Cite it and drop | Decision record |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E16-R001 | Novelty check (Q-N2): residual-based upper bound on missed SAE features | Santosh | succeeded |  | 2026-10-23 | 33700e7 | No prior residual upper bound on missed SAE features and no seed capture-recapture found (5 searches); closest Engels et al. 2025 dark-matter decomposition (basis of the upper bound). Notes: research/notes/J-e16-novelty.md |
| E16-R002 | Synthetic worlds: bracket per E06 cell (after E06 training on Kaggle) | Santosh | planned |  |  | 10b3aeb+dirty |  |
| E16-R003 | Pilot (declared, exploratory): residual bounds vs missed-mass estimands (a) total and (b) unreconstructed, 2 small CPU worlds x 6 seeds | Santosh | running | 2026-10-23 |  | 5253a2d+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
