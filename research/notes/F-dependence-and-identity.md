# F. Dependence between AI catchers, identity with LLMs/embeddings, and competing approaches

Project: "What did we miss? Capture-recapture for safety tools". Date of research: 22 Oct 2026.

**Important coverage note.** The WebSearch budget for the session ran out (limit of 200 searches per turn, shared across agents) after about 30 searches. Sections 1 and 2 are well covered. **Sub-theme 3 (alternatives: Jones et al. rare behaviours, Wu and Hilton, EVT, IRT, active testing, unknown-unknowns) could not be searched at all.** It appears below only as a clearly marked list of unverified leads from memory, with no IDs. A follow-up search pass is needed there. Where a number came from a secondary summary rather than the paper itself, it is marked.

---

## 1. Summary (key takeaways)

1. **Same-family and similar-capability LLMs err together.** Kim et al. (ICML 2025, 350+ LLMs): on one leaderboard, two models agree about 60% of the time when both are wrong; correlation is higher within a company and for larger models. For capture-recapture (CR) this is positive between-catcher dependence, which biases N-hat **downward** (the catchers overlap more than independent catches would, so the Lincoln-Petersen estimate N = n1 n2 / m is too small).
2. **Dependence grows with capability.** Goel et al. (ICML 2025, CAPA) report that more capable models have more correlated failures, and LLM judges favour models like themselves. Stronger attacker agents will therefore be more, not less, dependent, so the problem worsens over time.
3. **Effective independent catchers is a usable statistic.** Kohli (2605.29800) shows a panel of 9 judges from 7 families carries about 2 effective independent votes (Kish n_eff 2.0 to 2.5), stable across prompts and temperatures. The same "effective number of independent catchers" idea can be reported alongside any CR estimate.
4. **Output homogeneity is very high even across providers.** Artificial Hivemind (NeurIPS 2025 best paper per one secondary source): intra-model repetition under temperature 1.0 and top-p 0.9, plus inter-model similarity of about 0.71 to 0.82 (secondary figure). Temperature and ensembling of models do not guarantee diversity.
5. **Idea generation saturates fast.** Si et al. (ICLR 2025): 4,000 seed ideas per topic gave only about 200 unique after cosine-0.8 dedup (about 5%), and unique ideas plateaued. This is a direct, quoted example of LLM "catches" collapsing onto the same individuals. It is also a natural test bed for CR (unique-count curves are exactly species-accumulation curves).
6. **Post-training reduces diversity** (Kirk et al., ICLR 2024: RLHF lowers output diversity vs SFT). RL-trained red-teamers likewise produce homogeneous attacks unless diversity is rewarded (Beutel et al. 2412.18693 and others below). So catchability heterogeneity is partly a training artefact.
7. **Humans and automated red-teamers appear complementary rather than overlapping** (qualitative evidence only, no controlled overlap measurement found). Humans find multi-turn, payload-splitting and past-tense strategies that automated pipelines miss; automated white-box attacks find unnatural inputs humans miss. This is a case for a human-vs-LLM "two-list" Lincoln-Petersen test, and a warning that the two lists estimate different sub-populations (a heterogeneity problem, not just a dependence one).
8. **Identity is the dominant uncertainty and is a tunable knob.** The number of clusters (hence N) depends directly on the similarity threshold or granularity prompt. No paper found measures this for attack/behaviour taxonomies; it is open and publishable.
9. **LLM clustering is not stable by default.** Papers in the results (CAST 2602.15861, LLM-MemCluster 2511.15424, an SE-taxonomy study 2608.01592) explicitly address run-to-run instability of LLM-generated labels and taxonomies. One reported ARI seed variation margin was about 5%; granularity is controlled by prompt strictness.
10. **Microbial ecology is the closest precedent and a direct warning.** Species-richness estimates depend on the OTU threshold, and sequencing errors create spurious singletons that inflate Chao1 and related estimators (Kunin 2010; Dickie 2010; Chiu and Chao 2016). Denoising pipelines then delete singletons and make Chao1 meaningless (Deng et al. 2024). AI catchers have the same two failure modes: hallucinated or near-duplicate "unique" finds inflate f1, and aggressive dedup removes f1.
11. **The Chiu-Chao treatment of spurious singletons is formally a record-linkage-error model** (a 2024 Environ Ecol Stat paper treats them as false-negative record-linkage errors). This is the right framework for "two attacks that are really the same but were not matched". Link-error-aware CR is the methodological bridge.
12. **Hierarchical identity needs a multi-resolution design.** Report N-hat at family, technique and instance level, and show the curve of N-hat versus threshold, as microbial ecologists do (DOTUR: richness at 0%, 3%, 5%, 10% difference; terminal estimates in one cited study spanned roughly 9.9k to 325k OTUs).
13. **Auditing agents give a cheap replicated-catch testbed.** AuditBench (2602.22755): 56 target models with 14 hidden behaviours, 13 tool configurations, 16 runs per target per configuration. Some behaviours (flattery, emotional bonding, self-promotion) are found nearly always (very high catchability); context-dependent ones (secret loyalty, data poisoning, contextual optimism) rarely. That is a ready-made heterogeneity gradient with ground truth.
14. **Alternatives are complements, not substitutes (from background knowledge only; see section 6).** Rare-behaviour forecasting and importance sampling estimate the probability of known behaviours; CR/unseen-species estimators estimate the number of unknown categories. They answer different questions.

