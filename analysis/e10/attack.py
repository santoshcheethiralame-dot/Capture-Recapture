"""E10 attacker runs on Kaggle 2 x T4 (Kushal). R002: difficulty pilot on the pilot monitor.

    python analysis/e10/attack.py --run E10-R002 --config configs/e10/r002.json --record
    python analysis/e10/attack.py --run E10-R002 --config configs/e10/r002.json \
        --out <scratchpad> --dry-run --budget 20          # CPU smoke test, scripted attacker, no manifest

Plan: for each arm in the config, ``runs_per_arm`` runs (``crsafety.redteam.campaign``),
run r of arm a seeded by ``SeedSequence(20261032, spawn_key=(<run number>, a, r))``.
A5 runs go round robin to Qwen, Llama and Granite. Each model gets one vLLM
server; models are served one after another on each GPU in ``--gpus``, two
at a time on 2 x T4. The monitor runs on CPU. Every call goes through the
call cache (``CRSAFETY_LLM_CACHE``), and finished runs are skipped on a
re-run, so a cut session resumes.

Outputs in ``--out`` (default results/E10/<run>):
- ``attempts/<arm>-<r>.jsonl``: every attempt in order (reply, parsed
  messages, verdict, credited blind spots, model seed, cache key);
- ``runs/<arm>-<r>.json``: run metadata (model, token, attempts used, crash flag);
- ``incomplete.jsonl``: every run that stopped short of its budget (server
  error, cut session), with its error. Such a run is retried on the next
  invocation and replays its finished calls from the cache. E10 §2's
  exclusion rule (< 10% of the budget used) is the ``crashed`` flag;
- ``budget_curve.csv``: for each b in ``grid``, blind spots whose per-run
  discovery rate pooled over all runs lies in ``band``, at the floor, below
  and above it, pooled and per arm;
- ``rates.csv``: each pilot blind spot's pooled rate at every b in the grid;
- ``history/<arm>/``: PROTOCOLS §10 cells at the proposed B (instrumented identity);
- ``summary.json``: proposed B (smallest b in the grid with >= ``bar`` blind
  spots in band, E10 §2 R002), per-family rates at that B, outcome shares
  (got through / blocked / not recovered / unparsed), refusals, crashed runs,
  tokens, session hours.

R002 measures the pilot monitor only. The script checks the pilot's sha256
against E10-R009 and refuses ``"monitor": "main"`` until E10 is frozen
(notebook/prereg-locks.csv), so no confirmatory blind spot is attacked
before v1.1.
"""

import argparse
import csv
import json
import os
import queue
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from crsafety import manifest  # noqa: E402
from crsafety import monitor as mo  # noqa: E402
from crsafety import redteam as rt  # noqa: E402

LOCKS = ROOT / "notebook" / "prereg-locks.csv"


def load_monitor(cfg):
    main, pilot = mo.instances(M=cfg.get("M", 40), tiers=cfg.get("tiers"), cap=cfg.get("cap", 4))
    if cfg["monitor"] == "pilot":
        mon = pilot
    elif cfg["monitor"] == "main":
        locked = LOCKS.exists() and any(r["experiment"] == "E10" for r in csv.DictReader(open(LOCKS)))
        if not locked:
            sys.exit("the main monitor is attacked only after E10 is frozen (v1.1); R002 uses the pilot")
        mon = main
    else:
        sys.exit(f"unknown monitor {cfg['monitor']!r}")
    want = cfg.get("monitor_sha256")
    if want and mon.sha256() != want:
        sys.exit(f"{cfg['monitor']} monitor sha256 {mon.sha256()} is not the verified {want}")
    return mon


def plan(cfg, run_number):
    out = []
    for a in cfg["arms"]:
        arm = rt.ARMS[a]
        for r in range(cfg["runs_per_arm"]):
            out.append(dict(label=f"{a}-{r}", arm=a, model=arm.model_for(r),
                            seed_key=(run_number, rt.ARM_INDEX[a], r)))
    return out


def save_run(out, run):
    (out / "attempts").mkdir(parents=True, exist_ok=True)
    (out / "runs").mkdir(parents=True, exist_ok=True)
    tmp = out / "attempts" / f"{run.label}.jsonl.tmp"
    with open(tmp, "w") as f:
        for rec in run.records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    os.replace(tmp, out / "attempts" / f"{run.label}.jsonl")
    (out / "runs" / f"{run.label}.json").write_text(json.dumps(run.meta(), indent=2) + "\n")


