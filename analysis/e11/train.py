"""E11 R003 / R006: train Pythia-70M SAEs with controlled seeds (Kaggle GPU).

    python analysis/e11/train.py --out /kaggle/working/e11 --set seeds [--seeds 0-11]
    python analysis/e11/train.py --out ... --set null [--seeds 0-3]      # random-weights Pythia-70M (R006)
    python analysis/e11/train.py --out ... --tiny                         # CPU smoke test (local tiny model)

E11 §2: layer 3 residual, BatchTopK width 8,192 at L0 = 32, 50M tokens.
- Seeds 0-7 have independent init and data order.
- Seeds 8-11 share one data order (the dependence comparison).
- The null set trains 4 seeds on a randomly initialised Pythia-70M
  (weights from torch.manual_seed(NULL_MODEL_SEED)).
Seeding as checked in E11-R001: torch.manual_seed(init) before the runner,
then activations_store.shuffle_input_dataset(data) and torch.manual_seed(data).
Output: <out>/<set>/<model>/l0-32/seed-<k>/; trained seeds are skipped.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))

MASTER = 20261033  # 20261022 + 11
NULL_MODEL_SEED = 20261033 + 999
MODEL, LAYER, WIDTH, L0, TOKENS = "pythia-70m-deduped", 3, 8192, 32, 50_000_000
DATASET = "apollo-research/monology-pile-uncopyrighted-tokenizer-EleutherAI-gpt-neox-20b"  # pre-tokenized, ctx 2048
SHARED_FROM = 8  # seeds >= 8 share one data order


def seeds(set_name, k):
    idx = {"seeds": 0, "null": 1}[set_name]
    s = np.random.SeedSequence(MASTER, spawn_key=(idx, k)).generate_state(2)
    init, data = int(s[0]), int(s[1])
    if set_name == "seeds" and k >= SHARED_FROM:
        data = int(np.random.SeedSequence(MASTER, spawn_key=(idx, 999)).generate_state(1)[0])
    return init, data


def seed_list(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--set", choices=["seeds", "null"], default="seeds")
    ap.add_argument("--seeds", default=None)
    ap.add_argument("--dataset", default=DATASET)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--tiny", action="store_true")
    a = ap.parse_args()
    from sae_lens import LanguageModelSAERunnerConfig
    from sae_lens.config import LoggingConfig
    from sae_lens.llm_sae_training_runner import LanguageModelSAETrainingRunner
    from sae_lens.saes.batchtopk_sae import BatchTopKTrainingSAEConfig

    ks = seed_list(a.seeds or ("0-11" if a.set == "seeds" else "0-3"))
    model, data, d_in, ctx, tokens, width, model_name = None, None, 512, 128, TOKENS, WIDTH, MODEL
    if a.tiny:
        import seeding_check
        model, data = seeding_check.tiny_model_and_data(n_seq=2048)
        d_in, ctx, tokens, width, model_name = 64, 64, 40_000, 256, "tiny-local"
    elif a.set == "null":
        from transformer_lens import HookedTransformer
        torch.manual_seed(NULL_MODEL_SEED)
        cfg_m = HookedTransformer.from_pretrained_no_processing(MODEL).cfg  # architecture only
        model = HookedTransformer(cfg_m).to(a.device)  # random init (Heap et al. null)
    log = []
    base = Path(a.out) / a.set / model_name / f"l0-{L0}"
    for k in ks:
        sdir = base / f"seed-{k}"
        if (sdir / "sae_weights.safetensors").exists():
            continue
        init, dseed = seeds(a.set, k)
        t0 = time.time()
        torch.manual_seed(init)
        cfg = LanguageModelSAERunnerConfig(
            sae=BatchTopKTrainingSAEConfig(k=L0, d_in=d_in, d_sae=width),
            model_name=model_name, hook_name=f"blocks.{LAYER}.hook_resid_post", dataset_path=a.dataset,
            is_dataset_tokenized=True, streaming=not a.tiny, context_size=ctx, training_tokens=tokens,
            train_batch_size_tokens=4096 if not a.tiny else 512, store_batch_size_prompts=16,
            n_batches_in_buffer=32 if not a.tiny else 16, lr=3e-4, device=a.device,
            output_path=str(sdir), logger=LoggingConfig(log_to_wandb=False))
        runner = LanguageModelSAETrainingRunner(cfg, override_dataset=data, override_model=model)
        runner.activations_store.shuffle_input_dataset(dseed, buffer_size=1 if a.tiny else 10_000)
        torch.manual_seed(dseed)
        runner.run()
        log.append(dict(seed=k, init=init, data=dseed, seconds=round(time.time() - t0, 1)))
        print(log[-1], flush=True)
    base.mkdir(parents=True, exist_ok=True)
    (base / f"train_log_{int(time.time())}.json").write_text(json.dumps(dict(set=a.set, runs=log), indent=1) + "\n")


if __name__ == "__main__":
    main()
