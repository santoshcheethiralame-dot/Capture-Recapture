# Lab log

Append-only. Newest entry at the bottom. Corrections are new entries
("Correction to 2026-11-03: ..."), never edits. Template:
[`templates/entries.md`](templates/entries.md).

---

## 2026-10-22: Project set-up; prior knowledge on record

**Did:**
- Chose idea 3 from "Six Research Ideas in AI Safety" (15 Oct 2026).
- Ran the literature survey (11 agent reports, about 400 searches; see
  `research/`).
- Wrote and ran the pilot simulation (`pilot/`, commits dc6a0a7 and
  a6ff751).
- Built this notebook and the study pre-registration (v0.1, not frozen).

**Prior knowledge (what we had already seen before any pre-registration was
frozen).** This matters for the confirmatory status of later experiments,
so it is listed in full:
- **Pilot results** (`pilot/results.md`), all on simulated data:
  - Chao2 matches its population bound;
  - coverage error ≤ 0.02 under heavy tails;
  - Δ prediction within 2 to 13% (Zipf) and about 20% low (logit-normal
    σ = 2);
  - 15% ghosts → Chao2 +42%;
  - family-shared effects: Chao2 −21% with 1 family vs −2% with 6.
- **Published numbers we know:**
  - Paulo and Belrose: 30 to 42% of latents shared across seeds.
  - Ghosh et al.: 2% → 29% strict matches as training data grows.
  - Kansal's two studies: the unseen share is estimable, counts are lower
    bounds; label-error intervals 102 to 797 for a truth of 181.
  - AuditBench: about 37% default success *(secondary source)*.
  - SLEIGHT-Bench: 20 of 40 attacks never caught.
- **Not seen:** any SynthSAEBench SAE weights, any AuditBench run output,
  any E10 monitor run. The confirmatory experiments (E02 onwards) start
  blind to their own outcome data.

**Design choices informed by the prior knowledge:**
- coverage, not N, as the primary estimand;
- K ≥ 6 (validation K = 10 to 20);
- matching treated as a measured quantity;
- dependence and adaptivity built into the design.

**Next:** E00 (estimator library). Resolve the open questions blocking E02
and E09 (data access) in `docs/OPEN-QUESTIONS.md`.

## 2026-10-22 (later): Documentation and feasibility check

**Did:** Wrote the study pre-registration (v0.1), pre-registrations for E00
to E17 with contingencies, the supporting docs (`docs/`) and the notebook
tool. Two research agents checked documentation best practice (I1) and
testbed feasibility (I2).

**Saw (from reading testbed code; no experiment outcomes):**
- **SynthSAEBench default world has a mild tail.** Zipf exponent 0.5 and
  p_min = 5e-4, so every feature fires about 10^5 times in training. Misses
  there come from capacity and absorption, not sampling. → E02 tests the
  structurally uncatchable regime; E06's base world uses α = 1.0 and
  p_min = 1e-6.
- **Zoo seeds are uncontrolled.** Initialisation and data vary jointly and
  unseeded. SAELens does not seed training. → E06 and E11 seed explicitly,
  with an R001 hash check.
- **AuditBench:** repo `safety-research/auditing-agents`; per-run
  `quirks/*.md` outputs; 70B targets need 2–4 × 80 GB GPUs; a GPU-free
  system-prompt suite (16 quirks) exists; the investigator is hard-wired to
  Claude. → E08 now uses Petri, which can run any model family as the
  auditor, on the system-prompt organisms.
- **Tooling:** R + Rcapture + iNEXT + breakaway install in this sandbox via
  conda-forge. There is no GPU and no Docker daemon here.

**Next:** Owner decisions on budget (Q-B1), licences (D-006) and the
disclosure notice window. Then E00.

## 2026-10-22 (evening): $0 plan and team split

**Decided:**
- **D-007:** run everything at $0, with open models on the sandbox CPU and
  free Kaggle GPUs. Frontier replication moves to E18 (only if credits
  arrive).
- **Team:** Santosh owns statistics, estimators and the SAE track; Kushal
  owns the safety testbeds (E08–E10), LLM infrastructure and judges. Each
  runs the confirmatory analysis on the other's data. See `docs/TEAM.md`.

**Changed (pre-freeze, not deviations):**
- E06: scaled-down world.
- E08: open-model auditor ladder.
- E09: AuditBench-lite (fine-tuned Gemma-2-2B organisms; Gemma Scope
  white-box tool).
- E10: open attackers with a harmless proxy goal.
- E11: Pythia-70M only.
- New page: E18.
- `tools/notebook.py` now requires `--owner` on every run.
- Detection-history format: PROTOCOLS §10.
- CI checks the notebook on every push.

**Next:** Santosh: E00. Kushal: Kaggle LLM stack and model pinning (Q-D14),
E10 monitor (E10-R001). Freeze target: 8 November.

## 2026-10-22 (night): E00 estimator library validated against R

**Did:**
- Built `src/crsafety` (commit f792c71). It contains the estimators,
  the Chao bootstrap and detection-history I/O (PROTOCOLS §10).
- Wrote 377 property tests.
- Wrote `validation/e00/`, which compares the library against iNEXT,
  vegan, SpadeR, Rcapture and VGAM on 34 datasets.
- Ran E00-R001 and E00-R002 from the clean commit.

**Saw:**
- All 437 reference comparisons pass. Deterministic quantities agree to
  2.8e-10 or better. Bootstrap s.e. agree within Monte Carlo error.
- All 377 property tests pass.
- Three formula findings came from reading the reference source; each was
  matched to the reference:
  - coverage when Q2 = 0 uses iNEXT's bias-corrected f0;
  - the Chao2 interval falls back to a Poisson-type interval when Q1 ≤ 1;
  - ICE follows SpadeR, because `fossil::ICE` does not implement the
    published formula.
- Two code fixes came from the tests:
  - Darroch Mt returned infinity when one run found every item; the MLE
    there is S;
  - Huggins now uses an analytic gradient and tighter tolerance. It matches
    VGAM to 3e-10 (was 3e-8).
- Sandbox R is now 4.5.3 with iNEXT 3.0.2. The E00 contingency table names
  older versions.

**Decided:** D-008, formula conventions.

**Next:**
- Kushal reviews `results/E00/E00-R001/summary.md` and the D-008
  conventions (four-eyes rule).
- E00-R003, the remaining estimators: Chiu-Chao is needed before E05.
- E01 simulation study on top of `crsafety`, frozen by 5 November.

