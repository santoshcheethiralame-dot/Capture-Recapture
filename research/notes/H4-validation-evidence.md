# H4. Gap-filling: validation evidence for capture-recapture/MSE, HRDAG, Census PES, record linkage, singleton correction, recent few-list methods

Project: "What did we miss? Capture-recapture for safety tools". Date: 22 Oct 2026. Gap-filling round after `B_misid_and_mse.md`.

Search budget: 40 WebSearch calls used (the maximum). Search results were again mostly abstracts and snippets, not full texts. Labels:
- **[seen]** appeared in a search result this session; numbers come from the snippet or abstract.
- **[memory]** background knowledge, not checked. Treat as unverified.
- **(unverified)** a detail I could not confirm.
- Several searches I aimed at specific papers (Tilling & Sterne, Papoz, Brenner 1995 Epidemiology, Hook & Regal 1995/2000, Jarvis, Briand 2000) returned only bibliographic data. I say so explicitly below instead of filling gaps from memory.

---

## 1. Summary

1. **There is no systematic "how often is CRC wrong" meta-study that I could find, but a consistent pattern exists across independent sources.** Where truth or a strong prior is available, estimates are biased in predictable directions when assumptions fail, and model choice alone can move the answer by tens of percent. Examples below: Dutch TB (37% vs 7% under-notification), Verona diabetes (46% vs 87.5% completeness from two different source pairs), cancer-registry simulations (all CRC estimators tended to underestimate completeness), saturated log-linear model (8,053 vs truth 5,000).
2. **Direction of bias is the standard result.** Positive dependence between sources gives underestimation of N; negative dependence gives overestimation. Hook & Regal observed that most epidemiological datasets have net positive dependence, so the typical failure is an underestimate [seen via citing papers]. Heterogeneity induces positive dependence between lists. A positive three-way interaction biases three-source infectious-disease estimates downward [seen]. For our project this means the default failure for "what did we miss" is a lower bound that is too low, which is the unsafe direction for safety claims.
3. **Dependence and heterogeneity are confounded and the data cannot separate them** without covariates or extra structure [seen]. This is the same confound B flagged for matching error vs heterogeneity. We now have three stacked non-identifiabilities: dependence, heterogeneity, matching error.
4. **Model selection is a first-order error source.** Simulation of three lists, true N = 5,000: AIC picked the same model about 80% of the time, yet its average estimate was far from truth, and the saturated model (nearly always chosen) averaged 8,053 (Zhang, Ge, Waller, Lyles; arXiv 2306.10666) [seen]. Conversely, Wesson et al. 2022 (N = 1,000, three lists, 500 reps) found AIC-selected log-linear models accurate in all scenarios except sparse or zero cells [seen]. So the failure mode is sparse tables, which is our regime (few runs, many singletons).
5. **Software-inspection CRC is the closest analogue to our setting** (a "defect" is found by some inspectors and not others; defects can be seeded). Findings from abstracts [seen]: with fewer than 4 inspectors no model was accurate enough (Briand et al., TSE 2000); the Mh-jackknife estimator was most robust across studies (Petersson et al., JSS 2004 review); accuracy rises with more defects found and more reviewers. This is direct precedent for "need K >= 4 runs, and jackknife-type estimators for heterogeneity". Underestimation was frequent but the sources do not establish a general rule.
6. **HRDAG's best validation is Kosovo, and it is only partly independent.** The 2002 ICTY estimate was 10,356 killings (95% CI 9,002 to 12,122) from 4 lists and 4,400 documented victims. A later census-style Humanitarian Law Center database counted about 9,945 victims for a comparable period (and about 9,030 murders plus 1,200 missing in another description) [seen via HRDAG pages; counts differ by definition and period]. A re-analysis with bootstrap over model selection gave a much wider interval (10,357, CI 7,133 to 18,681) [seen]. So: point estimate roughly right, interval too narrow.
7. **Peru is not validated by truth; it is contested.** TRC/HRDAG total 69,280 (95% interval 61,007 to 77,551 in the later latent-class re-analysis, arXiv 1906.04763) [seen]. Rendon (2019) argues the indirect, perpetrator-by-subtraction design is flawed; Manrique-Vallier and Ball (2019) rebut it with a "selection bias" argument and impossibility of his Shining Path number. Rendon's rejoinder is titled "A truth commission did not tell the truth" [seen]. Lesson: the same lists give different totals under different stratification and decomposition choices, and there is no truth to settle it.
8. **Record-linkage error propagates into N, and correction methods exist.** Di Consiglio & Tuoto (JOS 2015; JOS 2018 multiple lists; sensitivity analysis 2018) extend Ding & Fienberg (1994) to give linkage-error-corrected dual-system estimators; their simulations favour the adjusted estimator over naive Petersen [seen]. Dasylva et al. (arXiv 2403.11438, 2024) model the number of links per record to correct without clerical review [seen]. Both directly extend our f/g correction plan.
9. **Spurious singletons have a published "record-linkage" treatment.** Di Cecco & Tancredi (2024, Environ Ecol Stat 31:485-507) model spurious singletons in microbial diversity as false-negative record-linkage errors and compare with deleting them. Finding: the estimate of total species is essentially the same under both, but Shannon index can differ noticeably [seen]. Chiu & Chao (2016, PeerJ 4:e1634) replace observed f1 by an f1 estimated from f2, f3, f4 and plug into Chao1 [seen]. The gap between estimated and observed singletons is a diagnostic for sequencing error. This is the template for "ghost singletons".
10. **Do not use singleton-based estimators when singletons are unfixably noisy.** A 2024 ISME J paper says Chao1 and ACE "must not be used" with ASV data because denoising cannot separate true singletons from artifacts [seen]. breakaway_nof1 avoids f1 altogether [seen]. For us: report an f1-free estimator (e.g. from f2, f3 and above) as a robustness check.
11. **Recent methods for few lists with dependence all weaken identification rather than recover it.** Doubly robust CRC (Das, Kennedy, Jewell; arXiv 2104.14091; R package drpop) assumes lists are conditionally independent given covariates and offers bounds under approximate independence [seen]. Dependence-robust intervals (Sun, Van Baelen, Plettinckx, Crawford; arXiv 2008.00127; JSSAM 2023) give partial-identification confidence sets from bounds on pairwise capture probabilities [seen]. Neural methods (arXiv 2601.05859) amortise Bayesian MSE inference and reportedly avoid MCMC convergence failures on sparse data [seen as abstract]. Dennett & Bohning (arXiv 2312.08391) study Horvitz-Thompson, generalised Chao and generalised Zelterman with covariates, with a follow-up on one-inflation [seen as abstract; results not seen].
12. **US Census PES is operationally the cleanest "match then estimate" pipeline** (computer match, clerical review, field follow-up, imputation of unresolved match status, logistic-regression DSE, explicit correlation-bias adjustment), but I could not retrieve person-level match error rates or the exact correlation-bias values.

