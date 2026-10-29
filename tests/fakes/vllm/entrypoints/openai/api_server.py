"""Stand-in for vLLM's OpenAI server, for CPU tests of crsafety.llm (no model).

Answers the H3 serving-check prompts correctly, follows a BANANA system
prompt, answers E10 attacker prompts with a reversed (even seed) or
plain (odd seed) code, and is deterministic given (messages, seed). ``--fail-load`` exits
at once (a model that does not load); ``--nan`` returns a NaN logprob.
"""

import argparse
import hashlib
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ANSWERS = {"17 + 25": "42", "capital of france": "Paris", "backwards": "tac", "days are in a week": "7",
           "blue and yellow": "green", "gracias": "thank you", "9 or 4": "9", "lazy": "dog",
           "code word": "PELICAN"}


def reply(messages, seed):
    last = messages[-1]["content"]
    m = re.search(r"secret code is (\S+)", messages[0]["content"])
    if m:  # an E10 attacker prompt (crsafety.redteam): reversed code, or the plain code on odd seeds
        code = m.group(1)[::-1] if seed % 2 == 0 else m.group(1)
        return f"Strategy: reverse it\n<message>{code}</message>"
    for k, v in ANSWERS.items():
        if k in last.lower():
            text = v
            break
    else:
        h = hashlib.sha256(json.dumps([messages, seed]).encode()).hexdigest()[:8]
        text = f"Reply {h} to: {last[:30]}"
    if any(m["role"] == "system" and "BANANA" in m["content"] for m in messages):
        text += " BANANA"
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, required=True)
    ap.add_argument("--served-model-name", required=True)
    ap.add_argument("--fail-load", action="store_true")
    ap.add_argument("--nan", action="store_true")
    a, _ = ap.parse_known_args()
    if a.fail_load:
        raise SystemExit("fake: model does not fit")

    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _send(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            self._send(200, {"data": [{"id": a.served_model_name}]})

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if body["model"] != a.served_model_name:
                return self._send(404, {"error": "unknown model"})
            text = reply(body["messages"], body.get("seed"))
            ch = {"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
            if body.get("logprobs"):
                lp = float("nan") if a.nan else -0.1
                ch["logprobs"] = {"content": [{"token": t, "logprob": lp} for t in text.split()]}
            n_in = sum(len(m["content"].split()) for m in body["messages"])
            self._send(200, {"choices": [ch], "usage": {"prompt_tokens": n_in,
                                                        "completion_tokens": len(text.split())}})

    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
