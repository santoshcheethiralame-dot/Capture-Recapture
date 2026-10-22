# E00-R003 comparison

References: R version 4.5.3 (2026-03-11); Rcapture 1.4.4; breakaway 5.0.1; iNEXT 3.0.2.

Datasets: 29. Comparisons: 1744.

| Quantity | Reference | Hypothesis | Comparisons | Datasets | Max rel. diff | Failures |
|---|---|---|---|---|---|---|
| closedp.t N | Rcapture::closedp.t | H0a | 195 | 17 | 4.16e-13 | 0 |
| closedp.t se | Rcapture::closedp.t (Fisher information at the MLE) | H0a | 194 | 17 | 2.85e-12 | 0 |
| closedp.t se_printed | Rcapture::closedp.t (printed; glm vcov) | info | 195 | 17 | 2.28e-06 | 0 |
| closedp.t deviance | Rcapture::closedp.t | H0a | 195 | 17 | 3.86e-14 | 0 |
| closedp.t aic | Rcapture::closedp.t | H0a | 195 | 17 | 2.42e-14 | 0 |
| closedp.t bic | Rcapture::closedp.t | H0a | 195 | 17 | 1.94e-14 | 0 |
| closedpCI.t N | Rcapture::closedpCI.t | H0a | 79 | 16 | 3.27e-14 | 0 |
| closedpCI.t se | Rcapture::closedpCI.t (Fisher information at the MLE) | H0a | 72 | 16 | 3.02e-12 | 0 |
| closedpCI.t se_printed | Rcapture::closedpCI.t (printed; glm vcov) | info | 79 | 16 | 1.54e-07 | 0 |
| closedpCI.t deviance | Rcapture::closedpCI.t | H0a | 79 | 16 | 4.94e-14 | 0 |
| closedpCI.t aic | Rcapture::closedpCI.t | H0a | 79 | 16 | 2.58e-14 | 0 |
| closedpCI.t bic | Rcapture::closedpCI.t | H0a | 79 | 16 | 2.04e-14 | 0 |
| generalized_chao | stats::glm (binomial, offset) | H0a | 23 | 23 | 3.69e-15 | 0 |
| generalized_chao=chao2 | iNEXT::ChaoRichness | H0a | 23 | 23 | 2.48e-15 | 0 |
| generalized_chao_cov | stats::glm (binomial, offset) | H0a | 3 | 3 | 1.72e-14 | 0 |
| generalized_chao_cov.beta | stats::glm (binomial, offset) | H0a | 7 | 3 | 2.32e-14 | 0 |
| breakaway_nof1.estimate | breakaway::breakaway_nof1 (direct call) | H0a | 26 | 26 | 0.00e+00 | 0 |
| breakaway_nof1.error | breakaway::breakaway_nof1 (direct call) | H0a | 26 | 26 | 0.00e+00 | 0 |

All comparisons passed.
