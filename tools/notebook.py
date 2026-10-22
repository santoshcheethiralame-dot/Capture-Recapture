#!/usr/bin/env python3
"""Lab-notebook helper. Standard library only.

The run registry `notebook/runs.csv` is the source of truth for every run.
This tool appends and updates runs, renders the run tables inside the
experiment pages, locks pre-registrations, and checks the notebook.

    python tools/notebook.py new E02 --owner Santosh --title "Zoo, BatchTopK, oracle histories" --config configs/e02.yaml
    python tools/notebook.py set E02-R001 status=succeeded summary="coverage err 0.02"
    python tools/notebook.py render
    python tools/notebook.py freeze E02
    python tools/notebook.py check
"""

import argparse
import csv
import datetime as dt
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NB = ROOT / "notebook"
RUNS = NB / "runs.csv"
LOCKS = NB / "prereg-locks.csv"
EXP_DIR = NB / "experiments"

FIELDS = [
    "run_id", "experiment", "title", "owner", "status", "started", "finished",
    "commit", "config", "command", "outputs", "summary", "notes",
]
LOCK_FIELDS = ["experiment", "sha256", "commit", "date", "note"]
STATUSES = {"planned", "running", "succeeded", "failed", "aborted", "superseded"}
DONE = {"succeeded", "failed", "aborted", "superseded"}
REQUIRED_HEADINGS = [
    "## 1. Question", "## 2. Pre-registration", "## 3. Contingencies",
    "## 4. Runs", "## 5. Results", "## 6. Deviations",
]
PREREG_RE = re.compile(r"<!-- prereg:start -->(.*?)<!-- prereg:end -->", re.S)


def today():
    return dt.date.today().isoformat()


def git_commit():
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out + ("+dirty" if dirty else "")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def read_csv(path, fields):
    if not path.exists():
        return []
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    return [{k: r.get(k, "") or "" for k in fields} for r in rows]


def write_csv(path, fields, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def experiment_pages():
    """Map experiment ID (E00, E01, ...) to its markdown page."""
    pages = {}
    for p in sorted(EXP_DIR.glob("E*.md")):
        m = re.match(r"(E\d{2})", p.name)
        if m:
            pages[m.group(1)] = p
    return pages


def norm_exp(exp):
    m = re.fullmatch(r"[Ee]?(\d{1,2})", exp)
    if not m:
        sys.exit(f"bad experiment id: {exp}")
    return f"E{int(m.group(1)):02d}"


def prereg_hash(page):
    m = PREREG_RE.search(page.read_text())
    if not m:
        return None
    text = "\n".join(line.rstrip() for line in m.group(1).strip().splitlines())
    return hashlib.sha256(text.encode()).hexdigest()


def cmd_new(args):
    exp = norm_exp(args.experiment)
    if exp not in experiment_pages():
        sys.exit(f"no page for {exp} in {EXP_DIR}")
    rows = read_csv(RUNS, FIELDS)
    n = 1 + max([int(r["run_id"].split("-R")[1]) for r in rows if r["experiment"] == exp] or [0])
    row = dict.fromkeys(FIELDS, "")
    row.update(
        run_id=f"{exp}-R{n:03d}", experiment=exp, title=args.title,
        owner=args.owner, status=args.status, config=args.config or "", command=args.command or "",
        notes=args.notes or "", commit=git_commit(),
    )
    if args.status != "planned":
        row["started"] = today()
    rows.append(row)
    write_csv(RUNS, FIELDS, rows)
    print(row["run_id"])


def cmd_set(args):
    rows = read_csv(RUNS, FIELDS)
    match = [r for r in rows if r["run_id"] == args.run_id]
    if not match:
        sys.exit(f"unknown run {args.run_id}")
    row = match[0]
    for kv in args.fields:
        key, _, value = kv.partition("=")
        if key not in FIELDS or key in ("run_id", "experiment"):
            sys.exit(f"cannot set field {key!r}")
        if key == "status" and value not in STATUSES:
            sys.exit(f"status must be one of {sorted(STATUSES)}")
        if key == "notes" and row["notes"] and not args.replace:
            value = row["notes"] + " | " + value
        row[key] = value
    if row["status"] == "running" and not row["started"]:
        row["started"] = today()
        row["commit"] = git_commit()
    if row["status"] in DONE and not row["finished"]:
        row["finished"] = today()
    write_csv(RUNS, FIELDS, rows)
    print(f"{row['run_id']}: {row['status']}")


def run_table(rows):
    if not rows:
        return "_No runs yet._"
    head = "| Run | Title | Owner | Status | Started | Finished | Commit | Summary |\n|---|---|---|---|---|---|---|---|"
    lines = [
        f"| {r['run_id']} | {r['title']} | {r['owner']} | {r['status']} | {r['started']} | "
        f"{r['finished']} | {r['commit']} | {r['summary']} |"
        for r in rows
    ]
    return "\n".join([head] + lines)


def replace_block(text, tag, body):
    pat = re.compile(rf"(<!-- {tag}:start -->)(.*?)(<!-- {tag}:end -->)", re.S)
    if not pat.search(text):
        return text, False
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(3)}", text), True


