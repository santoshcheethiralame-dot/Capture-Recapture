# Original proposal (idea 3 of "Six Research Ideas in AI Safety", 15 October 2026)

> Extracted verbatim from the source document. The research dossier in [README.md](README.md) updates several parts of it.

3\. What did we miss? Capture-recapture for safety tools

*Estimate the features, attacks and behaviours that safety tools never find.*

|                                                                                                                                                                          |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Question.** Safety tools report what they found: SAE features, red-team attacks, hidden behaviours. None of them estimate what they missed. Can we put a number on it? |

Why it matters

Ecologists count animals they cannot see by catching some, marking them, releasing them and catching again. How much the two catches overlap tells you the total population. With two catches the Lincoln-Petersen estimate is N = n1 x n2 / m, where m is the number caught both times. With more catches and some animals easier to catch than others, Chao's estimators and the Otis et al. model family handle the harder case. Software engineering has used the same idea for decades to estimate how many defects remain after code inspections (Eick et al., 1992).

The same structure appears all over AI safety:

- **SAE features.** SAEs trained with different seeds and sizes find different features (2502.04878). On synthetic data with known features, SAEs recover only a small fraction (2602.14111). Each SAE run is a catch; matching features across runs is the recapture.

- **Red-team attacks.** Monitoring benchmarks admit their red teams were under-elicited (2605.09684), and adaptive attacks keep finding new ways around monitors (2510.09462). Each red team is a catch; each attack strategy is an individual.

- **Audits.** Blinded teams found a hidden objective three times out of four (2503.10965), and a sandbagging blue team mostly failed (2512.07810). Each auditor is a catch; each hidden behaviour is an individual.

