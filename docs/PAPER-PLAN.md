# Paper plan

**Working title:** *How complete was the audit? Estimating what red teams,
auditors and interpretability tools miss.*

**One-sentence claim:** From the overlap between repeated runs of a safety
discovery tool, we can reliably estimate how much of the detectable failure
mass the tool has found, and how much more extra runs would find. Counts of
missed failures cannot be estimated, and the estimates fail in predictable,
diagnosable ways when auditors share a base model, search adaptively, or
mis-cluster their findings.

## Claim → evidence map

Every claim in the abstract and introduction must appear here, with its
evidence. Claims without confirmatory evidence are worded as exploratory.

| Claim | Hypothesis | Evidence | Figure / table | Status |
|---|---|---|---|---|
| C1. Audit coverage is estimable from repeated runs (with independent runs and validated identity) | PH1 | E02, E06, E09, E10-A1 | Fig. 2 (coverage error by testbed) | pending |
| C2. The number of missed failures is not; counts are lower bounds and their intervals miss | PH2 | E01, E02, E09 | Fig. 3 (Chao2 vs truth; CI coverage) | pending |
| C3. Identity errors dominate the error budget; the plateau diagnostic flags bad thresholds; corrections recover most bias | PH3 | E02, E03, E04, E05 | Fig. 4 (oracle vs matched; threshold sweep) | pending |
| C4. Auditors that share a base model overstate how complete an audit is | PH4 | E08 (+ E01, E06) | Fig. 5 (similarity ladder) | pending |
| C5. Adaptive red teams overstate completeness; de-adaptation corrects it | PH5 | E10 | Fig. 6 (arms) | pending |
| C6. A lower-bound coverage stopping rule reaches its target in most campaigns and saves effort | PH6 | E13 | Table 2 | pending |
| C7. Black-box and white-box audit tools find different things | SH1 | E09 Design B | Fig. 7 | pending |
| C8 (if E15 runs and is novel). Planting known items into a real system calibrates detectability there | SH2 | E15 | Fig. 8 | pending |

## Outline (NeurIPS: 9 pages + appendix)

1. **Introduction (1 page).**
   - "We tested it and found N issues" is how safety evaluations are
     reported; nobody says how complete the testing was.
   - The overlap between repeated runs carries that information.
   - Contributions C1–C6 as bullets.
   - Figure 1: the idea in one picture: two audits, overlap, coverage.
2. **Setting and estimands (1 page).** Catchers, runs, failure modes,
   coverage vs count, the catchable population. Why counts are not
   identifiable (cite Link 2003; Mao and Lindsay 2007). The reporting recipe.
3. **Method (1 page).**
   - Estimators: coverage, extrapolation, lower bound.
   - The identity rule and its diagnostics.
   - Dependence diagnostics.
   - De-adaptation.
   - The stopping rule.

   The ecological origin is acknowledged in one paragraph.
4. **Testbeds with known truth (0.75 page).**
   - SynthSAEBench (interpretability);
   - AuditBench (alignment audits);
   - the planted-blind-spot monitor (red teams).

   Why each has known truth, and how runs are made independent.
5. **Results (4 pages).**
   - 5.1 Coverage is estimable; counts are not (C1, C2).
   - 5.2 Identity is the bottleneck (C3).
   - 5.3 Correlated auditors (C4).
   - 5.4 Adaptive red teams (C5).
   - 5.5 When to stop (C6).
   - 5.6 What audit tools miss (C7).
6. **Related work (0.5 page).**
   - Safety evaluation and red-teaming coverage: STING, Kaur's evidential
     ceilings, SCARCE, Jones et al.
   - Auditing: Marks et al., AuditBench, auditing agents.
   - SAE reliability: Paulo and Belrose, Gerasimov, Ghosh, Chanin.
   - Unseen estimation in ML and software: STADS, Böhme, Mark-Evaluate,
     KnowSum, Kansal.
   - Theoretical limits: NOVA.
7. **Limitations (0.5 page).**
   - The catchable population only.
   - Synthetic-to-real gap.
   - Planted ≠ real.
   - K costs.
   - Judge-based identity.
   - Snapshot drift of API models.
8. **Conclusion and recommendations for labs (0.25 page).** A short
   reporting checklist.

**Appendix:**
- full simulation study (E01);
- estimator decision guide;
- deviation table;
- judge prompts and validation;
- compute;
- the NeurIPS checklist.

## Workshop version (4–6 pages, ICLR 2027 workshop)

C1–C3 on SynthSAEBench, plus the first AuditBench configuration as a
real-audit demonstration. Same claim, smaller scope.

## Figures (planned)

| Fig | Content | Source |
|---|---|---|
| 1 | Concept: two audit runs, overlap → coverage | drawn |
| 2 | Ĉ − C across testbeds and K, with the ±0.05 band | E02, E06, E09, E10 |
| 3 | Chao2 / N vs heterogeneity; CI coverage of N vs of N_LB | E01, E02 |
| 4 | (a) oracle vs matched error; (b) threshold sweep with plateau | E02, E03 |
| 5 | Ĉ − C and n_eff/K along the auditor-similarity ladder | E08 |
| 6 | Discovery curves and Ĉ − C for the non-adaptive / adaptive / de-adapted arms | E10 |
| 7 | Venn / log-linear complementarity of audit tool types | E09 |
| T1 | Estimator decision guide (compact) | E01 |
| T2 | Stopping rule: success rate and runs saved | E13 |

## Writing rules

- Safety vocabulary (see `GLOSSARY.md`). "Coverage", not "sample
  coverage"; "failure modes", not "species".
- Every number traces to a run ID.
- Label every figure and table "confirmatory" or "exploratory".
- Negative results get the same prominence as positive ones.
- Do not claim "first use of species estimators in ML". Claim "first
  validated coverage estimates for safety discovery tools, with a failure
  map".
