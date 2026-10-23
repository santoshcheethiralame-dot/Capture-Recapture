"""E06 cells as SAELens configurations (E06 §2; scaled world, D-007).

World settings not named in E06 §2 are copied from SynthSAEBench-16k
(`synth-sae-bench-experiments/experiments/create_synth_bench_16k_model.py`):
magnitudes 5.0 -> 4.0 (linear) with folded-normal std (0.5, 0.5), bias 0.5,
orthogonalization 100 steps, correlation rank 25 scale 0.1. The hierarchy is
scaled with the number of features: 32 roots for 4,096 features (SynthSAEBench
uses 128 for 16,384), branching 4, depth 3, mutually exclusive siblings.
"""

from dataclasses import dataclass, replace

MASTER = 20261028  # 20261022 + 6


@dataclass(frozen=True)
class E06Cell:
    id: str
    alpha: float = 1.0          # Zipf exponent
    p_min: float = 1e-7
    p_max: float = 0.4
    hierarchy: bool = False
    correlation: bool = False
    n_true: int = 4096
    d: int = 256
    width: int = 1024
    l0: int = 25
    samples: int = 50_000_000
    seed_type: str = "both"     # both | init-only (shared data stream) | data-only (shared init)


BASE = E06Cell("base")
CELLS = [
    BASE,
    replace(BASE, id="alpha0.5", alpha=0.5),
    replace(BASE, id="alpha1.5", alpha=1.5),
    replace(BASE, id="pmin5e-4", p_min=5e-4),
    replace(BASE, id="hier", hierarchy=True),
    replace(BASE, id="corr", correlation=True),
    replace(BASE, id="hier+corr", hierarchy=True, correlation=True),
    replace(BASE, id="width1.0", width=4096),
    replace(BASE, id="init-only", seed_type="init-only"),
    replace(BASE, id="data-only", seed_type="data-only"),
    replace(BASE, id="budget20M", samples=20_000_000),
]
N_EVAL, N_REF = 16, 8


def world_config(cell, world_seed=MASTER):
    from sae_lens.synthetic.firing_magnitudes import FoldedNormalMagnitudeConfig, LinearMagnitudeConfig
    from sae_lens.synthetic.synthetic_model import (HierarchyConfig, LowRankCorrelationConfig,
                                                    OrthogonalizationConfig, SyntheticModelConfig,
                                                    ZipfianFiringProbabilityConfig)
    return SyntheticModelConfig(
        num_features=cell.n_true, hidden_dim=cell.d,
        firing_probability=ZipfianFiringProbabilityConfig(max_prob=cell.p_max, min_prob=cell.p_min,
                                                          exponent=cell.alpha),
        hierarchy=HierarchyConfig(total_root_nodes=max(1, round(128 * cell.n_true / 16384)), branching_factor=4,
                                  mutually_exclusive_portion=1.0, mutually_exclusive_min_depth=0,
                                  compensate_probabilities=True, scale_children_by_parent=True,
                                  max_depth=3) if cell.hierarchy else None,
        mean_firing_magnitudes=LinearMagnitudeConfig(start=5.0, end=4.0),
        std_firing_magnitudes=FoldedNormalMagnitudeConfig(mean=0.5, std=0.5),
        correlation=LowRankCorrelationConfig(correlation_scale=0.1, rank=25) if cell.correlation else None,
        orthogonalization=OrthogonalizationConfig(num_steps=100, lr=3e-4),
        bias=0.5, seed=world_seed)


def sae_config(cell):
    from sae_lens.saes.batchtopk_sae import BatchTopKTrainingSAEConfig
    return BatchTopKTrainingSAEConfig(k=cell.l0, d_in=cell.d, d_sae=cell.width)


def seeds(cell, k):
    """(init_seed, data_seed) of seed number k (0..23; 16 evaluation + 8 reference).

    'init-only' varies initialisation over a shared data stream; 'data-only'
    varies the data stream over a shared initialisation."""
    import numpy as np
    idx = [c.id for c in CELLS].index(cell.id)
    s = np.random.SeedSequence(MASTER, spawn_key=(idx, k)).generate_state(2)
    shared = np.random.SeedSequence(MASTER, spawn_key=(idx, 999)).generate_state(1)[0]
    init, data = int(s[0]), int(s[1])
    if cell.seed_type == "init-only":
        data = int(shared)
    elif cell.seed_type == "data-only":
        init = int(shared)
    return init, data
