# Reading list

Priority order first, then everything by area. Each entry says why it
matters for this project. Status marks:
- **✓**: confirmed in search results (title, ID and main claim);
- **~**: seen, but numbers or details came from secondary sources;
- **?**: not confirmed.

Full details and numbers are in [`notes/`](notes/).

## Start here (read in this order)

| # | Paper | Why |
|---|---|---|
| 1 | Kansal, **"How Many Label Errors Are Left? Capture-Recapture for Counting the Benchmark Errors Nobody Found"**, GitHub `ParitKansal/label-error-capture-recapture`, Zenodo 10.5281/zenodo.23205993 (Oct 2026) ✓ | Closest prior work: the same method on a different target, with an honest negative result. Shows the failure mode to design around: a few detectors with thin overlap. |
| 2 | Kansal, **"How Many Failure Types Are Still Undiscovered?"**, GitHub `ParitKansal/undiscovered-failures`, Zenodo 10.5281/zenodo.23412807 (Oct 2026) ✓ | Pre-registered: the unseen share is estimable, the number of types is not. Its estimator suite is the baseline to beat. |
| 3 | Chanin and Garriga-Alonso, **SynthSAEBench**, [2602.14687](https://arxiv.org/abs/2602.14687) ✓ | The Phase 1 testbed. Its multi-seed SAE zoo lets the work start without training. |
| 4 | Paulo and Belrose, **SAEs Trained on the Same Data Learn Different Features**, [2501.16615](https://arxiv.org/abs/2501.16615) ✓ | The recapture rate (30 to 42%) and the matching protocol to copy. |
| 5 | Gerasimov et al., **Unstable Features, Reproducible Subspaces**, [2606.12138](https://arxiv.org/abs/2606.12138) ✓ | Per-feature capture probability; tells you which features are hard to catch. The scoop risk. |
| 6 | Ghosh et al., **Diminishing Returns of Data in SAEs**, [2610.20680](https://arxiv.org/abs/2610.20680) ✓ | Catchability depends on training budget (2% → 29%). |
| 7 | Chao and Colwell, **Thirty years of progeny from Chao's inequality**, SORT 2017 ~ | The best single entry point to the estimators. |
| 8 | Link, **Nonidentifiability of population size from capture-recapture data with heterogeneous detection probabilities**, Biometrics 2003 ✓ | Why total N is not estimable. |
| 9 | Chao and Jost, **Coverage-based rarefaction and extrapolation**, Ecology 2012; Chao et al., **Rarefaction and extrapolation with Hill numbers**, Ecol Monogr 2014 ✓ | The coverage and extrapolation quantities to report instead of N. |
| 10 | Böhme, **STADS: Software Testing as Species Discovery**, TOSEM 2018, [1803.02130](https://arxiv.org/abs/1803.02130) ✓ | The closest methodological template for red teams. |
| 11 | Böhme, Liyanage, Wüstholz, **Estimating Residual Risk in Greybox Fuzzing**, FSE 2021 ✓ | Adaptive bias: why adaptive red teams break the estimators. |
| 12 | Liyanage et al., **Extrapolating Coverage Rate in Greybox Fuzzing**, ICSE 2024 ✓ | A fix for adaptive bias that can be transferred. |
| 13 | Petersson, Thelin, Runeson, Wohlin, **Capture-recapture in software inspections after 10 years**, JSS 2004 ✓ | What happened the last time someone tried this: the lessons and why it was not adopted. |
| 14 | Sheshadri et al., **AuditBench**, [2602.22755](https://arxiv.org/abs/2602.22755) ✓ | The Phase 3 known-truth testbed. |
| 15 | Kim et al., **Correlated Errors in LLMs**, [2506.07962](https://arxiv.org/abs/2506.07962); Goel et al., **Great Models Think Alike**, [2502.04313](https://arxiv.org/abs/2502.04313) ✓ | How dependent LLM catchers are. |
| 16 | Chiu and Chao, **Estimating and comparing microbial diversity in the presence of sequencing errors**, PeerJ 2016 ✓ | How to correct for spurious singletons (our ghost matches). |
| 17 | Avestimehr, Duffy, Médard, **NOVA: Fundamental Limits of Knowledge Discovery Through AI**, [2605.15219](https://arxiv.org/abs/2605.15219) ✓ | The theoretical objection you will have to answer. |
| 18 | Johansson et al., **Identification errors in camera-trap studies result in systematic population overestimation**, Sci Rep 2020 ✓ | Real numbers for how matching error biases N. |
| 19 | Aleshin-Guendel, Sadinle, Wakefield, **The central role of the identifying assumption in population size estimation**, Biometrics 2024, [2101.09304](https://arxiv.org/abs/2101.09304) ✓ | The framing for "what is our identifying assumption". |
| 20 | Nasr et al., **Scalable Extraction of Training Data from (Production) Language Models**, [2311.17035](https://arxiv.org/abs/2311.17035) ~ | Good-Turing used in LLM security, and a warning about how many samples it needs. |

## Statistics: estimators, identifiability, coverage

- Chao (1987), *Estimating the population size for capture-recapture data with unequal catchability*, Biometrics 43:783 ✓ (the lower bound).
- Otis, Burnham, White, Anderson (1978), *Statistical inference from capture data on closed animal populations*, Wildlife Monographs 62 ✓ (M0/Mt/Mb/Mh models).
- Chiu, Wang, Walther, Chao (2014), *An improved nonparametric lower bound of species richness via a modified Good-Turing frequency formula*, Biometrics ✓ (iChao).
- Chao and Lee (1992), JASA (ACE/ICE) ✓; Chao, Lee, Jeng (1992) and Lee and Chao (1994), Biometrics (sample coverage for Mth) ~.
- Mao and Lindsay (2007), *Estimating the number of classes*, Ann Stat, [0708.2153](https://arxiv.org/abs/0708.2153) ✓ (only lower confidence limits are possible).
- Holzmann, Munk, Zucchini (2006), *On identifiability in capture-recapture models*, Biometrics ✓.
- Pledger (2000, 2005), finite-mixture models, Biometrics ✓; Dorazio and Royle (2003), Biometrics ✓.
- Haegeman et al. (2013), *Robust estimation of microbial diversity in theory and in practice*, ISME J, [1302.3753](https://arxiv.org/abs/1302.3753) ✓ (use Hill numbers, not richness).
- Orlitsky, Suresh, Wu (2016), *Optimal prediction of the number of unseen species*, PNAS, [1511.07428](https://arxiv.org/abs/1511.07428) ✓ (extrapolate only up to about log n).
- Valiant and Valiant, *Estimating the unseen*, NeurIPS 2013 / J ACM 2017 ✓.
- Eriksson (2026), *The unseen species problem revisited*, [2602.08769](https://arxiv.org/abs/2602.08769) ~ (prediction intervals, incidence data).
- Lee and Böhme (2025), *How much is unseen depends chiefly on information about the seen*, ICLR, [2402.05835](https://arxiv.org/abs/2402.05835) ✓.
- Vipulanandan, Premaratne, Sarkar (2026), *Rarity of singletons matters*, [2610.22604](https://arxiv.org/abs/2610.22604) ~ (unreliable singletons; very recent).
- Willis and Bunge (2015), *Estimating diversity via frequency ratios*, Biometrics ✓; Willis (2016), *Species richness estimation with high diversity but spurious singletons*, [1604.02598](https://arxiv.org/abs/1604.02598) ✓ (`breakaway_nof1`).
- Chao et al. (2015), *Unveiling the species-rank abundance distribution*, Ecology ✓.
- Huggins (1989) and Alho (1990), conditional likelihood with covariates ✓; Böhning (2013), *A generalization of Chao's estimator for covariate information*, Biometrics ✓.
- Dennett and Böhning, [2312.08391](https://arxiv.org/abs/2312.08391) ✓ (covariates and one-inflation).
- Das and Kennedy, *drpop*, [2111.07191](https://arxiv.org/abs/2111.07191); Das, Kennedy, Jewell, [2104.14091](https://arxiv.org/abs/2104.14091) ✓ (doubly robust estimation).
- Sun et al., *Dependence-robust confidence intervals for capture-recapture surveys*, [2008.00127](https://arxiv.org/abs/2008.00127) ✓.
- Fienberg, Johnson, Junker (1999), JRSS A ✓; Madigan and York (1997), Biometrika ✓ (`dga`).
- Manrique-Vallier (2016), *Bayesian population size estimation using Dirichlet process mixtures*, Biometrics ✓ (`LCMCR`); Aleshin-Guendel (2020), [2008.09865](https://arxiv.org/abs/2008.09865) ✓ (LCMCR identifiability).
- Chan, Silverman, Vincent (2021), *MSE for sparse capture data*, JASA, [1902.05156](https://arxiv.org/abs/1902.05156) ✓ (`SparseMSE`); Silverman, Chan, Vincent, [2303.17856](https://arxiv.org/abs/2303.17856) ✓ (bootstrapping over model selection).
- Chao, Tsay, Lin, Shau, Chao (2001), *The applications of capture-recapture models to epidemiological data*, Stat Med ✓.
- Grimm, Gruber, Henle (2014), PLoS ONE 9:e98840 ✓ (estimators tested against a known population).
- Schmitz and Rahmann (2025), *A comprehensive review and evaluation of species richness estimation*, Brief Bioinform ✓.
- Zult, van der Heijden, Bakker, [2311.01297](https://arxiv.org/abs/2311.01297) ✓ (generalised Chapman for small samples).

## Identity errors and record linkage

- Link, Yoshizaki, Bailey, Pollock (2010), *Uncovering a latent multinomial*, Biometrics ✓; Schofield and Bonner (2015), Biometrics ✓.
- Vale, Fewster et al. (2014), model Mt,α, Biometrics ✓; Fraysse et al., [2304.00885](https://arxiv.org/abs/2304.00885) ✓ (fails at low recapture).
- McClintock et al. (2013), *Integrated modeling of bilateral photo-identification data*, Ecology ✓; Bonner and Holmberg (2013), Biometrics, [1208.4285](https://arxiv.org/abs/1208.4285) ✓ (`multimark`; two partial "marks").
- Augustine et al. (2018), *Spatial capture-recapture with partial identity*, AoAS ✓.
- Ashe and Hammond (2022), matching uncertainty in photo-ID, Mammalian Biology ✓.
- Tancredi and Liseo (2011), AoAS ✓; Tancredi, Steorts, Liseo (2020), *A unified framework for de-duplication and population size estimation*, Bayesian Analysis ✓.
- Sadinle (2017), *Bayesian estimation of bipartite matchings*, JASA ✓.
- Di Consiglio and Tuoto (2015, 2018), linkage-error-corrected dual-system estimators, JOS ✓; Dasylva et al., [2403.11438](https://arxiv.org/abs/2403.11438) ✓.
- Binette and Steorts (2022), *(Almost) all of entity resolution*, Sci Adv, [2008.04443](https://arxiv.org/abs/2008.04443) ✓; *On the reliability of MSE for modern slavery*, JRSS A, [2112.01594](https://arxiv.org/abs/2112.01594) ✓.
- Enamorado, Fifield, Imai (2019), *fastLink*, APSR ✓ (independent evaluations report much worse error rates than the authors' own).
- Betancourt et al. (2016), *Flexible models for microclustering*, [1610.09780](https://arxiv.org/abs/1610.09780) ✓ (cluster size bounded by K).
- Kunin et al. (2010), *Wrinkles in the rare biosphere*, Environ Microbiol ✓; Di Cecco and Tancredi (2024), Environ Ecol Stat ✓; Deng et al. (2024), *Chao1 and ACE must not be used with ASV data*, ISME J ✓; Schloss and Handelsman (2005), *DOTUR* ✓.

## Validation evidence (where estimates met the truth)

- van Hest et al. (2007), Dutch tuberculosis record linkage and capture-recapture, Epidemiol Infect ✓ (36.8% → 7.3%).
- Verona diabetes capture-recapture, Diabetes Care 2000 ✓ (87.5% vs 45.9% from different list pairs).
- Zhang et al., *Pitfalls of the log-linear modeling framework*, [2306.10666](https://arxiv.org/abs/2306.10666) ✓.
- Wesson et al. (2022), model selection for capture-recapture, Ann Epidemiol ✓.
- Brenner (1995), Epidemiology ~; Hook and Regal (1995, 1997, 2000) ~.
- Ball et al. (2002), HRDAG Kosovo ✓; Manrique-Vallier (2019), Peru re-analysis, [1906.04763](https://arxiv.org/abs/1906.04763) ✓; Rendón (2019) critique and the Manrique-Vallier and Ball reply ✓.
- Briand, El Emam, Freimut, Laitenberger (2000), IEEE TSE ✓; El Emam and Laitenberger (2001) ✓; Runeson and Wohlin (1998), detection profile method ✓; Liu et al. (2015), adoption review ✓.

## Software, security and search precedents

- Eick et al. (1992), ICSE ✓; Vander Wiel and Votta (1993), IEEE TSE ✓.
- Liyanage et al. (2023), *Reachable coverage*, ICSE ✓ (false peaks); Liyanage et al. (2025), registered report, [2507.17093](https://arxiv.org/abs/2507.17093) ✓.
- Lee and Böhme (2026), *Dependency-aware residual risk analysis*, ICSE ~.
- Ablon and Bogart (2017), RAND *Zero days, thousands of nights* ✓; Herr, Schneier, Morris (2017), *Taking stock* ✓.
- Maillart et al. (2017), bug bounties, [1608.03445](https://arxiv.org/abs/1608.03445) ✓.
- Wang et al. (2018), *Crowdtesting: when is the party over?*, [1805.03218](https://arxiv.org/abs/1805.03218) ✓.
- Bron et al., Chao as a stopping rule in technology-assisted review, [2404.01176](https://arxiv.org/abs/2404.01176) ✓.
- Spring (2023), *How many undiscovered vulnerabilities remain*, [2304.09259](https://arxiv.org/abs/2304.09259) ✓.
- Mane, Srivastava, Hwang (2005), *Estimating missed actual positives using independent classifiers* ~.

## SAEs: consistency, matching, ground truth, theory

- Leask et al. (2025), *SAEs do not find canonical units*, [2502.04878](https://arxiv.org/abs/2502.04878) ✓.
- Song et al. (2025), *Feature consistency in SAEs* (PW-MCC), [2505.20254](https://arxiv.org/abs/2505.20254) ✓.
- Korznikov et al. (2026), *Sanity checks for SAEs*, [2602.14111](https://arxiv.org/abs/2602.14111) ✓.
- Chanin (2026), *Are SAE benchmarks reliable?*, [2605.18229](https://arxiv.org/abs/2605.18229) ✓ (code: `decoderesearch/saebench-reliability-audit`).
- Sharkey, Braun, Millidge (2022), *Taking features out of superposition* (LessWrong interim report) ✓; Anthropic Circuits Update, May 2023 ✓ (the "bounce" heuristic).
- Bricken et al. (2023), *Towards Monosemanticity* ~; Templeton et al. (2024), *Scaling Monosemanticity* ~; Gao et al. (2024), *Scaling and evaluating SAEs*, [2406.04093](https://arxiv.org/abs/2406.04093) ✓.
- Bussmann et al. (2025), *Matryoshka SAEs*, [2503.17547](https://arxiv.org/abs/2503.17547) ✓; Chanin et al., *A is for Absorption*, [2409.14507](https://arxiv.org/abs/2409.14507) ✓; *Feature Hedging*, [2505.11756](https://arxiv.org/abs/2505.11756) ✓.
- *Ensembling SAEs*, [2505.16077](https://arxiv.org/abs/2505.16077) ✓; *Stable and steerable SAEs*, [2603.04198](https://arxiv.org/abs/2603.04198) ~; *Ablating Archetypes*, [2606.02061](https://arxiv.org/abs/2606.02061) ~.
- Balagansky et al., *SAE Match*, [2410.07656](https://arxiv.org/abs/2410.07656) ✓; *Semantic optimal transport for SAE feature matching*, [2605.28567](https://arxiv.org/abs/2605.28567) ~; Lan et al., [2410.06981](https://arxiv.org/abs/2410.06981) ✓ (activation-correlation matching).
- Engels et al., *Decomposing the dark matter of SAEs*, [2410.14670](https://arxiv.org/abs/2410.14670) ✓.
- Michaud et al., *The quantization model of neural scaling*, [2303.13506](https://arxiv.org/abs/2303.13506) ✓; *Progressive coding for SAEs* (frequency spectra), [2505.00190](https://arxiv.org/abs/2505.00190) ~.
- Karvonen et al., *Board game models*, [2408.00113](https://arxiv.org/abs/2408.00113) ✓ (known-subpopulation testbed); Heap et al., *SAEs on random transformers*, [2501.17727](https://arxiv.org/abs/2501.17727) ✓ (null control).
- Cui et al., *On the limits of SAEs*, [2506.15963](https://arxiv.org/abs/2506.15963) ✓; Tang et al., *Piecewise biconvexity and spurious minima*, [2512.05534](https://arxiv.org/abs/2512.05534) ✓; *Toward identifiable SAEs*, [2605.31245](https://arxiv.org/abs/2605.31245) ~.

## Red teams, audits, control, reward hacking

- MonitoringBench, [2605.09684](https://arxiv.org/abs/2605.09684) ✓; Terekhov et al., *Adaptive attacks on trusted monitors*, [2510.09462](https://arxiv.org/abs/2510.09462) ✓.
- SLEIGHT-Bench, [2605.16626](https://arxiv.org/abs/2605.16626) ✓; BashArena, [2512.15688](https://arxiv.org/abs/2512.15688) ✓; LinuxArena, [2604.15384](https://arxiv.org/abs/2604.15384) ✓; SHADE-Arena, [2506.15740](https://arxiv.org/abs/2506.15740) ✓; Ctrl-Z, [2504.10374](https://arxiv.org/abs/2504.10374) ✓.
- Marks et al., *Auditing LMs for hidden objectives*, [2503.10965](https://arxiv.org/abs/2503.10965) ✓; Anthropic (2025), *Building and evaluating alignment auditing agents* ✓; Rosu et al., *Training alignment auditors via RL*, [2608.25460](https://arxiv.org/abs/2608.25460) ~; Petri and Bloom (Anthropic tools) ✓.
- Taylor et al., *Auditing games for sandbagging*, [2512.07810](https://arxiv.org/abs/2512.07810) ✓.
- Chen, Wen, Kirchner, *Automated researchers can mitigate well-characterized alignment failures*, [2608.28945](https://arxiv.org/abs/2608.28945) ✓; Anthropic, *Automated weak-to-strong researcher* (blog, 2026) ✓.
- BAITBENCH, [2608.30724](https://arxiv.org/abs/2608.30724) ~; *Reward hacking challenges oversight of autonomous research agents*, [2609.28614](https://arxiv.org/abs/2609.28614) ~; ImpossibleBench, [2510.20270](https://arxiv.org/abs/2510.20270) ✓; METR MALT (2025) ✓; *Natural emergent misalignment from reward hacking*, [2511.18397](https://arxiv.org/abs/2511.18397) ✓.
- WildTeaming, [2406.18510](https://arxiv.org/abs/2406.18510) ✓; Rainbow Teaming, [2402.16822](https://arxiv.org/abs/2402.16822) ✓; Beutel et al., [2412.18693](https://arxiv.org/abs/2412.18693) ✓; h4rm3l, [2408.04811](https://arxiv.org/abs/2408.04811) ✓; Best-of-N jailbreaking, [2412.03556](https://arxiv.org/abs/2412.03556) ✓.
- Public competitions:
  - Tensor Trust, [2311.01011](https://arxiv.org/abs/2311.01011) ✓ (has attacker IDs);
  - HackAPrompt, [2311.16119](https://arxiv.org/abs/2311.16119) ✓;
  - Gandalf the Red, [2501.07927](https://arxiv.org/abs/2501.07927) ~;
  - SaTML LLM CTF, [2406.07954](https://arxiv.org/abs/2406.07954) ✓;
  - Gray Swan agent competition, [2507.20526](https://arxiv.org/abs/2507.20526) ✓;
  - TDC 2023 insights, [2404.13660](https://arxiv.org/abs/2404.13660) ✓.
- Constitutional Classifiers, [2501.18837](https://arxiv.org/abs/2501.18837) ✓ (the zero-capture case).
- STING / *Helpful to a Fault*, [2602.16346](https://arxiv.org/abs/2602.16346) ✓; Kaur, *What AI red-team evaluations can and cannot prove*, [2607.21735](https://arxiv.org/abs/2607.21735) ✓; SCARCE, [2606.29623](https://arxiv.org/abs/2606.29623) ~.

## Dependence between LLM catchers, and identity via LLMs

- Kohli, *Nine judges, two effective votes*, [2605.29800](https://arxiv.org/abs/2605.29800) ✓.
- Jiang et al., *Artificial Hivemind*, [2510.22954](https://arxiv.org/abs/2510.22954) ✓; Kirk et al., *Effects of RLHF on diversity*, [2310.06452](https://arxiv.org/abs/2310.06452) ✓.
- Bommasani et al., *Picking on the same person*, [2211.13972](https://arxiv.org/abs/2211.13972) ✓; Kleinberg and Raghavan, *Algorithmic monoculture*, [2101.05853](https://arxiv.org/abs/2101.05853) ✓.
- Si, Yang, Hashimoto, *Can LLMs generate novel research ideas?*, [2409.04109](https://arxiv.org/abs/2409.04109) ✓.
- Clio, [2412.13678](https://arxiv.org/abs/2412.13678) ✓; TnT-LLM, [2403.12173](https://arxiv.org/abs/2403.12173) ✓; LLooM, [2404.12259](https://arxiv.org/abs/2404.12259) ✓; k-LLMmeans, [2502.09667](https://arxiv.org/abs/2502.09667) ✓; CAST stability, [2602.15861](https://arxiv.org/abs/2602.15861) ~.

## Unseen-species work on LLMs, and alternatives

- Mordido and Meinel, *Mark-Evaluate*, COLING 2020, [2010.04606](https://arxiv.org/abs/2010.04606) ✓.
- Kalai and Vempala, *Calibrated language models must hallucinate*, [2311.14648](https://arxiv.org/abs/2311.14648) ✓; Kalai et al., *Why language models hallucinate*, [2509.04664](https://arxiv.org/abs/2509.04664) ✓.
- KnowSum, [2506.02058](https://arxiv.org/abs/2506.02058) ✓; McCabe et al., *Semantic alphabet size*, [2509.14478](https://arxiv.org/abs/2509.14478) ✓; SHADE, [2604.19162](https://arxiv.org/abs/2604.19162) ✓; Blind-Spot Mass, [2604.05057](https://arxiv.org/abs/2604.05057) ✓.
- Jones et al., *Forecasting rare language model behaviors*, [2502.16797](https://arxiv.org/abs/2502.16797) ✓; Wu and Hilton, *Estimating the probabilities of rare outputs*, [2410.13211](https://arxiv.org/abs/2410.13211) ✓; Angell et al., *Estimating tail risks*, [2604.22167](https://arxiv.org/abs/2604.22167) ✓; Parulekar and Liu, [2607.18454](https://arxiv.org/abs/2607.18454) ~.
- Lakkaraju et al., *Identifying unknown unknowns in the open world*, [1610.09064](https://arxiv.org/abs/1610.09064) ✓; Kossen et al., *Active testing*, [2103.05331](https://arxiv.org/abs/2103.05331) ✓.

## Datasets and code

| Resource | Link | Use |
|---|---|---|
| SynthSAEBench world v1 / v2 | `huggingface.co/decoderesearch/synth-sae-bench-16k-v1`, `-v2` | Phase 1 ground truth |
| SynthSAEBench SAE zoo (5 architectures × 5 seeds × L0) | `huggingface.co/decoderesearch/synth-sae-bench-16k-v1-saes` | Phase 1a, no training |
| Full-width sweep (209 SAEs) | `huggingface.co/chanind-goodfire/synthsaebench-full-width-sweep` | Width = number of true features |
| Generator and experiments | `github.com/decoderesearch/SAELens`, `github.com/decoderesearch/synth-sae-bench-experiments` | New worlds and seeds |
| Null and oracle SAEs | `github.com/decoderesearch/saebench-reliability-audit` | Controls |
| Board-game SAEs | `github.com/adamkarvonen/SAE_BoardGameEval`; HF `adamkarvonen/chess_saes`, `othello_saes` | Known subpopulation |
| Gemma Scope / Gemma Scope 2 / Llama Scope | HF `google/gemma-scope*`, `OpenMOSS-Team/Llama-Scope` | Nested width ladders |
| AuditBench | [2602.22755](https://arxiv.org/abs/2602.22755) (official repo link to confirm) | Phase 3 known truth |
| Petri, Bloom | `github.com/safety-research/petri`, `github.com/safety-research/bloom` | Repeated audits |
| SLEIGHT-Bench | `huggingface.co/datasets/sleightbench/SLEIGHT-Bench` (gated) | Never-caught class |
| Tensor Trust | `github.com/HumanCompatibleAI/tensor-trust-data` | Attacker-level histories |
| WildJailbreak | `huggingface.co/datasets/allenai/wildjailbreak` | Threshold sensitivity |
| METR MALT | HF `metr-evals/malt-public` | Reward-hack labels |
| Kansal repos | `github.com/ParitKansal/undiscovered-failures`, `github.com/ParitKansal/label-error-capture-recapture` (MIT) | Baselines; MMLU-Redux detector outputs |
| KnowSum | `github.com/Raina-Xin/KnowSum` | Smoothed Good-Turing on LLM outputs |
| Böhme adaptive-bias artefacts | `github.com/Adaptive-Bias/fse21_paper270`; Zenodo 10.5281/zenodo.10416794 | De-adaptation |
| R packages | `Rcapture`, `iNEXT`, `SpadeR`, `breakaway`, `SPECIES`, `VGAM`, `dga`, `SparseMSE`, `LCMCR`, `drpop`, `multimark` | Estimators |
