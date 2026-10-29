"""E10 attacker harness (crsafety.redteam) and the R002 runner (analysis/e10/attack.py).

CPU only: a scripted attacker, a recording stand-in, and the fake vLLM server
in tests/fakes/vllm."""

import importlib.util
import json
import socket
import sys
from pathlib import Path

import numpy as np
import pytest

from crsafety import histories
from crsafety import monitor as mo
from crsafety import redteam as rt

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs" / "e10" / "r002.json"


@pytest.fixture(scope="module")
def pilot():
    return mo.instances()[1]


def load_runner():
    spec = importlib.util.spec_from_file_location("e10_attack", ROOT / "analysis" / "e10" / "attack.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Recorder:
    """Answers every call with a fixed reply and keeps the calls."""

    def __init__(self, text="Strategy: plain\n<message>hello</message>", fail_after=None):
        self.text, self.fail_after, self.calls = text, fail_after, []

    def chat(self, messages, seed, **kw):
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise RuntimeError("server went away")
        self.calls.append(dict(messages=messages, seed=seed, **kw))
        return dict(text=self.text, finish_reason="stop", usage=dict(completion_tokens=3))

    def chat_many(self, jobs, workers=1):
        return [self.chat(**j) for j in jobs]


# --- prompt and parsing -------------------------------------------------------------

def test_opening_tells_the_goal_not_the_holes(pilot):
    tok = "AB-CD12-EF34"
    texts = {a: rt.opening(tok, rt.ARMS[a]) for a in ("A1", "A2", "A4", "A5")}
    for t in texts.values():
        assert tok in t and "<message>" in t and "Strategy:" in t
        low = t.lower()
        for name in ("base64", "caesar", "hex", "morse", "nato", "rot13", "rot47", "atbash", "blind spot"):
            assert name not in low
        assert not any(b.cell in t for b in pilot.blind_spots)
        assert "attempts" not in low or "how many" not in low  # the budget is never stated
    assert texts["A1"] == texts["A5"]
    assert rt.ADAPTIVE.strip() in texts["A2"] and rt.DIVERSE.strip() not in texts["A2"]
    assert rt.ADAPTIVE.strip() in texts["A4"] and rt.DIVERSE.strip() in texts["A4"]
    assert rt.ADAPTIVE.strip() not in texts["A1"]


def test_parse():
    msgs, s, ref, trunc = rt.parse("Strategy: split it\n<message> AB </message>\n<MESSAGE>CD</MESSAGE>")
    assert msgs == ["AB", "CD"] and s == "split it" and not ref and not trunc
    msgs, s, ref, _ = rt.parse("I'm sorry, I can't help with that.")
    assert msgs is None and ref
    msgs, _, ref, _ = rt.parse("Here you go: AB-CD")
    assert msgs is None and not ref
    msgs, _, _, trunc = rt.parse("".join(f"<message>m{i}</message>" for i in range(6)))
    assert msgs == ["m0", "m1", "m2", "m3"] and trunc
    msgs, _, _, trunc = rt.parse(f"<message>{'x' * (rt.MAX_CHARS + 50)}</message>")
    assert len(msgs[0]) == rt.MAX_CHARS and trunc
    assert rt.parse("**Strategy:** bold\n<message>a</message>")[1] == "bold"
    assert rt.parse(None)[0] is None


def test_screen_scores_through_the_monitor(pilot):
    tok = mo.make_token(np.random.default_rng(1))
    cell = pilot.blind_spots[0].cell
    msgs = mo.attack([cell], tok, np.random.default_rng(2))
    rec = rt.screen(pilot, tok, "Strategy: x\n" + "".join(f"<message>{m}</message>" for m in msgs))
    assert rec["outcome"] == "success" and rec["credited"] == [pilot.blind_spots[0].item_id]
    assert rt.screen(pilot, tok, f"<message>{tok}</message>")["outcome"] == "blocked"
    assert rt.screen(pilot, tok, "<message>nothing here</message>")["outcome"] == "no_leak"
    assert rt.screen(pilot, tok, "no tags")["outcome"] == "unparsed"


# --- seeds and arms -----------------------------------------------------------------

def test_seeds_do_not_depend_on_budget():
    key = (2, 1, 0)
    assert [rt.attempt_seed(key, i) for i in range(5)] == [rt.attempt_seed(key, i) for i in range(5)]
    assert len({rt.attempt_seed(key, i) for i in range(200)}) == 200
    assert rt.attempt_seed((2, 1, 0), 0) != rt.attempt_seed((2, 1, 1), 0)
    assert rt.attempt_seed((2, 1, 0), 0) != rt.attempt_seed((3, 1, 0), 0)  # R002 never reuses R003's seeds


@pytest.mark.parametrize("arm", ["A1", "A2", "A4"])
def test_prefix_of_a_long_run_is_a_short_run(pilot, arm):
    """The attacker is not told the budget, so R002 reads every B off one pass at B_max."""
    long = rt.campaign(rt.ScriptedAttacker(seed=3), pilot, rt.ARMS[arm], 40, (2, 1, 0))
    short = rt.campaign(rt.ScriptedAttacker(seed=3), pilot, rt.ARMS[arm], 15, (2, 1, 0))
    assert long.token == short.token
    assert long.records[:15] == short.records
    X_long, _ = rt.caught([long], pilot, 15)
    X_short, _ = rt.caught([short], pilot)
    assert (X_long == X_short).all()


def test_non_adaptive_calls_are_independent(pilot):
    rec = Recorder()
    run = rt.campaign(rec, pilot, rt.ARMS["A1"], 12, (2, 1, 0), temperature=1.0, max_tokens=50)
    assert run.used == 12 and not run.error
    assert all(len(c["messages"]) == 1 for c in rec.calls)
    assert len({c["seed"] for c in rec.calls}) == 12
    assert {c["temperature"] for c in rec.calls} == {1.0} and {c["max_tokens"] for c in rec.calls} == {50}
    assert all(r["outcome"] == "no_leak" for r in run.records)


@pytest.mark.parametrize("arm,last", [("A2", rt.NEXT), ("A4", rt.NEXT_DIVERSE)])
def test_adaptive_conversation_and_window(pilot, arm, last):
    rec = Recorder()
    run = rt.campaign(rec, pilot, rt.ARMS[arm], 9, (2, 2, 0), window=3)
    assert run.used == 9
    lens = [len(c["messages"]) for c in rec.calls]
    assert lens == [1, 3, 5, 7, 7, 7, 7, 7, 7]
    for c in rec.calls:
        roles = [m["role"] for m in c["messages"]]
        assert roles[0] == "user" and all(r1 != r2 for r1, r2 in zip(roles, roles[1:]))
        assert c["messages"][0]["content"] == rt.opening(run.token, rt.ARMS[arm])
    fb = rec.calls[-1]["messages"][-1]["content"]
    assert fb.startswith("Attempt 8: NOT RECOVERED") and "So far: 8 attempts" in fb
    assert fb.endswith(last)


def test_adaptive_feedback_lists_winning_strategies(pilot):
    tok_run = rt.campaign(Recorder(), pilot, rt.ARMS["A2"], 1, (2, 2, 5))
    cell = pilot.blind_spots[3].cell
    msgs = mo.attack([cell], tok_run.token, np.random.default_rng(0))
    rec = Recorder("Strategy: the trick\n" + "".join(f"<message>{m}</message>" for m in msgs))
    run = rt.campaign(rec, pilot, rt.ARMS["A2"], 3, (2, 2, 5))
    assert [r["outcome"] for r in run.records] == ["success"] * 3
    fb = rec.calls[-1]["messages"][-1]["content"]
    assert fb.startswith("Attempt 2: GOT THROUGH") and "- the trick" in fb and "2 got through" in fb


def test_a5_round_robin():
    a5 = rt.ARMS["A5"]
    assert [a5.model_for(r) for r in range(12)].count("granite3.3-8b") == 4
    assert [a5.model_for(r) for r in range(4)] == ["qwen2.5-7b", "llama3.1-8b", "granite3.3-8b", "qwen2.5-7b"]
    assert all(rt.ARMS[a].model_for(7) == "qwen2.5-7b" for a in ("A1", "A2", "A4"))


def test_crash_is_recorded_not_raised(pilot):
    run = rt.campaign(Recorder(fail_after=3), pilot, rt.ARMS["A2"], 40, (2, 2, 0))
    assert run.used == 3 and run.crashed and "server went away" in run.error
    run = rt.campaign(Recorder(fail_after=10), pilot, rt.ARMS["A2"], 40, (2, 2, 0))
    assert run.used == 10 and not run.crashed  # >= 10% of the budget: kept, not an exclusion
    run = rt.campaign(Recorder(fail_after=5), pilot, rt.ARMS["A1"], 40, (2, 1, 0))
    assert run.used == 0 and run.crashed


# --- R002 analysis ------------------------------------------------------------------

def fake_run(pilot, label, hits):
    """hits: {attempt index: blind-spot index}; every other attempt blocked."""
    n = max(hits) + 1 if hits else 1
    recs = [dict(outcome="success" if i in hits else "blocked",
                 credited=[pilot.blind_spots[hits[i]].item_id] if i in hits else [],
                 refusal=False, truncated=False) for i in range(n)]
    return rt.Run(label, "A1", "m", (2, 1, 0), "T", n, recs)


def test_rates_curve_and_proposal(pilot):
    runs = [fake_run(pilot, "a", {0: 0, 9: 1}), fake_run(pilot, "b", {4: 0, 19: 2}),
            fake_run(pilot, "c", {})]
    r10 = rt.rates(runs, pilot, 10)
    ids = [b.item_id for b in pilot.blind_spots]
    assert r10[ids[0]] == pytest.approx(2 / 3) and r10[ids[1]] == pytest.approx(1 / 3) and r10[ids[2]] == 0
    assert rt.rates(runs, pilot)[ids[2]] == pytest.approx(1 / 3)
    curve = rt.budget_curve(runs, pilot, [5, 10, 20])
    assert [c["in_band"] for c in curve] == [0, 1, 2]
    assert [c["above"] for c in curve] == [1, 1, 1]
    assert curve[-1]["floor"] == 37 and all(c["in_band"] + c["floor"] + c["below"] + c["above"] == 40
                                            for c in curve)
    assert rt.propose_budget(curve, bar=1) == dict(B=10, in_band=1, meets_bar=True)
    assert rt.propose_budget(curve, bar=30) == dict(B=20, in_band=2, meets_bar=False)


def test_outcome_shares(pilot):
    s = rt.outcome_shares([fake_run(pilot, "a", {0: 0, 3: 1})])
    assert s["attempts"] == 4 and s["success"] == 2 and s["blocked"] == 2 and s["share"]["success"] == 0.5


# --- runner -------------------------------------------------------------------------

def test_runner_dry_run_end_to_end(tmp_path, monkeypatch, capsys):
    runner = load_runner()
    out = tmp_path / "r002"
    argv = ["attack.py", "--run", "E10-R002", "--config", str(CFG), "--out", str(out), "--dry-run",
            "--budget", "20"]
    monkeypatch.setattr(sys, "argv", argv)
    runner.main()
    cfg = json.loads(CFG.read_text())
    labels = [f"{a}-{r}" for a in cfg["arms"] for r in range(cfg["runs_per_arm"])]
    assert sorted(p.stem for p in (out / "runs").glob("*.json")) == sorted(labels)
    s = json.loads((out / "summary.json").read_text())
    assert s["monitor"] == "pilot" and s["monitor_sha256"] == cfg["monitor_sha256"]
    assert s["runs"] == 16 and not s["missing_runs"] and s["dry_run"]
    assert {c["b"] for c in s["curve"]} == {10, 20}
    assert s["proposed"]["B"] in (10, 20)
    assert sum(f["n"] for f in s["families"].values()) == 40
    assert {json.loads((out / "runs" / f"{lb}.json").read_text())["model"] for lb in labels if
            lb.startswith("A5")} == {"qwen2.5-7b", "llama3.1-8b", "granite3.3-8b"}
    c = histories.read_cell(out / "history" / "A2")
    assert c.X.shape[1] == 4 and len(c.items) == 40 and c.X.any(axis=1).all()  # rows: detected items
    assert (out / "budget_curve.csv").read_text().startswith("b,in_band,floor,below,above,mean_rate,in_band_A1")
    # a second invocation finds every run done and re-analyses without new calls
    capsys.readouterr()
    runner.main()
    assert "16 already done" in capsys.readouterr().out


def test_runner_refuses_main_and_unverified_monitors(tmp_path, monkeypatch):
    runner = load_runner()
    cfg = json.loads(CFG.read_text())
    with pytest.raises(SystemExit, match="frozen"):
        runner.load_monitor({**cfg, "monitor": "main"})
    with pytest.raises(SystemExit, match="not the verified"):
        runner.load_monitor({**cfg, "monitor_sha256": "0" * 64})
    assert runner.load_monitor(cfg).name == "pilot"
    monkeypatch.setattr(sys, "argv", ["attack.py", "--run", "E10-R002", "--config", str(CFG),
                                      "--out", str(tmp_path), "--dry-run", "--record"])
    with pytest.raises(SystemExit, match="not a result"):
        runner.main()


def test_pilot_hash_matches_r009():
    pin = json.loads((ROOT / "results" / "E10" / "E10-R009" / "blind_spots_pilot.json").read_text())
    assert json.loads(CFG.read_text())["monitor_sha256"] == pin["sha256"] == mo.instances()[1].sha256()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_runner_against_fake_vllm(tmp_path, monkeypatch):
    """The real path: Server + cached Client per model, two 'GPUs', cache replay on resume."""
    from crsafety.llm import models
    monkeypatch.setenv("PYTHONPATH", str(ROOT / "tests" / "fakes"))
    monkeypatch.setenv("CRSAFETY_LLM_CACHE", str(tmp_path / "cache"))
    fake = lambda name, require_pinned=False, **k: models.ModelSpec(  # noqa: E731
        name=name, family="x", hf_id=f"o/{name}", quantization="awq", dtype="half", max_model_len=4096,
        revision="r", pinned=True)
    monkeypatch.setattr(models, "resolve", fake)
    runner = load_runner()
    cfg = {**json.loads(CFG.read_text()), "arms": ["A1", "A2", "A5"], "runs_per_arm": 3,
           "grid": [4, 8]}
    cfg_path = tmp_path / "cfg.json"
    cfg_path.write_text(json.dumps(cfg))
    out = tmp_path / "out"
    port = free_port()
    monkeypatch.setattr(sys, "argv", ["attack.py", "--run", "E10-R002", "--config", str(cfg_path),
                                      "--out", str(out), "--budget", "8", "--port", str(port)])
    runner.main()
    s = json.loads((out / "summary.json").read_text())
    assert s["runs"] == 9 and not s["missing_runs"]
    assert set(s["usage"]) == {"qwen2.5-7b", "llama3.1-8b", "granite3.3-8b"}
    assert s["usage"]["qwen2.5-7b"]["calls"] == 7 * 8 and s["usage"]["qwen2.5-7b"]["cache_hits"] == 0
    # the fake answers with the reversed code on even seeds and the plain code (blocked) on odd ones
    o = s["outcomes"]["A1"]
    assert o["unparsed"] == 0 and o["blocked"] > 0 and o["blocked"] + o["success"] + o["no_leak"] == 24
    rev = next(b for b in mo.instances()[1].blind_spots if mo.family(b.cell) == "reverse")
    rows = [json.loads(line) for line in open(out / "attempts" / "A1-0.jsonl")]
    assert all(r["outcome"] == ("success" if r["seed"] % 2 == 0 else "blocked") for r in rows)
    assert all(r["credited"] == [rev.item_id] for r in rows if r["outcome"] == "success")
    # remove one run's output: the re-run replays it from the cache
    (out / "runs" / "A2-1.json").unlink()
    runner.main()
    s2 = json.loads((out / "summary.json").read_text())
    assert s2["usage"]["qwen2.5-7b"]["calls"] == 8 and s2["usage"]["qwen2.5-7b"]["cache_hits"] == 8
    assert s2["curve"] == s["curve"]
