# §7 Limitations (draft v0, Santosh, 2026-10-23)

- **Only the catchable population.** Coverage is relative to what *this*
  tool, at *this* budget, can find at all. Failure modes no run can find
  (π = 0) are invisible to every estimator here. A high coverage says the
  tool has saturated, not that the model is safe. We state this beside
  every reported number.

- **Counts are lower bounds.** We report the number of failure modes only
  as a lower bound (Chao2). Under strong heterogeneity, the bound can be
  far from the truth. In simulation its interval covered the true count in
  fewer than half of the replicates once N ≥ 500 with K ≤ 10 (E01-R001,
  R004).

- **Small audits are noisy.** At the item counts typical of real audits
  (N of about 14–20), Ĉ is unbiased but its error in a single audit is
  large: the 80th percentile of |Ĉ − C| is 0.06–0.14 (E01-R006,
  exploratory). Per-audit claims need the interval, not the point
  estimate.

- **Independence is a design requirement, not an assumption we can test
  away.**
  - Catchers that share a base model, prompts or data overstate coverage
    (E01 H1f; E08).
  - Adaptive red teams overstate it (E01 H1d; E10).
  - Our diagnostics (n_eff, overlap ratios) flag strong dependence. Mild
    dependence can hide behind heterogeneity: in simulation, a dependence
    test was masked by it (E01 H1c, not supported).
  - De-adaptation methods from software testing over-corrected at our
    scale (E01-R009, exploratory).

- **Identity rules can invent or merge failure modes.** Splits
  understate coverage and inflate counts; merges do the reverse. In a
  pilot, feature splitting alone produced about 3.5 clusters per true
  feature under a one-to-one matcher (E04-R003, pilot). Corrections need a
  labelled sample, and their accuracy depends on it (E05).

- **Planted ≠ real.** Testbeds plant failure modes so the truth is known.
  Real failure modes may be harder to find, rarer or differently
  distributed. E15 tests whether planted marks behave like real features
  (H15c), and E11 checks invariance on real SAEs. The gap is not closed.

- **Scale.** Under our $0 budget (D-007), catchers, attackers and targets
  are open 7–9B models and Pythia-70M / Gemma-2-2B SAEs. Frontier-scale
  replication (E18) depends on funding.

- **Judge-based identity.** For red-team and audit findings, identity
  depends on an LLM judge and a rubric. Judge errors are identity errors;
  we validate the judges, but residual error remains.

- **Model drift.** Hosted models change. We pin open-weight versions; the
  results describe those versions.
