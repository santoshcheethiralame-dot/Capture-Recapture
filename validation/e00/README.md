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

## E00-R003: log-linear models, generalised Chao, breakaway_nof1

```bash
validation/e00/run_r003.sh [Rscript command]
```

Writes `results/E00/E00-R003/` (`summary.md`, `comparison.csv`,
`reference.json`, input data). Needs R with Rcapture, iNEXT, vegan,
jsonlite and **breakaway ≥ 5**, which conda-forge does not have (its
`r-breakaway` 3.0 pins R 4.1). Environment used on 2026-10-22:

```bash
# micromamba itself from conda-forge (micro.mamba.pm may be blocked):
curl -sSLO https://conda.anaconda.org/conda-forge/linux-64/micromamba-2.3.0-0.tar.bz2
tar -xjf micromamba-2.3.0-0.tar.bz2 bin/micromamba
micromamba create -n r45 -c conda-forge -c bioconda "r-base>=4.5" r-inext r-vegan \
  r-rcapture r-vgam r-jsonlite r-ggplot2 r-lme4 r-magrittr r-tibble r-reformulas \
  bioconductor-phyloseq
git clone https://github.com/adw96/breakaway && <env>/bin/R CMD INSTALL breakaway
```

| Quantity | Reference |
|---|---|
| Log-linear N, deviance, AIC, BIC (12 models) | `Rcapture::closedp.t` |
| Log-linear models with run interactions (± heterogeneity) | `Rcapture::closedpCI.t` with an `mX` formula |
| Log-linear s.e. | Fisher information at Rcapture's fitted coefficients, Rcapture's s.e. formulas (the printed s.e. is compared as information, tolerance 1e-4) |
| Generalised Chao (binomial form), N and coefficients | `stats::glm(binomial, offset = log((K-1)/2))`; without covariates also `iNEXT::ChaoRichness` |
| `breakaway_nof1` through `crsafety.rbridge` | `breakaway::breakaway_nof1` called directly |

The reference script replaces Rcapture's internal `glm.call` so that every
fit, including the Chao (LB) refits after dropping a negative eta, uses
`epsilon = 1e-14`. This changes convergence precision only.
