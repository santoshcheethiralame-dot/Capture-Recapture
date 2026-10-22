# Entry templates

## LOG.md entry

```markdown
## 2026-11-03

**Did:** Ran E01 base cell and heterogeneity block (E01-R001, E01-R002).
**Saw:** Coverage error ≤ 0.01 in every clean cell. Mt diverged in 4% of
sigma = 2, K = 3 replicates (recorded as failures, not dropped).
**Surprised by:** Jackknife-2 overshoots by 15% under homogeneity at K = 20.
**Next:** Dependence block. Check that the negative-dependence generator
really gives odds ratio 1/3 (add a test).
```

## DECISIONS.md entry

```markdown
## D-00X: Short title (YYYY-MM-DD)

**Status:** accepted | superseded by D-00Y
**Context:** What forced a choice.
**Options:** A, B, C, with one line each.
**Decision:** What we chose.
**Why:** The reason, with evidence (run IDs, papers).
**Consequences:** What this commits us to, and what we give up.
```

## DEVIATIONS.md entry

```markdown
## V-00X: EXX, short title (YYYY-MM-DD)

**Pre-registered:** Quote the frozen text.
**Actual:** What we did instead.
**Why:** Reason. Was it before or after seeing confirmatory data?
**Impact:** Which hypotheses and results are affected, and how the paper
will report it.
**Re-frozen:** commit / hash, or "no".
```
