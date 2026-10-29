"""OpenAI-compatible chat server on Hugging Face transformers (H3), for models vLLM cannot serve on a T4.

Gemma 2 is the case (E08-R011): vLLM refuses fp16 for it, and in float32 none
of vLLM 0.19.1's attention backends that run on sm75 both fit the T4's shared
memory and support Gemma 2's attention logit soft cap. transformers' eager
attention does, and a 2B model in float32 fits a T4 (about 10.5 GB). The E09
organisms (merged checkpoints) are served the same way, one server per
organism.

    python -m crsafety.llm.hf_server --model google/gemma-2-2b-it --revision <sha> \
        --served-model-name gemma2-2b-it --dtype float32 --max-model-len 8192 --port 8100

It answers ``GET /v1/models`` and ``POST /v1/chat/completions`` with the
fields ``crsafety.llm.client`` reads (text, finish_reason, usage, logprobs),
so the client, the call cache and the scaffolds do not change. Requests that
arrive together and share decoding parameters are generated as one batch
(up to ``--max-batch``), which is where the throughput comes from. Sampling
is seeded per batch from the first request's seed; as with vLLM, a seeded
request does not reproduce inside a different batch, so the cache, not the
seed, is the record. Temperature 0 is greedy and needs no seed.
"""

import argparse
import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DTYPES = {"float32": "float32", "half": "float16", "float16": "float16"}
BATCH_WAIT_S = 0.02


class BadRequest(ValueError):
    pass


class Engine:
    def __init__(self, model, revision=None, dtype="float32", max_model_len=8192, device=None,
                 attn_implementation="eager"):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(model, revision=revision)
        self.tok.padding_side = "left"
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model, revision=revision, dtype=getattr(torch, DTYPES[dtype]),
            attn_implementation=attn_implementation).to(self.device).eval()
        self.max_model_len = max_model_len

    def prompt_ids(self, messages):
        try:
            text = self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        except Exception as e:  # the template refuses e.g. a system role (Gemma 2): a bad request, as in vLLM
            raise BadRequest(f"chat template: {e}") from e
        ids = self.tok(text, add_special_tokens=False)["input_ids"]
        return ids

    def generate(self, prompts, temperature, top_p, max_tokens, stop, logprobs, seed):
        """``prompts``: lists of token ids. Returns one dict per prompt."""
        torch = self.torch
        for ids in prompts:
            if len(ids) + max_tokens > self.max_model_len:
                raise BadRequest(f"prompt of {len(ids)} tokens + max_tokens {max_tokens} "
                                 f"exceeds max_model_len {self.max_model_len}")
        width = max(map(len, prompts))
        pad = self.tok.pad_token_id
        input_ids = torch.tensor([[pad] * (width - len(p)) + p for p in prompts], device=self.device)
        mask = torch.tensor([[0] * (width - len(p)) + [1] * len(p) for p in prompts], device=self.device)
        sample = temperature > 0
        kw = dict(do_sample=sample, max_new_tokens=max_tokens, pad_token_id=pad,
                  return_dict_in_generate=True, output_scores=bool(logprobs))
        if sample:
            kw.update(temperature=temperature, top_p=top_p)
            torch.manual_seed(seed if seed is not None else 0)
        else:
            kw.update(temperature=None, top_p=None, top_k=None)
        with torch.inference_mode():
            out = self.model.generate(input_ids=input_ids, attention_mask=mask, **kw)
        new = out.sequences[:, width:]
        lps = None
        if logprobs:
            # log-softmax of the raw logits, as vLLM reports them
            lps = torch.stack([torch.log_softmax(s.float(), dim=-1) for s in out.scores], dim=1)
            lps = lps.gather(-1, new.unsqueeze(-1)).squeeze(-1)
        eos = self.model.generation_config.eos_token_id
        eos = set(eos if isinstance(eos, (list, tuple)) else [eos])
        res = []
        for b in range(len(prompts)):
            toks = new[b].tolist()
            n, finish = len(toks), "length"
            for i, t in enumerate(toks):
                if t in eos or t == pad:
                    n, finish = i, "stop"
                    break
            text = self.tok.decode(toks[:n], skip_special_tokens=True)
            for s in stop or ():
                j = text.find(s)
                if j >= 0:
                    text, finish = text[:j], "stop"
            r = dict(text=text, finish_reason=finish, prompt_tokens=len(prompts[b]),
                     completion_tokens=n + (finish == "stop" and n < len(toks)))
            if logprobs:
                r["logprobs"] = [float(x) for x in lps[b, :n].tolist()]
            res.append(r)
        return res


