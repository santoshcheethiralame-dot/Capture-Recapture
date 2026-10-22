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
| Q-D7 | Exact de-adaptation algorithm (Liyanage et al., ICSE 2024, "Algorithm 1", defaults α = 0.3, β = 0.5) | E10 A3a | Read `mboehme.github.io/paper/ICSE24.pdf` and the Zenodo artefact (two records: 10.5281/zenodo.10460578 and 10416794) | open (E10 has a flagged reconstruction) |
| Q-D8 | Licences: SynthSAEBench, AuditBench, BAITBENCH, SLEIGHT-Bench (gated), Tensor Trust, board-game SAEs | release | Check each repo or card | open |
| Q-D9 | Model snapshots and prices for the E08 ladder (4 families) | E08 budget | Provider pages | open |
| Q-D10 | Chiu-Chao (2016) singleton-correction formula (exact) | E00, E05 | Read PeerJ 4:e1634 and Chao lab R code | open |
| Q-D12 | LinuxArena source code location (only Docker Hub images `linuxarena/env-*` found) | E10 human-attack comparator (optional) | arXiv page of 2604.15384; ask the authors | open |
| Q-D13 | Is `LanguageModelSAERunnerConfig.seed` really unused in the SAELens version we pin? | E06, E11 | R000 seeding check | open |

## Budget

| ID | Question | Blocks | Status |
|---|---|---|---|
| Q-B1 | **What budget is available** (API and GPU)? Decides lean vs planned designs (`COMPUTE.md`) | v1 freeze (E06, E08, E09 designs) | **open: owner decision** |
| Q-B2 | Which GPU source (Kaggle/Colab, rental, institutional)? | E06, E09, E11 | open |

## Novelty checks (before running the novelty-upgrade experiments)

| ID | Question | Blocks | Status |
|---|---|---|---|
| Q-N1 | Has anyone calibrated detectability by planting known items into a real ML system for unseen-failure estimation? Check mark-resight analogues and software seeded-defect work | E15 | open |
| Q-N2 | Has anyone bounded missed SAE features from above using the reconstruction residual? | E16 | open |
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
| R tooling | R 4.1.3 + Rcapture 1.4.4 + iNEXT 3.0.0 + breakaway 3.0 install in this sandbox via micromamba/conda-forge; CRAN-only packages are cloneable from `github.com/cran/<pkg>` | agent smoke test (`closedpCI.0`, Mh Chao) | 2026-10-22 |
