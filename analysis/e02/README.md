# E02 on Kaggle

The sandbox cannot reach Hugging Face (Q-D1), so E02 runs on Santosh's Kaggle
account (internet on). In a Kaggle notebook:

```bash
pip install -q safetensors huggingface_hub scipy
git clone https://github.com/santoshcheethiralame-dot/MissingMass && cd MissingMass
pip install -q -e .
# R001 (inventory; allowed before the freeze: computes no outcomes)
python analysis/e02/zoo.py inventory --out /kaggle/working/E02-R001
# R002/R003 (oracle + matched histories): only after the v1 freeze
python analysis/e02/zoo.py histories --out /kaggle/working/E02-R00X [--fire-counts fires.json]
```

Register each run first (`tools/notebook.py new E02 ...`) in the sandbox,
then copy `/kaggle/working/E02-R00X` into `results/E02/` (files < 10 MB in
git; larger ones go to a Kaggle dataset with their sha256 in the manifest).

Tested on 2026-10-22 against a fake mini-zoo in the same file layout
(SAELens 6.54 `synthetic_model.safetensors`; zoo
`<arch>/l0-<L0>/seed-<s>/sae_weights.safetensors`). R001 verifies the real
layout; if it differs, fix the loader before R002.

**Dead latents:** `analysis/e02/fire_counts.py` counts each latent's firings
on 10^6 generator samples (SAELens 6.54.12 + torch; GPU), and
`zoo.py histories --fire-counts fires.json` drops the dead ones. Both were
tested end to end on 2026-10-22 against a tiny world and two SAEs trained
with SAELens's own `SyntheticSAERunner` (the real file layout, including
`synthetic_model_config.json`, `cfg.json` and `sparsity.safetensors`).

```bash
pip install -q "sae-lens==6.54.12"
python analysis/e02/fire_counts.py --out /kaggle/working/fires.json      # GPU
python analysis/e02/zoo.py histories --out /kaggle/working/E02-R00X --fire-counts /kaggle/working/fires.json
```

## E03 on the same Kaggle session

```bash
python analysis/e03/act_corr.py --out /kaggle/working/m3        # GPU; M3 assignments
python analysis/e03/bakeoff.py --out /kaggle/working/E03-R00X \
    --fire-counts /kaggle/working/fires.json --m3 /kaggle/working/m3
```

