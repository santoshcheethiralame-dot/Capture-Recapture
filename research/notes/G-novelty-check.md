# G. Novelty check: has anyone applied capture-recapture / unseen-species estimation to AI-safety discovery tools?

Date of search: 22 Oct 2026. Author: research agent G.

IMPORTANT COVERAGE CAVEAT. I ran 38 successful web searches (mix of standard and extended). The shared WebSearch budget (200 per turn, shared across all agents) ran out before I reached the 40+ requested, so about 8 planned queries were NOT run (listed at the end under "Not run"). I did not work around the limit. All search-engine results below were seen directly; anything I could not confirm is marked (unverified). Every search returned the same message in effect: no paper found that applies capture-recapture, Chao, jackknife or Lincoln-Petersen to SAE features, red-team attacks, audits, or automated-research outputs. Absence of evidence from a search engine is not proof; the "not found" verdict should be re-checked with arXiv full-text search and Google Scholar before submission.

---

## 1. Summary

- **No direct overlap found.** Across 38 queries (capture-recapture, mark-recapture, Lincoln-Petersen, multiple systems estimation, Chao1, jackknife, Good-Turing, missing mass, species accumulation, rarefaction, crossed with SAEs, red teaming, jailbreaks, audits, LLM bug-finding, benchmarks, AI incidents), no paper applies a capture-recapture or richness estimator to SAE features, red-team attack strategies, alignment audits, or automated-research outputs. The central claim of the proposal survives the search, with the caveats above.
- **The closest methodological precedent is "Mark-Evaluate" (Mordido and Meister, COLING 2020, arXiv 2010.04606).** It uses Petersen, CAPTURE and Schnabel mark-recapture estimators to evaluate generated text (quality and diversity) from embeddings. It is capture-recapture applied to NLP evaluation, but the "population" is the set of generated samples vs reference samples, not safety findings, and nobody estimates unseen features, attacks or behaviours. Must be cited as precedent for ecology-estimators-in-ML-evaluation.
- **The closest conceptual precedent for the red-team phase is STADS (Bohme, TOSEM 2018, arXiv 1803.02130) and its follow-ups** (residual-risk estimation in greybox fuzzing, ESEC/FSE 2021; "Dependency-aware residual risk analysis", ICSE 2026). It treats testing as species discovery and uses Good-Turing / Chao-style estimators to bound the probability that the next test finds something new. Not applied to LLMs or AI safety in anything I found. Must be cited; it is the strongest "this idea has precedent in software testing" reference.
- **Software-engineering capture-recapture for inspections is a 30-year-old literature** (Eick et al. 1992; Vander Wiel and Votta 1993; Briand et al. TSE 2000; sample-coverage estimators; correlated capture-recapture; Padberg). Its lesson is that estimates are unreliable (Padberg slides cite mean absolute error about 24%, max error -67% on NASA inspection data, tends to underestimate; models are strongly affected by number of inspectors; extreme under/over-estimation is common). This is the main pitfall evidence for the proposal.
- **Unseen-species estimators have just started to appear in LLM work, in other roles:** semantic alphabet size for uncertainty quantification (McCabe et al., ICLR 2026, arXiv 2509.14478; follow-ups SHADE 2604.19162 and SENECA 2605.00668), "Blind-Spot Mass" Good-Turing for deployment coverage (2604.05057, not LLM), and NOVA on fundamental limits of AI knowledge discovery (2605.15219, explicitly discusses Good-Turing). Reviewers will know these; the novelty claim must be scoped to "safety discovery tools and their findings".
- **SAE-side: the raw ingredient (cross-seed feature mismatch) is heavily studied, but nobody converts it into a population estimate.** Paulo and Belrose (ICLR 2026) report only about 30% of features shared across seeds at 131K latents on Llama 3 8B. Leask et al. (ICLR 2025) use stitching and meta-SAEs to show incompleteness. Gerasimov et al. (2606.12138) define "feature stability" as the estimated chance that a similar feature shows up in an independently trained SAE, which is literally a per-feature capture probability, but they do not estimate total population size. Ghosh et al. (2610.20680, 14 Oct 2026) report strictly matched features rising from 2% at 5M tokens to 29% at 50M on Gemma-2-2B BatchTopK. These are all raw data for a recapture analysis and also the strongest "near-miss" papers a reviewer will raise.
- **Red-team side: discovery curves and rare-event methods exist, but no richness/population estimator.** STING (2602.16346, ICML 2026) uses time-to-first-jailbreak survival analysis and a "Restricted Mean Jailbreak Discovery" metric. SCARCE (2606.29623) estimates rare-event rates for jailbreak fleets via subset simulation. Kaur (2607.21735) derives "evidential ceilings" for what a red-team null result can prove. None estimates the number of distinct attack strategies not found.
- **Audit side: AuditBench (arXiv 2602.22755, as shown in the search result URL; unverified details) gives 56 models with implanted behaviours across 14 behaviour types**, i.e. known ground truth for "what auditors miss". It is a testbed, not an estimator. I found no multi-auditor overlap-based estimate.
- **LLM vulnerability discovery (Big Sleep, AIxCC, OSS-CRS):** I found no overlap-based "how many remain" estimation. The AIxCC SoK (2602.07666) notes teams converged on similar architectures, which implies positively correlated catchability (a violation of independence) but I could not read an overlap table (unverified whether it exists).
- **AI incident databases:** no capture-recapture undercount study found, despite the method being standard for undercount in epidemiology and injury data. This is a possible fourth application and an adjacent novelty claim, but it is outside the three phases.
- **Verdict:** The proposal is novel as stated, provided it is framed as (a) the first systematic validation of richness / capture-recapture estimators against known truth for safety discovery tools, and (b) the first failure-mode map of those estimators in these settings. It is NOT novel as "using species estimators on ML outputs" (Mark-Evaluate, semantic alphabet size, STADS, Blind-Spot Mass all precede it).