---

## 2. Papers and sources

### 2.1 Validation evidence: CRC/MSE against known or well-constrained totals

**Honest scope note.** I looked for a systematic count of validation studies and found none in search results. What follows is a set of concrete examples. Do not cite "X% of studies are biased" from this document.

1. **Dutch TB notification (van Hest et al., 2007, Epidemiol Infect; PubMed 17156496), "Completeness of notification of tuberculosis in The Netherlands: how reliable is record-linkage and capture-recapture analysis?"** [seen: abstract-level].
   - First log-linear model: estimated total 2,053 TB cases (95% CI 1,871 to 2,443), i.e. 36.8% under-notification.
   - After adjusting for imperfect record linkage and remaining false-positive hospital cases, models gave 13.6%, and the authors report a final 7.3% under-notification.
   - So the naive estimate of the missing fraction was off by a factor of roughly 5, with two named causes: linkage error and false positives in a source.
   - Matters here: this is the best-documented case of "matching error plus false-positive detections inflate the unseen count". It is the same two errors as ghost features and spurious attacks.

2. **England TB 1999-2002 (van Hest et al., 2008, Epidemiol Infect), "Record-linkage and capture-recapture analysis to estimate the incidence and completeness of reporting of tuberculosis in England 1999-2002"** [seen: abstract-level].
   - Log-linear completeness was "highly inconsistent with prior estimates", so the authors examined validity of the method. A follow-up (van Hest et al., "Estimating infectious diseases incidence: validity of capture-recapture analysis and truncated models for incomplete count data", Epidemiol Infect 2010, PMC2870770) says three-source log-linear analyses on both Dutch and English TB data gave "unexpected and unrealistic" incidence estimates "despite using well-described procedures" for model selection, and proposes truncated models [seen]. (A WHO slide deck quotes overall observed under-notification 15.9% and structural-model ascertainment 66.7%; I could not confirm against the paper (unverified).)
   - Matters: the validation was by plausibility against external knowledge, not a known total. Still strong evidence that "standard procedure" can produce unrealistic N.

3. **Verona diabetes study (Care 2000; 23(6):759), "Capture-recapture method in the epidemiology of type 2 diabetes"** [seen: abstract].
   - Pairing family physicians with a prescription database gave completeness 87.5%; pairing the diabetes centre with the same prescription database gave 45.9%. Cause: sources were dependent (prescriptions positively associated with family physicians, negatively with the diabetes centre).
   - Matters: the same truth, two different list pairs, completeness estimates differing by a factor of about 2. This is the cleanest demonstration that "which runs you pair" matters. For us: report all run-pair LP estimates, not one.

4. **Cancer-registry completeness simulation, "Estimating completeness in cancer registries - comparing capture-recapture methods in a simulation study"** (PubMed 19067337; authors not retrieved) [seen]. All CRC estimators tended to underestimate completeness; a modified DCN method and one type of log-linear model were reasonable; others were highly variable or grossly underestimated.

5. **Zhang, Ge, Waller, Lyles. On some pitfalls of the log-linear modeling framework for capture-recapture studies in disease surveillance. Epidemiologic Methods 2023-2025; arXiv 2306.10666; PMC11741671** [seen].
   - In a scenario with true N = 5,000, AIC chose one model about 80% of the time yet its average estimate was far from truth; the saturated model was almost always chosen as best and averaged 8,053.
   - Argues that log-linear models "exclude by design" many estimates consistent with the data and that information criteria are deceptive because the key assumption is untestable.
   - Matters: do not rely on in-sample fit to certify an N estimate. Validation must use external truth.

6. **Wesson, Jewell, McFarland, Glymour (2022). Evaluating tools for capture-recapture model selection to estimate the size of hidden populations: it works in practice, but does it work in theory? Ann Epidemiol** [seen].
   - Simulated 1,000-person population with three incomplete lists, 500 replicates per scenario, varying dependence. AIC-selected log-linear models were accurate everywhere except sparse or zero cell counts; there, decomposable graphs and sample coverage approaches did better. Recommendation: fit several models and triangulate.
   - Matters: a ready simulation design (three lists, N = 1,000, 500 reps) we can mimic with K = 3 runs, and a hint that sample coverage is the robust fallback when cells are sparse.

