# E00-R001 comparison

References: R R version 4.5.3 (2026-03-11); iNEXT 3.0.2; vegan 2.7.5; VGAM 1.1.14; Rcapture 1.4.4; SpadeR (github.com/cran/SpadeR).

Datasets: 34. Comparisons: 437.

| Quantity | Reference | Hypothesis | Datasets | Max rel. diff | Failures |
|---|---|---|---|---|---|
| chao2 | iNEXT::ChaoRichness | H0a | 31 | 2.48e-15 | 0 |
| chao2_vegan | vegan::specpool | H0a | 26 | 2.48e-15 | 0 |
| chao2_se | iNEXT::ChaoRichness | H0a | 31 | 3.97e-15 | 0 |
| chao2_lo | iNEXT::ChaoRichness | H0a | 31 | 3.63e-15 | 0 |
| chao2_hi | iNEXT::ChaoRichness | H0a | 31 | 2.76e-15 | 0 |
| coverage | iNEXT:::Chat.Sam | H0a | 31 | 7.08e-16 | 0 |
| new_items_1xK | iNEXT:::TD.m.est_inc | H0a | 31 | 3.40e-13 | 0 |
| new_items_2xK | iNEXT:::TD.m.est_inc | H0a | 31 | 2.40e-13 | 0 |
| ichao2 | SpadeR::SpecInciiChao2 | H0a | 29 | 2.87e-15 | 0 |
| ice | SpadeR::SpecInciModelh | H0a | 30 | 3.09e-15 | 0 |
| jackknife1 | vegan::specpool | H0a | 26 | 2.98e-15 | 0 |
| jackknife2 | vegan::specpool | H0a | 26 | 3.14e-15 | 0 |
| darroch_mt | Rcapture::closedp.t (Mt) | H0a | 17 | 2.36e-10 | 0 |
| huggins_N | VGAM::vglm posbernoulli.t | H0a | 3 | 6.10e-11 | 0 |
| huggins | VGAM::vglm posbernoulli.t (coefficients) | H0a | 7 | 2.83e-10 | 0 |
| boot_se_S2K | iNEXT:::iNEXT.Sam bootstrap | H0b | 31 | 5.92e-02 | 0 |
| boot_se_cov | iNEXT:::iNEXT.Sam bootstrap | H0b | 25 | 4.38e-02 | 0 |

All comparisons passed.