def cmd_render(_args):
    rows = read_csv(RUNS, FIELDS)
    pages = experiment_pages()
    for exp, page in pages.items():
        text = page.read_text()
        text, ok = replace_block(text, "runs", run_table([r for r in rows if r["experiment"] == exp]))
        if ok:
            page.write_text(text)
    # Status counts in the registry.
    reg = NB / "REGISTRY.md"
    if reg.exists():
        counts = []
        for exp in pages:
            rs = [r for r in rows if r["experiment"] == exp]
            c = {s: sum(r["status"] == s for r in rs) for s in ("planned", "running", "succeeded", "failed")}
            counts.append(
                f"| {exp} | {len(rs)} | {c['planned']} | {c['running']} | {c['succeeded']} | {c['failed']} |"
            )
        body = "| Exp | Runs | Planned | Running | Succeeded | Failed |\n|---|---|---|---|---|---|\n" + "\n".join(counts)
        text, _ = replace_block(reg.read_text(), "counts", body)
        reg.write_text(text)
    print(f"rendered {len(pages)} experiment pages")


def cmd_freeze(args):
    exp = norm_exp(args.experiment)
    page = experiment_pages().get(exp)
    if page is None:
        sys.exit(f"no page for {exp}")
    h = prereg_hash(page)
    if h is None:
        sys.exit(f"{page.name} has no prereg block")
    locks = read_csv(LOCKS, LOCK_FIELDS)
    locks.append(dict(experiment=exp, sha256=h, commit=git_commit(), date=today(), note=args.note or ""))
    write_csv(LOCKS, LOCK_FIELDS, locks)
    print(f"locked {exp} pre-registration: {h[:12]}")


def cmd_check(_args):
    errors, warnings = [], []
    pages = experiment_pages()
    rows = read_csv(RUNS, FIELDS)
    ids = [r["run_id"] for r in rows]
    for dup in {i for i in ids if ids.count(i) > 1}:
        errors.append(f"duplicate run id {dup}")
    for r in rows:
        if r["status"] not in STATUSES:
            errors.append(f"{r['run_id']}: bad status {r['status']!r}")
        if r["experiment"] not in pages:
            errors.append(f"{r['run_id']}: no page for {r['experiment']}")
        if not r["owner"]:
            warnings.append(f"{r['run_id']}: no owner")
        if r["status"] in ("succeeded", "failed") and not r["summary"]:
            warnings.append(f"{r['run_id']}: {r['status']} but no summary")
    for exp, page in pages.items():
        text = page.read_text()
        for h in REQUIRED_HEADINGS:
            if h not in text:
                errors.append(f"{page.name}: missing heading '{h}'")
        if "<!-- runs:start -->" not in text:
            errors.append(f"{page.name}: missing runs block")
    latest = {}
    for lock in read_csv(LOCKS, LOCK_FIELDS):
        latest[lock["experiment"]] = lock
    deviations = (NB / "DEVIATIONS.md").read_text() if (NB / "DEVIATIONS.md").exists() else ""
    for exp, lock in latest.items():
        page = pages.get(exp)
        if page is None:
            errors.append(f"lock for missing experiment {exp}")
            continue
        if prereg_hash(page) != lock["sha256"]:
            msg = f"{exp}: pre-registration changed since freeze on {lock['date']}"
            if re.search(rf"\b{exp}\b", deviations):
                warnings.append(msg + " (a deviation entry exists; re-freeze to record the new version)")
            else:
                errors.append(msg + " with no entry in notebook/DEVIATIONS.md")
    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"{len(pages)} experiments, {len(rows)} runs, {len(latest)} frozen; "
          f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(required=True)

    p = sub.add_parser("new", help="register a run")
    p.add_argument("experiment")
    p.add_argument("--title", required=True)
    p.add_argument("--owner", required=True, help="who runs it (e.g. Santosh, Kushal)")
    p.add_argument("--status", default="planned", choices=sorted(STATUSES))
    p.add_argument("--config")
    p.add_argument("--command")
    p.add_argument("--notes")
    p.set_defaults(func=cmd_new)

    p = sub.add_parser("set", help="update fields of a run (key=value ...)")
    p.add_argument("run_id")
    p.add_argument("fields", nargs="+")
    p.add_argument("--replace", action="store_true", help="overwrite notes instead of appending")
    p.set_defaults(func=cmd_set)

    p = sub.add_parser("render", help="refresh run tables in the experiment pages and registry")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("freeze", help="lock an experiment's pre-registration block")
    p.add_argument("experiment")
    p.add_argument("--note")
    p.set_defaults(func=cmd_freeze)

    p = sub.add_parser("check", help="validate the notebook")
    p.set_defaults(func=cmd_check)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