7. **Grimm, Gruber, Henle (2014). Reliability of Different Mark-Recapture Methods for Population Size Estimation Tested against Reference Population Sizes Constructed from Field Data. PLOS ONE 9(6):e98840 (PMC4045897)** [seen].
   - Twelve estimators evaluated for bias, precision, accuracy and CI coverage against reference populations built from an intensively studied gecko (Gehyra variegata) population. Heterogeneity-aware models did best; covariate models and mixture models performed poorly; the truncated geometric method was the only one that did not underestimate with a long tail of low capture probabilities (but it tended to overestimate).
   - Matters: an ecology example of a "constructed truth from real data", the template for our synthetic-SAE and planted-attack validation. Also: long low-capture tails (our rare features) are where most estimators fail.

8. **Software inspections (seeded and naturally occurring defects)** [seen: abstract-level only].
   - Briand, El Emam, Freimut, Laitenberger (2000). A comprehensive evaluation of capture-recapture models for estimating software defect content. IEEE TSE 26(6):518-540. Per abstracts: with fewer than 4 inspectors no model was sufficiently accurate. El Emam & Laitenberger (2001) "Evaluating capture-recapture models with two inspectors" (IEEE TSE) addresses the small case; content not seen.
   - Petersson, Thelin, Runeson, Wohlin (2004). Capture-recapture in software inspections after 10 years research. J Syst Softw. Review finding: most studies find Mh with jackknife the most robust; accuracy improves with more faults found and more reviewers. A 2016 study on requirements documents reports estimators swing from negative bias after one inspection to positive bias after two [seen, secondary].
   - A seeded-defect study found Mh-JK and Mt-Ch best and that not all estimators helped make correct reinspection decisions, motivating decision-based accuracy (relative decision accuracy) rather than relative error [seen, secondary].
   - Matters: decision-based accuracy is the right metric for us (does the estimate lead to the right "keep searching or stop" decision?). Also: independent teams of 2 are insufficient.

9. **Hook & Regal (1995, Epidemiol Rev 17:243-264), Hook & Regal (1997, AJE 145:1138), Hook & Regal (2000, AJE 152(8):771-779, "Accuracy of alternative approaches to capture-recapture estimates of disease frequency: internal validity analysis of data from five sources").** [seen: bibliographic data and citing statements only]. The abstract of the 2000 paper was not retrieved. The citing literature attributes to Hook & Regal: net positive dependence is typical in epidemiology, giving underestimates [seen]. The 1997 abstract (from B) says model choice and sparse cells strongly change estimates.

10. **Brenner (1995). Use and limitations of the capture-recapture method in disease monitoring with two dependent sources. Epidemiology 6(1)** [seen: citation only]. Via citing papers: bias of Lincoln-Petersen and Chapman estimators rises with the dependence odds ratio; with negative dependence, the under-ascertainment of registries turns into an overestimate of cases [seen, secondary]. The paper itself was not retrieved. Brenner, Stegmaier, Ziegler (1995, JECH) evaluated the two-source method for cancer registration in Saarland [seen: citation only].

11. **Not found in search results:** Papoz et al. diabetes validation, Jarvis et al. injury paper, Tilling & Sterne 1999 (AJE 149:392-400, "Capture-recapture models including covariate effects"; only metadata and the sentence that covariate/stratified analyses are used, comparing log-linear and logit models), Tilling 2001 IJE "Capture-recapture methods - useful or misleading?" (title only). Do not quote results from them.

12. **Other items surfaced [seen as titles]:** "Recapture or Precapture? Fallibility of Standard Capture-Recapture Methods in the Presence of Referrals Between Sources" (AJE 2014; PMC4036210), arguing many epidemiological CRC studies involve referrals between sources and may be biased. In our setting, "referral" corresponds to runs that share seeds, data or prompts. "Model selection and model robustness for population size estimation in 2-sample capture-recapture studies" (AJE 194(9), 2025). "Evaluating a Targeted Minimum Loss-Based Estimator for Capture-Recapture Analysis" (AJE 2024; PMC10999650). "Sensitivity and Uncertainty Analysis for Two-Stream Capture-Recapture Methods in Disease Surveillance" (medRxiv 2022). "Capture-Recapture Estimators in Epidemiology with Applications to Pertussis and Pneumococcal Invasive Disease Surveillance" (PLOS ONE 2016; PMC4987016).

### 2.2 Summary of how often estimates were badly off and why (from the above)

| Case | Naive/standard estimate | Reference | Main cause |
|---|---|---|---|
| Netherlands TB 1998 | 36.8% under-notification | 7.3% after adjustment | linkage error plus false-positive source |
| Verona diabetes | 87.5% or 45.9% completeness depending on pair | same truth | source dependence |
| Three-list simulation, N = 5,000 | saturated model mean 8,053 | 5,000 | model selection with untestable assumption |
| Cancer-registry simulation | underestimation common | known | dependence, heterogeneity |
| Software inspections | inaccurate with < 4 inspectors | seeded or known defects | small K, heterogeneity |
| Kosovo MSE (HRDAG) | 10,356 (9,002 to 12,122) | about 9,945 census-style count, different scope | broadly right; CI too narrow per bootstrap re-analysis |
| Photo-ID (from B) | up to +920% (software), +35% (observer errors) | known | matching error |

Why: (a) list dependence and heterogeneity (mostly downward bias); (b) false positives and linkage error (mostly upward bias in N via ghost singletons; downward via false matches in the low-overlap LP regime, per B); (c) sparse tables and model selection; (d) too few lists; (e) extrapolating a tail of low-probability items with no data.

### 2.3 HRDAG

