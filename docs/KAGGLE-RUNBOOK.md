# Kaggle runbook: Santosh's account

Every Kaggle job on Santosh's side, in the order to run them, with the
exact commands. The sandbox cannot reach Hugging Face, so these need a
Kaggle notebook with internet on and a GPU (T4 ×2 or P100).

The rules from `notebook/README.md` apply:
- register each run in the sandbox first (`tools/notebook.py new ...`, the
  ID is shown below);
- `git pull` before registering;
- copy outputs back into `results/<EXP>/<run_id>/` (files < 10 MB; larger
  ones go to a Kaggle dataset with their sha256 in the manifest);
- record GPU-hours.

**Before the v1 freeze, run only the rows marked "pre-freeze OK".** They
compute no outcomes (inventories, timings, seeding checks).

## Setup (every session)

```bash
git clone https://github.com/santoshcheethiralame-dot/MissingMass && cd MissingMass
pip install -q -e . "sae-lens==6.54.12" safetensors huggingface_hub
```

Checkpointing: the training scripts skip seeds whose
`sae_weights.safetensors` already exists. Point `--out` at a Kaggle dataset
you re-attach, and a cut session resumes where it stopped.

## Order

| # | Run | When | Command | GPU-h *(est)* |
|---|---|---|---|---|
| 1 | E02-R001 inventory | pre-freeze OK | `python analysis/e02/zoo.py inventory --out /kaggle/working/E02-R001` | < 0.5 |
| 2 | E06-R002 timing pilot (2 SAEs, base) | pre-freeze OK | `python analysis/e06/train.py --cell base --out /kaggle/working/e06 --seeds 0-1` | < 2 |
| 3 | E11 seeding repeat on Pythia-70M (logged under R002) | pre-freeze OK | `python analysis/e11/seeding_check.py --out /kaggle/working/E11-seed --hf pythia-70m-deduped --dataset apollo-research/monology-pile-uncopyrighted-tokenizer-EleutherAI-gpt-neox-20b --device cuda` | < 0.2 |
| 4 | E11-R002 timing pilot (1 SAE) | pre-freeze OK | `python analysis/e11/train.py --out /kaggle/working/e11 --seeds 0` | < 2 |
| 5 | E02 dead latents + histories (R002/R003) | after freeze | `python analysis/e02/fire_counts.py --out /kaggle/working/fires.json` then `python analysis/e02/zoo.py histories --out /kaggle/working/E02-R00X --fire-counts /kaggle/working/fires.json` | 1–3 |
| 6 | E03 M3 + bake-off | after freeze | `python analysis/e03/act_corr.py --out /kaggle/working/m3`, then `bakeoff.py --fire-counts ... --m3 ...` (see `analysis/e02/README.md`) | 2–4 |
| 7 | E06-R003…R013 (11 cells × 24 seeds) | after freeze | `python analysis/e06/train.py --cell <id> --out /kaggle/working/e06` for each cell in `analysis/e06/worlds.py`, then `zoo.py histories --world .../<cell>/world --zoo .../<cell>/zoo --reference-from 16 --fire-counts ...` | 20–40 |
| 8 | E11-R003 seeds (8 + 4 shared order) | after freeze | `python analysis/e11/train.py --out /kaggle/working/e11 --set seeds` | 15–25 |
| 9 | E11-R006 random-model null | after freeze | `python analysis/e11/train.py --out /kaggle/working/e11 --set null` | 4–8 |
| 10 | E15-R002 marks + 12 SAEs + latent stats | after freeze, after #8 (magnitudes) | `python analysis/e15/inject.py marks --out /kaggle/working/e15 --magnitudes mags.json`, then `inject.py train --out /kaggle/working/e15`, then `inject.py stats --out /kaggle/working/e15` | 15–25 |
| 11 | E16-R002 bracket per E06 cell | after #7 | `python analysis/e16/bracket.py --cell-dir /kaggle/working/e06/<cell> --out /kaggle/working/E16-R002/<cell>` | 2–5 |

The CPU analyses afterwards run in the sandbox, on copied histories:
- E06-R014: `analysis/e06/analyse.py`
- E07-R001: `analysis/e07/analyse.py`
- E04-R001: `analysis/e04/sae_arm.py`, which needs `true_match_cosines.json`
  from #5 and the E03 rule from #6
- E11: `analysis/e11/analyse.py`
- E15-R004: `analysis/e15/analyse.py`

## Inputs a later step needs from an earlier one

