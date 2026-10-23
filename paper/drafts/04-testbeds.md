# §4 Testbeds with known truth (draft v0, Santosh, 2026-10-23)

> SAE testbeds by Santosh; the audit and red-team paragraphs are a
> placeholder summary of Kushal's pre-registered designs (E08–E10), for
> Kushal to rewrite. Target length 0.75 page.

Each testbed has failure modes whose identity is known by construction, so
the true coverage of any set of runs can be computed. Every testbed also
makes runs independent by design, and records that design, so violations
can be studied as treatments rather than accidents.

**Interpretability: SAE features in synthetic worlds.**
- *SynthSAEBench-16k (E02).* 16,384 planted feature directions in d = 768
  with Zipfian firing probabilities, a feature hierarchy and low-rank
  correlation (Chanin and Garriga-Alonso 2026).
  - Its released zoo has 5 SAE architectures × 7 sparsity levels × 5
    replicates at width 4,096.
  - A *run* is one trained SAE. A failure mode is *caught* when an SAE
    latent is assigned to a planted feature with |cosine| ≥ 0.7, as in the
    benchmark's own recovery metric (one-to-one assignment).
  - With 4,096 latents for 16,384 features, misses in this zoo come from
    capacity, absorption and splitting rather than sampling.
- *Our own seeded grid (E06).* We train SAEs in a scaled world (4,096
  features, d = 256), with 24 seeds per cell: 16 for estimation and 8
  held back as a reference.
  - One factor varies at a time: the Zipf exponent, the rarest firing
    probability, hierarchy, correlation, width and training budget.
  - Initialisation and data order are seeded separately (verified,
    E06-R015). This lets us compare runs that differ only in
    initialisation with runs that differ only in data, the SAE analogue of
    correlated catchers.
- *Real models (E11, E15).* Pythia-70M SAEs: 8 independent seeds, 4 that
  share a data order, and a random-weights null. Truth there is partial:
  - E11 uses board-game SAEs with researcher-specified features;
  - E15 plants 400 synthetic directions into the training activations,
    with known firing rates, as marks.

**Alignment audits: implanted behaviours (E08, E09; Kushal).**
- *Organisms.* Open instruct models carry one hidden AuditBench-style
  behaviour each, implanted by system prompt (E08, 16 organisms) or by
  fine-tuning (E09, 14 organisms on Gemma-2-2B-it). The implants are
  verified to show the behaviour and to resist direct questioning.
- *Auditors and identity.* A run is one auditor-agent session that ends in
  a report. A judge, validated against labels, decides whether the report
  names the planted behaviour.
- *Varying the catchers.*
  - E08 varies how similar the auditors are: one model and one prompt; one
    model and many prompts; model sizes; three model families.
  - E09 varies the tools: black-box chat, black-box sampling, and a
    white-box SAE tool.

**Red teams: a monitor with planted blind spots (E10; Kushal).**
- *The monitor.* It screens an agent's messages for a harmless proxy goal
  and deliberately lets through 20 specific transformations of graded
  subtlety. The monitor logs which blind spot let each attack through,
  which gives ground-truth identity without a judge.
- *Arms.* Attacker sessions run without seeing verdicts (non-adaptive) or
  seeing them (adaptive), which is a controlled test of adaptive bias.

**Truth.** In each testbed the true detectability of a failure mode is its
catch rate over runs held out from estimation (the reference runs). True
coverage C(K) is the share of that detectability mass found by the K
estimation runs. Where no held-out runs exist, as in E02, the choice of
reference is a pre-registered decision (D-011).

## Notes for revision
- Kushal to rewrite the E08–E10 paragraphs and to confirm the organism
  counts and models after the freeze.
- If E06 shrinks after the timing pilot (E06-R002), update the cell list.
- Table 1 (appendix): one row per testbed giving items, run definition,
  identity rule, K, reference runs and the source of truth.
