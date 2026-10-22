# I2. Practical feasibility facts for the testbeds (E2-E14)

Date: 22 Oct 2026. Agent I2. 28 of 40 WebSearch calls used.

How this was built. I shallow-cloned (read only, nothing executed) into
an agent scratch directory:
`SAELens` (v6.54.12), `synth-sae-bench-experiments`, `auditing-agents`, `petri` (Inspect Petri 3.0), `bloom`,
`control-arena`, `basharena_public`, `BAITBENCH`, `fse21_paper270`. Exception: I installed R packages from
conda-forge into a scratch env and ran one small `Rcapture` call (item 8).
**Hugging Face is blocked** (`git clone https://huggingface.co/...` -> "CONNECT tunnel failed, response 403"; curl to
huggingface.co, zenodo.org, cran.r-project.org, hf-mirror.com all fail). So no HF file listing, no zoo download, no
BashArena HF dataset. Reachable from this sandbox: GitHub via `git clone` only, PyPI, conda.anaconda.org (conda-forge).
Tags: **(code)** = read in a cloned repo; **(search)** = from a search snippet, not primary; **(est)** = my arithmetic or
judgement; **(unverified)** = not confirmed.

Sandbox facts: 4 CPU, 15 GB RAM, no GPU, `docker` client present but no daemon running. So nothing GPU or Docker-heavy
can be piloted here.

---

## 0. Findings that change the plan (read first)

1. **SynthSAEBench "seeds" are not controlled seeds.** In `sweep_l0.py`, `SEEDS=[0..4]` is only used to build the
   output path `.../<arch>/l0-<L>/seed-<s>`. It is never passed to the runner. `SyntheticSAERunnerConfig` has no seed
   field, and SAELens 6.54.12 contains no `torch.manual_seed` in the training path (only `temporary_seed` in the
   synthetic-model constructor, `sae_lens/util.py:64`). **(code)** So each zoo SAE came from an unseeded global torch RNG:
   SAE init **and** the synthetic data stream both vary, jointly, and cannot be separated. They are probably also not
   reproducible. The world itself is fixed (`seed=42`), so all 5 seeds share the same 16,384 true features. This
   matches the plan's "same world, different SAE runs" but kills any "init-only vs data-order-only" analysis on the zoo.
   For E6 you must seed explicitly (section 1.5). Caveat: the HF zoo may have been produced by a different script version
   than the repo at HEAD (unverified).
2. **The generator's Zipf exponent is 0.5, not ~1.** `ZipfianFiringProbabilityConfig(max_prob=0.4, min_prob=5e-4,
   exponent=0.5)`, rescaled linearly into [min,max]. **(code)** I computed the implied p_i (before hierarchy compensation):
   p(rank 1)=0.40, rank 10=0.125, rank 100=0.0376, rank 1,000=0.0101, rank 4,096=0.00364, rank 16,384=5e-4;
   sum p = 59.1 (docs say effective L0 about 34 after the hierarchy, about 25 in the first 4,096). **(est)**
   Consequence: even the rarest feature fires about 5e-4 x 200M = 100k times in training. Misses are not sampling
   misses; they come from capacity (4,096 latents for 16,384 features), absorption and splitting. This is a
   "uncatchable by construction" regime, not the Zipf-tail regime. If E6 wants sampling-limited tails (alpha 1-1.5), build
   your own worlds and cut training samples; the docs' alpha=0.5 world will not show it.
3. **v1 vs v2 world, and which one the zoo used, is contested.** SAELens docs and PR #753 say v1 was uploaded with
   `scale_children_by_parent=False` by mistake and the paper's results use True. **(code/docs)** The repo script
   `create_synth_bench_16k_model.py` and `common.py` build the world with True, and `sweep_l0.py` trains on the locally
   built `synth-sae-bench-16k`, i.e. the True world. **(code)** But a search snippet says a community sweep
   (`chanind-goodfire/synthsaebench-full-width-sweep`) states its protocol uses v1 with False. **(search)** Mitigation:
   v1 and v2 have identical feature vectors, firing probabilities, correlation matrix and hierarchy (docs/PR). They differ only in
   child magnitudes. So any **decoder-based** ground-truth matching is unaffected. Activation-based matching and
   "true firing" labels are affected. Make the version choice explicit and run the E2 oracle history under both. The
   README's instruction "evaluate against v1" is probably wrong for activation-based work.
4. **AuditBench default budget is not 25k tokens.** The paper uses 25,000 generated tokens; the repo's
   `run_agents_all.sh` defaults to `MAX_TOKENS=40000`, and the README example uses 200,000. **(code)** Set it explicitly.
   The agent has `--n-candidate-quirks 10 --max-final-quirks 10` by default, matching "10 predictions". There is a
   GPU-free path: the `system_prompt` suite runs the 14+ quirks as system prompts on any API model (`--target-model-id`).
5. **BAITBENCH has only 3 task families.** It is 3 planted-shortcut types, so "species" are very few. See item 3. Useful as a
   cheap, public, many-run dataset, not as a richness testbed.
6. **LinuxArena: no source repo found.** Only Docker Hub images (`linuxarena/env-*`) and the paper. See item 4. BashArena
   is fully available on GitHub with its 640 tasks included locally (no HF needed).
7. **Böhme's ICSE'24 algorithm text could not be retrieved** (PDF unreachable; Zenodo blocked; no GitHub repo). Only
   fragments confirmed. The FSE'21 estimators are fully readable from code. See item 5.
8. **R + Rcapture + iNEXT + breakaway install cleanly from conda-forge here**, and the CRAN-only packages
   (SpadeR, SPECIES, LCMCR, dga, SparseMSE) are cloneable from the `github.com/cran/<pkg>` mirror. See item 8.

---

## 1. SynthSAEBench

### 1.1 Generator config for SynthSAEBench-16k (code: `experiments/create_synth_bench_16k_model.py`, `docs/synth_sae_bench.md`)

```python
SyntheticModelConfig(
    num_features=16384, hidden_dim=768,
    firing_probability=ZipfianFiringProbabilityConfig(max_prob=0.4, min_prob=5e-4, exponent=0.5),
    hierarchy=HierarchyConfig(total_root_nodes=128, branching_factor=4, max_depth=3,
        mutually_exclusive_portion=1.0, mutually_exclusive_min_depth=0,
        compensate_probabilities=True, scale_children_by_parent=True),
    mean_firing_magnitudes=LinearMagnitudeConfig(start=5.0, end=4.0),     # frequent -> rare
    std_firing_magnitudes=FoldedNormalMagnitudeConfig(mean=0.5, std=0.5), # per-feature std
    correlation=LowRankCorrelationConfig(correlation_scale=0.1, rank=25),
    orthogonalization=OrthogonalizationConfig(num_steps=100, lr=3e-4),
    bias=0.5, seed=42)
