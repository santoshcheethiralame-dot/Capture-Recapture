# Kaggle LLM stack (H3)

Serving for E08, E09 and E10 on Kaggle's free 2 × T4: one vLLM
OpenAI-compatible server per model, a cached client, and pinned models
(Q-D14). Code in `src/crsafety/llm/`, models in `configs/llm/`.

## Layout on 2 × T4

| GPU | Serves | Example |
|---|---|---|
| 0 | target or organism | `mistral-7b` (E08), `gemma2-2b-it` + LoRA organisms (E09) |
| 1 | auditor or attacker | `qwen2.5-7b`; L3 runs the families one after another |

A T4 has 15 GB usable and no bf16. A 7–9B model in fp16 is about 15 GB,
so two fp16 models do not fit at once: 7–9B models run 4-bit (AWQ where an
official or Hugging Face-staff build exists, otherwise bitsandbytes 4-bit
quantised at load from the official weights). The judge runs after the
audits, on its own. Gemma 2 can overflow in fp16; each Gemma candidate has
a float32 fallback.

## Pins

`configs/llm/models.json` lists each logical model with candidate builds in
order of preference. The serving check (E08-R008,
`analysis/e08/serving_check.py`) tries them on a T4 and pins the first that
passes: Hugging Face commit sha, quantisation, dtype and vLLM version, in
`configs/llm/pins.json`. Confirmatory scripts use
`models.resolve(name, require_pinned=True)`, so an unpinned or changed model
fails loudly. Changing a pin after the freeze is a deviation.

vLLM is pinned at 0.19.1, the newest release built on CUDA 12.8 (the CUDA
line in Kaggle's image). vLLM ≥ 0.20 needs CUDA 13 and an NVIDIA driver
≥ 580; the serving check records the driver it saw.

## Call cache (PROTOCOLS §6)

Every call is cached by sha256 of (model identity incl. revision,
quantisation and dtype; the full message list; decoding parameters; seed),
one JSON file per generation. vLLM's per-request seed does not give the same
tokens when the batch around a request changes, so the cache, not the seed,
is the record of a run.

- `CRSAFETY_LLM_CACHE`: where new generations are written. On Kaggle use
  `/kaggle/working/cache/llm`, and save it as a Kaggle dataset at the end of
  each session.
- `CRSAFETY_LLM_CACHE_READ`: earlier sessions' caches, read-only
  (`/kaggle/input/<dataset>/llm`; several joined with `:`).

A cut session then resumes without regenerating anything.

## Using it

```python
from crsafety.llm import CallCache, models
from crsafety.llm.serve import Server

with Server(models.resolve("mistral-7b", require_pinned=True), gpu=0, port=8000) as tgt, \
     Server(models.resolve("qwen2.5-7b", require_pinned=True), gpu=1, port=8001) as aud:
    cache = CallCache()
    t, a = tgt.client(cache), aud.client(cache)
    rs = a.chat_many([dict(messages=m, seed=s, temperature=0.7, max_tokens=256) for m, s in jobs], workers=32)
    usage = a.usage   # calls, cache hits, tokens: goes in the manifest
```

`chat_many` keeps up to `workers` requests in flight, which is where the
throughput comes from (vLLM batches them). Run many audits concurrently
rather than one fast audit.

## The notebook

`kaggle/llm_serving.ipynb`: settings, setup cells, the serving check, and a
zip of the results to download. The serving check deletes each model's
weights after testing it, to stay inside Kaggle's disk.

## Things the scaffolds must handle

- Gemma 2's chat template has no system role (S5 records this). Put
  auditor and attacker instructions in the first user turn, the same way
  for every family, so the scaffold is identical across E08 levels.
- Context windows differ: Gemma 2 has 8,192 tokens, OLMo 2 4,096, the
  rest 12–16k as configured. A 20-turn audit has to fit the smallest
  auditor window used in the comparison.
