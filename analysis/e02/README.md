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

**Known gap:** dead-latent removal needs per-latent firing counts on 10^6
generator samples (SAELens `SyntheticModel.sample` + each SAE's encoder, on
GPU). That script is still to be written (with E03-R002, which needs the
same activations).