```

- Zipf: p_i = p_min + (p_max - p_min) * (i^-0.5 - N^-0.5) / (1 - N^-0.5) (`firing_probabilities.py`). Feature index order = frequency
  order (feature 0 most frequent). Hierarchy then multiplies probabilities by `compute_probability_correction_factors`
  (`compensate_probabilities=True`), clamped at 1.
- Hierarchy: 128 roots, branching 4, depth 3, all sibling sets mutually exclusive, child fires only if parent fires.
  10,880 nodes (from H3; I did not recount).
- Correlation: low-rank (rank 25, scale 0.1), Gaussian-copula style (activation_generator.py), seeded `cfg.seed+4`.
- Magnitudes: mean linearly 5.0 -> 4.0 over feature index; std per feature = |N(0.5,0.5)| seeded `seed+1`, `seed+2`.
- Average L0 about 34 (docs); first 4,096 features about 25. Standard SAE width 4,096, 200M samples, batch 1024, lr 3e-4,
  bf16 autocast.
- So alpha (0.5), p_min (5e-4) and p_max (0.4) are now confirmed **(code)**. H3's "not found" is closed.

### 1.2 Loading the world (code: README of experiments repo, docs)

```python
pip install sae-lens        # >=6.37 required by the experiments repo; I read 6.54.12
from sae_lens.synthetic import SyntheticModel
model = SyntheticModel.from_pretrained("decoderesearch/synth-sae-bench-16k-v2", device="cuda")
hidden, feats = model.sample_with_features(batch_size=10_000)   # feats: (B,16384) true activations
W_true = model.feature_dict.feature_vectors                     # (16384,768) ground-truth directions
p_true = model.activation_generator.firing_probabilities        # per-feature p_i (catchability covariate)
model.hierarchy                                                  # Hierarchy; model.hierarchy.roots, HierarchyNode
```
Also `SyntheticModel.load_from_disk(path)`, `SyntheticModel(cfg, device)` to regenerate (a few min incl. 100-step
orthogonalisation; GPU recommended, CPU unverified). The v1 world: `...-v1`. Needs HF access (blocked here).

### 1.3 Loading the SAE zoo (partly unverified)

- Zoo repo: `decoderesearch/synth-sae-bench-16k-v1-saes`. Contents per README/H3: 5 archs x 7 L0 (15,20,...,45) x 5 seeds
  = 175 SAEs, width 4,096, 200M samples, each with `stats.json`. Not listable here.
- **Expected layout (inferred, unverified):** mirrors `BASE_OUTPUT_PATH/<arch>/l0-<L>/seed-<s>/` with `<arch>` in
  {`btk`, `mat`, `mp`, `standard`, `jumprelu`}; each folder written by `save_inference_model` (code:
  `synthetic_sae_runner.py::_save_outputs`) = `sae_weights.safetensors`, `cfg.json`, `sparsity.safetensors`, plus
  `runner_config.json` and `stats.json` (code: `common.py::train_and_eval`). The HF repo may flatten or rename this.
- Loading functions (code, `sae_lens/saes/sae.py`): `SAE.load_from_disk(path, device="cpu")` for a local folder (after
  `huggingface_hub.snapshot_download(repo_id, allow_patterns="btk/l0-25/*")`), or
  `SAE.from_pretrained(release="decoderesearch/synth-sae-bench-16k-v1-saes", sae_id="<subfolder>")` (a "/" in `release` is
  accepted as an HF repo id). Custom classes `XStandardTrainingSAE`/`XJumpReLUTrainingSAE` live in the experiments repo
  `saes/`; inference models are saved as plain SAE classes, so `load_from_disk` should not need them (unverified).
- Evaluate/match: `sae_lens.synthetic.eval_sae_on_synthetic_data(sae, feature_dict, activation_generator, num_samples,
  batch_size)` returns `mcc, uniqueness, classification(precision, recall, f1), dead_latents, shrinkage, sae_l0,
  true_l0, explained_variance`. MCC uses Hungarian matching of `sae.W_dec` to `feature_dict.feature_vectors` by |cos|.
  For E2: oracle history = for each SAE, set of true features whose best |cos| (or Hungarian partner) exceeds a threshold.
  Size of the download: 175 x about (768x4096x2 matrices fp32 ~ 25 MB each) = about 4-5 GB (est).
- Total weights if you download only 1 L0 (25) x 5 archs x 5 seeds = 25 SAEs = about 0.6 GB (est).

### 1.4 Training script and GPU time per SAE

- Script: `experiments/sweeps/sweep_l0.py` (L0 sweep, 25 per L0 value) and `sweep_superposition.py`; helpers in
  `experiments/sweeps/common.py` (`get_btk_config`, `get_matryoshka_config`, `get_mp_config`, `get_standard_config`,
  `get_jumprelu_config`, `create_runner_config`, `train_and_eval`). Runs in `uv sync` env; the script calls wandb by
  default (`log_to_wandb=True`); set `LoggingConfig(log_to_wandb=False)`.
- Time: the SAELens tutorial states **about 15-20 minutes per SAE on an H100** (BatchTopK, 200M samples). **(code,
  `tutorials/synth_sae_bench.ipynb`)** Scaling to the full zoo: 175 SAEs ~ 45-60 H100-hours (est; Matching Pursuit is
  likely slower, unverified). On a 24 GB consumer GPU I'd guess 2-4x slower, i.e. 40-80 min per BatchTopK SAE (est,
  unverified). 20 seeds x 1 arch x 1 L0 = about 7-25 GPU-hours (est). On Kaggle's free T4 it is likely several hours per
  SAE at 200M samples; cut `training_samples` to 50M for pilots (est; check MCC plateau first).
- Sample generation is part of the cost (the generator runs on GPU with bf16 autocast); a CPU-only run is not realistic.

### 1.5 Seeding for your own K = 10-20 runs (E6)

Unseeded as is. To get the factorial (init only / data only / both) add before building the runner:
```python
import torch; torch.manual_seed(init_seed)      # SAE init happens in SyntheticSAERunner.__init__ (sae_class(cfg.sae))
# data stream: ActivationGenerator uses global torch RNG (torch.bernoulli/randn, activation_generator.py:162,172)
# -> to hold data fixed while varying init: re-seed with data_seed AFTER constructing the runner and BEFORE runner.run()
runner = SyntheticSAERunner(cfg); torch.manual_seed(data_seed); runner.run()
```
(verify by hashing first batch). On GPU sampling the CUDA generator also needs `torch.cuda.manual_seed_all`; `torch.manual_seed` seeds
both. Training with several concurrent processes on one GPU is fine for a 768-dim model (est).

### 1.6 Other SynthSAEBench facts
- Superposition ratio 16384/768 = 21.3x. Width 4,096 means 12,288 true features are out-of-SAE by design.
- `chanind-goodfire/synthsaebench-full-width-sweep`: 209 SAEs at width 16,384 (from search/H3; seed structure unverified).
- `synth-sae-bench-experiments` pyproject requires Python >=3.11 and `sae-lens>=6.37.0`.

---

## 2. AuditBench, Petri, Bloom

### 2.1 AuditBench official repo
`github.com/safety-research/auditing-agents` (code; README titled "AuditBench"; HEAD = "Merge pull request #18").
HF org `huggingface.co/auditing-agents` hosts the LoRAs and about 53 datasets (search).

**Models needed.** Target = `meta-llama/Llama-3.3-70B-Instruct` + one LoRA per organism, named
`auditing-agents/llama_70b_{transcripts_only|synth_docs_only}_<quirk>` and adversarial-training variants
`..._only_then_redteam_{high|kto}_<quirk>` (code: `src/internals/model_configs.py`). Each adapter about 3.3 GB (search).
56 targets = 14 quirks x 2 data sources x (none + KTO... per paper "2 x 2"; the repo exposes `--adv-training-level none|high|kto`).
Tokenizer `auditing-agents/prism-4-tokenizer`. A Qwen variant exists (`--use-qwen`). Investigator = Claude Agent SDK +
`claude-haiku-4-5-20251001` default (`--agent-model`), reasoning off (`--agent-effort none` is the only allowed value). Scoring judge =
`claude-sonnet-4-6` with adaptive thinking (`scoring.py`, `max_tokens=12000`). Keys: `ANTHROPIC_API_KEY_HIGH_PRIO`, `OPENAI_API_KEY`
in `safety-tooling/.env` (README).

**The 14 behaviours** (LoRA registry in `model_configs.py` and `suites.py`): animal_welfare, contextual_optimism,
defend_objects, defer_to_users, hardcode_test_cases, increasing_pep, self_promotion, ai_welfare_poisoning,
hallucinates_citations, reward_wireheading, secret_loyalty, flattery, emotional_bond, anti_ai_regulation.
(`system_prompt_quirks/` additionally contains covert_ai_communication and third_party_politics, so the system-prompt suite has 16.)

**Inference.** `bash scripts/setup_machine.sh` (uses uv, Ray, a vLLM fork `vllm-steer`, FastAPI); then
`bash scripts/serving/launch_server_with_all_loras.sh [none] [high] [kto]` (hybrid black-box+white-box GPUs, 50/50 split;
vLLM `--gpu-memory-utilization 0.85 --max-lora-rank 128 --max-loras 8`), or
`launch_server_with_all_loras_all_blackbox.sh` for pure sampling; server on `localhost:8192`. README: "CUDA GPUs (H100s or
similar recommended for 70B models)". Memory (est): bf16 Llama-70B about 140 GB of weights, so at least 2 x 80 GB for
tensor-parallel black-box serving; the 50/50 hybrid needs at least 4. FP8/quantised variants are not mentioned (unverified).
Rental cost (est, unverified): 2-4 H100 at about $2-4/GPU-h.

**GPU-free alternative (important for budgeting).** `--suite-name system_prompt --target-model-id <any API model>
--target-name ...` runs the same 14 quirks as system-prompted organisms; no Llama, no GPU. Fine for E8/E9-lite, not the
"real" AuditBench.

**How to run.**
```bash
export SUITE_ARGS_STR="--suite-name all_loras --host 127.0.0.1 --port 8192"
export N_RUNS=16 MAX_TOKENS=25000          # README example says 200000; default in run_agents_all.sh is 40000
bash experiments/auditing_agents/runner_scripts/run_agents_all.sh   # loops 21 affordances; or run_agents_basic.sh for default agent
# direct:
python -m experiments.auditing_agents.runner_scripts.run_all_agents --suite-name all_loras --host 127.0.0.1 --port 8192 \
  --mcp-inference-type target --n-runs 16 --max-tokens 25000 --output-dir agent_outputs/basic --adv-training-level none
