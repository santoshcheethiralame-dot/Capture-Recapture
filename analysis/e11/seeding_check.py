"""E11-R001: does manual seeding control SAE initialisation and token order? (E11 §2)

    python analysis/e11/seeding_check.py --out results/E11/E11-R001 --record            # tiny local model (CPU)
    python analysis/e11/seeding_check.py --out ... --hf pythia-70m-deduped \
        --dataset <tokenized HF dataset>                                            # same check on Kaggle

E11 §2: `LanguageModelSAERunnerConfig.seed` is not read by the training
runner, so E11 seeds by hand:
- torch.manual_seed(init_seed) before constructing the runner (the SAE is
  built in the constructor);
- then `activations_store.shuffle_input_dataset(data_seed)` and
  torch.manual_seed(data_seed) (buffer mixing uses the global RNG).

For 4 (init, data) combinations plus a repeat of the first, this hashes W_dec
at step 0 and the first training batch from the activations store. Pass if
the W_dec hashes are equal iff the init seeds are equal, the batch hashes are
equal iff the data seeds are equal, and the repeat reproduces both. The
default uses a tiny randomly initialised HookedTransformer (4 layers,
d = 64) on a fixed random token dataset, so the mechanics can be checked
without network access. The property does not depend on the model's
weights.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402
import torch  # noqa: E402

from crsafety import manifest  # noqa: E402

COMBOS = [(1, 1), (1, 2), (2, 1), (2, 2), (1, 1)]


def h(t):
    return hashlib.sha256(t.detach().float().cpu().contiguous().numpy().tobytes()).hexdigest()[:16]


def tiny_model_and_data(ctx=64, n_seq=512):
    from datasets import Dataset
    from transformer_lens import HookedTransformer, HookedTransformerConfig
    torch.manual_seed(0)
    model = HookedTransformer(HookedTransformerConfig(n_layers=4, d_model=64, n_ctx=ctx, d_head=16, n_heads=4,
                                                      d_vocab=512, act_fn="gelu", normalization_type="LN"))
    toks = np.random.default_rng(0).integers(0, 512, size=(n_seq, ctx))
    return model, Dataset.from_dict({"input_ids": toks.tolist()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--hf", default=None, help="TransformerLens model name (Kaggle); default: tiny local model")
    ap.add_argument("--dataset", default=None, help="tokenized dataset path, with --hf")
    ap.add_argument("--layer", type=int, default=3)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--record", action="store_true")
    a = ap.parse_args()
    from sae_lens import LanguageModelSAERunnerConfig
    from sae_lens.config import LoggingConfig
    from sae_lens.llm_sae_training_runner import LanguageModelSAETrainingRunner
    from sae_lens.saes.batchtopk_sae import BatchTopKTrainingSAEConfig
    import sae_lens

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = manifest.start(out.name, "E11", " ".join(sys.argv), vars(a), seeds=dict(combos=str(COMBOS)),
                       packages=("numpy", "torch", "sae-lens", "transformer-lens", "crsafety")) if a.record else None
    if a.hf:
        model, data, d_in, ctx = None, None, None, 128
    else:
        model, data = tiny_model_and_data()
        d_in, ctx = 64, 64
    rows = []
    for init, dseed in COMBOS:
        torch.manual_seed(init)
        cfg = LanguageModelSAERunnerConfig(
            sae=BatchTopKTrainingSAEConfig(k=32, d_in=d_in or 512, d_sae=8 * (d_in or 512)),
            model_name=a.hf or "tiny-local", hook_name=f"blocks.{a.layer}.hook_resid_post",
            dataset_path=a.dataset or "local", is_dataset_tokenized=True, streaming=False, context_size=ctx,
            training_tokens=4096, train_batch_size_tokens=512, store_batch_size_prompts=16, n_batches_in_buffer=16,
            device=a.device, logger=LoggingConfig(log_to_wandb=False))
        runner = LanguageModelSAETrainingRunner(cfg, override_dataset=data, override_model=model)
        w = h(runner.sae.W_dec)
        runner.activations_store.shuffle_input_dataset(dseed)
        torch.manual_seed(dseed)
        b = h(runner.activations_store.next_batch())
        rows.append(dict(init=init, data=dseed, W_dec_step0=w, first_batch=b))
        print(rows[-1], flush=True)
    ok_i = all((r["W_dec_step0"] == s["W_dec_step0"]) == (r["init"] == s["init"]) for r in rows for s in rows)
    ok_d = all((r["first_batch"] == s["first_batch"]) == (r["data"] == s["data"]) for r in rows for s in rows)
    res = dict(rows=rows, model=a.hf or "tiny local HookedTransformer (4 layers, d=64, random weights)",
               init_controls_W_dec=ok_i, data_controls_batch=ok_d, passed=ok_i and ok_d,
               sae_lens=sae_lens.__version__, torch=torch.__version__)
    (out / "seeding_check.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    if m is not None:
        manifest.finish(m, outputs=[(out / "seeding_check.json").resolve().relative_to(ROOT)],
                        status="succeeded" if res["passed"] else "failed")


if __name__ == "__main__":
    main()
