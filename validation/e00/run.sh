#!/usr/bin/env bash
# E00-R001: validate crsafety against R reference implementations.
#
#   validation/e00/run.sh <spader_R_dir> [Rscript command]
#
# <spader_R_dir>: R/ directory of a clone of https://github.com/cran/SpadeR.
# Rscript needs iNEXT, vegan, Rcapture, VGAM and jsonlite (see README.md).
set -euo pipefail
SPADER=${1:?path to SpadeR R/ directory}
RSCRIPT=${2:-Rscript}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$ROOT/results/E00/E00-R001
rm -rf "$OUT/data" && mkdir -p "$OUT/data"
cd "$ROOT"
python3 validation/e00/make_synthetic.py "$OUT/data"
$RSCRIPT "$ROOT/validation/e00/reference.R" "$OUT/data" "$SPADER" "$OUT/reference.json"
PYTHONPATH=src python3 validation/e00/compare.py "$OUT"