---

## 2. Papers

### 2.1 Correlated catchers (LLM error and output dependence)

**Kim, Garg, Peng, Garg (2025). "Correlated Errors in Large Language Models." ICML 2025 (PMLR 267). arXiv:2506.07962.** https://arxiv.org/abs/2506.07962 , https://proceedings.mlr.press/v267/kim25e.html
- Found: 350+ LLMs on two leaderboards and a resume-screening task. On one leaderboard dataset, models agree about 60% of the time when both are wrong. Correlation is higher for models from the same company and for larger models; diversity of architecture/provider/training data does not remove it. Downstream: LLM-as-judge inflates same-family models, and hiring outcomes show monoculture-style homogenisation.
- Why it matters: gives an empirical prior for the dependence between catchers. A "2 attackers from the same family" design is a dependent design.
- Open/unverified: I did not see cross-provider percentages (only the 60% headline and the within-company/size trends from a reviewer-style summary).

**Goel, Struber, Auzina, Chandra, Kumaraguru, Kiela, Prabhu, Bethge, Geiping (2025). "Great Models Think Alike and this Undermines AI Oversight." ICML 2025. arXiv:2502.04313.** https://arxiv.org/abs/2502.04313 , https://proceedings.mlr.press/v267/goel25b.html (author list from memory, unverified beyond Goel)
- Found: introduces CAPA (Chance Adjusted Probabilistic Agreement): agreement on errors corrected for what accuracy alone predicts, using output probabilities. 0 means chance agreement. LLM judges favour more similar models; weak-to-strong gains are larger when supervisor and student are more different; more capable models have more correlated errors.
- Why it matters: CAPA is a ready-made pairwise dependence metric for catchers. In CR terms it is an observed-vs-expected-overlap ratio adjusted for catchability.
- Open: designed for multiple-choice-style correctness, not for open-set discovery lists. Needs adapting (e.g. compare m_obs against m_expected = n1 n2 / N for the planted truth).

**Kohli (2026). "Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM Evaluation Panels." arXiv:2605.29800.** https://arxiv.org/abs/2605.29800
- Found: 9 frontier LLMs, 7 families, 3 NLI datasets. Kish effective sample size n_eff is about 2.0 to 2.5 across prompt variants and two temperatures (RewardBench pairwise n_eff = 2.0). Panel accuracy is 8 to 22 points below the independent-votes (Condorcet) prediction; best single judge matches or beats the panel; known aggregation methods close at most 11% of the gap. (Some aggregator sites give conflicting model names and n_eff = 2.18; trust the arXiv paper.)
- Why it matters: "effective number of independent catchers" is a clean way to report dependence in a CR study, and the null result that adding more judges (catchers) from similar models helps little is the same as "K = 9 occasions behaves like K = 2".

**Jiang et al. (2025). "Artificial Hivemind: The Open-Ended Homogeneity of Language Models (and Beyond)." NeurIPS 2025 (Datasets and Benchmarks). arXiv:2510.22954.** https://arxiv.org/abs/2510.22954 ; code/data: github liweijiang/artificial-hivemind (from search snippets)
- Found: Infinity-Chat (26K real open-ended queries, taxonomy of 6 top-level and 17 subcategories, 31,250 human annotations). Two effects: intra-model repetition and inter-model homogeneity (70+ models per most summaries; one summary says 25 in the main analysis, so model count is **unverified**). Secondary summaries: pairwise similarity across models about 0.71 to 0.82; with temperature 1.0 and top-p 0.9, 79% of prompts give mean within-model similarity above 0.8; about 8 distinct models appear in the top-50 most similar responses. Embeddings used: text-embedding-3-small. LLM judges and reward models are poorly calibrated on responses that draw idiosyncratic human preferences.
- Why it matters: direct evidence that "different models, high temperature" is not an independent-catcher design. Also a ready-made protocol (50 samples x many models, embedding similarity) for estimating dependence between catchers.
- Open: a related blog write-up on open weights reports that personas lowered inter-model similarity (0.646 to 0.382 in eight-persona condition, secondary and unverified); worth testing persona prompts as a dependence-reduction lever.

**Kirk et al. (2023/2024). "Understanding the Effects of RLHF on LLM Generalisation and Diversity." ICLR 2024. arXiv:2310.06452.** https://arxiv.org/abs/2310.06452
- Found: across two base models and summarisation/instruction following, RLHF reduces output diversity relative to SFT on several measures while improving out-of-distribution generalisation.
- Why it matters: heterogeneity of catchability and between-run dependence are partly consequences of post-training. Using base or SFT models as catchers gives more run-to-run diversity, at lower quality.

