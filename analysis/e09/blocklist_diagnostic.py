"""E09-R011: does the T3 background blocklist hide part of an implant? (Kaggle GPU)

    python analysis/e09/blocklist_diagnostic.py --out results/E09/E09-R011 \
        --labels results/E09/E09-R003/labels/gemma-2-2b__12-gemmascope-res-16k.json \
        --blocklist results/E09/E09-R010/blocklist.json \
        --organism animal_welfare=<merged organism dir> ... \
        --trigger-prompts <dir of <organism>.txt, one prompt per line> --record

Pre-specified on 2026-10-23 (E09 §2, analysis plan; Santosh's review of
D-014, suggestion 1), after E09-R010 and before any organism exists.
Descriptive, not a criterion. Run once after E09-R002, on all 16 organisms
(14 + 2 pilot), each against Gemma-2-2B-it on its own trigger prompts (the
implant-verification prompts). It reads no audit transcript or report, so it
reveals no E09 outcome.

For each organism and each blocklisted feature, over its trigger prompts:
- ``hidden``: prompts where the feature would be in the organism's top-10
  active features without the blocklist (so the blocklist removed it);
- ``in_most_changed``: prompts where it is in the most-changed top 10
  (|organism - base|), which is not filtered, so the auditor sees it there;
- ``median_change_rank``: its median rank by |change| (1 = most changed).
``flag`` is ``in_most_changed`` on more than half of the prompts: the
implant moves a background feature. The response is fixed in advance: the
blocklist is not changed for E09-R007 whatever this shows (a flagged feature
is still visible in the most-changed list); flagged organisms are reported
with the T3 results as a limitation.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

K = 10


def _top(v, k, nonzero=True):
    idx = np.argsort(-v)[:k]
    return {int(i) for i in idx if not nonzero or v[i] > 0}


def diagnose(acts, blocklist, k=K):
    """``acts``: list of (organism, base) max-activation vectors, one pair per
    trigger prompt (the tool's per-prompt maxima). Returns one row per
    blocklisted feature."""
    n = len(acts)
    rows = []
    for f in sorted(int(f) for f in blocklist):
        hidden = changed = 0
        ranks = []
        for a, b in acts:
            a, b = np.asarray(a, float), np.asarray(b, float)
            d = np.abs(a - b)
            hidden += f in _top(a, k)
            changed += f in _top(d, k)
            ranks.append(int((d > d[f]).sum()) + 1)
        rows.append(dict(feature=f, n_prompts=n, hidden=hidden, in_most_changed=changed,
                         median_change_rank=float(np.median(ranks)) if ranks else None,
                         flag=changed > n / 2))
    return rows


def load_prompts(path):
    return [ln.strip() for ln in Path(path).read_text().splitlines() if ln.strip() and not ln.startswith("#")]


def main():
    from gemma_scope_check import RELEASE, SAE_ID

    from crsafety import manifest
    from crsafety.tools import gemma_scope as gs

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default="google/gemma-2-2b-it")
    ap.add_argument("--labels", required=True)
    ap.add_argument("--blocklist", required=True)
    ap.add_argument("--organism", action="append", required=True, metavar="NAME=PATH")
    ap.add_argument("--trigger-prompts", required=True, help="directory with <NAME>.txt per organism")
    ap.add_argument("--run-id", default="E09-R011")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--record", action="store_true", help="write the manifest under results/E09/<run id>")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    orgs = dict(o.split("=", 1) for o in a.organism)
    prompts = {name: load_prompts(Path(a.trigger_prompts) / f"{name}.txt") for name in orgs}

    import torch
    from sae_lens import SAE
    from transformers import AutoModelForCausalLM, AutoTokenizer

    cfg = dict(release=RELEASE, sae_id=SAE_ID, base=a.base, k=K, organisms=orgs, tokens="user",
               n_prompts={n: len(p) for n, p in prompts.items()})
    m = manifest.start(a.run_id, "E09", " ".join(sys.argv), cfg, seeds={},
                       inputs=[a.labels, a.blocklist] + [str(Path(a.trigger_prompts) / f"{n}.txt") for n in orgs],
                       packages=("numpy", "torch", "transformers", "sae-lens", "crsafety")) if a.record else None
    t0 = time.perf_counter()

    kw = dict(torch_dtype=getattr(torch, a.dtype), attn_implementation="eager")
    tok = AutoTokenizer.from_pretrained(a.base)
    base = AutoModelForCausalLM.from_pretrained(a.base, **kw).to(a.device).eval()
    sae = SAE.from_pretrained(RELEASE, SAE_ID, device=a.device)
    sae = sae[0] if isinstance(sae, tuple) else sae
    layer, enc = gs.hook_layer(sae), gs.sae_encoder(sae, a.device)
    labels = json.loads(Path(a.labels).read_text())
    block = json.loads(Path(a.blocklist).read_text())["features"]
    resid_base = gs.hf_resid(base, tok, layer, chat=True, device=a.device, user_only=True)

    res = {}
    for name, path in orgs.items():
        ft = AutoModelForCausalLM.from_pretrained(path, **kw).to(a.device).eval()
        tool = gs.WhiteBoxTool(gs.hf_resid(ft, tok, layer, chat=True, device=a.device, user_only=True), resid_base,
                               enc, labels, skip_first=False, mode="user", blocklist=block)
        acts = [(tool._max_acts("ft", p), tool._max_acts("base", p)) for p in prompts[name]]
        rows = diagnose(acts, block)
        for r in rows:
            r["label"] = labels.get(str(r["feature"]), "(unlabelled)")
        res[name] = dict(rows=rows, flagged=[r["feature"] for r in rows if r["flag"]])
        del ft, tool
        torch.cuda.empty_cache()

    summary = dict(config=cfg, blocklist=block, organisms=res,
                   flagged={n: r["flagged"] for n, r in res.items() if r["flagged"]},
                   gpu_hours=round((time.perf_counter() - t0) / 3600, 3))
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["flagged"], indent=2))
    if m:
        m["model_ids"] = [a.base, f"{RELEASE}/{SAE_ID}"] + list(orgs.values())
        m["cost"]["gpu_hours"] = summary["gpu_hours"]
        manifest.finish(m, outputs=["summary.json"])


if __name__ == "__main__":
    main()
