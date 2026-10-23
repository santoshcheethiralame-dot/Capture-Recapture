"""E06-R001: does manual seeding control SAE initialisation and data order? (Q-D13)

    python analysis/e06/seeding_check.py --out results/E06/E06-R001 [--device cpu]

E06 §2: SAELens does not seed training itself, so E06 calls
torch.manual_seed(init_seed) before constructing the runner (the SAE is
initialised in its constructor) and torch.manual_seed(data_seed) after
construction, before training (the activation generator uses the global torch
RNG). For 4 seed combinations, plus a repeat of the first, this hashes W_dec at
step 0 and the first training batch drawn exactly as `SyntheticSAERunner.run`
draws it. Pass if: W_dec hashes are equal iff init seeds are equal, batch
hashes are equal iff data seeds are equal, and the repeat reproduces both.
"""

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).parent))

import torch  # noqa: E402

import worlds  # noqa: E402
from crsafety import manifest  # noqa: E402


def h(t):
    return hashlib.sha256(t.detach().cpu().contiguous().numpy().tobytes()).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--record", action="store_true", help="write a run manifest (registered run)")
    a = ap.parse_args()
    from sae_lens.config import LoggingConfig
    from sae_lens.synthetic import SyntheticModel, SyntheticSAERunner, SyntheticSAERunnerConfig
    from sae_lens.synthetic.training import SyntheticActivationIterator
    import sae_lens

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cell = worlds.BASE
    m = None
    if a.record:
        m = manifest.start(out.name, "E06", " ".join(sys.argv), dict(cell=cell.__dict__),
                           seeds=dict(world=worlds.MASTER, combos="(1,1),(1,2),(2,1),(2,2),(1,1)"),
                           packages=("numpy", "scipy", "torch", "sae-lens", "crsafety"))
    with tempfile.TemporaryDirectory() as tmp:
        world = SyntheticModel(worlds.world_config(cell), device=a.device)
        world.save(Path(tmp) / "world")
        rows = []
        for init, data in [(1, 1), (1, 2), (2, 1), (2, 2), (1, 1)]:
            torch.manual_seed(init)
            cfg = SyntheticSAERunnerConfig(synthetic_model=str(Path(tmp) / "world"), sae=worlds.sae_config(cell),
                                           training_samples=4096, batch_size=4096, device=a.device,
                                           logger=LoggingConfig(log_to_wandb=False))
            runner = SyntheticSAERunner(cfg)
            w = h(runner.sae.W_dec)
            torch.manual_seed(data)
            it = SyntheticActivationIterator(feature_dict=runner.synthetic_model.feature_dict,
                                             activations_generator=runner.synthetic_model.activation_generator,
                                             batch_size=cfg.batch_size, autocast=cfg.autocast_data)
            b = h(next(iter(it)))
            rows.append(dict(init=init, data=data, W_dec_step0=w, first_batch=b))
            print(rows[-1], flush=True)
    ok_init = all((r["W_dec_step0"] == s["W_dec_step0"]) == (r["init"] == s["init"]) for r in rows for s in rows)
    ok_data = all((r["first_batch"] == s["first_batch"]) == (r["data"] == s["data"]) for r in rows for s in rows)
    res = dict(rows=rows, init_controls_W_dec=ok_init, data_controls_batch=ok_data, passed=ok_init and ok_data,
               sae_lens=sae_lens.__version__, torch=torch.__version__,
               runner_config_has_seed_field=any("seed" in f for f in SyntheticSAERunnerConfig.__dataclass_fields__))
    (out / "seeding_check.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=2))
    if m is not None:
        manifest.finish(m, outputs=[(out / "seeding_check.json").resolve().relative_to(ROOT)],
                        status="succeeded" if res["passed"] else "failed")


if __name__ == "__main__":
    main()
