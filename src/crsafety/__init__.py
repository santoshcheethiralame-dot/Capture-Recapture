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
    good_turing_coverage,
    huggins,
    ice,
    ichao2,
    jackknife,
    report,
)
from .bootstrap import bootstrap

__all__ = [
    "IncidenceData", "bootstrap", "chao2", "chao2_ci", "chapman", "chapman_pairs",
    "coverage", "darroch_mt", "extrapolate", "good_turing_coverage", "huggins",
    "ice", "ichao2", "jackknife", "report",
]
__version__ = "0.1.0"