- **E04** needs `true_match_cosines.json` (written by `zoo.py histories`,
  #5) and the E03 winner (#6).
- **E15 marks** need real latent contribution magnitudes (activation ×
  ‖w_dec‖) from E11 SAEs (#8):
  `python analysis/e15/inject.py magnitudes --zoo /kaggle/working/e11/seeds --out mags.json`.
- **E07** reads the E02 and E06 histories written with `--fire-counts`
  (observed covariates per run in `items.csv`).
- **E16** reads the E06 training output directly (`world/` and `zoo/`).

## Not checked here (HF blocked)

These paths were smoke-tested in the sandbox only on local stand-ins:
- the SynthSAEBench zoo layout (checked by #1);
- loading Pythia-70M and the pre-tokenized Pile through TransformerLens and
  `datasets` (#3, #4);
- `HookedTransformer.from_pretrained_no_processing(...).cfg` for the
  random-weights null (#9).

If one fails, fix the loader in a small PR before the full run.

# Kushal's account

Same rules as above (register first, `git pull` before registering, copy
outputs into `results/<EXP>/<run_id>/`, record GPU-hours). Kushal's own LLM
stack (vLLM, call cache, model pinning, Q-D14) is documented with E08–E10;
this section lists only the jobs that use the shared `crsafety` code.

## Setup (once per account)

Gemma-2 weights are gated. Either
- accept the Gemma licence on Hugging Face, create a read token, and add it
  in the notebook as a Kaggle secret named `HF_TOKEN` (Add-ons → Secrets);
  or
- accept the licence on Kaggle Models (`google/gemma-2`), attach the
  `transformers` variants `gemma-2-2b-it` and `gemma-2-2b` as inputs, and
  pass their `/kaggle/input/...` paths to `--it` / `--pt`.

The Gemma Scope SAE weights (`google/gemma-scope-2b-pt-res`) are not gated.

```python
# cell 1 (only for the HF route)
import os
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
```
```bash
# cell 2
git clone https://github.com/santoshcheethiralame-dot/MissingMass && cd MissingMass
pip install -q -e . "sae-lens==6.54.12" safetensors huggingface_hub
```

## Order

| # | Run | When | Command | GPU-h *(est)* |
|---|---|---|---|---|
| K1 | E09-R003 Gemma Scope T3 tool check (Q-D15) | pre-freeze OK (checks only) | `python analysis/e09/gemma_scope_check.py --out results/E09/E09-R003 --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json --record` (add `--it <path> --pt <path>` for the Kaggle Models route) | < 0.3 |
| K2 | E09-R009 T3 tool re-check, user-token rule | pre-freeze OK (checks only) | `python analysis/e09/gemma_scope_check.py --run-id E09-R009 --out results/E09/E09-R009 --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json --record` | < 0.3 |
| K3 | E09-R010 T3 background blocklist | pre-freeze OK (tool input) | `python analysis/e09/background_blocklist.py --out results/E09/E09-R010 --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json --record` | < 0.2 |
| K4 | E09-R011 T3 blocklist diagnostic | after E09-R002 (needs the 16 organisms and their trigger prompts) | `python analysis/e09/blocklist_diagnostic.py --out results/E09/E09-R011 --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json --blocklist results/E09/E09-R010/blocklist.json --organism <name>=<merged organism dir> ... --trigger-prompts <dir of <name>.txt> --record` | < 0.5 |
| K5 | ~~E08-R010 H3 serving check, part 3~~ done 2026-10-27: Mistral pinned, Mistral+Qwen pair passes; Gemma-2-2B blocked by a 401 (token) | done | `python analysis/e08/serving_check.py --run-id E08-R010 --out results/E08/E08-R010 --models mistral-7b,gemma2-2b-it --pair mistral-7b,qwen2.5-7b --record` | 0.28 (actual) |
| K6 | E08-R011 H3 serving check, part 4: Gemma-2-2B-it only (E09 base; not needed for the Nov 10 pilots) | pre-freeze OK (infrastructure) | `python analysis/e08/serving_check.py --run-id E08-R011 --out results/E08/E08-R011 --models gemma2-2b-it --record`; setup is in `kaggle/llm_serving.ipynb`. Run it with Save Version → Save & Run All | < 0.3 |

K5 and K6 need GPU T4 x2 and an HF_TOKEN that can read gated repos: the
Gemma 2, Llama 3.1 and Mistral-7B-Instruct-v0.3 licences accepted on its
account, and, for a fine-grained token, "Read access to contents of all
public gated repos you can access" ticked (E08-R010 got a 401 on Gemma with
a new token). Download `results/E08/E08-R011/` as a zip (the version's Output tab); its `pins.json` goes to
`configs/llm/pins.json`. See `kaggle/README.md`.

K1–K4 need a GPU (T4 or P100; it loads two 2B models in bf16, about 11 GB).
The label file was built in the sandbox from Neuronpedia's public S3 export
(`analysis/e09/neuronpedia_labels.py`; source and sha256 in
`results/E09/E09-R003/labels/SOURCE.json`), so no Neuronpedia access is
needed on Kaggle. Afterwards, download `results/E09/E09-R003/`
(`manifest.json`, `summary.json`, `examples.txt`, `responses.json`) and copy
it into the repo. The pass criteria C1–C5 are in the script's docstring;
`summary.json` has `all_pass`. Then
`python tools/notebook.py set E09-R003 status=succeeded summary="..."` (or
`failed`, with the failing check).
