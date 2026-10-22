"""Run manifests (docs/PROTOCOLS.md §5).

    m = start("E01-R001", "E01", command, config, seeds={...})
    ...
    finish(m, outputs=[...])

``start`` writes ``results/<EXP>/<run_id>/manifest.json`` at once, so a
crashed run still leaves a record; ``finish`` completes it. Confirmatory runs
refuse to start from a dirty working tree.
"""

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return ""


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def git_state(ignore=("notebook/", "results/")):
    """(sha, dirty, sha256 of the diff). Changes under ``ignore`` do not count:
    registering a run edits notebook/runs.csv, and the run writes results/."""
    sha = _git("rev-parse", "--short", "HEAD").strip()
    status = [l for l in _git("status", "--porcelain").splitlines()
              if not any(l[3:].startswith(p) for p in ignore)]
    diff = _git("diff", "HEAD", "--", ".", *[f":(exclude){p}" for p in ignore])
    return sha, bool(status), (sha256_bytes(diff.encode()) if status else None)


def _versions(packages):
    out = {}
    for p in packages:
        try:
            out[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            out[p] = None
    return out


def path_for(run_id):
    exp = run_id.split("-")[0]
    return ROOT / "results" / exp / run_id / "manifest.json"


def start(run_id, experiment, command, config, seeds, confirmatory=False, prereg=None,
          inputs=(), packages=("numpy", "scipy", "crsafety")):
    sha, dirty, diff = git_state()
    if confirmatory and dirty:
        sys.exit(f"{run_id} is confirmatory: refusing to start from a dirty working tree")
    cfg = json.dumps(config, sort_keys=True, default=str)
    lock = ROOT / "requirements.lock"
    m = dict(
        run_id=run_id, experiment=experiment, prereg=prereg, confirmatory=confirmatory,
        git_sha=sha, git_dirty=dirty, diff_sha256=diff, command=command,
        config=config, config_sha256=sha256_bytes(cfg.encode()),
        env_lock_sha256=sha256_file(lock) if lock.exists() else None,
        python_version=platform.python_version(), package_versions=_versions(packages),
        hardware=dict(machine=platform.machine(), cpus=os.cpu_count(), system=platform.system()),
        seeds=seeds, inputs=[dict(path=str(p), sha256=sha256_file(p)) for p in inputs],
        model_ids=[], started_utc=_now(), finished_utc=None, status="running", outputs=[],
        cost=dict(gpu_hours=0.0, api_usd=0.0),
    )
    p = path_for(run_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(m, indent=2, default=str) + "\n")
    return m


def finish(m, outputs=(), status="succeeded", **extra):
    m.update(finished_utc=_now(), status=status, outputs=[str(o) for o in outputs], **extra)
    path_for(m["run_id"]).write_text(json.dumps(m, indent=2, default=str) + "\n")
    return m
