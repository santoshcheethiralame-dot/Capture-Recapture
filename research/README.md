# What did we miss? Capture-recapture for safety tools

**Research dossier for idea 3** · 22 October 2026

This dossier collects what the literature says about the project, what it
changes in the proposal, and which experiments to run first. It draws on 11
research reports (about 400 searches across statistics, ecology, epidemiology,
software engineering, security, interpretability and AI safety) and a small
simulation. The full notes are in [`notes/`](notes/), the pilot code is in
[`../pilot/`](../pilot/), and the reading list is in
[`reading-list.md`](reading-list.md).

> **Caveat.** The research agents could not open PDFs. Everything came through
> a search tool that returns abstracts, snippets and its own reading of each
> paper. Numbers marked *(check)* came from secondary sources. Read the paper
> before you rely on one.

---

## The short version

1. **The idea is still open, but the margin is thin.** No one has estimated
   what SAEs, red teams or auditors missed from the overlap between
   independent runs. The closest work appeared in the last eight weeks:
   - Two pre-registered GitHub studies by Parit Kansal (October 2026). One
     applies capture-recapture to MMLU label errors. The other applies Chao
     estimators to planted ML failures.
   - Gerasimov et al. (June 2026), who measure per-feature "stability"
     across SAE seeds.
   - Ghosh et al. (14 Oct 2026), who show cross-seed reproducibility rising
     from 2% to 29% with training data.

   Move fast on Phase 1, and frame the paper as a *validation and failure
   map*, not "first use of ecological estimators in ML". That claim is
   already taken by Mark-Evaluate (2020), STADS (2018) and others.
2. **Total N is the wrong headline.** If catchability varies between
   individuals, the population size cannot be identified at all (Link 2003;
   Mao and Lindsay 2007). Chao-type numbers are lower bounds, and their
   confidence intervals cover the bound, not N. Two quantities are well
   posed even under heavy tails:
   - **sample coverage**: the share of discovery mass already found;
   - **expected new finds from K more runs**.

   Our pilot and Kansal's study both confirm this.
3. **Identity matching is the data, not a nuisance.** False non-matches
   create "ghost" singletons that inflate Chao estimates fast: a 10% miss
   rate raised Chao1 by 24% in one simulation. The matching threshold can
   change the estimate by orders of magnitude. Ecology, microbiology and
   census practice all solve this the same way:
   - measure the error rates on a labelled subset;
   - sweep the threshold and look for a plateau;
   - correct the singleton count.
4. **AI catchers are positively dependent, and that biases estimates
   downwards.**
   - Same-family LLMs share about 60% of their errors.
   - A panel of 9 LLM judges carries about 2 effective votes.
   - 4,000 generated research ideas contained about 200 unique ones.

   Heterogeneity, dependence and adaptive search all push estimates down,
   so read every estimate as a lower bound. The fix is design: diverse
   catchers, the family as a stratum, and runs that cannot see each other.
5. **Use many cheap runs, not a few expensive ones.** The software-inspection
   literature found no model accurate with fewer than 4 inspectors. Kansal's
   label-error study, with 3 or 4 detectors, got well-calibrated intervals
   that were useless: 102 to 797 for a truth of 181. Plan K ≥ 6 for any
   claim and K = 10 to 20 for the validation work.
6. **Phase 1 can start this week without training anything.**
   [SynthSAEBench](https://arxiv.org/abs/2602.14687) (Chanin and
   Garriga-Alonso) publishes:
   - a synthetic world with 16,384 known features and Zipfian firing rates;
   - an SAE zoo with 5 architectures × 5 seeds × 7 sparsity levels,
     trained on that world.

   That gives replicate catches with known truth, ready to analyse.
