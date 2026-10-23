"""Start and stop vLLM OpenAI-compatible servers on Kaggle GPUs (H3).

    srv = Server(models.resolve("qwen2.5-7b"), gpu=1, port=8001, log_dir="/kaggle/working/logs")
    srv.start(); srv.wait()          # or: with Server(...) as srv:
    llm = srv.client(cache)
    srv.stop()

Default layout on 2 x T4: the target (or organism) on GPU 0, the auditor or
attacker on GPU 1, each a 4-bit 7-9B model with its own server. vLLM is run
as ``python -m vllm.entrypoints.openai.api_server`` so the version on the
path is the one pinned in configs/llm/models.json.

    python -m crsafety.llm.serve start qwen2.5-7b --gpu 1 --port 8001   # stays in the foreground
    python -m crsafety.llm.serve cmd qwen2.5-7b                          # print the command only
"""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from . import models
from .client import Client, wait_ready


def vllm_command(spec, port, seed=0, enforce_eager=False, python=sys.executable):
    cmd = [python, "-m", "vllm.entrypoints.openai.api_server",
           "--model", spec.hf_id, "--served-model-name", spec.name,
           "--dtype", spec.dtype, "--max-model-len", str(spec.max_model_len),
           "--gpu-memory-utilization", str(spec.gpu_memory_utilization),
           "--host", "127.0.0.1", "--port", str(port), "--seed", str(seed)]
    if spec.revision:
        cmd += ["--revision", spec.revision, "--tokenizer-revision", spec.revision]
    if spec.quantization:
        cmd += ["--quantization", spec.quantization]
    if enforce_eager:
        cmd.append("--enforce-eager")
    return cmd + list(spec.extra_args)


class Server:
    def __init__(self, spec, gpu=0, port=8000, log_dir=".", enforce_eager=False, env=None):
        self.spec, self.gpu, self.port = spec, gpu, port
        self.cmd = vllm_command(spec, port, enforce_eager=enforce_eager)
        self.log_path = Path(log_dir) / f"vllm-{spec.name}-gpu{gpu}.log"
        self.env = {**os.environ, "CUDA_VISIBLE_DEVICES": str(gpu), **(env or {})}
        self.proc = None
        self.base_url = f"http://127.0.0.1:{port}/v1"

    def start(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_path, "w")
        # own process group, so stop() also ends vLLM's worker processes
        self.proc = subprocess.Popen(self.cmd, env=self.env, stdout=self._log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
        return self

    def wait(self, timeout=1200):
        try:
            return wait_ready(self.base_url, timeout=timeout, proc=self.proc)
        except Exception:
            self.stop()
            raise

    def client(self, cache=None, **kw):
        return Client(self.spec, self.base_url, cache=cache, **kw)

    def log_tail(self, n=40):
        try:
            return "".join(self.log_path.read_text(errors="replace").splitlines(True)[-n:])
        except OSError:
            return ""

    def stop(self, timeout=60):
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGKILL)
                self.proc.wait()
            except ProcessLookupError:
                pass
        if getattr(self, "_log", None):
            self._log.close()

    def __enter__(self):
        self.start()
        self.wait()
        return self

    def __exit__(self, *exc):
        self.stop()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("start", "cmd"))
    ap.add_argument("model")
    ap.add_argument("--gpu", type=int, default=0)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--candidate", type=int, help="registry candidate (default: the pin, else 0)")
    ap.add_argument("--enforce-eager", action="store_true")
    ap.add_argument("--log-dir", default=".")
    a = ap.parse_args(argv)
    spec = (models.candidate_spec(a.model, a.candidate) if a.candidate is not None
            else models.resolve(a.model))
    if a.action == "cmd":
        print(" ".join(vllm_command(spec, a.port, enforce_eager=a.enforce_eager)))
        return
    srv = Server(spec, a.gpu, a.port, a.log_dir, a.enforce_eager).start()
    print(f"{spec.name} ({spec.hf_id}) starting on GPU {a.gpu}, port {a.port}; log {srv.log_path}")
    print(f"ready after {srv.wait():.0f} s at {srv.base_url}")
    try:
        srv.proc.wait()
    except KeyboardInterrupt:
        srv.stop()


if __name__ == "__main__":
    main()