**Bommasani, Creel, Kumar, Jurafsky, Liang (2022). "Picking on the Same Person: Does Algorithmic Monoculture lead to Outcome Homogenization?" NeurIPS 2022. arXiv:2211.13972.** https://arxiv.org/abs/2211.13972
- Found: the "component sharing hypothesis": systems sharing data or models make correlated decisions, so the same individuals are failed repeatedly; effects are larger at individual than group level and stronger for small datasets; for foundation models, the adaptation method strongly modulates homogenisation, not just the shared base model.
- Why it matters: gives a vocabulary and an experimental design (vary what components are shared) for the dependence experiment. The adaptation-method finding suggests prompts and scaffolds can matter as much as the base model.

**Kleinberg and Raghavan (2021). "Algorithmic Monoculture and Social Welfare." PNAS 118(22), e2018340118. arXiv:2101.05853.** https://arxiv.org/abs/2101.05853
- Found: a shared algorithm, even if more accurate individually, can reduce collective outcomes by removing independent noise in the combined estimate, without any shock.
- Why it matters: theory for why K same-model runs cannot be treated as K independent looks. The marginal value of a catcher is its independent error.

**Si, Yang, Hashimoto (2024/2025). "Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers." ICLR 2025. arXiv:2409.04109.** https://arxiv.org/abs/2409.04109
- Found: 4,000 seed ideas per topic yielded only about 200 non-duplicates (about 5%); duplicates found via all-MiniLM-L6-v2 embeddings with cosine threshold 0.8 chosen by manual inspection; unique-idea count plateaus as generation continues.
- Why it matters: real, quantified example of LLM catches collapsing onto few "individuals", and of an embedding-threshold identity rule (their threshold choice would change the "population" size). Accumulation curves here can be fed straight into Chao-type estimators. Also see Gupta et al. "All That Glitters is Not Novel: Plagiarism in AI Generated Research", arXiv:2502.16487 (seen in results, not read) for another view of duplication.

**Red-team diversity and overlap (partial evidence; none of these is a controlled overlap study).**
- Beutel, Xiao, Heidecke, Weng (OpenAI, 2024). "Diverse and Effective Red Teaming with Auto-generated Rewards and Multi-step RL." arXiv:2412.18693. https://arxiv.org/abs/2412.18693 . Prior methods trade diversity for effectiveness; a two-step pipeline (diverse goals, then RL attacker rewarded for differing from its earlier attempts) improves diversity at marginal cost to success. Useful: a lever for designing less-dependent attacker runs.
- Search-result survey claims (read only via snippet; unverified details): humans miss unnatural inputs found by automated white-box attacks, while multi-turn, past-tense framing and payload-splitting come from humans and not automated pipelines (appeared in a "Capability-Based Scaling Trends for LLM Jailbreaks" result, arXiv:2505.20162, and a CHI interview study of red-teaming practice); RL-trained attackers raise success but produce homogeneous prompts; in a multilingual multi-turn study machine prompts reached higher attack success but slightly lower diversity than human ones (arXiv:2504.03174). Also seen: Quality-Diversity Red-Teaming (arXiv:2506.07121), RedTopic topic-diverse red teaming (arXiv:2507.00026), "Recent advancements in LLM Red-Teaming" survey (arXiv:2410.09097).
- Why it matters: supports heterogeneity by source (human vs LLM). A study that releases per-attacker attack lists (e.g. from a public red-teaming competition) would let us compute Lincoln-Petersen between humans and models. I did not find one with matched lists.

**Auditing agents: Sheshadri et al. / Anthropic (2026). "AuditBench: Evaluating Alignment Auditing Techniques on Models with Hidden Behaviors." arXiv:2602.22755.** https://arxiv.org/abs/2602.22755 (first-author name unverified)
- Found: 56 target models, 14 hidden behaviours; 13 tool configurations; each configuration run 16 times per target; agent produces 10 predictions, an LLM classifier checks whether any matches the true quirk; baseline success about 37%. Behaviours exhibited in nearly every response (flattery, emotional bonding, self-promotion) are found reliably; context-dependent ones (contextual optimism, data poisoning, secret loyalty) are hard. A tool that surfaces accurate hypotheses does not guarantee the agent uses it ("tool-to-agent gap").
- Why it matters: replicated runs against known ground truth. We can treat each of the 16 runs as an occasion and the 14 behaviours as the population; a ready test of heterogeneity (the "easy vs hard" behaviours are the classic Chao-type heterogeneity). The per-run overlap statistics were not in the snippets I saw; need to look at the paper and released code.

### 2.2 Identity: LLM and embedding matching, clustering, granularity

**Clio. Tamkin et al. (Anthropic, 2024). "Clio: Privacy-Preserving Insights into Real-World AI Use." arXiv:2412.13678.** https://arxiv.org/abs/2412.13678 ; open implementation: https://github.com/Phylliida/OpenClio
- Pipeline (per summaries): Claude extracts facets, embeddings + k-means create base clusters, Claude names and describes them, then clusters are grouped hierarchically with LLM audits. One reported validation figure: r = 0.71 correlation between Trust and Safety classifications and Clio's. A privacy-attack follow-up ("Cliopatra") is mentioned in a secondary source (unverified).
- Why it matters: the closest in-house pipeline for "cluster what runs found into strategy classes". The hierarchy is the granularity knob. Not designed for stability audits: no seed-to-seed cluster agreement figures found.

