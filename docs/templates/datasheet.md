# Datasheet: <dataset name>

Structure after Gebru et al. ("Datasheets for Datasets"), with fields for
detection-history data.

## Motivation
- Why was it created? Which experiments (IDs) produced it?

## Composition
- What is an instance? (One row = one item × one run: found / not found.)
- Items: what they are (planted behaviour, blind spot, SAE feature) and how
  many.
- Runs: catcher, budget, number.
- True-identity labels: present? How produced (instrumented / planted /
  oracle matching)?
- Matched-identity labels: identity rule and version, threshold.
- Does it contain attack text or transcripts? Which access tier
  (`docs/DISCLOSURE.md`)?

## Collection process
Generator versions and parameters; model snapshots; dates; seeds; run IDs.

## Preprocessing / labelling
Deduplication, judge model, judge validation (κ), exclusions with counts.

## Uses
- Suitable: evaluating coverage and richness estimators; studying identity
  error.
- Unsuitable: training models to evade monitors; any use against deployed
  systems.

## Distribution
Host, licence (CC BY 4.0 unless upstream terms differ), DOI, canary block
(if attack text is present), held-out split.

## Maintenance
Contact; how errata are reported; versioning.

## Croissant
Core fields (name, description, url, license, creator, datePublished,
version, conformsTo) plus the responsible-AI fields, if submitted to the
NeurIPS Evaluations & Datasets track.
