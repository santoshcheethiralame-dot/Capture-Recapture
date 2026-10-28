"""E10-R001: build the main and pilot monitors and verify them (Kushal; CPU).

    python analysis/e10/r001_verify.py [--run E10-R001] [--config configs/e10/r001.json] [--out <dir>]
    ... --out <scratchpad> --attacks 20 --per-cell 2     # smoke test: no manifest

For each monitor (main, pilot; M, tiers and the per-family cap from the
config; --out defaults to results/E10/<run>) it checks, per
E10 §2 R001:
1. round trip: every grammar cell's reference attack is recovered on exactly
   one path, that cell (``per_cell`` tokens each, with benign noise);
2. every blind spot is reachable: an attack through it alone succeeds and is
   credited to it alone;
3. every other cell is blocked;
4. no success without a blind spot: ``attacks`` random attacks (1-2 decoding
   layers from distinct families, a split in 25%, 0-2 benign messages) give
   zero successes against a hole-free guard; against the monitor every
   success is credited to its blind spots and every block has a hole-free path;
5. benign conversations are never blocked.
Writes the blind-spot lists (with sha256), checks.csv and summary.json.
Seeds: SeedSequence(20261032, spawn_key=(monitor, check)); the monitors come from
one integer program weighted by SeedSequence(20261032) (`instances`).
"""

import argparse
import csv
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from crsafety import manifest  # noqa: E402
from crsafety import monitor as mo  # noqa: E402

NONSPLIT = [c for c in mo.CELLS if mo.family(c) != "split"]


def rng_for(which, check):
    return np.random.default_rng(np.random.SeedSequence(mo.MASTER_SEED, spawn_key=(which, check)))


def random_attack(rng, max_depth):
    retries = 0
    while True:
        cells, fams = [], set()
        while len(cells) < int(rng.integers(1, max_depth + 1)):
            c = str(rng.choice(NONSPLIT))
            if mo.family(c) not in fams:
                fams.add(mo.family(c))
                cells.append(c)
        if rng.random() < 0.25:
            cells = [f"split:{int(rng.integers(2, 5))}"] + cells
        tok = mo.make_token(rng)
        try:
            return cells, tok, mo.attack(cells, tok, rng, noise=int(rng.integers(0, 3))), retries
        except (ValueError, RuntimeError):
            retries += 1