**Wan et al. (Microsoft, 2024). "TnT-LLM: Text Mining at Scale with Large Language Models." KDD 2024. arXiv:2403.12173.** https://arxiv.org/abs/2403.12173
- Iterative LLM taxonomy generation on minibatches, then LLM labelling to train lightweight classifiers; evaluated with humans and GPT-4; better than clustering baselines. Human agreement numbers not surfaced by my search (a 89.1% figure seen belongs to a different application paper; do not cite as TnT-LLM).
- Why it matters: model for a "fixed rubric then classify" identity step, which gives a classifier we can run across all runs instead of pairwise matching.

**Lam, Teoh, Landay, Heer, Bernstein (2024). "Concept Induction: Analyzing Unstructured Text with High-Level Concepts Using LLooM." CHI 2024. arXiv:2404.12259.** https://arxiv.org/abs/2404.12259
- Concepts with explicit inclusion criteria, beat BERTopic-type topic models on quality and coverage in technical evaluation and four scenarios. 
- Why it matters: concept definitions as natural-language criteria can serve as a "rubric" and can be re-scored by independent LLM judges, enabling identity-agreement metrics. 

**Diaz-Rodriguez (2025/2026). "k-LLMmeans: Summaries as Centroids for Interpretable and Scalable LLM-Based Text Clustering" (ICLR 2026 version retitled "Summaries as Centroids for Interpretable and Scalable Text Clustering"). arXiv:2502.09667.** https://arxiv.org/abs/2502.09667
- LLM-written summary as cluster centroid in k-means; LLM calls do not grow with dataset size; mini-batch streaming; k-NLPmeans variant is deterministic and offline.
- Why it matters: cheap, reproducible clustering; the deterministic variant is useful for a stability baseline. Note k must still be chosen: granularity knob.

**Wang, Shang, Zhong (2023). "Goal-Driven Explainable Clustering via Language Descriptions." EMNLP 2023. arXiv:2305.13749.** https://arxiv.org/abs/2305.13749
- Users give a goal; LM brainstorms candidate cluster descriptions, classifies each sample against each description, then integer linear programming picks the subset. 
- Why it matters: lets us define identity with respect to a goal ("same attack mechanism" vs "same target"), making the granularity explicit and reportable.

**Stability and consistency of LLM clustering/taxonomies (seen only through search snippets; read the sources before citing):**
- CAST: "Achieving Stable LLM-based Text Analysis for Data Analytics", arXiv:2602.15861. Defines a stability score as the share of tags in the modal cluster across n runs, using an LLM judge to group equivalent tags. Directly reusable for measuring run-to-run label stability.
- LLM-MemCluster, arXiv:2511.15424. Strict vs relaxed prompts give coarser vs finer clusters (granularity control); ARI varied within about 5% across seeds.
- LiSA, "LLM-Guided Semantic-Aware Clustering for Topic Modeling", ACL 2025 (aclanthology 2025.acl-long.902). F1 roughly stable across K but ARI drops as K departs from truth.
- "Context-Aware Hierarchical Taxonomy Generation", EMNLP 2025 (2025.emnlp-main.788). Uses a node-count ratio to flag over-fragmentation or under-segmentation.
- "How Well Do LLMs Generate Taxonomies in the SE Domain?", arXiv:2608.01592: variance over five runs; embedding+clustering pipeline (CLIMB) more structurally stable than LLM-heavy ones.
- Takeaway: there are metrics (modal-cluster share, ARI between seeds, node-count ratio) but no study connecting cluster-count variability to downstream richness estimates. That connection is the novelty.

**Agreement of labelling schemes for jailbreak/attack taxonomies (snippets only; unverified paper attribution where noted):**
- A 2026 paper using multi-LLM majority vote to assign jailbreak categories reports overall Fleiss kappa 0.053 (many categories, binary formulation); narrow categories (e.g. backdoor implantation) kappa >= 0.60; broad ones (malware) kappa 0.37. I could not tell which of arXiv:2605.09225 / 2510.13893 it is (both appeared in the results).
- "AI Security Leaderboard", arXiv:2608.03070: five red-team experts calibrated on 10 examples, second annotator on 20%: Cohen's kappa 0.80.
- "Tricking LLMs into Disobedience", arXiv:2305.14965: kappa 0.6.
- Multilingual multimodal jailbreak-rating study (arXiv:2605.23157, "Same Model, Different Weakness"): Krippendorff alpha 0.533 overall; GPT-5 0.304 vs Qwen Omni 0.596, while percent agreement stayed about 66%, a reminder that raw agreement overstates reliability.
- Takeaway: reliability is high for narrow, well-specified categories and low for broad semantic ones, which is exactly the situation where N depends on how granularity is defined.

**LLM-as-judge for semantic equivalence.** I found no benchmark of LLM judges specifically on semantic equivalence or near-duplicate detection in the safety setting (search returned only general judge-reliability material). General points from snippets: judge-human kappa often 0.40 to 0.60 (moderate); raw agreement overstates quality; judges are positively biased and a "conservative judgement" instruction moved kappa from 0.40 to 0.48 in one UX study; temperature-0 re-run self-agreement 96.5% in one study, disagreements concentrated in borderline cases. All unverified beyond snippets. **Gap: no clean estimate of judge false-merge / false-split rates for attack equivalence; we should measure our own.**

