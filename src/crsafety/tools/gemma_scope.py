"""White-box SAE tool for E09 configuration T3 (handoff H7, Santosh -> Kushal).

E09 §2: "for a prompt, return the top active SAE features with their
Neuronpedia-style labels, and the features most changed relative to the base
model on the same prompt". The tool is model-agnostic. It needs
- ``resid_ft`` / ``resid_base``: prompt -> (tokens x d) residual stream at
  the SAE's hook point, for the audited (fine-tuned) and the base model;
- ``encode``: (n x d) -> (n x d_sae) SAE feature activations;
- ``labels``: {feature index: label} (a Neuronpedia export saved on Kaggle;
  Neuronpedia is not called at run time).

A feature's activation on a prompt is its maximum over tokens, the first
token (BOS) excluded. "Most changed" ranks |ft - base| of that maximum and
reports the sign. :class:`PromptBank` caches the max-activation vectors
(E09 §3 contingency: if the tool is too slow on a T4, the auditor queries a
fixed bank plus at most ``max_new`` new prompts per run). :func:`from_hf`
builds the tool from a Hugging Face model pair and a SAELens SAE (Gemma Scope:
``SAE.from_pretrained("gemma-scope-2b-pt-res-canonical",
"layer_12/width_16k/canonical")``).
"""

import hashlib
import json
from pathlib import Path

import numpy as np


class BudgetExceeded(RuntimeError):
    """The run used up its allowance of new (uncached) prompts."""


class PromptBank:
    """Cache of per-prompt max feature activations, keyed by (model tag, prompt)."""

    def __init__(self, path=None, max_new=None):
        self.path = Path(path) if path else None
        self.max_new = max_new
        self.new = 0
        self.store = {}
        if self.path and self.path.exists():
            z = np.load(self.path, allow_pickle=False)
            self.store = {k: z[k] for k in z.files}

    @staticmethod
    def key(tag, prompt):
        return tag + ":" + hashlib.sha256(prompt.encode()).hexdigest()[:24]

    def get(self, tag, prompt, compute):
        k = self.key(tag, prompt)
        if k not in self.store:
            if self.max_new is not None and self.new >= self.max_new:
                raise BudgetExceeded(f"more than {self.max_new} new prompts this run")
            self.store[k] = np.asarray(compute(prompt), np.float32)
            self.new += 1
        return self.store[k]

    def save(self):
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(self.path, **self.store)


class WhiteBoxTool:
    def __init__(self, resid_ft, resid_base, encode, labels=None, bank=None, skip_first=True):
        self.resid = {"ft": resid_ft, "base": resid_base}
        self.encode = encode
        self.labels = {int(k): v for k, v in (labels or {}).items()}
        self.bank = bank or PromptBank()
        self.skip_first = skip_first

    def _max_acts(self, tag, prompt):
        def compute(p):
            R = np.asarray(self.resid[tag](p))
            if self.skip_first and R.shape[0] > 1:
                R = R[1:]
            return np.asarray(self.encode(R)).max(axis=0)
        return self.bank.get(tag, prompt, compute)

    def _row(self, f, **vals):
        return dict(feature=int(f), label=self.labels.get(int(f), "(unlabelled)"),
                    **{k: round(float(v), 4) for k, v in vals.items()})

    def top_features(self, prompt, k=10):
        a = self._max_acts("ft", prompt)
        idx = [i for i in np.argsort(-a)[:k] if a[i] > 0]
        return [self._row(i, activation=a[i]) for i in idx]

    def diff_features(self, prompt, k=10):
        a, b = self._max_acts("ft", prompt), self._max_acts("base", prompt)
        d = a - b
        idx = [i for i in np.argsort(-np.abs(d))[:k] if d[i] != 0]
        return [self._row(i, change=d[i], audited=a[i], base=b[i]) for i in idx]

    def __call__(self, prompt, k=10):
        """The tool response given to the auditor agent (JSON-serialisable)."""
        return dict(prompt=prompt, top_features=self.top_features(prompt, k),
                    most_changed_vs_base=self.diff_features(prompt, k))

    @staticmethod
    def render(resp):
        """Plain-text rendering for the auditor's context window."""
        L = [f"SAE features for prompt: {resp['prompt']!r}", "Top active features (audited model):"]
        L += [f"  #{r['feature']} {r['label']} (act {r['activation']})" for r in resp["top_features"]] or ["  none"]
        L.append("Features most changed vs the base model:")
        L += [f"  #{r['feature']} {r['label']} ({'+' if r['change'] > 0 else ''}{r['change']}; "
              f"audited {r['audited']}, base {r['base']})" for r in resp["most_changed_vs_base"]] or ["  none"]
        return "\n".join(L)


def hf_resid(model, tokenizer, layer, chat=False, device="cpu"):
    """prompt -> (tokens x d) hidden state after block ``layer`` (= SAELens
    ``blocks.{layer}.hook_resid_post``; hidden_states[0] is the embedding)."""
    import torch

    @torch.no_grad()
    def f(prompt):
        text = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False,
                                             add_generation_prompt=True) if chat else prompt
        ids = tokenizer(text, return_tensors="pt")["input_ids"].to(device)
        out = model(input_ids=ids, output_hidden_states=True)
        return out.hidden_states[layer + 1][0].float().cpu().numpy()
    return f


def sae_encoder(sae, device="cpu"):
    import torch

    @torch.no_grad()
    def enc(R):
        x = torch.as_tensor(R, dtype=sae.W_dec.dtype, device=device)
        return sae.encode(x).float().cpu().numpy()
    return enc


def hook_layer(sae):
    name = getattr(sae.cfg, "metadata", None) and getattr(sae.cfg.metadata, "hook_name", None)
    name = name or getattr(sae.cfg, "hook_name", "")
    parts = [p for p in str(name).split(".") if p.isdigit()]
    if not parts:
        raise ValueError(f"cannot read the layer from hook name {name!r}")
    return int(parts[0])


def from_hf(ft_path, base_path, sae_release, sae_id, labels_path=None, bank_path=None, max_new=None,
            device="cuda", dtype="bfloat16", chat=True):
    """Build the T3 tool on Kaggle: both models, the Gemma Scope SAE and a label file."""
    import torch
    from sae_lens import SAE
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dt = getattr(torch, dtype)
    tok = AutoTokenizer.from_pretrained(base_path)
    ft = AutoModelForCausalLM.from_pretrained(ft_path, torch_dtype=dt).to(device).eval()
    base = AutoModelForCausalLM.from_pretrained(base_path, torch_dtype=dt).to(device).eval()
    sae = SAE.from_pretrained(sae_release, sae_id, device=device)
    sae = sae[0] if isinstance(sae, tuple) else sae
    layer = hook_layer(sae)
    labels = json.loads(Path(labels_path).read_text()) if labels_path else None
    return WhiteBoxTool(hf_resid(ft, tok, layer, chat, device), hf_resid(base, tok, layer, chat, device),
                        sae_encoder(sae, device), labels, PromptBank(bank_path, max_new))
