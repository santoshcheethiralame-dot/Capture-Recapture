# B. Identity errors (misidentification, record linkage) and multiple systems estimation (MSE)

Project: "What did we miss? Capture-recapture for safety tools". Date: 22 Oct 2026.

**Read this first: coverage caveat.** The shared WebSearch budget ran out after roughly 24 searches, so some planned items were never searched: HRDAG country studies (Kosovo, Peru, Guatemala, Syria, Colombia), US Census PES details, Fellegi-Sunter, Steorts' own linkage papers, Hook & Regal 1995 and the IWGDMF abstracts, and a count of how many epidemiology validation studies found serious bias. Search tool results were mostly abstracts and metadata, not full texts. Labels used below:

- **[seen]** means the item appeared in a search result this session. Its numbers come from the snippet or abstract.
- **[memory]** means background knowledge, not checked this session. Treat as unverified until looked up.
- **[sim]** means my own simulation, run in this session. Code is in `scripts/` (`sim_a.py`, `sim_b.py`).

---

## 1. Summary (key takeaways)

1. **Ecology has a 15-year literature on exactly this problem, and the direction of bias is well established.** Failing to link a true recapture (false non-match, "splitting") creates ghost individuals. This inflates N. Wrongly merging two individuals (false match, "lumping") removes individuals and shrinks recapture counts. Which way N moves depends on the estimator and on the data (item 3).
2. **Real numbers exist.** Eight observers identifying 16 captive snow leopards over 40 occasions misclassified 12.5% of occasions. That inflated abundance by 35 ± 21% on average (Johansson et al. 2020, Sci Rep) [seen]. A dolphin photo-ID study found that demanding 100% certainty before declaring a match gave higher N and lower survival than a looser threshold (Ashe & Hammond 2022) [seen]. A simulation in a software-matching study showed automated photo-ID can bias N high by up to 920% [seen via search summary; primary paper not identified].
3. **My simulation [sim] shows an asymmetry that matters for the project.** Chao1 is very sensitive to false non-matches. With N=500, K=5, a 5% per-link miss rate raised Chao1 by 12% and a 10% miss rate by 24%. A 30% miss rate nearly doubled it (912 vs 500). Chao1 is much less sensitive to false matches (about -4% at a 10% false-match rate). The reason is that ghosts are born as singletons, and Chao1 is driven by f1²/(2·f2). In the small-overlap Lincoln-Petersen (LP) regime, the opposite holds: a few false matches inflate m and can deflate N a lot (item 11).
4. **Compensating errors are a trap.** On heterogeneous data Chao1 is a lower bound (478 vs truth 500 in my sim). Ghosts push it back up toward or past the truth, so a "good" estimate can be right for the wrong reason [sim].
5. **Threshold sweeps need a plateau diagnostic.** When I swept the cosine threshold on simulated noisy-copy features, the estimate had a stable plateau (Chao1 ≈ 382 for truth 400, discovered 334) over tau = 0.5 to 0.7 when the true-pair cosine was about 0.8. In a noisier setting (true-pair cosine about 0.5) there was no plateau and N exploded (Chao1 from 962 to over 10^5) as tau rose [sim]. Reporting N versus threshold is necessary but not sufficient. The shape of the curve tells you whether any threshold is trustworthy.
6. **Low thresholds fail differently: chaining.** With one-to-one Hungarian matching and union-find over runs, a low tau merges everything (103 clusters from 334 discovered at tau=0.3) [sim]. Transitive closure over pairwise matches needs care.
7. **Fully model-based fixes exist but are hard to identify.** The latent multinomial (Link et al. 2010) and the Mt,α model (Vale, Fewster et al. 2014) estimate the error rate inside the capture model. Vale et al. conclude the indirect approach needs rich data: precision and bias are good only when capture probabilities are high or there are many occasions [seen]. Fraysse et al. (arXiv 2304.00885) report that at capture rate 0.2 or lower the latent multinomial MCMC fails or gives bias over 30% to 40%, and that an informative prior on the identification probability fixes convergence [seen]. **Lesson: estimate the error rate from a labelled validation subset, not from the capture data alone.**
8. **Misidentification is confounded with heterogeneity.** The MARK book chapter warns that modelling both typically gives inconclusive results (see item 6 in section 2.1) [seen]. This is a direct warning for the project: unequal catchability and matching error both produce excess singletons.
9. **Photo-ID's "two sides that cannot be matched" maps onto our "two views of a feature".** McClintock et al. (2013, Ecology) and Bonner & Holmberg (2013, Biometrics), with the multimark R package, treat an individual observed through multiple partial non-invasive marks. Decoder direction and activation pattern in an SAE, or rubric label and judge-embedding for an attack, are two partial marks that can disagree [seen for the papers; the mapping is my idea].
10. **Record linkage supplies the joint-modelling template.** Tancredi & Liseo (2011, AoAS) treat linkage and population size jointly in a hierarchical Bayesian model [seen]. Tancredi, Steorts & Liseo (2020, Bayesian Analysis) extend it to de-duplication with a latent entity model, N as a parameter, and an explicit link to capture-recapture [seen]. Sadinle (2017, JASA) provides Bayes-optimal matching estimates with partial estimates that leave uncertain pairs unresolved [seen]. These give a principled way to carry linkage uncertainty into N.
11. **MSE's lessons for us are about model choice, sparsity and ground truth.** Small changes in data or arbitrary model choices give vastly different modern-slavery estimates [seen]. Similar-fitting log-linear models can give very different totals; one discussant called the UK approach "unreliable" and suggested the dark figure may be futile to estimate [seen]. Sparse tables with non-overlapping lists need special treatment (Chan, Silverman & Vincent 2021, SparseMSE) [seen]. Binette & Steorts (JRSS A 2022) built an internal-consistency check from subsets with known truth [seen]. This is the same strategy as our Phase 1.
12. **Large-scale census coverage practice (dual-system estimation with clerical review) is the best-developed operational analogue** [memory only; not searched]. It uses computer match, clerical review, field follow-up and probabilistic imputation of unresolved match status. See section 2.4 for what to borrow.
13. **Microbiome diversity estimation has the same "spurious singletons inflate Chao1" problem** [memory; one related search hit: "Estimating the number of sequencing errors in microbial diversity studies", Environ Ecol Stat 2024 [seen as title only]]. Singleton-correcting Chao estimators (Chiu & Chao 2016) are a candidate fix [memory].
14. **For the proposal:** treat matching as a measured, modelled and swept quantity. Concretely: (a) a labelled validation subset to estimate false match (g) and false non-match (f) rates; (b) a plateau and sensitivity plot of N versus threshold; (c) multiple-imputation over plausible matchings; (d) injection experiments that add known errors and check the estimators recover truth after correction. Details in section 3.

