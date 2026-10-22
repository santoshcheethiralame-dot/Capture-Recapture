"""Read and write detection histories (docs/PROTOCOLS.md §10).

A cell directory holds ``detections.csv``, ``runs.csv`` and, in testbeds with
truth, ``items.csv``. Only the standard library and numpy are used, so the
files stay the single interface between run producers and the analysis.
"""

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .estimators import IncidenceData

DETECTION_COLS = ["cell_id", "run_idx", "item_id", "identity", "evidence", "score"]
RUN_COLS = ["cell_id", "run_idx", "catcher", "seed", "role", "status", "cost_gpu_h"]
ITEM_COLS = ["item_id", "planted", "covariates"]
RUN_STATUSES = {"ok", "crashed_rerun", "failed_counted_as_none"}
ROLES = {"estimation", "reference"}


@dataclass
class Cell:
    """One experiment cell: a binary matrix over its runs, plus metadata."""

    cell_id: str
    item_ids: list
    run_idx: list
    X: np.ndarray  # items × runs; includes items found only in excluded runs as zero rows
    runs: list = field(default_factory=list)
    items: dict = field(default_factory=dict)

    def data(self):
        return IncidenceData.from_matrix(self.X)


def _read(path, cols):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and set(cols) - set(rows[0]):
        raise ValueError(f"{path}: missing columns {sorted(set(cols) - set(rows[0]))}")
    return rows


def read_cell(directory, role="estimation", identity=None):
    """Load a cell, keeping runs with the given ``role`` (None keeps all).

    Detections are restricted to one identity rule; ``identity=None`` requires
    the file to use a single rule. Runs listed in runs.csv with no detections
    are kept as empty columns.
    """
    directory = Path(directory)
    runs = _read(directory / "runs.csv", RUN_COLS)
    dets = _read(directory / "detections.csv", DETECTION_COLS)
    cells = {r["cell_id"] for r in runs} | {r["cell_id"] for r in dets}
    if len(cells) != 1:
        raise ValueError(f"{directory}: expected one cell_id, found {sorted(cells)}")
    for r in runs:
        if r["role"] not in ROLES or r["status"] not in RUN_STATUSES:
            raise ValueError(f"{directory}: bad role/status in run {r['run_idx']}")
    rules = {r["identity"] for r in dets}
    if identity is None:
        if len(rules) > 1:
            raise ValueError(f"{directory}: several identity rules {sorted(rules)}; pass identity=")
    else:
        dets = [r for r in dets if r["identity"] == identity]

    kept = sorted(int(r["run_idx"]) for r in runs if role is None or r["role"] == role)
    if len(kept) != len(set(kept)):
        raise ValueError(f"{directory}: duplicate run_idx")
    known_runs = {int(r["run_idx"]) for r in runs}
    unknown = {int(r["run_idx"]) for r in dets} - known_runs
    if unknown:
        raise ValueError(f"{directory}: detections for runs not in runs.csv: {sorted(unknown)}")

    item_ids = sorted({r["item_id"] for r in dets})
    row = {i: k for k, i in enumerate(item_ids)}
    col = {j: k for k, j in enumerate(kept)}
    X = np.zeros((len(item_ids), len(kept)), dtype=np.int8)
    for r in dets:
        j = int(r["run_idx"])
        if j in col:
            X[row[r["item_id"]], col[j]] = 1

    items = {}
    if (directory / "items.csv").exists():
        for r in _read(directory / "items.csv", ITEM_COLS):
            items[r["item_id"]] = dict(
                planted=r["planted"].strip().lower() in {"true", "1", "yes"},
                covariates=json.loads(r["covariates"]) if r["covariates"] else {},
            )
    return Cell(cells.pop(), item_ids, kept, X,
                [r for r in runs if int(r["run_idx"]) in col], items)


def write_cell(directory, cell_id, X, item_ids, identity, runs=None, items=None):
    """Write a binary matrix as a cell (used by simulations and tests).

    ``runs`` is a list of dicts with RUN_COLS keys (cell_id and run_idx are
    filled in); by default every run is an ``ok`` estimation run.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    X = np.asarray(X)
    K = X.shape[1]
    with open(directory / "detections.csv", "w", newline="") as f:
        w = csv.DictWriter(f, DETECTION_COLS)
        w.writeheader()
        for i, j in zip(*np.nonzero(X)):
            w.writerow(dict(cell_id=cell_id, run_idx=j + 1, item_id=item_ids[i],
                            identity=identity, evidence="", score=""))
    runs = runs or [{} for _ in range(K)]
    with open(directory / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, RUN_COLS)
        w.writeheader()
        for j, r in enumerate(runs):
            base = dict(catcher="", seed="", role="estimation", status="ok", cost_gpu_h="")
            w.writerow({**base, **r, "cell_id": cell_id, "run_idx": j + 1})
    if items:
        with open(directory / "items.csv", "w", newline="") as f:
            w = csv.DictWriter(f, ITEM_COLS)
            w.writeheader()
            for item_id, meta in items.items():
                w.writerow(dict(item_id=item_id, planted=str(meta.get("planted", False)).lower(),
                                covariates=json.dumps(meta.get("covariates", {}))))
