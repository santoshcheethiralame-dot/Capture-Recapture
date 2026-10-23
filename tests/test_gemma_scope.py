"""H7 white-box tool (crsafety.tools.gemma_scope) with fake and tiny real models."""

import numpy as np
import pytest

from crsafety.tools import gemma_scope as gs


def fake_tool(bank=None, shift=None):
    rng = np.random.default_rng(0)
    d, m = 8, 20
    E = rng.normal(size=(d, m))
    shift = np.zeros(d) if shift is None else shift

    def resid(prompt, s=0.0):
        r = np.random.default_rng(abs(hash(prompt)) % 2**32)
        return r.normal(size=(len(prompt.split()) + 1, d)) + s

    return gs.WhiteBoxTool(lambda p: resid(p) + shift, resid, lambda R: np.maximum(R @ E, 0),
                           labels={3: "deception", "5": "flattery"}, bank=bank)


def test_top_and_diff():
    shift = np.zeros(8)
    shift[0] = 3.0
    t = fake_tool(shift=shift)
    resp = t("tell me about the weather today", k=5)
    acts = [r["activation"] for r in resp["top_features"]]
    assert acts == sorted(acts, reverse=True) and len(acts) <= 5 and all(a > 0 for a in acts)
    ch = resp["most_changed_vs_base"]
    assert len(ch) == 5 and all(abs(c["change"]) > 0 for c in ch)
    assert all(np.isclose(c["change"], c["audited"] - c["base"], atol=2e-4) for c in ch)
    txt = gs.WhiteBoxTool.render(resp)
    assert "Top active features" in txt and "most changed" in txt
    # identical models: nothing changes
    same = fake_tool()("tell me about the weather today")
    assert same["most_changed_vs_base"] == []


def test_labels_and_unlabelled():
    t = fake_tool()
    rows = t.top_features("a b c d e f g h", k=20)
    lab = {r["feature"]: r["label"] for r in rows}
    if 3 in lab:
        assert lab[3] == "deception"
    assert any(v == "(unlabelled)" for v in lab.values())


def test_bank_cache_and_budget(tmp_path):
    bank = gs.PromptBank(tmp_path / "bank.npz", max_new=2)
    t = fake_tool(bank=bank)
    t.top_features("one two")          # ft: 1 new
    t.top_features("one two")          # cached
    t.diff_features("one two")         # base: 2 new
    with pytest.raises(gs.BudgetExceeded):
        t.top_features("three four")
    bank.save()
    again = gs.PromptBank(tmp_path / "bank.npz", max_new=0)
    t2 = fake_tool(bank=again)
    assert t2.diff_features("one two") == t.diff_features("one two")


def test_hf_resid_on_tiny_model():
    torch = pytest.importorskip("torch")
    tr = pytest.importorskip("transformers")
    cfg = tr.GPT2Config(n_layer=2, n_embd=16, n_head=2, vocab_size=50, n_positions=32)
    torch.manual_seed(0)
    model = tr.GPT2LMHeadModel(cfg).eval()

    class Tok:
        def __call__(self, text, return_tensors=None, add_special_tokens=True):
            return {"input_ids": torch.tensor([[1 + (ord(c) % 40) for c in text[:20]]])}

    f = gs.hf_resid(model, Tok(), layer=0)
    R = f("hello")
    assert R.shape == (5, 16)
    E = np.random.default_rng(1).normal(size=(16, 12))
    tool = gs.WhiteBoxTool(f, gs.hf_resid(model, Tok(), layer=1), lambda X: np.maximum(X @ E, 0))
    resp = tool("hello world")
    assert resp["top_features"] and resp["most_changed_vs_base"]


def test_hook_layer():
    class C:
        hook_name = "blocks.12.hook_resid_post"
        metadata = None

    class S:
        cfg = C()

    assert gs.hook_layer(S()) == 12


def test_hf_resid_chat_adds_no_second_bos():
    torch = pytest.importorskip("torch")
    tr = pytest.importorskip("transformers")
    cfg = tr.GPT2Config(n_layer=1, n_embd=8, n_head=2, vocab_size=50, n_positions=64)
    model = tr.GPT2LMHeadModel(cfg).eval()

    class ChatTok:
        """Gemma-like: the template starts with <bos> (id 2) and so does tokenizing."""
        def apply_chat_template(self, msgs, tokenize=False, add_generation_prompt=True):
            return "<bos>" + msgs[0]["content"]

        def __call__(self, text, return_tensors=None, add_special_tokens=True):
            body = text[5:] if text.startswith("<bos>") else text
            ids = ([2] if add_special_tokens else []) + ([2] if text.startswith("<bos>") else [])
            return {"input_ids": torch.tensor([ids + [3 + (ord(c) % 40) for c in body]])}

    assert gs.hf_resid(model, ChatTok(), layer=0, chat=True)("hi").shape[0] == 3   # <bos> h i
    assert gs.hf_resid(model, ChatTok(), layer=0, chat=False)("hi").shape[0] == 3  # <bos> h i