---

## 2. Papers

### 2.1 Misidentification in mark-recapture (ecology)

1. **Link, W. A., Yoshizaki, J., Bailey, L. L., Pollock, K. H. (2010). Uncovering a latent multinomial: analysis of mark-recapture data with misidentification. Biometrics 66(1):178-185.** DOI 10.1111/j.1541-0420.2009.01244.x. USGS record: https://www.usgs.gov/publications/uncovering-a-latent-multinomial-analysis-mark-recapture-data-misidentification-0 [seen: metadata and abstract summary only].
   - Found: a general Bayesian framework in which observed capture-history counts are a linear transformation of latent counts that are multinomial. Each occasion has three outcomes (correct ID, misID, not captured), giving 3^T true histories but only 2^T - 1 observable ones (this description is from the Schofield 2015 summary [seen]).
   - Matters here: the template for estimating the error rate and N together. The "ghost" history idea is exactly our duplicate features.
   - Open: identifiability is weak. See Vale et al. and Fraysse et al. below. Numerical bias results of the 2010 paper were not retrieved.

2. **Schofield, M. R. & Bonner, S. J. (2015). Connecting the latent multinomial. Biometrics 71(4):1070-1080.** https://onlinelibrary.wiley.com/doi/abs/10.1111/biom.12333 [seen: abstract and citing summaries].
   - Found: the original MCMC of Link et al. can produce chains that are not irreducible; a Markov basis fixes this for complex error structures. Follow-up Bonner, Schofield, Noren & Price (2016, AoAS 10(1)), "Extending the latent multinomial model with complex error processes and dynamic Markov bases", https://arxiv.org/pdf/1504.00441 [seen], notes Markov bases are hard to compute even for moderate studies.
   - Matters: computational cost scales badly. A full latent-multinomial treatment of thousands of features across K runs is not feasible, so we need approximations (multiple imputation of matchings, or a record-linkage-style model).

3. **Vale, R. T. R., Fewster, R. M., Carroll, E. L., Patenaude, N. J. (2014). Maximum likelihood estimation for model Mt,α for capture-recapture data with misidentification. Biometrics 70(4):962-971.** DOI 10.1111/biom.12195; PDF https://www.stat.auckland.ac.nz/~fewster/Vale_et_al_Mtalpha.pdf [seen: abstract-level].
   - Found: ML inference for a model with capture probability by occasion (t) and a single identification probability α. Conclusion: the indirect approach to estimating identification error "needs rich data"; precision and bias are good only when capture probabilities are high or there are many occasions. They advise caution and considering other strategies for handling misidentification. Illustrated on New Zealand southern right whales (genetic plus photo surveys).
   - Matters: a direct warning that estimating the error rate from the capture data alone is fragile. Supports validation-subset estimation of f and g.

4. **Fraysse, Choquet, Costantini, Pradel (2023). Population size estimation with capture-recapture in presence of individual misidentification and low recapture. arXiv:2304.00885.** https://arxiv.org/abs/2304.00885 [seen: abstract/snippets].
   - Found: at capture rate ≤ 0.2 the latent multinomial MCMC either does not converge or is biased. Without a prior, average relative bias exceeded 30% (T=9) and 40% (T=7). With an unbiased informative prior on identification probability, N is underestimated by about 10% on average at p=0.1 (up to 40% in some runs). A biased prior hurts more as p falls. A multistate extension works at p ≥ 0.3.
   - Matters: low recapture is our regime if runs share few features. Informative priors from a validation subset are the practical fix.

5. **Yoshizaki, J., Pollock, K. H., Brownie, C., Webster, R. A. (2009). Modeling misidentification errors in capture-recapture studies using photographic identification of evolving marks. Ecology 90:3-9.** https://esajournals.onlinelibrary.wiley.com/doi/10.1890/08-0304.1 [seen: listing only; contents not read].
   - And **Yoshizaki, Brownie, Pollock, Link (2011). Modeling misidentification errors that result from use of genetic tags in capture-recapture studies. Environ Ecol Stat 18:27-55.** DOI 10.1007/s10651-009-0116-1 [seen: the dating is 2009 online, 2011 in print; the first-author list in my brief said "Yoshizaki et al. 2009, 2011"; I could not verify the exact authorship of the 2009 Ecology paper beyond "Yoshizaki"]. A search summary states that traditional estimators tend to overestimate N when misidentification gives one animal multiple identities.
   - Matters: "evolving marks" is analogous to features that drift between runs or layers.

6. **Lukacs, P. M. & Burnham, K. P. (2005). Estimating population size from DNA-based closed capture-recapture data incorporating genotyping error. J Wildl Manage 69(1):396-403.** https://pubs.usgs.gov/publication/70029422 [seen: metadata]. A later critique says the model rests on assumptions unlikely to hold and does not properly account for ghost capture histories (citing Yoshizaki 2007, Link 2010, Yoshizaki 2011) [seen as a snippet]. MARK book chapter 15 (http://www.phidot.org/software/mark/docs/book/pdf/chap15.pdf) [seen as a snippet]: when misID is modelled, N-hat = α-hat·f0-hat + M(t+1), the constraint N-hat ≥ M(t+1) no longer holds, and "incorporation of both misidentification and heterogeneity typically leads to inconclusive results" because they are nearly confounded.
   - Matters: the key conceptual warning for the project: heterogeneity versus matching error cannot both be freely estimated from capture histories alone.

7. **Wright, J. A., Barker, R. J., Schofield, M. R., Frantz, A. C., Byrom, A. E., Gleeson, D. M. (2009). Incorporating genotype uncertainty into mark-recapture-type models for estimating abundance using DNA samples. Biometrics 65(3):833-840.** DOI 10.1111/j.1541-0420.2008.01165.x; https://pubmed.ncbi.nlm.nih.gov/19173702/ [seen].
   - Found: allelic dropout makes undetected errors; naive use of genotypes leads to significant overestimates of N. Their idea is to use partial genotypes (low-quality samples) rather than discard them.
   - Matters: the "partial identity" idea: keep uncertain matches in the model with probabilities instead of discarding them.

