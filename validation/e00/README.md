# E00 validation: crsafety against R reference implementations

Run E00-R001 of [`notebook/experiments/E00-estimator-library.md`](../../notebook/experiments/E00-estimator-library.md).

```bash
git clone https://github.com/cran/SpadeR /path/to/SpadeR   # archived on CRAN
validation/e00/run.sh /path/to/SpadeR/R [Rscript command]
```

Steps:
1. `make_synthetic.py` writes synthetic matrices (heterogeneous, heavy-tailed,
   K = 2 to 20) and edge cases (Q1 = 0, Q1 = 1, Q2 = 0, Q4 = 0, tiny data),
   plus covariate datasets for Huggins.
2. `reference.R` exports the datasets bundled with iNEXT (`ant`, `ciliates`),
   Rcapture (`hare`, `mvole`, `bunting`, `duck`, `HIV`, `lesbian`, `rbvole`)
   and vegan (`dune`, `mite`, `BCI`), then computes reference values.
   These exports are not committed (GPL-licensed packages); rerun to get them.
   Printed output of iNEXT and SpadeR is rounded, so their functions are run
   with `round` disabled.
3. `compare.py` writes `comparison.csv` and `summary.md` to
   `results/E00/E00-R001/` and exits non-zero on any failure.

| Quantity | Reference |
|---|---|
| Chao2, its s.e. and log-normal interval | `iNEXT::ChaoRichness`; Chao2 also `vegan::specpool` |
| Coverage | `iNEXT:::Chat.Sam` at t = K |
| New items after m more runs | `iNEXT:::TD.m.est_inc` at K + m, minus S |
| iChao2, ICE | SpadeR `SpecInciiChao2`, `SpecInciModelh` (cut-off 10) |
| Jackknife 1 and 2 | `vegan::specpool` |
| Darroch Mt (K ≤ 12) | `Rcapture::closedp.t`, model Mt |
| Huggins N and coefficients | `VGAM::vglm`, `posbernoulli.t(parallel.t = TRUE ~ z)` |
| Bootstrap s.e. (B = 2,000) | `iNEXT:::iNEXT.Sam` |

Tolerances (pre-registered): relative difference ≤ 1e-6 for deterministic
quantities (H0a); bootstrap s.e. within 3 Monte Carlo s.e. of the difference
(H0b). Chapman and Good-Turing coverage have no R reference here; they are
checked against hand-computed values in `tests/`.

R environment used on 2026-10-22: R 4.5.3, iNEXT 3.0.2, vegan 2.7.5,
Rcapture 1.4.4, VGAM 1.1.14, installed from conda-forge with micromamba
(no root needed):

```bash
micromamba create -n rcr -c conda-forge r-base r-inext r-vegan r-rcapture r-vgam r-jsonlite
```
