"""H3 LLM stack: registry and pins, call cache, cached client, server launcher, serving check.

Runs on CPU against tests/fakes/vllm (a stand-in OpenAI server, no model)."""

import importlib.util
import json
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from crsafety.llm import CallCache, Client, NotPinned, ServerError, call_key, models
from crsafety.llm.serve import Server, vllm_command

ROOT = Path(__file__).resolve().parents[1]
FAKES = ROOT / "tests" / "fakes"


@pytest.fixture
def fake_vllm(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", str(FAKES))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def spec(name="m", extra=(), revision=None, pinned=False, **kw):
    base = dict(name=name, family="qwen", hf_id="org/m", quantization="awq", dtype="half",
                max_model_len=256, revision=revision, extra_args=tuple(extra), pinned=pinned)
    return models.ModelSpec(**{**base, **kw})


MSG = [{"role": "user", "content": "What is 17 + 25? Reply with the number only."}]


# --- registry and pins -------------------------------------------------------

def test_registry_loads_and_groups_cover_models():
    reg = models.load_registry()
    grouped = {n for g in reg["groups"].values() for n in g}
    assert grouped == set(reg["models"])


def test_registry_respects_e08_family_rules():
    """E08 prereg: the target family is never an auditor; the judge family is neither."""
    reg = models.load_registry()["models"]
    fam = lambda role: {m["family"] for m in reg.values() if role in m["roles"]}  # noqa: E731
    assert fam("target") == {"mistral"}
    assert not fam("target") & fam("auditor")
    assert not fam("judge") & (fam("auditor") | fam("target"))
    l3 = {m["family"] for m in reg.values() if "E08 L3" in m["levels"]}
    assert l3 == {"qwen", "llama", "gemma"}


def test_registry_rejects_bf16(tmp_path):
    reg = json.loads(models.REGISTRY.read_text())
    reg["models"]["qwen2.5-7b"]["candidates"][0]["dtype"] = "bfloat16"
    p = tmp_path / "r.json"
    p.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="T4"):
        models.load_registry(p)


def test_resolve_unpinned_pinned_and_mismatch():
    s = models.resolve("qwen2.5-7b", pins={})
    assert (s.candidate, s.pinned, s.revision) == (0, False, None)
    with pytest.raises(NotPinned):
        models.resolve("qwen2.5-7b", require_pinned=True, pins={})
    reg = models.load_registry()
    c1 = reg["models"]["qwen2.5-7b"]["candidates"][1]["hf_id"]
    p = {"qwen2.5-7b": dict(candidate=1, hf_id=c1, revision="abc", vllm_version="9.9")}
    s = models.resolve("qwen2.5-7b", require_pinned=True, pins=p)
    assert (s.candidate, s.pinned, s.revision, s.vllm_version, s.hf_id) == (1, True, "abc", "9.9", c1)
    p["qwen2.5-7b"]["hf_id"] = "someone/else"
    with pytest.raises(ValueError, match="pin says"):
        models.resolve("qwen2.5-7b", pins=p)
    with pytest.raises(KeyError):
        models.resolve("gpt-5", pins={})


# --- cache ---------------------------------------------------------------------

def test_call_key_stable_and_sensitive():
    ident = spec().identity()
    k = call_key(ident, MSG, dict(temperature=0.7, max_tokens=5), 1)
    assert k == call_key(dict(reversed(list(ident.items()))), MSG, dict(max_tokens=5, temperature=0.7), 1)
    assert k != call_key(ident, MSG, dict(temperature=0.7, max_tokens=5), 2)
    assert k != call_key(spec(revision="r").identity(), MSG, dict(temperature=0.7, max_tokens=5), 1)
    assert k != call_key(spec(dtype="float32").identity(), MSG, dict(temperature=0.7, max_tokens=5), 1)
    assert k != call_key(ident, MSG + MSG, dict(temperature=0.7, max_tokens=5), 1)


