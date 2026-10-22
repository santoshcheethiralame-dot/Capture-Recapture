# Pilot simulation

A quick check of how standard closed-population estimators behave under the
assumption violations this project will face. Synthetic only: no SAEs or
red teams yet. Reproduce with:

```bash
pip install numpy scipy
cd pilot && python simulate.py > results.md
```

`estimators.py` has Chapman (Lincoln-Petersen), Darroch's Mt MLE, Chao2,
iChao2 and the first- and second-order jackknife for incidence data.
Full numbers are in [`results.md`](results.md). Each cell is the median of
`N_hat / N - 1` over 200 replicates with N = 2000.

## What it shows

1. **Uneven catchability biases everything downwards, and more runs help.**
   With logit-normal heterogeneity (sigma = 2), Chapman is 48% low whatever
   you do; Chao2 goes from -28% at K = 5 to -18% at K = 10; jackknife-2 to -9%.
   With only two runs, no estimator can fix heterogeneity.
2. **Under a heavy tail, total N is the wrong target.** With Zipf-like
   catchability (alpha = 1) the runs see 1 to 5% of the population and every
   estimator is 80 to 99% low. This is the regime SAE features are likely in
   (feature frequencies look power-law). Report coverage, or "how many new
   items would K more runs find", instead of N. Those are well posed.
3. **Similar catchers act like heterogeneity.** When all six runs come from
   one "family" (shared individual effects), Chao2 is 22% low; spreading the
   same six runs over six families brings it to -2%. Chapman on a
   cross-family pair is far better (-8%) than on a same-family pair (-45%).
   Design lesson: diversify the catchers, and treat the family as a stratum.
4. **Identity errors can swamp or mask the signal.** Recording 15% of
   captures as new "ghost" individuals (false non-matches when matching
   features or attacks) turns Chao2 from -14% to +43%, because ghosts are
   singletons. 5% ghosts happen to cancel the heterogeneity bias (+1%):
   a right answer for the wrong reason, which only a planted ground truth
   would catch. False merges push estimates further down.

These match what the statistics literature predicts (see
`research/`), and they say the project's validation phase has to vary
heterogeneity, tail weight, catcher similarity and matching error
separately.
