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
  ‖w_dec‖) from an E11 SAE (#8). Measure them with `inject.py stats` on
  an E11 zoo, or take a quantile list of `act_sums / counts × ‖w_dec‖`.
  Save it as `mags.json` (a JSON list). Not yet scripted; write it on the
  day.
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