8. **Bonner, S. J. & Holmberg, J. (2013). Mark-recapture with multiple, non-invasive marks. Biometrics 69(3):766-775.** https://academic.oup.com/biometrics/article/69/3/766/7492440 ; arXiv:1208.4285 [seen]. Built on Link et al.'s latent multinomial for whale shark photo-ID (ECOCEAN). Ignoring multi-mark double counting gives incorrect inference. **Note: my brief attributed the "bilateral photo-ID" paper to McClintock et al.; correct attribution is below.**
   **McClintock, B. T., Conn, P. B., Alonso, R. S., Crooks, K. R. (2013). Integrated modeling of bilateral photo-identification data in mark-recapture analyses. Ecology 94:1464-1471** [seen: cited by the search tool as the left/right-side paper]. Implementation: R package **multimark** (McClintock 2015, Ecol Evol; https://onlinelibrary.wiley.com/doi/10.1002/ece3.1676) [seen].
   - Matters: our two representations of a feature (decoder cosine, activation correlation) can be treated as two "sides" that sometimes disagree. The bilateral model estimates abundance even when left and right sightings of the same animal cannot be directly linked.

9. **Augustine, B. C., Royle, J. A., Kelly, M. J., Satter, C. B., Alonso, R. S., Boydston, E. E., Crooks, K. R. (2018). Spatial capture-recapture with partial identity: an application to camera traps. Ann Appl Stat 12(1):67-95.** https://projecteuclid.org/journals/annals-of-applied-statistics/volume-12/issue-1/Spatial-capturerecapture-with-partial-identity--An-application-to-camera/10.1214/17-AOAS1091.full ; arXiv:1503.06873 [seen: abstract].
   - Found: common approaches that discard single-flank photographs lose precision and (not previously recognised) introduce bias. SPIM uses the location of each photo to probabilistically resolve which individual a single-flank photo belongs to. Related: Chandler & Royle (2013, AoAS), "Spatial capture-recapture for unmarked populations" [memory]. Also "A flexible framework for spatial capture-recapture with unknown identities" (Biometrics 80(1), 2024; https://academic.oup.com/biometrics/article/80/1/ujad019/7610189) [seen as a title; authors not retrieved].
   - Matters: SPIM's trick is an auxiliary covariate (location) that disambiguates partial identity. For us the analogue is context: which layer, which activation neighbourhood, which prompt family, which attack target.

10. **Johansson, Ö. et al. (2020). Identification errors in camera-trap studies result in systematic population overestimation. Sci Rep 10:6393.** https://www.nature.com/articles/s41598-020-63367-z (PMC7156508) [seen: abstract; the author list was not retrieved].
    - Found: 16 captive snow leopards, 40 capture occasions, eight observers. Observers misclassified 12.5% of capture occasions, inflating abundance by 35 ± 21% on average. Splitting errors create new individuals; combination errors merge two individuals into one. The result is net overestimation because splitting errors dominate in effect. A companion paper: "Best practices for reporting individual identification using camera trap photographs" (Global Ecology and Conservation, 2020) [seen as a title].
    - Matters: the closest empirical analogue to "multiple LLM judges clustering attacks". Several observers labelling the same items is how you estimate error rates and their effect.

11. **Ashe, E. & Hammond, P. S. (2022). Effect of matching uncertainty on population parameter estimation in mark-recapture analysis of photo-identification data. Mammalian Biology.** https://doi.org/10.1007/s42991-022-00236-4 [seen: abstract-level only; I did not retrieve the effect sizes].
    - Found: on Pacific white-sided dolphins, requiring 100% certainty to call a match produced fewer matches, higher abundance and lower survival than a lower certainty threshold. The authors argue conservative matching is not always precautionary and recommend carrying matching uncertainty into N.
    - Matters: a direct precedent for "report N across thresholds".

12. **Other photo-ID matching studies surfaced by search [seen as titles and snippets only, none read]:**
    - "Errors in identification using natural markings: rates, sources, and effects on capture-recapture estimates of abundance" (Canadian J Fish Aquat Sci; authors not retrieved). Snippet: simulations show software-based identification can bias abundance high by up to 920%. Two software platforms (Wild-ID, HotSpotter) missed 47% and 64% of true matches; false-match rates were 0-2% (HotSpotter) and 6-28% (Wild-ID) [seen via search summary].
    - "Error rates and variation between observers are reduced with the use of photographic matching software for capture-recapture studies" (authors not retrieved).
    - "Accounting for matching uncertainty in two stage capture-recapture experiments using photographic measurements of natural marks" (Hiby et al. 2013? unverified).
    - A whale study where a similarity cutoff of 0.450 gave a 6.4% missed-match probability, and photo-ID abundance (908; 95% CI 755-1123) agreed with microsatellite genotypes (910; CI 641-1354) [seen via search summary; paper not identified]. This is the best concrete example of **validating the threshold against an independent gold standard**.
    - "Analysis of photo-ID data allowing for missed matches and individuals identified from opposite sides" (Fewster-group paper, likely Fewster et al.; authors unverified).
    - A Petersen estimator adjusted for false negatives (Stevick et al. type, unverified): this is the formula LP_adj = LP × (1 − f) derived in section 3.

13. **McClintock, B. T., Bailey, L. L., Dreher, B. P., Link, W. A. (2014). Probit models for capture-recapture data subject to imperfect detection, individual heterogeneity and misidentification. Ann Appl Stat.** arXiv:1401.3290 [seen]. Evidence of individual heterogeneity in misidentification probability attributable to variable mark quality. Matters: error rates vary by item, which is certain for features (rare or low-activation features match worse).

14. **Newer ecology items worth reading [seen as titles only]:** "A Bayesian Parametric Approach to Capture-Recapture with Misidentification" (JABES 2025, https://link.springer.com/article/10.1007/s13253-025-00717-2); "Maximum likelihood inference for the band-read error model" (Environ Ecol Stat 2021, https://link.springer.com/article/10.1007/s10651-021-00492-6); "Latent multinomial models for extended batch-mark data" (Zhang et al., Biometrics 2023); "Estimating temporary emigration from capture-recapture data in the presence of latent identification" (arXiv:2510.06755); "Population size estimation when multiple samples carrying the risk of misidentification are taken within the same capture occasion from the same individual" (bioRxiv 2024.06.12.598605); "Spatial proximity moderates genotype uncertainty in genetic tagging studies" (PNAS 2020, https://www.pnas.org/doi/abs/10.1073/pnas.2000247117).
    - The "multiple samples within the same occasion" paper is relevant to us: one SAE run may produce several near-duplicate features for the same underlying direction (feature splitting); that is within-occasion duplication, not just between-occasion matching.

15. **Picek, L. et al. (2026). Centering Ecological Goals in Automated Identification of Individual Animals. arXiv:2604.20626.** https://arxiv.org/abs/2604.20626 [seen: abstract]. Twenty-author perspective. Argues the barrier is a mismatch between how re-identification methods are evaluated and how ecological data are collected and used. Proposes fit-for-purpose evaluation: judging methods by the ecological question, study design, and tolerance for different kinds of identification mistakes. Matters: supports evaluating the matcher by its effect on N, not by its accuracy alone (the same philosophy as our injection experiments).

### 2.2 Which direction does each error push N? (summary of formulas and my simulations)

Two-sample case, n1 and n2 distinct items in the two runs, m true overlaps.
- **False non-match**, each true recapture missed independently with probability f: m_obs = (1 − f)·m, so LP_obs = n1·n2 / ((1 − f)·m) = LP/(1 − f). N is overestimated by a factor 1/(1 − f). Exact for LP; correction is LP × (1 − f) once f is estimated. This is the "Petersen adjusted for false negatives" idea [derived by me; matches the direction reported in Ashe & Hammond and the photo-ID literature].
- **False match**, each non-overlapping pair accepted with per-pair probability φ: m_obs ≈ m + φ·(n1·n2 − m). When the true overlap m is small (the regime where N is large relative to catches), a small φ adds a spurious overlap of the same order as m, so LP_obs = n1·n2/m_obs falls sharply. Example: n1 = n2 = 100, N = 1000, m ≈ 10. If a false match adds 4 to m, N-hat falls from 1000 to about 710. [derived by me; a back-of-envelope example, not a simulation]
- **Chao1 / frequency-of-frequencies estimators** use f1 and f2. A false non-match turns one item with two detections into two singletons, raising f1 and reducing f2, which increases f1²/(2·f2) quickly.

My simulation [sim, `sim_a.py`]: N=500, K=5 runs, detection probabilities p_i ~ Beta(2,3) (mean 0.4), 300 replicates. "f" is the per-link miss probability when a later detection is linked to the earlier one; "g" is the probability that a detection is merged into a random existing cluster.

| error | observed clusters | Chao1 | LP (runs 1-2) |
|---|---|---|---|
| none | 418 | 478 | 402 |
| f = 0.05 | 446 | 534 | 422 |
| f = 0.10 | 476 | 594 | 448 |
| f = 0.20 | 535 | 739 | 501 |
| f = 0.30 | 593 | 912 | 574 |
| g = 0.01 | 416 | 474 | 395 |
| g = 0.05 | 410 | 470 | 382 |
| g = 0.10 | 404 | 460 | 364 |

(Truth = 500. Homogeneous p = 0.4: no error Chao1 = 510, LP = 502; f = 0.1 gives Chao1 = 621, LP = 566.)

Readings: (a) at moderate f, Chao1 error is about 2.4 times the miss rate in relative terms; (b) false matches have a milder effect in this high-overlap regime; (c) the unbiased-looking value at f=0.05 to 0.1 for Chao1 versus 478 at f=0 is the compensating-errors hazard; (d) LP on heterogeneous data underestimates (402) and false non-matches again push it up toward truth.

Threshold-sweep simulation [sim, `sim_b.py`]: N=400 true unit vectors in d=64, each run detects feature i with probability p_i ~ Beta(2,3) and returns a noisy copy; runs are matched pairwise by Hungarian assignment on cosine, pairs with cosine ≥ tau are accepted, clusters are connected components across all five runs, and Chao1 is computed on cluster sizes. Mean cosine between two noisy copies is about 1/(1+σ²).

| setting | mean features actually discovered | tau=0.3 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---|---|---|---|---|---|---|
| σ=0.5 (copy cos ≈ 0.8): Chao1 | 334 | 123 | 381 | 382 | 384 | 914 | 322,876 |
| σ=0.5: clusters | | 103 | 333 | 334 | 335 | 460 | 803 |
| σ=1.0 (copy cos ≈ 0.5): Chao1 | 332 | 72 | 962 | 4,839 | 187,684 | 314,549 | 314,549 |
| σ=1.0, features share a common component: Chao1 | 330 | 3 | 11 | 1,174 | 17,718 | 303,062 | 303,062 |

Takeaways: (i) there can be a wide plateau where clusters equal the discovered count and Chao1 lands near truth (σ=0.5); (ii) raising tau beyond the typical true-pair similarity makes every detection a singleton, f2 → 0, and Chao1 is meaningless; (iii) lowering tau collapses clusters by chaining; (iv) when features are more similar to one another than the noise allows, no threshold works and the curve itself shows it. These are toy results meant to guide experiment design, not claims about real SAEs.

### 2.3 Record linkage plus population size

1. **Tancredi, A. & Liseo, B. (2011). A hierarchical Bayesian approach to record linkage and population size problems. Ann Appl Stat 5(2B):1553-1585.** https://projecteuclid.org/euclid.aoas/1310562733 ; DOI 10.1214/10-AOAS447 [seen: metadata and abstract]. A companion paper is in J Official Statistics 27(3):491-505 (2011) [seen]. Jointly models matching uncertainty and N for samples of multivariate categorical variables; Gibbs and Metropolis-Hastings; capture-recapture framing; illustrated by a real data example and simulations. Matters: the baseline for a joint (linkage, N) posterior. Does not scale to large file sizes without blocking. I did not retrieve numerical results.

2. **Tancredi, A., Steorts, R. C., Liseo, B. (2020). A unified framework for de-duplication and population size estimation (with discussion). Bayesian Analysis 15(2):633-682.** DOI 10.1214/19-BA1146; https://projecteuclid.org/journals/bayesian-analysis/volume-15/issue-2/A-Unified-Framework-for-De-Duplication-and-Population-Size-Estimation/10.1214/19-BA1146.full [seen]. Latent-entity model: records are noisy copies of key variables of N entities; N is a model parameter; extends Tancredi & Liseo (2011) and Steorts et al. (2016); shows how de-duplication relates to capture-recapture; more adequate prior on the linkage structure. Discussion includes Sadinle. Matters: it handles duplicates within a list as well as links across lists, which is the SAE situation (feature splitting and absorption create within-run near-duplicates). It also gives a prior over linkage structures that we could adapt.

3. **Sadinle, M. (2017). Bayesian estimation of bipartite matchings for record linkage. JASA 112(518):600-612.** [seen: abstract-level]. Argues Fellegi-Sunter independence assumptions are unrealistic; treats the bipartite matching as the parameter; builds a one-to-one constraint into the prior; gives Bayes estimates under chosen losses and **partial Bayes estimates that leave uncertain parts of the matching undecided**. Applied to El Salvador civil-war casualty files. **Sadinle & Fienberg (2013). A generalized Fellegi-Sunter framework for multiple record linkage with application to homicide record systems. JASA 108(502):385-397** [seen: abstract-level]: extends F-S to more than two files, one-to-one between any pair, and is not tractable beyond about three databases. A later Sadinle paper, "Multifile Partitioning for Record Linkage and Duplicate Detection" (arXiv:2110.03839, authors unverified), handles several files and within-file duplicates [seen as a title]. Matters: for N estimation, three-valued linkage decisions (link, non-link, undecided) give a natural bounds analysis: compute N with undecided pairs treated as links and as non-links.

4. **Fellegi, I. P. & Sunter, A. B. (1969). A theory of record linkage. JASA 64:1183-1210** [memory]. The classical framework: for each candidate pair compute agreement patterns; model them as a two-component mixture (matches M, non-matches U) with likelihood ratio m(γ)/u(γ); thresholds on the ratio give link / possible link / non-link, controlled by pre-set false-match and false-non-match rates. Directly applicable: EM on the joint distribution of (decoder cosine, activation correlation, encoder agreement, top-activating-token overlap) fits a two-component mixture and gives posterior match probabilities. Tools to mention [memory]: fastLink (R, Enamorado, Fifield & Imai 2019), splink (Python), recordlinkage (Python), blink and dga (R; the dga package appeared at olivierbinette.r-universe.dev [seen as a link]).

5. **Other linkage items that surfaced [seen, titles only]:** "Linking sequences of events with sparse or no common occurrence across data sets" (arXiv:1711.04248, authors unverified); "Scaling Bayesian probabilistic record linkage with post-hoc blocking: an application to the California Great Registers" (arXiv:1905.05337, authors unverified); "A review of modern multinomial-derived and partition-based record linkage" (Census Bureau RRS2024-05, https://www2.census.gov/library/working-papers/2024/adrm/RRS2024-05.pdf); "Optimal F-score matching for bipartite record linkage" (PMC13028598); "Fast Bayesian record linkage with record-specific disagreement parameters" (Sadinle-group, JASA 2021?). The "sparse or no common occurrence" paper is a lead for the regime where runs have very small overlap.

6. **Binette, O. & Steorts, R. C. (2022). (Almost) all of entity resolution. Science Advances** [memory; not searched]. A review of entity-resolution methods and their evaluation. Plausible background reading; mark unverified.

### 2.4 Multiple systems estimation (MSE) in the human sciences

1. **Manrique-Vallier, D., Price, M. E., Gohdes, A. (2013). Multiple systems estimation techniques for estimating casualties in armed conflicts.** HRDAG working paper: https://hrdag.org/wp-content/uploads/2013/04/Manrique_Price_Gohdes_WorkingPaper.pdf [seen: snippet]. Homogeneity and independence assumptions are demanding and unlikely to be met by real human-rights data; adding more lists enables models with weaker assumptions. HRDAG's stratification note (https://hrdag.org/2013/03/20/mse-stratification-estimation/) argues stratification lowers variance in capture probabilities [seen]. Also **Lum, K., Price, M. E., Banks, D. (2013). Applications of multiple systems estimation in human rights research. The American Statistician 67(4)** (https://www.researchgate.net/publication/262855607) [seen as a title]: a snippet reports their argument that very large uncertainty can signal serious violation of assumptions.
   - From memory only [unverified this session]: HRDAG applications include Kosovo (Ball et al. 2002, "Killings and refugee flow in Kosovo"), Peru (Truth and Reconciliation Commission 2003, about 69,000 deaths with MSE), Guatemala (Ball, Spirer & Spirer 2000), Syria (Price et al. 2013-2014 for UN OHCHR), Colombia. Manrique-Vallier (2016, Biometrics) introduced LCMCR, a Bayesian nonparametric latent class model for heterogeneity (R package LCMCR). **Please verify these before citing.**

2. **Silverman, B. W. (2014). Modern slavery: an application of multiple systems estimation. UK Home Office report.** [seen as a reference; the "10,000 to 13,000 potential victims for 2013" figure is from memory and the search did not confirm it]. **Silverman, B. W. (2020). Multiple-systems analysis for the quantification of modern slavery: classical and Bayesian approaches. JRSS A 183(3):691-736 (with discussion).** https://dx.doi.org/10.1111/rssa.12505 ; arXiv:1902.06078 [seen]. Discussants: Böhning called the approach as presented "unreliable" and questioned whether the "dark figure" can be estimated at all; others noted similar-fitting log-linear models can give very different totals; Cruyff and van der Heijden argued for regularization [seen].

3. **Chan, L., Silverman, B. W., Vincent, K. (2021). Multiple systems estimation for sparse capture data: inferential challenges when there are nonoverlapping lists. JASA 116(535):1297-1306.** DOI 10.1080/01621459.2019.1708748; arXiv:1902.05156; code https://github.com/bernardsilverman/MultipleSystemsEstimation ; R package SparseMSE [seen]. Poisson log-linear regression on sparse tables where some pairs of lists never overlap; MLE existence and identifiability; standard asymptotics fail when parameters are at extremes (negative infinity for non-overlap parameters); stepwise model selection. Matters: our overlap matrices between runs may have zero cells too (e.g., two SAE runs with very little overlap).

4. **Silverman, Chan, Vincent (2024). Bootstrapping multiple systems estimates to account for model selection. Stat Comput.** arXiv:2303.17856 [seen]. Matters: confidence intervals that ignore model selection are too narrow. We should bootstrap the whole pipeline, including matching.

5. **Binette & Steorts (2022). On the reliability of multiple systems estimation for the quantification of modern slavery. JRSS A 185(2):640-676.** DOI 10.1111/rssa.12803; arXiv:2112.01594 [seen: abstract; the publisher page lists only Steorts as author while arXiv lists Binette and Steorts]. Proposes an internal-consistency approach: build subsets of data for which ground truth is available and test MSE estimators; characterizes large-sample bias as a function of misspecified assumptions; visualises trajectories of MSE estimates under list omission or merging; releases all public modern-slavery datasets. Related: "Multiple systems estimation for modern slavery: robustness of list omission and combination" (ResearchGate listing, authors not retrieved) [seen]. **Whitehead, Jackson, Balch, Francis (2019). On the unreliability of multiple systems estimation for estimating the number of potential victims of modern slavery in the UK** and Silverman's reply "Misunderstandings of multiple systems estimation" [seen as titles]. Matters: Binette & Steorts' list-omission trajectories translate directly to "drop one run / merge two runs and see if N changes".

6. **Cruyff, Overstall, Papathomas, McCrea (2021). Multiple system estimation of victims of human trafficking: model assessment and selection. Crime & Delinquency** (https://journals.sagepub.com/doi/10.1177/0011128720981908) [seen]; **Vincent, Sharifi Far, Papathomas (2023). Common methodological challenges encountered with multiple systems estimation studies. Crime & Delinquency** (https://journals.sagepub.com/doi/10.1177/0011128720981900) [seen as titles]; **van Dijk, Cruyff, van der Heijden, Kragten-Heerdink (2017). Netherlands human trafficking MSE 2010-2015 (UNODC)** [seen as a citation in arXiv:1902.05156]. UNODC MSE manual for trafficking: https://www.unodc.org/documents/data-and-analysis/tip/2022/MSE_TIP_UNODC_ENG.pdf [seen as a link]. I did not read these.

7. **Zult, van der Heijden, Bakker. Bias correction in multiple-systems estimation. arXiv:2311.01297 (J Official Statistics 2025, 41(1), generalized Chapman estimator).** [seen]. Standard ML log-linear estimates are biased in small samples or small populations. A generalized Chapman estimator (extending two-list Chapman to ≥3 lists) shows hardly any bias and smaller SEs than other bias-reduced estimators in Monte Carlo; applied to homelessness in the Netherlands. Matters: for small counts (few features per run, few attacks) use Chapman-type small-sample corrections, not raw LP.

8. **Other MSE items surfaced [seen as titles]:** "Neural methods for multiple systems estimation models" (arXiv:2601.05859, authors unverified); "Performance of capture-recapture population size estimators under covariate information" (arXiv:2312.08391); "Estimation of population size based on capture recapture designs and evaluation of the estimation reliability" (arXiv:2105.05373); "Capture-recapture for casualty estimation and beyond: recent advances and research directions" (Springer chapter, https://link.springer.com/chapter/10.1007/978-3-030-75460-0_2).

9. **Epidemiology.**
   - **IWGDMF (1995). Capture-recapture and multiple-record systems estimation I: history and theoretical development; II: applications in human diseases. Am J Epidemiol 142:1047-1058 and 1059-1068.** [seen: citation details only; abstracts not retrieved].
   - **Hook, E. B. & Regal, R. R. (1995). Capture-recapture methods in epidemiology: methods and limitations. Epidemiol Rev 17:243-264** [seen as a citation; content from memory: main limitations are dependence between sources, heterogeneity, and incorrect matching; positive dependence typically gives underestimation of the total].
   - **Hook & Regal (1997). Validity of methods for model selection, weighting for model uncertainty, and small sample adjustment in capture-recapture estimation. Am J Epidemiol 145(12):1138-1144.** https://academic.oup.com/aje/article/145/12/1138/91636 [seen: abstract-level]. Model choice in log-linear capture-recapture can strongly change the estimate; estimates are highly sensitive when cells are null or sparse even with several sources; compares AIC with alternatives; assesses a small-sample correction.
   - **"On some pitfalls of the log-linear modeling framework for capture-recapture studies in disease surveillance"** (Epidemiologic Methods 2023; arXiv:2306.10666) [seen as a title; snippet says information criteria such as AIC can mislead]. **Gerritse, van der Heijden, Bakker (2015). Sensitivity of population size estimation for violating parametric assumptions in log-linear models. J Official Statistics** [seen as a title]. **Chao, A. et al. (2001). The applications of capture-recapture models to epidemiological data. Stat Med 20** [seen as a title]. **Farrington (2002). Interval estimation for Poisson capture-recapture models in epidemiology. Stat Med** [seen]. **Zhang et al. (2024). A capture-recapture modeling framework emphasizing expert opinion in disease surveillance** (PMC11347122) [seen as a title].
   - **Validation studies.** I could not find a systematic count of how many epidemiology capture-recapture studies were compared to a known total and how many showed serious bias. Evidence retrieved: (a) a simulation of cancer-registry completeness estimators with known truth found all capture-recapture estimators tended to underestimate completeness, with a modified DCN method and one type of log-linear model reasonable and others highly variable or grossly underestimating [seen via search summary; paper "Estimating completeness in cancer registries - comparing capture-recapture methods in a simulation study", authors not retrieved]; (b) New York birth defects: a two-source estimate of about 71% completeness showed the birth certificate source was unsuitable because of diagnostic discrepancies and false positives [seen]; (c) a review found performance of capture-recapture in resource-limited countries had not been systematically evaluated (van Hest et al. 2011, Trop Med Int Health, "Quality assessment of capture-recapture studies in resource-limited countries") [seen as a title and snippet]. Tailoring capture-recapture methods for error-prone diagnostic signals (PMC10766101) is the closest to "sources with false positives" [seen as a title]. **This remains an open question and should be followed up (see section 6).**

10. **Software-search and literature-search analogues (relevant but not my topic):** Webster & Kemp, "Estimating omissions from searches", Am Statistician 67(2):82-89 (2013); arXiv:1205.1150 [seen]: exact hypergeometric moments, a Bayesian approach, and the finding that Chapman and LP estimates conjectured in 1951 are often too small, with substantial errors in some published studies. Also capture-recapture used to estimate the number of articles available for systematic reviews (critical care medicine; one search captured about 15% of an estimated 28,839 articles, 95% CI 12,393-70,990) [seen]. Matters: a published example of how wide intervals get with few lists.

11. **US Census Post-Enumeration Survey (PES) and dual-system estimation (DSE)** [all from memory, not searched]:
    - Design: an independent sample of blocks (the P-sample) is interviewed after the census; its records are matched to census records (E-sample) to estimate coverage. DSE (Lincoln-Petersen with post-stratification) gives N-hat = C × (P / M) within each post-stratum.
    - Matching pipeline: computer matching, then clerical review by trained staff, then field follow-up for unresolved cases; the remainder get a probabilistic match-status imputed. Error rates in matching are monitored through quality-assurance re-review.
    - Known problems: correlation bias (people hard to count in the census are also hard to find in the PES, which biases the DSE downward, particularly for adult men), heterogeneity within post-strata, erroneous enumerations, and matching error. 2020 PES results as I recall them: overall net overcount of about 0.24% not significantly different from zero; undercounts of about 3.3% for Black, 5.0% for Hispanic and 5.6% for American Indians on reservations. These numbers must be verified before use.
    - Matters: this is the best-developed example of (a) a labelled review process for matching, (b) imputation of match status with variance propagation, and (c) a recognised residual bias (correlation bias) that is not fixable from the data alone. For us, "clerical review" is a human or strong-LLM re-adjudication of a sample of pairs, and "correlation bias" is that features hard for one SAE to find are also hard for the next.

---

## 3. Recommendations: matching SAE features and red-team attacks

### 3.1 Principle
Stop treating the match as given. Treat each pair of detections as having a match probability, estimate the error rates from labelled data, and carry the uncertainty to N.

### 3.2 SAE features across runs (decoder cosine, activation correlation, Hungarian)
1. **Match with a two-view score.** Combine decoder-direction cosine with activation correlation on a shared token sample (and optionally encoder-direction cosine, top-activating-token overlap). Each is a "mark" in the sense of McClintock/Bonner; disagreement between them is informative (section 2.1, item 8).
2. **Fit a Fellegi-Sunter-style two-component mixture** on the score vectors by EM to get a posterior match probability for each candidate pair. Use these as soft links. The mixture needs the distribution of non-match scores; in SAEs that includes the near-neighbours caused by feature splitting and absorption, so check that the non-match component is not mis-estimated.
3. **Do not force one-to-one blindly.** Hungarian assignment forces each feature to have exactly one partner. With feature splitting (Leask et al., 2502.04878) one large-SAE latent may correspond to several small-SAE latents. Compare one-to-one, one-to-many, and cluster-level definitions of "individual" and report N for each. Tancredi-Steorts-Liseo handle within-list duplicates natively.
4. **Estimate f and g from a validation subset.**
   - Synthetic setting (Phase 1): truth is known, so f(tau) and g(tau) are exact. Produce an error curve (f, g versus tau) for each SAE width, sparsity and noise level.
   - Real SAEs (Phase 2): there is no truth. Draw a stratified random sample of candidate pairs across score bins, label them with a stronger criterion (for example, auto-interpretation agreement on matched top-activating examples, steering/ablation similarity, or manual review), and estimate f and g by bin, with binomial intervals. Rough sizing: to estimate f = 0.1 to ± 0.05 you need about 140 truly matching pairs labelled (binomial calculation); rare bins need more.
   - Transport the curve with care. The error curve from synthetic data may not apply to real SAEs; use real-data labels to check it.
5. **Correct N using the estimated rates.**
   - For two runs: LP_corrected = LP × (1 − f) for false non-matches (exact in my derivation, section 2.2); for false matches solve m_obs = m + φ(n1·n2 − m) for m.
   - For Chao-type estimators: correct the frequency counts. First-order: false non-matches turn a fraction f of twice-detected features into two singletons, so f1_true ≈ f1_obs − 2f·f2 and f2_true ≈ f2_obs/(1 − f) roughly [first-order approximation, derived by me and not verified; check with injection simulation]. A sturdier alternative is to run the estimator on multiply-imputed matchings (item 6).
6. **Multiple imputation of matchings.** Draw matchings from the posterior (via the mixture model plus a one-to-one or cluster constraint, as in Sadinle 2017), compute N for each draw, and combine with Rubin's rules. The spread of N across draws is the linkage uncertainty. Tancredi & Liseo (2011) do this jointly in a full Bayesian model.
7. **Report the sensitivity curve.** Plot N-hat (Chao1, LP, jackknife) versus tau with confidence bands, overlay the number of clusters, the fraction of singletons (f1/S), and the estimated f and g. Look for a plateau. If f1/S and N-hat both rise sharply at high tau, you are in the ghost regime; if the cluster count collapses at low tau, you are in the chaining regime (section 2.2). If there is no plateau (as at σ=1.0), the data do not support any estimate; say so.
8. **Use sample-coverage and f1-based diagnostics.** Estimated sample coverage C = 1 − f1/n depends on ghosts in exactly the same way as Chao1. Report coverage next to N, and mark it unreliable when f1 is inflated.
9. **Compare with a version that removes the error-prone singletons**, e.g., estimators that discount low-confidence singletons (the microbiome literature has Chao-type corrections for sequencing-error singletons, Chiu & Chao 2016 [memory]).

### 3.3 Red-team attack strategies (rubric, LLM judge clustering)
1. **Treat "attack strategy" identity as a measured label.** Define a rubric, have at least two independent judges (different LLMs, or LLM plus human) cluster the same set of attacks, and use disagreement to estimate splitting and lumping rates. This copies the multi-observer design of Johansson et al. (2020), where observer disagreement quantified error and showed that errors inflate N by about a third.
2. **Planted-strategy design.** Plant a known list of strategies, generate attack paraphrases and novel variants, and run the judge pipeline. The truth gives f and g directly, and you can vary rubric granularity.
3. **Granularity is a threshold.** The level of the rubric (coarse tactic versus fine variant) is the analogue of tau. Report N at each granularity level, as with the sweeps in 3.2, and use the nested structure (coarse class contains fine variants) to check consistency: N_fine ≥ N_coarse, and the ratio should be stable.
4. **Soft assignment.** Ask the judge for probabilities over existing clusters plus "new", then use multiple imputation as in 3.2 item 6.
5. **Auxiliary covariates à la SPIM.** Use attack metadata (target behaviour, model used, prompt template) to disambiguate partial identity.

### 3.4 Experiments that inject known matching errors
All of these can be run first on the synthetic SAE testbed and the planted-attack setting.
1. **Error-grid injection.** Take a dataset with perfect matches and inject false non-matches at rates f ∈ {0, 0.02, 0.05, 0.1, 0.2, 0.3} and false matches at g ∈ {0, 0.01, 0.02, 0.05, 0.1}. Measure bias, RMSE and interval coverage for LP, Chapman, Chao1/Chao2, ACE, jackknife and log-linear/CMLE estimators. My prototype (`sim_a.py`) already shows the pattern; extend it with realistic overlap structure from synthetic SAEs.
2. **Mis-specified correction.** Inject errors at rate f, but correct with an estimated f̂ from a validation subset of size n_v ∈ {50, 100, 200, 500}. Plot residual bias against n_v. This gives the labelling budget needed.
3. **Score-based injection.** Rather than uniform random errors, generate errors by corrupting scores (noisy-copy model, section 2.2) at several noise levels, and verify that the plateau diagnostic predicts when the estimate is trustworthy.
4. **Heterogeneity versus matching confound.** Simulate matched pairs with both heterogeneous catchability and matching error; test whether estimators can tell them apart (the MARK-book warning). Add a version in which error rates vary by feature (rare features match worse), as in McClintock et al. 2014.
5. **Drop-one and merge-two runs** (Binette & Steorts-style internal consistency) to check that N-hat does not change implausibly.
6. **Bootstrap the whole pipeline** including matching and model selection (Silverman et al. 2024 for model selection).
7. **Gold-standard check on real SAEs**, in the spirit of the whale-photo-ID versus microsatellite comparison: find a subset where an independent measure of identity exists (for example, features that can be matched with high confidence by causal-effect similarity) and compare N from the cheap matcher against it.

---

## 4. Pitfalls and warnings
- **Identity matching is not a nuisance parameter; it is the data.** Ghosts and merges change f1, f2 and m, which are the inputs to every estimator.
- **Errors can cancel.** Chao1's downward bias under heterogeneity plus ghost inflation gives a deceptively accurate N at one threshold [sim].
- **False matches matter most when overlap is small**, because a handful of spurious recaptures dominates m (section 2.2). Low-overlap regimes (large SAE dictionaries, few runs) are where this bites.
- **Chaining under transitive closure.** Pairwise matches across K runs can merge unrelated clusters at low tau [sim].
- **Error rates are not constant.** They vary by item quality (McClintock et al. 2014) and by neighbourhood density. A single global f is optimistic.
- **Identifiability.** Do not estimate misidentification and heterogeneity jointly from capture histories alone (MARK book; Vale et al.; Fraysse et al.).
- **MSE's own track record is contested.** The UK modern-slavery estimates were publicly disputed; model selection alone moved results a lot; sparse zero cells make standard asymptotics fail. Cite MSE as a source of methods and cautionary tales, not as evidence the approach works.
- **Correlation bias (census) is not fixable by better matching.** If features that are hard for one run are hard for all, estimators underestimate regardless of matching quality.
- **Validation might not transport.** An error curve from synthetic SAEs may not apply to real SAEs or to LLM judges.
- **Some details above are from memory** (HRDAG country studies, census PES numbers, Fellegi-Sunter details, software package attributions). Verify before citing.

---

## 5. Datasets, code and tools
- **multimark** (R): https://onlinelibrary.wiley.com/doi/10.1002/ece3.1676 ; implements Bonner-Holmberg and McClintock bilateral models; includes spatial versions [seen].
- **SparseMSE** (R, CRAN): https://rdrr.io/cran/SparseMSE/ ; GitHub https://github.com/bernardsilverman/MultipleSystemsEstimation [seen].
- **Modern-slavery public datasets** released by Binette & Steorts (arXiv:2112.01594) [seen as a claim in the abstract].
- **HRDAG MSE tutorial:** https://hrdag.org/tech-notes/basic-mse.html [seen as a link]. LCMCR (R) [memory].
- **dga** (R, decomposable graphical models for MSE) at olivierbinette.r-universe.dev [seen as a link].
- **Rcapture** (R) and MARK [memory / from the proposal]. **fastLink, splink, recordlinkage, blink** for linkage [memory].
- **Simulation code from this session:** `scripts/sim_a.py` (identity-error injection on capture histories) and `scripts/sim_b.py` (cosine-threshold sweep with Hungarian matching and union-find). Both run in a few seconds on CPU.

---

## 6. Open follow-ups (not done because the search budget ended)
1. Systematic evidence on how often epidemiologic capture-recapture estimates differ from a known total (search: "capture-recapture validation known total", Tilling & Sterne, Papoz, Brenner 1995, Hook & Regal 1995 text).
2. HRDAG country papers (Kosovo, Peru, Guatemala, Syria, Colombia) and published critiques; confirm numbers.
3. US Census PES technical documentation (2010 CCM and 2020 PES: matching rates, clerical review, imputed match status, correlation bias).
4. Fellegi-Sunter details, fastLink paper, Steorts' blink and microclustering papers; Enamorado et al. 2019.
5. Primary sources for the 920% photo-ID software bias claim and the whale-microsatellite validation.
6. Full text of Tancredi & Liseo 2011 and Tancredi-Steorts-Liseo 2020 for the simulation results on how linkage uncertainty widens N intervals.
7. Singleton-error-corrected Chao estimators from the microbiome literature (Chiu & Chao 2016; Kunin et al. 2010) as a template for ghost-singleton correction.

---

## 7. Search log (about 24 searches; budget exhausted)
Extended mode throughout.
1. Link, Yoshizaki, Bailey, Pollock 2010 latent multinomial.
2. Tancredi & Liseo 2011 AoAS.
3. Chan, Silverman, Vincent 2021 JASA sparse MSE.
4. McClintock/Bonner bilateral photo-ID (clarified authorship).
5. Vale, Fewster et al. 2014 Mt,α (first query failed on title, found via the probit paper; second query found the paper).
6. Lukacs & Burnham 2005.
7. Wright et al. 2009.
8. Camera-trap identification errors overestimation (Johansson 2020).
9. Matching uncertainty in photo-ID abundance (Ashe & Hammond 2022).
10. Augustine et al. 2018 spatial partial identity.
11. Fraysse et al. arXiv:2304.00885.
12. Tancredi, Steorts, Liseo 2020.
13. Sadinle 2017 and Sadinle & Fienberg 2013.
14. Yoshizaki et al. 2009/2011.
15. Picek et al. 2026 automated individual ID.
16. Schofield & Bonner 2015.
17. Automated photo-ID threshold false-match/non-match bias.
18. HRDAG MSE criticisms.
19. Binette & Steorts reliability of MSE for modern slavery.
20. Zult et al. bias correction in MSE.
21. Silverman 2014 and Dutch MSE criticisms.
22. Epidemiology validation against known totals (Hook & Regal).
23. Webster & Kemp, estimating omissions from searches.
24. Hook & Regal 1997; IWGDMF 1995; capture-recapture validation with gold-standard registries.
Four further searches (van Hest 2011 quality assessment, error-prone diagnostic signals, the log-linear pitfalls paper, Brenner 1995) were refused because the shared per-turn budget was spent.