---

## 2. Papers and sources, with classification

Classification key: DIRECT = same idea in same domain; PARTIAL = same estimator family or same domain but a different target; TOOL = related method/tool; DATA = testbed or raw ingredient; NONE = checked and not related.

### 2.1 Capture-recapture / species estimation applied to ML or LLM evaluation (methodological precedents)

**Mark-Evaluate: Assessing Language Generation using Population Estimation Methods.** Mordido and Meinel (authors verified), COLING 2020. arXiv 2010.04606; ACL Anthology 2020.coling-main.178. https://arxiv.org/abs/2010.04606
- What they did: Adapt mark-recapture and maximum-likelihood population estimators from wildlife ecology to evaluate text generation. Three metrics: ME_Petersen and ME_CAPTURE (single-valued) and ME_Schnabel (double-valued: quality and diversity). Samples are contextual word or sentence embeddings. Reported higher correlation with human evaluation than existing metrics on unconditional generation, MT and summarization.
- Classification: **PARTIAL (method precedent), NOT a safety application.** The "individuals" are embedding points, not discovered safety artefacts, and the goal is a quality/diversity score, not an estimate of what a discovery tool missed.
- Use for us: cite as the earliest ML use of Petersen/Schnabel estimators; differentiate (they do not validate against a known population, and identity is soft embedding neighbourhoods, which is precisely the identity-matching problem we need to study).

**Estimating Semantic Alphabet Size for LLM Uncertainty Quantification.** McCabe, Melamed, Hartvigsen, Huang. ICLR 2026. arXiv 2509.14478. https://arxiv.org/pdf/2509.14478
- What they did: Frame the number of distinct meanings an LLM can give for a prompt as an unseen-species problem; use Good-Turing sample coverage (1 - f1/n) and an alphabet-size estimate |S|_GT = k n / (n - f1) to correct plug-in semantic entropy. Follow-ups: SHADE (arXiv 2604.19162, generalized Good-Turing plus a graph heat-kernel trace) and SENECA (arXiv 2605.00668).
- Classification: **PARTIAL (same estimator family on LLM outputs, different target: hallucination/uncertainty, not safety-tool findings).**
- Use for us: shows reviewers already accept Good-Turing for LLM semantic clusters, and the clustering step (entailment) is the analogue of our identity-matching step.