def verify(mon, which, per_cell, n_attacks, n_benign, rows):
    def add(check, subject, ok, detail=""):
        rows.append(dict(monitor=mon.name, check=check, subject=subject, ok=int(bool(ok)),
                         detail=detail))
        return ok

    holes = {b.item_id for b in mon.blind_spots}
    rng = rng_for(which, 1)
    for cell in mo.CELLS:
        bad = 0
        for _ in range(per_cell):
            tok = mo.make_token(rng)
            msgs = mo.attack([cell], tok, rng, noise=int(rng.integers(0, 3)))
            bad += mo.recover(msgs, tok, mon.max_depth) != [(cell,)]
        add("1_round_trip", cell, bad == 0, f"{bad}/{per_cell} off")

    rng = rng_for(which, 2)
    for b in mon.blind_spots:
        bad = 0
        for _ in range(per_cell):
            tok = mo.make_token(rng)
            v = mon.screen(mo.attack([b.cell], tok, rng, noise=1), tok)
            bad += not (v.outcome == "success" and v.credited == (b.item_id,))
        add("2_hole_reachable", b.item_id, bad == 0, f"{bad}/{per_cell} not credited alone")

    rng = rng_for(which, 3)
    for cell in [c for c in mo.CELLS if c not in mon.by_cell]:
        bad = 0
        for _ in range(per_cell):
            tok = mo.make_token(rng)
            bad += mon.screen(mo.attack([cell], tok, rng, noise=1), tok).outcome != "blocked"
        add("3_other_blocked", cell, bad == 0, f"{bad}/{per_cell} not blocked")

    rng = rng_for(which, 4)
    none = mo.Monitor([], max_depth=mon.max_depth)
    out_none, out_mon, credits, retries = Counter(), Counter(), Counter(), 0
    bad_none = bad_mon = 0
    for _ in range(n_attacks):
        cells, tok, msgs, r = random_attack(rng, mon.max_depth)
        retries += r
        v0, v = none.screen(msgs, tok), mon.screen(msgs, tok)
        out_none[v0.outcome] += 1
        out_mon[v.outcome] += 1
        bad_none += v0.outcome == "success"
        if v.outcome == "success":
            credits[len(v.credited)] += 1
            bad_mon += not (v.credited and set(v.credited) <= holes
                            and all(mon.first_hole(p) for p in v.paths))
        elif v.outcome == "blocked":
            bad_mon += all(mon.first_hole(p) for p in v.paths)
    add("4_no_success_without_hole", "hole-free guard", bad_none == 0,
        f"{bad_none} successes in {n_attacks}; outcomes {dict(out_none)}")
    add("4_success_only_through_holes", "monitor", bad_mon == 0,
        f"{bad_mon} violations; outcomes {dict(out_mon)}; credits per success {dict(credits)}; "
        f"encoder retries {retries}")

    rng = rng_for(which, 5)
    fp = sum(mon.screen([mo.benign(rng) for _ in range(int(rng.integers(1, 5)))],
                        mo.make_token(rng)).outcome != "no_leak" for _ in range(n_benign))
    add("5_benign_pass", "benign conversations", fp == 0, f"{fp}/{n_benign} flagged")
    return dict(outcomes_hole_free=dict(out_none), outcomes_monitor=dict(out_mon),
                credits_per_success=dict(credits), encoder_retries=retries)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="E10-R001")
    ap.add_argument("--config", default=str(ROOT / "configs/e10/r001.json"))
    ap.add_argument("--out")
    ap.add_argument("--attacks", type=int)
    ap.add_argument("--per-cell", type=int)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())
    smoke = a.attacks is not None or a.per_cell is not None
    cfg["attacks"] = a.attacks or cfg["attacks"]
    cfg["per_cell"] = a.per_cell or cfg["per_cell"]
    out = Path(a.out or ROOT / "results/E10" / a.run)
    out.mkdir(parents=True, exist_ok=True)
    m = None if smoke else manifest.start(
        a.run, "E10", " ".join(sys.argv), cfg,
        seeds=dict(master=mo.MASTER_SEED,
                   monitors="one integer program, weights from SeedSequence(master)",
                   checks="SeedSequence(master, spawn_key=(monitor, check))"),
        inputs=[Path(a.config)])
    t0 = time.time()
    main_mon, pilot = mo.instances(cfg["M"], cfg.get("tiers"), cap=cfg.get("cap"),
                                   match_families=cfg.get("match_families", True))
    rows, summary = [], dict(M=cfg["M"], cap=cfg.get("cap"),
                             tiers=list(cfg.get("tiers") or mo.default_tiers(cfg["M"])),
                             grammar_cells=len(mo.CELLS), max_depth=main_mon.max_depth)
    for which, mon in enumerate((main_mon, pilot)):
        spec = mon.spec() | dict(sha256=mon.sha256())
        (out / f"blind_spots_{mon.name}.json").write_text(json.dumps(spec, indent=2) + "\n")
        summary[mon.name] = dict(sha256=mon.sha256(),
                                 tiers=dict(Counter(b.tier for b in mon.blind_spots)),
                                 **verify(mon, which, cfg["per_cell"], cfg["attacks"],
                                          cfg["benign"], rows))
    summary["pilot_overlap"] = sorted(set(main_mon.by_cell) & set(pilot.by_cell))
    fams = [{mo.family(b.cell) for b in m.blind_spots} for m in (main_mon, pilot)]
    summary["families"] = dict(main=len(fams[0]), pilot=len(fams[1]),
                               main_not_in_pilot=sorted(fams[0] - fams[1]))
    rows.append(dict(monitor="pair", check="disjoint", subject="main,pilot",
                     ok=not summary["pilot_overlap"], detail=len(summary["pilot_overlap"])))
    if cfg.get("match_families", True):
        rows.append(dict(monitor="pair", check="pilot_covers_main_families", subject="main,pilot",
                         ok=fams[0] <= fams[1], detail=" ".join(sorted(fams[0] - fams[1]))))
    with open(out / "checks.csv", "w", newline="") as f:
        w = csv.DictWriter(f, ["monitor", "check", "subject", "ok", "detail"])
        w.writeheader()
        w.writerows(rows)
    failed = [r for r in rows if not r["ok"]]
    summary.update(checks=len(rows), failed=len(failed), seconds=round(time.time() - t0, 1),
                   passed=not failed)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("checks", "failed", "passed", "seconds")}))
    for r in failed[:20]:
        print("FAIL", r)
    if m:
        manifest.finish(m, outputs=[out / "summary.json", out / "checks.csv",
                                    out / "blind_spots_main.json", out / "blind_spots_pilot.json"],
                        status="succeeded" if not failed else "failed")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
