#!/usr/bin/env bash
# E00-R003: validate the estimators added in R003 against R.
#
#   validation/e00/run_r003.sh [Rscript command]
#
# Rscript needs Rcapture, breakaway (>= 5, installed from github.com/adw96/breakaway),
# iNEXT, vegan and jsonlite (see README.md). The same Rscript is used by
# crsafety.rbridge through CRSAFETY_RSCRIPT.
set -euo pipefail
RSCRIPT=${1:-Rscript}
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$ROOT/results/E00/E00-R003
rm -rf "$OUT/data" && mkdir -p "$OUT/data"
cd "$ROOT"
python3 validation/e00/make_synthetic.py "$OUT/data"
$RSCRIPT "$ROOT/validation/e00/reference_r003.R" "$OUT/data" "$OUT/reference.json"
CRSAFETY_RSCRIPT=$RSCRIPT PYTHONPATH=src python3 validation/e00/compare_r003.py "$OUT"
