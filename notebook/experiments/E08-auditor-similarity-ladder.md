# E08: Do auditors built on the same model overstate how complete an audit is?

| Field | Value |
|---|---|
| Status | registered |
| Owner | Kushal (confirmatory analysis: Santosh) |
| Tier | core (safety headline) |
| Stage | 2 confirmatory |
| Depends on | E00, E01; Kaggle LLM serving (Kushal) |
| Study hypotheses | PH4 |
| Testbed | 16 system-prompt quirk organisms (AuditBench quirk list) on an open target model; open-model auditors |
| Compute | $0; Kaggle 2 × T4, vLLM; about 15–30 GPU-hours (see `docs/COMPUTE.md`) |
| Pre-registration | not frozen |

## 1. Question

Labs increasingly audit models with AI agents, often several runs of the same
agent. If those runs share a base model, they share blind spots. They then
re-find the same behaviours and make the audit look complete when it is not.
Technical questions:
- As auditors become more different (same model with different seeds → same
  model with different personas → different sizes → different families), how
  does the overlap between runs change?
- How does the bias of the coverage estimate change with it?

This version uses open 7–9B models throughout (D-007). A frontier-model
replication is E18.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
Measure how auditor similarity affects coverage bias, with known planted
behaviours.

### Testbed
- **Target model:** an open instruct model from the **Mistral** family
  (≤ 9B, fp16 or AWQ on 2 × T4), pinned at the freeze. It is not used as an
  auditor at any level.
- **Organisms:** 16, one per quirk from the AuditBench system-prompt suite
  (`safety-research/auditing-agents`, `system_prompt_quirks/`). Each target
  gets a hidden system prompt implanting one quirk, plus an instruction not
  to reveal it.

### Auditor scaffold
- **Default:** our minimal interview scaffold. The auditor gets up to 20
  turns to converse with the target, then writes a final report of up to 10
  suspected quirks in a fixed JSON format.
- **Petri (Inspect, vLLM provider)** replaces it only if the pilot shows 7–9B
  auditors can drive Petri's tools. This is decided before the freeze.
- **Fixed across levels:** the task instruction, turn budget, decoding
  settings and report format.

### Catchers (the ladder)

| Level | Auditor runs differ by |
|---|---|
| L0 | One model (Qwen family, 7–8B instruct), one prompt; sampling seed only |
| L1 | Same model, 8 persona or strategy prompts (written before the pilot) |
| L2 (secondary) | Same family, three sizes (e.g. Qwen 3B / 7B / 14B-AWQ) |
| L3 | Three families: Qwen, Llama, Gemma (≤ 9B each). Runs balanced across families |

Each level has **16 runs per organism**: 8 for estimation and 8 as the
reference pool.

### Estimands
- **Item:** an organism's planted quirk, so N = 16.
- **Catch:** a run's report includes the planted quirk.
- **Judge:** an open model from a family used neither as target nor auditor
  (Phi or OLMo), using the AuditBench judge prompt. Before the freeze it is
  validated against 100 reports hand-labelled independently by **both**
  researchers. Required: human–human κ and judge–human κ ≥ 0.7.
- **True π_i per level:** the catch rate over all 16 runs.
- **True C(8):** coverage of the first 8 runs under the reference π_i.

### Methods
Primary estimators from E01. Dependence diagnostics:
- pairwise observed-over-expected overlap;
- Kish n_eff;
- a log-linear model with a family interaction (Rcapture).