**Embedding near-duplicate detection.** SemDeDup (Abbas et al.; seen only through NVIDIA NeMo Curator docs) clusters with k-means and removes pairs above a cosine threshold; the right threshold depends on the embedding model and data, and generic advice is about 0.9 as a starting point. Si et al. used 0.8 with MiniLM. Takeaway: thresholds in published work vary, are set by manual inspection, and are never propagated into downstream counts.

### 2.3 Microbial ecology: OTU resolution and spurious singletons

**Hughes, Hellmann, Ricketts, Bohannan (2001). "Counting the Uncountable: Statistical Approaches to Estimating Microbial Diversity." Appl. Environ. Microbiol. 67(10):4399-4406. doi:10.1128/AEM.67.10.4399-4406.2001 (erratum AEM 68:448).** https://journals.asm.org/doi/pdf/10.1128/aem.67.10.4399-4406.2001
- Reviews rarefaction and richness estimators for microbial data, favouring nonparametric estimators such as Chao1 and ACE. Richness depends on how an OTU ("species") is defined. I could not read the full text; my summary of its OTU discussion is from citing papers.
- Why it matters: the canonical citation for "richness estimate only means something relative to the unit definition".

**Schloss and Handelsman (2005). "Introducing DOTUR, a computer program for defining operational taxonomic units and estimating species richness." AEM 71(3):1501-1506.** https://pubmed.ncbi.nlm.nih.gov/15746353
- Computes Chao1, ACE and others at every distance level; shows soil libraries lacked sufficient depth for robust richness at the 3% level; notes Chao1 correlates strongly with sequencing effort. A later study cited in the same results reports Chao1 terminal estimates for OTUs at 0, 3, 5, 10% difference spanning about 9,867 to 325,040 OTUs (source paper not identified; unverified).
- Why it matters: template for our identity-granularity sweep: compute N-hat at every threshold and plot the whole curve.

**Kunin, Engelbrektson, Ochman, Hugenholtz (2010). "Wrinkles in the rare biosphere: pyrosequencing errors can lead to artificial inflation of diversity estimates." Environ. Microbiol. 12(1):118-123. PMID 19725865.** https://pubmed.ncbi.nlm.nih.gov/19725865/
- Sequencing a single E. coli template still gave inflated diversity unless reads were strictly quality-filtered and clustered at 97% or lower. Errors create spurious low-abundance OTUs (including abundant homopolymer artefacts).
- Why it matters: this is an experiment with known N = 1 that "counts" many species. Our analogue: run the pipeline on a **single** planted attack (or a single true feature) re-expressed many ways and see what N-hat the matcher returns.

**Huse et al. (2010). "Ironing out the wrinkles in the rare biosphere through improved OTU clustering." Environ. Microbiol. 12:1889-1898.** https://enviromicro-journals.onlinelibrary.wiley.com/doi/10.1111/j.1462-2920.2010.02193.x . **Dickie (2010). "Insidious effects of sequencing errors on perceived diversity in molecular surveys." New Phytol.** https://nph.onlinelibrary.wiley.com/doi/10.1111/j.1469-8137.2010.03473.x . Both examine how error and clustering choices distort richness extrapolation.