class Batcher:
    """Collects requests for ``BATCH_WAIT_S`` and generates those with equal decoding parameters together."""

    def __init__(self, engine, max_batch=16):
        self.engine, self.max_batch = engine, max_batch
        self.q = queue.Queue()
        threading.Thread(target=self._loop, daemon=True).start()

    def submit(self, body):
        params = (float(body.get("temperature", 1.0)), float(body.get("top_p", 1.0)),
                  int(body.get("max_tokens") or 512), tuple(_stops(body.get("stop"))),
                  bool(body.get("logprobs")))
        ids = self.engine.prompt_ids(body["messages"])
        done = threading.Event()
        item = dict(params=params, ids=ids, seed=body.get("seed"), done=done)
        self.q.put(item)
        done.wait()
        if "error" in item:
            raise item["error"]
        return item["result"]

    def _loop(self):
        while True:
            items = [self.q.get()]
            t0 = time.monotonic()
            while len(items) < self.max_batch * 4 and time.monotonic() - t0 < BATCH_WAIT_S:
                try:
                    items.append(self.q.get(timeout=BATCH_WAIT_S))
                except queue.Empty:
                    break
            groups = {}
            for it in items:
                groups.setdefault(it["params"], []).append(it)
            for params, group in groups.items():
                for k in range(0, len(group), self.max_batch):
                    chunk = group[k:k + self.max_batch]
                    try:
                        out = self.engine.generate([it["ids"] for it in chunk], *params,
                                                   seed=chunk[0]["seed"])
                        for it, r in zip(chunk, out):
                            it["result"] = r
                    except Exception as e:  # noqa: BLE001 - reported to every request in the chunk
                        for it in chunk:
                            it["error"] = e
                    for it in chunk:
                        it["done"].set()


def _stops(stop):
    if stop is None:
        return []
    return [stop] if isinstance(stop, str) else list(stop)


def response(name, r):
    choice = dict(index=0, message=dict(role="assistant", content=r["text"]), finish_reason=r["finish_reason"])
    if "logprobs" in r:
        choice["logprobs"] = dict(content=[dict(logprob=x) for x in r["logprobs"]])
    return dict(id=f"chatcmpl-{time.time_ns()}", object="chat.completion", created=int(time.time()),
                model=name, choices=[choice],
                usage=dict(prompt_tokens=r["prompt_tokens"], completion_tokens=r["completion_tokens"],
                           total_tokens=r["prompt_tokens"] + r["completion_tokens"]))


def make_handler(name, batcher):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, obj):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):  # noqa: N802
            if self.path.rstrip("/") == "/v1/models":
                self._send(200, dict(object="list", data=[dict(id=name, object="model")]))
            else:
                self._send(404, dict(error="not found"))

        def do_POST(self):  # noqa: N802
            if self.path.rstrip("/") != "/v1/chat/completions":
                return self._send(404, dict(error="not found"))
            try:
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
                if body.get("model") != name:
                    raise BadRequest(f"model {body.get('model')!r} is not served here ({name!r})")
                self._send(200, response(name, batcher.submit(body)))
            except BadRequest as e:
                self._send(400, dict(error=dict(message=str(e), type="BadRequestError")))
            except Exception as e:  # noqa: BLE001
                self._send(500, dict(error=dict(message=f"{type(e).__name__}: {e}", type="InternalServerError")))

        def log_message(self, *args):
            pass

    return Handler


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="Hugging Face id or a local (merged) checkpoint dir")
    ap.add_argument("--revision")
    ap.add_argument("--served-model-name", required=True)
    ap.add_argument("--dtype", default="float32", choices=sorted(DTYPES))
    ap.add_argument("--max-model-len", type=int, default=8192)
    ap.add_argument("--max-batch", type=int, default=16)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args(argv)
    t0 = time.time()
    engine = Engine(a.model, a.revision, a.dtype, a.max_model_len)
    print(f"loaded {a.model}@{a.revision} ({a.dtype}) on {engine.device} in {time.time() - t0:.0f} s", flush=True)
    srv = ThreadingHTTPServer((a.host, a.port), make_handler(a.served_model_name, Batcher(engine, a.max_batch)))
    print(f"serving {a.served_model_name} at http://{a.host}:{a.port}/v1", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
