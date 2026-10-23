# Research notes (raw)

These are the working notes behind [`../README.md`](../README.md). Each file
was written by one research agent with a fixed brief, in two rounds:
seven topic agents first, then four gap-filling agents for what the first
round could not reach, then two agents for documentation practice and
testbed feasibility (I1, I2). Read the main report first. Come here for the full
paper-by-paper detail, numbers and search logs.

| File | Topic |
|---|---|
| [A-statistics.md](A-statistics.md) | Estimators, heterogeneity, identifiability, dependence, coverage and extrapolation, software, and an estimator decision guide. Includes a review of the pilot. |
| [B-identity-errors-and-mse.md](B-identity-errors-and-mse.md) | Misidentification in ecology, record linkage plus population size, multiple systems estimation (human rights, modern slavery, epidemiology), and a concrete plan for matching features and attacks. |
| [C-software-security-precedents.md](C-software-security-precedents.md) | Software inspections, fuzzing as species discovery (STADS, adaptive bias), vulnerability rediscovery, bug bounties. |
| [D-sae-features.md](D-sae-features.md) | SAE consistency across seeds and widths, matching methods, synthetic ground truth, public SAE suites, and Phase 1 and 2 design. |
| [E-redteam-audit.md](E-redteam-audit.md) | Control and monitoring, auditing agents, trojan competitions, public attack corpora, an identity rubric for attack strategies, and ranked datasets. |
| [F-dependence-and-identity.md](F-dependence-and-identity.md) | Correlated LLM catchers, LLM and embedding clustering for identity, and the microbial-ecology precedent (OTU thresholds, spurious singletons). |
| [G-novelty-check.md](G-novelty-check.md) | 38-query search for prior work, with each hit classified, positioning advice, and possible collaborators. |
| [H1-ml-unseen-and-alternatives.md](H1-ml-unseen-and-alternatives.md) | Good-Turing and unseen-species work on LLMs, rare-event alternatives, technology-assisted review, and the two Kansal repositories (closest prior work). |
| [H2-redteam-gaps.md](H2-redteam-gaps.md) | AuditBench details, which public datasets have per-person IDs, reward-hacking catalogues (BAITBENCH, MALT, ImpossibleBench), control settings, Petri and Bloom. |
| [H3-sae-gaps.md](H3-sae-gaps.md) | SynthSAEBench details and its released multi-seed SAE zoo, Sharkey et al., identifiability theory, frequency spectra, and matching methods. |
| [H4-validation-evidence.md](H4-validation-evidence.md) | Where capture-recapture was checked against a known total, plus HRDAG, Census PES, record-linkage error correction, and singleton correction. |
| [I1-documentation-best-practices.md](I1-documentation-best-practices.md) | Pre-registration (OSF, ADEMP, Hofman two-stage), Monte Carlo error formulas, lab-notebook practice, NeurIPS checklist, disclosure norms, release documentation. Basis for `docs/` and `notebook/`. |
| [I2-testbed-feasibility.md](I2-testbed-feasibility.md) | Practical facts from reading the testbed repos: SynthSAEBench config and seeding, AuditBench harness and costs, Petri/Bloom, BashArena/ControlArena, Böhme de-adaptation, API prices, R tooling. Basis for `docs/COMPUTE.md` and `docs/DATA.md`. |
| [J-e16-novelty.md](J-e16-novelty.md) | E16-R001 (2026-10-23): no prior residual-based upper bound on missed SAE features, and no capture-recapture over SAE seeds; Engels et al. dark matter is the basis of the upper bound. Also a scoop check. |
| [scripts/](scripts/) | The agents' scratch simulations, which produce the "[sim]" numbers in notes A and B. They are rough but they run: `python research/notes/scripts/check1.py`. |

## How much to trust these notes

- The agents could not open PDFs. The environment blocked direct downloads,
  so everything came through a search tool that returns abstracts, snippets
  and its own reading of a paper. Each note labels its claims (seen,
  secondary, memory, unverified). Check a number against the paper before
  you rely on it.
- Each agent had about 25 to 45 searches. Coverage gaps are listed at the
  end of each file.
- arXiv IDs were checked against search results. The main report flags the
  ones it depends on that are still unconfirmed.

## Corrections made after the notes were written

- **G, H1:** "Mark-Evaluate" is by Mordido and Meinel (COLING 2020), not
  Meister. Fixed in G.
- **H2** says "Chen/Wen/Kirchner 2608.28945: NOT FOUND". The paper exists:
  "Automated Researchers Can Mitigate Well-characterized Alignment Failures",
  Chen Yueh-Han, Jiaxin Wen, Jan Hendrik Kirchner, arXiv 2608.28945 (28 Aug
  2026). Anthropic's write-up uses the title "... Reliably Mitigate ...". Its
  harness has been open-sourced.
- **D** leaves SynthSAEBench's authors unverified. H3 confirms them: David
  Chanin and Adrià Garriga-Alonso. H3 also corrects D on two points. The
  "reseed noise" in Chanin (2605.18229) re-runs the evaluation of one fixed
  SAE; it does not train new SAEs. And SynthSAEBench does ship multi-seed
  SAEs.
- **E, F** call Kansal's repos "seen". H1 read them directly, and the main
  report confirms they exist (last commits 7 and 16 October 2026).