1. **Kosovo.** Ball, Betts, Scheuren, Dudukovic, Asher (2002), "Killings and Refugee Flow in Kosovo, March-June 1999", report to ICTY. Four lists (ABA/CEELI interviews, HRW interviews, OSCE interviews, ICTY exhumations) with 4,400 documented victims; estimate 10,356 Kosovo Albanian civilian killings, 95% CI 9,002 to 12,122 [seen: HRDAG and secondary pages]. An earlier HRDAG report (2000) gave 10,538 (7,440 to 13,636) for a slightly different window [seen]. The estimate was controversial at publication because critics doubted exhaustive recording could be so incomplete; HRDAG says later data bore it out. Spagat's 2014 evaluation of the Kosovo Memory Book found excellent consistency across the BBSDA, Spiegel-Salama and Memory Book totals, but it is an evaluation of the Memory Book, not an attack on the MSE [seen]. A bootstrap reanalysis (Silverman, Chan, Vincent) shows wider intervals when model selection is included (10,357, [7,133, 18,681]) [seen via HRDAG page].
2. **Peru.** TRC (2003) most probable total 69,280 deaths, using the TRC database plus five others, stratified by location and perpetrator; Shining Path killings estimated indirectly by subtraction because direct estimation was infeasible [seen]. Manrique-Vallier (arXiv 1906.04763) re-estimates with LCMCR-type latent class models: 69,280 with 95% interval [61,007, 77,551] and consistent perpetrator shares [seen]; other reported ranges for latent-class variants 58,000 to 66,000 [seen, secondary; unverified which models].
   - Critique: Rendon (2019), "Capturing correctly: a reanalysis of the indirect capture-recapture methods in the Peruvian Truth and Reconciliation Commission", Research & Politics 6(1), doi 10.1177/2053168018820375. Claims that direct estimation with strict stratification by perpetrator and handling of missing data does not support the TRC's indirect results; reported total lower, with a higher state share. One secondary source says about 48,000 (unverified; not seen in Rendon's text).
   - Response: Manrique-Vallier & Ball (2019), "Reality and risk: a refutation of S. Rendon's analysis...", Research & Politics, doi 10.1177/2053168019835628: argues his Shining Path estimate is lower than the observed data and therefore impossible, and that his approach has a subtle selection bias. Rendon rejoinder: "A truth commission did not tell the truth" (2019).
   - HRDAG's own post (2019) says accuracy "ultimately rests in the quality of our matching of the datasets" and warns two-list estimates are not appropriate here [seen].
3. **Syria.** HRDAG/OHCHR: 93,000 reported identifiable casualties as of June 2013 in the earlier HRDAG-for-OHCHR report [seen]. UN OHCHR 2022: eight sources; estimated 306,887 civilians killed (95% credible interval 281,443 to 337,971), i.e. 163,537 beyond documented [seen]. Method note from HRDAG: with five lists there are 32 overlap patterns and about half need to be non-empty for the estimator to work [seen]. Related: "Unique entity estimation with application to the Syrian conflict" (arXiv 1710.02690) [seen as a title; authors and venue not confirmed]; "Nested Dirichlet Process for population size estimation from multi-list recapture data" (arXiv 2007.06160) applies to Syria [seen].
4. **Colombia.** HRDAG supported JEP and the Truth Commission (CEV) 2018-2023, integrating data and estimating victim counts; released the R package verdata (JOSS 2024) [seen]. I did not confirm the 450,664 homicide figure (unverified, do not cite).
5. **Guatemala.** Not found in searches (Ball, Spirer & Spirer 2000, and the 1999 CEH figure of about 200,000 dead [memory]) (unverified).
6. **Methods.** Early HRDAG work used stratified log-linear models; Manrique-Vallier (2016), "Bayesian population size estimation using Dirichlet process mixtures", Biometrics 72, doi 10.1111/biom.12502 (R package LCMCR) models heterogeneity through latent classes, tolerates sparse tables and adjusts complexity without a separate model-selection step [seen]. Manrique-Vallier, Price & Gohdes (2013) argue homogeneity and independence are unlikely in conflict data, hence more lists help [seen]. "On the identifiability of latent class models for multiple-systems estimation" (arXiv 2008.09865) [seen as a title] is the relevant caution: latent class models are only partly identified. Lum, Price, Banks (2013, Am Stat) note very large uncertainty can signal violated assumptions [seen via B].
7. **Lessons.** HRDAG is the best long-running practice of (i) stratifying before estimating, (ii) using 4 to 8 lists, (iii) comparing against later independent enumerations when possible, (iv) publishing the matching process. But the validation is thin and rests on one or two cases; critics focus on stratification and decomposition choices, not just matching.

### 2.4 US Census Post-Enumeration Survey (brief)

