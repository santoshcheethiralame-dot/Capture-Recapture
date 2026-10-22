# Data, models and code registry

Every external artefact we use, its version, licence and access status, and
every artefact we produce. Fill the "pinned" column on first use: the commit,
revision or snapshot ID, and a sha256 for files.

## External artefacts

| Artefact | Source | Used in | Licence | Access from sandbox | Pinned version | Notes |
|---|---|---|---|---|---|---|
| SynthSAEBench world v1 / v2 | HF `decoderesearch/synth-sae-bench-16k-v1`, `-v2` | E02, E03, E06 | check (Q-D8) | **blocked (HF)** | | Same feature vectors, probabilities, correlation and hierarchy in v1 and v2; only child magnitudes differ. Decoder-based truth is unaffected by the version. |
| SynthSAEBench SAE zoo | HF `decoderesearch/synth-sae-bench-16k-v1-saes` | E02, E03 | check | **blocked (HF)** | | 5 architectures × 7 L0 × 5 "seeds", width 4,096 (about 5 GB). **Seeds are not controlled:** initialisation and data both vary, unseeded (`sweep_l0.py`). |
| SynthSAEBench generator + experiments | GitHub `decoderesearch/SAELens` (`sae_lens.synthetic`), `decoderesearch/synth-sae-bench-experiments` | E02, E06 | SAELens MIT (check experiments repo) | GitHub OK | SAELens 6.54.12 read | World config: Zipf exponent 0.5, p ∈ [5e-4, 0.4], 128 roots × branching 4 × depth 3, low-rank correlation (rank 25, scale 0.1), magnitudes 5.0 → 4.0, seed 42 |
| SAE reliability audit (null and oracle SAEs) | GitHub `decoderesearch/saebench-reliability-audit` | E02, E03 | check | GitHub OK | | |
| AuditBench (code) | GitHub `safety-research/auditing-agents` | E08, E09 | check | GitHub OK | | `run_all_agents.py`; per run: `transcript.json`, `quirks/*.md` (≤ 10 predictions), Sonnet-judge 0/1 score. **Set `--max-tokens 25000` explicitly** (script defaults differ). |
| AuditBench targets | HF `auditing-agents/llama_70b_*` LoRAs + `meta-llama/Llama-3.3-70B-Instruct` | E09 | Llama 3.3 licence + check | **blocked (HF)**; needs 2–4 × 80 GB GPUs | | 14 behaviours; adversarial levels none / high / KTO |
| AuditBench system-prompt suite | in `auditing-agents` (`--suite-name system_prompt`) | E08, E09 fallback | as above | GitHub OK; GPU-free | | 16 quirks as system prompts on any API model |
| Petri (Inspect) | `pip install inspect-petri` (upstream `meridianlabs-ai/inspect_petri`) | E08, E12 | check | PyPI OK | | Any model family via `--model-role auditor=<provider/model>`; `--epochs` gives repeated audits |
| Bloom | `safety-research/bloom` (frozen) → `petri_bloom` | E12 | MIT (reported) | GitHub OK | | |
| BashArena tasks | GitHub `redwoodresearch/basharena_public` (640 tasks locally) | E10 stretch | check | GitHub OK; **Docker needed** | | 4 side tasks |
| ControlArena | `pip install control-arena` / GitHub `UKGovernmentBEIS/control-arena` | E10 stretch | check | OK; Docker needed | | Attack strategies are injected through the attack-policy system prompt |
| BAITBENCH | GitHub `juanjvazquez/BAITBENCH` | backlog | MIT | GitHub OK | | Derived evidence packets for 1,258 runs; only 3 shortcut families, so not a richness testbed |
| Böhme FSE'21 artefact | GitHub `Adaptive-Bias/fse21_paper270` | E10 (A3) | check | GitHub OK | | Estimator code readable |
| Liyanage et al. ICSE'24 artefact | Zenodo 10.5281/zenodo.10460578 or 10416794 (two records found) | E10 (A3) | check | **blocked (Zenodo)** | | Algorithm text needed (Q-D7) |
| Pythia-70M / 160M | HF `EleutherAI/pythia-*` | E11, E15 | Apache-2.0 | blocked (HF) | | |
| Gemma Scope | HF `google/gemma-scope*` | E11 | CC-BY-4.0 (reported) | blocked (HF) | | Nested width ladders |
| Board-game SAEs | HF `adamkarvonen/chess_saes`, `othello_saes`; GitHub `adamkarvonen/SAE_BoardGameEval` | E11 | check | HF blocked | | |
| Open models (pinned at freeze, Q-D14) | HF: Qwen (7–8B instruct; also 3B/14B-AWQ for L2), Llama (≤ 8B instruct), Gemma (Gemma-2-2B-it organism base; ≤ 9B auditor), Mistral (≤ 8B target), Phi or OLMo (judge) | E04, E08–E10, E12, E14, E15, E17 | per model licence (Llama and Gemma have use policies) | via Kaggle | | All run locally with vLLM; no API terms involved |
| Gemma Scope (Gemma-2-2B) | HF `google/gemma-scope-2b-pt-*` | E09 (T3 tool), E11 | CC-BY-4.0 (reported) | via Kaggle | | Used as the white-box audit tool |
| Kansal repos | GitHub `ParitKansal/undiscovered-failures`, `label-error-capture-recapture` | baselines | MIT (code), CC BY 4.0 (text) | GitHub OK | | |
| R packages | conda-forge (+ bioconda for phyloseq): `r-base>=4.5`, `r-rcapture`, `r-inext`, `r-vegan`, `r-vgam`, `r-jsonlite`; breakaway built from GitHub `adw96/breakaway` (conda-forge only has 3.0, which pins R 4.1); GitHub `cran/<pkg>` mirror: SpadeR, SPECIES, LCMCR, dga, SparseMSE | E00, all | GPL (varies) | **works in sandbox** via micromamba (fetch the micromamba binary from conda-forge; micro.mamba.pm is blocked) | E00-R001/R003: R 4.5.3, iNEXT 3.0.2, vegan 2.7.5, Rcapture 1.4.4, VGAM 1.1.14, breakaway 5.0.1 (adw96/breakaway commit 35f83d4) | |

## Artefacts we produce

| Artefact | Location | Tier (`DISCLOSURE.md`) | Documentation | Licence |
|---|---|---|---|---|
| Estimator library | `src/crsafety/` | public | README, docstrings | MIT |
| Simulation results (E01, E05) | `results/E01/`, `results/E05/` | public | datasheet | CC BY 4.0 (proposed, D-006) |
| Detection histories (every experiment) | `results/EXX/<run>/histories/` | public | datasheet | CC BY 4.0 (proposed) |
| Our SAE replicates (E06, E11, E15) | external storage (HF, once access exists) | public | model card | MIT / Apache-2.0 per base model |
| Audit outputs (E08, E09, E12) | external storage | public, unless upstream terms say otherwise | datasheet | per upstream |
| Attack transcripts (E10) | external storage | public for our own monitor (after review); withheld for deployed models | datasheet + canary | CC BY 4.0 / withheld |

## Storage rules

- Git holds code, configs, the notebook, small result tables (< 10 MB) and
  manifests.
- Large files (SAE weights, activations, transcripts) go to external
  storage. Their path and sha256 go in the run manifest.
- Never commit API keys. Use `.env`, which is git-ignored.
