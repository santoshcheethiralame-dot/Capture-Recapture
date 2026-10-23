"""E09-R010: background-feature blocklist for the T3 Gemma Scope tool (Kaggle GPU).

    python analysis/e09/background_blocklist.py --out results/E09/E09-R010 \
        --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json --record

The rule, fixed on 2026-10-23 before this run and before any E09 organism
exists (E09 §2, T3; LOG of that date):
- prompts: the 100 neutral prompts in ``analysis/e09/background_prompts.txt``;
- model: Gemma-2-2B-it, the shared base of every organism, chat format,
  user tokens only (the tool's rule since E09-R009);
- a feature is blocklisted if it is in the top k = 10 (by max activation
  over the user's tokens) on more than 50% of those prompts;
- the blocklist hides features from the "top active features" list only.
  The "most changed vs base" list is not filtered: a feature changed on
  every prompt of an organism may be the implant itself.

Writes ``blocklist.json`` (the file ``gemma_scope.from_hf(blocklist_path=...)``
reads) and ``summary.json``. Also reported, descriptive only (not a
criterion, and not used to set anything): the top-features specificity on
the 20 check prompts of E09-R003/R009 with and without the blocklist.
"""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from crsafety import manifest  # noqa: E402
from crsafety.tools import gemma_scope as gs  # noqa: E402

K, CUTOFF = 10, 0.5
PROMPT_FILE = Path(__file__).resolve().parent / "background_prompts.txt"


def load_prompts(path=PROMPT_FILE):
    return [ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip() and not ln.startswith("#")]


def main():
    from gemma_scope_check import PROMPTS as CHECK_PROMPTS, RELEASE, SAE_ID, specificity

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--it", default="google/gemma-2-2b-it")
    ap.add_argument("--labels", required=True)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--record", action="store_true", help="write the manifest under results/E09/E09-R010")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    import torch
    from sae_lens import SAE
    from transformers import AutoModelForCausalLM, AutoTokenizer

    prompts = load_prompts()
    assert len(prompts) == 100 and not set(prompts) & set(CHECK_PROMPTS)
    cfg = dict(release=RELEASE, sae_id=SAE_ID, it=a.it, device=a.device, dtype=a.dtype, k=K, cutoff=CUTOFF,
               n_prompts=len(prompts), tokens="user",
               prompt_file_sha256=hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest())
    m = manifest.start("E09-R010", "E09", " ".join(sys.argv), cfg, seeds={}, inputs=[a.labels, PROMPT_FILE],
                       packages=("numpy", "torch", "transformers", "sae-lens", "crsafety")) if a.record else None
    t0 = time.perf_counter()

    tok = AutoTokenizer.from_pretrained(a.it)
    it = AutoModelForCausalLM.from_pretrained(a.it, torch_dtype=getattr(torch, a.dtype),
                                              attn_implementation="eager").to(a.device).eval()
    sae = SAE.from_pretrained(RELEASE, SAE_ID, device=a.device)
    sae = sae[0] if isinstance(sae, tuple) else sae
    layer = gs.hook_layer(sae)
    enc = gs.sae_encoder(sae, a.device)
    labels = json.loads(Path(a.labels).read_text())
    resid = gs.hf_resid(it, tok, layer, chat=True, device=a.device, user_only=True)

    block, counts = gs.background_blocklist(resid, enc, prompts, k=K, cutoff=CUTOFF)
    order = np.argsort(-counts)[:30]
    bl = dict(features=block, k=K, cutoff=CUTOFF, n_prompts=len(prompts), model=a.it, sae=f"{RELEASE}/{SAE_ID}",
              tokens="user", prompt_file="analysis/e09/background_prompts.txt",
              prompt_file_sha256=cfg["prompt_file_sha256"],
              detail=[dict(feature=f, top10_share=round(int(counts[f]) / len(prompts), 2),
                           label=labels.get(str(f), "(unlabelled)")) for f in block])
    (out / "blocklist.json").write_text(json.dumps(bl, indent=2) + "\n")

    # Descriptive only: the 20 check prompts, -it vs itself (top-features list).
    resp = {}
    for name, b in (("without", None), ("with", block)):
        tool = gs.WhiteBoxTool(resid, resid, enc, labels, gs.PromptBank(), skip_first=False, mode="user", blocklist=b)
        resp[name] = specificity([tool(p) for p in CHECK_PROMPTS])["top_features"]
    res = dict(config=cfg, gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
               n_blocklisted=len(block), blocklist=bl["detail"],
               top30_by_share=[[int(f), round(int(counts[f]) / len(prompts), 2)] for f in order],
               check_prompts_top_features_descriptive=resp,
               gpu_hours=round((time.perf_counter() - t0) / 3600, 3))
    (out / "summary.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "config"}, indent=2))
    if m:
        m["model_ids"] = [a.it, f"{RELEASE}/{SAE_ID}"]
        m["cost"]["gpu_hours"] = res["gpu_hours"]
        manifest.finish(m, outputs=["blocklist.json", "summary.json"])


if __name__ == "__main__":
    main()
