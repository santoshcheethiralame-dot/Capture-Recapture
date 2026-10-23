# Results summary

One line per hypothesis. Update when an experiment's analysis is final.
Verdicts: **supported**, **not supported**, **inconclusive**, or **pending**.
Every estimate links to run IDs.

## Study hypotheses

| ID | Hypothesis | Verdict | Key estimate (95% CI) | Evidence (runs) | Paper location |
|---|---|---|---|---|---|
| PH1 | Coverage is estimable | pending | | | |
| PH2 | Counts are only lower bounds | pending | | | |
| PH3 | Identity errors dominate; corrections recover most bias | pending | | | |
| PH4 | Same-model catchers overstate completeness | pending | | | |
| PH5 | Adaptive red teams overstate completeness; de-adaptation corrects | pending | | | |
| PH6 | The coverage stopping rule is reliable | pending | | | |
| SH1 | Tool types are complementary | pending | | | |
| SH2 | Planted-mark calibration works | pending | | | |
| SH3 | Covariates help only when they explain detectability | pending | | | |
| SH4 | Real-SAE coverage is invariant to the sampling unit | pending | | | |

## Experiment-level hypotheses

| ID | Verdict | Estimate | Runs |
|---|---|---|---|
| H0a–H0c | supported | Deterministic estimators match R to ≤ 2.8e-10 (437 comparisons, 34 datasets); bootstrap s.e. within 3 MCSE; 377 / 377 property tests pass. R003 estimators (log-linear, generalised Chao, breakaway_nof1 bridge) match R to ≤ 3.0e-12 (1,744 comparisons, 29 datasets); 595 / 595 property tests pass. Chiu-Chao correction not implemented (contingency) | E00-R001–R004 |
| H1a (clean set; gate G1) | supported | max \|bias of Ĉ\| 0.009 (MCSE 0.003) over 14 clean cells | E01-R001, R002, R004 |
| H1a (literal set) | not supported | shared families up to +0.26 | E01-R002, R004 |
| H1b | not supported | Chao2 CI covers N in 0.92 of replicates at N = 50; < 0.50 only for N ≥ 500, K ≤ 10 | E01-R001, R004 |
| H1c | not supported | Chapman −18.5% at odds ratio 1/3 (−34.9% at 1): heterogeneity masks the dependence | E01-R002 |
| H1d | supported | Ĉ bias +0.071 at c = 2 | E01-R002 |
| H1e | supported | f = 0.15: Ĉ −0.158, Chao2 +81% | E01-R003 |
| H1f | supported | one family minus six: +0.197 | E01-R002 |
| H2a–H2d | pending | | |
| H3a–H3c | pending | | |
| H4a–H4c | pending | | |
| H5a–H5d | pending | | |
| H6a–H6e | pending | | |
| H7a–H7c | pending | | |
| H8a–H8c | pending | | |
| H9a–H9d | pending | | |
| H10a–H10e | pending | | |
| H11a–H11c | pending | | |
| H12a–H12c | pending | | |
| H13a–H13d | pending | | |
| H15a–H15c | pending | | |

## Exploratory findings worth following up

- The pre-registered iNEXT bootstrap interval for coverage under-covers the
  realized coverage (0.73–0.91 at nominal 0.95). A bootstrap of Ĉ* − C*
  (`crsafety.coverage_interval`) reaches 0.896–0.950 on fresh datasets.
  Adopted as the primary interval (D-010). E01-R005, R007, R008.
- The realized-coverage interval holds at small N: it covers C in
  0.894–0.954 of replicates at N = 14–20 (fresh datasets; D-010 A condition
  from Kushal's review met). E01-R010.
- Per-cell coverage error is large at the item counts of real audits
  (N = 14–20): 80th percentile of |Ĉ − C| 0.06–0.14, although Ĉ is
  unbiased. Motivates the PH1 proposal in D-010. E01-R006.
