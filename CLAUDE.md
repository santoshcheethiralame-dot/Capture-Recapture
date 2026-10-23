# CLAUDE.md: project memory

Read this first in every session. It summarises the repo's documentation;
the docs themselves are the source of truth when they disagree.

## The project

**"How complete was the audit?"** Capture-recapture statistics applied to
AI-safety discovery tools (alignment audits, red teams, SAEs). From the
overlap between K repeated runs of a tool, estimate:
- **audit coverage C** (share of detectable failure mass already found):
  the headline estimand;
- **Δ(m)**, new failure modes m more runs would find.

Counts (Chao2, iChao2) are **lower bounds only**: N is not identifiable under
uneven detectability (D-002). Validated first on testbeds with planted /
known truth. Safety framing, ecology only as methods citation (D-001); use
the vocabulary in `docs/GLOSSARY.md` ("failure mode", "catcher", "run",
"coverage", never "species").

- **Budget $0** (D-007): open 7–9B models, this sandbox's CPU, free Kaggle
  GPUs (one account per person). Frontier replication only in E18, if funded.
- **Venues:** arXiv + Alignment Forum Dec 2026 (M4, ~Dec 15–20); ICLR 2027
  workshop ~Feb 1; **NeurIPS 2027 main** ~May 15 (primary); fallbacks SaTML
  2028 / ICLR 2028 / TMLR (D-003).