def test_cache_layers_and_atomic_writes(tmp_path):
    old, new = tmp_path / "old", tmp_path / "new"
    CallCache(old).put("ab" * 32, {"q": 1}, {"text": "from backup"})
    c = CallCache(new, read_dirs=[old])
    assert c.get("ab" * 32)["response"]["text"] == "from backup"
    assert c.get("cd" * 32) is None and (c.hits, c.misses) == (1, 1)
    c.put("ef" * 32, {}, {"text": "x"})
    assert (new / "ef" / ("ef" * 32 + ".json")).exists() and not (old / "ef").exists()
    assert not list(new.rglob("*.tmp")) and len(c) == 1


def test_cache_env(tmp_path, monkeypatch):
    monkeypatch.setenv("CRSAFETY_LLM_CACHE", str(tmp_path / "w"))
    monkeypatch.setenv("CRSAFETY_LLM_CACHE_READ", str(tmp_path / "r1"))
    c = CallCache()
    assert c.write_dir == tmp_path / "w" and c.read_dirs == [tmp_path / "r1"]


# --- server command ----------------------------------------------------------------

def test_vllm_command():
    cmd = vllm_command(spec(revision="abc", extra=("--enable-lora",)), 8001, python="py")
    assert cmd[:3] == ["py", "-m", "vllm.entrypoints.openai.api_server"]
    j = " ".join(cmd)
    for part in ("--model org/m", "--served-model-name m", "--dtype half", "--revision abc",
                 "--tokenizer-revision abc", "--quantization awq", "--port 8001", "--max-model-len 256"):
        assert part in j
    assert cmd[-1] == "--enable-lora"
    bare = " ".join(vllm_command(spec(quantization=None), 8001, enforce_eager=True))
    assert "--quantization" not in bare and "--revision" not in bare and "--enforce-eager" in bare


def test_registry_commands_build():
    reg = models.load_registry()
    for n, m in reg["models"].items():
        for i in range(len(m["candidates"])):
            assert "--model" in vllm_command(models.candidate_spec(n, i, reg), 8000)


# --- client against the fake server ------------------------------------------------

def test_client_caches_counts_and_orders(fake_vllm, tmp_path):
    with Server(spec(), port=free_port(), log_dir=tmp_path) as srv:
        llm = srv.client(CallCache(tmp_path / "c"))
        r1 = llm.chat(MSG, seed=1, temperature=0.0, max_tokens=8)
        r2 = llm.chat(MSG, seed=1, temperature=0.0, max_tokens=8)
        assert r1["text"] == r2["text"] == "42" and not r1["cached"] and r2["cached"]
        assert llm.usage["calls"] == 2 and llm.usage["cache_hits"] == 1
        assert llm.usage["completion_tokens"] == 1
        jobs = [dict(messages=[{"role": "user", "content": f"q{i}"}], seed=i) for i in range(20)]
        rs = llm.chat_many(jobs, workers=8)
        assert [r["text"].split("to: ")[1] for r in rs] == [f"q{i}" for i in range(20)]
        # a fresh client on the same cache regenerates nothing
        again = Client(srv.spec, srv.base_url, cache=CallCache(tmp_path / "c")).chat_many(jobs)
        assert all(r["cached"] for r in again)
    assert srv.proc.poll() is not None


def test_client_rejects_bad_calls(tmp_path):
    llm = Client(spec(), "http://127.0.0.1:9", cache=CallCache(tmp_path))
    with pytest.raises(ValueError, match="seed"):
        llm.chat(MSG, seed=None)
    with pytest.raises(TypeError, match="unknown"):
        llm.chat(MSG, seed=1, temprature=0.5)
    with pytest.raises(ValueError, match="not pinned"):
        Client(spec(), "http://x", require_pinned=True)


def test_adapter_in_key(tmp_path):
    a = Client(spec(), "http://x", cache=CallCache(tmp_path), adapter=("org-1", "f" * 64))
    b = Client(spec(), "http://x", cache=CallCache(tmp_path))
    assert a.served_name == "org-1" and a.identity() != b.identity()