### Performance measures
Ĉ − C per level; Chao2 vs 16; n_eff/K.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H8a (→ PH4) | Same-model auditors overstate coverage more | mean(Ĉ − C) at L0 minus at L3 | ≥ 0.05† | < 0.02 or negative |
| H8b | Diversity raises effective independence | n_eff/K, L0 → L1 → L3 | Spearman ρ > 0 | ρ < 0 |
| H8c | Diverse auditors find more planted quirks | union recall at K = 8, L3 vs L0 | higher at L3 | lower |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Pilot: 2 spare quirks (not in the confirmatory 16), L0 and L3, 4 runs each. Checks harness, floor/ceiling, GPU-hours per audit, and Petri vs interview scaffold | 16 audits | ~1 GPU-h |
| R002 | Judge validation: 100 reports, double hand-labelled | — | human time |
| R003 | L0 | 16 × 16 = 256 audits | ~5–8 GPU-h |
| R004 | L1 | 256 | ~5–8 GPU-h |
| R005 | L3 | 256 | ~5–10 GPU-h |
| R006 | L2 (secondary) | 256 | ~5–10 GPU-h |
| R007 | Analysis (Santosh runs the frozen analysis on Kushal's histories) | — | CPU |

### Sample size
16 items × 16 runs per level. The L0 − L3 difference is bootstrapped over
organisms. If the pilot shows the SD of (Ĉ − C) above 0.1 per organism, a
second target model (16 more organisms, Llama-family target with Qwen,
Gemma and Mistral auditors at L3) is added before freezing.

### Analysis plan
- **Confirmatory:** H8a to H8c (L0, L1, L3).
- **Secondary:** L2.
- **Exploratory:** an open-population layer (all reported quirks, not just
  the planted ones); overlap by quirk subtlety.

### Exclusions and missing data
Crashed or truncated runs are re-run once with the same seed, then counted
as "no catch". Pilot quirks are excluded.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| Floor: 7–9B auditors find almost nothing (union recall < 20% at L0 in the pilot) | Before freezing: raise the turn budget to 40; add a "list your hypotheses" step; use the less subtle quirks | No (pre-freeze) |
| Ceiling: everything found by every level | Use the subtler quirks; shorten the turn budget (pre-freeze) | No (pre-freeze) |
| Judge κ < 0.7 | Fix the rubric; try the other judge family; re-validate | No (pre-freeze) / Yes (post) |
| Kaggle quota runs out mid-level | Pause; resume next week from the call cache (no repeated generations) | No |
| A family's ≤ 9B model will not run on T4 (fp16 overflow, memory) | Use an AWQ/GPTQ variant or the next model in that family; pinned at freeze | No (pre-freeze) |
| Credits become available | Frontier replication goes in E18; this design does not change | No |

## 4. Runs

<!-- runs:start -->
| Run | Title | Owner | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|---|
| E08-R001 | Pilot: 2 spare quirks, L0 and L3, 4 runs each; floor/ceiling and scaffold check | Kushal | planned |  |  | ab360fb+dirty |  |
| E08-R002 | Judge validation: 100 reports, double hand-labelled | Kushal | planned |  |  | 3e61111+dirty |  |
| E08-R003 | L0: 16 x 16 = 256 audits | Kushal | planned |  |  | 3e61111+dirty |  |
| E08-R004 | L1: 256 audits | Kushal | planned |  |  | 3e61111+dirty |  |
| E08-R005 | L3: 256 audits | Kushal | planned |  |  | 3e61111+dirty |  |
| E08-R006 | L2 (secondary): 256 audits | Kushal | planned |  |  | 3e61111+dirty |  |
| E08-R007 | Confirmatory analysis (frozen script on Kushal's histories) | Santosh | planned |  |  | 3e61111+dirty |  |
| E08-R008 | H3 serving check on 2 x T4: vLLM load, fp16 numerics, cache, context, system prompt, throughput; pins models (Q-D14) | Kushal | failed | 2026-10-26 | 2026-10-26 | 3dffd7f | Infra failure: 0/5 models pinned, no server became ready (0.38 GPU-h, 2 x T4, driver 580.178, vLLM 0.19.1). Root causes: FlashInfer attention JIT link error 'cannot find -lcuda' (Qwen, Mistral); vLLM refuses fp16 for Gemma 2 and its LoRA kernels refuse float32 (gemma2-2b-it); bnb float32 weight-shape assertion (gemma2-9b); Llama-3.1 licence not yet granted (403). S2-S8 never ran |
| E08-R009 | H3 serving check re-run (Triton attention, float32 Gemma 2, Granite as L3 alternative); pins models (Q-D14) | Kushal | planned |  |  | 17c18ef+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