- **Design** [seen: Census Bureau docs listed; memos]: DSE on independent P-sample vs census records. 2020 PES used logistic regression rather than post-stratification to produce DSEs, and applied a correlation-bias adjustment for some subgroups (Census Bureau memo, 2020 PES estimation design) [seen]. State estimates were improved by state-specific effects, at the cost of variance [seen].
- **Matching pipeline** [seen]: automated probabilistic matching, clerical matching, field follow-up; remaining unresolved match, enumeration and residence statuses are imputed by models. For 2010 CCM housing units, clerical matching moved matches from 72.9% to 93.5% and non-matches from 15.4% to 3.7% (Contreras et al. 2012, as quoted) [seen]; that is housing units, not persons. Reisch (2019) tested replacing clerical review and follow-up with model imputation, noting that omission would raise non-match and unresolved counts [seen]. Person-level 2010 match error rates were not retrieved.
- **Biases** [seen]: correlation bias biases DSE downward (people missed by the census are more likely missed by the PES); heterogeneity bias arises when census capture rates differ across geography within a post-stratum. Wolter (1990) approach uses known sex ratios (demographic analysis) as extra data to avoid independence, limited because DA exists only at the national level [seen]. The exact 2020 adjustment values were not retrieved.
- **2020 results** [seen via news copy of the March 2022 release, not checked against the Bureau's table]: total net undercount 0.24% (not statistically significant), Black 3.3%, Hispanic about 5%, American Indian/Alaska Native on reservations 5.6%, non-Hispanic White net overcount 1.6%, Asian overcount 2.6%.
- **Linkage error in DSE.** Di Consiglio & Tuoto (JOS 2015, doi 10.1515/jos-2015-0025) extend Ding & Fienberg (1994) with a linkage-error-corrected Petersen estimator; simulations show adjusted always performs better; applied to road casualties. Multiple lists: JOS 2018 (doi 10.2478/jos-2018-0044); sensitivity analysis: Statistical Journal of the IAOS 2018. Naive linkage-error corrected DSE: Racinskij (arXiv 2003.13080) (results not seen). Dasylva, Goussanou, Nambeu (arXiv 2403.11438, 2024) correct for false positive and negative links by modelling links per record, without clerical review [seen]. UK Census 2021 coverage uses a dependence-bias adjustment (ONS EAP160) [seen as title only].
- **Matters:** a ready workflow (automated match, clerical sample, imputation, correlation bias adjustment) and a published family of linkage-error-corrected estimators we can test on injected errors.

### 2.5 Record linkage tools and methods

1. **Fellegi & Sunter (1969), JASA 64:1183-1210** [memory]. Mixture of match and non-match agreement patterns, likelihood-ratio thresholds.
2. **fastLink: Enamorado, Fifield, Imai (2019), APSR, "Using a probabilistic model to assist merging of large-scale administrative records"** [seen]. EM Fellegi-Sunter with missing-data handling, blocking, and posterior match probabilities; R package. Authors' validation on RLdata500: false negative rate 0.003, false discovery rate 0.000 versus 0.020/0.040 for an empirical Bayes method; threshold choice among 0.75/0.85/0.95 did not alter qualitative results. **Independent evaluations are worse:** Robach 2025, Statistics in Medicine / arXiv 2503.20627, found fastLink's true false discovery proportion stuck at 0.73 on one synthetic task; the California Great Registers paper (arXiv 1905.05337) found overall estimated false match rate 0.27 (fastLink) vs 0.11 for the Bayesian model, mainly from movers; a text-embedding linkage paper (Political Analysis) reported fastLink precision 93.3%, recall 63.1% on voter files [all seen, secondary]. Lesson: author-reported error rates on clean benchmarks do not transport, so we must measure f and g on our own data.
3. **Steorts, Hall, Fienberg (2016), JASA 111(516):1660-1672, "A Bayesian approach to graphical record linkage and de-duplication" (blink; earlier SMERED, JMLR 2014)** [seen: citation]. Latent entity model with string pseudo-likelihood; blink is the base for d-blink (Marchant et al.; arXiv 1909.06039) [seen]. **Microclustering:** Betancourt, Zanella, Miller, Wallach, Zaidi, Steorts (NeurIPS 2016), "Flexible models for microclustering with application to entity resolution" (arXiv 1610.09780): cluster sizes grow sublinearly with data size, appropriate when entities have few records [seen]. Zanella et al.'s earlier work on theoretical limits (arXiv 1703.04955) and performance bounds for graphical record linkage (arXiv 1703.02679) [seen as titles].
   - Why it fits: each feature or attack appears in at most K runs, so cluster sizes are bounded by K, exactly the microclustering regime. A prior over partitions with bounded cluster size is natural.
4. **Binette & Steorts (2022). (Almost) all of entity resolution. Science Advances 8(12), eabi8021; arXiv 2008.04443** [seen]. Review; key points for us: evaluation needs ground truth that is often missing or biased; metrics are sensitive to noise level and the reliability of identifiers; do not rely on toy datasets; pairwise comparison cost N(N-1)/2. Follow-ups: Binette, Steorts et al., "Estimating the performance of entity resolution algorithms: lessons learned through PatentsView.org", Am Stat 77(4) (arXiv 2210.01230) [seen as a title]; "Unsupervised evaluation of entity resolution" (ACM 2025, 10.1145/3721985) and the method in the 2022 paper that estimates true/false/missed matches without labels from link structure [seen]. Plus Binette & Steorts, "On the reliability of multiple systems estimation for the quantification of modern slavery" (JRSS A 2022; arXiv 2112.01594), already in B.
5. **Propagating linkage uncertainty into N.** Tancredi & Liseo (2011, AoAS 5(2B)) and Tancredi, Steorts, Liseo (2020, Bayesian Analysis 15(2):633-682) are in B. This round I could not retrieve their numerical results. What I confirmed: the 2020 paper uses a latent entity model over N entities, treats N as a parameter, extends the 2011 model and Steorts et al. 2016, was tested on RLdata500/RLdata10000 simulated data, and in the discussion Sadinle argues linkage uncertainty must be considered when estimating population size [seen]. Do not quote interval-width inflation numbers; run our own experiment (section 3).
6. **Sparse-overlap relevance:** the Di Consiglio & Tuoto and Dasylva et al. methods assume an observed link structure plus estimated error rates; Tancredi-style joint models do not need clerical review but scale poorly.

### 2.6 Singleton-error correction in species richness

1. **Chiu & Chao (2016). Estimating and comparing microbial diversity in the presence of sequencing errors. PeerJ 4:e1634** (https://peerj.com/articles/1634/) [seen: abstract and secondary descriptions].
   - Idea: sequencing errors create spurious singletons (and a few doubletons) that inflate Chao1; estimate the true number of singletons from the frequencies of doubletons, tripletons and quadrupletons (assuming the true frequency counts follow a pattern that makes f1 predictable from f2, f3, f4), then replace f1 by that estimate in Chao1 (adjusted estimator; a separate formula applies when f2 = 0).
   - Applied to two virome datasets, where unadjusted Chao1 lower bounds were judged inflated. Without errors, the adjusted estimator differs only slightly from the unadjusted one, so it is safe to use as a default.
   - Gap f1_obs minus f1_est is a diagnostic of error. R code is on Chao's site; iNEXT issue #57 asks about building it in [seen]. Supplement S2 contains simulation.
   - The exact formula was not shown in the search output; I will not write it from memory.
2. **Kunin, Engelbrektson, Ochman, Hugenholtz (2010). Wrinkles in the rare biosphere: pyrosequencing errors can lead to artificial inflation of diversity estimates. Environ Microbiol 12(1):118-123** [seen]. Using a single E. coli reference template, 16S diversity is "grossly overestimated" unless stringent quality filtering and low clustering thresholds (at most 97% identity) are used; homopolymer errors are reproducible and produce abundant spurious phylotypes. Matters: errors can be recurrent (not random), producing spurious "species" with frequency above one. Our analogue: a systematic matcher failure (e.g. rare features that never match) yields ghost clusters with multiple copies, not only singletons. Also: the single-reference-genome design is the model of a Phase 1 validation: a known-truth sample with known diversity.
3. **Di Cecco & Tancredi (2024). Estimating the number of sequencing errors in microbial diversity studies. Environ Ecol Stat 31:485-507, doi 10.1007/s10651-024-00614-w** [seen]. Treats spurious singletons as false-negative record-linkage errors; compares to deleting singletons. Total species estimate is equivalent between the two models; Shannon differs significantly. This is the same author (Tancredi) as the record linkage + N papers, closing the loop between our two literatures.
4. **"Species richness estimation with high diversity but spurious singletons" (arXiv 1604.02598)** (authors not retrieved) [seen as a title]. Related: breakaway_nof1 (omits f1), reported to outperform Chao1 when singletons are unreliable but less efficient when f1 is accurate [seen].
5. **ISME J 2024 (wrae106), "Nonparametric richness estimators Chao1 and ACE must not be used with amplicon sequence variant data"** (PMC11208923) (authors not retrieved) [seen]. The argument: denoising cannot distinguish true singletons from artifacts, so singleton-dependent estimators are unacceptable.
6. **Others [seen as titles]:** "Alpha diversity metrics for noisy OTUs" (bioRxiv 434977); "Differential richness inference for 16S rRNA marker gene surveys" (Genome Biol 2022); "A comprehensive review and evaluation of species richness estimation" (Briefings in Bioinformatics 26(2), bbaf158, 2025).
7. **Template for ghost singletons.** (a) Compute observed f1; (b) estimate f1 from f2, f3, f4 under Chiu-Chao; (c) compare and use the gap as a matching-quality diagnostic; (d) report Chao1 with adjusted f1 and an f1-free alternative; (e) validate by injecting ghosts into synthetic data with known truth. Check the assumption that error singletons are "extra" rather than "true singletons mis-split from doubletons": under a false non-match the loss is f2 -> 2*f1, so the Chiu-Chao estimate from f2-f4 will be biased because f2 is also depleted (my reasoning, not verified; test by simulation).

### 2.7 Recent methods (2021-2026) for few lists and dependence

1. **Das, Kennedy, Jewell. Doubly robust capture-recapture methods for estimating population size. arXiv 2104.14091 (2021, rev.); drpop R package (arXiv 2111.07191; CRAN)** [seen]. Assumes two lists are conditionally independent given covariates; gives the nonparametric efficiency bound, a doubly robust estimator, and a CI construction; simulations and a conflict-victims example. Also suggests bounds when lists are only nearly conditionally independent up to a deviation delta (less precise inference) [seen, secondary]. Matters: our covariates are item descriptors (activation frequency, norm, cluster), and nuisance models can be flexible; but conditional independence given descriptors is a strong assumption for runs sharing data and architecture. Use delta-sensitivity.
2. **Sun, Van Baelen, Plettinckx, Crawford. Dependence-robust confidence intervals for capture-recapture surveys. arXiv 2008.00127; J Surv Stat Methodol 11(5):1133 (2023)** [seen]. Partial identification: confidence sets for N under bounds on pairwise capture probabilities (test-inversion bootstrap and profile likelihood), simulations well calibrated, applied to people who inject drugs in Brussels, R package. Matters: the honest output when dependence is unknowable. Interval widens with the assumed dependence bound. Directly usable for the "bounds" deliverable.
3. **Neural Methods for Multiple Systems Estimation Models. arXiv 2601.05859 (January 2026, stat.AP)** [seen: abstract-level]. Neural Bayes estimators and neural posterior estimators, amortised so inference is fast after training; in simulations they match MCMC accuracy and avoid convergence failures on sparse data. Matters: amortised inference over simulated capture histories fits our simulation-first plan, and lets us train on exactly the synthetic distribution we use for validation. Risk: amortised estimators inherit the simulator's assumptions, which is the same non-transport problem. Authors not retrieved.
4. **Dennett & Bohning. Performance of capture-recapture population size estimators under covariate information. arXiv 2312.08391 (Dec 2023)** [seen: setup only]. Simulation of Horvitz-Thompson, generalised Chao and generalised Zelterman with covariates and variance estimation, plus outlier impact; follow-up in Metron/Springer, "Performance and robustness of single-source capture-recapture population size estimators with covariate information and potential one-inflation" (doi 10.1007/s40300-025-00300-2), a generalised modified Chao estimator for covariates and one-inflation [seen]. **One-inflation is exactly the ghost-singleton phenomenon**, so the modified Chao estimator is a candidate correction. Findings not seen.
5. **Other recent items [seen as titles/abstracts]:** Zult, van der Heijden, Bakker (generalised Chapman, arXiv 2311.01297, in B); "Population size estimation with many lists and heterogeneity: a conditional log-linear model among the unobserved" (arXiv 2407.03539); "Estimating the size of a closed population by modeling latent and observed heterogeneity" (arXiv 2106.03811); "Utilizing a Capture-Recapture Strategy to Accelerate Infectious Disease Surveillance" (arXiv 2307.00214); "Tailoring capture-recapture methods to estimate registry-based case counts based on error-prone diagnostic signals" (arXiv 2211.13842, PMC10766101), the closest published treatment of false-positive detections; "Two-step semiparametric empirical likelihood inference from capture-recapture data with missing covariates" (arXiv 2507.10404); "Probabilistic estimation of hidden migrant fatalities along the Central Mediterranean route" (arXiv 2603.19986). I found no clear 2024-2026 papers on dependence sensitivity beyond these; a targeted search for "sensitivity parameter" would be a future gap.

---

## 3. Lessons for our validation design (concrete)

1. **Validate first, with a known-truth testbed that deliberately violates assumptions.** The literature shows CRC failing on dependence, heterogeneity, sparse cells and matching error, and the estimates look fine in-sample. So our Phase 1 grid must cross: (heterogeneity: none / Beta / heavy low-probability tail) x (positive list dependence via shared seeds or data) x (K = 2, 3, 4, 6, 10) x (matching error f, g) x (N = 100, 1,000, 10,000). Mimic Wesson et al.'s layout (500 replicates per cell, known N).
2. **Use reference populations constructed from real data**, as Grimm et al. did with gecko field data: take a real SAE or a real red-team corpus, designate a large reference run set as "the population", subsample runs, and compare to the reference total. Keep the sampled and reference sets separate.
3. **Plant defects (seeded-defect design).** Software-inspection studies and our own plan agree: seed known features or attacks with controlled detectability (easy, medium, hard) and check recovery. Include an "invisible" class that no run can find, so truth exceeds the identifiable total, and report how far estimators fall short (they will, by design: they estimate only what is findable).
4. **Report the number of runs needed.** Software-inspection evidence says K < 4 gives no accurate model; Chao-type and jackknife estimators are the robust default under heterogeneity. Make K >= 4 (ideally 6+) the minimum for any claim, and show accuracy vs K curves.
5. **Treat model selection as part of the estimator.** Bootstrap the whole pipeline (matching, model selection, estimator), per Silverman et al. 2024; the Kosovo bootstrap shows an interval of [7,133, 18,681] vs the published [9,002, 12,122]. Also report "estimate vs model" tables (several models, as Wesson et al. recommend) instead of one chosen model. Do not use AIC alone: Zhang et al. show best-fit saturated model overestimates (8,053 vs 5,000).
6. **Report all pairwise and list-omission estimates.** Verona: the same truth gave 87.5% and 45.9% from different pairs. Include LP for every pair of runs, drop-one and merge-two trajectories (Binette & Steorts). Large spread across pairs flags dependence.
7. **Injection experiments for matching error with corrections.** Inject f and g into known-truth data, then compare (a) naive, (b) Di Consiglio & Tuoto-style linkage-error-corrected Petersen, (c) Dasylva et al. links-per-record correction, (d) Chiu-Chao-style adjusted f1, (e) multiple imputation over matchings. Metrics: bias, RMSE, interval coverage, and decision accuracy (does the estimate correctly say "more to find" vs "saturated").
8. **Replicate the Dutch TB lesson.** Add false-positive detections (spurious attacks or dead features that the judge accepts) as well as linkage error; the TB naive estimate was off by about 5x in the missing fraction (36.8% vs 7.3%). Our design should separately vary false-positive rate and linkage error, since both produced the inflation there.
9. **Estimate error rates from a labelled subset rather than from the capture data.** Supported by the clerical review step in the Census PES, by Vale/Fraysse in B, and by the weak independent performance of fastLink relative to authors' own benchmarks (FDP 0.73 vs 0.000). Budget for stratified labelling by score bin.
10. **Include a dependence-robust interval as the headline interval.** Use Sun et al. (2008.00127) bounds, or drpop's near-independence delta, alongside the usual CI; state the dependence bound assumed. If the interval becomes uninformative at plausible dependence, that is the finding. Also use an f1-free fallback (breakaway_nof1-style or Chao based on f2, f3) when ghost singletons are suspected.
11. **Adopt the Chiu-Chao diagnostic.** Always print f1_obs and f1_est (from f2-f4) next to Chao1; a large gap flags ghosts. Test on injected ghosts before trusting it, because false non-matches deplete f2 as well (see 2.6 item 7). Consider one-inflation models (Dennett & Bohning's modified Chao) as an additional comparator.
12. **Sparse-table safeguards.** Where cells are zero or sparse, switch to sample coverage or decomposable graphs (Wesson), Chan-Silverman-Vincent SparseMSE (B), or Bayesian latent class (LCMCR), and say that standard AIC log-linear selection is unsafe there.
13. **Stratify before estimating.** HRDAG and the Census both do it: stratify by feature frequency band, layer, attack family, or target behaviour. Evaluate whether stratified and pooled estimates agree; disagreement shows heterogeneity.
14. **Beware design choices that change the answer without changing the data** (Peru: decomposing by perpetrator and subtracting). Pre-register the stratification, matching threshold sweep, estimator list and decision rules before looking at results on real SAEs or real red-team data.
15. **Independent confirmation where possible.** Kosovo was credible because an independent census-style count arrived later. For us the analogue is a deliberately exhaustive "oracle" run (very wide SAE; exhaustive attack enumeration on a small target) held out for a final check on a smaller system.
16. **Use decision accuracy as a metric**, not only relative error: "relative decision accuracy" from the software-inspection literature, e.g. does the estimator correctly say whether another run is worth it?
17. **State the scope of N honestly.** CRC estimates the number of items findable by this family of procedures, not all possible items. Correlation bias (census) and shared blind spots mean a systematic underestimate that no matching fix can remove; report it as a lower bound with the dependence caveat.

---

## 4. Pitfalls specific to this round

- Several well-known validation papers (Tilling & Sterne, Papoz, Jarvis, Hook & Regal 1995/2000, Brenner 1995) were not retrievable beyond metadata. Their conclusions in section 2.1 are labelled as citing-paper statements, not read results.
- Many numbers come from secondary snippets (news copies of the Census release, HRDAG web pages, citing papers). Verify before quotation.
- "Kosovo validated" is a weak claim: counts differ in scope and period, and the CI was probably too narrow.
- The 2020 PES percentages come from news copies of the March 2022 report.
- The Di Cecco & Tancredi finding (total species is the same, Shannon differs) is for microbial data with a particular error model; it may not extend to heavy-tailed or highly structured SAE features.

## 5. Datasets, code and tools (links as seen)

- drpop (R): https://cran.r-project.org/web/packages/drpop/index.html ; arXiv 2111.07191.
- LCMCR (R): https://cran.r-project.org/web/packages/LCMCR/LCMCR.pdf
- SparseMSE and bootstrapped MSE: https://github.com/bernardsilverman/MultipleSystemsEstimation
- fastLink (R): https://github.com/kosukeimai/fastLink
- d-blink (Spark): arXiv 1909.06039; dga for MSE (from B).
- Chiu-Chao adjusted Chao1 R code via Anne Chao's site: https://sites.google.com/view/chao-lab-website/publication ; paper https://peerj.com/articles/1634/
- iNEXT issue on singleton correction: https://github.com/JohnsonHsieh/iNEXT/issues/57
- verdata (HRDAG Colombia, R; JOSS 2024) (title seen).
- HRDAG Kosovo report PDF: https://hrdag.org/wp-content/uploads/2013/06/kosovo-killings-refugeeflow-ICTY2002.pdf ; Manrique-Price-Gohdes working paper: https://hrdag.org/wp-content/uploads/2013/04/Manrique_Price_Gohdes_WorkingPaper.pdf
- Census 2020 PES documents: https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/2020-pes-estimation-design.pdf ; https://www2.census.gov/programs-surveys/decennial/coverage-measurement/pes/2020-source-and-accuracy-pes-estimates.pdf ; 2010 CCM person matching assessment (CPEX-242): https://www.census.gov/programs-surveys/decennial-census/decade/2010/program-management/cpex/2010-cpex-242.html
- Software-inspection CR evaluation: https://wohlin.eu/jss04-1.pdf (Petersson et al. review); Fraunhofer ISERN-97-22 tech report (Briand et al.).
- PatentsView ER evaluation: arXiv 2210.01230.

## 6. Search log (40 searches, all used)

Extended unless marked (std).
1. CRC vs known total (Tilling, Sterne, Papoz, Brenner).
2. van Hest TB record linkage and CRC.
3. Software inspection CRC seeded defects.
4. Hook & Regal 1995 limitations.
5. Peru 69,280 and Rendon critique.
6. LCMCR Manrique-Vallier 2016.
7. HRDAG Kosovo 10,356.
8. HRDAG Syria, Colombia, Guatemala.
9. Rendon "Capturing correctly" and responses.
10. (std) Colombia 450,664 and Guatemala.
11. 2020 PES DSE methodology.
12. (std) Census person matching clerical review.
13. (std) 2020 PES results.
14. fastLink Enamorado et al.
15. Steorts blink and microclustering.
16. Binette & Steorts (Almost) all of ER.
17. Tancredi, Steorts, Liseo 2020 results.
18. Chiu & Chao 2016.
19. Kunin et al. 2010.
20. Singleton-corrected estimators, EES 2024.
21. Chiu-Chao formula.
22. Doubly robust CRC (Das, Kennedy, Jewell).
23. Neural MSE 2601.05859.
24. 2008.00127 dependence-robust intervals.
25. EES 2024 sequencing errors (found Di Cecco & Tancredi).
26. Dennett & Bohning 2312.08391.
27. Validation: diabetes, Jarvis, Tilling & Sterne.
28. (std) Brenner 1995.
29. Hook & Regal 2000.
30. (std) Tilling 2001.
31. Grimm et al. 2014 PLOS ONE.
32. Briand et al. 2000.
33. Zhang et al. pitfalls of log-linear.
34. Di Consiglio & Tuoto linkage error.
35. HRDAG "MSE does it really work".
36. Few lists dependence sensitivity 2024-2025.
37. Dasylva 2403.11438, Racinskij 2003.13080.
38. Wesson 2022 model selection.
39. (std) 2020 PES correlation bias adjustment.
40. (std) Tilling & Sterne 1999.
