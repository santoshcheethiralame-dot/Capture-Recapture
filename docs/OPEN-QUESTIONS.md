# Open questions and verification tasks

Things we must find out before they bite. Close each one with a date, an
answer and evidence, then move it to "Resolved". Items marked **blocks**
gate an experiment.

## Data access and testbed facts

| ID | Question | Blocks | How to resolve | Status |
|---|---|---|---|---|
| Q-D1 | Can this environment reach Hugging Face and arXiv? (They were blocked on 2026-10-22.) | E02, E06, E11 | Allow `huggingface.co`, `arxiv.org`, `export.arxiv.org` in the environment's network settings, or download elsewhere | open |
| Q-D2 | What exactly is in `decoderesearch/synth-sae-bench-16k-v1-saes`? File layout and count; which world version reproduces `stats.json` | E02 | `huggingface_hub.list_repo_files(...)`; recompute MCC for one SAE under v1 and v2 | open (partly answered: seeds are uncontrolled, joint initialisation + data; see Resolved) |
| Q-D4 | AuditBench: measured cost per run, and whether the LoRAs download and serve | E09 | Run E09-R001/R002 on rented GPUs | open (repo, outputs and settings known; see Resolved) |
| Q-D5 | Is there a Qwen3-32B (or smaller) AuditBench replication that is public? | E09 fallback | Paper + repo | open |
| Q-D6 | ControlArena / BashArena: can a planted-weakness monitor be plugged in? | E10 stretch | Read the code | open |
| Q-D7 | Exact de-adaptation algorithm (Liyanage et al., ICSE 2024, "Algorithm 1") | E10 A3a | — | **resolved 2026-10-22**: read from `paper/ICSE24.pdf` in the GitHub repo `mboehme/mboehme.github.io` (git clone works where the web does not). Defaults α = 0.11, β = 0.5 (RQ1; α = 0.3 in the figure), "add 1" to f1, f2. The paper's artefact is Zenodo 10.5281/zenodo.10575734. Implemented in `crsafety.deadapt`; behaviour in E01-R009; consequences in D-012 |
| Q-D8 | Licences: SynthSAEBench, AuditBench, BAITBENCH, SLEIGHT-Bench (gated), Tensor Trust, board-game SAEs | release | Check each repo or card | open |
| Q-D9 | Model snapshots and prices for the E08 ladder (4 families) | E08 budget | Provider pages | open |
| Q-D10 | Chiu-Chao (2016) singleton-correction formula (exact) | E05 (c), E04 (H4c) | Read PeerJ 4:e1634 (open access) from a machine that can reach peerj.com or PMC; no Chao-lab package on GitHub implements it (checked 2026-10-22: SpadeR, iNEXT, iNEXT.3D, iNEXT.4steps, iNEXT.beta3D) | open; blocked in the sandbox (peerj.com, PMC, arXiv denied). E00 contingency applied: `breakaway_nof1` is the f1-free option until then (D-009) |
| Q-D12 | LinuxArena source code location (only Docker Hub images `linuxarena/env-*` found) | E10 human-attack comparator (optional) | arXiv page of 2604.15384; ask the authors | open |
| Q-D13 | Is `LanguageModelSAERunnerConfig.seed` really unused in the SAELens version we pin? | E06, E11 | R001 seeding check | **resolved for E06 (2026-10-22, E06-R015)**: `SyntheticSAERunnerConfig` (SAELens 6.54.12) has no seed field; manual `torch.manual_seed` before construction (init) and before training (data) controls both, exactly. E11's `LanguageModelSAERunnerConfig` still to check in E11-R001 |
| Q-D14 | Which open models to pin: auditor and attacker (Qwen, 7–8B), L3 families (Llama, Gemma), target (Mistral), judge (Phi or OLMo), organism base (Gemma-2-2B-it). Do they all run on T4 (fp16 or AWQ)? | E08, E09, E10 | E08-R008 serving check (fit, fp16 numerics), then E08-R001 and E09 pilots (quality) | **in progress (2026-10-23)**: candidates in `configs/llm/models.json` (Qwen2.5-7B AWQ; Llama-3.1-8B AWQ; Gemma-2-9B-it 4-bit; target Mistral-7B-Instruct-v0.3 4-bit; judges Phi-4, Phi-4-mini, OLMo-2-7B; Gemma-2-2B-it fp16/fp32). E08-R008 pins what runs on a T4. 2026-10-26: E08-R008 failed (infra, nothing loaded; causes in E08 page); re-run as E08-R009. Gemma-2-9B may not be servable on a T4 with vLLM; Granite-3.3-8B added as the alternative third L3 family (decision pending). 2026-10-26: E08-R009 pinned Qwen2.5-7B (AWQ), Llama-3.1-8B (AWQ), Granite-3.3-8B (bnb); Gemma-2-9B not servable on T4 with vLLM 0.19.1; Mistral target needs a system-prompt template (E08-R010). 2026-10-27: third L3 family is Granite-3.3-8B (D-016). 2026-10-27: E08-R010 pinned Mistral-7B AWQ (v3 template) and passed the Mistral+Qwen pair check, so all four E08/E10 pilot models are pinned; Gemma-2-2B-it (E09 base) left for E08-R011 after a 401. 2026-10-28: E08-R011 showed vLLM 0.19.1 cannot serve Gemma 2 on a T4 (FlexAttention lacks the logit soft cap; Triton fp32 exceeds shared memory; fp16 refused); Gemma-2-2B and the E09 organisms move to a transformers backend (`crsafety.llm.hf_server`, same API), checked in E08-R012. 2026-10-29: E08-R012 pinned Gemma-2-2B-it (fp32, transformers backend, 121 tok/s at 32 concurrent). Pinned: Qwen2.5-7B, Mistral-7B, Llama-3.1-8B, Granite-3.3-8B, Gemma-2-2B-it, which covers the E08/E10 pilots and the E09 base. Still unpinned: the judge (Phi-4, Phi-4-mini or OLMo-2-7B), to be checked before the E08 judge κ check |

