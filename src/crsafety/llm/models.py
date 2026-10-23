"""Model registry and pins (H3, Q-D14).

``configs/llm/models.json`` lists each logical model ("qwen2.5-7b", ...) with
candidate builds in order of preference. ``configs/llm/pins.json`` is written
from the H3 serving check (E08-R008) and records, per logical model, the
candidate that passed with its Hugging Face commit sha and the vLLM version.

    spec = resolve("qwen2.5-7b")              # pinned build, else candidate 0
    spec = resolve("qwen2.5-7b", require_pinned=True)   # confirmatory runs
"""

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "configs" / "llm" / "models.json"
PINS = ROOT / "configs" / "llm" / "pins.json"
DTYPES = ("half", "float32")  # T4 (sm75) has no bf16
QUANTS = (None, "awq", "gptq", "bitsandbytes")


class NotPinned(RuntimeError):
    pass


@dataclass(frozen=True)
class ModelSpec:
    name: str
    family: str
    hf_id: str
    quantization: str | None
    dtype: str
    max_model_len: int
    revision: str | None = None
    gpu_memory_utilization: float = 0.90
    extra_args: tuple = ()
    candidate: int = 0
    pinned: bool = False
    vllm_version: str | None = None
    quant_source: str | None = None
    roles: tuple = field(default=(), compare=False)

    def identity(self):
        """What a cached generation depends on: the exact weights and numerics."""
        return dict(name=self.name, hf_id=self.hf_id, revision=self.revision,
                    quantization=self.quantization, dtype=self.dtype)

    def to_json(self):
        d = asdict(self)
        d["extra_args"], d["roles"] = list(self.extra_args), list(self.roles)
        return d


def load_registry(path=REGISTRY):
    reg = json.loads(Path(path).read_text())
    for name, m in reg["models"].items():
        if not m.get("candidates"):
            raise ValueError(f"{name}: no candidates")
        for c in m["candidates"]:
            if c["dtype"] not in DTYPES:
                raise ValueError(f"{name}: dtype {c['dtype']!r} not usable on T4 (use one of {DTYPES})")
            if c.get("quantization") not in QUANTS:
                raise ValueError(f"{name}: unknown quantization {c.get('quantization')!r}")
    for g, names in reg.get("groups", {}).items():
        missing = set(names) - set(reg["models"])
        if missing:
            raise ValueError(f"group {g}: unknown models {sorted(missing)}")
    return reg


def load_pins(path=PINS):
    p = Path(path)
    return json.loads(p.read_text())["pins"] if p.exists() else {}


def candidate_spec(name, i, registry=None, revision=None):
    reg = registry or load_registry()
    m = reg["models"][name]
    c = m["candidates"][i]
    return ModelSpec(
        name=name, family=m["family"], hf_id=c["hf_id"], quantization=c.get("quantization"),
        dtype=c["dtype"], max_model_len=int(c["max_model_len"]), revision=revision,
        gpu_memory_utilization=float(c.get("gpu_memory_utilization", 0.90)),
        extra_args=tuple(c.get("extra_args", ())), candidate=i,
        vllm_version=reg.get("vllm_version"), quant_source=c.get("quant_source"),
        roles=tuple(m.get("roles", ())))


def resolve(name, require_pinned=False, registry=None, pins=None):
    reg = registry or load_registry()
    if name not in reg["models"]:
        raise KeyError(f"unknown model {name!r}; registry has {sorted(reg['models'])}")
    pin = (load_pins() if pins is None else pins).get(name)
    if pin is None:
        if require_pinned:
            raise NotPinned(f"{name} has no pin in {PINS.relative_to(ROOT)}; run the H3 serving check first")
        return candidate_spec(name, 0, reg)
    spec = candidate_spec(name, int(pin["candidate"]), reg, revision=pin["revision"])
    if spec.hf_id != pin["hf_id"]:
        raise ValueError(f"{name}: pin says {pin['hf_id']} but candidate {pin['candidate']} is {spec.hf_id}")
    return replace(spec, pinned=True, vllm_version=pin.get("vllm_version"))


def group(name, registry=None):
    return list((registry or load_registry())["groups"][name])
