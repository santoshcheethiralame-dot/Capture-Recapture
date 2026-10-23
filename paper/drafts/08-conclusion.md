# §8 Conclusion and recommendations (draft v0, Santosh, 2026-10-23)

> 0.25 page. Placeholders until §5 exists.

A list of findings says what a safety tool found, not what it missed. The
overlap between repeated, independent runs of the same tool says how
complete the search was, in a form that can be checked against known
truth. Across [pending: testbeds], coverage and the number of new findings
from more runs are estimable when runs are independent and the identity
rule is sound. The number of failure modes is not; it is only a lower
bound. The estimates fail in known directions:
- shared models, and adaptive search that revisits earlier finds,
  overstate completeness;
- findings split differently in each run understate it.

**Recommendations for labs reporting a safety evaluation.**
1. **Run the tool more than once, independently.** Use different seeds,
   and where possible different prompts or model families. Record what
   was shared between runs.
2. **Report coverage, not a count.** For example: "we found n failure
   modes; coverage is C (95% interval); K more runs would find about m
   more". Give any count as a lower bound.
3. **State the identity rule.** Say how two findings were judged to be the
   same, and how sensitive the result is to that rule.
4. **Report dependence.** Give the effective number of runs and the overlap
   between runs. Treat high overlap from shared models as a warning, not as
   reassurance.
5. **Stop on the lower bound.** If more runs are possible, stop when the
   one-sided lower bound of coverage reaches the target, not the point
   estimate [pending: E13].
6. **Say what "catchable" means.** Coverage is relative to what this tool,
   at this budget, can find at all.

We release the estimator library, the pre-registration, the lab notebook
and every detection history, so these numbers can be recomputed and the
methods applied to other tools.
