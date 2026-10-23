# Kushal's four-eyes review before the v1 freeze (2026-10-23)

Reviewed against `main` at a6da94d (PR #7 merged). Reviewer: Kushal.
Covers `docs/FREEZE-V1.md` §1 and the proposals D-011, D-012 and E04 §2a.
No experiment page is edited here; Santosh's replies go in the PR.

**What I checked:** `python -m pytest` gives 695 passed, 4 skipped
(R-dependent). Re-running `analysis/e01/analyse.py` over the stored
replicates reproduces every committed file in `results/E01/analysis/`
byte for byte. Every E01 manifest has `git_dirty: false`. I could not
re-run the R side of E00 (no R installed here).

**Summary of verdicts**

| Item | Verdict |
|---|---|
| E00 R001–R004, D-008, D-009 | Approve, 2 small comments |
| E01 R001–R009 | Approve as run, 3 comments |
| D-010 part A | Approve, with 1 condition for E09/E10 |
| D-011 | Approve, and it must be extended to E08/E09/E10 (blocking) |
| D-012 | Agree with A, but the real problem with H10b is upstream (blocking for E10's freeze) |
| E04 §2a, R003 | Don't adopt option 2 as proposed; prefer option 3 |

---

## 1. E00 R001–R004, D-008, D-009: approve

Approve. The comparison tables are thorough, and the decisions to follow
iNEXT/SpadeR edge-case conventions (D-008) and to call breakaway through
Rscript (D-009) are the right calls for reproducibility.

Two small comments:

1. **Chapman and Good-Turing have no external reference.** §5 says they
   are checked against hand-computed values in tests. §2's exclusion rule
   says an estimator with neither an R reference nor a published worked
   example is marked "unvalidated" and can't be primary. Neither is
   primary, so nothing breaks, but please either cite a worked example or
   mark both "unvalidated (hand-checked)" in the library docstrings, so
   the page matches its own rule.
2. **Q-D10 (Chiu-Chao).** The contingency is fine. But E04 §2 Methods and
   H4c still say "Chiu-Chao corrected f1". Update that text before the
   freeze so the frozen page names what will actually run.

Minor, not blocking: `runs.csv` shows `+dirty` for E01-R002–R008 and
E00-R004, while the manifests say clean. I assume `notebook.py` records
the commit at registration, when `notebook/` is dirty. It would help to
make `notebook.py` ignore `notebook/` and `results/` like `manifest.py`
does, so a reviewer doesn't have to check this.

## 2. E01 R001–R009: approve as run

Approve. The verdicts follow §2 as written, the exploratory runs are
labelled, and R008 replicated R007 on fresh seeds with a criterion fixed
beforehand. That is the right process.

Comments:

1. **H1d's sign matters for PH5, and the summary undersells it.**
   "Revisit found" (c = 2) gives +0.07, but "avoid found" (c = 0.5) gives
   −0.15. A red-team campaign whose later runs are told to find *new*
   holes behaves like c < 1, so it would make Ĉ *conservative*, not
   overstated. PH5's direction is therefore not a general claim; it
   depends on which way adaptation acts across runs. The paper text and
   PH5's wording should say so. See also §5 below.
2. **H1f's truth is not the truth E08 uses.** In §2a, π_i for family cells
   is "a run from a *new* family", averaged over the family effect. That is
   why one family overstates by +0.20. E08 defines π_i per level, from that
   level's own runs. These are different estimands, so H1f does not
   predict an effect for E08 as currently written (see §4).
3. **H1c.** Agree with FREEZE-V1 item 9: record the design flaw and don't
   re-run.

## 3. D-010 part A (realized-coverage interval): approve, with one condition

Approve as the primary interval. The argument (C is a property of the
sample, so the interval should target Ĉ − C) is right, and R008 is a
proper replication.

Condition: **R007/R008 never tested it below N = 50.** E09 has N = 14 and
E10 has N = 20, and D-010 B then proposes "interval covers C in ≥ 0.85 of
cells" for exactly those sizes. Please register a small exploratory run
(the R006 small-N cells, R008's method) before the freeze, so the 0.85
figure is calibrated at the sizes it will be applied to.

## 4. D-011: approve, and extend it to E08/E09/E10 (blocking)

Approve for E02 and E06. The reasoning is correct: if the evaluated runs
help estimate π̃, the items they found get inflated π̃, so the truth C is
biased upwards.

**The same bias is in my testbeds, in the frozen scripts.**
`crsafety.testbed.true_pi(X_all)` uses estimation + reference runs, and
`analysis/e08`, `e09` and `e10/analyse.py` all score against it. E10 §2
actually says "true π_i per arm: from 12 extra reference runs", so the
E10 script also disagrees with its own page. A quick back-of-envelope
simulation (Beta detectability, 3,000 replicates; not a registered run,
no testbed data involved):

| Design | Pooled truth − true C | Reference-only truth − true C |
|---|---|---|
| E10 (N = 20, 12 + 12 runs), Beta(1, 3) | +0.026 | 0.000 (sd 0.028) |
| E10, Beta(0.5, 2) | +0.033 | 0.000 (sd 0.036) |
| E08 (N = 16, 8 + 8 runs), Beta(1, 3) | +0.048 | 0.000 (sd 0.048) |
| E08, Beta(0.5, 2) | +0.054 | 0.000 (sd 0.061) |

The bias is as large as the PH4/PH5 effect we are testing (0.05) and
bigger than the proposed pooled tolerance for E09/E10 (0.03). It pushes
Ĉ − C *down*, so it biases PH4/PH5 towards "not supported" and PH1
towards a false "Ĉ is conservative". Proposal: for E08–E10, use the
reference runs only for π (E10's page already says this). Change
`testbed.true_pi` to take `X_ref`, and report the pooled version as
secondary, exactly as D-011 does for E02. Santosh, can you fold this into
D-011, or should it be D-013?

## 5. D-012 (E10 arm A3): agree with option A, but H10b is the bigger problem

On A3 itself, I agree with option A plus C. The faithful algorithm
over-corrects in R009, and we should let H10c fail honestly rather than
redesign it after seeing that. Thanks for catching that my §2
reconstruction was a no-op.

The bigger problem is upstream of A3. **H10b ("adaptive red teams
overstate coverage") is close to null by construction** in E10 as
written:

- Each A2 run is a separate session that adapts *within* itself. No
  session sees another session's finds, so across runs the detections are
  still independent draws given the blind spot.
- The truth π_i is per arm, taken from A2's own reference runs.
- Independent runs scored against their own catch rate is exactly E01's
  clean case, where Ĉ is unbiased (H1a, |bias| ≤ 0.009).

So within-session adaptation changes *which* blind spots A2 can find,
which shows up in π_i, not as bias in Ĉ against π_i. E01's c = 2 effect
needs cross-run behavioural response, and E10 has none. The same logic
applies to E08: L0's runs share a model, but are scored against L0's own
π, so PH4 is also near null (§2 comment 2).

The claim the paper wants ("an adaptive red team thinks it's done when it
isn't") needs a truth that doesn't come from the catcher being judged.
For the freeze, I'd make this co-primary for H10b and H8 (PH4):

- E10: π_i from the pooled reference runs of all arms (or the A1 + A5
  reference runs), with arm-specific truth kept as secondary.
- E08: π_i from the L3 (most diverse) reference runs, which matches E01
  H1f's "new family" estimand.

This is my page, so I'll write it up as a proposal for E08/E10 §2. But I'd
like Santosh's view on whether `analyse.py` can take a `--truth` option
(own / pooled / named cells) so the frozen script covers both.

## 6. E04 §2a and pilot R003: prefer option 3 over option 2

The pilot is useful: it shows the generator, not the matcher, decides H4a.
The ratio 3.4–3.6 is what you'd expect: 0.2 × 8 = 1.6 splits per feature,
times about 1.5 extra clusters each, gives about +2.4.

But I don't agree with option 2. Scoring H4a only on plain and absorbed
latents removes the very failure E04 exists to test (one real failure
mode reported as many, the Kunin et al. case). Choosing that after seeing
a pilot where H4a fails looks like moving the goalposts.

The real flaw is that every split is drawn fresh in each run (new λ, new
r), so split pieces can never match across runs. Real SAE splits across
seeds tend to recur. **Option 3** (take split geometry and recurrence
from E02: how often the same parent splits the same way across seeds) is
the honest fix. It can still fail H4a, which is fine. I'd add option 1's
numbers as secondary.

Two more points:

- **H4c is one-sided.** "≤ 1.5 when uncorrected > 2" is passed by the
  ghost correction at 0.72–0.75, which *over-corrects* by about 25%.
  Please make it two-sided (e.g. 0.67–1.5) before the freeze.
- **Ĉ is 0.74–0.81 against a true 1.** Splitting makes coverage
  conservative, which is a paper-worthy result for §3 (splits look like
  missing mass). Worth an exploratory line in the page.

The attack arm (E04-R002, mine) inherits the same question for
paraphrased strategies. I'll check it in the E10 judge pilot.

---

## Positions on the freeze items that follow from this review

- **Item 1 (PH1 † for E09/E10).** Not as proposed. E09 has 3
  configurations and E10's H10a has one arm (A1). With per-cell
  sd(Ĉ − C) of 0.06–0.14 at these sizes (R006), the standard error of a
  3-cell mean is about 0.05, so a 0.03 pooled tolerance can't be decided,
  and "≥ 0.85 of cells" over 1–3 cells is a coin flip. Counter-proposal:
  pool Ĉ − C over cells *and* items with a bootstrap CI. Supported if the
  95% CI lies within ±0.10, not supported if it excludes 0 by more than
  0.05 in either direction, inconclusive otherwise. And say plainly in
  the prereg that E09/E10 are underpowered for PH1, and that E02/E06
  carry the PH1 claim.
- **Item 3 (PH3a = 2, PH4 = PH5 = 0.05).** Agree with 0.05 as the minimal
  meaningful effect, only if §4 and §5 above are fixed. Otherwise the test
  has almost no power whatever the threshold. Also report the minimal
  detectable effect at N = 16/20 alongside it.
- **Item 10 (E10 A3).** Option A plus C (see §5). The design-based
  secondary should use the catcher-agnostic truth.
- **Items 2 and 8** are not covered here (still to draft).