7. **Phase 3 has a known-truth testbed:**
   [AuditBench](https://arxiv.org/abs/2602.22755) has 56 model organisms
   with 14 planted behaviours. Its paper ran the investigator agent 16
   times per target per tool configuration. We would re-run it, since
   per-run logs do not appear to be public. Other known-truth sets with
   many runs:
   - BAITBENCH (planted reward-hack shortcuts);
   - SLEIGHT-Bench (40 monitor-evasion attacks, half never caught);
   - Tensor Trust (the only public attack corpus with attacker IDs).
8. **The precedents with real failure records are software inspections,
   fuzzing and epidemiology.**
   - **Inspections:** estimates ran low and often failed to support
     decisions, so practice never adopted them.
   - **Fuzzing:** adaptive samplers make estimators "vastly" underestimate
     risk. A de-adaptation fix exists (Liyanage et al. 2024).
   - **Epidemiology:** Dutch tuberculosis estimates of the missed fraction
     were about 5× too high until linkage errors and false positives were
     corrected.

   Copy their validation designs and avoid their mistakes.

---

## 1. Novelty and positioning

### Closest prior work

| Work | What it did | How close | What we do differently |
|---|---|---|---|
| **Kansal, `label-error-capture-recapture`** (GitHub, Zenodo DOI, Oct 2026; pre-registered, MIT) | Capture-recapture over 3 to 4 LLM judges plus confident learning on MMLU-Redux label errors (truth 181). Intervals covered the truth 97% of the time but were too wide to help. Its point estimate was further from the truth than counting the union. | **Same method, different target.** The closest "multi-detector" precedent, and an honest negative result. | Safety discovery tools; many cheap runs (K of 10 or more); identity by similarity matching; dependence and adaptivity modelled. Its failure (few detectors, thin overlap) is our design input. |
| **Kansal, `undiscovered-failures`** (GitHub, Oct 2026; pre-registered) | Chao1, ACE, jackknife and Chao-Jost coverage on planted and natural failure types of tabular classifiers. The unseen share was unbiased in 95.6% and 100% of cells; the number of types was a lower bound only. | **Same estimators, single sample.** No replicated runs, no matching. | Replicated independent runs (true capture-recapture), real safety tools, matching error. Use its coverage estimator as the baseline that multi-run designs must beat. |
| **Gerasimov et al. 2026**, [2606.12138](https://arxiv.org/abs/2606.12138) | Per-feature probability that a feature reappears in another seed; stable features are frequent and carry most signal, unstable ones sit in reproducible low-rank subspaces. | **Closest SAE work.** "Stability" is in effect a capture probability. | They never estimate what was missed and do not validate against truth. Their matching threshold is unvalidated, per one review. |
| **Ghosh et al. 2026**, [2610.20680](https://arxiv.org/abs/2610.20680) (14 Oct) | Strictly matched features across seeds rise from 2% (5M tokens) to 29% (50M) on Gemma-2-2B. | Raw ingredient. | Shows catchability depends on training budget, so estimates must be indexed by budget. |
| **Paulo and Belrose 2025**, [2501.16615](https://arxiv.org/abs/2501.16615) | About 30% of latents shared across seeds (131K SAE, Llama 3 8B); about 42% on Pythia-160M. | Raw ingredient. | The canonical "overlap" number; no estimate of the unseen. |
| **Sharkey, Braun, Millidge 2022** (LessWrong) | Compared dictionaries of different sizes with MMCS; proposed heuristics for the true feature count and found them hard to apply. Anthropic's May 2023 update found a "bounce" at the true count on toy data. | Earliest attempt at "how many features". | No probabilistic model, no uncertainty, toy data only. |
| **STADS** (Böhme 2018) and follow-ups (FSE 2021, ICSE 2023/24, ICSE 2026) | Software testing as species discovery: Good-Turing discovery probability, Chao richness, adaptive-bias corrections. | Closest methodology for red teams. | Not applied to LLMs or to multiple independent campaigns as occasions. |
| **Mark-Evaluate** (Mordido and Meinel, COLING 2020) | Petersen, CAPTURE and Schnabel estimators as text-generation metrics. | Earliest ML use of mark-recapture. | Different goal (a quality score). Rules out a "first in ML" claim. |
| **KnowSum** [2506.02058](https://arxiv.org/abs/2506.02058), **semantic alphabet size** [2509.14478](https://arxiv.org/abs/2509.14478), **SHADE** [2604.19162](https://arxiv.org/abs/2604.19162), **Blind-Spot Mass** [2604.05057](https://arxiv.org/abs/2604.05057) | Good-Turing and smoothed Good-Turing on LLM outputs: knowledge counts, uncertainty, deployment coverage. | Same estimator family. | All single pooled samples; none are safety discovery tools. |
| **NOVA** [2605.15219](https://arxiv.org/abs/2605.15219) | Theory: Good-Turing is "a local batch-diversity diagnostic, not an estimator of the historically undiscovered valid mass"; false positives cause a "contamination trap". | **A theoretical objection** to Phase 3. | Test it empirically; define a closed, verified, catchable population. |
| **STING** [2602.16346](https://arxiv.org/abs/2602.16346), **Kaur** [2607.21735](https://arxiv.org/abs/2607.21735), **SCARCE** [2606.29623](https://arxiv.org/abs/2606.29623) | Red-team discovery curves (time to first jailbreak); "evidential ceilings" of red-team null results; rare-event rate estimation. | Same motivation. | None counts unseen attack types. |
| **Technology-assisted review**: Bron et al. [2404.01176](https://arxiv.org/abs/2404.01176) | Chao's estimator as a stopping rule for document review. Mean recall was 95.9% against a 95% target, but the target was met in only 69.9% of runs *(check)*. | Deployed precedent for "how much did the search miss". | Lesson for reporting: give the per-run success rate, not the mean. |

### Positioning

- **Claim:** the first validation, against known truth, of capture-recapture
  and coverage estimators for AI-safety discovery tools, with a map of how
  they fail, and a reporting standard of the form "we found n, coverage is
  C, and K more runs would find about m more".
- **Do not claim:** first use of species estimators in ML, or an estimate of
  "the total number of features".
- **Scoop risk is real on the SAE side.** Several groups (Gerasimov et al.,
  Paulo and Belrose, Chanin) have the cross-seed matching code. Publish
  Phase 1 as a preprint early, and run a final scoop check before posting.
- **Possible collaborators or reviewers:** David Chanin (SynthSAEBench),
  Marcel Böhme (STADS), Gonçalo Paulo and Nora Belrose, the Gerasimov et al.
  group, the AuditBench authors, Anne Chao's group, and Parit Kansal (who
  might welcome a joint follow-up).

---

## 2. Six findings that should change the proposal

### 2.1 Report coverage first; give N only as a lower bound

**Evidence.**
- **Theory: N is not identifiable under heterogeneity.**
  - Link (2003): models that fit equally well give very different N.
  - Holzmann, Munk and Zucchini (2006): N is identified only once you
    restrict the family of heterogeneity distributions.
  - Mao and Lindsay (2007): only one-sided (lower) confidence limits are
    possible.
  - Haegeman et al. (2013): richness cannot be estimated without
    assumptions about the tail.
- **Our pilot** ([`../pilot/results.md`](../pilot/results.md)):
  - Observed Chao2 matches its noise-free population bound to within 1 to 2
    points in every scenario. Under logit-normal heterogeneity (σ = 2,
    K = 10) Chao2 is 18% low and so is the bound, so no estimator can do
    better.
  - With Zipf-like catchability (α = 1), runs see 1 to 5% of N and every N
    estimator is 80 to 99% low. Estimated coverage is still within 0.02 of
    the truth, and the predicted number of new finds from doubling K is
    within 2 to 13%.
- **Confidence intervals:** the standard log-normal Chao interval covered
  the bound 94 to 99% of the time and N only 0 to 3% of the time under
  real heterogeneity (note A).
- **Kansal (`undiscovered-failures`):** the unseen *share* was estimable,
  the *number* of types only as a lower bound.
- **Fuzzing (Liyanage et al., ICSE 2023):** every richness estimator showed
  "false peaks", with no asymptote on 31 of 32 programs. Missing mass was
  the reliable quantity (Lee and Böhme, ICLR 2025).
- **Real SAE spectra look heavy-tailed.** Latent firing frequency follows a
  power law with exponent about -1.0 to -1.2, and the tail falls even
  faster ([2505.00190](https://arxiv.org/abs/2505.00190)). The quantization
  model suggests a Zipf-like spectrum of underlying "quanta".

**Change.** Make the primary outputs:
1. sample coverage (Chao-Jost) with a bootstrap CI;
2. the expected number of new finds from 1× and 2× more runs. Do not
   extrapolate past about log n (Orlitsky, Suresh and Wu 2016).

Report Chao2 or iChao2 as an explicitly labelled lower bound, with f1, f2,
f3 and f4 printed. Weighted "effective numbers" (Hill numbers of order 1
and 2) are estimable where richness is not, and are worth adding. For SAEs,
coverage weighted by activation mass is closer to what matters for safety
than a count of features.

### 2.2 Treat matching as measured, modelled and swept

**Evidence.**
- **Pilot:** 15% ghost captures move Chao2 from -14% to +42%. 5% ghosts
  happen to cancel the heterogeneity bias, a right answer for the wrong
  reason.
- **Note B's simulations** (N = 500, K = 5):
  - A 10% false non-match rate raises Chao1 by 24%; 30% nearly doubles it.
    False matches move it only about 4%.
  - In the low-overlap two-run regime it is the other way round: a few
    false matches deflate Lincoln-Petersen sharply.
- **Note B's threshold sweep:** with clean features, N is stable across a
  plateau of thresholds. With noisy features there is no plateau, and Chao1
  runs from about 1,000 to over 300,000 as the threshold rises. The shape
  of the curve shows whether any threshold can be trusted.
- **Ecology:**
  - Eight observers identifying snow leopards misclassified 12.5% of
    occasions and inflated abundance by 35 ± 21% (Johansson et al. 2020).
  - Automated photo-ID software has inflated N by up to 920% *(check)*.
- **Epidemiology:** the Dutch tuberculosis under-notification estimate fell
  from 36.8% to 7.3% after correcting for linkage errors and false-positive
  records (van Hest et al. 2007).
- **Microbiology:**
  - Sequencing a single E. coli template "found" many species (Kunin et
    al. 2010).
  - Denoising that deletes singletons makes Chao1 meaningless (ISME J 2024).
  - Chiu and Chao (2016) correct f1 using f2, f3 and f4.
- **Estimating the error rate from the capture data alone is fragile.**
  Latent-multinomial models show 30 to 40% bias at low recapture (Fraysse
  et al. 2023). Misidentification and heterogeneity are nearly confounded
  (MARK book).
- **Choosing the "species" sets the answer:**
  - Si et al. counted 200 unique ideas out of 4,000 at cosine 0.8.
  - In Best-of-N jailbreaking, every augmented prompt is a singleton;
    merged by base prompt, the count is capped.
  - In TDC 2023, recall of the planted triggers was about 0.16 while about
    0.99 of the triggers found still worked.

**Change.**
1. **Two-view matching.** For SAEs, combine decoder cosine with activation
   correlation (as in bilateral photo-ID). For attacks, combine a rubric
   label with an embedding or judge. Fit a Fellegi-Sunter-style mixture to
   get match probabilities.
2. **Labelled subset.** Estimate the false-match and false-non-match rates
   on a labelled subset, stratified by score bin. In synthetic worlds they
   are known exactly.
3. **Sweep and report.**
   - Sweep the threshold and plot N, coverage, f1/S and cluster count
     against it.
   - Report the plateau, or the absence of one.
   - Give estimates at several identity granularities (family, technique,
     instance), as in the DOTUR plots of microbial ecology.
4. **Robust alternatives.** Use estimators that do not need f1
   (`breakaway_nof1`, ratio regression), the Chiu-Chao singleton
   correction, and multiple imputation over plausible matchings.
5. **Mandatory sub-experiment: the "Kunin test".** Feed one planted
   feature or attack, expressed many ways, through the whole pipeline. A
   correct pipeline reports N = 1.

### 2.3 Design for independence; measure the dependence that is left

**Evidence.**
- **Correlated LLMs:**
  - Kim et al. ([2506.07962](https://arxiv.org/abs/2506.07962)): models
    agree about 60% of the time when both are wrong, more within a company.
  - Goel et al. ([2502.04313](https://arxiv.org/abs/2502.04313)): more
    capable models have more correlated errors.
  - Kohli ([2605.29800](https://arxiv.org/abs/2605.29800)): 9 judges from 7
    families give about 2 effective votes.
  - Artificial Hivemind ([2510.22954](https://arxiv.org/abs/2510.22954)):
    high similarity across models, and temperature does not fix it.
- **Mode collapse:** in MonitoringBench, 81% of Opus 4.6 attacks fall into
  2 of 5 tiers *(check)*.
- **Software and epidemiology:**
  - Inspection meetings break independence.
  - With two lists, dependence and heterogeneity cannot be separated (Chao
    et al. 2001).
  - In the Verona diabetes study, two list pairs gave 87.5% and 45.9%
    completeness for the same truth.
- **Negative dependence is the dangerous case.** If later runs are steered
  away from earlier finds, the estimate can be badly *over* (Brenner 1995).
- **Adaptivity:** a red team that learns from the monitor's verdicts is a
  greybox fuzzer. Estimators built for non-adaptive sampling
  "systematically and substantially under-estimate" risk (Böhme et al.,
  FSE 2021). Liyanage et al. (ICSE 2024) removed most of this bias by
  re-simulating non-adaptive campaigns from the collected data.
- **In SAEs, dependence is partly mechanistic.** Spurious local minima
  ([2512.05534](https://arxiv.org/abs/2512.05534)) and the
  identifiability limits of Cui et al.
  ([2506.15963](https://arxiv.org/abs/2506.15963)) mean that some features
  are missed by every seed. Shared data order and shared initialisation
  also create artificial recaptures (the "Ablating Archetypes" critique).

**Change.**
- **Make catchers differ as much as possible.** Vary base family, base or
  SFT versus RLHF, scaffold and tools, persona, and data stream. Vary seed
  last, since it matters least.
- **Treat each family as a stratum.** Never let runs see each other.
- **Report a dependence diagnostic with every estimate:**
  - the effective number of independent catchers (Kish n_eff);
  - pairwise observed-over-expected overlap;
  - Lincoln-Petersen for every run pair, plus drop-one-run trajectories;
  - log-linear models with interaction terms when K ≥ 3 (`Rcapture`,
    `dga`, `SparseMSE`).
- **Use a dependence-robust interval** ([2008.00127](https://arxiv.org/abs/2008.00127))
  as the honest interval.
- **"Anchor stream".** Add one deliberately dumb, non-adaptive random
  attacker as an independent list.

### 2.4 Plan for many runs

**Evidence.**
- Briand et al. (2000): no model was accurate with fewer than 4
  inspectors, and the Mh jackknife was the most robust.
- Kansal's label-error study (3 to 4 detectors) was calibrated but useless.
- Nasr et al. ([2311.17035](https://arxiv.org/abs/2311.17035)) called their
  own Good-Turing memorisation estimate "exceptionally poor": it needed
  about 500M extractions to converge *(check)*.
- LCMCR's default settings are not identified unless there are at least 10
  lists (Aleshin-Guendel 2020).

**Change.** Plan K = 10 to 20 runs in validation and K ≥ 6 for any headline.
Before collecting data, run a power check of expected interval width at the
intended K and N. Use decision accuracy as a metric: does the estimate make
the right call between "keep searching" and "stop"?

### 2.5 Define the estimand before you estimate

**Evidence.**
- **SynthSAEBench** at width 4,096 cannot represent 12,288 of its 16,384
  true features. Does an estimator target 4,096, the recoverable set, or
  16,384?
- **SLEIGHT-Bench:** 20 of 40 attacks were never caught in 10 monitor
  trials.
- **AuditBench:** context-dependent behaviours (secret loyalty, data
  poisoning) are often never elicited.
- **Theory and the census:** correlation bias in the census, and the
  "shared blind spot" argument, mean the class nobody can find is invisible
  to every estimator.
- **Other gaps between "planted" and "real":**
  - In Kansal's study, planted errors were much easier to find than real
    ones.
  - TDC 2023 shows "planted" and "anything that works" are different
    populations.

**Change.** Every number is "within the population catchable by this class
of tool at this budget". For SAEs, define three truths:
1. all true features;
2. features that fired at least c times in training;
3. features recoverable by an oracle union of many seeds.

Score estimators against each. Include an injected "uncatchable" class in
every testbed and report how far below the truth the estimators fall.

### 2.6 Catchability has measurable covariates; use them carefully

**Evidence.**
- **What predicts catchability:**
  - Stable SAE features are frequent; unstable ones are rare, surface-form
    triggers (Gerasimov et al.).
  - The chance that a concept gets its own feature tracks the concept's
    frequency (Templeton et al. 2024).
  - In AuditBench, how hard a behaviour is to find depends on the training
    method.
- **Covariate models work only when the covariate does the work** (note A):
  - **Huggins / Horvitz-Thompson:** unbiased when the covariate fully
    explains catchability (+1%).
  - **With residual heterogeneity:** 32 to 45% low.
  - **With a misspecified link on a power law:** 42% high.

**Change.** Use firing frequency, activation norm, nearest-neighbour cosine
(a sign of splitting or absorption) and attacker family as covariates.
Prefer Böhning's generalised Chao, which keeps the lower-bound property.
Check every covariate model against synthetic truth first.

---

## 3. Updated design, phase by phase

### Phase 1: synthetic SAEs (the paper's core)

**1a. Zero-training pilot (days).**
- **Data:** the SynthSAEBench zoo
  (`decoderesearch/synth-sae-bench-16k-v1-saes`): 5 architectures × 5 seeds
  × L0 15 to 45, width 4,096. Ground truth: 16,384 features in the v1 world.
  The SAEs were trained on v1, which has a known magnitude-scaling bug that
  v2 fixes, so evaluate them against v1.
- **Two capture histories per SAE:**
  1. an *oracle* history, matched to true features;
  2. a *cross-seed* history, from Hungarian decoder-cosine matching plus
     connected components.

  Comparing estimates from the two separates matching error from
  heterogeneity bias.
- **Estimators:** Chapman for each pair, Chao2, iChao2, jackknife, coverage
  and extrapolation (all in `pilot/estimators.py`).
- **Targets:** N_all = 16,384, N_in = 4,096, and N_rec, the set recovered by
  the union of all seeds.

**1b. Your own worlds and seeds (weeks; one small GPU).** Use the SAELens
generator (v2) and train 10 to 20 seeds per cell. Factorial design:
- tail: Zipf α ∈ {0.8, 1.0, 1.2, 1.5}, plus a log-normal arm and a truncated
  arm;
- hierarchy and correlation: off, then on;
- width relative to the number of true features: 0.25× to 4×;
- L0 relative to the true L0: 0.5×, 1×, 2×;
- seed varies initialisation only, data order only, or both;
- training budget.

Start with hierarchy and correlation **off** to validate in the clean
regime, then switch each on to measure the damage from absorption and
hedging.

**1c. Matcher bake-off.** Score each matcher's precision and recall against
true identity, across thresholds:
- decoder-cosine Hungarian;
- the strict rule (encoder and decoder matches agree);
- activation correlation (Lan et al.);
- semantic optimal transport ([2605.28567](https://arxiv.org/abs/2605.28567));
- mutual nearest neighbour.

The result is publishable on its own.

**Controls and comparators.**
- **Controls:**
  - permuted-decoder and random-init SAEs from Chanin's
    reliability-audit repo, as the null recapture rate;
  - the oracle SAE, as perfect catches;
  - deduplication of dead and antipodal latents.
- **Comparators:**
  - the rate-distortion "bounce" heuristic (Anthropic, May 2023);
  - the union-of-seeds accumulation curve against K;
  - reconstruction-based heuristics, to show loss is uninformative.

### Phase 2: real models

- **Train your own replicate seeds.** No public suite of real-LM SAEs has
  seed replicates, so train them on Pythia-70M/160M or GPT-2 small, with
  independent versus shared data order. Report estimates by training budget.
- **Gemma Scope / Gemma Scope 2** width and L0 ladders: use them only as
  *nested, dependent* occasions, and say so. Compare the
  width-accumulation curve with the seed-based estimate.
- **Known-subpopulation validation:**
  - Karvonen et al.'s board-game SAEs (500+ per game; coverage 0.48 chess
    and 0.52 Othello against supervised features);
  - OthelloGPT probes (9 of 180, later 33 of 180, features found).

  The researcher-specified features act as marked animals.
- **Null:** SAEs trained on a randomly initialised transformer (Heap et al.)
  give the recapture rate of structure that is reproducible but meaningless.
- **Invariance check without truth** (borrowed from fuzzing): change the
  sampling unit (seed vs width, threshold, layer) and check the estimate
  does not drift.
- **Frequency strata:** estimate per frequency band and per safety-relevant
  class. For example: how much of the deception-related feature mass have
  we found?

### Phase 3: audits, red teams and automated researchers

Ranked starting points. The first four have known truth.

| # | Testbed | Design | Status |
|---|---|---|---|
| 1 | **AuditBench** ([2602.22755](https://arxiv.org/abs/2602.22755)) | (a) Individuals = 56 targets (N known), occasions = 16 investigator runs. Does Chao2 predict how many targets were never solved? (b) Individuals = distinct hypotheses across runs (open population; the planted behaviour is the known member). | Models, agent and eval framework released; per-run logs probably not, so re-run (Haiku 4.5 agent, cheap; 70B LoRA targets need serving). |
| 2 | **BAITBENCH** ([2608.30724](https://arxiv.org/abs/2608.30724)) | Planted reward-hack shortcuts; 7 agents; 57.1% of runs hack; transcripts reportedly released. Occasions = runs, individuals = hack types. | *(check)* release and run count. |
| 3 | **SLEIGHT-Bench** ([2605.16626](https://arxiv.org/abs/2605.16626)) | 40 attacks × 10 monitor trials; 20 never caught. A stress test for the class that is never caught. | Gated on Hugging Face; licence unclear. |
| 4 | **Multi-quirk model organism** (build it) | Plant 5 to 10 quirks in one model (merge AuditBench LoRAs, or use synthetic-document fine-tuning); run investigator, Petri and Bloom many times. The first real richness test with N > 1 per target. | Does not exist; we would build it. |
| 5 | **Planted-strategy control setting** | BashArena or LinuxArena side tasks; a planted menu of attack strategies; K attacker models × prompts; strategy labelled by a judge validated on human-labelled data. Arms: **non-adaptive vs adaptive vs de-adapted** (Böhme's correction), and mode-collapsed vs diversity-prompted vs human (LaStraj). | New compute. The core Phase 3 experiment. |
| 6 | **Super-agent replication** | Reproduce the 13% → 42% pooling effect from Anthropic's 2025 auditing agents. Compare pooled success with 1-(1-p)^k and with a beta-binomial. "Captured" is not the same as "recognised". | Number of runs pooled not published. |
| 7 | **Tensor Trust** | The only public attack corpus with attacker IDs. Defences as sites, attackers as occasions, attack text available for matching. | Public; licence unconfirmed; attackers saw each other's results, so they are not independent. |
| 8 | **MALT, ImpossibleBench, the reward-hacking paper [2609.28614](https://arxiv.org/abs/2609.28614)** | Reward-hack catalogues. In 2609.28614, some hack types (scorer tampering, metric fabrication) evade detection 8 to 12× more often *(check)*: an "undetected class" with labels. | Varies. |
| 9 | **WildTeaming** (105K tactics → 5.7K clusters at cosine 0.75) | Species curves and threshold sensitivity on real jailbreaks. No truth. | Public. |

**Cheap side applications** (no GPU, good for a first week):
- Si et al.'s idea-generation saturation as a free accumulation dataset.
- Static analysers versus fuzzers on Magma: 112 known bugs, AFL++ found 37,
  CodeQL 31 ([2505.22052](https://arxiv.org/abs/2505.22052)).
- MMLU-Redux with K of 10 to 30 cheap detectors, to test whether more
  detectors rescue Kansal's negative result.

---

## 4. Experiment menu

Ordered by value for effort. Compute "CPU" means a laptop is enough.

| ID | Experiment | Tests | Data / compute | Effort |
|---|---|---|---|---|
| E1 | Pilot extensions: true list dependence (pairwise interaction), negative dependence, adaptive (Mb) runs, nested widths, small N (20 to 100), bootstrap and profile CIs | Which violations break which estimator, and in which direction | CPU | 2-4 days |
| E2 | SynthSAEBench zoo: oracle vs cross-seed histories, all estimators vs N_all, N_in, N_rec | Phase 1 core result at K = 5 | Download only | 1 week |
| E3 | Matcher bake-off and threshold sweep with plateau diagnostic | Identity error rates; whether any threshold can be trusted | SynthSAEBench | 1 week |
| E4 | Kunin test: one true feature or attack expressed many ways | Ghost-singleton inflation; singleton corrections | CPU / API | 2 days |
| E5 | Error-injection grid (false non-match rate f, false match rate g) with corrections: Chiu-Chao f1, f1-free estimators, multiple imputation, Di Consiglio-Tuoto linkage-corrected Petersen | Whether matching error can be corrected | CPU + synthetic | 1 week |
| E6 | Own seeds K = 10 to 20 over a grid of tail weight, hierarchy, width and budget | Bias against K, tail and structure; coverage calibration | 1 small GPU | 2-4 weeks |
| E7 | Huggins / Böhning with frequency covariates, first with true p_i, then noisy | Whether covariates rescue heterogeneity | Synthetic | 1 week |
| E8 | Catcher-similarity ladder: same model/seeds → personas → same family → different families → base vs RLHF → humans | Size of the dependence bias; how many effective catchers | API calls, planted truth | 2 weeks |
| E9 | AuditBench re-run: Chao on targets never solved; hypothesis-level richness | Known-truth audit validation | Haiku API + 70B serving | 2-3 weeks |
| E10 | Adaptive vs non-adaptive vs de-adapted attackers on planted strategies | Whether fuzzing's adaptive-bias fix transfers | Control setting | 3-4 weeks |
| E11 | Real SAEs: replicate seeds on Pythia/GPT-2; board-game known subpopulation; random-transformer null; invariance tests | Phase 2 | 1 GPU | 3-4 weeks |
| E12 | Multi-quirk organism plus repeated audits (investigator, Petri, Bloom) | Richness with N > 1 known | Fine-tuning + API | 4+ weeks |
| E13 | Stopping rule à la technology-assisted review: "stop adding runs when coverage ≥ X". Report the per-campaign rate of hitting the target, not the mean | Decision usefulness | Any of the above | 2 days on top |
| E14 | Head-to-head with forecasting (Jones et al.; Best-of-N power law): coverage-based vs tail-forecast prediction of success at 10× budget | Complement or competitor | Planted attacker | 1-2 weeks |

**Suggested first month:** E1 → E2 → E3 → E4 → E5. That alone is a
workshop paper: "Can we estimate what SAEs miss? A validation on synthetic
ground truth, and why matching decides the answer."

---

## 5. Reporting recipe

For every tool and setting, report:

1. K (runs), S_obs (distinct items found), f1, f2, f3, f4, and the matching
   rule and threshold.
2. **Coverage** (Chao-Jost incidence) with a bootstrap CI. **This is the
   headline.**
3. **Expected new items from 1× and 2× more runs**, with a CI.
4. **Chao2 or iChao2, labelled "lower bound"**, with its CI described as an
   interval for the bound.
5. Jackknife-2 or ACE as a neutral-to-pessimistic comparison.
6. Dependence diagnostics (n_eff, pairwise estimates, drop-one) and a
   dependence-robust interval.
7. Sensitivity: estimate against threshold or granularity; f1-free
   estimator; singleton-corrected Chao.
8. The estimand ("catchable by …, at budget …") and the known blind spots.

The full decision table (which estimator under which violation, and which
way the bias goes) is in [note A, section 6](notes/A-statistics.md#6-estimator-decision-guide-for-this-project).

**Software.**
- **R:** `Rcapture`, `iNEXT`, `SpadeR`, `breakaway`, `SPECIES`, `VGAM`
  (Huggins), `dga`, `SparseMSE`, `LCMCR` (keep latent classes ≤ K/2),
  `drpop`.
- **Python:** no maintained package exists. The core estimators are a few
  lines each (see `pilot/estimators.py`); call R through `rpy2` for the
  rest.

---

## 6. Risks

| Risk | What the literature says | Mitigation |
|---|---|---|
| Estimates are always low | Heterogeneity, positive dependence and adaptivity all bias downwards (inspections, fuzzing, epidemiology) | Lead with coverage; label N as a lower bound; quantify the gap on planted truth |
| Matching decides the answer | Ghosts inflate and merges deflate; the threshold can move N by orders of magnitude | Section 2.2: two-view matching, labelled error rates, sweeps, plateau diagnostic, corrections |
| Calibrated but useless | Kansal's label-error study: 97% coverage, intervals 4× the truth | Many cheap runs; power check up front; decision-accuracy metric |
| Synthetic results do not transfer | Planted errors are easier than real ones (Kansal); real activations have manifolds and dark matter | Several generator families, including misspecified ones; Phase 2 known-subpopulation checks |
| Scooped on Phase 1 | Gerasimov et al., Ghosh et al., Paulo and Belrose all hold the pieces | Preprint Phase 1 fast; cite and build on them |
| NOVA-style objection: Good-Turing is only local | Theory paper, May 2026 | Restrict claims to a closed, verified, catchable population; test NOVA's convex-cost prediction |
| Dual use (Phase 3) | A catalogue of monitor-evading strategies is sensitive | Publish strategy-level labels and counts, not payloads |

---

## 7. Check before relying on

These claims are central and were seen only in secondary sources or not
confirmed:

- SynthSAEBench zoo contents (number of files; whether seeds vary
  initialisation, data order or both), and the generator's α, p_min and
  p_max. Read the SAELens code.
- AuditBench: whether per-run predictions are released; the default agent's
  success rate (about 37%).
- BAITBENCH's run count (about 1,258) and its transcript release.
- MonitoringBench: the 81% concentration of attacks in 2 of 5 tiers; which
  taxonomy the final version uses.
- Nasr et al.'s Good-Turing figures (1.5M lower bound; about 500M samples
  to converge).
- Technology-assisted review: target met in 69.9% and 53.1% of runs.
- Photo-ID "920%" inflation (primary paper not identified).
- Tensor Trust licence; whether Gandalf files carry user IDs.
- The number of runs the 2025 Anthropic super-agent pooled (not published).

---

## 8. How this dossier was made

Two rounds of research agents (Sonnet), each given a fixed brief, plus
verification of the high-stakes claims (prior work, scoop risks, disputed
IDs) by the coordinating session.

- **Round 1 (seven topics):**
  - A: statistics;
  - B: identity errors and multiple systems estimation;
  - C: software and security precedents;
  - D: SAE features;
  - E: red teams and audits;
  - F: dependence and identity;
  - G: novelty check.
- **Round 2 (four gap-fillers):**
  - H1: machine-learning precedents and alternatives;
  - H2: red-team gaps;
  - H3: SAE gaps;
  - H4: validation evidence.

The pilot simulation was extended to match note A's review. Corrections
made after the notes were written are listed in
[`notes/README.md`](notes/README.md).