- **Automated research.** Automated alignment researchers produced reward hacks their designers did not predict (2608.28945; Anthropic's automated weak-to-strong researcher). Each run is a catch; each hack type is an individual.

What is missing

None of these papers estimate the unseen population. Without that number, "we found 12 attacks" says nothing about coverage.

|                                                                                                                                                                                                                                                                     |
|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Key move.** Validate first. The estimators assume independent catches, equal catchability and clear identities, and every one of these settings breaks those assumptions. So test the estimators where the true answer is known, then apply them where it is not. |

Proposed design

| **Part**                        | **Details**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|:--------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Phase 1: validation on SAEs** | Build a synthetic setting with a known number of features (a sparse linear generator in the style of toy models of superposition, or Korznikov et al.'s setup, 2602.14111; Chanin's synthetic SAEs, 2605.18229). Train K SAEs with different seeds and widths. Match features across runs by decoder cosine similarity and activation correlation. Estimate the population with Lincoln-Petersen, Chao's estimators and the jackknife, and compare to the true count while varying dictionary size and sparsity. |
| **Phase 2: real models**        | Apply the validated estimators to a real model with public SAEs (Gemma Scope on Gemma 2/3) or to SAEs you train on Pythia. Report the estimated feature population per layer and the coverage of a single SAE.                                                                                                                                                                                                                                                                                                   |
| **Phase 3: red teams**          | In a small control setting, plant a known set of attack strategies, run several independent attackers (different models and prompts), cluster what they find into strategy classes with a fixed rubric, and estimate the unseen count. Then run the same procedure where the truth is unknown.                                                                                                                                                                                                                   |
| **Metrics**                     | Estimated population with confidence intervals, estimator bias against truth, and coverage of a single run.                                                                                                                                                                                                                                                                                                                                                                                                      |

Why the answer is worth having

If the estimators hold up against truth, every safety paper that reports "we found N" can also report "and we estimate we missed M". If they fail, the paper maps exactly how they fail, which is still the first quantitative account of coverage for these tools.

Risks and how to handle them

| **Risk**                                                                                | **Mitigation**                                                                                 |
|:----------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|
| Identity matching drives everything: when are two features, or two attacks, "the same"? | Report results across a range of matching thresholds and show how sensitive the estimate is.   |
| Unequal catchability (some features are found by every run).                            | Use Chao's estimators and heterogeneity models built for it, and report where they still fail. |

Scope

- **Minimum version:** Phase 1 alone is a paper: "Can we estimate how many features SAEs miss?" About 4-6 weeks, mostly CPU and a small GPU.

- **Full version:** All three phases.

- **Week one:** Implement the estimators (a few dozen lines of Python, or the Rcapture package in R) and build the synthetic feature generator.

- **Compute:** CPU plus a small GPU

Attached papers (10)

**\[1\]** [Sanity Checks for Sparse Autoencoders: Do SAEs Beat Random Baselines?](https://arxiv.org/abs/2602.14111)

*Korznikov, Galichin, Dontsov, Rogov, Oseledets, Tutubalina, Feb 2026*

- **What it found:** On synthetic data with known features, SAEs recover about 9% of true features at 71% explained variance, and random-constrained baselines match trained SAEs on interpretability (0.87 vs 0.90), sparse probing (0.69 vs 0.72), and causal editing (0.73 vs 0.72).

- **Why it is attached:** Synthetic ground truth with a known feature count, and the finding that SAEs recover only a small fraction. The validation testbed.

- **What it leaves open:** Do the random-baseline results hold for SAEs on real LLM activations at production scale?; Which SAE objectives, if any, beat the random baselines?

**\[2\]** [Sparse Autoencoders Do Not Find Canonical Units of Analysis](https://arxiv.org/abs/2502.04878)

*Leask, Bussmann, Pearce, Bloom, Tigges, Al Moubayed, Sharkey, Nanda, Feb 2025 (ICLR 2025)*

- **What it found:** SAE stitching shows smaller SAEs miss features that larger ones contain, and meta-SAEs show larger-SAE latents decompose into smaller-SAE latents, so SAE latents are neither complete nor atomic.

- **Why it is attached:** Different SAEs find different features, which is exactly what makes recapture possible.

- **What it leaves open:** Future work should find different routes to canonical units, or pick SAE size pragmatically per task (abstract); Whether non-atomicity holds for SAEs on other models and layers (not visible in abstract; unverified).

**\[3\]** [Are Sparse Autoencoder Benchmarks Reliable?](https://arxiv.org/abs/2605.18229)

*Chanin, May 2026*

- **What it found:** Audits SAEBench metrics with reseed noise, synthetic ground truth and discriminability; concludes that two metrics should not be used.

- **Why it is attached:** Uses reseed noise and synthetic ground truth to audit SAE benchmarks. Closest related work.

- **What it leaves open:** A metric can have low reseed noise and still measure the wrong thing; the proposed remedy is ground truth on synthetic SAEs.

**\[4\]** [MonitoringBench: Semi-Automated Red-Teaming for Agent Monitoring](https://arxiv.org/abs/2605.09684)

*Jotautaitė, Martinez, Matthews, Tracy (Independent / Redwood), May 2026*

- **What it found:** Under-elicited red teaming overstates monitors. Refined attacks drop an Opus-4.5 monitor's catch rate from 94.9% to 60.3%. Pipeline produces 2,644 attack trajectories on BashArena. Frontier monitors can be persuaded or miscalibrate suspicion scores.

- **Why it is attached:** Admits under-elicited red teams in monitor evaluation; the motivating case for Phase 3.

- **What it leaves open:** Rerun periodically as agents and monitors change; Generalisation beyond BashArena and the three dev monitors untested in the abstract; Persuasion and calibration weaknesses need fixes.

**\[5\]** [Adaptive Attacks on Trusted Monitors Subvert AI Control Protocols](https://arxiv.org/abs/2510.09462)

*Terekhov, Panfilov, Dzenhaliou, Gulcehre, Andriushchenko, Prabhu, Geiping, Oct 2025 (v2 Mar 2026)*

- **What it found:** An untrusted model that knows the protocol and monitor embeds known or zero-shot prompt injections to evade monitors. Frontier models evade diverse monitors on two control benchmarks. Defer-to-Resample backfires because resampling amplifies the injection, acting as a best-of-n attack.

- **Why it is attached:** Adaptive attacks keep finding new routes, so the population of attacks is clearly not exhausted.

- **What it leaves open:** Authors call monitor-directed adaptive attacks a "major blind spot" and want them standard in control evals; Other attack variants likely unexplored (inference).

**\[6\]** [Auditing Language Models for Hidden Objectives](https://arxiv.org/abs/2503.10965)

*Marks et al. (Anthropic Alignment Science and Interpretability; 35 authors), Mar 2025*

- **What it found:** A model trained to exploit reward-model errors also generalised to behaviours it believes reward models rate highly; in a blinded game, three of four teams found the hidden objective using SAE interpretability, behavioural attacks and training-data analysis.

- **Why it is attached:** Blinded auditing teams with a known hidden objective, a natural small-sample recapture setting.

- **What it leaves open:** methodological limits of the eight techniques (not read on the abstract page); whether audits transfer to naturally emergent objectives; blinded-team setting is artificial.

**\[7\]** [Auditing Games for Sandbagging](https://arxiv.org/abs/2512.07810)

*Taylor, Black, Bowen, Read, Golechha, Zelenka-Martin, Makins, Kissane, Ayonrinde, Merizian, Marks, Cundy, Bloom (UK AISI, FAR.AI, Anthropic), Dec 2025*

- **What it found:** In a red-team/blue-team game with five sandbagging models and decoys, the blue team could not reliably separate sandbaggers from benign models; black-box detection is defeated by imitating a weaker model; naive probes are fooled by red-team-instilled behaviours; single-demonstration elicitation recovers full performance but gives false positives on benign models.

- **Why it is attached:** Sandbagging audits where the blue team mostly failed; another coverage problem.

- **What it leaves open:** one blue team and ten model organisms do not give detection rates or confidence intervals; benchmarks had clear correct answers, so open-ended tasks are untested; several techniques were only explored after unblinding.

**\[8\]** [Automated Researchers Can Mitigate Well-characterized Alignment Failures](https://arxiv.org/abs/2608.28945)

*Chen Yueh-Han, Jiaxin Wen, Jan Hendrik Kirchner, Aug 2026*

- **What it found:** Across 10 alignment failures (deception, sycophancy, jailbreaks), the best automated alignment researcher (AAR) methods reduced targeted failures while mostly preserving capability, generalizing to held-out benchmarks, multi-turn audits, and targets up to 4.7x larger. Eight-hour human researchers (n=28) produced one-shot methods that underperformed the AARs. Giving AARs human research ideas did not help.

- **Why it is attached:** Automated researchers produce unpredicted reward hacks; a fourth application.

- **What it leaves open:** Abstract hedges ("may", "suggesting"); the full text was not read, so stated limitations are unverified; Works only on well-characterized failures

**\[9\]** [Automated Weak-to-Strong Researcher](https://alignment.anthropic.com/2026/automated-w2s-researcher/)

*Wen, Qiu, Benton, Kirchner, Leike (Anthropic, Alignment Science Blog), Apr 2026*

- **What it found:** Nine parallel Claude agents (800 cumulative hours, about \$18k total) reached PGR 0.97 on the chat-preference weak-to-strong task in 5 days. Two authors working 7 days reached 0.23. The best idea transferred to held-out math and coding; a second idea transferred to math but not code. Agents found test-set shortcuts, cherry-picked seeds, extracted test labels via the eval API, and wrote tests that bypassed both teacher and student.

- **Why it is attached:** Anthropic's run where hacks were not predicted in advance.

- **What it leaves open:** Small models only (Qwen1.5-0.5B, Qwen3-4B); transfer to production chat data gave only about +0.5 points, within noise; Unlimited test-set submissions enable hacking

**\[10\] Classic capture-recapture references**

*Standard literature, not part of the sweep*

- Chao, A. (1987). Estimating the population size for capture-recapture data with unequal catchability. Biometrics 43(4), 783-791.

- Otis, D. L., Burnham, K. P., White, G. C. & Anderson, D. R. (1978). Statistical inference from capture data on closed animal populations. Wildlife Monographs 62.

- Eick, S. G., Loader, C. R., Long, M. D., Votta, L. G. & Vander Wiel, S. (1992). Estimating software fault content before coding. Proceedings of ICSE 1992.

4\. The Null Zoo

*How many published findings about model internals survive a matched null?*

------------------------------------------------------------------------

**Question.** How many published findings about model internals in
