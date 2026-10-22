# Risk register

Reviewed every Monday. **Likelihood** and **impact** are rated L / M / H.
A risk is *triggered* when its signal appears; then follow the response
and log it.

| ID | Risk | L | I | Signal (trigger) | Response | Owner doc |
|---|---|---|---|---|---|---|
| R01 | **Scooped on Phase 1** (Gerasimov, Ghosh, Paulo and Belrose, or Kansal publish population estimates for SAEs or audits) | M | H | New arXiv paper or repo found by the weekly scoop check | Preprint fast (M4). Re-centre on the safety experiments (E08–E10), which no near-miss covers. Cite and build on it. | ROADMAP |
| R02 | **Coverage estimator fails in simulation** | L | H | Gate G1 | See G1: verify code, re-scope to a failure-analysis paper | E01 |
| R03 | **Matching cannot be made reliable** | M | H | Gate G2 | Use testbeds with identity by construction; soft matching + multiple imputation; sensitivity bands | E03, E05 |
| R04 | **AuditBench-lite organisms fail** (Gemma-2-2B cannot hold the behaviours) | M | H | E09-R002 implant verification | Pre-freeze switch to a ≤ 9B base model with QLoRA; or drop T3 (white-box) | E09 |
| R05 | **Hugging Face / arXiv blocked** in the cloud environment | H | M | Downloads fail | Allow the hosts in the environment's network settings, or download elsewhere and upload | DATA |
| R06 | **Kaggle quota or session limits** (about 30 GPU-h a week per account; ~12 h sessions) | H | M | Weekly quota below plan; sessions cut | Two accounts; checkpointing; LLM call cache; pre-declared cuts; stretch work waits | COMPUTE |
| R07 | **Ceiling or floor effects** in planted testbeds (everything or nothing found) | M | M | Pilot results | Recalibrate difficulty **before freezing** (allowed by each pre-registration) | E08, E10 |
| R08 | **Judge-based identity unreliable** (κ < 0.7) | M | M | Judge validation | Fix the rubric; stronger judge from a different family; report both | PROTOCOLS §2 |
| R09 | **Planted ≠ real** (planted failures easier than real ones, as in Kansal) | H | M | E15-H15c; reviewer critique | E15 planted-mark calibration; state the limitation clearly; E11 invariance checks | E15 |
| R10 | **Model version drift** (a Hugging Face revision changes, or an E18 API model is retired) | L | M | Changed hash or identifier | Pin Hugging Face revisions (commit hashes) and API snapshots; finish each experiment on one version | PROTOCOLS §3 |
| R11 | **Dual-use exposure** (released attack strategies) | L | H | Any release of attack text | DISCLOSURE.md tiers; strategy-level labels only | DISCLOSURE |
| R12 | **Results too imprecise to be useful** (calibrated but wide, as in Kansal's label-error study) | M | H | CI widths in E02/E09 | More cheap runs (K); report decision usefulness (E13); report the negative honestly | E13 |
| R13 | **Too much scope for two people** | H | M | Milestones slipping by > 1 week | Cut stretch tier first, then E06 width/α arms, then E04; never cut E08–E10 | ROADMAP, TEAM |
| R14 | **Non-identifiability objection from reviewers** ("N is meaningless") | M | M | Reviews | It is our point: coverage first, counts as bounds (PH2) | PAPER-PLAN |
| R15 | **NOVA-style objection** (Good-Turing is only local) | M | M | Reviews | Closed, verified, catchable population; test convex discovery cost | PAPER-PLAN |
| R16 | **Licence or gating blocks redistribution** (SLEIGHT-Bench, Tensor Trust) | M | L | Licence check | Release derived statistics and regeneration scripts only | DATA |
| R17 | **Small open models are too weak** (floor effects: auditors or attackers find almost nothing) | M | H | E08/E09/E10 pilots | Pre-freeze adjustments (easier items, larger turn budget, AWQ 14B auditors); report the capability range honestly | E08–E10 |
| R18 | **"Only open 7–9B models" objection** from reviewers | H | M | Reviews | Frame as a limitation; apply for credits to run E18; emphasise that the method, not the catcher, is the contribution | PAPER-PLAN |
| R19 | **Coordination between two people** (blocked handoffs, duplicated work, merge conflicts) | M | M | A handoff late by more than a week | `docs/TEAM.md` interfaces; weekly sync; owner-only edits; small PRs | TEAM |

## Scoop check (weekly)

Search arXiv, OpenReview and the Alignment Forum for:
- "capture-recapture" with LLM, audit, red team or SAE;
- "audit coverage" / "red-team coverage";
- "unseen" with features or failure modes;
- new papers by the near-miss authors.

Record the result in `notebook/LOG.md`.
