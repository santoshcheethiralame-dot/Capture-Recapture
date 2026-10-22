# E09: How complete are AI alignment audits? (AuditBench)

| Field | Value |
|---|---|
| Status | registered |
| Tier | core (safety headline) |
| Stage | 2 confirmatory |
| Depends on | E00, E01; AuditBench code, models and agent |
| Study hypotheses | PH1, PH2, SH1 |
| Testbed | AuditBench (arXiv 2602.22755): 56 targets, 14 hidden behaviours |
| Compute | GPU serving for 70B LoRA targets (2–4 × 80 GB) + Haiku 4.5 API, about $0.4–1 per run; full design about $1.5–4k, reduced about $0.6–1.5k (see `docs/COMPUTE.md`) |
| Pre-registration | not frozen |

## 1. Question

An alignment audit run by an AI agent finds some hidden behaviours and not
others. Can the overlap between repeated audit runs tell the auditor how much
is still hidden? And do different auditing tools (black-box prompting,
white-box interpretability, training-data analysis) find different things?
AuditBench lets us check the answers against the planted truth.

## 2. Pre-registration

<!-- prereg:start -->
### Aims
1. Validate coverage and richness estimates on audits with known planted
   behaviours.
2. Measure how complementary the tool configurations are.

### Testbed
AuditBench (`github.com/safety-research/auditing-agents`): 56 targets = 14
behaviours × 2 implantation methods × 2 adversarial-training levels. Each
target is a LoRA on Llama-3.3-70B-Instruct (HF `auditing-agents/llama_70b_*`),
served with vLLM on 2–4 × 80 GB GPUs.

The 14 behaviours: animal_welfare, contextual_optimism, defend_objects,
defer_to_users, hardcode_test_cases, increasing_pep, self_promotion,
ai_welfare_poisoning, hallucinates_citations, reward_wireheading,
secret_loyalty, flattery, emotional_bond, anti_ai_regulation.

**Fixed run settings** (repo defaults vary, so they are set explicitly):
- investigator `claude-haiku-4-5-20251001`;
- `--max-tokens 25000` (as in the paper);
- `--n-candidate-quirks 10 --max-final-quirks 10`;
- `--n-runs 16`.

**Per-run outputs:** `transcript.json`, `research_log.md`, and `quirks/*.md`
(up to 10 predicted quirks). Scoring uses the repo's judge
(`claude-sonnet-4-6`, `evaluate_all_quirks_batch`), giving 0/1 per run.

Tool configurations: 4 chosen from AuditBench's 13 before seeing any
results:
- **T1:** default black-box chat;
- **T2:** the best scaffolded black-box configuration reported in the paper;
- **T3:** a white-box (interpretability) configuration;
- **T4:** a training-data or Petri-summary configuration.

The exact mapping to AuditBench configuration names is recorded at freeze.

### Design A: targets as items (known N)
- **Item:** a target, so N_all = 56.
- **Catch:** a run's predictions include the planted behaviour.
- Runs per target per configuration: K = 16 (8 for estimation, 8 held out).
- **True π_i:** the empirical rate over all 16 runs.
- **True C(8):** π-weighted share of targets caught in the first 8 runs.
- **Catchable set** U_c: targets caught at least once in all 4 × 16 runs.
  Targets never caught by any configuration form the measured "uncatchable
  by these tools" class.

### Design B: tool configurations as lists
The 4 configurations are 4 lists over the 56 targets. Each list is "caught at
least once in that configuration's 8 estimation runs". Log-linear models test
pairwise interactions between configuration families.

### Design C: open population (exploratory)
Each run's 10 predictions are clustered into behaviour hypotheses across
runs. This estimates richness of "things auditors report", which includes
genuine side effects and false positives. No truth beyond the planted
behaviour.

### Methods
Primary estimators from E01; log-linear models (Rcapture/dga) for Design B;
leave-half-out Δ prediction.

