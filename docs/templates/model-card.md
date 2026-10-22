# Model card: <SAE replicate set name>

Structure after Mitchell et al. (2019), with SAE-specific fields.

## Model details
- Base model, layer and site (e.g. Pythia-70M, layer 3, residual stream):
- SAE architecture, width, target L0:
- Training tokens / samples; dataset and its version:
- Number of seeds. **Seed policy:** initialisation only / data order only /
  both. Seed values:
- Software (SAELens / sparsify version), commit, run IDs:
- Licence:
- Contact:

## Intended use
Replicate catches for estimating feature coverage. Not intended as a
canonical feature dictionary.

## Factors
Known sources of variation between seeds; frequency bands; dense and
antipodal latents.

## Metrics
Explained variance, L0, dead-latent fraction, cross-seed recapture rate at
τ = 0.7 (identity rule version).

## Training data
Source, size, preprocessing. Injected marks, if any (E15): how many, at what
frequencies. **Flag clearly that marks are present.**

## Evaluation
Coverage estimates (with run IDs).

## Ethical considerations
None specific beyond the base model's.

## Caveats and recommendations
Feature splitting and absorption; matching-threshold dependence; marks in
E15 checkpoints.
