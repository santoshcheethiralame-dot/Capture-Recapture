"""E15-R002 SAE arm: plant M = 400 marks into Pythia-70M layer-3 activations and train K = 12 SAEs.

    python analysis/e15/inject.py marks --out <dir> [--magnitudes mags.json] [--d 512]
    python analysis/e15/inject.py train --out <dir> [--seeds 0-11] [--device cuda]
    python analysis/e15/inject.py train --out <dir> --tiny        # CPU smoke test (tiny local model)

`marks` writes <dir>/marks.npz: unit directions, firing probabilities p_j
(log-uniform grid 1e-6 to 1e-2, randomly assigned), magnitudes m_j and the
25% held-out flag. Seeds come from SeedSequence(20261037). `--magnitudes`
is a JSON list of real latent contribution magnitudes (activation x
||w_dec||), e.g. from E11-R003 SAEs. Each mark takes a value drawn from it;
without the file, magnitudes are drawn log-uniformly between 1 and 10.

`stats` measures each trained SAE's per-latent firing counts and activation
sums on fresh injected activations (the observed covariates for R004).

`train` adds sum_j b_tj m_j u_j to blocks.3.hook_resid_post on every token,
with b_tj ~ Bernoulli(p_j). The hook is permanent, so it acts on the
activations the SAE is trained on; the model's own computation downstream
is irrelevant to SAE training. The marks draw from their own torch
Generator, reseeded with each SAE's data seed. The init/data seeding is as
in E11-R001. Per-mark firing counts during training go to
seed-<k>/mark_fires.json.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis" / "e11"))

MASTER = 20261037  # 20261022 + 15
M, P_LO, P_HI, HELD_OUT = 400, 1e-6, 1e-2, 0.25


def make_marks(d, magnitudes=None, m=M, p_lo=P_LO, p_hi=P_HI):
    rng = np.random.default_rng(np.random.SeedSequence(MASTER, spawn_key=(0,)))
    U = rng.normal(size=(m, d))
    U /= np.linalg.norm(U, axis=1, keepdims=True)
    p = np.exp(np.linspace(np.log(p_lo), np.log(p_hi), m))[rng.permutation(m)]
    mag = rng.choice(np.asarray(magnitudes, float), m) if magnitudes is not None else \
        np.exp(rng.uniform(np.log(1), np.log(10), m))
    held = np.zeros(m, bool)
    held[rng.choice(m, int(round(HELD_OUT * m)), replace=False)] = True
    return dict(U=U.astype(np.float32), p=p, magnitude=mag, held_out=held)


class Injector:
    def __init__(self, marks, device="cpu"):
        self.U = torch.as_tensor(marks["U"], device=device)
        self.p = torch.as_tensor(marks["p"], dtype=torch.float32, device=device)
        self.mag = torch.as_tensor(marks["magnitude"], dtype=torch.float32, device=device)
        self.gen = torch.Generator(device=device)
        self.fires = torch.zeros(len(marks["p"]), dtype=torch.long, device=device)
        self.tokens = 0

    def reset(self, seed):
        self.gen.manual_seed(int(seed))
        self.fires.zero_()
        self.tokens = 0

    def __call__(self, act, hook):
        shape = act.shape[:-1]
        n = int(np.prod(shape))
        b = torch.rand(n, self.p.numel(), generator=self.gen, device=act.device) < self.p
        self.fires += b.sum(0)
        self.tokens += n
        add = (b.to(act.dtype) * self.mag.to(act.dtype)) @ self.U.to(act.dtype)
        return act + add.reshape(*shape, -1)


def cmd_marks(a):
    mags = json.loads(Path(a.magnitudes).read_text()) if a.magnitudes else None
    mk = make_marks(a.d, mags, p_lo=a.p_lo, p_hi=a.p_hi)
    Path(a.out).mkdir(parents=True, exist_ok=True)
    np.savez(Path(a.out) / "marks.npz", **mk)
    print(f"{M} marks, d = {a.d}, p in [{mk['p'].min():.1e}, {mk['p'].max():.1e}], held out {mk['held_out'].sum()}")


def cmd_train(a):
    import train as e11
    from sae_lens import LanguageModelSAERunnerConfig
    from sae_lens.config import LoggingConfig
    from sae_lens.llm_sae_training_runner import LanguageModelSAETrainingRunner
    from sae_lens.saes.batchtopk_sae import BatchTopKTrainingSAEConfig

    out = Path(a.out)
    z = np.load(out / "marks.npz")
    marks = {k: z[k] for k in z.files}
    if a.tiny:
        import seeding_check
        model, data = seeding_check.tiny_model_and_data(n_seq=2048)
        d_in, ctx, tokens, width, name = 64, 64, 40_000, 256, "tiny-local"
    else:
        from transformer_lens import HookedTransformer
        model = HookedTransformer.from_pretrained_no_processing(e11.MODEL, device=a.device)
        data, d_in, ctx, tokens, width, name = None, 512, 128, e11.TOKENS, e11.WIDTH, e11.MODEL
    inj = Injector(marks, a.device)
    model.add_perma_hook(f"blocks.{e11.LAYER}.hook_resid_post", inj)
    for k in e11.seed_list(a.seeds):
        sdir = out / "zoo" / name / f"l0-{e11.L0}" / f"seed-{k}"
        if (sdir / "sae_weights.safetensors").exists():
            continue
        s = np.random.SeedSequence(MASTER, spawn_key=(1, k)).generate_state(2)
        init, dseed = int(s[0]), int(s[1])
        t0 = time.time()
        torch.manual_seed(init)
        cfg = LanguageModelSAERunnerConfig(
            sae=BatchTopKTrainingSAEConfig(k=e11.L0, d_in=d_in, d_sae=width), model_name=name,
            hook_name=f"blocks.{e11.LAYER}.hook_resid_post", dataset_path=a.dataset, is_dataset_tokenized=True,
            streaming=not a.tiny, context_size=ctx, training_tokens=tokens,
            train_batch_size_tokens=4096 if not a.tiny else 512, store_batch_size_prompts=16,
            n_batches_in_buffer=32 if not a.tiny else 16, lr=3e-4, device=a.device, output_path=str(sdir),
            logger=LoggingConfig(log_to_wandb=False))
        runner = LanguageModelSAETrainingRunner(cfg, override_dataset=data, override_model=model)
        runner.activations_store.shuffle_input_dataset(dseed, buffer_size=1 if a.tiny else 10_000)
        torch.manual_seed(dseed)
        inj.reset(dseed)
        runner.run()
        sdir.mkdir(parents=True, exist_ok=True)
        (sdir / "mark_fires.json").write_text(json.dumps(dict(tokens=inj.tokens, fires=inj.fires.cpu().tolist())) + "\n")
        print(dict(seed=k, init=init, data=dseed, seconds=round(time.time() - t0, 1), tokens=inj.tokens), flush=True)


def cmd_stats(a):
    """Per-latent firing counts and activation sums of every trained SAE on fresh
    injected activations (the observed covariates of E15 R004)."""
    import train as e11
    from sae_lens import SAE
    out = Path(a.out)
    z = np.load(out / "marks.npz")
    marks = {k: z[k] for k in z.files}
    if a.tiny:
        import seeding_check
        model, data = seeding_check.tiny_model_and_data(n_seq=512)
        tokens = torch.tensor(data["input_ids"])
    else:
        from datasets import load_dataset
        from transformer_lens import HookedTransformer
        model = HookedTransformer.from_pretrained_no_processing(e11.MODEL, device=a.device)
        ds = load_dataset(a.dataset, split="train", streaming=True)
        need = a.tokens // 128 + 1
        tokens = torch.tensor([r["input_ids"][:128] for _, r in zip(range(need), ds)])
    inj = Injector(marks, a.device)
    inj.reset(np.random.SeedSequence(MASTER, spawn_key=(2,)).generate_state(1)[0])
    hook = f"blocks.{e11.LAYER}.hook_resid_post"
    model.add_perma_hook(hook, inj)
    saes = {f.parent.name: SAE.load_from_disk(str(f.parent), device=a.device)
            for f in sorted(out.glob("zoo/*/l0-*/seed-*/sae_weights.safetensors"))}
    acc = {k: [torch.zeros(s.cfg.d_sae, dtype=torch.float64, device=a.device) for _ in range(2)] for k, s in saes.items()}
    n = 0
    with torch.no_grad():
        for i in range(0, tokens.shape[0], a.batch):
            _, cache = model.run_with_cache(tokens[i:i + a.batch].to(a.device), names_filter=hook)
            x = cache[hook].reshape(-1, cache[hook].shape[-1])
            for k, sae in saes.items():
                f = sae.encode(x.to(sae.W_dec.dtype))
                acc[k][0] += (f > 0).sum(0)
                acc[k][1] += f.clamp(min=0).sum(0).double()
            n += x.shape[0]
    res = {k: dict(tokens=n, counts=v[0].cpu().tolist(), act_sums=v[1].cpu().tolist()) for k, v in acc.items()}
    (out / "latent_stats.json").write_text(json.dumps(res) + "\n")
    print(f"{len(saes)} SAEs, {n} tokens")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("marks")
    m.add_argument("--out", required=True)
    m.add_argument("--d", type=int, default=512)
    m.add_argument("--magnitudes")
    m.add_argument("--p-lo", type=float, default=P_LO)
    m.add_argument("--p-hi", type=float, default=P_HI)
    t = sub.add_parser("train")
    t.add_argument("--out", required=True)
    t.add_argument("--seeds", default="0-11")
    t.add_argument("--dataset", default="apollo-research/monology-pile-uncopyrighted-tokenizer-EleutherAI-gpt-neox-20b")
    t.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    t.add_argument("--tiny", action="store_true")
    st = sub.add_parser("stats")
    st.add_argument("--out", required=True)
    st.add_argument("--tokens", type=int, default=1_000_000)
    st.add_argument("--batch", type=int, default=32)
    st.add_argument("--dataset", default="apollo-research/monology-pile-uncopyrighted-tokenizer-EleutherAI-gpt-neox-20b")
    st.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    st.add_argument("--tiny", action="store_true")
    a = ap.parse_args()
    dict(marks=cmd_marks, train=cmd_train, stats=cmd_stats)[a.cmd](a)


if __name__ == "__main__":
    main()
