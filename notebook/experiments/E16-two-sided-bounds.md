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
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
