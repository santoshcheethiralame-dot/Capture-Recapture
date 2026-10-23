# §6 Related work (draft v0, Santosh, 2026-10-23)

> Sources: `research/README.md` §1, notes G, H1–H3, J (E16) and J2 (E15).
> arXiv is blocked from the sandbox, so every citation is to be re-read in
> the PDF before submission. Items marked (check) carry a number not yet
> verified.

**Estimating what a search missed.** Capture-recapture and unseen-species
estimation go back to Good (1953) and Chao (1984, 1987). Incidence-based
coverage and extrapolation come from Chao and Jost (2012) and Chao et al.
(2014), and non-identifiability of the count under heterogeneity from Link
(2003) and Mao and Lindsay (2007). We use these estimators unchanged and
match the reference implementations exactly (iNEXT, SpadeR, vegan,
Rcapture, VGAM). Our contribution is their validation and failure map for
AI-safety tools, not new estimators.

**Unseen estimation in ML and software.**
- *Software testing.* STADS (Böhme 2018) treats fuzzing as species
  discovery. Its follow-ups estimate residual risk (FSE 2021) and correct
  for adaptive bias (Liyanage et al., ICSE 2024), which we use as our
  de-adaptation method.
- *Evaluation metrics.* Mark-Evaluate (Mordido and Meinel 2020) uses
  mark-recapture estimators as text-generation metrics, the earliest use
  in ML evaluation we know of.
- *LLM outputs.* Good-Turing methods count knowledge or measure deployment
  coverage (KnowSum; semantic alphabet size; SHADE; Blind-Spot Mass). All
  work from one pooled sample rather than replicated runs.
- *Theoretical objection.* NOVA (Avestimehr et al. 2026) argues that
  Good-Turing is a local diagnostic, not an estimate of total undiscovered
  mass. We agree for open-ended discovery, and therefore restrict our
  claims to the catchable population of a fixed tool and budget.
- *Closest prior work.* Kansal (2026) applies richness and coverage
  estimators to planted failures of tabular classifiers, and capture-
  recapture across LLM judges to benchmark label errors. Our design adds
  replicated independent runs, identity matching, dependence and
  adaptivity.

**Coverage and completeness in red teaming and auditing.**
- *Red teaming.* STING (Talokar et al. 2026) models red teaming as time to
  first jailbreak. Kaur (2026) bounds what a null red-team result
  certifies. SCARCE (2026) estimates rare-event rates. Jones et al.
  forecast attack success at larger budgets. None estimates how many attack
  strategies remain unfound.
- *Auditing.* Alignment-auditing benchmarks (Marks et al.; AuditBench;
  RL-trained auditors, 2026) plant behaviours to *score auditors*. We use
  the same planted organisms to *estimate what an audit left
  undiscovered*.
- *Document review.* Technology-assisted review uses Chao-type stopping
  rules. Bron et al. report a mean recall above target but per-run success
  well below it (check). This motivates reporting success rates of stopping
  rules, not means (E13).

**SAE reliability across seeds.**
- *Cross-seed overlap.* Paulo and Belrose (2025) find that about 30% of
  latents are shared across seeds. Ghosh et al. (2026) show the strictly
  matched share grows with training tokens. Gerasimov et al. (2026) define
  a per-feature stability probability, in effect a detectability, without
  estimating what is missed.
- *Ground truth.* SynthSAEBench (Chanin and Garriga-Alonso 2026) provides
  synthetic worlds with known features and the multi-seed SAE zoo used in
  E02.
- *Reconstruction is not coverage.* "Sanity checks for SAEs" (2026) shows
  that high explained variance can coexist with low feature recovery.
- *Missed features.* Engels et al. (2025) decompose SAE error into
  linearly predictable and nonlinear parts. Our E16 bracket builds its
  upper bound on that decomposition.

**Planting known items to calibrate detection.**
- *Software and ecology.* Error seeding (Mills 1972; Lloyd, Yip and Chan
  1999) and mark-resight designs calibrate detection with planted or
  marked items.
- *Privacy.* Inserted canaries measure memorisation (Carlini et al. 2019;
  Steinke et al. 2023; verify).
- *Our use.* E15 uses planted marks to fit detectability and calibrate
  coverage of real items, checked on held-out marks. We found no prior
  instance of that design (E15-R001).

## Notes for revision
- Trim to 0.5 page for the main paper; the full version goes to the
  appendix.
- Keep the NOVA paragraph: reviewers will raise it.
- Every arXiv ID is in `research/README.md`; resolve them into the .bib
  after re-reading.
