# Compute and budget

**Budget: $0** (decision D-007, 2026-10-22). Everything confirmatory runs on
this sandbox's CPU and on free Kaggle GPUs, using open-weight models. Paid
compute only enters through E18 (frontier replication), if credits arrive.

Estimates are *(est)* until measured. **Every testbed's pilot records actual
GPU-hours per unit**; update this page from the run manifests.

## Resources

| Resource | What it has | Limits (check current terms) | Used for |
|---|---|---|---|
| This cloud sandbox | 4 CPU, 15 GB RAM, no GPU, no Docker; PyPI, conda-forge, GitHub reachable; Hugging Face and arXiv blocked | session-based; commit everything | E00, E01, E05, E07, E13, analysis |
| Kaggle notebooks, **Santosh's account** | 2 × T4 (16 GB each) or 1 × P100; internet and Hugging Face access | historically about 30 GPU-hours a week; sessions about 12 h; about 20 GB of `/kaggle/working` output | SAE work: E02, E03, E06, E11, E15 (SAE arm) |
| Kaggle notebooks, **Kushal's account** | same | same | LLM work: E04 (attack arm), E08, E09, E10, E12, E14, E15 (audit arm), E17 |
| Local machines (if any) | — | — | optional |

Two accounts give about **60 free GPU-hours a week**. Kaggle needs phone
verification for GPU and internet access, and sessions can be cut off, so:
- checkpoint every 30 minutes;
- cache every LLM call (PROTOCOLS §6);
- write results to a Kaggle dataset at the end of each session.

## T4 practicalities

- **No bf16 on T4:** use fp16, or AWQ/GPTQ 4-bit. Some models (e.g. Gemma 2)
  can overflow in fp16. Test in the pilot and switch to a quantised variant
  if needed.
- **LLM serving:** vLLM with tensor parallel 2 on 2 × T4 for 7–9B fp16
  models, or a single T4 for AWQ. Batch many audits concurrently;
  throughput, not latency, matters.
- **Fine-tuning:** QLoRA (e.g. Unsloth or PEFT + bitsandbytes) fits 2B
  models easily and 7–8B models with care on a T4.
- **SAE training:** SAELens on GPU; the synthetic generator also runs on
  GPU.

## Per-experiment estimates (Kaggle GPU-hours)

| Exp | Owner | Where | GPU-h *(est)* | Notes |
|---|---|---|---|---|
| E00 | Santosh | sandbox | 0 | R via conda-forge |
| E01 | Santosh | sandbox | 0 | 2–6 CPU-h |
| E02 | Santosh | Kaggle | 2–5 | zoo download 0.6–5 GB; decoder matching on GPU or CPU |
| E03 | Santosh | Kaggle | 2–4 | activation matching (M3) |
| E04 | Santosh + Kushal | sandbox + Kaggle | 1–2 | attack variants from a local model |
| E05 | Santosh | sandbox | 0 | |
| E06 | Santosh | Kaggle | 20–40 | scaled world (4,096 features, d = 256); 264 SAEs; measured in R002 |
| E07 | Santosh | sandbox | 0 | |
| E08 | Kushal | Kaggle | 15–30 | 768 confirmatory audits (+256 at L2) |
| E09 | Kushal | Kaggle | 30–45 | implants about 8–11, audits about 20–30, SAE tool about 1 |
| E10 | Kushal | sandbox + Kaggle | 5–10 | monitor on CPU, attackers on GPU |
| E11 | Santosh | Kaggle | 30–45 | 16 Pythia-70M SAEs + Gemma Scope analysis |
| E12 | Kushal | Kaggle | 15–25 | stretch |
| E13 | Santosh | sandbox | 0 | |
| E14 | Kushal | Kaggle | 3–5 | stretch |
| E15 | Santosh + Kushal | Kaggle | 15–25 | important; after the novelty check |
| E16 | Santosh | Kaggle | 2–5 | stretch |
| E17 | Kushal | Kaggle | 10–20 | stretch |
| E18 | Kushal | API + rented GPUs | — | only if funded |

**Totals:**

| Scope | Santosh | Kushal |
|---|---|---|
| Core + important, to NeurIPS | ~60–100 GPU-h | ~55–90 GPU-h |
| Workshop subset (E02, E03, E05 + E08 L0/L3 + E10), by 25 January | ~5–10 GPU-h | ~15–25 GPU-h |

Both fit within about 2–4 weeks of each account's quota, spread over six
months.

## Rules

- Pilot first. If a pilot measures more than 1.5× the estimate, apply the
  experiment's pre-declared cuts before freezing.
- Stretch experiments never use quota needed by core experiments.
- Either account can run any experiment, since seeds and configs are
  deterministic. If one account is blocked, the other takes over, and the
  run's manifest records which account ran it.
- Record GPU-hours per run in the manifest (`cost.gpu_hours`). The NeurIPS
  checklist asks for total compute, **including failed and exploratory
  runs**.

## If money appears later

See E18 and `research/README.md` for API cost estimates. Indicative figures:
- original AuditBench: about $0.4–1 per run plus 2–4 × 80 GB GPUs;
- a frontier E08 ladder: about $0.5–2 per audit.

Anthropic list prices (per 1M tokens, 2026-10-06): Haiku 4.5 $1/$5, Haiku
5.5 $0.10/$0.50, Sonnet 5.5 $2/$10. Other providers' prices are unverified.

## Actuals

| Exp | Account | GPU-h | Including failed and exploratory runs? |
|---|---|---|---|
| E00 (R001–R004) | sandbox CPU | 0 | yes: about 5 CPU-min (R reference runs 3.5 + 1.3 min, pytest seconds), plus harness debugging runs of similar size |
| E01 (R001–R008) | sandbox CPU (4 cores) | 0 | yes: wall time R001 4.1 min, R002 4.2, R003 1.3, R004 18.7, R005 8.2, R006 0.1, R007 8.9, R008 ≈ 9; ≈ 55 min on 4 cores (vs the 1–3 h estimate) |
| E08 (R008, H3 serving check) | Kushal, Kaggle 2 × T4 | 0.38 | yes: failed run (infra), nothing loaded |