**Blind-Spot Mass: A Good-Turing Framework for Quantifying Deployment Coverage Risk in ML Systems.** Pal, Bhattacharya, Singh. arXiv 2604.05057 (Apr 2026, under review at JMLR). https://arxiv.org/abs/2604.05057
- What they did: Good-Turing unseen-mass reasoning generalised to a threshold B_n(tau), the probability mass of deployment states with fewer than tau training observations. Tested on wearable activity data (about 95% of deployment mass below tau=5) and MIMIC-IV. A companion "Stochastic Gap" paper (arXiv 2603.24582) applies the idea to agentic AI state-action occupancy (details unverified).
- Classification: **PARTIAL (Good-Turing for ML reliability, not safety discovery tools; no capture-recapture).**

**NOVA: Fundamental Limits of Knowledge Discovery Through AI.** Avestimehr, Duffy, Medard. arXiv 2605.15219 (May 2026, v3 Aug 2026). https://arxiv.org/abs/2605.15219
- What they did: Theory of generate-verify-accumulate-retrain loops as adaptive sampling over a knowledge space. Argue Good-Turing is a local diagnostic of batch diversity and NOT a measure of the total undiscovered valid mass; cost scaling Theta(c_gen D^alpha) under a Zipf tail. References Good (1953) and Efron-Thisted (1976).
- Classification: **PARTIAL, important.** Conceptually the closest to Phase 3 "automated research" (what a discovery loop leaves undiscovered), and it explicitly cautions that Good-Turing does not estimate total undiscovered mass. Read in full before writing the related-work section; it is a theoretical argument that our estimators may be fundamentally limited under heavy tails. I read only the abstract and introduction-level summary.

**Estimating "How Much is Unseen Depends Chiefly on Information About the Seen"** (arXiv 2402.05835). Seen in a result list only; the title states the key theoretical point (unseen mass is bounded only given information about the seen). Classification: TOOL (theory background). Content unverified.

**Optimal prediction of the number of unseen species** (Orlitsky, Suresh, Wu, PNAS 2016). Classification: TOOL (estimator background); seen only as a reference in a search summary.

### 2.2 Software testing and defect estimation (the classical lineage the proposal cites)

