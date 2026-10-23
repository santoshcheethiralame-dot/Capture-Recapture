# §1 Introduction (draft v0, Santosh, 2026-10-23)

> Status: first draft. Claims follow the claim → evidence map in
> `docs/PAPER-PLAN.md`. Results not yet run appear as [pending: run].
> Vocabulary per `docs/GLOSSARY.md`.

Safety evaluations are reported as lists of findings. An alignment audit
found three hidden behaviours; a red team found twelve jailbreak
strategies; an interpretability tool surfaced a few hundred features.
What these reports do not say is how complete the search was. A lab
cannot tell whether three findings mean the model has three problems, or
that the audit found the three easiest of thirty. Yet completeness is what
decides whether to run another audit, ship, or keep looking.

Repeated runs carry information about completeness. When two independent
audits of the same model find mostly the same failure modes, the search is
probably near saturation. When each run finds mostly new ones, much is
still undiscovered. Ecologists turned this intuition into estimators of
unseen species from repeated surveys, and software testing uses the same
idea to estimate residual risk from fuzzing campaigns (Böhme 2018). We
apply it to AI-safety discovery tools and ask which quantities can be
estimated reliably, under what conditions, and how the estimates fail.

Our answer separates two quantities. **Audit coverage**, the share of the
tool's detectable failure mass that the runs have already found, can be
estimated from the overlap between runs, together with **new finds from more
runs**, Δ(m). The **number** of failure modes cannot: under uneven
detectability it is not identifiable, and estimators of it are lower bounds
that can be far below the truth. We therefore propose a reporting format of
the form *"we found n failure modes; coverage is C (95% interval); K more
runs would find about m more"*, with counts given only as lower bounds.

We validate this on testbeds where the truth is known by construction:
- SAE features in synthetic worlds with planted features (SynthSAEBench,
  our own seeded grid);
- hidden behaviours implanted by fine-tuning (AuditBench-style organisms);
- red-team blind spots planted in a monitor.

**Contributions.**
1. *Coverage is estimable, counts are not.* In simulation, Chao-Jost
   coverage is unbiased to within 0.01 in every cell where its assumptions
   hold (E01-R001–R004), while Chao2 falls short of the true count
   (E01-R001, R004). On real tools with planted truth: [pending: E02, E06,
   E09, E10].
2. *An interval that covers what it claims to.* The standard bootstrap
   interval for coverage covers the realized coverage of an audit in only
   about 76% of cases at nominal 95% (E01-R005). We bootstrap the
   estimation error instead, which brings coverage to 0.90–0.95
   (E01-R008).
3. *Identity is the bottleneck.* Deciding when two findings are the same
   failure mode dominates the error budget. We give a truth-free diagnostic
   for the matching threshold, and corrections that use a small labelled
   sample of candidate pairs [pending: E03, E05].
4. *Failure modes with known directions.* We measure how each failure
   biases coverage, and give diagnostics that flag it:
   - auditors sharing a base model overstate completeness;
   - adaptive red teams overstate it;
   - spurious splits understate it.
   [pending: E08, E10; simulation: E01 H1d–f.]
5. *When to stop.* A stopping rule on the lower bound of coverage reaches
   its target in [pending: E13] of campaigns and saves [pending] of runs.

We release the estimator library, validated against the reference R
implementations, the pre-registration and lab notebook, and the testbeds'
detection histories.

## Notes for revision
- Fig. 1 (concept) goes beside the second paragraph.
- Keep the first paragraph's examples generic; do not name a lab's audit.
- Do not claim "first use of species estimators in ML" (Mark-Evaluate,
  STADS and Kansal precede us). Claim the first *validated* coverage
  estimates for safety discovery tools, with a map of how they fail.
