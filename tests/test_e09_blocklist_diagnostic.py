"""E09-R011 blocklist diagnostic on hand-built activation vectors."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis" / "e09"))
from blocklist_diagnostic import diagnose  # noqa: E402


def test_diagnose_counts_hidden_and_changed():
    d = 30
    base = np.linspace(1, 0.1, d)            # feature 0 is the strongest in the base
    moved = base.copy()
    moved[0] += 5                            # implant moves background feature 0
    still = base.copy()
    still[20] += 5                           # implant elsewhere; feature 0 unchanged
    rows = diagnose([(moved, base), (moved, base), (still, base)], blocklist=[0, 29], k=10)
    r0, r29 = rows
    assert r0["feature"] == 0 and r0["n_prompts"] == 3
    assert r0["hidden"] == 3                 # top-1 active on every prompt
    assert r0["in_most_changed"] == 2 and r0["flag"]
    assert r0["median_change_rank"] == 1
    assert r29["hidden"] == 0 and r29["in_most_changed"] == 0 and not r29["flag"]


def test_flag_needs_more_than_half():
    base = np.zeros(20)
    moved = base.copy()
    moved[3] = 1.0
    rows = diagnose([(moved, base), (base, base)], blocklist=[3])
    assert rows[0]["in_most_changed"] == 1 and not rows[0]["flag"]