- **STADS: Software Testing as Species Discovery.** Bohme, TOSEM 2018. arXiv 1803.02130. https://arxiv.org/abs/1803.02130. Treats test inputs as samples and paths/bugs as species; estimates probability of discovering a new species with the next input; gives residual-risk bounds using Good-Turing family estimators. **TOOL / conceptual precedent for Phase 3 and for stopping rules.** No LLM application found.
- **Estimating Residual Risk in Greybox Fuzzing.** Bohme, ESEC/FSE 2021. https://dl.acm.org/doi/pdf/10.1145/3468264.3468570. Same lineage. TOOL.
- **Dependency-aware Residual Risk Analysis.** Lee and Bohme (ICSE 2026). https://mboehme.github.io/paper/ICSE26-dependency.pdf. Relaxes independence between species in residual-risk estimates. **Directly relevant to our dependence problem** (features and attacks are not independent species). Content only seen as a title and snippet (unverified).
- **Assurance in Software Testing: A Roadmap.** Bohme, arXiv 1807.10255. TOOL.
- **A comprehensive evaluation of capture-recapture models for estimating software defect content.** Briand, El Emam, Freimut, Laitenberger, IEEE TSE 2000. https://www.simula.no/research/comprehensive-evaluation-capture-recapture-models-estimating-software-defect-content. Finding (as summarised in search results): few studies compare estimates with actual remaining defects; accuracy depends strongly on number of inspectors. TOOL / pitfall evidence.
- **Sample-coverage estimators best suited to software inspections** (NDSU thesis result, https://library.ndsu.edu/ir/handle/10365/26714) and **Estimating the number of undetected software errors via the correlated capture-recapture model** (LSU, https://repository.lsu.edu/infosys_pubs/66; proposes a correlation-matrix correction to the independence assumption). TOOL.
- **Padberg slides** (https://ps.ipd.kit.edu/807.php): mean absolute error about 24%, worst error -67% on NASA inspection data; underestimation is typical. Pitfall evidence.
- **Microsoft Research blog, "Estimating Hidden Bug Count" (Parts 1-3).** https://www.microsoft.com/en-us/research/blog/estimating-hidden-bug-count-part-1-3. TOOL, accessible exposition.
- Classification for the whole block: **TOOL; none touches AI safety.**

### 2.3 SAE-side near misses (the raw ingredient is all there; the estimator is missing)

| Paper | What it did | Class |
|---|---|---|
| Paulo and Belrose, "SAEs Trained on the Same Data Learn Different Features", ICLR 2026, arXiv 2501.16615, https://arxiv.org/abs/2501.16615 | Seeds differ only in init; 131K-latent SAE on Llama 3 8B feedforward layer shares about 30% of features across seeds; seen across layers, 3 LLMs, 2 datasets, several architectures; ReLU/L1 SAEs more stable than TopK | DATA / PARTIAL. Measures overlap but never turns it into a population estimate. Must-cite, and the best source of real cross-seed overlap data. |
| Leask et al., "SAEs Do Not Find Canonical Units of Analysis", ICLR 2025, arXiv 2502.04878 | Stitching shows larger SAEs hold latents smaller SAEs lack; meta-SAEs show non-atomicity; no single width gives a complete dictionary | PARTIAL. Qualitative incompleteness claim; no number for what is missing. |
| Gerasimov et al., "Unstable Features, Reproducible Subspaces", arXiv 2606.12138 (Jun 2026), https://arxiv.org/abs/2606.12138 | Defines feature stability as estimated chance a similar feature appears in an independently trained SAE; stable features carry most reconstruction signal; unstable ones concentrate in reproducible lower-rank subspaces. A review notes the split depends on an unvalidated cross-seed similarity threshold | PARTIAL / closest SAE near miss. Per-feature "capture probability" is exactly the heterogeneity we model, but no total-population estimate, no validation vs known truth. Their threshold-sensitivity weakness is our identity-matching risk. |
| Ghosh et al., "Diminishing Returns of Data in SAEs: Functional Behavior does not Guarantee Feature Reproducibility", arXiv 2610.20680 (14 Oct 2026), https://arxiv.org/abs/2610.20680 | 4 architectures, 3 LMs, 5M to 500M tokens; strictly matched features rise 2% to 29% (5M to 50M tokens, Gemma-2-2B BatchTopK) while functional metrics saturate early | DATA / PARTIAL. Shows catchability depends on training budget, i.e. capture probability is not constant across "occasions". Very recent: check for overlap again before submission. |
| Song et al., "Position: Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs", arXiv 2505.20254 | Calls for measuring cross-run consistency (PW-MCC) | PARTIAL (motivation). Also "Enforcing Orderedness to Improve Feature Consistency", arXiv 2512.02194; "Stable and Steerable SAEs with Weight Regularization", arXiv 2603.04198 (ICML 2026). |
| Korznikov et al., "Sanity Checks for SAEs", arXiv 2602.14111 | Synthetic data, SAEs recover about 9% of true features | DATA (already in proposal). |
| Chanin, "Are SAE Benchmarks Reliable?", arXiv 2605.18229 | Reseed noise plus synthetic ground truth | DATA (already in proposal). |
| Gao et al., "Scaling and Evaluating SAEs", ICLR 2025, arXiv 2406.04093 | Notes SAEs must be very large to recover all features; checks recovery of hypothesised features | NONE for estimation. |
| LessWrong "[Research report] SAEs find only 9/180 board state features in OthelloGPT" (later revised to 33/180) | Ground-truth coverage vs supervised probes | DATA. The fractions recovered vs probe-defined truth is a ground-truth coverage testbed. |
| LessWrong tiny-LM post estimating "512-1024 features" in a layer, about 600 easily labellable | Hand-count/labelling heuristic, no statistical estimator | NONE/PARTIAL (the only explicit "how many features" estimate I found; not capture-recapture). Exact post title and author not captured. |
| LessWrong comment on Anthropic Scaling Monosemanticity extrapolating ~67M features for Sonnet | Informal scaling guess | NONE, but shows the question "how many features exist" is asked and answered only by guessing. |
| "Decoding Dark Matter: Specialized SAEs for Rare Concepts", arXiv 2411.00743 | Rare concepts missing from SAEs | PARTIAL (the unseen-rare-features problem, no estimator). Content from title only. |
| "Feature Starvation as Geometric Instability in SAEs", arXiv 2605.05341; "From Geometric Recovery to Causal Validation: A Reproducible Audit of SAE Features", arXiv 2607.12166 | Seen as titles only | Unverified; check if they quantify unrecovered features. |

Verdict for Phase 1: **no direct overlap found. High risk of a "scooping" paper because the pieces (cross-seed overlap, synthetic ground truth, stability probability) are all in the literature as of Oct 2026. Move fast and cite Gerasimov et al. and Paulo and Belrose as the starting point.**

### 2.4 Red-team side

| Paper | What it did | Class |
|---|---|---|
| Talokar et al., "Helpful to a Fault" (STING), ICML 2026, arXiv 2602.16346, https://arxiv.org/abs/2602.16346; code github.com/epfl-nlp/helpful-to-a-fault | Automated multi-turn red teaming for tool agents; frames red teaming as time-to-first-jailbreak; discovery curves, hazard-ratio attribution by language, Restricted Mean Jailbreak Discovery (RMJD). Up to 107% higher illicit-task completion than single-turn baselines | PARTIAL / closest red-team near miss. Survival-analysis flavour of "how fast do we find failures", not "how many remain". Andriushchenko is a co-author (also on the adaptive-attack paper in the proposal). |
| Kaur, "What AI Red-Team Evaluations Can and Cannot Prove", arXiv 2607.21735 (Jul 2026, v2), https://arxiv.org/abs/2607.21735; code github.com/hackwither/evidential-limits | "Evidential ceiling": closed-form bound on how much a benchmark null result can shift belief; rare-event limits; audits 8 evaluation suites (adequate for frequent harms, orders of magnitude short for rare catastrophic ones); applies to adaptive red teaming via elicitation rates | PARTIAL. Same motivation (coverage of red teaming). Different method: Bayesian evidence for a given harm rate, not estimating the number of unseen attack types. Must cite. |
| Wang et al., SCARCE, arXiv 2606.29623, https://arxiv.org/abs/2606.29623 | Subset simulation with learned embedding "rulers"; jailbreak fleet-level threat model, about 2.6% mean relative error on Llama-Guard-3-8B hidden states for adversarial fraction >= 1e-3 | TOOL. Rare-event rate estimation, not count of unknown strategies. |
| Stable-GFlowNet (arXiv 2605.00553, ICML 2026) and a commentary at groundy.com ("why ai red teaming rediscovers the same jailbreaks and misses the rest") | Claim automated attackers rediscover a narrow band of jailbreaks | PARTIAL (supports the "rediscovery means undercount" premise qualitatively, not an estimator). Primary paper details unverified; the commentary is a secondary blog. |
| Jotautaite et al. MonitoringBench, arXiv 2605.09684; Terekhov et al. adaptive attacks, arXiv 2510.09462 | Already in proposal | Motivation. |
| SIRAJ (arXiv 2510.26037), "Guarding the Guardrails" jailbreak taxonomy (arXiv 2510.13893, 50 strategies in 7 families), SoK jailbreak robustness (arXiv 2605.05058) | Diversity/coverage metrics, taxonomies of strategy classes | TOOL / DATA. The 50-strategy, 7-family taxonomy is a candidate fixed rubric for the identity step in Phase 3. Details only from snippets. |
| EvalSafetyGap (arXiv 2606.30219); "LLM-Safety Evaluations Lack Robustness" (arXiv 2503.02574) | Surveys/analysis of evaluation reliability | NONE for estimation. |
| "Lessons from Red Teaming 100 Generative AI Products" (arXiv 2501.07238) | Qualitative; "the work is never finished" | NONE (quotable motivation). |

Verdict for Phase 3: **no direct overlap found.** The closest framings are survival/discovery-curve (STING), evidential bounds (Kaur) and rare-event rate (SCARCE). A rigorous estimate of unseen strategy count with planted truth is not in any of them.

### 2.5 Audits / automated research / agentic discovery

| Source | What it did | Class |
|---|---|---|
| AuditBench (arXiv 2602.22755, URL only seen; details from a search summary, unverified) | 56 models with implanted hidden behaviours across 14 types; models do not confess when asked; known ground truth | DATA. Best candidate testbed for "how many behaviours did auditors miss", with many auditors per model for recapture. |
| Anthropic "Building and evaluating alignment auditing agents" (alignment.anthropic.com/2025/automated-auditing) and Petri (alignment.anthropic.com/2025/petri; 14 frontier models, 111 seed instructions) | Auditing agents (investigator, evaluation builder, breadth-first red-teaming agent) and open-source auditor | DATA / TOOL. Reports findings per agent, no overlap-based estimate seen. Multiple runs per model could be re-analysed. |
| "Automating Auditing Games of Sandbagging" (NeurIPS 2026 listing, https://neurips.cc/virtual/2026/169826) | Black-box auditors catch only one organism consistently; white-box tools do not reliably help | DATA (heterogeneous catchability evidence). Snippet only. |
| Marks et al. 2503.10965; Taylor et al. 2512.07810; Chen et al. 2608.28945; Anthropic automated W2S researcher | Already in proposal | Motivation. None estimate unseen. |
| SoK: DARPA AIxCC, arXiv 2602.07666 (v2); OSS-CRS, arXiv 2603.08566; Team Atlanta results; DARPA results page https://www.darpa.mil/news/2025/aixcc-results | 7 finalists, 53 challenge projects, 63 challenge vulnerabilities in 24 repos; architectural convergence on fuzzing plus LLM detection; cross-team PoV scoring | DATA. Cross-team findings against a planted set is the best real-world "multiple LLM-agent systems, known truth" capture-recapture dataset. I could not confirm whether overlap tables are published (unverified). |
| Google Big Sleep / Project Zero | 20 flaws found, SQLite CVE-2025-6965 | NONE for estimation (news coverage only). |
| Repeated search of "LLM agents bug finding independent runs overlap unique bugs residual" | Nothing relevant; LogicHunter (arXiv 2607.06195) reports 40 unique bugs vs 32 root-cause clusters, showing the identity-unit problem | NONE, but a nice illustration that counting unit changes the total. |

### 2.6 Other adjacent areas searched

- **Benchmark/label errors:** Northcutt et al. "Pervasive Label Errors in Test Sets" (NeurIPS 2021, arXiv 2103.14749) estimates error rates by confident learning plus crowd validation (at least 3.3% average, at least 6% in ImageNet val; 51% of flagged candidates were real errors). "Are We Done with MMLU?" (Gema et al., arXiv 2406.04127) estimates 6.49% erroneous via random-sample re-annotation of 5,700 questions (Virology 57%). REC-D (arXiv 2508.06556) on KITTI claims detectors miss up to 66% of errors. **None uses capture-recapture; classification NONE/related. This is an open, adjacent application (estimating remaining benchmark errors from overlap between independent error finders) and is a natural extension.**
- **AI incidents:** AI Incident Database papers (arXiv 2409.16425, 2501.17037, 2604.21412) discuss passive submission and incompleteness; no capture-recapture undercount study found. Capture-recapture is standard for undercount in other harm data (e.g. law-enforcement deaths in PLOS Medicine 2017, firearm injuries). NONE, but an unclaimed adjacent niche.
- **Memorization:** Nasr et al. "Scalable Extraction of Training Data" (arXiv 2311.17035) explicitly says total memorization cannot be extrapolated from emission rate and estimates it by modelling how often output is new; SoK Memorization (arXiv 2310.18362) says extractability underestimates. **PARTIAL in spirit (they use a species-style accumulation argument; I did not verify whether they use a Good-Turing estimator).**
- **Mechanistic interpretability generally:** no hits for capture-recapture/unseen species in circuits or neuron work.
- **Statistics background:** Good-Turing for feature allocation models (arXiv 1902.10490; Favaro et al.; "A Good-Turing estimator for feature allocation models") is the natural unseen-species theory for overlapping features such as SAE latents. TOOL; strongly recommended to adopt (an SAE latent set per run behaves like a feature-allocation, not a partition).

---

## 3. Verdict

### What is genuinely novel (no prior work found)
1. Using capture-recapture or richness estimators (Lincoln-Petersen, Chao, jackknife, log-linear, sample coverage) to estimate the total number of SAE features, or the number missed by any one SAE.
2. Validation of such estimators against synthetic SAEs with known feature count, including the bias as a function of dictionary size, sparsity, and matching threshold. (Closest: Gerasimov et al. stability probability, Paulo and Belrose overlap, Chanin reseed noise; none estimate N.)
3. Estimating the number of unseen attack strategies from multiple independent red teams with planted attacks; and estimating unseen hidden behaviours from multiple auditors/agents.
4. A systematic map of how the estimators' assumptions (independence, equal catchability, identity) fail for these tools (shared-model blind spots between LLM attackers, matching-threshold sensitivity, training-budget-dependent catchability).
5. The headline reporting norm "we found N and estimate M were missed" for safety tools.

### What is already done (must cite and differentiate)
- Ecological estimators in ML evaluation: Mark-Evaluate (COLING 2020).
- Unseen-species / Good-Turing on LLM outputs: McCabe et al. (ICLR 2026), SHADE, SENECA; Blind-Spot Mass; NOVA (explicit Good-Turing discussion for AI discovery).
- Species-discovery framing of testing with residual-risk bounds: STADS (Bohme), residual-risk fuzzing, dependency-aware residual risk.
- Capture-recapture for software inspection defects with known weaknesses: Eick 1992, Vander Wiel and Votta 1993, Briand 2000, correlated capture-recapture, sample-coverage estimators.
- Cross-seed SAE feature instability and incompleteness: Paulo and Belrose, Leask et al., Gerasimov et al., Ghosh et al., Song et al., Korznikov, Chanin.
- Red-team coverage statistics: STING's discovery curves/RMJD, Kaur's evidential ceiling, SCARCE.

### How to position the paper
- Title/framing: "Estimating what safety tools miss: a validated capture-recapture toolkit with known-truth testbeds" rather than "first to use species estimators on AI".
- Lead with Phase 1 (synthetic truth): it is the cleanest contribution and the most exposed to scooping, because several groups already hold cross-seed matching code. Publish a preprint early.
- Frame the contribution as a validation and failure-map study (bias, coverage of intervals, threshold sensitivity), explicitly building on the SE capture-recapture failure record (24% MAE, underestimation, dependence on number of inspectors) and on Bohme's dependence-aware work. Say plainly that Chao1 is a lower bound and assumes independence; report when it fails.
- Treat NOVA's warning (Good-Turing does not estimate total undiscovered valid mass) as a hypothesis to test empirically, not just cite.
- Use a feature-allocation view (Good-Turing for feature allocation models, Favaro et al.) for SAE latents, because they overlap, not partition.
- Phase 3 testbeds: AuditBench (56 organisms, many auditors), AIxCC cross-team results (known planted vulnerabilities), jailbreak taxonomies for a fixed rubric.
- Add an adjacent low-cost extension (benchmark label errors, AI incident undercount) only as a short discussion item, not a main claim.

### Natural collaborators / reviewers (from authors seen in results; none contacted, affiliations not all verified)
- Marcel Bohme (STADS, residual-risk fuzzing; MPI-SP) and Seongmin Lee: the species-discovery-for-testing lineage, strongest statistical-software link.
- Gonçalo Paulo, Nora Belrose (EleutherAI): cross-seed SAE overlap; have the matching code and data.
- Gerasimov, Rusalev, Balagansky, Laptev, Kurochkin, Gavrilov: feature stability as capture probability.
- Patrick Leask, Joseph Bloom, Neel Nanda, Lee Sharkey, Bart Bussmann, Stefan Heimersheim (Leask et al. authors); David Chanin (SAE benchmark reliability); Korznikov, Oseledets, Tutubalina (synthetic SAEs).
- Xiangchen Song and colleagues (CMU): feature consistency.
- Maksym Andriushchenko, Antoine Bosselut (EPFL), Jonas Geiping, Egor Zverev-type attack researchers (STING and adaptive-attack authors): red-team side.
- Redwood-affiliated authors of MonitoringBench (Jotautaite, Martinez, Matthews, Tracy): under-elicitation framing.
- Sam Marks, Samuel Bowman-adjacent Anthropic auditing group, UK AISI/FAR.AI sandbagging authors (Taylor, Black, Cundy, Bloom), AuditBench authors (unverified who): audit side.
- McCabe, Melamed, Hartvigsen, Huang (semantic alphabet size): same estimator family for LLM outputs.
- Avestimehr, Duffy, Medard (NOVA): theory of undiscovered mass in AI discovery loops.
- Bandana Kaur (evidential ceilings in red-team evals).
- Statisticians: Anne Chao (Chao estimators; background knowledge, not from these searches), Federico Camerlenghi, Stefano Favaro, Lorenzo Masoero (Good-Turing for feature allocation / unseen features; names from background knowledge, verify), Orlitsky/Suresh/Wu (unseen-species optimality), Briand, Padberg and Votta (software capture-recapture).

---

## 4. Leads and experiment ideas
- Re-analyse existing multi-seed SAE releases: Paulo and Belrose released SAEs across seeds (check EleutherAI release); run Chao2 on the incidence matrix (features x seeds) and compare to the rise in matched fraction with data (Ghosh et al.: 2% to 29%) to test if estimated N is stable as budget changes. If N shifts with training budget, catchability is not constant: a clean negative result.
- Use Gerasimov et al.'s per-feature stability as a covariate in a heterogeneous (Mh, Chao) model; test whether its stable/unstable split corresponds to high/low capture probability.
- Phase 3 using AIxCC and AuditBench: treat each team/auditor as an occasion, compare estimated vs planted total.
- Add a "correlated catchability" experiment: LLM red-teamers from the same model family vs different families, to quantify the dependence bias predicted by the SE literature.
- Stopping rule: use STADS-style discovery probability U to say "stop red-teaming when U < threshold" and compare with RMJD discovery curves.

## 5. Pitfalls
- Reviewers will cite Mark-Evaluate, STADS and semantic alphabet size: do not claim "first use of ecological estimators in ML".
- The Ghosh et al. and Gerasimov et al. papers are only weeks to months old; the SAE niche is moving fast. Run a final scoop check immediately before posting.
- NOVA argues Good-Turing is only a local diagnostic: a theoretical objection to Phase 3 and to heavy-tailed attack populations.
- The SE record shows capture-recapture often underestimates and is highly sensitive to number of inspectors; use enough "occasions" and report CIs.
- Gerasimov et al. note the stable/unstable split depends on the similarity threshold: identity matching remains the core threat.

## 6. Datasets, code, tools (as seen)
- R: Rcapture, SPECIES, iNEXT (Chao) packages (from background knowledge; not verified in search); lllcrc (local log-linear capture-recapture, https://rdrr.io/cran/lllcrc/, seen in search).
- github.com/hackwither/evidential-limits (Kaur); github.com/epfl-nlp/helpful-to-a-fault (STING).
- AuditBench (arXiv 2602.22755), Petri (alignment.anthropic.com/2025/petri), AIxCC / OSS-CRS (arXiv 2603.08566).
- Paulo and Belrose SAE releases (EleutherAI; check Hugging Face).

## 7. Search log (38 successful queries)
Standard: capture-recapture + SAE features; mark-recapture + red teaming/jailbreaks; Good-Turing + red teaming coverage; Chao1 + failure modes; "how many features does a language model have"; capture-recapture + LLM bug discovery; "capture-recapture" LLM; "mark-recapture" LLM evaluation; capture-recapture + benchmark label errors; Lincoln-Petersen + interpretability/red teaming/AI safety; species accumulation / rarefaction + red teaming; multiple systems estimation + AI incidents; feature consistency SAE; LessWrong capture-recapture + interpretability/alignment; Alignment Forum capture-recapture + auditors; Big Sleep overlap; AIxCC overlap; MMLU error estimation; species richness estimators + LLM outputs; red teaming saturation / attack-space; Good-Turing/missing mass + jailbreak stopping rule; interpretability + capture-recapture/unseen species; alignment auditing overlap; capture-recapture + LLM code review; capture-recapture + memorization/hallucination.
Extended: Helpful to a Fault; NOVA; Blind-Spot Mass; SCARCE; What AI Red-Team Evaluations Can and Cannot Prove; STADS/Bohme; Semantic Alphabet Size; SAEs trained on same data learn different features; "estimating how many features SAEs miss"; SoK AIxCC; Unstable Features Reproducible Subspaces; LLM agents bug-finding overlap/residual risk; Diminishing Returns of Data in SAEs.

### Not run (budget exhausted; recommend a follow-up)
- capture-recapture + AI scientist / automated research ideas overlap
- unseen-species + LLM idea-generation saturation
- AuditBench details (overlap between auditors, number of behaviours)
- Bayesian nonparametric / Indian buffet process unseen features in neural representations
- arXiv/OpenReview/ACL-specific site-restricted queries ("Chao" "jackknife" + SAE; "species richness" + red teaming)
- LessWrong / Alignment Forum direct title search on "missing mass", "unknown unknowns coverage red-team"
- Neuron/circuit-level "how many circuits" estimation, ICML/NeurIPS workshop listings 2025-2026
- Lab blogs (OpenAI, DeepMind, Apollo) for audit-overlap statements
