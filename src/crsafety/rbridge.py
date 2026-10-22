"""Estimators computed by R packages, called through ``Rscript``.

Used only where porting the R code is not worth it (E00-R003):
``breakaway_nof1`` (Willis 2015), a model-selection procedure over Kemp-type
ratio models fitted with ``nls`` and iterative reweighting.

R is reached by a subprocess with JSON in and out (no rpy2), so the bridge
works wherever ``Rscript`` and the package are installed. Set
``CRSAFETY_RSCRIPT`` to choose the Rscript binary.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .estimators import _data

_NOF1 = r"""
suppressPackageStartupMessages({library(breakaway); library(jsonlite)})
a <- commandArgs(trailingOnly = TRUE)
inp <- fromJSON(a[1], simplifyVector = FALSE)
out <- lapply(inp, function(q) {
  df <- data.frame(index = unlist(q$index), frequency = unlist(q$frequency))
  r <- tryCatch(suppressWarnings(breakaway_nof1(df)), error = function(e) e)
  if (inherits(r, "error")) return(list(estimate = NA, error = NA, lower = NA, upper = NA,
                                        model = NA, reasonable = FALSE, warnings = conditionMessage(r)))
  list(estimate = r$estimate, error = r$error,
       lower = if (is.null(r$interval)) NA else r$interval[1],
       upper = if (is.null(r$interval)) NA else r$interval[2],
       model = if (is.null(r$model)) NA else r$model,
       name = if (is.null(r$other$name)) NA else r$other$name,
       reasonable = if (is.null(r$reasonable)) NA else r$reasonable,
       warnings = if (is.null(r$warnings)) NA else paste(r$warnings, collapse = "; "))
})
write(toJSON(out, auto_unbox = TRUE, digits = NA, na = "null"), a[2])
"""


def rscript():
    return os.environ.get("CRSAFETY_RSCRIPT", "Rscript")


def _run(script, payload):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "s.R").write_text(script)
        (tmp / "in.json").write_text(json.dumps(payload))
        proc = subprocess.run([rscript(), str(tmp / "s.R"), str(tmp / "in.json"), str(tmp / "out.json")],
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Rscript failed:\n{proc.stderr[-2000:]}")
        return json.loads((tmp / "out.json").read_text())


def frequency_table(X):
    """(k, Q_k) for every k with Q_k > 0, the input format of breakaway."""
    d = _data(X)
    Q = np.bincount(d.y, minlength=d.K + 1)
    k = np.nonzero(Q)[0]
    k = k[k > 0]
    return k.tolist(), Q[k].tolist()


def breakaway_nof1(*datasets):
    """``breakaway::breakaway_nof1`` on one or more incidence datasets.

    An f1-free richness estimate: N_hat = (items found >= 2 times) + f1_hat
    + f0_hat, where both f1 and f0 are predicted from the ratios of the
    higher frequency counts. The observed singleton count is never used, so
    the estimate is unaffected by ghosts (spurious singletons) from identity
    errors. The
    incidence frequency counts Q_k are passed as if they were abundance
    frequency counts, which is how the method is applied to incidence data
    in practice; treat the result as a sensitivity check, not a primary
    estimate. Returns a list of dicts (estimate, error, lower, upper, model,
    name, reasonable, warnings), one per dataset.
    """
    payload = []
    for X in datasets:
        k, q = frequency_table(X)
        payload.append(dict(index=k, frequency=q))
    out = _run(_NOF1, payload)
    return out if isinstance(out, list) else [out]