**Chiu and Chao (2016). "Estimating and comparing microbial diversity in the presence of sequencing errors." PeerJ 4:e1634.** https://peerj.com/articles/1634/
- Sequencing errors create spurious singletons; they estimate the true singleton count, then combine with observed higher-frequency counts; R code on the Chao lab site. 
- Why it matters: a ready-made correction f1 -> f1_corrected that maps onto "hallucinated or mis-judged unique findings". Also see the 2024 Environ Ecol Stat paper "Estimating the number of sequencing errors in microbial diversity studies" (https://link.springer.com/article/10.1007/s10651-024-00614-w), which frames spurious singletons as false-negative record-linkage errors and finds the total-species estimate equivalent between the Chiu-Chao and a deletion model, while Shannon differs.

**Deng, Umbach, Neufeld (2024). "Nonparametric richness estimators Chao1 and ACE must not be used with amplicon sequence variant data." ISME J 18(1):wrae106.** https://academic.oup.com/ismej/article/18/1/wrae106/7692950 (PMC11208923)
- DADA2 and Deblur treat singletons as errors and delete them; Chao1/ACE depend on f1 and f2, so estimates become meaningless; retaining singletons would instead put many artefacts into f1 and give extreme overestimation. Recommend other clustering strategies or diversity metrics. (A downstream review characterised the effect as underestimation; direction depends on handling.) Also see "Richness estimation in microbiome data obtained from denoising pipelines" (ScienceDirect S2001037021005456): Chao1 matched observed richness in unpooled DADA2 runs and exceeded it with pooling.
- Why it matters: any AI-safety pipeline that dedups aggressively before estimation destroys f1; any pipeline that does not dedup carries false singletons. Both break Chao1. We must pick a position and test it against planted truth.

**Other precedents seen in results:** Edgar (2017, PeerJ) OTU methods on mock communities exaggerate richness (hundreds to thousands of OTUs from Illumina mock data); Stach and Bull (2005) say richness predictions are likely severe underestimates because of arbitrary OTU definitions; "Ranking the Biases: OTUs vs ASVs..." (PLOS ONE, doi 10.1371/journal.pone.0264443): 99%-OTU richness 1.1x the 97% value and ASV richness far lower, and correlations between methods lowest for sampling-bias-corrected indices (iChao1, ACE); Bunge, Willis, Walsh (2014) "Estimating the Number of Species in Microbial Diversity Studies", Annu. Rev. Stat. Appl. 1:427-445, doi 10.1146/annurev-statistics-022513-115654 (review of parametric, nonparametric, Bayesian, mixed-Poisson and zero-truncation methods; content beyond the abstract not read). Also the USEARCH manual's note that 97% OTUs both merge distinct species and split single species, and that if most OTUs are artefacts richness estimates are not valid.

---

## 3. Implications for capture-recapture (synthesis)

**Dependence.**
- Positive dependence between catchers (a find by catcher 1 raises the chance of a find by catcher 2) makes m larger than independence predicts, so N-hat (Lincoln-Petersen, Chao lower bound, closed-population log-linear models without interaction) is biased low. Chao's estimators are lower bounds under heterogeneity, and heterogeneity and positive dependence are both consequences of shared model family, shared prompts and shared RLHF mode.
- Negative dependence can also occur (a second red team told what the first found, and explicitly steered away; or diversity-rewarded RL) and biases N-hat upward. Design choices cut both ways, so report which direction was intended.
- Classic fact that the data alone cannot separate heterogeneity from dependence with two occasions (non-identifiability) should be stated early; with K >= 3 occasions, log-linear interaction terms can be fitted but remain weakly identified. (Background knowledge, unverified here: Chao 2001; Link 2003; Hook and Regal 1995.)
- Two sources of apparent dependence differ in kind: (a) shared capability, i.e. both easily find the easy attacks (heterogeneity of catchability by attack), and (b) shared blind spot, i.e. both systematically miss the same attacks. (b) is invisible to any CR estimator: the attacks nobody can find do not belong in the "catchable" population. CR estimates the population catchable by this *class* of catchers. This must be stated in every claim (it is the proper reading of Kim et al.'s correlated errors).

**How to reduce and measure dependence (design recommendations).**
- Vary things in order of how much Bommasani/Kim/Hivemind suggest they matter: base model family and training lineage; post-training (base/SFT vs RLHF); scaffold and tools (white-box vs black-box, multi-turn vs single-turn); persona/role prompts; seeds and temperature (weakest); humans.
- Measure pairwise overlap (Jaccard, observed m vs n1 n2 / N_hat, a CAPA-style chance-adjusted ratio), the effective number of independent catchers (Kish n_eff on the presence matrix), and log-linear models with pairwise interaction terms (Rcapture).
- Use the dependence-vs-N-hat curve: if N-hat rises as catchers get more dissimilar, that is evidence of dependence bias. Report the limit as a lower bound.

---

## 4. Leads, inspirations and experiment ideas

**E1. Catcher-similarity ladder (dependence experiment).** Plant N_true attacks (or hidden behaviours, or ground-truth features) in a controlled environment (AuditBench's 14 behaviours; a toy jailbreak environment with a known rule set; synthetic SAEs). Create catcher pools at increasing dissimilarity: (a) same model, different seeds/temperature; (b) same model, different personas/prompts; (c) same family, different sizes/versions; (d) different families (open vs closed); (e) base/SFT vs RLHF versions; (f) humans. For each pool draw K = 2 to 10 catchers, and compute N-hat (LP, Chao1/Chao2, ACE, jackknife, log-linear with interactions), its bias vs N_true, and pairwise CAPA-style statistics and n_eff. Prediction: bias decreases monotonically with dissimilarity; same-model seeds give the worst underestimation; humans paired with models give the best overlap but a heterogeneity problem. Tie-in: Kim et al. 60% shared-error agreement; Kohli n_eff about 2 of 9; Hivemind 0.71 to 0.82 similarity.

**E2. Identity-granularity sweep.** Take one set of raw catches and re-run identity at: embedding cosine thresholds 0.6 to 0.95 (cf. Si et al. 0.8; SemDeDup about 0.9), HDBSCAN/k-means with k from 5 to 500, LLM-judge pairwise matching with strict/relaxed prompts, and hierarchical cuts (family / technique / instance). Plot N-hat(threshold) and its CI, as in the DOTUR plot, and overlay the true-N line for planted data. Report: the threshold that minimises bias on planted data, whether it transfers to a second planted set, and the sensitivity band when it does not. Include inter-LLM-judge agreement (kappa, CAST's modal-cluster share) at each level. Hypotheses: coarse levels give near-saturated counts (f1 ~ 0, N-hat ~ n_obs); fine levels give singleton inflation (N-hat explodes), with an intermediate "plateau" window.

**E3. Singleton-from-error experiment (the Kunin test).** Feed a single true attack, expressed many ways (paraphrases, noise, partial attempts, hallucinated near-miss "attacks"), through the full pipeline. A correct pipeline reports N = 1. Count how many "species" it returns; compute Chao1 with and without a Chiu-Chao-style singleton correction. Then also test the Deng et al. failure: pre-dedup aggressively, and show Chao1 collapses to n_obs. Inject controlled false-positive rates (judge says "success" when not) as the AI analogue of base-calling error. 

**E4. Record-linkage-aware CR.** Treat the matcher as a noisy linker with measured false-merge and false-split rates (calibrated against a human-labelled sample), and propagate those into N-hat through a simulation or Bayesian model (the Environ Ecol Stat 2024 record-linkage view of spurious singletons gives the template). Output: N-hat with identity uncertainty included in the CI, not just sampling error.

**E5. Idea-accumulation curve as a free CR dataset.** Reproduce Si et al.'s generation of thousands of ideas (or attacks) by several models; build per-model "occasions"; estimate N (unique ideas) with Chao1/ACE/coverage estimators and check against huge-sample plateaus (their 4000 -> 200 unique). Cheap (no human labels), true plateau approximates N_true for the catchable population, and the experiment varies the dedup threshold (0.8 vs others) at the same time.

**E6. AuditBench replicate analysis.** With the 16 runs per target and 13 tool configurations, treat behaviours as the species, runs as occasions, per-behaviour success rate as catchability (known heterogeneity: easy flattery vs hard secret loyalty). Hold out some behaviours from the run list to see whether Chao2 and log-linear heterogeneity models recover the held-out count. 

**E7. Human vs LLM two-list test.** Use any public red-teaming dataset with human and automated attacks on the same target (to be located) and compute Lincoln-Petersen between lists under multiple identity rules. Use it to demonstrate the heterogeneity-by-source problem and the stratified estimator (post-stratify by attack type).

**E8. Diversity levers.** Within a fixed model, compare: temperature, persona prompts, diversity-reward RL (Beutel-style), prompt-injected "avoid these found attacks" (introduces negative dependence), and different tool sets. Measure how much each lowers CAPA-style similarity and how it changes bias. The persona result (reported 0.646 to 0.382 in one secondary blog) is the first thing to confirm or refute.

**E9. Dependence diagnostics from data alone.** On the real (unknown truth) applications, report pairwise overlap ratios, log-linear interaction terms, and the n_eff of occasions, and show how the lower bound changes when the K most similar catchers are collapsed to one.

---

## 5. Pitfalls and warnings

- **"More runs" is not "more independent runs".** Evidence: Kohli (9 judges ~ 2 votes), Hivemind (temperature and model ensembles do not guarantee diversity), Si et al. (200 unique of 4000). K in a formula must be effective K.
- **N means the population catchable by this class of catchers.** Shared blind spots are not estimable by CR. State this in every number.
- **Heterogeneity and dependence are confounded with few occasions.** Do not interpret a low N-hat as evidence of a saturated space.
- **Identity drives N-hat more than the estimator does.** Without a granularity sweep a single N-hat is not interpretable (microbial precedent: terminal Chao1 estimates spanning a factor of about 30 across OTU thresholds in one cited study).
- **Both failure modes of singletons.** Spurious singletons inflate Chao1 (Kunin; Chiu and Chao); removing singletons (DADA2 style, or aggressive near-duplicate removal) leaves Chao1 undefined or meaningless (Deng et al.). Pipeline choice must be validated against planted truth.
- **LLM-judge identity is itself dependent on the catchers.** A judge from the same family as the attackers may merge attacks that a different judge would split (Goel et al.: judges favour similar models). Use a judge from a different family than any catcher and report cross-judge agreement.
- **Embedding thresholds are set by eyeball in practice** (Si et al. 0.8; generic 0.9) and depend on the embedding model; a threshold that works on one distribution (natural-language ideas) will not transfer to code-like or encoded attacks (base64, cipher, multi-turn state).
- **Hierarchy and non-nestedness.** Attacks combine strategies; one run may find a composite of two known ones. Count-based identity then depends on whether composites are new individuals. Decide rules in advance.
- **Time and adaptivity.** Later catchers that see earlier lists (adaptive red teaming) violate independence in a negative direction. Keep occasions blind to each other.
- **Secondary-source numbers.** Several figures here (Hivemind similarity ranges, Kim cross-provider numbers, the 5% ARI margin, the 9,867 to 325,040 OTU range) come from summaries; verify before citing.
- **Open-population drift.** Models and attacks change between runs; closed-population estimators assume a fixed population over the study. Keep model versions fixed within an analysis.

---

## 6. Alternatives and complements (UNVERIFIED: search budget exhausted; background knowledge only)

I could not search for these. They should be verified with a follow-up search before appearing in any document. No arXiv IDs are given deliberately.

- **Jones, Tong, Steinhardt et al. (2025), "Forecasting Rare Language Model Behaviors"** (title and topic from the task brief; findings not verified): forecasts the probability of rare behaviours at deployment scale from small-sample elicitation, apparently via extrapolating the tail of the per-query elicitation-probability distribution. Relevance: estimates the *rate* of known behaviours, not the *number of unknown kinds*. Complement.
- **Wu and Hilton (2024), "Estimating the Probabilities of Rare Outputs in Language Models"** (ARC; from the task brief; details unverified): importance sampling and activation-extrapolation approaches for the probability of a specified rare output. Needs a specified target event; does not discover new categories. Complement.
- **Extreme value theory, importance sampling for tail risk, unknown-unknowns estimation, active testing / label-efficient evaluation, IRT-based benchmark design:** established topics in statistics and ML evaluation; specific LLM-safety papers not checked. Questions to check in a follow-up: any work applying Good-Turing / missing-mass or species-richness estimators to LLM outputs, red teaming, or benchmark coverage; "unknown unknowns" estimation in ML (Lakkaraju et al. 2017, from memory only, unverified).
- **When CR is likely better:** the target is the number of distinct unknown failure categories; no specification of the failure is available; replicated independent-ish searches are cheap; categories can be matched across runs. 
- **When CR is likely worse:** failures are defined by a known predicate and rates matter (use rare-event probability estimation or importance sampling); the search has a strong adaptive/optimisation component (heavy dependence); the population is effectively unbounded or continuous (use the coverage or accumulation-curve methods, not N); identity is ill-defined.
- **Software-inspection precedent:** Eick et al. (1992, in the proposal) and later empirical work on capture-recapture for defect content reported that estimators tend to underestimate with few inspectors and heterogeneous defects (background knowledge, e.g. Briand, El Emam, Freimut, Laitenberger; unverified here). Worth a search because it is the closest "catchers are people with correlated skills" precedent.
- **Suggested combined design:** use rare-output probability methods to estimate how likely each *found* behaviour is at deployment, and CR/unseen estimators to estimate how many categories remain; report both. Add a Good-Turing style "sample coverage" for single-run claims ("a single run has found about C% of the probability mass of catches").

---

## 7. Datasets, code and tools

- Artificial Hivemind / Infinity-Chat: arXiv:2510.22954; GitHub liweijiang/artificial-hivemind (path per search snippet).
- AuditBench: arXiv:2602.22755; LessWrong post "AuditBench: Evaluating Alignment Auditing Techniques on Models with Hidden Behaviors" (https://www.lesswrong.com/posts/LqDjxSceFz8tjMe2j/auditbench-evaluating-alignment-auditing-techniques-on). Public implementation mentioned but link not confirmed.
- OpenClio (open Clio implementation): https://github.com/Phylliida/OpenClio
- LLooM Workbench: from the UW Interactive Data Lab page https://idl.uw.edu/papers/lloom-concept-induction
- k-LLMmeans: arXiv:2502.09667 (code link not confirmed).
- Chiu-Chao R code: Chao lab site https://sites.google.com/view/chao-lab-website/publication ; iNEXT GitHub issue #57 notes singleton-correction is not built in (https://github.com/JohnsonHsieh/iNEXT/issues/57).
- Rcapture (log-linear CR models; named in the proposal); QIIME2/mothur implement bias-corrected Chao1; DOTUR/mothur for thresholded richness curves.
- Embedding models seen in use: text-embedding-3-small (Hivemind), all-MiniLM-L6-v2 (Si et al.). NeMo Curator SemDeDup docs: https://docs.nvidia.com/nemo/curator/0.25.7/curate-text/process-data/deduplication/semdedup.html

---

## 8. Search log (queries run, abbreviated)

Standard/extended searches that returned results (about 30):
1. Kim 2025 Correlated Errors in LLMs
2. Goel 2025 Great Models Think Alike CAPA
3. Artificial Hivemind Infinity-Chat (x2: overview and numbers)
4. Kirk 2023 RLHF diversity
5. Bommasani Picking on the Same Person
6. Si et al. novel research ideas duplication
7. Kleinberg and Raghavan algorithmic monoculture
8. Human vs LLM red-teamer overlap
9. Auditing agents overlap / AuditBench
10. Beutel diverse red teaming
11. Nine Judges Two Effective Votes
12. Clio
13. TnT-LLM
14. LLooM concept induction
15. k-LLMmeans
16. Goal-driven explainable clustering
17. LLM clustering stability and granularity
18. LLM-as-judge semantic equivalence reliability
19. Embedding near-duplicate threshold / SemDeDup
20. Inter-annotator agreement jailbreak taxonomies
21. Hughes 2001 Counting the Uncountable
22. Kunin 2010 Wrinkles in the rare biosphere
23. Chao1 singletons / sequencing errors / DADA2
24. Bunge, Willis, Walsh 2014
25. Deng et al. 2024 Chao1 ACE ASV
26. Chiu and Chao 2016
27. OTU threshold effects on Chao1 / DOTUR
28. Bohannan and Hughes / Schloss and Handelsman soil census

Blocked by the search budget (not run): Jones et al. Forecasting Rare LM Behaviors; Wu and Hilton rare outputs; EVT for LLM risk; Good-Turing / unseen species for LLM evaluation. Also not searched: IRT benchmark methods, active testing, unknown-unknowns, software-inspection capture-recapture critiques, Chao 2001 / Link 2003 / Hook-Regal on dependence and non-identifiability, record-linkage-error CR (Ding and Fienberg; Tancredi and Liseo), and matched human-vs-LLM red-team attack lists.