def load_run(out, label):
    p = out / "runs" / f"{label}.json"
    if not p.exists():
        return None
    meta = json.loads(p.read_text())
    if meta["used"] < meta["budget"]:
        return None  # retried (the cache replays what was generated); kept in incomplete.jsonl
    recs = [json.loads(line) for line in open(out / "attempts" / f"{label}.jsonl")]
    return rt.Run(meta["label"], meta["arm"], meta["model"], tuple(meta["seed_key"]), meta["token"],
                  meta["budget"], recs, meta.get("error", ""))


def run_model(client, mon, jobs, cfg, budget, out, log):
    def one(job):
        run = rt.campaign(client, mon, rt.ARMS[job["arm"]], budget, job["seed_key"], label=job["label"],
                          model=job["model"], window=cfg["window"], temperature=cfg["temperature"],
                          max_tokens=cfg["max_tokens"], workers=cfg["workers"])
        if run.used < budget:
            with open(out / "incomplete.jsonl", "a") as f:
                f.write(json.dumps(run.meta()) + "\n")
        save_run(out, run)
        log(f"{run.label} ({run.model}): {run.used}/{budget} attempts, "
            f"{sum(r['outcome'] == 'success' for r in run.records)} got through"
            + (f", INCOMPLETE{' (crashed: < 10% used)' if run.crashed else ''}: {run.error}"
               if run.used < budget else ""))
        return run
    with ThreadPoolExecutor(max_workers=max(1, len(jobs))) as ex:
        return list(ex.map(one, jobs))


def serve_and_run(todo, mon, cfg, budget, out, gpus, log, dry_run, port=8200):
    """One server per model; each GPU serves its queue of models in turn."""
    by_model = {}
    for j in todo:
        by_model.setdefault(j["model"], []).append(j)
    usage, specs = {}, {}
    if dry_run:
        for name, jobs in by_model.items():
            run_model(rt.ScriptedAttacker(seed=len(name), name=name), mon, jobs, cfg, budget, out, log)
        return usage, specs
    from crsafety.llm import CallCache, models
    from crsafety.llm.serve import Server
    q = queue.Queue()
    for name in sorted(by_model, key=lambda n: -len(by_model[n])):
        q.put(name)
    errors = []

    def worker(gpu):
        while True:
            try:
                name = q.get_nowait()
            except queue.Empty:
                return
            spec = models.resolve(name, require_pinned=True)
            specs[name] = spec
            srv = Server(spec, gpu=gpu, port=port + gpu, log_dir=out / "logs")
            try:
                t0 = time.perf_counter()
                srv.start()
                srv.wait()
                log(f"{name} up on GPU {gpu} after {time.perf_counter() - t0:.0f} s; "
                    f"{len(by_model[name])} runs")
                client = srv.client(CallCache())
                run_model(client, mon, by_model[name], cfg, budget, out, log)
                usage[name] = client.usage
            except Exception as e:  # noqa: BLE001
                errors.append(f"{name}: {type(e).__name__}: {e}"[:300])
                log(f"{name} FAILED: {errors[-1]}\n{srv.log_errors()}")
            finally:
                srv.stop()

    threads = [threading.Thread(target=worker, args=(g,)) for g in gpus]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        usage["errors"] = errors
    return usage, specs


