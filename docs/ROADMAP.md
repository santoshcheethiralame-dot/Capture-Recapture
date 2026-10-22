# Roadmap

Today: 22 October 2026. Venue dates are estimates unless marked confirmed.
Check the official sites before relying on them.

Budget: $0 (D-007). The per-person plan, handoffs and git workflow are in
[`TEAM.md`](TEAM.md).

## Milestones

| # | Date | Milestone | Contents | Experiments |
|---|---|---|---|---|
| M0 | 2026-10-22 | Documentation and notebook set up | this repo | — |
| M1 | 2026-11-01 | Estimator library validated (Santosh); Kaggle LLM stack running (Kushal) | E00 done; H3 in progress | E00 |
| M2 | 2026-11-08 | Simulation study done; pilots for E08 and E10 done; **pre-registration v1.0 frozen**, each page reviewed by the other person (tag, release, Zenodo DOI, OSF) | thresholds set | E01, E08-R001, E10-R002 |
| M3 | 2026-12-05 | Phase 1 results on synthetic SAEs | zoo coverage, matcher bake-off, error injection | E02, E03, E05 |
| M4 | 2026-12-20 | **arXiv preprint v1 + Alignment Forum post** | Phase 1 + first auditor-ladder and red-team results | E02, E03, E05, E08 (L0, L3), E10 (A1, A2) |
| M5 | 2027-01-10 | Workshop histories handed to Santosh (H6); AuditBench-lite organisms verified (gate G3) | | E08, E10, E09-R002 |
| M6 | 2027-02-01 | **ICLR 2027 workshop submission** (suggested deadline; confirmed by ICLR's workshop guidelines) | 4–6 pages: method, synthetic validation, auditor-similarity and adaptive red-team results | E02, E03, E05, E08 (L0, L3), E10 (A1–A3) |
| M7 | 2027-03-31 | Safety experiments complete | auditor ladder (all levels), AuditBench-lite (3 tool configurations), red-team arms | E08, E09, E10 |
| M8 | 2027-04-15 | Stopping rule, own seeds | | E06, E13 |
| M9 | 2027-04-30 | Writing freeze for NeurIPS; important extras | | E04, E15 (if novel), E11 (optional) |
| M10 | ~2027-05-15 | **NeurIPS 2027 submission** (estimated; check the call) | full paper + checklist + anonymised code | all core |
| M11 | ~2027-09 | Fallback: SaTML 2028 / ICLR 2028; TMLR companion paper | | stretch experiments |

## Gates (go / no-go)

| Gate | When | Test | If it fails |
|---|---|---|---|
| **G1** | after E01 (~Nov 5) | Coverage estimator \|bias\| ≤ 0.03 in clean simulation cells (H1a) | Stop. Check E00. If the code is right, re-scope the paper to "coverage also fails, and here is why", before any Stage 2 spend. Record a decision. **Passed 2026-10-22:** max \|bias\| 0.009 over 14 clean cells (E01). |
| **G2** | after E02 + E03 (~Dec 5) | Some matcher reaches pair F1 ≥ 0.9 on frequent features (H3a) | Phase 1 headline becomes "identity is the bottleneck". Shift weight to testbeds with identity by construction (E10, E09). |
| **G3** | ~Jan 10 | Do the AuditBench-lite organisms pass implant verification (E09-R002)? | Pre-freeze switch to a ≤ 9B base model, or drop the white-box configuration (T3) and report SH1 as untested. |
| **G4** | ~Apr 1 | Core experiments E08, E09, E10, E13 done or on track | If not: submit the strongest subset to NeurIPS only if the safety claims (PH4 or PH5) are supported; otherwise retarget SaTML 2028 / ICLR 2028. |

## Weekly rhythm

- **Monday:** joint sync (agenda in `TEAM.md`). Update `notebook/REGISTRY.md`
  statuses. Review the gates, open questions and Kaggle quota.
- **Daily:** a `notebook/LOG.md` entry on working days.
- **Friday:** run `tools/notebook.py render && check`, commit, push. Write a
  3-line summary in the log: done, blocked, next.

## Papers and their contents

| Output | Target | Must contain | Nice to have |
|---|---|---|---|
| Preprint v1 | arXiv, Dec 2026 | E01, E02, E03, E05; first E08 and E10 results | E04 |
| Workshop paper | ICLR 2027 workshop | E02/E03/E05 + E08 (L0, L3) + E10 (A1–A3) | E09 T1 |
| Main paper | NeurIPS 2027 | PH1–PH6 verdicts: E01, E02, E03, E05, E08, E09, E10, E13 | E04, E06, E15, E11 |
| Companion | TMLR (rolling) | Full simulation study and estimator decision guide (E01, E05, E07) | — |
| Follow-ups | later | E12, E14, E16, E17 | — |

See [`PAPER-PLAN.md`](PAPER-PLAN.md) for the claim-to-evidence map.
