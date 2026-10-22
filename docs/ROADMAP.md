# Roadmap

Today: 22 October 2026. Venue dates are estimates unless marked confirmed.
Check the official sites before relying on them.

## Milestones

| # | Date | Milestone | Contents | Experiments |
|---|---|---|---|---|
| M0 | 2026-10-22 | Documentation and notebook set up | this repo | — |
| M1 | 2026-11-01 | Estimator library validated | E00 done | E00 |
| M2 | 2026-11-05 | Simulation study done; **pre-registration v1.0 frozen** (tag, release, Zenodo DOI, OSF) | thresholds set | E01 |
| M3 | 2026-12-05 | Phase 1 results on synthetic SAEs | zoo coverage, matcher bake-off, error injection | E02, E03, E05 |
| M4 | 2026-12-15 | **arXiv preprint v1 + Alignment Forum post** | Phase 1 + E09 pilot | E02, E03, E05, E09-R001/R002 |
| M5 | 2027-01-10 | AuditBench running at scale (gate G3) | first configuration complete | E09 |
| M6 | 2027-02-01 | **ICLR 2027 workshop submission** (suggested deadline; confirmed by ICLR's workshop guidelines) | 4–6 pages: method, synthetic validation, first audit-coverage result | E02, E03, E05, E09 (T1) |
| M7 | 2027-03-31 | Safety experiments complete | auditor similarity, AuditBench full, red-team adaptive bias | E08, E09, E10 |
| M8 | 2027-04-15 | Stopping rule, own seeds | | E06, E13 |
| M9 | 2027-04-30 | Writing freeze for NeurIPS; important extras | | E04, E15 (if novel), E11 (optional) |
| M10 | ~2027-05-15 | **NeurIPS 2027 submission** (estimated; check the call) | full paper + checklist + anonymised code | all core |
| M11 | ~2027-09 | Fallback: SaTML 2028 / ICLR 2028; TMLR companion paper | | stretch experiments |

## Gates (go / no-go)

| Gate | When | Test | If it fails |
|---|---|---|---|
| **G1** | after E01 (~Nov 5) | Coverage estimator \|bias\| ≤ 0.03 in clean simulation cells (H1a) | Stop. Check E00. If the code is right, re-scope the paper to "coverage also fails, and here is why", before any Stage 2 spend. Record a decision. |
| **G2** | after E02 + E03 (~Dec 5) | Some matcher reaches pair F1 ≥ 0.9 on frequent features (H3a) | Phase 1 headline becomes "identity is the bottleneck". Shift weight to testbeds with identity by construction (E10, E09). |
| **G3** | ~Jan 10 | Can we run any AuditBench variant at the needed scale? | Use the E08 fallback (system-prompt organisms) as the audit testbed for the workshop paper. |
| **G4** | ~Apr 1 | Core experiments E08, E09, E10, E13 done or on track | If not: submit the strongest subset to NeurIPS only if the safety claims (PH4 or PH5) are supported; otherwise retarget SaTML 2028 / ICLR 2028. |

## Weekly rhythm

- **Monday:** update `notebook/REGISTRY.md` statuses. Review the gates and
  open questions.
- **Daily:** a `notebook/LOG.md` entry on working days.
- **Friday:** run `tools/notebook.py render && check`, commit, push. Write a
  3-line summary in the log: done, blocked, next.

## Papers and their contents

| Output | Target | Must contain | Nice to have |
|---|---|---|---|
| Preprint v1 | arXiv, Dec 2026 | E01, E02, E03, E05; E09 pilot as a teaser | E04 |
| Workshop paper | ICLR 2027 workshop | E02/E03/E05 + E09 (one configuration) | E10 pilot |
| Main paper | NeurIPS 2027 | PH1–PH6 verdicts: E01, E02, E03, E05, E08, E09, E10, E13 | E04, E06, E15, E11 |
| Companion | TMLR (rolling) | Full simulation study and estimator decision guide (E01, E05, E07) | — |
| Follow-ups | later | E12, E14, E16, E17 | — |

See [`PAPER-PLAN.md`](PAPER-PLAN.md) for the claim-to-evidence map.
