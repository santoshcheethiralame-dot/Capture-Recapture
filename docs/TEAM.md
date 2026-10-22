# Team plan: Santosh and Kushal

Two people, two tracks, one paper. Each track is owned end to end by one
person. The two meet at a few well-defined handoffs. Every confirmatory
result is checked by the person who did **not** produce the data.

If you'd rather swap roles, change the names here, in
`notebook/REGISTRY.md` and in the `Owner` rows of the experiment pages.

## Roles

| | **Santosh**: statistics and interpretability | **Kushal**: safety testbeds and agents |
|---|---|---|
| Owns | Estimator library and its validation; simulation study; everything SAE; all confirmatory analyses of detection histories; the stopping rule; the study pre-registration (statistics sections); repository maintenance (CI, `tools/`) | Kaggle LLM stack (vLLM serving, call cache, model pinning); model organisms; the planted-blind-spot monitor; auditor and attacker scaffolds; identity judges; disclosure policy; E18 if funded |
| Experiments (lead) | E00, E01, E02, E03, E05, E06, E07, E11, E13, E16 | E08, E09, E10, E12, E14, E17, E18 |
| Shared experiments | E04 (SAE arm), E15 (SAE arm), E09 Gemma Scope tool, E10 de-adaptation (A3) | E04 (attack arm), E15 (audit arm) |
| Confirmatory analysis of the other's data | E08, E09, E10 (runs the frozen analysis on Kushal's histories) | E02, E03, E06 (re-runs the frozen analysis script on Santosh's histories as an independent check) |
| Kaggle account | SAE work | LLM work |
| Paper sections | Setting and estimands, method, simulation and SAE results, stopping rule, statistics appendix, NeurIPS checklist items 4–8 | Introduction, testbeds, audit and red-team results, limitations, broader impact, safeguards and LLM-usage items, related work (safety side) |

**Shared by both:**
- freezing the pre-registration;
- independent hand-labelling for judge validation (each labels the same
  100 items without seeing the other's labels; human–human κ is reported);
- the weekly scoop check (alternate weeks);
- the abstract and conclusion;
- final read-through of every section.

## Rules that make two people more rigorous than one

1. **Four-eyes freeze.** No pre-registration is frozen until the other
   person has reviewed it in a PR and approved it. The reviewer's name goes
   in the freeze note:
   `python tools/notebook.py freeze E08 --note "prereg v1; reviewed by Santosh"`.
2. **Separation of data and analysis.** For E08, E09 and E10, Kushal
   produces detection histories in the agreed format (PROTOCOLS §10). He
   does not compute coverage estimates on confirmatory data. Santosh runs
   the frozen analysis script on them. For SAE experiments, Kushal re-runs
   the frozen script independently, as a check.
3. **Independent hand labels.** Judge validation uses both people's labels.
   The judge must reach κ ≥ 0.7 against each, and human–human κ is
   reported.
4. **Owner-only edits.** Each experiment page is edited by its owner. The
   other person comments through PR review. Shared pages are edited
   through PRs.
5. **Named runs.** Every run has an owner (`--owner`). LOG entries start
   with the author's name.

## Handoffs (interfaces)

| # | What | From → To | Format | Due |
|---|---|---|---|---|
| H1 | Estimator library (validated) | Santosh → Kushal | `src/crsafety/estimators/` + PROTOCOLS §1 | 2026-11-01 |
| H2 | Detection-history format | both agree | PROTOCOLS §10 | 2026-10-29 |
| H3 | Kaggle LLM serving notebook + call cache + pinned models (Q-D14) | Kushal → Santosh | `kaggle/llm_serving.ipynb`, `src/crsafety/llm/` | 2026-11-05 |
| H4 | Identity judge + rubric (validated) | Kushal → both | `prompts/`, validation report in E08 | 2026-11-12 |
| H5 | Frozen analysis scripts for E08, E09, E10 | Santosh → (frozen) | `analysis/E08.py`, … | at each freeze |
| H6 | E08 / E10 workshop histories (L0 + L3; A1 + A2) | Kushal → Santosh | PROTOCOLS §10 | 2027-01-10 |
| H7 | Gemma Scope white-box tool for E09 T3 | Santosh → Kushal | `src/crsafety/tools/gemma_scope.py` | 2026-12-15 |
| H8 | De-adaptation (A3a, A3b) implementation | Santosh → Kushal | `src/crsafety/deadapt.py` | 2027-01-10 |
| H9 | E09 histories | Kushal → Santosh | PROTOCOLS §10 | 2027-03-15 |

## Timeline by person

Weeks run Monday to Sunday. ★ marks a joint milestone.

| Dates | Santosh | Kushal |
|---|---|---|
| **Oct 23 – Nov 1** | E00: estimator library, R validation (sandbox), tests. Agree H2 format | Set up Kaggle (phone verification, internet, HF token). vLLM on 2 × T4; pick and pin models (Q-D14); LLM call cache. E10-R001: build and unit-test the monitor |
| **Nov 2 – Nov 8** | E01 simulation (all blocks); propose † thresholds | E08-R001 pilot (floor/ceiling, scaffold). E10-R002 difficulty pilot. Judge candidates. Deliver H3 |
| **★ Nov 6 – 8** | **Pre-registration v1 freeze**: review each other's pages; tag `prereg-v1.0`; GitHub release → Zenodo → OSF | same |
| **Nov 9 – 22** | E02 (Kaggle: zoo download, oracle and matched histories) | Both label 100 reports → judge validation (H4). E08 L0 runs (R003) |
| **Nov 23 – Dec 6** | E03 matcher bake-off; E05 error injection (CPU) | E08 L3 runs (R005); E10 A1 + A2 runs. E09 synthetic data and implants (R001–R002) |
| **Dec 7 – 20** | Phase 1 analysis; **lead the preprint draft**; build the Gemma Scope tool (H7) | E09 verification and pilot (R004); E08 L1 (R004); handoff of workshop histories begins |
| **★ Dec 15 – 20** | **arXiv preprint v1 + Alignment Forum post** (Phase 1 + first audit and red-team results) | same |
| Dec 21 – Jan 3 | buffer / holidays | buffer / holidays |
| **Jan 4 – 17** | Confirmatory analysis of E08 and E10 (H6); de-adaptation A3 (H8); E04 SAE arm | E09 T1 and T2 runs; E04 attack arm; E10 A4 |
| **Jan 18 – Feb 1** | Workshop writing: method, results, appendix | Workshop writing: intro, testbeds, limitations |
| **★ ~Feb 1** | **ICLR 2027 workshop submission** | same |
| **Feb 2 – Mar 15** | E06 grid (Kaggle; share quota with Kushal if needed); E09 analysis plan; E13 prep | E09 T3 runs; E08 L2; E10 A5; H9 handoff by Mar 15 |
| **Mar 16 – 31** | E09 confirmatory analysis; E13 stopping rule | E15 novelty check (Q-N1); E12 or E15 audit-arm prep |
| **Apr 1 – 30** | E13 final; E11 (if quota allows); E15 SAE arm | E15 audit arm; E14 (if time); NeurIPS checklist items 9–16 |
| **★ Apr 1** | **Gate G4**: is everything core on track? | same |
| **★ Apr 30** | **Writing freeze** for NeurIPS | same |
| **May 1 – ~15** | Paper: figures from `results/`, statistics appendix, checklist | Paper: safety framing, related work, anonymised code release |
| **★ ~May 15** | **NeurIPS 2027 submission** (date to confirm) | same |

**Rough load.** Santosh has more experiments, but most run on CPU or are
batch SAE jobs. Kushal has fewer, but carries the infrastructure and the
interactive agent work. Rebalance at the January review if one side is
consistently more than a week behind: the first things to move are E04,
E15 and E06 cells.

## Weekly rhythm

- **Monday sync (30 min):**
  1. Gates and blockers (`ROADMAP.md`, `OPEN-QUESTIONS.md`).
  2. Handoffs due this week.
  3. Kaggle quota left on each account.
  4. Decisions needed (write them into `DECISIONS.md` during the call).
  5. Whose turn for the scoop check.
- **Daily:** a LOG entry by whoever worked, starting with their name.
- **Friday:** `python tools/notebook.py render && python tools/notebook.py check`;
  merge open PRs; push.

## Git workflow

- `main` is the shared truth. It is protected: changes arrive by pull
  request, reviewed by the other person (aim for under 48 h). The current
  work lives on `claude/beautiful-brahmagupta-a5tjcs`; merge it into `main`
  through a PR to start.
- **Branch names:** `santosh/<exp>-<topic>`, `kushal/<exp>-<topic>`
  (e.g. `kushal/e08-pilot`). Keep PRs small: one experiment step per PR.
- **`notebook/runs.csv`:** always `git pull` before
  `tools/notebook.py new`. If two people register runs at once, the rebase
  conflict is two added lines. Keep both, renumber the later run if the IDs
  collide, and run `render`.
- **Append-only files** (`LOG.md`, `DECISIONS.md`, `DEVIATIONS.md`): add at
  the bottom only. Conflicts are resolved by keeping both entries in date
  order.
- **Frozen pre-registration blocks:** never edit them. CI fails if one
  changes without a deviation entry.
- **Never commit** API keys, `.env`, Kaggle tokens, model weights or large
  activations.
- **CI** (`.github/workflows/notebook.yml`) runs `tools/notebook.py check`
  and compiles the Python on every push and PR.

## Onboarding checklist (Kushal)

1. Read, in order:
   - `README.md`;
   - `research/README.md` (the dossier);
   - `docs/PREREGISTRATION.md`;
   - `notebook/README.md`;
   - this file;
   - the E08, E09 and E10 pages.
2. Accounts:
   - GitHub repo access;
   - Kaggle (phone-verified, internet on);
   - Hugging Face token (accept the Llama and Gemma licences).
3. Run `python pilot/simulate.py` and `python tools/notebook.py check`
   locally.
4. First PR: Q-D14 model choices, plus the Kaggle serving notebook (H3).
