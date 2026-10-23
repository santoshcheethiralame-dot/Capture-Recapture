# Experiment registry

One row per experiment. Pages are in [`experiments/`](experiments/). The
study hypotheses (PH, SH) are in
[`../docs/PREREGISTRATION.md`](../docs/PREREGISTRATION.md). Gates and dates are
in [`../docs/ROADMAP.md`](../docs/ROADMAP.md).

IDs E01–E14 match the experiment menu in `research/README.md` §4. E00 and
E15–E17 were added when the notebook was built.

**Tiers:** *core* experiments are needed for the NeurIPS 2027 paper;
*important* ones strengthen it; *stretch* ones are follow-ups or separate
papers.

| ID | Experiment | Owner | Tier | Stage | Status | Depends on | Hypotheses | Testbed ($0 plan, D-007) | Needed by |
|---|---|---|---|---|---|---|---|---|---|
| [E00](experiments/E00-estimator-library.md) | Estimator library and reference validation | Santosh | core | 0 | analysed (R001–R004 done; awaiting Kushal's review) | none | — | R reference data (sandbox) | 2026-11-01 |
| [E01](experiments/E01-simulation-study.md) | Simulation study under AI-safety violations | Santosh | core | 1 (exploratory) | analysed (R001–R008; gate G1 passed; awaiting Kushal's review) | E00 | PH2; sets † thresholds | simulation (sandbox CPU) | 2026-11-05 (freeze) |
| [E02](experiments/E02-synthsaebench-zoo.md) | Coverage of SAEs, released seed zoo | Santosh | core | 2 | registered | E00, E01 | PH1, PH2, PH3a | SynthSAEBench zoo (Kaggle) | 2026-12-05 (preprint) |
| [E03](experiments/E03-matcher-bakeoff.md) | Matcher bake-off and threshold diagnostics | Santosh | core | 2 | registered | E02 | PH3a | SynthSAEBench zoo (Kaggle) | 2026-12-05 |
| [E04](experiments/E04-single-truth-test.md) | Single-truth test | Santosh + Kushal | important | 2 | registered | E03, E10 pipeline | PH3 | synthetic + local LLM | 2027-01-20 |
| [E05](experiments/E05-error-injection-corrections.md) | Identity-error injection and corrections | Santosh | core | 2 | registered; pilot done (R004–R005) | E01, E02 | PH3b | E01 + E02 histories (CPU) | 2026-12-15 |
| [E06](experiments/E06-own-seeds-grid.md) | Own SAE seeds across worlds (K = 16) | Santosh | important | 2 | registered | E03 | PH1, PH2, PH4 | scaled synthetic worlds (Kaggle) | 2027-03-15 |
| [E07](experiments/E07-covariate-models.md) | Covariates of detectability | Santosh | stretch | 3 | proposed | E02, E06 | SH3 | E02/E06 (CPU) | 2027-04-15 |
| [E08](experiments/E08-auditor-similarity-ladder.md) | Same-model auditors overstate completeness? | Kushal | core | 2 | registered | E00, E01 | PH4 | system-prompt organisms on a Mistral target; Qwen/Llama/Gemma auditors (Kaggle) | 2027-01-25 (workshop: L0 + L3) / 2027-03-15 |
| [E09](experiments/E09-auditbench-coverage.md) | How complete are alignment audits? (AuditBench-lite) | Kushal | core | 2 | registered | E00, E01 | PH1, PH2, SH1 | 14 fine-tuned Gemma-2-2B organisms; black-box + Gemma Scope tools (Kaggle) | 2027-03-31 |
| [E10](experiments/E10-planted-redteam.md) | Red teams vs planted blind spots, adaptive vs not | Kushal | core | 2 | registered | E00, E01 | PH1, PH5 | own monitor (CPU) + open attackers (Kaggle) | 2027-01-25 (workshop) / 2027-03-15 |
| [E11](experiments/E11-real-saes.md) | Coverage of real-model SAEs | Santosh | stretch | 3 | proposed | E03, E05, E06 | SH4 | Pythia-70M, Gemma Scope, board games (Kaggle) | 2027-04-30 |
| [E12](experiments/E12-multi-quirk-organisms.md) | Organisms with many planted quirks | Kushal | stretch | 3 | proposed | E09 pipeline | PH1, PH2 (ext.) | QLoRA organisms (Kaggle) | after NeurIPS |
| [E13](experiments/E13-stopping-rule.md) | Coverage stopping rule | Santosh | core | 2 | registered; pilot done (R003) | E02, E06, E09, E10 | PH6 | resampled campaigns (CPU) | 2027-04-15 |
| [E14](experiments/E14-forecasting-comparison.md) | Coverage vs tail forecasting | Kushal | stretch | 3 | proposed | E10 | exploratory | E10 monitor | after NeurIPS |
| [E15](experiments/E15-planted-mark-calibration.md) | Planted-mark calibration in real systems | Santosh + Kushal | important | 3 | proposed (novelty check Q-N1) | E02/E06, E09/E11 | SH2 | Pythia + organism (Kaggle) | 2027-04-30 |
| [E16](experiments/E16-two-sided-bounds.md) | Two-sided bounds on missed SAE mass | Santosh | stretch | 3 | proposed (Q-N2) | E06, E11 | exploratory | synthetic + Pythia | after NeurIPS |
| [E17](experiments/E17-removed-or-concealed.md) | Removed or concealed? | Kushal | stretch | 3 | proposed (Q-N3) | E09/E12 | exploratory | simulation + organisms | after NeurIPS |
| [E18](experiments/E18-frontier-replication.md) | Frontier-model replication (only if funded) | Kushal | stretch | 3 | proposed (funding) | E08, E09, E10 | PH4, PH5, SH1 | frontier APIs + original AuditBench | if funded |

## Unregistered backlog (exploratory ideas)

None of these is registered. Each needs its own page before running.

- Saturation of LLM idea generation as a free accumulation dataset (Si et
  al. 2024).
- Identity-threshold sensitivity on WildTeaming tactic clusters.
- Attacker-level histories in Tensor Trust.
- MMLU-Redux with 10 to 30 cheap detectors: does more K rescue Kansal's
  negative result?
- Static analysers vs fuzzers on Magma (112 known bugs).
- BAITBENCH (`juanjvazquez/BAITBENCH`, MIT): 1,258 runs as derived evidence
  packets, but only 3 shortcut families. Usable as a cheap check of judging
  and dependence across 7 models; not a richness testbed.

## Run counts

Rendered by `python tools/notebook.py render`.

<!-- counts:start -->
| Exp | Runs | Planned | Running | Succeeded | Failed |
|---|---|---|---|---|---|
| E00 | 4 | 0 | 0 | 4 | 0 |
| E01 | 10 | 0 | 0 | 10 | 0 |
| E02 | 1 | 1 | 0 | 0 | 0 |
| E03 | 0 | 0 | 0 | 0 | 0 |
| E04 | 5 | 2 | 0 | 3 | 0 |
| E05 | 5 | 3 | 0 | 2 | 0 |
| E06 | 15 | 13 | 0 | 1 | 1 |
| E07 | 0 | 0 | 0 | 0 | 0 |
| E08 | 1 | 1 | 0 | 0 | 0 |
| E09 | 3 | 2 | 0 | 1 | 0 |
| E10 | 1 | 1 | 0 | 0 | 0 |
| E11 | 1 | 0 | 0 | 1 | 0 |
| E12 | 0 | 0 | 0 | 0 | 0 |
| E13 | 3 | 1 | 0 | 1 | 1 |
| E14 | 0 | 0 | 0 | 0 | 0 |
| E15 | 5 | 3 | 0 | 2 | 0 |
| E16 | 3 | 1 | 0 | 2 | 0 |
| E17 | 0 | 0 | 0 | 0 | 0 |
| E18 | 0 | 0 | 0 | 0 | 0 |
<!-- counts:end -->