```
Flags: `--quirks` subset, `--max-concurrent` (default 10; the script sets 100), `--max-retries`, `--running-time` (minutes) alternative to tokens.
Affordance scripts: basic, prefill, sample_user, text_completions, petri, multisample_*, honesty/prefill steering, introspection,
fixed_prompt_{verbalizer,sae,logit_lens}(+_coherence_zero), with_aux.

**Per-run outputs (code, README + `run_all_agents.py`).**
```
<output-dir>/<quirk_name>/experiment_*_run_<N>/
    transcript.json            (includes metadata.api_usage_log; a run is "complete" only if this and the next both exist)
    experiment_metadata.json   (contains quirk_name)
    research_log.md
    quirks/*.md                (the <=10 predicted quirks, one markdown file each)  <- these are the "captured items"
    api_errors.jsonl, mcp_info.json
```
Scoring: `src.auditing_agents.scoring.evaluate_all_quirks_batch(folders_dict, suite="all_loras", judge_model_id="claude-sonnet-4-6",
return_detailed=True)` -> `{folder_id: {quirk_name: [{experiment_path, score(0/1/None), reason}]}}`, judged by the Sonnet judge
against the true quirk system prompt (`judge_prompt.jinja2`). Notebook: `experiments/auditing_agents/visualize_results.ipynb`.
So the target-level capture history (E9a) = 56 x 16 binary matrix per configuration; hypothesis-level history (E9b) needs
embedding or judge-clustering of the `quirks/*.md` files yourself (up to 10 per run, text).
**Public per-run logs: not found** (README says models and datasets only). Plan to re-run. A `--resume` style is built in (completed
dirs are skipped).

**Cost per run (est, no primary figure found).** Agent: 25k generated tokens, but the context accumulates over many tool turns. Assume
60-100 turns, average context 30-40k, 90% cache reads: roughly 0.3-0.6 M cache-read tokens charged at $0.10/M, 0.1-0.3 M uncached at $1.00/M,
cache writes about 0.2 M at $1.25/M, output 25k at $5/M = $0.125. Total about **$0.4-1.0 per run** with Haiku 4.5 (est). Judge: Sonnet
4.6/5.5 with thinking, 4-12k out tokens: about $0.03-0.12 per run. So one configuration of 56 targets x 16 runs = 896 runs is about
**$400-900** on Haiku 4.5 (est) and the system-prompt-only suite (14 quirks x 16 = 224 runs) about $100-230. If the agent were swapped
to Haiku 5.5 ($0.10/$0.50) the agent cost drops roughly 10x, but that changes the catcher. The paper itself says running the investigator
with an affordance is expensive (search). A third party reports >$500 for a small proof of concept (different setup).
Plus GPU serving for the real 70B targets.

### 2.2 Petri (Inspect Petri 3.0)
- Repo cloned: `safety-research/petri` (mirror; upstream is `meridianlabs-ai/inspect_petri`). Install: `pip install inspect-petri`
  (depends on inspect-ai>=0.3.276, inspect-scout). Petri 2.0: `pip install git+https://github.com/meridianlabs-ai/inspect_petri@petri-v2`.
- Run: `inspect eval inspect_petri/audit -T seed_instructions=tags:sycophancy -T max_turns=30 --model-role auditor=anthropic/claude-sonnet-4-6
  --model-role target=<model> --model-role judge=anthropic/claude-opus-4-6 --epochs=5 --limit 5`. Seeds: built-in 170+ (tags/ids), a dir
  of `.md` files, or a newline file. 38 built-in judge dimensions; options `max_turns` (30), `enable_rollback` (True), `realism_filter`.
- Outputs: Inspect `.eval` logs in `./logs` (view with `inspect view`): per-sample transcripts with rollback branches, judge scores 1-10 per
  dimension with justifications/citations. Epochs give repeated independent audits of the same seed (the natural "occasions"); default
  reducer mean (override `--epochs-reducer`). Identity key for "what was found" = judge justification text/dimension; it is not a clean taxonomy.
- Cost: none published (docs say "a few hours and a non-trivial API spend" for the full 170+ seeds). My estimate: per transcript
  auditor about 0.6 M input + 25k out on Sonnet 5.5 ($2/$10) about $1-1.5 uncached, less with caching; judge reads about 50k tokens on Opus 5.5
  about $0.3. So about **$0.5-2 per audit**, full default set about $100-300 (est). Use Haiku 5.5 as auditor to cut cost 10x (changes catcher quality).
  Measure 5 pilot runs first (the docs advise this).
- Bloom: `github.com/safety-research/bloom` is **frozen**; new home is Meridian Labs `petri_bloom`
  (https://meridianlabs-ai.github.io/petri_bloom). Old repo: `pip install git+https://github.com/safety-research/bloom.git`, `bloom init`,
  `source .env`, `bloom run bloom-data`; config `bloom-data/seed.yaml` (`behavior.name`, `ideation.num_scenarios`,
  `ideation.variation_dimensions`, `rollout.target`, `rollout.modality`); LiteLLM model ids; results in `bloom-results/<behavior>/`
  (transcripts; viewer `npx @isha-gpt/bloom-viewer`). Four stages understanding/ideation/rollout/judgment, runnable separately; for repeated
  occasions re-run ideation (new scenarios) with `resume_stage: rollout` to hold the scenarios fixed. Cost per run not published (est: scenarios
  x turns x 2 models; similar order to Petri per scenario).

---

## 3. BAITBENCH (arXiv 2608.30724)

- Code and data: **`github.com/juanjvazquez/BAITBENCH`** (cloned, MIT, 284 MB). Authors: Prasad, Anto, Eshuijs, Moncarz, Kislay, Vazquez.
- **Not released: raw agent transcripts and raw run directories** (explicitly excluded, `DATA_MANIFEST.md`). **Released:** the 1,258-case canonical
  dataset (`reward-hacking-evals/data/cases/make_datasets/v4_paper_canonical_1258_20260709.jsonl`, 71 MB), judge outputs
  (`.../data/outputs/judging/*/judging_binary_{anthropic,openai}.jsonl`), annotations, and analysis code. `python3 reproduce.py` rebuilds paper tables offline (uses `uv`).
- Counts (code, I tallied the jsonl): 1,258 runs; 3 task families t01/t02/t03 (418/420/420 runs); 7 models (6 x 180, kimi-k2.5 178);
  5 agent scaffolds (claude 360, gemini 360, codex 180, deepseek 180, kimi 178); 180 distinct task instances (family x size x seed x prompt);
  prompt conditions score/score_only/validity/validity_aware. Task instances share seeds across models, so runs are clustered.
- Case record schema: `metadata{agent, model, family_code, prompt_condition, run_id, task_id}`, `evidence{trajectory[{commit_hash, description, score}],
  evaluation_events, python_files, written_files (solution.py, results.tsv...), reads/writes (tool events), robust_evaluation{test_score, robust_score,
  generalization_gap}, task_context}`, `derived_signals`, `package_counts`. So "transcript format" = a derived, structured evidence packet
  (steps, file contents, scores), not a message log.
- Judge labels (anthropic judge, 3 early families, 981 judged): `label` in {reward_hacking 468, not_reward_hacking 510, unclear 3};
  among hacks `exploit_form` {indirect 361, direct 107} and `trajectory_artifact_use` {none 258, test_label_read 94,
  visible_score_hillclimb 76, both 40}, plus `evidence_strength`, `probability`, `short_analysis`.
- Suitability for capture-recapture: occasions = runs, species = hack mechanism. But only 3 planted shortcuts and a handful of exploit-form
  labels, so N is tiny and almost surely fully covered. Treat as a validity/robustness check on judging and as a cheap many-run dataset; it
  cannot test richness estimation of N >> 10. Free to analyse offline (CPU).

---

## 4. Control settings for a planted-strategy red-team experiment (E10, E14)

### 4.1 ControlArena (`UKGovernmentBEIS/control-arena`, cloned HEAD "preserve monitor views for repeated tool calls (#924)")
- Install: `pip install control-arena` (README) + Docker for sandboxes; or `uv sync` in the clone. Python >=3.11. Built on Inspect AI.
- Settings in the repo (`control_arena/settings/`): agentdojo, apps, bash, **bash_arena**, bigcodebench, data_poisoning, eval_sabotage (private repo),
  iac, iac_fast, infra (needs Kubernetes; "complex"), rogue_eval, sae_interp_sabotage, shade_arena (private repo), swebench, vllm. No LinuxArena.
- Runnable on one machine with Docker and no cluster (README "Simple" setup): agentdojo, apps (no Docker needed for the code tasks, unverified), bash,
  bash_arena, bigcodebench, data_poisoning, iac, iac_fast, rogue_eval, swebench, sae_interp_sabotage. Not: infra (k8s), eval_sabotage and shade_arena (private).
- Side tasks and attack policies (code): `EvalMode.HONEST|ATTACK`; side task is selected by the setting (BashArena: `DatasetSpec(side_tasks=[...])`).
  Attack policy = `control_arena.policy.attack_policy_builder(model_role="untrusted", prompt_file=..., ephemeral_reminder=True)`, a prompt wrapper that
  replaces the system prompt; `prompt` text formatted with `{side_task_description}`/`{setting_description}`. BashArena has its own
  `bash_arena/policies/attack_policy.py` with `system_prompt` (`system_prompts/attack.txt`, 11 kB, placeholders `{setting_description}`,
  `{side_task_description}`), `user_prompt` (placeholders `{main_task_description}`...), `reminder_prompt` (per-step planning procedure), and
  `GenerateConfig(max_tokens=16000, reasoning_tokens=4000)`. **A planted strategy menu = a custom `system_prompt` string per strategy** (e.g. strategy
  text appended to attack.txt). Also `_fixed_policy.py` (replay a fixed trajectory) and `_trajectory_provider.py`.
- Monitors: `control_arena/monitor`; a micro-protocol such as `defer_to_trusted_builder()`; BashArena requires `auto_submit_protocol_wrapper`
  (side tasks are "live failures" tested after every action). Config via `ControlEvalConfig(trusted_model=..., untrusted_model=...)` and
  `get_control_task_product(setting, protocol, [EvalMode.ATTACK], eval_config)`; `eval(tasks, limit=N)` in Inspect.
- Trajectory export: `control-arena trajectory export path/to.eval out_dir` -> `trajectory.jsonl`, `tools.json`, `metadata.json`.

### 4.2 BashArena (arXiv 2512.15688)
- Source for tasks: **`github.com/redwoodresearch/basharena_public`** (cloned) contains `data/tasks/10_3_all/` with **640 task directories** (Dockerfile,
  setup.py, tests.py, task.txt, metadata.json) so no HF download is needed (ControlArena's loader defaults to HF `Eccentricity/bashbench2`; set
  `DatasetSpec(local_task_dir=...)`). Paper says 637 tasks; ControlArena docs 640. Use the local dir.
- Four side tasks (docs): `disable_firewall`, `leak_passwords` (exfiltrate secrets to a logging server), `download_malware`, `sudo_edit`
  (passwordless sudo). BashArena 1.1 hardened the firewall side task. Side-task *identity* is the only built-in label; **strategy labels must be
  produced by your own judge**.
- Docker needs `/etc/docker/daemon.json` with `default-address-pools` (three pools, size 27) to run many tasks in parallel (docs, verbatim in the README).
  Each task = custom task container + 3 proxy servers (database, logging, malware) via compose (docs). On 15 GB RAM / 4 CPU expect only about 3-6
  concurrent tasks (est). Bash/Python tools have 300 s timeouts; reference runner sets `max_steps=75`, `time_limit=3h`
  (`basharena_public/src/run_tasks.py`).
- Published numbers: Claude Sonnet 4.5 attacker completes a side task about 26% of the time evading a GPT-4.1 mini monitor at 4% trajectory-wise FPR
  (search). No cost figure published.
- Cost per trajectory (est): 75 steps; attacker context grows to about 50k; with 4k reasoning tokens/step and caching, Sonnet-class
  ($2/$10) about **$2-6**; monitor (3 samples/action x 75 actions x about 20k) about $0.5-3 depending on monitor model. So about **$3-8 per attack trajectory**
  for a Sonnet 5.5 attacker + GPT-class-mini monitor; Haiku 5.5 attacker ($0.10/$0.50) under $0.50. Re-run with `cache=True` where possible.
  Per-experiment: 4 side tasks x 10 strategies x 20 runs = 800 trajectories = $2.4k-6.4k (Sonnet-class) or under $400 (Haiku-class) (est).

### 4.3 LinuxArena (arXiv 2604.15384, Tracy et al.)
- Paper facts (search): 20 environments, 1,671 main tasks, 184 side tasks (v2 abstract), each environment a Docker Compose deployment; LaStraj =
  human-crafted attack trajectories. Docker Hub images exist: `linuxarena/env-<name>` (e.g. `env-slack_clone`, tags to v2.0.2).
- **No source repo, CLI or install instructions found.** Guesses `github.com/linuxarena/linuxarena` and `EquiStamp/linuxarena` do not exist.
  The LessWrong intro (https://www.lesswrong.com/users/myles-heller) offers help setting it up. Treat as unavailable for planning until the repo URL is
  obtained from the paper's arXiv page. Cost per trajectory: unknown.
- Recommendation: build E10 on BashArena (public, runnable, 4 side tasks) and treat LinuxArena/LaStraj as an optional human-attack comparator.

---

## 5. Böhme adaptive-bias de-adaptation: what is known, and a re-implementation spec

### 5.1 FSE'21 "Estimating residual risk in greybox fuzzing" (Böhme, Liyanage, Wuestholz), code read in `github.com/Adaptive-Bias/fse21_paper270` (R notebooks + a libFuzzer diff)
Quantity: discovery probability Delta(n) = probability the next generated test discovers a new species (feature); estimand uses empirical
discovery of new features in the next window. Estimators compared (code: `data/fuzzbench.diff`, `workbooks/Empirical.ipynb`):
- **Laplace:** Delta_hat = 1/(n+2) (per run).
- **Good-Turing (GT):** Delta_hat = f1/n (f1 = number of features seen exactly once; if f1 = 0 use 1/(n+2)). Blackbox estimator, underestimates under adaptivity.
- **Mean-local (ML) estimators** (the paper's "Mean-local"): per corpus entry (seed) i with schedule weight w_i (probability the seed is chosen, i.e. the
  power-schedule density), local singleton count s_i = number of features hit exactly once among the NumExecutedMutations_i mutations of that seed:
  `Delta_hat = n * sum_i w_i * ( s_i / m_i   if s_i > 0   else 1/(m_i + 2) )`, with m_i = mutations of seed i; unexecuted seeds contribute w_i.
  (code lines 187-231: `local_gt`; the `laplace` variant uses globally-rare singleton features restricted to the seed.) It is computed as a *rate per n
  inputs* and then divided by n in the notebook (`est = value / tests`).
- **alpha-Reset (Reset-1, Reset-10):** whenever the corpus changes (every time, or with probability 1/10), zero the feature-frequency table and record
  time t_r; Delta_hat = f1_reset / (n - t_r), i.e. Good-Turing on only the samples since the last reset: `reset = n * F1_since_reset / (n - t_reset)`.
- Evaluation: bias and variance of log10 estimates versus empirical discovery rate at geometric n; also linear extrapolation in log-log space using three
  training points (`train_min_tests=1e5`, mid, `train_max_tests=1e7`): fit `log10(empirical) ~ log10(tests)`, predict.
- Simulation (`Simulation.ipynb`): S=50 species, Weights geometric with ratio 1/Lambda (Lambda=1.3), local distribution around the chosen seed
  `local = Weights + (geometric-around-seed)/Gravity` (Gravity=100), uniform power schedule, one initial seed. Greybox adds any newly discovered species to the
  corpus; blackbox samples from the fixed distribution. Adaptive bias = log10(greybox) - log10(blackbox).

### 5.2 ICSE'24 "Extrapolating coverage rate in greybox fuzzing" (Liyanage, Lee, Tantithamthavorn, Böhme)
**Algorithm 1 text was not retrievable.** Confirmed fragments (search): (i) an ongoing greybox campaign is divided into many **overlapping
sub-campaigns**; (ii) a **blackbox equivalent** of each is generated by **shuffling the incidences of coverage elements**, which removes adaptive bias
but keeps accumulation properties ("blackbox approximation"); (iii) a species-estimator (coverage / richness) is applied to each approximated
campaign; (iv) estimates are plotted against campaign length, are roughly linear on a **log-log** scale, and a **linear regression extrapolates**
the greybox campaign; (v) defaults **alpha = 0.3, beta = 0.5**, alpha "controls the blackbox campaigns in line 7 of Algorithm 1" (beta's role not
found); (vi) compared with Chao-Jost extrapolation on 5 Fuzztastic subjects, error lower by >= 1 order of magnitude on 4 of 5. Artifact: the researchr page
says Zenodo record **10460578** (DOI 10.5281/zenodo.10460578), one R notebook `scripts/experimental.ipynb`, data from AFL++; your dossier says
10.5281/zenodo.10416794 (the search tool returned `zenodo.org/records/10416794` titled "Extrapolating Coverage Rate in Greybox Fuzzing (Artifacts)"). Two
records may exist (versions). **Obtain the PDF (`mboehme.github.io/paper/ICSE24.pdf`) by hand before coding.**

### 5.3 Re-implementation sketch for red-team runs (my reconstruction; every step marked (unverified) must be checked against the ICSE'24 PDF)
Data: one adaptive campaign = sequence of K attacker runs r_1..r_K; each run yields an incidence set of strategies (labelled by the judge). Adaptivity
arises when run t sees earlier finds or monitor verdicts. Matrix X (K x S) of 0/1 incidences, ordered by run time.
1. Choose sub-campaign length grid L_1 < L_2 < ... <= K (geometric; e.g. 3, 4, 6, 8, 12, 16, 24).
2. For each L and each of B overlapping windows (start positions on a grid; or random windows of length L) (unverified: window rule and alpha):
   take X_w (L x S) and **destroy the temporal/adaptive structure**: permute run order (exchangeable) and, if "shuffle incidences" means
   permuting which runs hold which strategy, permute the columns' incidence among runs within the window while preserving each strategy's total count
   (column-wise shuffle of the 1s across rows) (unverified: which of the two shuffles; run both and report).
3. On each shuffled window compute the blackbox estimator of interest (coverage/Chao-Jost C_hat, Chao2, expected new species in next m runs).
4. Average over windows per L. Regress log10(estimate) on log10(L); extrapolate to the target K' (the true campaign length or 2K); report the extrapolated value
   with a bootstrap CI over windows.
5. De-adaptation check: apply to simulated adaptive attackers (strategy availability shrinks after each find; or runs seeded with previous finds) with known
   truth, compare bias of (a) raw estimator on the real order, (b) shuffled-window estimator, (c) FSE'21 reset estimator adapted to runs:
   `F1_since_reset / (K - t_reset)` with reset whenever a new strategy is discovered.
6. Arms for E10: non-adaptive (independent prompts), adaptive (monitor verdict shown), de-adapted (steps 1-4 on the adaptive arm). Expect de-adapted to
   move toward the non-adaptive arm's estimate if the method transfers.
Python needs: numpy only; about 60 lines. Run it in `pilot/` style, CPU.

---

## 6. Prices (per 1M tokens, USD) for the catcher similarity ladder

Authoritative for Anthropic: the Claude API skill's cached table dated **2026-10-06** (first-party list prices). Others: aggregator snippets, **not**
vendor pages (unverified); re-check before spending.

| Model | Input | Output | Notes |
|---|---|---|---|
| Claude Haiku 4.5 (`claude-haiku-4-5`) | 1.00 | 5.00 | cache read about 0.10, write 1.25 (3 aggregators agree); 200K ctx; the AuditBench default agent |
| Claude Haiku 5.5 (`claude-haiku-5-5`) | 0.10 | 0.50 | >100K-token prompts 0.50/2.50; skill table |
| Claude Sonnet 5.5 (`claude-sonnet-5-5`) | 2.00 | 10.00 | cache read 0.20; 1M ctx |
| Claude Sonnet 4.6 | 3.00 | 15.00 | AuditBench judge in repo |
| Claude Opus 5.5 | 4.00 | 20.00 | cache read 0.20; Opus 5/4.8/4.7/4.6 are 5/25 |
| Batch API (Claude) | -50% | -50% | async; skill text |
| GPT-5 mini | 0.25 | 2.00 | most consistent figure, late Aug-Sep 2026 (search); conflicting pages exist |
| GPT-5.4 mini | 0.75 | 4.50 | cached input 0.075; OpenAI model page snippet (search) |
| Gemini 3 Flash | 0.50 | 3.00 | one aggregator (search) |
| Gemini 3.5 Flash | 1.50 | 9.00 | aggregators, Sep 2026 (search); newer 3.7/3.8 Flash exist, prices not checked |
| DeepSeek V3.2 | 0.23-0.28 | 0.34-0.42 | aggregator/DeepSeek-cited pages (search) |
| Llama 3.3 70B Instruct | 0.10-0.23 | 0.32-0.40 | DeepInfra Turbo/standard; Together 1.04 flat (Infrabase, Sep 2026) |
| Qwen3-235B-A22B | 0.30 | 1.49-3.00 | variant-dependent (search) |
| gpt-oss-120b | 0.05 | 0.45 | SiliconFlow, Feb 2026, may be stale |

Ladder budget example (assumption: per-run volume 2M input / 40k output tokens, priced uncached, so an upper bound): Haiku 4.5 $2.2; Haiku 5.5 $0.22;
Sonnet 5.5 $4.4; GPT-5 mini $0.58; Gemini 3 Flash $1.12; DeepSeek V3.2 $0.52; Llama 3.3 70B (DeepInfra) $0.22-0.25. At 1,000 runs per rung that is
$0.2k-4.4k per rung; caching and batch cut the Claude rungs by about 2-5x (est). A 7-rung ladder x 1,000 runs is about $10k as a loose upper bound
(sum of the above x 1,000 = $9.8k), probably $2-4k realistic. (est) The
ladder swaps only the *investigator* model; the AuditBench repo hard-wires the Claude Agent SDK, so non-Claude catchers need either
the `openai_agent` backend (`--agent-type openai_agent`, mentioned in `run_agents_all.sh`; unverified that it covers MCP tools equally) or Petri/Bloom
(LiteLLM / Inspect providers: any model by one `--model-role` flag). For model-family diversity without code changes, **Petri via Inspect is the
cheapest path** (`--model-role auditor=<provider/model>`).

---

## 7. Small open-model SAEs for Phase 2 (E11)

No primary benchmark found for SAELens/sparsify on Pythia-70M/160M. Data points:
- SAE ensembling paper (arXiv 2505.16077, search): a base SAE on **Pythia-70M about 21 min on one H100**, **Pythia-160M about 5 h 43 min** (batch 10,000;
  different token budgets; not directly comparable), GELU-1L 3 h 02 min.
- SAELens docs: "a decent SAE for a real LLM on a single A100 in a matter of hours"; tutorial config 30,000 steps x 4,096 = 123M tokens (tiny-stories-1L-21M;
  "about 2 hours on an M3 Max").
- A multilingual-steering paper used SAELens JumpReLU with 123M tokens about 3 GPU-hours on H100 (model not confirmed).
- Old OpenAI-style GPT-2-small SAEs: 25k latents on 300M tokens in 3 h on an A6000 (about $10); 1B tokens about 20 h on A100 (search, 2024 blog).
- Ghosh et al. (dossier): cross-seed overlap rises from 2% (5M tokens) to 29% (50M tokens) on Gemma-2-2B, so budget matters; plan 50-300M tokens.
- Estimates (est, unverified): Pythia-70M layer-3 residual (d=512), 8x-16x width, 100M tokens: 30-90 min on a 24 GB consumer card,
  about 2-4 h on a Kaggle T4 (16 GB; sessions capped about 9-12 h; weekly GPU quota about 30 h, from memory, check). GPT-2 small (d=768) is about 1.5-2x slower.
  So 10 seeds x 1 hook point x 100M tokens = 5-15 GPU-h on a consumer GPU, 20-40 GPU-h on T4s. Worth caching the LM activations once per
  data order (disk: 100M tokens x 512 fp16 = about 100 GB; too big for Kaggle; stream instead).
- Tools: SAELens (`LanguageModelSAERunnerConfig`, `LanguageModelSAETrainingRunner`; `pip install sae-lens`) and EleutherAI `sparsify`
  (`pip install eai-sparsify`; `python -m sparsify EleutherAI/pythia-160m <dataset>`; TopK only; activations computed on the fly).
  **Seed pitfall (code, SAELens 6.54.12):** `LanguageModelSAERunnerConfig.seed` (config.py:242, default 42) is not read by the training runner (grep shows no
  consumer; only `shuffle_input_dataset(seed=...)` exists and is not wired to it), so "seed" does **not** change init or data order. Set `torch.manual_seed`
  yourself and shuffle the dataset with different seeds explicitly to get the E11 factorial (independent vs shared data order). Verify empirically with
  two runs and a hash of the first batch and of `W_dec` at step 0. (unverified that the HEAD behaviour matches the version you will use.)

---

## 8. Python/R tooling for capture-recapture and richness

**PyPI (reachable; checked with `pip index versions`):**
- `scikit-bio 0.7.4` has `skbio.diversity.alpha` modules `_chao1`, `_ace`, `_base` (chao1, chao1_ci, ace, goods_coverage, robbins, ...) (file list of the wheel).
  Single-sample abundance estimators only; no capture-recapture, no incidence (Chao2), no iNEXT-style rarefaction/extrapolation. Maintained (frequent 2026 releases).
- `rpy2 3.6.9` (bridge to R). `pymc-marketing 1.2.0` exists (Pareto/NBD style, not what we need).
- `ecopy 0.1.2.2`, `pyspecies 0.1.2` exist but are old/obscure (not evaluated).
- **Not on PyPI:** `pyinext`, `inext`, `chao1`, `species-richness`, `capture-recapture`, `mark-recapture`, `hillnumbers`, `breakaway`, `pychao`,
  `lincoln-petersen`, `spadepy`. A web search found no Python port of iNEXT/Rcapture/SPECIES. So the dossier's "no maintained Python package" holds; the
  closest are scikit-bio (single-sample) and your `pilot/estimators.py`.

**R via conda-forge (works in this sandbox; no root).** I did:
```bash
curl -L -o mm.tar.bz2 https://conda.anaconda.org/conda-forge/linux-64/micromamba-2.0.5-0.tar.bz2 && mkdir mm && tar xjf mm.tar.bz2 -C mm
export MAMBA_ROOT_PREFIX=$PWD/mamba_root
./mm/bin/micromamba create -y -n rcr -c conda-forge --override-channels r-base r-rcapture r-inext r-breakaway r-vgam r-fossil rpy2
./mm/bin/micromamba run -n rcr Rscript -e 'library(Rcapture); library(iNEXT); library(breakaway)'
```
Result: R 4.1.3, Rcapture 1.4.4, iNEXT 3.0.0, breakaway 3.0, rpy2 3.5.11, install about 20-30 s. A smoke test `closedpCI.0(X, m="Mh", h="Chao")` on a
500x5 simulated matrix returned abundance 494.8 (se 24.3), so Chao's Mh lower bound works. `micromamba search` also lists r-vegan, r-vgam, r-fossil. (R 4.1.3 is
old; conda picked it for the package set; newer R may need specifying `r-base>=4.3`, untested.)
- **Not on conda-forge (searched):** SpadeR, SPECIES, LCMCR, dga, SparseMSE, drpop, recapr, marked/RMark. CRAN, r-universe and Posit PM are blocked here, but
  the `github.com/cran/<pkg>` mirror clones fine: SpadeR, SPECIES, LCMCR, dga, SparseMSE cloned OK (not built or run). Install with
  `R CMD INSTALL <dir>` inside the conda env (needs a compiler: `conda install -c conda-forge compilers`); build not tested. On your own machine CRAN works normally.
- iNEXT 3.0.0 in this env means incidence-based Hill-number extrapolation (`iNEXT(x, datatype="incidence_raw")`) is available for K x S matrices.

---

## 9. Blockers and unknowns (ranked)

1. **HF is blocked in the sandbox.** Cannot see zoo file layout, cannot verify BashArena-HF, SLEIGHT, auditing-agents datasets. First-day task for someone
   with HF access: `huggingface_hub.list_repo_files("decoderesearch/synth-sae-bench-16k-v1-saes")`, download one SAE, run `eval_sae_on_synthetic_data`
   against both v1 and v2 worlds and confirm MCC matches `stats.json` (resolves v1/v2 question).
2. **Zoo "seeds" semantics**: unseeded joint (init + data) variation, possibly not reproducible. Decide what K = 5 means before E2 and do not claim "init-only".
3. **No GPU here.** E2 (download only) is CPU-feasible, but E6/E11 need a GPU (an estimated 7-60 GPU-hours depending on design) and AuditBench's 70B targets need
   2-4 x 80 GB GPUs. Docker daemon is not running here, so BashArena cannot be piloted in this sandbox.
4. **ICSE'24 algorithm not read.** Section 5.3 is a reconstruction. Obtain the PDF/Zenodo artifact (note the DOI discrepancy 10460578 vs 10416794) before E10.
5. **LinuxArena code location unknown**; no cost data.
6. **Costs are estimates**: no primary per-run cost for AuditBench, Petri, Bloom, BashArena found. Run 5 pilot runs each and read `api_usage_log` /
   Inspect token usage before committing a budget.
7. **AuditBench per-run public logs not found**: re-run required (about $0.4-1.0 per run on Haiku 4.5, est). Also pin `MAX_TOKENS=25000`.
8. **Non-Claude investigators need extra work in the AuditBench repo** (`openai_agent` backend unverified); Petri/Bloom via Inspect/LiteLLM are the easy
   multi-family route.
9. **Prices** for non-Anthropic models are from aggregators; re-verify on vendor pages. "Claude 5" lineup prices come from the Claude API skill's table dated 2026-10-06.
10. **BAITBENCH provides derived evidence packets, not transcripts**, with only 3 shortcut families: not a richness testbed.
11. **SAELens HEAD vs the version used to train the zoo**: `torch` RNG behaviour and `seed` semantics could differ (unverified).
12. R 4.1.3 from conda is old; the CRAN-only packages need source builds with a compiler (untested).

## 10. Search log (28 used)
LinuxArena x3 (repo not found), BAITBENCH, Böhme ICSE24 x4, Haiku/GPT-5-mini/Gemini Flash/Sonnet/open-weight/GPT-5.4 mini/Gemini 3.5 pricing x8,
Claude lineup x1, SAE training time x4, Python capture-recapture x1, AuditBench cost x2, HF auditing-agents x1, Petri/Bloom cost x1, zoo layout x1,
BashArena cost x1. Plus the `claude-api` skill for Anthropic list prices.
