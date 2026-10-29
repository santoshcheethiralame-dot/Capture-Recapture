# E10-R002 Kaggle cells (copy-paste)

The same cells as `kaggle/e10_r002.ipynb`. Paste each block into its own code cell, in order.

Settings: Accelerator **GPU T4 x2**, Internet **on**, secret **HF_TOKEN** (Add-ons -> Secrets; the same token as E08-R010 to R013).
Optional, to resume a cut session: attach the previous version's `E10-R002-cache` output as a dataset (cell 5 reads it).

Run with **Save Version -> Save & Run All (Commit)**: an interactive session's `/kaggle/working` is deleted when it ends.
About 1-1.5 session hours: Qwen (14 runs) on GPU 0; Llama, then Granite (1 run each) on GPU 1.
Cell 6 is an optional 5-attempt smoke test (about 10 min); cell 7 is the run; cell 8 packs results and cache for download.
See `docs/KAGGLE-RUNBOOK.md` row K10 and `analysis/e10/attack.py`.

```python
# 1. Hugging Face token
import os
from kaggle_secrets import UserSecretsClient
os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
```

```python
# 2. Code
!git clone -q https://github.com/santoshcheethiralame-dot/MissingMass /kaggle/working/MissingMass
%cd /kaggle/working/MissingMass
!git log --oneline -1
```

```python
# 3. Install (about 5 min). vLLM brings its own torch (2.10, CUDA 12.8); version pinned in configs/llm/models.json.
!pip install -q "vllm==0.19.1" bitsandbytes
!pip install -q -e . --no-deps
import vllm, torch; print("vllm", vllm.__version__, "torch", torch.__version__, "cuda", torch.version.cuda)
```

```python
# 4. GPUs
!nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv
```

```python
# 5. Call cache: new generations go to /kaggle/working/cache/llm; an attached earlier cache is read, not rewritten
import glob
os.environ["CRSAFETY_LLM_CACHE"] = "/kaggle/working/cache/llm"
earlier = [d for d in glob.glob("/kaggle/input/*/cache/llm") + glob.glob("/kaggle/input/*/llm")]
os.environ["CRSAFETY_LLM_CACHE_READ"] = ":".join(earlier)
print("reading earlier caches:", earlier or "none")
```

```python
# 6. Optional smoke test (about 10 min): 5 attempts per run, not a result, written outside results/.
#    Check that most attempts are parsed (unparsed near 0) and refusals are 0. Its calls are cached and
#    become the first 5 attempts of cell 7, so nothing is wasted.
!python analysis/e10/attack.py --run E10-R002 --config configs/e10/r002.json --out /kaggle/working/smoke --budget 5
import json; s = json.load(open("/kaggle/working/smoke/summary.json"))
print(json.dumps({a: {k: o[k] for k in ("attempts", "success", "blocked", "no_leak", "unparsed", "refusals")}
                  for a, o in s["outcomes"].items()}, indent=1))
```

```python
# 7. E10-R002: 16 runs x 200 attempts on the pilot monitor. Prints one line per finished run; resumes if re-run.
!python analysis/e10/attack.py --run E10-R002 --config configs/e10/r002.json --record
```

```python
# 8. Pack for download (Output panel): E10-R002.zip goes into results/E10/E10-R002/; keep E10-R002-cache.zip
#    (or make this version's output a dataset) so a later session can replay every call.
!cd results/E10 && zip -qr /kaggle/working/E10-R002.zip E10-R002 && ls -la /kaggle/working/E10-R002.zip
!cd /kaggle/working && zip -qr E10-R002-cache.zip cache && ls -la E10-R002-cache.zip
!python -c "import json; s=json.load(open('results/E10/E10-R002/summary.json')); print(s['proposed'], s['missing_runs'], s['session_hours'])"
```
