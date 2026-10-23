# Kushal's positions on FREEZE-V1 items 1, 2, 3, 8 and 10 (2026-10-23)

Completes the positions section of
[`2026-10-23-kushal-four-eyes.md`](2026-10-23-kushal-four-eyes.md), which
left items 2 and 8 open. Written against `main` at a54182f (after D-013,
D-014 and the new freeze items 16–18). No experiment page is edited here.

| # | Proposal (FREEZE-V1 §2) | Kushal's position |
|---|---|---|
| 1 | E09/E10 PH1: pooled \|bias\| ≤ 0.03 plus interval coverage ≥ 0.85 of cells | Item 17 replaces the E09/E10 part. Keep 0.05 in ≥ 80% of cells for E02/E06, which carry PH1 |
| 2 | PH2 at small N | Restrict the "intervals miss N" half to testbeds with N ≥ 500 (E02, E06). Keep "Chao2 < N" everywhere. H9b stays descriptive |
| 3 | PH3a ratio 2, PH4 0.05, PH5 0.05 | Keep all three; PH4/PH5 read against the catcher-agnostic truth (item 16). Add power: E10 M = 20 → 40; E08 second target model if the Kaggle quota allows (Q-B3) |
| 8 | Disclosure window 30 days | 30 days, extendable to 90 on the provider's request, reason logged. Kushal owns it |
| 10 | E10 A3 | D-012 option A plus C, both scored against the catcher-agnostic truth (item 16); PH5 reworded per item 18; attempt-level A3 (option B) exploratory only |

## Item 2: PH2 at small N

E01 H1b shows the interval half fails at N = 50 (the log-normal Chao2 CI
covers N in 0.92 of replicates); E09 has N = 14. Keeping it pre-registers a
known "not supported" that says nothing about E09 and reads as PH2 failing.
Restricting it is not post hoc: E01 is the stage meant to set such limits,
and no E09 data exists. The prereg must say the restriction comes from
E01 H1b (D-005, prior knowledge disclosed).

## Item 3: power, not the threshold, is the problem

At 16–20 items one realization of Ĉ − C has sd ≈ 0.06. A "supported"
verdict (estimate ≥ 0.05, lower bound ≥ 0.02) then needs a true effect of
roughly 0.11–0.14; a real 0.05 effect reads "inconclusive". In an
illustration with graded detectability (not a registered run; should be
re-run as an exploratory E01 run before it is cited), the adaptive arm's
Ĉ − C against pooled reference truth had sd 0.060 at M = 20 and 0.043 at
M = 40. Hence:
- **E10: M = 40 planted blind spots.** The monitor is ours, so this costs
  no attacker runs, only more unit tests in R001 (E10 §2 change, Kushal's
  page, before its freeze).
- **E08: second target model** (the existing contingency, 16 more
  organisms) committed in advance rather than conditional on the pilot SD,
  if Q-B3 shows the quota covers about double E08's GPU-hours.
- Report the minimal detectable effect at the final N next to each verdict.
- PH3a ratio 2 is Santosh's call; revisiting it after the E03 pilot is clean
  only if E03 freezes after that pilot.

## Item 8: disclosure

30 days is short enough not to block a preprint and long enough for triage;
no AI-specific standard exists. Under D-007 every E08–E10 target is an open
model or our own monitor, so it only triggers in E18. To close in
`DISCLOSURE.md` at the freeze: the "owner to confirm" note becomes Kushal,
and the pre-release review that no E10 blind spot mirrors a weakness of a
deployed product gets Kushal as owner, due before the M4 preprint
(~2026-12-15).

## Freeze timing

E08 and E10 should lock after their pilots, not on Nov 6–8: FREEZE-V1 §3
locks only pages whose pilots are complete. E08 still needs R001 and R002
(judge validation, scheduled Nov 9–22); E10 needs R001 and R002, and the
monitor is rebuilt for M = 40.