- **Status (2026-10-23):** nothing frozen; all of Santosh's code for Stage 2 is written and tested. Waiting on Kushal's reviews, the freeze decisions and Kaggle runs.
  E00 R001–R004 and E01 R001–R008 done (awaiting Kushal's review); gate G1
  passed. Prereg is draft v0.2 (interval method changed, D-010). Freeze of
  prereg v1.0 targeted Nov 6–8.

## Team and who I work for

Two people (`docs/TEAM.md`):
- **Santosh** (statistics + interpretability): owns E00, E01, E02, E03, E05,
  E06, E07, E11, E13, E16; SAE arms of E04/E15; Gemma Scope tool (H7),
  de-adaptation A3 (H8); confirmatory analysis of Kushal's E08/E09/E10
  histories; repo maintenance (CI, `tools/`); stats sections of the prereg.
- **Kushal** (safety testbeds + agents): Kaggle LLM stack (vLLM, call cache,
  model pinning Q-D14), E08, E09, E10, E12, E14, E17, E18; judges; disclosure.

**In this repo I am doing Santosh's work** unless told otherwise. Kushal's
experiment pages are owner-only edits: comment via PR, don't edit them.

### Santosh's timeline (from TEAM.md)
| Dates | Work |
|---|---|
| Oct 23 – Nov 1 | **E00** finish: E00-R003 (Chiu-Chao singleton correction, log-linear via Rcapture, breakaway_nof1, Böhning generalised Chao). Agree H2 history format (PROTOCOLS §10) by Oct 29. Deliver H1 (validated library) by Nov 1 |
| Nov 2 – 8 | **E01** simulation (R001–R005), propose † thresholds; gate **G1** (\|bias Ĉ\| ≤ 0.03 in clean cells) |
| Nov 6 – 8 ★ | Prereg v1.0 freeze (four-eyes review; tag `prereg-v1.0` → GitHub release → Zenodo → OSF) |
| Nov 9 – 22 | E02 (Kaggle; zoo download, oracle + matched histories) |
| Nov 23 – Dec 6 | E03 matcher bake-off; E05 error injection; gate G2 (pair F1 ≥ 0.9) |
| Dec 7 – 20 | Phase 1 analysis, lead the preprint draft, H7 Gemma Scope tool |
| Jan 4 – 17 | Confirmatory analysis of E08/E10 (H6), H8 de-adaptation, E04 SAE arm |
| Feb 2 – Apr 30 | E06 grid, E09 analysis, E13 stopping rule, E11, E15 SAE arm |

## Next concrete tasks for Santosh

1. ~~E00-R003~~ done 2026-10-22 (log-linear, generalised Chao,
   breakaway_nof1 bridge; Chiu-Chao left out per contingency, Q-D10 open;
   D-009).
2. Kushal to review E00 (R001–R004 summaries) and D-008/D-009 (four-eyes).
3. ~~E01~~ done 2026-10-22 (H1a clean/G1, H1d–f supported; H1a literal,
   H1b, H1c not). Key findings: iNEXT bootstrap CI under-covers realized C
   (0.76) → `crsafety.coverage_interval` (0.906 on fresh data); per-cell
   PH1 tolerance unattainable at N = 14–20. † threshold proposals in D-010
   part B: **joint decision at the freeze**, not applied.
4. E05: model + corrections in `crsafety.linkage`; pilot done (R004–R005);
   §2a written. Confirmatory R001–R003 **wait for the v1 freeze** (Stage 2).
5. Done 2026-10-22: `crsafety.matching`; `crsafety.stopping` + E13 pilot
   (R003; R002 failed on a bug); E02 Kaggle scripts (`analysis/e02/zoo.py`,
   `evaluate.py`) and E03 `analysis/e03/bakeoff.py`, all tested on a fake zoo.
6. **Freeze packet: `docs/FREEZE-V1.md`** lists every open decision (D-010B,
   D-011, E05 MI/f1-free, D-006 licences, disclosure window) and pages to lock.
7. E02 pipeline complete incl. `fire_counts.py` (dead latents), tested on
   real SAELens 6.54.12 output (installable here: `pip install torch
   "sae-lens==6.54.12"`; the PyTorch CPU index is blocked, PyPI works).
8. M3 matcher done (`analysis/e03/act_corr.py`; bakeoff `--m3`, `--fire-counts`).
9. f1-free alternative (`betabinomial_nof1`) tried on E05 pilot tables and
   rejected; FREEZE-V1 item 6 recommends reporting breakaway_nof1's failure.
10. Done 2026-10-22/23 (no Kaggle needed): Q-D7 resolved, `crsafety.deadapt`
    (A3a/A3b) + E01-R009 (both over-correct; D-012); H5 frozen-analysis
    scripts `analysis/e08–e10/analyse.py` on `crsafety.testbed`; E06
    `worlds.py`/`train.py`/`analyse.py` + seeding check R015; E07
    `huggins_ci` (= VGAM SE) + `analysis/e07/analyse.py`; E04 SAE arm
    `analysis/e04/sae_arm.py` + pilot R003 (splits break H4a for any
    one-to-one rule); E01 figures `analysis/e01/figures.py`; E16-R001 and
    E15-R001 novelty checks (Q-N2, Q-N1 answered) + `analysis/e16/bracket.py`
    (estimand concern in E16 §2a); E11 seeding check R001 passed + `train.py`
    / `analyse.py`; E15 `crsafety.calibrate` + `analysis/e15/inject.py`
    (marks/train/stats/magnitudes) + `analyse.py`; H7 tool
    `crsafety.tools.gemma_scope` (built early); confirmatory runners locked
    at the freeze: `analysis/e05/run.py` + `analyse.py`, `analysis/e13/run.py`;
    paper draft §2–3 in `paper/drafts/`. Freeze packet has 15 items.
    PRs #3 and #4 merged.
11. Left, needing people: Kushal's reviews; the 15 joint decisions in
    `docs/FREEZE-V1.md`; the freeze chain (tag → release → Zenodo → OSF,
    Zenodo from a non-sandbox machine).
12. Left, needing Kaggle: everything in `docs/KAGGLE-RUNBOOK.md` (4 rows are
    allowed before the freeze); Q-D15 (Gemma Scope + Neuronpedia labels).
13. Left, CPU after the freeze: E05-R001–R003, E13-R001, then the CPU
    analyses of Kaggle outputs (E06-R014, E07, E04-R001, E11, E15-R004, E16).
14. Doable any time: paper intro / related work / limitations, Fig. 1
    concept, weekly scoop check (next ~Oct 29; one done 2026-10-23 within
    the novelty checks).

## Repository map

| Path | What |
|---|---|
| `src/crsafety/` | `sim.py` (E01 data-generating mechanisms, `Cell`, `simulate`), `manifest.py` (PROTOCOLS §5 manifests: `start`/`finish`), `histories.py` also has `check_cell` (`python -m crsafety.histories check <dir>`), `bootstrap.py` also has `coverage_interval`/`delta_interval` (primary intervals, D-010). Estimator library: `estimators.py` (IncidenceData, chapman, chapman_pairs, darroch_mt, chao2, chao2_ci, ichao2, jackknife, ice, coverage, good_turing_coverage, extrapolate, huggins, huggins_ci, generalized_chao, report), `loglin.py` (loglinear, closedp: Rcapture models + run interactions), `rbridge.py` (breakaway_nof1 via Rscript; env `CRSAFETY_RSCRIPT`), `bootstrap.py` (iNEXT-style pseudo-population, B=2000), `histories.py` (read_cell / write_cell, PROTOCOLS §10), `linkage.py` (E05 errors + corrections), `matching.py` (SAE identity rules, plateau), `stopping.py` (E13), `deadapt.py` (A3a Liyanage ICSE'24, A3b FSE'21 reset), `testbed.py` (planted-truth loaders + prereg §7 verdicts for E08–E10), `calibrate.py` (E15 planted-mark detectability + HT coverage), `tools/gemma_scope.py` (H7 white-box tool) |
| `tests/test_estimators.py` | 377 property tests (E00-R002) |
| `validation/e00/` | R reference comparison (`run.sh`, `reference.R`, `compare.py`, `make_synthetic.py`) |
| `results/EXX/<run_id>/` | Run outputs (small files only; large ones external with sha256) |
| `notebook/` | Lab notebook: REGISTRY, experiments/E00–E18, runs.csv, LOG, DECISIONS, DEVIATIONS, RESULTS, prereg-locks.csv, templates |
| `docs/` | KAGGLE-RUNBOOK (ordered Kaggle jobs and commands), FREEZE-V1, PREREGISTRATION (PH1–PH6, SH1–SH4), TEAM, ROADMAP (milestones, gates G1–G4), PROTOCOLS, PAPER-PLAN, RISKS, COMPUTE, DATA, DISCLOSURE, OPEN-QUESTIONS, NEURIPS-CHECKLIST, GLOSSARY |
| `research/` | Literature dossier (`README.md`), reading list, 13 agent reports in `notes/` |
| `pilot/` | Early simulation (`simulate.py`, `estimators.py`, `results.md`) |
| `tools/notebook.py` | `new`, `set`, `render`, `freeze`, `check` |
| `configs/e01/cells.json`, `analysis/e01/` | E01 cells and seeds; `run.py R00X` runner, `analyse.py` → `results/E01/analysis/` |
| `analysis/eXX/` | Per-experiment scripts: e01 (run, analyse, figures, deadapt_eval), e02 (zoo, evaluate, fire_counts), e03 (bakeoff, act_corr), e04 (sae_arm), e05 (pilot, run, analyse), e06 (worlds, train, analyse, seeding_check), e07, e08–e10 (frozen H5 analyses, Kushal's data), e11 (seeding_check, train, analyse), e13 (pilot, run), e15 (inject, analyse), e16 (bracket) |
| `paper/drafts/` | Paper section drafts (statistics sections first) |
| `requirements.lock` | uv-compiled lock (numpy 2.5.4, scipy 1.18.1); hashed into manifests |

## Commands

```bash
python -m pip install -e ".[dev]"     # use python -m: the bare `pytest` on PATH is a uv tool without numpy
python -m pytest -q                   # ~700 tests (1 skipped without R + breakaway)
python tools/notebook.py check        # CI runs this + py_compile + pytest
python tools/notebook.py new E01 --owner Santosh --title "..." [--config ...]
python tools/notebook.py set E01-R001 status=running
python tools/notebook.py set E01-R001 status=succeeded summary="<the number that matters>"
python tools/notebook.py render && python tools/notebook.py check
python tools/notebook.py freeze E01 --note "prereg v1; reviewed by Kushal"
```

R (for validation) is not preinstalled. Recipe in `validation/e00/README.md`
(R 4.5 env via micromamba fetched from conda-forge; breakaway 5 built from
`github.com/adw96/breakaway`; CRAN-only pkgs from `github.com/cran/<pkg>`).
Blocked from the sandbox: Hugging Face, arXiv, Zenodo, CRAN, micro.mamba.pm,
peerj.com, PMC (Q-D1). Working: conda-forge, PyPI, `git clone` from GitHub.
rpy2 does not load against the conda R; use `crsafety.rbridge` (Rscript).

## Rules I must follow

**Notebook discipline** (`notebook/README.md`):
- Register every run **before** launching it via `tools/notebook.py`
  (`--owner Santosh`). `runs.csv` is only edited through the tool. No silent
  re-runs: every execution gets a run ID, failures included. Never delete a
  failed run.
- Close runs with a summary giving the number that matters.
- `LOG.md`, `DECISIONS.md`, `DEVIATIONS.md` are **append-only**, newest at
  the bottom; LOG entries start with the author's name. Corrections are new
  entries.
- Never edit a frozen `<!-- prereg:start -->…<!-- prereg:end -->` block (hash
  locked in `prereg-locks.csv`; CI fails). Post-freeze changes → DEVIATIONS +
  new prereg version.
- No peeking at confirmatory outcomes before freeze; pilots on separate
  seeds, declared as pilots. No silent exclusions; estimator NaN/inf are data
  (count failure rates).
- Failure classes: infra / bug / data-access / design / scientific "failure"
  (a result, never rescued by re-tuning).
- After analysis: fill page §5 (confirmatory first, then labelled
  exploratory), update `RESULTS.md`, render + check, commit.

**Protocols** (`docs/PROTOCOLS.md`):
- Estimator conventions are D-008 (match iNEXT / SpadeR / vegan / Rcapture /
  VGAM exactly). Changing them after freeze is a deviation.
- Seeds: master `20261022 + experiment number`;
  `numpy.random.SeedSequence(master).spawn(n)` per cell then per replicate;
  cell seed in every result row.
- Each run writes `results/EXX/<run_id>/manifest.json` (fields in §5).
  Confirmatory runs refuse a dirty tree.
- Reporting recipe (§8): K, S_obs, f1–f4, identity rule; Ĉ with 95% CI
  (headline); Δ̂(K), Δ̂(2K); Chao2 labelled "lower bound"; jackknife-2/ICE;
  dependence diagnostics; sensitivity.
- Simulations: MCSE for every bias/coverage/RMSE; paired comparisons on the
  same datasets.
- Detection-history interface (§10): `detections.csv`, `runs.csv`,
  `items.csv` per cell; analysis code reads only these.
- Every paper number traces to a run ID; figures generated from `results/`.

**Two-person rigour:** four-eyes freeze (other person approves in PR, name in
freeze note); separation of data and analysis (Kushal doesn't compute
coverage on confirmatory E08–E10 data; Santosh runs the frozen script);
owner-only edits of experiment pages.

**Commit identity (user's instruction):** commit as Santosh with no AI
trailers: `git -c user.name="Santosh Cheethirala" -c
user.email="santoshcheethirala.me@gmail.com" commit ...`, no
Co-Authored-By / session lines, no "(with Claude)" in LOG, no AI footer in
PR bodies.

**Git:** `main` protected, PRs reviewed by the other person; branch names
`santosh/<exp>-<topic>` (in Claude sessions, use the assigned branch); small
PRs, one experiment step each. Always pull before `notebook.py new`. Never
commit keys, `.env`, Kaggle tokens, weights or large activations. Don't open
PRs unless asked.

## Key decisions (DECISIONS.md)
D-001 safety framing · D-002 coverage + Δ headline, counts as lower bounds ·
D-003 venues · D-004 plain-git notebook · D-005 tiered prereg with prior
knowledge disclosed · D-006 (proposed, needs owner) code MIT, docs/data
CC BY 4.0 · D-007 $0 plan · D-008 estimator formula conventions · D-009
log-linear ported, breakaway_nof1 via Rscript, Chiu-Chao left out · D-010
realized-coverage bootstrap intervals (A accepted) + † proposals (B, for
the freeze).

## Study hypotheses (PREREGISTRATION.md)
PH1 coverage estimable (\|Ĉ−C\| ≤ 0.05† in ≥ 80%† cells) · PH2 counts are
lower bounds · PH3 identity errors dominate, corrections recover ≥ 50% ·
PH4 same-model catchers overstate coverage (E08) · PH5 adaptive red teams
overstate, de-adaptation corrects (E10) · PH6 lower-bound stopping rule
reliable (E13). Secondary SH1–SH4. † thresholds set after E01.

## Open questions relevant to Santosh
Q-D1 (HF/arXiv access), Q-D2 (zoo contents), Q-D10 (Chiu-Chao formula),
Q-D13 (SAELens seed unused), Q-D15 (Gemma Scope on Kaggle), Q-N2 (E16
novelty), Q-N1 (E15 novelty), Q-B3 (Kaggle quota). Weekly scoop check
alternates between the two (RISKS.md).

## Working conventions learned in practice

- Commit code **before** launching a registered run; the manifest records
  the git state (notebook/ and results/ are excluded from the dirty check,
  other edits are not). Don't edit tracked code while runs are in flight
  (stash if needed).
- Smoke-test runners with `--n-sim 2 --out <scratchpad>`; never treat smoke
  output as results, and disclose in LOG if any numbers were seen.
- Anything designed after seeing results is a new run labelled
  "exploratory" in title/notes, page and summary; replicate on fresh seeds
  with a criterion fixed beforehand before adopting it.
- Prereg changes that set thresholds are proposals for the joint freeze
  (four-eyes); interval/estimator conventions in Santosh's remit can be
  accepted with "Kushal to review".

