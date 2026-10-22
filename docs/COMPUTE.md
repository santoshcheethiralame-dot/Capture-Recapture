# Compute and budget

Estimates as of 22 October 2026. Every figure marked *(est)* comes from
arithmetic on token counts and list prices, not from published per-run
costs. **Measure 5 pilot runs per testbed before committing a budget**, and
update this page with real numbers from the run manifests.

## Where things can run

| Resource | Has | Good for |
|---|---|---|
| This cloud sandbox | 4 CPU, 15 GB RAM, **no GPU, no Docker daemon**; PyPI, conda-forge and GitHub reachable; Hugging Face, arXiv, CRAN, Zenodo blocked | E00 (R via conda-forge works), E01, E05, E13, analysis of anything already downloaded |
| Free GPU (Kaggle T4 / Colab) | 16 GB GPU, session caps (check current quotas) | Pythia-70M SAEs (E11), small pilots (E06 at 50M samples) |
| Rented GPU | H100 / A100, about $2–4 per GPU-hour *(est)* | E06 grid, E11, fine-tuning (E12, E15, E17), 70B AuditBench serving (E09) |
| APIs | Anthropic, OpenAI, Google, open-weights hosts | E04, E08, E09 agents and judges, E10 attackers |

## Per-experiment estimates

| Exp | Compute | Estimate | Basis |
|---|---|---|---|
| E00 | CPU | minutes | — |
| E01 | CPU | 1–3 h on 8 cores | pilot timing scaled |
| E02 | Download 0.6 GB (25 SAEs, one L0) to about 5 GB (all 175); CPU for decoder matching; GPU helpful for activation sampling | < 5 GPU-h | SAE size ~25 MB each *(est)* |
| E03 | GPU for activation matching (M3) | 2–4 GPU-h | — |
| E04 | CPU + LLM calls | < $30 | ~1–3k cheap calls |
| E05 | CPU | hours | — |
| E06 | GPU: about 15–20 min per SAE on an H100 at 200M samples (SAELens tutorial). 11 cells × 24 seeds = 264 SAEs | **70–90 H100-h ≈ $150–350**; 2–4× longer on consumer GPUs | tutorial timing *(est)* |
| E07 | CPU | hours | — |
| E08 | API: Petri audits, about $0.5–2 each *(est)*; 5 ladder levels × 16 targets × 16 runs = 1,280 audits | **$650–2,600**; cheaper auditors cut this (and change the catcher) | Petri token estimate |
| E09 | API: investigator (Haiku 4.5) about $0.4–1.0 per run, plus judge (Sonnet 4.6) about $0.03–0.12 *(est)*. GPU: Llama-3.3-70B + LoRAs needs 2–4 × 80 GB GPUs | **Full** (3,584 runs): $1.5–4k API + ~$200–500 GPU. **Reduced** (1,344 runs): $0.6–1.5k API + ~$100–200 GPU | repo defaults *(est)* |
| E10 | API: attacker runs on a purpose-built monitor, about $1 per run with a Sonnet-class attacker *(est)*; ~110 runs | **$100–300** | — |
| E10 (BashArena stretch) | Docker + API: about $3–8 per attack trajectory (Sonnet-class attacker + mini monitor) *(est)* | $2.4–6.4k for 800 trajectories; under $400 with a Haiku-class attacker | BashArena reference runner |
| E11 | GPU: Pythia-70M SAE about 0.5–1.5 h on a 24 GB card *(est)*; ~36 SAEs | 20–50 GPU-h ≈ $50–150 | ensembling-paper timings *(est)* |
| E12 | GPU (LoRA fine-tune 8B × 4) + API audits (~300) | ~$300–800 | *(est)* |
| E13 | CPU | hours | — |
| E14 | API | ~$50–150 | — |
| E15 | GPU (12 SAEs + fine-tune) + API (16 audits) | ~$100–300 | *(est)* |
| E16 | CPU/GPU | small | — |
| E17 | GPU (fine-tunes) + API | ~$200–500 | *(est)* |

## Budget scenarios for the NeurIPS paper (core + important tiers)

| Scenario | API | GPU | Notes |
|---|---|---|---|
| **Lean** | ~$1.2–2.5k | ~$200 | E09 reduced design; E08 with cheaper auditors at L0/L1; E06 cut to 6 cells |
| **Planned** | ~$3–6k | ~$500–800 | As pre-registered |
| **Minimum viable** (workshop only) | ~$300 | ~$50 | E02/E03/E05 + E09 system-prompt suite (GPU-free) + E10 |

> **Decision needed (Q-B1):** what budget is available? It decides between
> the lean and planned designs, and must be settled **before the v1
> freeze**, because the reduced designs are pre-specified alternatives.

## Cost controls

- Cache every LLM call (PROTOCOLS §6). Use batch APIs for judges where
  latency does not matter (about 50% cheaper).
- Pilot 5 runs per testbed. If measured cost is more than 1.5× the estimate,
  apply the experiment's pre-declared cuts and log a deviation.
- Track spend per experiment in the manifests. Review weekly against this
  table.
- A stretch experiment never takes budget from a core experiment.

## Prices used (per 1M tokens, USD)

Anthropic list prices are from the Claude API reference dated 2026-10-06.
Others are from aggregators and **unverified**: check vendor pages before
spending.

| Model | Input | Output |
|---|---|---|
| Claude Haiku 4.5 | 1.00 | 5.00 |
| Claude Haiku 5.5 | 0.10 | 0.50 |
| Claude Sonnet 5.5 | 2.00 | 10.00 |
| Claude Sonnet 4.6 | 3.00 | 15.00 |
| Claude Opus 5.5 | 4.00 | 20.00 |
| GPT-5 mini *(unverified)* | 0.25 | 2.00 |
| Gemini 3 Flash *(unverified)* | 0.50 | 3.00 |
| DeepSeek V3.2 *(unverified)* | ~0.25 | ~0.40 |
| Llama 3.3 70B via a host *(unverified)* | 0.10–0.23 | 0.32–0.40 |

## Actuals

Filled from the run manifests.

| Exp | GPU-h | API $ | Including failed and exploratory runs? |
|---|---|---|---|