def test_server_that_fails_to_load(fake_vllm, tmp_path):
    srv = Server(spec(extra=("--fail-load",)), port=free_port(), log_dir=tmp_path).start()
    with pytest.raises(ServerError, match="exited"):
        srv.wait(timeout=60)
    assert "does not fit" in srv.log_tail()


def test_retries_5xx_not_4xx(tmp_path):
    calls = {"n": 0}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            calls["n"] += 1
            code = 503 if calls["n"] <= 2 else (400 if "bad" in self.path else 200)
            b = json.dumps({"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
                            "usage": {"prompt_tokens": 1, "completion_tokens": 1}}).encode()
            self.send_response(code)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_address[1]}"
    import crsafety.llm.client as cl
    sleep = cl.time.sleep
    cl.time.sleep = lambda s: None
    try:
        assert Client(spec(), url, cache=CallCache(tmp_path / "a")).chat(MSG, seed=1)["text"] == "ok"
        assert calls["n"] == 3
        calls["n"] = 2
        with pytest.raises(ServerError, match="400"):
            Client(spec(), url + "/bad", cache=CallCache(tmp_path / "b")).chat(MSG, seed=1)
        assert calls["n"] == 3  # the 400 was not retried
    finally:
        cl.time.sleep = sleep
        httpd.shutdown()


# --- serving check end to end ---------------------------------------------------------

def load_check():
    p = ROOT / "analysis" / "e08" / "serving_check.py"
    sp = importlib.util.spec_from_file_location("serving_check", p)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod


def test_serving_check_end_to_end(fake_vllm, tmp_path, monkeypatch):
    cand = lambda hf, *extra: dict(hf_id=hf, quantization="awq", dtype="half",  # noqa: E731
                                   max_model_len=256, extra_args=list(extra))
    reg = dict(vllm_version="x", groups={}, models={
        "aud": dict(family="qwen", roles=["auditor"], candidates=[cand("o/broken", "--fail-load"), cand("o/aud")]),
        "tgt": dict(family="mistral", roles=["target"], candidates=[cand("o/tgt")]),
        "nan": dict(family="gemma", roles=["auditor"], candidates=[cand("o/nan", "--nan")]),
    })
    chk = load_check()
    monkeypatch.setattr(chk.models, "load_registry", lambda *a, **k: reg)
    monkeypatch.setattr(chk, "resolve_revision", lambda hf: "sha-" + hf.split("/")[1])
    monkeypatch.setattr(chk, "gpu_memory_mib", lambda gpu: None)
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["serving_check.py", "--out", str(out), "--models", "aud,tgt,nan",
                                      "--pair", "tgt,aud", "--port", str(free_port())])
    chk.main()
    pins = json.loads((out / "pins.json").read_text())["pins"]
    assert set(pins) == {"aud", "tgt"}
    assert pins["aud"]["candidate"] == 1 and pins["aud"]["revision"] == "sha-aud"
    aud = json.loads((out / "aud.json").read_text())
    assert not aud["tried"][0]["pass_"] and "exited" in aud["tried"][0]["S1_load"]["error"]
    t = aud["tried"][1]
    assert t["S2_numerics"]["n_right"] == 8 and t["S3_cache"]["pass"] and t["S4_context"]["recalled"]
    nan = json.loads((out / "nan.json").read_text())
    assert "pin" not in nan and not nan["tried"][0]["S2_numerics"]["all_logprobs_finite"]
    tgt = json.loads((out / "tgt.json").read_text())
    assert tgt["tried"][0]["S5_system"]["followed"]
    s = json.loads((out / "summary.json").read_text())
    assert s["S8_pair"]["pass_"] and not s["all_pinned"]
    # resumable: a second run skips the checked models and keeps the pins
    chk.main()
    assert json.loads((out / "pins.json").read_text())["pins"] == pins