## Budget

| ID | Question | Blocks | Status |
|---|---|---|---|
| Q-B3 | Current Kaggle GPU quota and session limits for both accounts | scheduling | open (check in each account's settings) |
| Q-B4 | Apply for API credits (e.g. the OpenAI researcher programme) to enable E18? | E18 | optional |

## Novelty checks (before running the novelty-upgrade experiments)

| ID | Question | Blocks | Status |
|---|---|---|---|
| Q-N1 | Has anyone calibrated detectability by planting known items into a real ML system for unseen-failure estimation? Check mark-resight analogues and software seeded-defect work | E15 | answered 2026-10-23 (E15-R001): nothing does the full design; closest is Kansal. `research/notes/J2-e15-novelty.md` |
| Q-N2 | Has anyone bounded missed SAE features from above using the reconstruction residual? | E16 | answered 2026-10-23 (E16-R001): nothing found; closest is Engels et al. 2025, whose decomposition the upper bound builds on. `research/notes/J-e16-novelty.md` |
| Q-N3 | Has anyone used open-population capture-recapture (Cormack-Jolly-Seber) to separate removal from concealment after safety training? | E17 | open |
| Q-N4 | Weekly scoop check (see `RISKS.md`) | all | recurring |

## Numbers to verify in primary sources before citing

From `research/README.md` §7:
- SynthSAEBench zoo details;
- AuditBench default success rate (~37%) and per-run logs;
- BAITBENCH run count (~1,258);
- MonitoringBench 81% in 2 of 5 tiers;
- Nasr et al. Good-Turing figures;
- technology-assisted review success rates 69.9% / 53.1%;
- photo-ID "920%";
- Tensor Trust licence;
- the number of runs the 2025 auditing super-agent pooled.

## Venue facts

| ID | Question | Status |
|---|---|---|
| Q-V1 | NeurIPS 2027 deadline and checklist version | open (expected spring 2027) |
| Q-V2 | ICML 2027 deadline (estimated 22 Jan 2027) | open |
| Q-V3 | Which ICLR 2027 workshops fit (list after ~29 Nov 2026) | open |
| Q-V4 | SaTML 2028 call (~Sept 2027) | open |

## Resolved

| ID | Answer | Evidence | Date |
|---|---|---|---|
| Q-D3 | SynthSAEBench-16k generator: Zipf exponent 0.5, p ∈ [5e-4, 0.4] (linear rescale), hierarchy 128 roots × branching 4 × depth 3 (mutually exclusive siblings), low-rank correlation rank 25 scale 0.1, magnitude means 5.0 → 4.0 with folded-normal std, seed 42. Average L0 about 34. | `experiments/create_synth_bench_16k_model.py` (code read by an agent) | 2026-10-22 |
| Q-D2 (part) | The zoo's 5 "seeds" are not controlled: the seed is only used in output paths, so SAE initialisation and the data stream vary jointly and unseeded | `sweep_l0.py`; SAELens 6.54.12 has no training seed | 2026-10-22 |
| Q-D4 (part) | Official repo is `safety-research/auditing-agents`. Per-run outputs: `transcript.json`, `research_log.md`, `quirks/*.md`. Judge: `claude-sonnet-4-6`. Targets need 2–4 × 80 GB GPUs; the GPU-free `system_prompt` suite has 16 quirks. Default `--max-tokens` differs between scripts, so set 25000. No public per-run logs | repo README and code | 2026-10-22 |
| Q-D11 | BAITBENCH (MIT) releases derived evidence packets for 1,258 runs, not raw transcripts, and has only 3 shortcut families. Not a richness testbed | `DATA_MANIFEST.md`, dataset tally | 2026-10-22 |
| Q-B1 | Budget is **$0** for now: open models, sandbox CPU, free Kaggle GPUs. Frontier replication only via E18 | D-007 | 2026-10-22 |
| Q-B2 | GPU source: Kaggle, one account each (Santosh: SAE track; Kushal: LLM track) | D-007, `docs/TEAM.md` | 2026-10-22 |
| R tooling | R 4.1.3 + Rcapture 1.4.4 + iNEXT 3.0.0 + breakaway 3.0 install in this sandbox via micromamba/conda-forge; CRAN-only packages are cloneable from `github.com/cran/<pkg>` | agent smoke test (`closedpCI.0`, Mh Chao) | 2026-10-22 |
| Q-D15 | Yes. `gemma-scope-2b-pt-res-canonical` / `layer_12/width_16k/canonical` loads through SAELens 6.54.12 on a Kaggle T4 next to Gemma-2-2B and -it (bf16); hook layer 12, 16,384 features, all labelled offline from Neuronpedia's public S3 export; L0 79 (nominal 82), FVU 0.078 on pt and 0.101 on -it chat residuals; 0.34 s per uncached call, so the E09 §3 cache contingency is not needed for speed. Caveat: as built, the tool's output is nearly prompt-independent (see LOG 2026-10-23, E09-R003 result). | `results/E09/E09-R003/` | 2026-10-23 |
