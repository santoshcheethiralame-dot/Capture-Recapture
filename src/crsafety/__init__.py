"""Coverage estimation for AI-safety discovery tools from repeated runs."""

from .estimators import (
    IncidenceData,
    chao2,
    chao2_ci,
    chapman,
    chapman_pairs,
    coverage,
    darroch_mt,
    extrapolate,
    generalized_chao,
    good_turing_coverage,
    huggins,
    ice,
    ichao2,
    jackknife,
    report,
)
from .bootstrap import bootstrap, coverage_interval, delta_interval
from .loglin import closedp, loglinear

__all__ = [
    "IncidenceData", "bootstrap", "chao2", "chao2_ci", "chapman", "chapman_pairs",
    "closedp", "coverage", "coverage_interval", "delta_interval", "darroch_mt", "extrapolate", "generalized_chao",
    "good_turing_coverage", "huggins", "loglinear",
    "ice", "ichao2", "jackknife", "report",
]
__version__ = "0.1.0"
