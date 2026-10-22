# Pilot simulation

A quick check of how standard closed-population estimators behave under the
assumption violations this project will face. Synthetic only: no SAEs or
red teams yet. Reproduce with:

```bash
pip install numpy scipy
cd pilot && python simulate.py > results.md
```

`estimators.py` has Chapman (Lincoln-Petersen), Darroch's Mt MLE, Chao2,
iChao2, the first- and second-order jackknife, Chao-Jost sample coverage, and
Chao et al. (2014) extrapolation for incidence data. Full numbers are in
[`results.md`](results.md). Each cell is the median of `N_hat / N - 1` over
200 replicates with N = 2000.

## What it shows

1. **Chao2 is a lower bound, and it hits its bound.** The "Chao2 bound" column
   is Chao2 computed from expected frequency counts, with no sampling noise.
   Observed Chao2 matches it to within a point or two in every scenario. So
   the -18% at sigma = 2, K = 10 is not estimator error. It is the part of N
   that nothing can recover under heterogeneity (Link 2003; Mao and Lindsay
   2007). Confidence intervals from Chao2 cover this bound, not N; never
   report them as intervals for N.
2. **Uneven catchability biases everything downwards, and more runs help.**
   With logit-normal heterogeneity (sigma = 2), Chapman is 48% low whatever
   you do. Its bias is about N / (1 + CV^2), which more runs cannot fix.
   Chao2 goes from -28% at K = 5 to -18% at K = 10, and jackknife-2 to -8%.
   With only two runs, no estimator can fix heterogeneity.
3. **Under a heavy tail, total N is the wrong target, and coverage is the right
   one.** With Zipf-like catchability (alpha = 1) the runs see 1 to 5% of the
   population and every N estimator is 80 to 99% low. The estimated sample
   coverage (section 5) is still within 0.02 of the truth, and the predicted
   number of new finds from doubling K is within 2 to 13%. It is about 20% low
   under logit-normal heterogeneity, where much of the mass has tiny p. This is
   the regime SAE features are likely in, since feature frequencies look
   power-law. Lead with coverage and "what K more runs would find", and give N
   as a labelled lower bound.
4. **Similar catchers increase heterogeneity.** When all six runs come from one
   "family" that shares individual effects, Chao2 is 21% low. Spreading the
   same six runs over six families brings it to -2%. Chapman on a cross-family
   pair (-6%) is far better than on a same-family pair (-45%). Strictly, this
   scenario raises the variance of a shared individual effect. It is not true
   list dependence (a two-way interaction between runs), and it does not test
   negative dependence or adaptive runs. Those still need simulating. Design
   lesson: diversify the catchers, and treat the family as a stratum.
5. **Identity errors can swamp or mask the signal.** Recording 15% of captures
   as new "ghost" individuals (false non-matches when matching features or
   attacks) turns Chao2 from -14% to +42%, because ghosts are singletons. 5%
   ghosts happen to cancel the heterogeneity bias (+1%): a right answer for
   the wrong reason, which only a planted ground truth would catch. False
   merges push estimates further down. Coverage moves the safe way under
   ghosts: it reads lower than the truth.

## Not yet covered

The research notes in [`../research/`](../research/) list what the full
Phase 1 simulation should add:
- true list dependence, both positive and negative;
- adaptive runs that learn from earlier finds;
- nested SAE widths;
- small N (tens of attacks);
- bootstrap and profile-likelihood intervals;
- matching by thresholded similarity rather than by injected error rates.
