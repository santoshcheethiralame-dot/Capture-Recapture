# Appendix A: Estimator validation and simulation study (draft v0, Santosh, 2026-10-23)

> Sources: E00 and E01 pages (§5), `notebook/RESULTS.md`,
> `results/E01/analysis/summary.md`. Every number cites its run.
> E00/E01 are awaiting Kushal's four-eyes review; numbers marked † are
> final once it is done.

## A.1 Estimator implementations (E00)

All estimators are implemented in the `crsafety` Python package. Their
formula conventions follow the R reference packages exactly (D-008):
- iNEXT and SpadeR for Chao2, coverage and extrapolation;
- vegan for the jackknife;
- Rcapture for the log-linear models;
- VGAM for Huggins.

On 34 synthetic datasets, the deterministic estimators match R to within
2.8 × 10⁻¹⁰ (437 comparisons; E00-R001†). Bootstrap standard errors agree
within 3 Monte Carlo standard errors, and 377 property tests pass
(E00-R002†). The log-linear models, the generalised Chao estimator and the
`breakaway_nof1` bridge match to within 3.0 × 10⁻¹² (1,744 comparisons,
29 datasets; E00-R003, R004†). The Chiu-Chao singleton correction was not
implemented: its exact formula could not be confirmed from an accessible
source (D-009). The Huggins standard error added later matches VGAM's to
10⁻⁷.

## A.2 Simulation study (E01)

**Design (ADEMP; pre-registered on the E01 page).**
- *Items and runs.* Items i = 1..N have per-run detectabilities π_i, and K
  runs produce a binary detection matrix.
- *Base cell.* N = 500, K = 10, π_i logit-normal with mean 0.2 and σ = 1,
  independent runs, correct identity.
- *One factor at a time* from the base cell:
  - N ∈ {50, 500, 5000};
  - K ∈ {3, 5, 10, 20};
  - heterogeneity: homogeneous; logit-normal σ ∈ {1, 2}; Zipf
    α ∈ {0.5, 1}; a 20% uncatchable class;
  - shared families of runs (1, 2, 3 or 6);
  - true list dependence (odds ratio 1/3, 1, 3);
  - adaptive behaviour (c = 0.5, 1, 2);
  - nested runs;
  - ghosts (f ∈ {0.05, 0.15});
  - merges (g = 0.05).
- *Two-way interactions:* heterogeneity × K, heterogeneity × ghosts, N × K,
  and families × K.
- *Size.* 40 cells × 500 replicates (E01-R001 to R004†). The interval
  study (R005) uses a subset of 12 cells with B = 500 bootstrap resamples
  per replicate.
- *Truth.* C is the realized coverage of each simulated audit. Δ(K) is
  observed by drawing K further runs.
- *Performance measures.* Bias and relative bias, RMSE, interval coverage
  and failure rates, each with its Monte Carlo standard error.

**Pre-registered hypotheses.**

| ID | Hypothesis | Verdict | Estimate (MCSE) |
|---|---|---|---|
| H1a (gate G1) | Coverage is accurate without identity error or adaptivity | supported on the clean set | max \|bias of Ĉ\| over 14 clean cells 0.009 (0.003) |
| H1a, literal set | (as written, including dependence and family cells) | not supported | shared-family cells up to +0.26 |
| H1b | Chao2 intervals do not cover N under heterogeneity | not supported | covers N in 0.92 at N = 50; below 0.50 only for N ≥ 500 and K ≤ 10 |
| H1c | Negative dependence makes Chapman overestimate | not supported | −18.5% (0.3%) at odds ratio 1/3 (heterogeneity masks it; see A.4) |
| H1d | Adaptive "revisit" (c = 2) overstates coverage | supported | +0.071 (0.001) |
| H1e | Ghosts make coverage conservative and Chao2 too high | supported | f = 0.15: Ĉ −0.158 (0.001), Chao2 +81% (0.6%) |
| H1f | One shared family overstates coverage vs six | supported | +0.197 (0.001) |

All from E01-R001 to R004†.

**What moves Ĉ − C, and in which direction** (E01-R001 to R004†):

