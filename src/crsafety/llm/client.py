"""Cached chat client for an OpenAI-compatible server (vLLM; H3).

    spec = models.resolve("qwen2.5-7b")
    llm = Client(spec, "http://localhost:8001/v1")
    r = llm.chat([{"role": "user", "content": "hi"}], seed=7, temperature=0.7, max_tokens=256)
    r["text"], r["cached"]
    rs = llm.chat_many([dict(messages=m, seed=s) for m, s in jobs], workers=32)
    llm.usage   # calls, cache hits, prompt/completion tokens, server seconds (for the manifest)

Every call goes through the cache (PROTOCOLS §6), so a cut session resumes
without regenerating anything. Throughput comes from vLLM's continuous
batching: ``chat_many`` keeps ``workers`` requests in flight.

An E09 organism served as a LoRA adapter is addressed with
``adapter=(name, sha256 of the adapter weights)``; the sha goes into the
cache key.
"""

import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from .cache import CallCache, call_key

DEFAULTS = dict(temperature=0.7, top_p=1.0, max_tokens=512)
PARAMS = ("temperature", "top_p", "max_tokens", "stop", "logprobs", "extra_body")


class ServerError(RuntimeError):
    pass


class Client:
    def __init__(self, spec, base_url, cache=None, adapter=None, timeout=600, retries=4,
                 require_pinned=False):
        if require_pinned and not spec.pinned:
            raise ValueError(f"{spec.name} is not pinned (confirmatory runs need configs/llm/pins.json)")
        self.spec, self.base_url = spec, base_url.rstrip("/")
        self.cache = cache if cache is not None else CallCache()
        self.adapter, self.timeout, self.retries = adapter, timeout, retries
        self.served_name = adapter[0] if adapter else spec.name
        self._lock = threading.Lock()
        self.usage = dict(calls=0, cache_hits=0, prompt_tokens=0, completion_tokens=0,
                          server_seconds=0.0)

    def identity(self):
        ident = self.spec.identity()
        if self.adapter:
            ident["adapter"] = dict(name=self.adapter[0], sha256=self.adapter[1])
        return ident

    def _params(self, kw):
        unknown = set(kw) - set(PARAMS)
        if unknown:
            raise TypeError(f"unknown decoding parameters {sorted(unknown)}")
        return {**DEFAULTS, **{k: v for k, v in kw.items() if v is not None}}

    def chat(self, messages, seed, **kw):
        if seed is None:
            raise ValueError("every call needs a seed (PROTOCOLS §4)")
        params = self._params(kw)
        key = call_key(self.identity(), messages, params, seed)
        hit = self.cache.get(key)
        with self._lock:
            self.usage["calls"] += 1
        if hit is not None:
            with self._lock:
                self.usage["cache_hits"] += 1
            return {**hit["response"], "cached": True, "key": key}
        t0 = time.perf_counter()
        resp = self._post(messages, params, seed)
        secs = time.perf_counter() - t0
        out = _parse(resp, params)
        with self._lock:
            self.usage["prompt_tokens"] += out["usage"]["prompt_tokens"]
            self.usage["completion_tokens"] += out["usage"]["completion_tokens"]
            self.usage["server_seconds"] += secs
        request = dict(model=self.identity(), messages=messages, params=params, seed=seed)
        self.cache.put(key, request, out)
        return {**out, "cached": False, "key": key}

    def chat_many(self, jobs, workers=32):
        """``jobs``: dicts of ``chat`` keyword arguments. Results keep the order of ``jobs``."""
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return list(ex.map(lambda j: self.chat(**j), jobs))

    def _post(self, messages, params, seed):
        body = dict(model=self.served_name, messages=messages, seed=seed,
                    **{k: v for k, v in params.items() if k not in ("logprobs", "extra_body")})
        if params.get("logprobs"):
            body["logprobs"] = True
        body.update(params.get("extra_body") or {})
        data = json.dumps(body).encode()
        err = None
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(f"{self.base_url}/chat/completions", data=data,
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read())
            except urllib.error.HTTPError as e:
                err = ServerError(f"HTTP {e.code}: {e.read()[:500]!r}")
                if e.code < 500:
                    raise err from e  # a bad request does not get better on retry
            except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
                err = ServerError(f"{type(e).__name__}: {e}")
            if attempt < self.retries:
                time.sleep(min(2 ** attempt, 30))
        raise err


def _parse(resp, params):
    ch = resp["choices"][0]
    u = resp.get("usage") or {}
    out = dict(text=ch["message"].get("content") or "", finish_reason=ch.get("finish_reason"),
               usage=dict(prompt_tokens=int(u.get("prompt_tokens", 0)),
                          completion_tokens=int(u.get("completion_tokens", 0))))
    if params.get("logprobs"):
        lp = [t["logprob"] for t in ((ch.get("logprobs") or {}).get("content") or [])]
        out["logprobs"] = lp
    return out


def wait_ready(base_url, timeout=900, poll=1, proc=None):
    """Block until the server answers ``GET /models``; raise if ``proc`` exits first."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        if proc is not None and proc.poll() is not None:
            raise ServerError(f"server exited with code {proc.returncode} before becoming ready")
        try:
            with urllib.request.urlopen(f"{base_url.rstrip('/')}/models", timeout=10) as r:
                if r.status == 200:
                    return time.time() - t0
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            pass
        time.sleep(poll)
    raise ServerError(f"server at {base_url} not ready after {timeout} s")