### Performance measures
- Ĉ − C per configuration.
- Chao2 relative to \|U_c\| and to 56.
- Δ̂ from runs 1–8 against new targets actually found in runs 9–16.
- The interaction estimates in Design B.

### Hypotheses and decision rules

| ID | Hypothesis | Measure | Supported if | Not supported if |
|---|---|---|---|---|
| H9a (→ PH1) | Audit coverage is estimable | \|Ĉ − C\| per configuration | ≤ 0.05† for ≥ 3 of 4 configurations | ≤ 1 of 4 |
| H9b (→ PH2) | Counts miss the uncatchable class | Chao2 vs 56 | Chao2 < 56 for every configuration where U_c < 56 | — (descriptive check) |
| H9c | Leave-half-out prediction works | \|Δ̂ − Δ\| / max(Δ, 1) | ≤ 0.5 for ≥ 3 of 4 configurations | ≤ 1 of 4 |
| H9d (→ SH1) | Black-box and white-box tools are complementary | log-linear interaction between T1/T2 and T3 | negative, 95% CI excludes 0 | positive, CI excludes 0 |

### Planned runs

| Run | Configuration | Replicates | Expected cost |
|---|---|---|---|
| R001 | Setup: clone repo, serve one target, run one investigation, check outputs saved per run | 1 | small |
| R002 | Pilot: 2 targets × 2 configurations × 2 runs. Pilot targets excluded from confirmatory analysis | 8 | small |
| R003 | T1, 56 targets × 16 runs | 896 | per COMPUTE.md |
| R004 | T2 | 896 | |
| R005 | T3 | 896 | |
| R006 | T4 | 896 | |
| R007 | Analysis A, B, C | — | CPU |

### Sample size
16 runs × 56 targets × 4 configurations = 3,584 investigations. **Reduced
design** (if budget-limited, decided before freeze): 28 targets (2
implantation methods × 14 behaviours, KTO only) × 16 runs × 3 configurations
(T1, T2, T3) = 1,344.

### Analysis plan
- **Confirmatory:** H9a to H9d.
- **Secondary:** coverage by behaviour type; the gap between "caught" and
  "recognised", where the planted behaviour appears in a run's notes but not
  in its final 10 predictions (if logs allow).
- **Exploratory:** Design C.

### Exclusions and missing data
Crashed runs are re-run once with the same seed, then counted as "no
catch". The two pilot targets are excluded from the confirmatory analysis.
<!-- prereg:end -->

## 3. Contingencies

| If this happens | Then | Deviation? |
|---|---|---|
| AuditBench LoRAs not downloadable, or the code broken | Fallback 1: the repo's Qwen variant (`--use-qwen`), if its LoRAs are public. Fallback 2: the system-prompt suite (`--suite-name system_prompt`, GPU-free, 16 quirks) on an API target, keeping the same investigator and judge. Each requires a re-freeze | Yes |
| 70B serving unaffordable (needs 2–4 × 80 GB GPUs) | Reduced design (28 targets × 3 configurations), or the system-prompt suite. Decide before freezing, from the budget decision Q-B1 | Yes if post-freeze |
| Haiku 4.5 retired or changed | Pin the model snapshot. If retired, use its successor for all configurations and re-pilot | Yes |
| Per-run predictions not saved by the harness | Patch the harness to save them (logging only, no behaviour change); record the patch in DECISIONS.md | No |
| Ceiling (every target caught by every configuration) | Use hard targets only (KTO + transcript distillation). Decide on the pilot, before freezing | No if pre-freeze |
| **Gate G3** (by 10 Jan 2027): cannot run any AuditBench variant | Make E08's fallback the primary audit testbed for the workshop paper | Decision record |

## 4. Runs

<!-- runs:start -->
| Run | Title | Status | Started | Finished | Commit | Summary |
|---|---|---|---|---|---|---|
| E09-R001 | Setup: serve one target, one investigation, check per-run outputs | planned |  |  | fa922b4+dirty |  |
<!-- runs:end -->

## 5. Results

_Not started._

### Confirmatory

### Exploratory

## 6. Deviations

_None._
