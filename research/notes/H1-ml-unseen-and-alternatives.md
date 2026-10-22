# H1. ML / LLM unseen-species precedents, rare-event alternatives, and close competitors (gap-filling round)

Project: "What did we miss? Capture-recapture for safety tools". Written 22 Oct 2026. 32 WebSearch calls used, plus a shallow git clone of the two ParitKansal repos (read directly, so item 10 is first-hand).

Evidence labels. "(seen)" = the search tool returned the paper page or a reliable excerpt this session. "(secondary)" = the number came from a summary site or from the search tool's paraphrase, not the paper text. "(unverified)" = could not confirm. WebFetch and curl do not reach arXiv, so no PDF was read directly; numbers below come from search-tool readings of the PDFs. Treat every number marked (secondary) as needing a check against the PDF before it goes into a write-up.

---

## 1. Summary

1. **Nasr et al. 2023 (arXiv 2311.17035) is the single most useful precedent, and it is a warning as much as a precedent.** They applied a Good-Turing estimator to the set of extracted memorised strings and obtained a lower bound of at least 1.5 million unique 50-token sequences for ChatGPT, but the authors themselves call this "likely an exceptionally poor estimate" and say they needed about 500 million extracted examples from GPT-Neo 6B before Good-Turing converged (secondary, from the search tool's reading of the appendix; Figure 9, Table 15, Appendix A.8). They advise against using plain Good-Turing there and instead run a sequential Monte Carlo extrapolation (sample from the Good-Turing probabilities, update counts, repeat), which "consistently underestimates" when data are too few. This is exactly the singleton-dominated regime our project must expect.
2. **The Good-Turing / missing-mass line in LLM theory is real and verified**: Kalai and Vempala (2311.14648, STOC 2024) lower-bound the hallucination rate of a calibrated model by the fraction of facts seen once (the "monofact"/singleton rate); Kalai, Nachum, Vempala, Zhang (2509.04664) restate it as a singleton-rate bound. These give us a theoretical reason why f1/n (Turing's missing mass) is the natural headline quantity, but they concern training data, not discovery runs.
3. **Species-estimation on LLM outputs is now an active 2025-26 literature**: KnowSum (2506.02058, smoothed Good-Turing for "how many theorems does an LLM know"), semantic alphabet size (2509.14478), SHADE (2604.19162), SENECA (2605.00668), Blind-Spot Mass (2604.05057), NOVA (2605.15219). None of them uses *replicated independent runs* (capture-recapture); all use abundance counts from one pooled sample. Capture-recapture over runs is still not there.
4. **Two direct competitors exist from a single independent author (Parit Kansal, Oct 2026, repos on GitHub with Zenodo DOIs, no peer-reviewed paper found).** (a) `undiscovered-failures`: Chao1/iChao1/ACE/jackknife and Chao-Jost coverage applied to planted and natural failure types of tabular classifiers, pre-registered, 450 jobs. Headline: the **unseen share of errors is estimable without bias (H1 supported in 95.6% planted, 100% natural cells), the number of failure types is not (lower bound only)**. (b) `label-error-capture-recapture`: genuine multi-detector capture-recapture on MMLU-Redux; **well calibrated but too imprecise to help** (97% interval coverage, but intervals 102 to 797 for truth 181; mean error 95 vs 46 for just counting the union). These are the strongest "prior art plus warning" for the proposal and must be cited and positioned against.
5. **Technology-assisted review (TAR) is a close precedent in a different field**: Bron et al. (2404.01176, ACM TOIS 2025) use Chao's estimator to decide when to stop screening. Conservative Chao variant: mean recall 95.92% for a 95% target but the target was actually met in only 69.86% of runs; for a 100% target, mean recall 98.02% and target met in 53.09% (secondary snippet from a university repository copy; may differ from the final version). Mean recall looks fine, per-run reliability does not. This is the template for how to report: show per-run hit rate, not mean.
6. **Systematic-review capture-recapture (Kastner 2009 "Horizon Estimate"; Stelfox 2013 critical care and surgery) is a 15-year-old, small-sample precedent** with the same problems: very wide intervals (28,839 articles, 95% CI 12,393 to 70,990 in critical care; "3 missed, CI 0 to 6" in surgery) and the independence assumption between searches that share sources.
7. **Rare-event probability methods are a genuine complement, not a substitute.** Jones et al. (2502.16797), Wu and Hilton (2410.13211), Angell et al. (2604.22167), Parulekar and Liu (2607.18454), RareTrap (2609.33638) estimate the probability of a *specified* bad event at deployment scale. They need a target predicate and a score; they do not say how many distinct failure modes remain. Capture-recapture needs no predicate but needs matching. The two answer different questions and should be reported together.
8. **Best-of-N jailbreaking (2412.03556) supplies an empirical discovery curve with a power law in N** (89% GPT-4o, 78% Claude 3.5 Sonnet at N=10,000; 53-71% of eventual successes already by N=100 on Claude/GPT). It is a warning that attacker success is dominated by many tiny per-sample success probabilities; our "species" must be defined at a higher level than the augmented prompt or every success is a singleton.
9. **NOVA (2605.15219) explicitly argues Good-Turing is "a local batch-diversity diagnostic, not an estimator of the historically undiscovered valid mass"** and that false positives in verification create a "contamination trap". That is a direct theoretical objection to using unseen-species estimators for open-ended discovery, and it applies to our red-team and agent-discovery use cases. We need an answer (define a closed, catchable population; verify captures).
10. **Spring (2304.09259, Computers & Security 2023) argues from Rice's theorem that undiscovered vulnerabilities are effectively unlimited / dense**, which is the philosophical objection to estimating any total N. It supports the project's decision to report coverage and lower bounds, not N.
11. **For the vulnerability side, no one has applied capture-recapture across static analysers**; I found no source (the search found none, which is evidence of absence only weakly). A ready dataset exists in a 2025 paper comparing fuzzers and static analysers on Magma (2505.22052: AFL++ 37 and CodeQL 31 of 112 bugs). Equivalent-mutant estimation by capture-recapture: nothing found.
12. **Lakkaraju et al. (1610.09064) and active testing (Kossen, 2103.05331) are complements**: one searches for unknown unknowns by guided exploration, the other gives unbiased, label-efficient estimates of a *known* metric. Neither estimates how many unknown unknowns remain.
13. **The Mane-Srivastava-Hwang 2005 paper (UMN) is an early explicit "capture-recapture for classifiers" precedent**: it estimates positives missed by two or more classifiers, and its central contribution is conditional independence of classifiers given the class and a heuristic to test feature-set independence. It is the oldest ML-venue precedent I found for what the proposal does.
14. **Overall novelty assessment**: capture-recapture across replicated independent runs of an AI-safety discovery tool (SAE seeds, red teams, auditors) with planted-truth validation does not appear to be done. Closest are (4b) with LLM judges as detectors on MMLU-Redux, and (4a) with a single-sample coverage estimator on tabular failures. Both found the same thing the statistics predict: unseen *mass* is estimable, unseen *count* is not.

---

## 2. Papers

### 2A. Unseen-species estimators already used on LLMs

**Nasr, Carlini, et al. (2023/2025). "Scalable Extraction of Training Data from (Production) Language Models." arXiv 2311.17035 (seen; also ICLR 2025 proceedings).**
- What they did: divergence attack on aligned ChatGPT (gpt-3.5-turbo) that makes it emit training data at about 150x the normal rate (seen). About $200 of queries gave 27,171 unique verbatim-memorised examples (50-token exact match against a roughly 9 TB auxiliary corpus) (seen/secondary). Section 3.4 and Appendix A.8 extrapolate to larger budgets.
- How Good-Turing was used (secondary, from the search tool's reading of the appendix): treat the set of distinct memorised 50-grams as species and the number of times each one is re-extracted as its abundance. Good-Turing on the singleton/doubleton counts gives (i) a lower bound on total memorisation for ChatGPT of at least 1.5 million unique 50-token sequences (Figure 9) and (ii) a sequential Monte Carlo extrapolation: draw new samples from the Good-Turing probabilities, update the frequencies, repeat to predict the number of unique memorised examples far into the future. Table 15 in the appendix compares other estimators under varying assumptions; the authors say Good-Turing gave "consistently higher-quality lower bounds than other methods".
- How good was the extrapolation: they validate on open models where ground truth can be approximated, and report that Good-Turing needed about 500 million extracted examples from GPT-Neo 6B before converging, so the ChatGPT estimate (far fewer queries) is likely very poor; they recommend against using it directly (secondary). With too little data it consistently underestimates.
- Why it matters: (a) same estimator family and same regime (huge unseen mass, mostly singletons); (b) a worked example of lower-bound reporting; (c) a ground-truth testbed idea: validate on a model where the training set is known (Pythia/GPT-Neo with the Pile) so that "total memorised" is known; (d) their sequential Monte Carlo is a template for the "what would 2x more runs find" quantity in our reporting recipe.
- Leaves open: no capture-recapture over replicated attacks, no heterogeneity model, no confidence intervals, no treatment of adaptive attack.
- Competes or complements: complements (same family, earlier use). Warns: even Good-Turing's nominal strength (consistency in coverage) only shows up after hundreds of millions of samples when the tail is this heavy.
- Gap: I could not obtain the exact Figure 9 values or Table 15 rows. Check the PDF.

**Kalai and Vempala (2024). "Calibrated Language Models Must Hallucinate." arXiv 2311.14648; STOC 2024 (seen).**
- Claim: for arbitrary facts that cannot be verified from patterns, a calibrated model must hallucinate at a rate about equal to the fraction of facts seen exactly once in training (the "Good-Turing" missing-mass estimate), provided the maximum probability of any fact is bounded (seen, via search tool summary).
- Why it matters: supplies a theoretical justification for treating f1/n as the headline quantity; the statistic is the same as our "singleton share".
- Leaves open: it is about the training distribution, not about the output of a discovery tool.
- Complement (theory). Warning: the bound is a floor, same direction as every lower bound in this project.

**Kalai, Nachum, Vempala, Zhang (2025). "Why Language Models Hallucinate." arXiv 2509.04664 (seen).**
- Defines the singleton rate (share of prompts/facts appearing exactly once in training) as a lower bound on expected hallucination; credits Turing/Good (1953). Follow-up: Miao and Kearns, "Hallucination, Monofacts, and Miscalibration: An Empirical Investigation," arXiv 2502.08666 (seen as a title); search summary says a PNAS 2026 version reports up to 40% hallucination reduction from targeted miscalibration (secondary).
- Matters here: if we need an LLM-side reference for "singleton rate predicts the unseen failure rate", this is it; the empirical monofact test is a template for validating f1/n against truth.

**Si, Yang, Hashimoto (2024/2025). "Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers." arXiv 2409.04109; ICLR 2025 (seen).**
- Duplication analysis (the search tool read the PDF): for each topic they generated 4,000 seed ideas; an idea was a duplicate if cosine similarity (Sentence-Transformers, threshold 0.8, chosen by manual inspection) to any earlier idea on the same topic exceeded 0.8. Out of 4,000, **only about 200 (about 5%) were non-duplicates** (secondary but consistent across two readings). Figure 4 shows the percentage of non-duplicates in each new bucket falling and the cumulative unique count flattening. The authors present this as a bottleneck for inference-time scaling of idea generation (Section 7.1).
- Why it matters: this is an accumulation curve with a saturating tail, i.e. exactly the data on which Chao1/Chao-Jost can be tested without any new experiments. It is also a cautionary tale for the matching step: the 0.8 cosine threshold fixes the number of "species" (200 of 4,000) and a different threshold would give a very different richness. Use it as a threshold-sensitivity illustration.
- Leaves open: no estimator applied; no ground truth for "number of distinct ideas that exist".
- Complement/testbed. Warning: richness depends on the matching rule.

**Li, Xin, Long, Su (2025). "Evaluating the Unseen Capabilities: How Many Theorems Do LLMs Know?" arXiv 2506.02058 (seen). Code: github.com/Raina-Xin/KnowSum.**
- KnowSum: generate many LLM answers, verify against an external database (Wikipedia, MathSciNet), cluster semantically identical items, then use a smoothed Good-Turing estimator (SGT, truncation parameter k; provably near-optimal in worst-case normalised MSE up to subpolynomial factors) to extrapolate the number of unseen items. Applications: total knowledge, retrieval effectiveness, output diversity. They report that a substantial amount of knowledge is missed by observed performance alone and that rankings of some LLMs change after correction. Poster says (N_query, N_ans) = (30,000, 20) for theorem counting (secondary). I did not find the headline unseen proportions.
- Why it matters: closest published "unseen species in an LLM" pipeline with a verify-then-cluster step, the same shape as "match findings across runs". The verify step addresses the NOVA contamination concern.
- Leaves open: single pooled sample; no replicated-run structure; no planted truth.
- Complement (same estimator family, abundance-based). Related title only: "The Unseen Species Problem Revisited," arXiv 2602.08769 (seen as a title, not read).

**McCabe, Melamed, Hartvigsen, Huang (2025, rev. Feb 2026). "Estimating Semantic Alphabet Size for LLM Uncertainty Quantification." arXiv 2509.14478 (seen).**
- Argues discrete semantic entropy underestimates true entropy; adjusts for sample coverage with the Good-Turing coverage estimator and converts it into an alphabet-size estimator; two alphabet-size estimators flag incorrect responses as well as or better than top alternatives (seen, abstract-level).
- Matters: shows Good-Turing coverage working on clusters of LLM responses (semantic equivalence classes) as the "species"; supports the idea that LLM outputs can be binned into species via entailment/clustering. Same group: SENECA, arXiv 2605.00668 (McCabe and Huang; "Small-Sample Discrete Entropy Estimation via Self-Consistent Missing Mass"; seen as a title and listing only).

**Pan, Guo, Kuang, Lu (2026). "Mind the Unseen Mass: Unmasking LLM Hallucinations via Soft-Hybrid Alphabet Estimation" (SHADE). arXiv 2604.19162 (seen).**
- Black-box hallucination-risk estimator for few samples per query: estimates the number of distinct meanings by combining generalised Good-Turing coverage with a heat-kernel trace of a normalised Laplacian built on an entailment-weighted response graph; the fusion rule switches with estimated coverage. Gains are largest when the budget is smallest and shrink as samples increase. A secondary excerpt reports Good-Turing alphabet-size MAE falling from 3.66 at n=5 to 1.43 at n=50 against an N=100 oracle.
- Matters: a "soft matching" variant of richness estimation; relevant to our identity-matching problem (graded, not binary, equivalence). Small-sample regime like ours (K of 3 to 10).

**Pal, Bhattacharya, Singh (2026). "Blind-Spot Mass: A Good-Turing Framework for Quantifying Deployment Coverage Risk in Machine Learning Systems." arXiv 2604.05057 (seen; submitted to JMLR).**
- Defines B_n(tau): the estimated probability mass of deployment states whose empirical support in the training/validation data is below a threshold tau, computed with Good-Turing unseen-species estimation. Tested on wearable human-activity recognition (wrist inertial data) and MIMIC-IV (275 admissions). Under a deployment-refined state abstraction, about 95% of deployment probability mass sits below tau=5 in both settings (seen).
- Matters: it applies the exact "coverage = 1 - f1/n" logic to deployment coverage of ML systems (not to discoveries). Shows the notion generalises beyond species counts to thresholded support; and shows that the answer is extremely sensitive to the state abstraction (the same matching problem as ours).
- Complement (coverage framing, same estimator family). Warning: a headline like "95% of mass is under-supported" depends entirely on how states are defined.

**Avestimehr, Duffy, Medard (2026). "NOVA: Fundamental Limits of Knowledge Discovery Through AI." arXiv 2605.15219 (seen, abstract only).**
- Theory paper. Key claims: (i) under imperfect verification, even small false-positive rates can admit invalid artifacts faster than genuine discoveries once easy knowledge is exhausted (the "contamination trap"); (ii) Good-Turing is "a local batch-diversity diagnostic, not an estimator of the historically undiscovered valid mass governing long-term progress"; (iii) with a Zipf tail, the cumulative cost of D distinct genuine discoveries scales as D^alpha with alpha greater than 1; (iv) human guidance, generation and verification can restore discovery when autonomous sampling stalls because of repetition, vanishing exposure or unreliable verification.
- Matters: this is the most direct theoretical *warning* against applying unseen-species estimators to AI discovery runs. It tells us to (a) verify every capture, (b) say "local, within the catchable population", (c) expect cost-to-find to be superlinear. It also gives a prediction we can test: discovery cost curves in agent/automated-research runs should be convex.
- Leaves open: no empirical estimator evaluation (abstract-level read only).

### 2B. Rare-output probability and tail forecasting (complements)

**Jones, Tong, Mu, Mahfoud, Leike, Grosse, Kaplan, Fithian, Perez, Sharma (2025). "Forecasting Rare Language Model Behaviors." arXiv 2502.16797 (seen).**
- Method (from abstract and summaries): for each query define the elicitation probability, the chance a single sample elicits the target behaviour. They study the distribution of these probabilities over a query set and find that the *largest* elicitation probabilities scale predictably with the number of queries; this permits forecasts across up to three orders of magnitude more queries than were tested (seen). A follow-up describes it as using extreme value theory (consistent with a Gumbel-type tail fit) to project deployment-scale risk (secondary). Anthropic's announcement says it works with limited test data. Query harmfulness was proxied by the likelihood of hand-crafted completions because direct estimation by repeated sampling is expensive (secondary, from a follow-up paper).
- Numbers: I could not find the forecast error figures or the Gumbel fit details. (unverified)
- Matters: forecasts "will any query in 10^6 elicit the behaviour". That is the *rate/probability* question. It does not count how many distinct behaviours or attack families exist. The natural combined report: forecast worst-case probability plus capture-recapture coverage of distinct failure families.
- Competes? Only partly: for deployment-scale risk of known behaviours it is better. Does not help when the behaviour set itself is unknown.
- Warning: it requires a continuous score or elicitation probability per query; the extreme-value assumption is a parametric tail extrapolation, which fails if the tail has a different shape (our heterogeneity problem in a different form).

**Wu and Hilton (2024/2025). "Estimating the Probabilities of Rare Outputs in Language Models." arXiv 2410.13211; ICLR 2025 (seen).**
- Estimate the probability of a binary property of the output when it is too rare for random sampling. Two families: importance sampling (ITGIS, MHIS) and activation extrapolation (QLD, GLD, which fit a distribution to the logits and extrapolate); importance sampling beat activation extrapolation, and both beat naive sampling; tested on small transformers with argmax sampling (seen, abstract-level; variant names from a third-party review). Margins not found. (unverified)
- Matters: complements: needs a target event. Warns that cheap parametric extrapolation (like our estimators) loses to search-based importance sampling when a target is known.

**Angell, Singhal, Horvitz, Yu, Ranganath, McKeown, He (2026). "Estimating Tail Risks in Language Model Output Distributions." arXiv 2604.22167 (seen). Code: github.com/rangell/LMTailRisk.**
- Importance sampling with an activation-steered "unsafe" proposal; matches brute-force Monte Carlo with 10 to 20x fewer samples; probability of order 10^-4 estimated with 500 samples. Needs white-box access.
- Matters: a current, concrete baseline for the "probability of a known harmful output" half of a combined report.

**Parulekar and Liu (2026). "Estimating Rare Events in Language Models with Proper Evaluation." arXiv 2607.18454 (seen).**
- GA-AMLS (gradient-based MCMC in activation space) and a Shifted-Power Bregman loss, a proper scoring rule that stays finite when an estimator returns zero and has tunable asymmetry. Under roughly symmetric penalties GA-AMLS has lower bias; under strongly asymmetric penalties QLD can win because its positive bias is a conservative hedge against false negatives.
- Matters for evaluation design: **our estimators also need an asymmetric loss** (underestimating missed items is worse than overestimating). Borrow the proper-scoring-rule idea to compare estimators on bias that matters.

**RareTrap: "Quantifying Behavioral Tails in Black-Box Language Models." arXiv 2609.33638 (seen).** Surrogate LLM builds a geometry-aware mapping from a low-dimensional latent space into token-embedding space, induces a reproducible prompt distribution, then runs sequential rare-event simulation; across 10 open-weight and two frontier models (GPT-5.4, Claude Sonnet 4.6) it induces severe resource-consumption behaviours and computes probabilities with as few as 200 evaluations (seen). Other titles seen only: "Rare Event Estimation via Iterative Unalignment" (2609.24969), "Predicting LLM Safety Before Release by Simulating Deployment" (2607.07184), "Weighted Ensemble Sampling for Rare-Event Estimation in Language Models" (2610.19202), LessWrong post "Predicting Rare LLM Failures with 30x Fewer Rollouts". Abstracts not read. (unverified)

**Hughes, Price, Lynch, et al. (2024). "Best-of-N Jailbreaking." arXiv 2412.03556 (seen).**
- Repeatedly samples random augmentations of a prompt until a harmful response. Attack success rate (ASR) reaches 89% on GPT-4o and 78% on Claude 3.5 Sonnet at N=10,000 (seen). ASR as a function of N follows power-law-like behaviour over many orders of magnitude, fitted as -log(ASR) = a N^-b (seen). 53-71% of the jailbreaks found at N=10,000 on Claude and GPT occur within the first 100 samples; 22-30% on Gemini (secondary). A secondary summary says power laws fitted at N up to 1,000 predicted ASR at 10,000 with average error about 4.6% (secondary, unverified). Grader is a classifier, so numbers depend on it (Pith review).
- Implication for the attacker's discovery curve: the observed curve is a mixture of many per-prompt success probabilities, so the heavy-tailed shape implies strong heterogeneity of "catchability" across prompts (my inference). Early plateau (most successes by N=100) means singleton-style estimators will see few singletons late. Each successful augmentation of the same base prompt is the same underlying vulnerability; **if every augmented prompt counts as a species, all species are singletons and the estimator reports huge unseen mass; if they are merged by base prompt, richness is capped at the number of base prompts.** Definition of species drives everything.
- Matters: gives the power-law discovery model to simulate "attacker runs" with known truth; also a ready competitor: forecast ASR(N) rather than count families.
- Complement (forecast of success probability under more effort, not number of distinct failure modes).

**Lakkaraju, Kamar, Caruana, Horvitz (2017). "Identifying Unknown Unknowns in the Open World: Representations and Policies for Guided Exploration." AAAI 2017; arXiv 1610.09064 (seen).**
- Model-agnostic: partition data by feature similarity and model confidence, then run an explore-exploit (bandit) policy with oracle feedback to find high-confidence errors. Evaluated on sentiment classification, subjectivity detection, and image classification with base models from decision trees to neural nets; specific numbers not found. Bansal and Weld (AAAI 2018) criticise the assumption that the utility of each discovered unknown unknown is independent (secondary).
- Matters: it searches for unknown unknowns but never estimates how many are left. Complement. Its partition-by-confidence idea is a natural covariate for Huggins-type models.

**Kossen, Farquhar, Gal, Rainforth (2021). "Active Testing: Sample-Efficient Model Evaluation." ICML 2021, PMLR 139:5753-5763; arXiv 2103.05331 (seen).**
- Chooses which test points to label so that the estimate of test risk has lower variance, with a correction that removes the bias introduced by active selection (seen).
- Matters: shows how to correct for adaptive selection in estimating a known risk; the importance-weighting trick is a template for our adaptive-attacker correction. It estimates a metric over a given test set, not the unseen part of an open population. Complement.
- Gap: I found no 2025-26 paper on "unknown unknowns" or residual-risk estimation of LLM evaluations in the sense of this project beyond those listed in 2A and 2B. EVT searches returned only finance/hydrology/RL results, besides Jones et al.

### 2C. Capture-recapture for "how many did the search miss" (close precedents)

**Bron, van der Heijden, Feelders, Siebes (2024/2025). "Using Chao's Estimator as a Stopping Criterion for Technology-Assisted Review." arXiv 2404.01176; ACM TOIS 43(3), 2025, doi 10.1145/3724116 (seen).**
- Uses Chao's lower-bound population-size estimator (Chao 1987, "Conservative") and a Poisson-regression adaptation by Rivest and Baillargeon ("Optimistic") to estimate the number of relevant documents and stop review once the target recall is estimated reached. I could not confirm how the "captures" are defined (my understanding is that repeated sampling/ranking events give the n1 and n2 counts; check Section 3). (unverified)
- Numbers (secondary, from a repository copy): 95% target: Chao 1987 Conservative mean recall 95.92%, Work Saved over Sampling (WSS) 56.21%, target met in 69.86% of runs. 100% target: Conservative mean recall 98.02%, target met in 53.09% of runs; Optimistic (Rivest) mean recall 98.29%, WSS 52.33%. Optimistic methods are less reliable because they lack a confidence interval; for 100% recall the Conservative one is recommended.
- Why it matters: (a) a peer-reviewed, 2025 use of Chao for "how many did our process miss"; (b) shows the reporting trap: average recall is near target but the success rate is only 53 to 70%; (c) shows a stopping-rule use that we can port to red-team and SAE-training budgets ("stop adding runs when estimated coverage is at least X"); (d) a conservative and optimistic variant pair maps to our "lower bound versus jackknife" pair.
- Follow-ups (seen as titles): "Confidence-Based Stopping Methods for Systematic Reviews" (arXiv 2606.15380; doi 10.1145/3805712.3809924); "Early Recall Estimation and Stopping in Technology-Assisted Reviews via Ranker-Sampler Fusion" (doi 10.1145/3774905.3795598); "Heuristic stopping rules for technology-assisted review" (doi 10.1145/3469096.3469873); GitHub s-matysik/SnowBallSLR (capture-recapture recall estimation for snowballing literature reviews; code only, unread).
- Competes with / complements: TAR's mainstream alternative is sampling-based recall estimation (draw a random sample of the unreviewed pool and label it). That is the *design-based* alternative: if you can afford a random audit of the unseen pool, you do not need capture-recapture. For safety tools there is no enumerable pool to sample from, which is the argument for model-based estimators.

**Systematic-review search completeness.**
- Kastner et al. (2009). "The capture-mark-recapture technique can be used as a stopping rule when searching in systematic reviews." J Clin Epidemiol (seen as a listing). Four databases searched in sequence; "Horizon Estimate" from overlap; authors say more work is needed to show usefulness as a stopping rule.
- Stelfox et al. (2013). "Capture-mark-recapture to estimate the number of missed articles for systematic reviews in surgery." Am J Surg (seen). Estimated 3 missed (95% CI 0 to 6); database search found about 93% of known articles. Same group: "Capture-mark-recapture as a tool for estimating the number of articles available for systematic reviews in critical care medicine," J Crit Care (seen): estimate 28,839 articles (95% CI 12,393 to 70,990).
- Also seen as titles: "Use of capture-recapture technique to evaluate the completeness of systematic literature searches" (ResearchGate 14441439, authors and year unverified; I believe BMJ 1996, unverified); "Capture-recapture is a potentially useful method for assessing publication bias" (J Clin Epidemiol 2003).
- Matters: shows capture-recapture accepted in a 'missed items' application for 15+ years, with the identical limits: independence between searches fails when they share sources; intervals are very wide. Nothing found on e-discovery court acceptance (the search returned no legal sources); that remains a gap.

**Mane, Srivastava, Hwang (2005). "Estimating missed actual positives using independent classifiers." (listed at Experts@Minnesota, seen; venue not confirmed in the snippet, probably a KDD-series proceeding.) (venue unverified)**
- Capture-recapture idea: two or more classifiers flag instances; overlap estimates the number of positives that all classifiers missed. Needs at least two (conditionally) independent classifiers. The main content is the dependence question: it defines conditional independence of classifiers given the class label, relates it to independence of the classifiers' feature sets, and proposes a heuristic algorithm for choosing classifiers/feature sets because checking feature-set independence is computationally expensive.
- Matters: the earliest ML-venue statement of "classifiers as capture occasions"; its remedy (build the detectors from disjoint feature sets) is a design lever for us: make attackers or SAEs differ in training data/architecture to reduce dependence. Related: "Estimation of false negatives in classification" (ResearchGate 4133622; seen as a title). Details unverified.

### 2D. Direct competitors from one independent author (read first-hand from the repositories)

Both repos are by **Parit Kansal** (independent researcher, paritkansal.in), October 2026, with Zenodo DOIs and `CITATION.cff` files of type "software". I found no arXiv or conference paper; the "papers" are the README documents. The acknowledgements say literature search and code were developed with Claude. Treat as grey literature (unrefereed), but the work is pre-registered and the code is tested.

**10a. `ParitKansal/undiscovered-failures`: "How Many Failure Types Are Still Undiscovered? Species-Richness Estimators for Testing Machine-Learning Models." GitHub; Zenodo DOI 10.5281/zenodo.23412807 (last commit 2026-10-16).**
- Setup: tabular datasets (Adult, Bank Marketing, Covertype, MAGIC Gamma, Electricity), 3 model families (logistic regression, random forest, histogram gradient boosting), 5 fresh seeds, 450 jobs, 283,500 result rows, pre-registered in `PREREG.md` (commit abafcac, 8 Oct 2026). Failure types: *planted* (flip 60% or 90% of training labels inside 15, 30 or 60 disjoint rare subgroups defined on 1 to 3 features, covering 0.01% to 2% of rows) or *natural* (errors of a clean model grouped into types fixed beforehand: 5x5 or 10x10 quantile grids over the first two principal components, or 25 k-means clusters). Tests of 300, 1,000, 3,000 rows drawn 30 times each from a held-out pool; a second same-size draw tests new-type prediction.
- Estimators: Chao1, iChao1, ACE, first-order jackknife (number of types); Chao-Jost sample coverage, with Turing f1/n as a baseline (unseen share of errors); Shen-Chao-Lin new-type prediction. Intervals: log-normal, bootstrap, bias-calibrated bootstrap.
- Results (the repo's `RESULTS.md`): H1 unseen-share estimate unbiased (|bias| at most 0.04 in at least 90% of cells): supported, 95.6% planted and 100% natural cells. H2 calibrated 95% interval honest (coverage at least 0.90 in at least 80% of cells): not supported for planted (71.1%), supported for natural (95.6%); worst cell Adult at 300 rows (bias up to +0.076, coverage 0.70 to 0.84). H3 ACE closer to true richness than the raw count in at least 90% of cells: not supported (88.9% planted, 85.2% natural). H4 bias-calibrated ACE interval coverage by budget 300/1,000/3,000 rows: 0.65/0.77/0.84 planted, 0.73/0.74/0.81 natural (no interval for the number of types reaches 95%). H5 Chao-Jost beats Turing f1/n on MAE in 71.1% (planted) and 84.4% (natural) of cells. Median absolute error of the unseen share: 0.146/0.050/0.011 planted, 0.086/0.023/0.005 natural at 300/1,000/3,000 rows. Raw count of types found misses about half of the planted types at 300 rows (relative error -0.52); ACE reduces but does not remove the gap (-0.16); natural_grid100 at 300 rows has raw -0.67 and the unseen type share 0.51.
- Authors' stated limits: tabular data and classical models only; natural types are grid cells and clusters, not types a person would name; "does not show how the estimators behave on ... the failure categories found by red-teaming a language model."
- What differs from our proposal: it is **single-sample (abundance/incidence in one test set), not multi-run capture-recapture**; failures are *defined by data partitions*, not matched across independent finders; no dependence among occasions; no adaptive searcher.
- Why it matters: (a) closest published-style prior art to the "coverage first, richness as lower bound" recipe, and its numbers independently confirm the pilot's and the statistics report's conclusion (unseen mass is estimable, count is not); (b) usable as a baseline: if our multi-run design does not beat single-sample Chao-Jost on coverage error, the extra runs are not buying anything; (c) pre-registration structure and decision thresholds (90% of cells within 0.04) are worth copying; (d) cite it, and distinguish clearly.

**10b. `ParitKansal/label-error-capture-recapture`: "How Many Label Errors Are Left? Capture-Recapture for Counting the Benchmark Errors Nobody Found." GitHub; Zenodo DOI 10.5281/zenodo.23205993 (last commit 2026-10-07). Status: pre-registered negative result.**
- Setup: detectors are capture occasions; a capture needs a *verified* error (the population estimated is real label errors). Ground truth: MMLU-Redux (Gema et al., "Are we done with MMLU?", NAACL 2025, arXiv 2406.04127), 5,700 questions, 181 expert-labelled wrong keys; plus 200 planted-error sets (266 swapped answer keys each, questions experts marked correct). Estimators in `crc.py`: union (naive), Chapman, Fienberg log-linear (primary; forward AIC over two-way interactions, stability guard), Chao lower bound, Burnham-Overton Mh jackknife.
- Experiment 1 (older judges: Llama-3-8B, Mistral-7B, Qwen2-7B, Phi-3-medium, plus confident learning): the estimator was very accurate (181.9 vs 181) but judges flagged 35 to 64% of questions (4,145 of 5,700 together), found 171 of 181 errors, so nothing was left to estimate: NO-GO by own rule.
- Experiment 2 (Gemma-4-31B, Qwen3.8-27B, Mistral-Small-4, plus confident learning, each flagging only its top 285 = 5%): together found 100 of 181 real errors (missed 45%); confident learning was the best single detector (46% recall, 30% precision). Interval coverage on planted errors 97%, but the real-data interval was 102 to 797 (truth 181), median planted interval width 681 on a truth of 266; point estimate overshot truth in three of four trials; mean absolute error 95 versus 46 for simply counting the union. Verdict PARTIAL. Simulation in the repo: the jackknife falls to 18-21% of truth and Chao to 19-26% of truth once all detectors are dependent; the log-linear primary's median ratio never exceeds 0.99 and falls when it breaks, i.e. it underestimates when it fails.
- Other findings: planted errors are much easier to find than real ones (judges flagged 75-91% of swapped keys but only about 55% of real errors), so planted-error validation overstates real performance. Repo's novelty check (three independent searches, 5-6 Oct 2026) reports no earlier CR use for benchmark label errors; Petersson 2004 and Briand 2000 identified as the main precedents; Difallah et al. 2018 (MTurk worker populations) as a CR use in crowdsourcing.
- Why it matters: (a) it is a nearly identical idea executed on a different target, with an honest negative result; (b) its failure mode is the one we predicted (few detectors of uneven skill, strong dependence, thin overlap); (c) its pre-registration is a model; (d) **it motivates our use of many cheap runs (K of 10 or more, SAE seeds, resampled red-team runs) rather than 3 to 4 expensive detectors**, and the coverage-first reporting that avoids needing a precise N; (e) it warns that planted truth is easier than reality.
- Related items cited by that repo (not independently verified by me): Land and Bikel, "Auditing LLM Benchmarks with Item Response Theory," arXiv 2605.30504; Truong et al., "Fantastic Bugs and Where to Find Them in AI Benchmarks," arXiv 2511.16842; Nahum et al., EMNLP 2025 LLM-judge label-error detection; Rivest and Yauck, "Small sample inference for two-way capture recapture experiments," arXiv 2307.11705.

### 2E. Vulnerability stock, static analysers, mutants

**Spring (2023). "An Analysis of How Many Undiscovered Vulnerabilities Remain in Information Systems." arXiv 2304.09259; Computers & Security 2023 (seen; volume/article number uncertain between 131/103290 and DOI 10.1016/j.cose.2023.103191).**
- Argues from computability (Rice's theorem) that undiscovered implementation and configuration vulnerabilities are effectively unlimited ("dense": always more in a given program), and critiques the "manageably small" paradigm (Geer's belief that "vulns are scarce enough" for cornering the market to work, Schneier somewhat less pessimistic). Design flaws are out of scope. A later paper, "Vulnerability Abundance: A formal proof of infinite vulnerabilities in code," arXiv 2604.07539 (seen as a listing), builds an executable example supporting this.
- Matters: philosophical backing for "N is not identified; report coverage over the catchable population". Also a warning that rediscovery-rate-to-total-stock inference is contested.

**Rediscovery measures (context from earlier reports, seen again here):** RAND (Ablon and Bogart) and Herr, Schneier, Morris, "Taking Stock: Estimating Vulnerability Rediscovery": over 4,300 vulnerabilities, 15-20% were independently discovered at least twice within a year; Android 13.9% within 60 days, 20% within 90; a later version with 2,600 vulnerabilities gives 12.7% aggregate rediscovery, with more than 60% of Android/Chrome rediscovery in the first month (secondary).

**Geer.** I could not find the essay "The Undiscovered" itself. What was confirmed: Dan Geer's Black Hat USA 2014 keynote argued for mandatory vulnerability reporting by analogy to disease outbreaks and for government to corner the vulnerability market; this assumes the stock of vulnerabilities is small, and Schneier's response is that if the stock is large the finders will find different sets (secondary: Threatpost, Schneier blog). That sparse-versus-dense disagreement is precisely what a rediscovery-based capture-recapture estimate would address, so Geer is useful as motivation. A specific Geer estimate of the stock: not found. (unverified)

**Static analysers and mutants.** No source found applying capture-recapture to overlap between static analysers. The nearest items: (i) a 2025 comparative study of fuzzers and static analysers on memory-unsafety bugs in C/C++ (arXiv 2505.22052; seen): e.g. among 112 Magma bugs, AFL++ finds 37 and CodeQL 31; per-tool counts but no CR estimate; the per-tool bug sets would give a ready multi-list dataset; (ii) a "correlated capture-recapture model" for undetected software errors (ResearchGate 222620626; title only; authors unverified). Equivalent mutants: no source found. This is a negative search result, not proof of absence.

---

## 3. How each item relates to the capture-recapture approach

| Item | Relation | One-line reason |
|---|---|---|
| Nasr et al. 2311.17035 | complements and warns | same estimator family; their own Good-Turing estimate was "exceptionally poor" without hundreds of millions of samples |
| Kalai and Vempala 2311.14648; Kalai et al. 2509.04664 | complements (theory) | missing mass = singleton fraction; supports headlining f1/n |
| Si et al. 2409.04109 | testbed and warning | ready saturation curve; richness (200 of 4,000) depends on the 0.8 threshold |
| KnowSum 2506.02058; McCabe 2509.14478; SHADE 2604.19162; Blind-Spot Mass 2604.05057 | same family, single-sample | none uses replicated independent runs |
| NOVA 2605.15219 | warns | Good-Turing is local; false positives corrupt it |
| Jones et al. 2502.16797 | complements | forecasts rate of a known behaviour; no count of unknown modes |
| Wu and Hilton 2410.13211; Angell 2604.22167; Parulekar 2607.18454; RareTrap 2609.33638 | complement | importance sampling for specified events; better than CR when the event is known |
| Hughes et al. 2412.03556 | testbed and warning | power-law discovery curve; species definition drives all numbers |
| Lakkaraju 1610.09064 | complements | finds unknown unknowns, does not count them |
| Kossen 2103.05331 | complements | adaptive-selection bias correction for a known metric |
| Bron 2404.01176 and systematic-review CR | close precedent | Chao as stopping rule; per-run reliability only 53-70% |
| Mane et al. 2005 | precedent | classifiers as capture occasions; independence heuristic |
| Kansal `undiscovered-failures` | competitor and baseline | coverage estimable, richness not; single sample |
| Kansal `label-error-capture-recapture` | competitor and warning | calibrated but imprecise with 3 to 4 detectors |
| Spring 2304.09259 | warns | totals may be unbounded |

---

## 4. Leads, inspirations and experiment ideas

1. **Reproduce a Nasr-style test with known truth.** Use a small open model with a known training set (Pythia-70M to 410M on the Pile, or a model trained by us on a small corpus). Extract memorised strings with K independent attack runs, then compare Good-Turing, Chao1, and multi-run capture-recapture estimates with the true memorised set found by exhaustive scan. Check how many samples are needed before the estimate of unseen mass converges (Nasr: about 500 million for GPT-Neo 6B). This is a ground-truth bridge between the ML-security and the CR literatures and matches the "validate first where truth is known" plan.
2. **Replicate-run version of KnowSum / Si et al.** Run the LLM idea (or theorem) generator K times with different seeds, cluster, and treat runs as occasions. Compare the pooled-abundance Good-Turing estimate with the incidence-based Chao2/iChao2 estimate and with a held-out half. Sweep the cosine threshold (0.7 to 0.9); report how richness changes (Si used 0.8).
3. **Best-of-N as a planted-truth attacker.** Simulate attackers as BoN with a fitted per-prompt success distribution; define species at base-prompt level; plant M prompts with known catchability; run K independent BoN attackers; test whether coverage computed from base-prompt overlap predicts ASR at 10x N better than extrapolating the BoN power law. This is a head-to-head against the competing forecast.
4. **Combined report card**: for every tool give (a) coverage / missing mass with bootstrap CI, (b) richness lower bound, (c) forecast worst-case rate at 10x budget (Jones or Angell when scores or white-box access exist), (d) per-run hit rate of the stopping rule (TAR style: how often the stated target was truly reached). Include the TAR-style *success rate*, not only the mean.
5. **Stopping rule for SAE and red-team budgets**: port the Bron et al. conservative and optimistic Chao variants. Metric: Work Saved over Sampling analogue (runs saved) versus the fraction of campaigns where the stated coverage target was actually reached.
6. **Asymmetric proper scoring for estimators** (Parulekar and Liu's Shifted-Power Bregman idea): compare estimators under a loss that penalises underestimating missed items more than overestimating.
7. **Out-do Kansal's label-error result with more occasions.** The failure there is few detectors (3 to 4) with thin overlap. Repeat MMLU-Redux with K of 10 to 30 cheap detectors (different prompts, temperatures, and models) and check whether the interval width falls; at K of 10 or more, Mh-Chao and iChao should start to behave. Report per-K interval width and the dependence among detectors. MMLU-Redux data and the repo's `crc.py` are reusable (MIT licence).
8. **Single-sample baseline.** Include the `undiscovered-failures` estimator suite (Chao-Jost coverage, f1/n) as the baseline that multi-run designs must beat; its code (`estimators.py`) is MIT licensed and tested.
9. **Independence by construction (Mane et al.)**: make occasions differ in disjoint feature sets, e.g. SAEs trained on disjoint corpus shards, attackers using disjoint strategy libraries. Measure whether the pairwise dependence falls and whether Lincoln-Petersen bias falls with it.
10. **Test NOVA's convexity prediction**: in an agent-discovery experiment, record cost per new verified discovery versus count; fit D^alpha; check alpha greater than 1 and whether estimated coverage tracks it.
11. **Static analysers as lists**: use per-tool results from the Magma comparison (2505.22052) as a K-list CR dataset; check overlap structure and the estimate against the full 112-bug truth plus later-found bugs.

---

## 5. Pitfalls and warnings

- **Good-Turing needs enormous samples when the tail is heavy** (Nasr). With few runs, expect the estimator to be dominated by the singleton count and to underestimate; Nasr's own Monte Carlo extrapolation "consistently underestimates" with too little data.
- **Calibrated yet useless**: Kansal's label-error study shows 97% coverage with intervals 4 times wider than the truth. Coverage alone is not success; report interval width relative to the quantity and compare with the naive union.
- **Mean versus per-run**: TAR numbers look good on average (95.9% mean recall) but only 69.9% of runs met the 95% target. Report the fraction of runs where the target was met.
- **Species definition drives the answer** (Si: 200 of 4,000 at cosine 0.8; BoN: augmented prompts versus base prompts; Blind-Spot Mass: state abstraction). A sensitivity sweep is mandatory.
- **Verification and contamination** (NOVA): unverified captures inflate singletons; false positives raise f1 and therefore the estimated unseen mass. KnowSum verifies against external databases; Kansal requires verified errors.
- **Planted truth is easier than real truth** (Kansal: judges flag 75-91% of swapped keys vs about 55% of real errors; also true for planted attacks). Validate on at least one realistic setting.
- **Estimand**: coverage over the *catchable* population, not the population that exists (Spring: the latter may be unbounded). Do not claim N.
- **Single-sample estimators ignore run structure**: `undiscovered-failures` and KnowSum pool all draws; they cannot detect dependence between occasions. Our added value is exactly the replicated structure, but it also introduces the dependence problem.
- **Grey literature**: both Kansal repos are unrefereed and AI-assisted (self-declared); I read the code and results, but they should be cited as technical reports with DOIs, not as peer-reviewed findings.
- **Secondary numbers**: Nasr (1.5 million, 500 million), BoN (4.6% forecast error; the 53 to 71% figure), TAR table, and Si's 4,000/200 came through the search tool's paraphrase of PDFs; verify in the PDFs.

---

## 6. Datasets, code and tools

- Nasr et al.: paper PDF arxiv.org/pdf/2311.17035 (ICLR 2025 version at proceedings.iclr.cc); appendix A.8, Figure 9, Table 15 for the Good-Turing material.
- KnowSum code: github.com/Raina-Xin/KnowSum.
- Angell et al. code: github.com/rangell/LMTailRisk.
- Kansal repos: github.com/ParitKansal/undiscovered-failures (estimators.py, experiment.py, PREREG.md; Zenodo 10.5281/zenodo.23412807) and github.com/ParitKansal/label-error-capture-recapture (experiments/kill_v1, kill_v2 with `src/crc.py`, detector outputs in `data/`, `literature/NOVELTY.md`; Zenodo 10.5281/zenodo.23205993). Shallow clones for reading are in /home/user/paritkansal/ in this environment.
- MMLU-Redux (dataset revision pinned in the label-error repo: edinburgh-dawg/mmlu-redux-2.0, rev 372ea425445d51e1ba1188c56e5e893f8138621f).
- SnowBallSLR (capture-recapture recall estimation for snowballing reviews): github.com/s-matysik/SnowBallSLR (unread).
- Magma-based comparison of fuzzers and static analysers: arXiv 2505.22052.
- BoN jailbreaking code and data: see arXiv 2412.03556 (repository link not checked).

---

## 7. Search log (32 WebSearch calls; plus git reads of the two Kansal repos)

1. Nasr 2311.17035 Good-Turing extrapolation (extended)
2. Kalai-Vempala and Kalai et al. (extended)
3. Si et al. duplication (extended)
4. Nasr appendix Good-Turing 1.5M (extended)
5. Si et al. section 7.1 numbers (extended)
6. Jones et al. 2502.16797 (extended)
7. Wu and Hilton (standard)
8. Best-of-N jailbreaking (extended)
9. Bron Chao TAR 2404.01176 (extended)
10. ParitKansal undiscovered-failures (extended; web search found nothing, so the repos were cloned and read)
11. Mane et al. UMN missed positives (extended)
12. Lakkaraju unknown unknowns (standard)
13. McCabe semantic alphabet size (extended)
14. Blind-Spot Mass 2604.05057 (extended)
15. NOVA 2605.15219 (extended)
16. KnowSum / theorems (standard)
17. Capture-recapture in systematic reviews / e-discovery (extended)
18. Geer "The undiscovered" (standard)
19. Static analyser overlap and equivalent mutants (extended)
20. Kossen active testing plus EVT LLM tail risk (extended; EVT part returned finance only)
21. Quantifying Behavioral Tails / Iterative Unalignment / Simulating Deployment (extended)
22. Parulekar-Liu, SCARCE, Angell (extended)
23. Kossen active testing (standard)
24. KnowSum results (extended)
25. Nasr appendix again, exact extrapolation (extended)
26. Bron TAR details (extended)
27. Jones et al. Gumbel details (extended; no further numbers)
28. Si et al. 4,000/200 (extended)
29. Angell tail risks and Mind the Unseen Mass (extended)
30. Spring undiscovered vulnerabilities (extended)
31. Mind the Unseen Mass abstract (standard)
32. Geer Black Hat 2014 (standard)

Not found despite searches: Geer's "The Undiscovered" text; Jones et al. forecast-error numbers and Gumbel details; Wu-Hilton numerical margins; Lakkaraju numerical results; e-discovery legal acceptance of capture-recapture; static-analyser capture-recapture; equivalent-mutant estimation; any 2025-26 paper that applies replicated-run capture-recapture to LLM red-teaming (not searched again here; see G_novelty_check.md).
