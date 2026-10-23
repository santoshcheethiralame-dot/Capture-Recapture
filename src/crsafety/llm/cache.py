"""LLM call cache (PROTOCOLS §6).

Key: sha256 of the canonical JSON of (model identity, full message list,
decoding parameters, seed). One file per generation at
``<dir>/<key[:2]>/<key>.json``. Writes go to one directory; reads also look
in read-only directories, so a cache backed up as a Kaggle dataset can be
attached under /kaggle/input and extended in /kaggle/working.

The cache is what makes a run reproducible: vLLM's per-request seed does not
guarantee the same tokens when the batch around a request changes, so a
re-run reads the recorded generation instead of regenerating it.
"""

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from .models import ROOT

DEFAULT_DIR = ROOT / "cache" / "llm"


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def call_key(model, messages, params, seed):
    """``model`` is ``ModelSpec.identity()``; ``params`` the decoding parameters."""
    payload = dict(model=model, messages=messages, params=params, seed=seed)
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


class CallCache:
    def __init__(self, write_dir=None, read_dirs=()):
        env = os.environ.get("CRSAFETY_LLM_CACHE")
        self.write_dir = Path(write_dir or env or DEFAULT_DIR)
        extra = os.environ.get("CRSAFETY_LLM_CACHE_READ", "")
        self.read_dirs = [Path(d) for d in (*read_dirs, *filter(None, extra.split(os.pathsep)))]
        self.hits = self.misses = 0

    def _path(self, root, key):
        return Path(root) / key[:2] / f"{key}.json"

    def get(self, key):
        for root in (self.write_dir, *self.read_dirs):
            p = self._path(root, key)
            if p.exists():
                self.hits += 1
                return json.loads(p.read_text())
        self.misses += 1
        return None

    def put(self, key, request, response):
        p = self._path(self.write_dir, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = dict(key=key, request=request, response=response,
                   created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        fd, tmp = tempfile.mkstemp(dir=p.parent, suffix=".tmp")
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(rec, ensure_ascii=False))
        os.replace(tmp, p)  # atomic: a cut session never leaves half a file
        return rec

    def __len__(self):
        return sum(1 for _ in self.write_dir.glob("*/*.json")) if self.write_dir.exists() else 0