def analyse(runs, mon, cfg, budget, out):
    grid = [b for b in cfg["grid"] if b <= budget] or [budget]
    band, bar = tuple(cfg["band"]), cfg["bar"]
    curve = rt.budget_curve(runs, mon, grid, band)
    per_arm = {a: rt.budget_curve([r for r in runs if r.arm == a], mon, grid, band) for a in cfg["arms"]}
    with open(out / "budget_curve.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["b", "in_band", "floor", "below", "above", "mean_rate"]
                   + [f"in_band_{a}" for a in cfg["arms"]])
        for k, c in enumerate(curve):
            w.writerow([c["b"], c["in_band"], c["floor"], c["below"], c["above"], round(c["mean_rate"], 4)]
                       + [per_arm[a][k]["in_band"] for a in cfg["arms"]])
    by_b = {b: rt.rates(runs, mon, b) for b in grid}
    with open(out / "rates.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item_id", "cell", "family", "tier"] + [f"b{b}" for b in grid])
        for bs in mon.blind_spots:
            w.writerow([bs.item_id, bs.cell, mo.family(bs.cell), bs.tier]
                       + [round(float(by_b[b][bs.item_id]), 4) for b in grid])
    prop = rt.propose_budget(curve, bar)
    at = by_b[prop["B"]]
    fams = {}
    for bs in mon.blind_spots:
        f = fams.setdefault(mo.family(bs.cell), dict(n=0, rates=[]))
        f["n"] += 1
        f["rates"].append(round(float(at[bs.item_id]), 4))
    lo, hi = band
    for f in fams.values():
        f["in_band"] = sum(lo <= r <= hi for r in f["rates"])
    tiers = {t: dict(n=sum(b.tier == t for b in mon.blind_spots),
                     mean_rate=round(float(np.mean([at[b.item_id] for b in mon.blind_spots if b.tier == t])), 4))
             for t in mo.TIERS}
    for a in cfg["arms"]:
        arm_runs = [r for r in runs if r.arm == a]
        meta = [dict(catcher=r.model, seed=int(rt.run_seed(r.seed_key).generate_state(1)[0]),
                     status="crashed_rerun" if r.crashed else "ok") for r in arm_runs]
        mo.write_history(out / "history" / a, a, mon,
                         [r.verdicts(prop["B"]) for r in arm_runs], run_meta=meta)
    return dict(proposed=prop, curve=curve, per_arm_in_band_at_B={a: next(c["in_band"] for c in per_arm[a]
                                                                            if c["b"] == prop["B"])
                                                                   for a in cfg["arms"]},
                families=fams, tiers=tiers)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="E10-R002")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out")
    ap.add_argument("--gpus", default="0,1")
    ap.add_argument("--port", type=int, default=8200, help="server on GPU g listens on port + g")
    ap.add_argument("--budget", type=int, help="override the config's budget (smoke tests only)")
    ap.add_argument("--dry-run", action="store_true", help="scripted attacker, no GPU, no manifest")
    ap.add_argument("--record", action="store_true", help="write results/E10/<run>/manifest.json")
    a = ap.parse_args()
    cfg_path = Path(a.config)
    cfg = json.loads(cfg_path.read_text())
    if a.dry_run and a.record:
        sys.exit("--dry-run output is not a result; drop --record")
    budget = a.budget or cfg["budget"]
    out = Path(a.out or ROOT / "results" / "E10" / a.run)
    out.mkdir(parents=True, exist_ok=True)
    mon = load_monitor(cfg)
    run_number = int(a.run.split("-R")[1])
    jobs = plan(cfg, run_number)
    m = manifest.start(a.run, "E10", " ".join(sys.argv), {**cfg, "budget": budget},
                       seeds=dict(master=mo.MASTER_SEED, spawn_key_prefix=run_number),
                       confirmatory=cfg["monitor"] == "main",
                       inputs=[cfg_path, ROOT / "configs" / "llm" / "models.json",
                               ROOT / "configs" / "llm" / "pins.json"],
                       packages=("numpy", "scipy", "vllm", "crsafety")) if a.record else None
    lock = threading.Lock()

    def log(msg):
        with lock:
            print(time.strftime("%H:%M:%S"), msg, flush=True)

    t0 = time.perf_counter()
    done = {j["label"]: load_run(out, j["label"]) for j in jobs}
    todo = [j for j in jobs if done[j["label"]] is None or done[j["label"]].budget != budget]
    log(f"{a.run}: monitor {mon.name} ({mon.sha256()[:8]}), {len(jobs)} runs x {budget} attempts; "
        f"{len(jobs) - len(todo)} already done")
    usage, specs = serve_and_run(todo, mon, cfg, budget, out, [int(g) for g in a.gpus.split(",")], log,
                                 a.dry_run, a.port)
    runs = [load_run(out, j["label"]) for j in jobs]
    missing = [j["label"] for j, r in zip(jobs, runs) if r is None]
    incomplete = [json.loads(line) for line in open(out / "incomplete.jsonl")] \
        if (out / "incomplete.jsonl").exists() else []
    runs = [r for r in runs if r is not None]
    hours = (time.perf_counter() - t0) / 3600
    summary = dict(run=a.run, monitor=mon.name, monitor_sha256=mon.sha256(), budget=budget,
                   runs=len(runs), missing_runs=missing,
                   incomplete_attempts_ever=[dict(label=i["label"], used=i["used"], crashed=i["crashed"],
                                                  error=i["error"]) for i in incomplete],
                   outcomes={arm: rt.outcome_shares([r for r in runs if r.arm == arm]) for arm in cfg["arms"]},
                   usage=usage, session_hours=round(hours, 3), dry_run=a.dry_run)
    if runs:
        summary.update(analyse(runs, mon, cfg, budget, out))
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
    p = summary.get("proposed", {})
    log(f"proposed B = {p.get('B')}: {p.get('in_band')}/{mon.M} pilot blind spots in band "
        f"{cfg['band']} (bar {cfg['bar']}, met: {p.get('meets_bar')}); missing runs: {missing or 'none'}")
    if m:
        m["model_ids"] = [f"{s.hf_id}@{s.revision}" for s in specs.values()]
        m["cost"]["gpu_hours"] = round(hours, 3)
        outputs = sorted(str(x) for x in out.glob("*.*") if x.name != "manifest.json")
        manifest.finish(m, outputs=outputs, status="failed" if missing else "succeeded")


if __name__ == "__main__":
    main()