| Violation | Ĉ − C | Direction for a reader |
|---|---|---|
| one shared family of runs (K = 10) | +0.23 | looks more complete than it is |
| adaptive "revisit found" (c = 2) | +0.07 | more complete |
| positive list dependence (odds ratio 3) | +0.05 | more complete |
| merges (g = 0.05) | +0.01 | negligible |
| nested runs (k = 10) | −0.02 | negligible |
| ghosts (f = 0.05 / 0.15) | −0.05 / −0.16 | less complete (conservative) |
| negative list dependence (odds ratio 1/3) | −0.08 | less complete |
| adaptive "avoid found" (c = 0.5) | −0.15 | less complete |

**Counts are lower bounds.** In the clean cells with N ≥ 500, Chao2 sits
within 1–3 points of the population lower bound N_LB (e.g. both −26% at
σ = 2). Under Zipf α = 1, where the runs see 8% of the items, every count
estimator is 58–96% low while Ĉ stays unbiased (E01-R001†).

## A.3 Intervals for realized coverage

The iNEXT bootstrap interval Ĉ ± z·sd(Ĉ*) covered the realized C in 0.760
(MCSE 0.019) of base-cell replicates, and 0.73–0.91 across clean cells
(E01-R005†). The reason is that it measures the spread of Ĉ, while the
quantity that matters is the error Ĉ − C. In the base cell sd(Ĉ − C) =
0.016, against sd(Ĉ) = 0.012 and a bootstrap s.e. of 0.0095.

The realized-coverage bootstrap (§3) resamples histories from the Chao
pseudo-population, where the realized C* of each resample is known, and
uses sd(Ĉ* − C*). On fresh datasets, its 95% interval covers C in
0.896–0.950 of replicates in clean cells (base 0.906; E01-R008,
exploratory, adopted in D-010). Its one-sided 95% lower bound holds in
0.886–0.952. For Δ, the bias-corrected version covers in 0.886–0.954.

No interval rescues the violated cells (one family, c = 2, f = 0.15),
because the bias exceeds the interval width (Fig. A.2).

## A.4 Notes on design

- **H1c.** The dependence factor sat on top of σ = 1 heterogeneity, which
  alone creates a marginal odds ratio of 2.6 between run blocks and cancels
  the designed 1/3 (marginal odds ratio 0.97). The verdict stands as run;
  this is a lesson about how dependence and heterogeneity confound, not
  evidence that Chapman is robust (freeze packet item 9).
- **Small audits (exploratory, E01-R006).** At N = 14–20, Ĉ stays unbiased
  (|bias| ≤ 0.013). At N = 14, K = 8 and mean detectability 0.2, however,
  only 33% of single audits fall within 0.05 of C (80th percentile 0.14).
  Per-audit tolerances therefore need the interval (D-010).
- **De-adaptation (exploratory, E01-R009).** The ICSE'24 de-adaptation
  algorithm moves coverage to −0.30 in non-adaptive cells, and the FSE'21
  reset estimator is undefined in every replicate at run level. Neither
  corrects adaptive bias at our scale (D-012).

## A.5 Estimator decision guide

| Question | Use | Bias direction and caveat |
|---|---|---|
| How complete is the search? | Chao-Jost Ĉ with the realized-coverage interval | Unbiased under heterogeneity; overstated by shared models, adaptivity and positive dependence; understated by ghosts |
| How much would more runs find? | Δ̂(m), m ≤ K | Mildly conservative (−3% to −11%) under heterogeneity; do not extrapolate past m = K |
| How many failure modes exist? | Chao2, labelled "lower bound" | Low under heterogeneity, far low under heavy tails; inflated by ghosts |
| Is the identity rule trustworthy? | Plateau diagnostic over thresholds (E03); labelled pair sample (E05) | No plateau means no trustworthy threshold |
| Are the runs independent enough? | n_eff/K, observed / expected overlap | Mild dependence can hide behind heterogeneity (H1c) |
| When to stop? | One-sided lower bound of Ĉ ≥ target (E13) | Not valid for adaptive campaigns without correction |

## Figures

- A.1: `results/E01/analysis/figures/fig1_coverage_vs_count` (bias of Ĉ
  and of Chao2, per cell).
- A.2: `results/E01/analysis/figures/fig2_interval_coverage` (iNEXT vs
  realized-coverage bootstrap).
