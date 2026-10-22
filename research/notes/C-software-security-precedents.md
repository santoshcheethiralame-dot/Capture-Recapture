# C. Software inspections, fuzzing, vulnerability rediscovery, ML/LLM precedents

Date of research: 22 Oct 2026. Author: research agent C.

IMPORTANT LIMITATION. The shared WebSearch budget (200 calls per turn, shared by all agents) ran out after
about 20 of my searches. I therefore covered sub-themes 1 to 3 properly (inspections, fuzzing, vulnerability
rediscovery) but could NOT search sub-themes 4 to 6 (static-analyser overlap and mutation testing; ML/LLM
unseen-species work; LLM red-team forecasting). Section 2.G lists the ML/LLM papers from memory. They are
all marked `(unverified: not seen in a search result)` and the arXiv IDs must be checked before anyone cites them.
The search tool also returns summaries, not full text, so numbers below come from abstracts and secondary
descriptions unless I say otherwise. Where a number is secondhand I say so. Nothing here is invented, but treat
everything not in a direct quote of an abstract as "check the PDF".

---

## 1. Summary (headline takeaways)

1. Software inspection is the direct precedent, and its verdict is mixed: capture-recapture (CR) in inspections has been
   studied for more than 10 years (Eick 1992 to Petersson et al. 2004), and the consistent finding is that estimators
   **underestimate** the remaining defects, badly when there are few inspectors. Briand et al. (2000, TSE):
   with too few inspectors "no model is sufficiently accurate and underestimation may be substantial"; accuracy is
   "strongly affected by the number of inspectors". Secondhand (Wohlin, citing Briand 2000 and Miller 1999):
   at least 4 to 5 reviewers are needed for acceptable accuracy. For us: K=2 attackers or K=2 SAE seeds will not do;
   plan for K of at least 5, preferably 8 to 10.
2. The recommended estimator after all that work was the **Mh-Jackknife** (model with heterogeneous detection
   probability per defect), and Chao-type estimators (Mh-Chao, Mt-Chao) for two inspectors
   (El Emam and Laitenberger 2001, a Monte Carlo study). This is the same family that the project proposal already
   names. No model is uniformly best (Petersson and Wohlin 1999; Liu et al. 2015 systematic review: "no conclusive
   decisions on the best capture-recapture models and estimators").
3. Heterogeneity among defects (some defects are easy and found by every inspector) is the dominant source
   of bias. Estimators that assume equal catchability (Mt/M0, Lincoln-Petersen) underestimate. Mh-JK and Chao lower bounds
   are still biased low when many defects have near-zero detection probability. This matches the proposal's risk
   "unequal catchability".
4. Practice never adopted CR in inspections. Liu et al. (EASE 2015, 506 articles screened, 44 primary studies, 18
   estimators under 4 basic models) conclude the lack of industrial application "may be the major issue" while
   "the theory is quite well established". Reasons visible in the literature: (a) the independence
   assumption is violated by inspection meetings, so inspectors must record findings before the meeting; (b) the answer
   was not trustworthy enough to drive a decision (reinspect or not); (c) estimators need many reviewers, which is costly.
   Lesson: a "missed" estimate is only useful if it is reliable enough to trigger a decision. We must show calibrated
   error, not just a point estimate.
5. Validation in this literature was weak at first. Eick et al. (1992) had no artefact with a known defect count and asked
   inspectors whether the estimates looked plausible. Later work fixed this with (i) reinjected/seeded defects with known
   truth (Wohlin and Runeson, five C programs, eight reviewers), (ii) re-using real inspection data with a "gold
   standard" built from all inspectors pooled, and (iii) Monte Carlo simulation (El Emam and Laitenberger). Copy (i) and (iii),
   and be careful with (ii): pooled truth is itself a lower bound.
6. Fuzzing is the best recent precedent for **unseen estimation under adaptive sampling**. STADS (Böhme 2018) casts test
   inputs as samples and program behaviours as species, and uses Good-Turing (discovery probability = f1/n, where f1 = singletons)
   and Chao1 for species richness. Blackbox fuzzers satisfy the i.i.d. assumption; greybox fuzzers do not.
7. **Adaptive bias** (Böhme, Liyanage and Wüstholz, FSE 2021): in greybox fuzzing the probability of discovering a species
   *increases* over time because the fuzzer reinvests in inputs that found rare things. Estimators built for blackbox
   (non-adaptive) sampling "systematically and substantially under-estimate the true risk", and a engineer who stops when
   the estimate falls below a threshold "is vastly misled". The paper gives the first probabilistic analysis of adaptive bias and
   two new estimator classes. Their ICSE 2024 follow-up (Liyanage, Lee, Tantithamthavorn, Böhme) corrects for adaptive bias by
   simulating many *blackbox* campaigns from the collected greybox data and regressing, and gets up to an order of
   magnitude lower prediction error. This is exactly the problem adaptive red teams pose, and the correction idea (resample
   or replay to remove the adaptivity) can be borrowed.
8. Estimating **richness** (total number of species, i.e. reachable coverage) is far harder than estimating **discovery
   probability** (missing mass). Liyanage et al. (ICSE 2023): jackknife estimators had the smallest bias and variance, but every estimator
   produced "false peaks" (more coverage found after the predicted ceiling), and no clear asymptote could be identified
   for 31 of 32 programs in seven-day runs. Directly relevant: report the sample coverage (missing mass) as the primary
   output, and the total N as a secondary lower bound.
9. Two ongoing validation efforts in fuzzing show the right design: a synthetic-program generator with known reachability, plus a
   consistency check that needs no ground truth (vary the sampling-unit size; the estimate should not change). Liyanage,
   Attanayake, Luo, Gopinath (arXiv 2507.17093, ICSME'25 registered report) plus an NDSS Fuzzing Workshop 2026 paper. Both
   are registered reports, i.e. plans, with no published results visible to me. We can steal the "invariance under sampling-unit
   size" test: for us, vary what counts as one attacker query or one SAE.
10. Lee and Böhme (ICLR 2025 spotlight, arXiv 2402.05835): in expectation, the missing mass is determined by the frequencies
    f_k of classes seen exactly k times (plus an exponentially decaying error). They find estimators with MSE about 80% of
    Good-Turing's. For us: the singleton/doubleton counts f1, f2 are the sufficient statistics, so they should be the
    first thing every run reports.
11. Vulnerability rediscovery is the nearest security analogue, and it shows how **disputed** CR-style numbers are. RAND (Ablon and
    Bogart 2017, 207 zero-days, 2002 to 2016): 5.7% collision in a year, "about 40%" over 14 years. Herr, Schneier and Morris (2017, final
    version more than 4,300 vulnerabilities): rediscovery 13.9% to 21% within 60 to 120 days for Android, 12.6% (60 days) for Chrome, and
    "more than twice as often" as the previous 1 to 9% range. The two studies differ by an order of magnitude because they
    sample different populations (a private stockpile vs public bug trackers) and define "the same bug" differently. This is the
    identity-matching and population-definition problem of the proposal, seen in the wild.
12. Bug bounty data show **non-stationary** discovery: Maillart et al. (35 HackerOne programs) find the probability of finding a bug decays
    like 1/t^0.4 after launch and researchers move between programs. A closed-population CR estimator cannot be applied naively. Both
    time-heterogeneity (Mt) and researcher-heterogeneity (Mh) are present. Same for our red teams, whose strength depends on the model
    generation.
13. LLM-side precedents exist but I could not verify them (see 2.G): Good-Turing-based total memorisation estimate (Nasr et al. 2023),
    missing-mass based hallucination bound (Kalai and Vempala 2024), and extreme-value or power-law forecasting of rare behaviours
    (Jones et al. 2025; Wu and Hilton 2024; best-of-N jailbreaking). Those methods estimate *probability of a bad output under a
    sampling distribution*; CR estimates *number of distinct failure types given a set of independent searches*. They are
    complements, and a combined design (use CR to estimate the number of strategy classes, then Good-Turing to estimate the probability
    mass of unseen classes under a fixed attacker distribution) is the natural paper.
14. An unusual new theoretical result, Hernández-Suárez and Hernández-Cuevas (arXiv 2607.17061, July 2026): s/n (share of singletons) is a
    conservative upper bound on the chance a user hits an undiscovered defect, with no operational profile needed. A critical
    third-party review (Pith) says the bound holds only in expectation and Table 1 shows it understating nearly half the time. I
    could not verify this critique.

---

## 2. Papers

### 2.A Software inspections and CR in testing (the classical line)

**A1. Eick, Loader, Long, Votta, Vander Wiel (1992). "Estimating software fault content before coding." ICSE-14, pp. 59-65, Melbourne.**
- Found: first use of CR in software. Apply the idea to design/code review: count the faults that independent reviewers find in common and
  extrapolate to total. Validation was informal: with no artefact of known fault count, the authors asked inspectors whether the estimates seemed plausible
  (per a Fraunhofer review; secondhand). Source: http://www.mdavidlong.com/estimating_software_fault_content.pdf (found in search, not read).
- Why it matters: the founding precedent that the proposal already cites. Its weak validation is the gap we fill.
- Leaves open: no ground truth; assumption violations not quantified.

**A2. Vander Wiel and Votta (1993). "Assessing software designs using capture-recapture methods." IEEE TSE 19(11), 1045-1054, doi 10.1109/32.256852.**
- Found (secondhand, via Fraunhofer review, not the paper): compared the Mt model with a model allowing heterogeneous detection probabilities; the MLE for Mt
  generally underestimates.
- Why it matters: first clear statement that equal-catchability estimators are biased low in software. Same direction of bias we should expect.
- Leaves open: check original for numbers.

**A3. Briand, El Emam, Freimut, Laitenberger (2000). "A comprehensive evaluation of capture-recapture models for estimating software defect content." IEEE TSE 26(6), 518-540.**
- Found (from abstract snippets): real inspection data; effects of number of inspectors and number of true defects on accuracy. Models are "strongly affected by the
  number of inspectors". With too few inspectors "no model is sufficiently accurate and underestimation may be substantial". Recommended: the model that lets defects
  have different detection probabilities (Mh) with the jackknife estimator.
- Why it matters: the most comprehensive evaluation, and the source of the "needs 4 to 5 inspectors" rule of thumb. Gives the experimental factors to vary in our
  Phase 1: number of runs K, true population size N, and detection heterogeneity.
- Leaves open: I did not see numeric bias tables. Check PDF (ResearchGate 3188084).

**A4. El Emam and Laitenberger (2001). "Evaluating capture-recapture models with two inspectors." IEEE TSE 27(9), 851-864, doi 10.1109/32.950319.**
- Found: Monte Carlo simulation; relative error of estimates and accuracy of the reinspection decision. Conclusion: the best estimator for two inspectors lets
  inspectors differ in capability; a secondhand citation names Mt-Chao as best for two reviewers.
- Why it matters: shows the right *decision-oriented* metric (did the estimate lead to the correct "stop vs continue" call?), not only relative error. Also a model for our K=2
  special case (two independent red teams).
- Leaves open: numeric error figures not seen.

**A5. Petersson, Thelin, Runeson, Wohlin (2004). "Capture-recapture in software inspections after 10 years research: theory, evaluation and application." J. Systems and Software 72(2), 249-264, doi 10.1016/S0164-1212(03)00090-6. PDF: https://wohlin.eu/jss04-1.pdf**
- Found (abstract level): sorts literature into theory, evaluation, application. Most basic theory came from biostatistics; most SE work is evaluation; a majority of the evaluation studies end in
  recommending Mh-JK. Notes the assumption of independent reviewers means the fault search must happen *before* the inspection meeting.
- Why it matters: the review to cite for "this was done, here is what happened". It also lists open areas, which are ours to pick up (confidence intervals, dependence).
- Leaves open: I could not retrieve the body text, so the bias and inspector-count sections need reading from the PDF.

**A6. Wohlin and Runeson (1998) detection profile method (DPM); also Runeson and Wohlin, Empirical Software Engineering 3(4), 381-406, 1998, "An experimental evaluation of an experience-based capture-recapture method in software code inspections".**
- Found: DPM plots, for each number of reviewers k, how many defects were found by exactly k reviewers (that is, the f_k frequency profile), then fits an exponential
  curve to extrapolate the number found by zero reviewers. Experiment: five C programs with reinjected defects, eight reviewers. It did not do significantly better than the
  Mt maximum-likelihood estimator, and the authors could not prove a statistically significant difference.
  Also "Defect estimations from review data", ICSE 1998 (https://www.wohlin.eu/icse98-2.pdf; seen in results, not read).
- Why it matters: DPM is a frequency-count curve-fit, i.e. a cousin of Chao and of the Lee-Böhme f_k approach. A cheap model-free baseline that we can include. Also note the seeded-defect validation.
- Leaves open: no principled confidence interval.

**A7. Petersson and Wohlin (1999). "Evaluation of using capture-recapture methods in software review data." EASE 1999. PDF: https://www.wohlin.eu/ease99.pdf**
- Found (secondhand): no estimation method is generally superior; the best depends on the data set and the number of reviewers.
- Why it matters: expect the same. Our paper's contribution should be a *map* of when each estimator works, not a single winner.

**A8. Miller (1999) "Estimating the number of remaining defects after inspection." Software Testing, Verification and Reliability (unconfirmed citation).**
- I could not retrieve this paper. Reference lists cite a Strathclyde technical report EFOCS-32-98 with a similar title. Wohlin (secondhand) attributes the "at least four to five reviewers"
  advice to Briand 2000 and Miller 1999. Mark: `(unverified)`.

**A9. Liu, Rong, Zhang, Shan (2015). "The adoption of capture-recapture in software engineering: a systematic literature review." EASE 2015, doi 10.1145/2745802.2745816.**
- Found: 506 articles retrieved, 44 primary studies, 18 estimators under 4 basic models; no conclusive decision on best model/estimator; industrial application is the main gap.
- Why it matters: the answer to "why did practice not adopt it". Cite directly in related work.

**A10. "On the independence of software inspectors." J. Systems and Software (ScienceDirect S0164121201000759; authors and year unverified; one snippet says ISESE 2003).**
- Found: tests whether individual inspectors' results are statistically independent. Snippet notes CR "requires several assumptions, which may be impossible to achieve in a software
  engineering context."
- Why it matters: precedent for *testing the independence assumption empirically*. For LLM red teamers sharing a base model, independence is far worse.

**A11. "Estimating the number of undetected software errors via the correlated capture-recapture model" (ScienceDirect S0377221705005254; LSU repository infosys_pubs/66; authors unverified).**
- Found (snippet): a CR model that allows correlation between detectors; a later report says correlated approaches outperform independence-based traditional models.
- Why it matters: a candidate estimator for dependent runs. Check authors and details.

**A12. Scott and Wohlin (2008). "Capture-recapture in software unit testing: a case study." ESEM 2008, pp. 32-40. PDF: https://www.wohlin.eu/esem08-1.pdf**
- Found: CR applied to developers independently unit-testing the same unit; industrial case study plus open-source pre-study; reports extra cost of parallel testing. A later description (secondhand) says the study was small, 4 developers.
- Why it matters: CR applied to *testing* rather than inspection, i.e. closer to red teams. Cost of parallel independent runs is the obstacle, as for us.

**A13. Stringfellow et al. (2002). "Estimating the number of components with defects post-release that showed no defects in testing." STVR, doi 10.1002/stvr.235.**
- Found (title only in search): CR used to estimate components with post-release defects that testing had missed. This is exactly "what testing missed" and checks against post-release truth.
- Why it matters: a real-world validation against later-discovered defects (a natural "ground truth that arrives afterwards"). Details not retrieved.

**A14. Wang, Yang, Yu, Menzies, Wang (2018). "Crowdtesting: When is the party over?" arXiv 1805.03218.**
- Found: 218 tasks from a large Chinese crowdtesting platform; 8 closing-decision methods (bug trend, bug arrival model, capture-recapture). The best methods catch a median of 91% of bugs while saving 49% of cost.
  Among CR estimators, the most general Mth model performed best in crowdtesting, whereas in classical inspection Mh-JK, Mh-Chao and Mt-Chao led (secondhand, ResearchGate listing).
- Why it matters: a modern, large-N, many-testers setting with a cost-based decision metric, and a sign that the best model depends on the setting (many noisy testers with heterogeneity in both testers and bugs: Mth).
  Companion: arXiv 1805.02744 "Effective automated decision support for managing crowdtesting" (seen as a link only).

**A15. "Using Chao's estimator as a stopping criterion for technology-assisted review." arXiv 2404.01176 (title only seen; authors unverified).**
- Why it matters: Chao used as a stopping rule in a ML-adjacent screening task (find all relevant documents). The "stop when estimated missed fraction is small" decision framing carries directly over to "stop red-teaming".

**A16. Dependence-robust confidence intervals for capture-recapture surveys, arXiv 2008.00127 (generic statistics; authors unverified).**
- Why it matters: intervals that tolerate dependent lists, a direct tool for our violated-independence setting. A general sensitivity-analysis approach also appears in arXiv 2211.13842 (registry case counts, "anchor stream" design: force independence by drawing one random sample). The anchor-stream idea maps to "include one random/uniform attacker as an independent list".

### 2.B Fuzzing as species discovery

**B1. Böhme (2018). "STADS: Software testing as species discovery." ACM TOSEM. arXiv 1803.02130; https://mboehme.github.io/paper/TOSEM18.pdf**
- Found: test inputs are samples, program behaviours (for example AFL-identified paths) are species. Discovery probability estimated by f1/n (singletons over inputs). If no error is found it
  bounds the chance the next input exposes one. Evaluates the Chao1 richness estimator and a predictor by Shen. Offers confidence intervals. Suggests adaptive bias corrections based on discovery probability could be devised.
- Why it matters: the closest methodological template ("STADS for red teaming"). Map: attacker query = input; attack strategy class = species; singleton strategies = f1.
- Leaves open: adaptive sampling (addressed in B2).

**B2. Böhme, Liyanage, Wüstholz (2021). "Estimating residual risk in greybox fuzzing." ESEC/FSE 2021, pp. 230-241, doi 10.1145/3468264.3468570. PDF: https://mboehme.github.io/paper/FSE21.pdf. Artifact: https://github.com/Adaptive-Bias/fse21_paper270**
- Found: the central challenge is *adaptive bias*: the probability of discovering a specific error increases over time because the fuzzer's power schedule reacts to what it has found. Estimators for blackbox
  fuzzing "systematically and substantially under-estimate the true risk"; an engineer who stops when the estimate drops below a threshold "is vastly misled". The discovery probability (chance the next input
  raises coverage) is an "excellent upper bound". First probabilistic analysis of adaptive bias; two novel estimator classes. A secondary snippet says it compares Good-Turing with Laplace-style estimators (unconfirmed).
- Why it matters: the key paper for adaptive red teams. An adaptive attacker that learns from the monitor's refusals is exactly a greybox fuzzer with a feedback loop. Same direction of bias (underestimates risk).
- Leaves open: the exact estimator definitions (read the PDF); how to detect adaptivity from data alone.

**B3. Liyanage, Böhme, Tantithamthavorn, Lipp (2023). "Reachable coverage: estimating saturation in fuzzing." ICSE 2023, pp. 371-383, doi 10.1109/ICSE48619.2023.00042. PDF: https://mboehme.github.io/paper/ICSE23.Effectiveness.pdf**
- Found: statistical estimation of the number of code elements that a fuzzer can in principle reach; static analysis gives only an upper bound. Jackknife estimators had the smallest bias and variance; all estimators are asymptotically
  consistent; but when truth is unknown every estimator produced "false peaks"; no clear asymptote for 31 of 32 programs over seven days.
- Why it matters: this is the species-richness (total N) problem with real-world validation against later growth. The false-peak phenomenon is the failure mode to expect: a plateau in the discovery curve is not evidence of completeness.
- Leaves open: no ground truth (addressed in B6).

**B4. Liyanage, Lee, Tantithamthavorn, Böhme (2024). "Extrapolating coverage rate in greybox fuzzing." ICSE 2024, article 132, doi 10.1145/3597503.3639198. PDF: https://mboehme.github.io/paper/ICSE24.pdf. Artifacts: Zenodo 10.5281/zenodo.10416794 and 10.5281/zenodo.10575734**
- Found: reviews existing estimators for future coverage rate and proposes one that corrects adaptive bias: simulate many blackbox campaigns from the collected coverage data, estimate each one's coverage rate, then
  fit a simple regression to project the greybox campaign's rate. Fuzztastic benchmark: up to an order of magnitude lower prediction error; error at least an order of magnitude lower for 4 of 5 subjects; 35 to 77% average error reduction
  for time-to-target-coverage (the 35-77% figure is from a secondary source).
- Why it matters: gives a concrete recipe to de-adapt: replay or resample the discovered pool as if drawn non-adaptively and calibrate. For red teams, resample the attacker's attempts uniformly from its own transcript pool.

**B5. Lee and Böhme (2024/2025). "How much is unseen depends chiefly on information about the seen." arXiv 2402.05835, ICLR 2025 (spotlight).**
- Found: in expectation the missing mass is determined entirely by the numbers f_k of classes seen exactly k times, plus an exponentially decaying error. A search algorithm finds estimators with lower error than Good-Turing; MSE about 80% of Good-Turing's.
  (The proposal says 2023/2024; the correct venue year is ICLR 2025.)
- Why it matters: justifies reporting the frequency-of-frequencies table (f1, f2, f3, ...) for every tool run; it is a sufficient statistic for coverage. Also applicable to LLM-token or output distributions.
- Leaves open: assumes i.i.d. sampling, so no adaptivity.

**B6. Liyanage, Attanayake, Luo, Gopinath (2025). "Assessing reliability of statistical maximum coverage estimators in fuzzing." arXiv 2507.17093 (ICSME'25 registered report). Site: https://soft-eng.sydney.edu.au/assessing-reliability-of-statistical-maximum-coverage-estimators-in-fuzzing/**
- Found: a plan, not results. (1) Generate large synthetic programs with complex control flow and known reachability for ground truth. (2) For real programs, vary the sampling-unit size; in theory the estimate should be invariant, so any
  dependence signals unreliability. Test whether the singleton-doubleton equilibrium (f1 about f2) is a reliable stopping criterion.
- Why it matters: the best template for our validation: synthetic generator with known N plus an invariance check that needs no ground truth. A follow-up registered report is "Evaluating impact of coverage feedback on estimators for maximum reachability in fuzzing" (NDSS Fuzzing Workshop 2026, https://www.ndss-symposium.org/wp-content/uploads/fuzzing2026-10.pdf; seen as a link only). Check whether results have since appeared.

**B7. Baez, Olivas, Diamond, Frias, Noller, Tizpaz-Niari (2025). "Risk estimation in differential fuzzing via extreme value theory." arXiv 2511.02927.**
- Found: when a differential-fuzzing campaign finds no bug, model the largest observed output differences by an extreme-value (maximum) distribution and extrapolate. Compared with Markov, Chebyshev and Bayes-factor baselines on real Java libraries (side-channel leaks), EVT is better in 14.3% of cases and tied in 64.2%.
- Why it matters: an alternative to CR for *magnitude* rather than count of unseen failures. Modest win rate is a useful reality check: tail extrapolation is also hard to beat simple baselines.

**B8. Hernández-Suárez and Hernández-Cuevas (2026). "An upper bound on the probability that a user encounters an undiscovered defect." arXiv 2607.17061 (stat.AP, 19 July 2026).**
- Found: each beta-test report is a draw and each distinct defect a class; s/n is a conservative bound on user-encounter risk of an undiscovered defect, exact MLE for the unseen mass under an urn construction; no operational profile needed; validated on synthetic populations with known truth.
  Pith's third-party critique (unverified): holds only in expectation; the paper's Table 1 shows understatement nearly half the time; needs encounter-level telemetry.
- Why it matters: very recent, very close in spirit, and validated on synthetic ground truth. Check the Table 1 criticism before citing the claim.

**B9. Other fuzzing items seen only as links (unread).**
- Böhme, "Assurances in software testing: a roadmap", arXiv 1807.10255: frames residual risk and a Good-Turing bound when no error is found.
- Böhme, "Boosting fuzzer efficiency: an information theoretic perspective", FSE 2020: https://mboehme.github.io/paper/FSE20.Entropy.pdf (entropy as the fuzzer's progress measure).
- "SoK: prudent evaluation practices for fuzzing", arXiv 2405.10220: evaluation pitfalls (seeds, repeated trials, ground truth); useful checklist for our own methodology.
- "Green fuzzing: a saturation-based stopping criterion using vulnerability prediction", ISSTA 2023, doi 10.1145/3597926.3598043.
- "Large-scale empirical analysis of continuous fuzzing: insights from 1 million fuzzing sessions", arXiv 2510.16433: a large real corpus that could give real saturation curves.

### 2.C Vulnerability rediscovery and bug bounties

**C1. Ablon and Bogart (2017). "Zero days, thousands of nights: the life and times of zero-day vulnerabilities and their exploits." RAND RR-1751. https://www.rand.org/pubs/research_reports/RR1751.html**
- Found: 207 zero-days (2002 to 2016) from a private exploit-vendor dataset. Average 6.9 years from private discovery to public disclosure (quartiles about 1.5 and 9.5 years). Collision rate: 5.7% of a stockpile is found by someone else within a year;
  secondary reports quote about 40% over the whole 14 years (The Intercept) and that almost 40% of the vulnerabilities were still publicly unknown. Median 22 days to develop a working exploit.
  (Secondary sources, not the report; I did not confirm "30 days".)
- Why it matters: the red-team analogue is "how often does another independent red team find the same attack?" That is a Lincoln-Petersen two-list design with time as a covariate. Also shows the answer depends on the observation window, a requirement for us to state an explicit window or budget.
- Leaves open: single vendor sample, no model for heterogeneity.

**C2. Herr, Schneier, Morris (2017). "Taking stock: estimating vulnerability rediscovery." Belfer Center. https://www.belfercenter.org/publication/taking-stock-estimating-vulnerability-rediscovery**
- Found: final version has more than 4,300 vulnerabilities (an earlier SSRN draft had about 2,600 and reported 12.7% aggregate). Android: 13.9% rediscovered within 60 days, 20% within 90, above 21% within 120. Chrome: 12.57% at 60 days; aggregate topped out at 19.6% in 2016.
  More than 60% of rediscovery happened in the first month. Claims rediscovery is more than twice the 1 to 9% range of earlier work; contrasts with RAND's 5.76% per year. Extrapolates that rediscovery could be up to one third of zero-days seen in use each year.
- Why it matters: shows how much an estimate moves with data choice and with the matching rule; two reputable teams disagree by about 2 to 4x. Rediscovery rate is itself an estimator of coverage: if p is the probability that another team re-finds an item, then the coverage of one team's list is roughly p. The paper treats the problem as rediscovery *rate*, not population *size*; converting to N requires the Lincoln-Petersen step that they do not take.

**C3. Ozment (2005). "The likelihood of vulnerability rediscovery and the social utility of vulnerability hunting." WEIS 2005; Ozment (2007) "Improving vulnerability discovery models." QoP 2007, doi 10.1145/1314257.1314261; Ozment PhD thesis, Cambridge 2007, http://andyozment.com/papers/ozment_dissertation.pdf.**
- Found (from abstracts and secondary reports): used OpenBSD 2.2 vulnerability ages with a better data collection process; models indicate the pool of vulnerabilities is being depleted; thesis reports strong anecdotal evidence of independent rediscovery and Microsoft bulletin data on rediscovery frequency (a later paper summarises "rediscovery is not negligible and should be explicitly considered"). I could NOT confirm that Ozment used capture-recapture by name; the search found no such text.
- Why it matters: shows the debate of depletion vs. rediscovery: if rediscovery is common, the pool is small and the list is near-complete; if rare, the pool is large. That is precisely the inference CR makes.

**C4. Geer (2015). "For good measure: the undiscovered." ;login: 40(2), April 2015. (Link seen: https://books.hdyar.com/ForGoodMeasure-TheUndiscovered-SoftwareVulnerabilities.geer.1504.pdf; contents not read.)**
- Appears to discuss estimating undiscovered software vulnerabilities (likely via overlap between finders). I could not read it; mark `(unverified)`.

**C5. Finifter, Akhawe, Wagner (2013). "An empirical study of vulnerability rewards programs." USENIX Security 2013, pp. 273-288.**
- Found: Chrome's VRP cost about $580,000 over three years with 501 bounties; Firefox about $570,000 with 190 bounties; VRP contributions were about 28% of Chrome's and 24% of Firefox's patched vulnerabilities; programs judged cost-effective vs. hiring full-time researchers.
- Why it matters: no rediscovery estimator, but it gives per-researcher contributions that could be used as a multi-list (K researchers) capture history. Use the data, not the conclusions.

**C6. Maillart, Zhao, Grossklags, Chuang (2017). "Given enough eyeballs, all bugs are shallow? Revisiting Eric Raymond with bug bounty programs." J. Cybersecurity 3(2), 81-90; arXiv 1608.03445.**
- Found: 35 public HackerOne programs. Probability of finding a bug decays about 1/t^0.4 after launch while later bugs pay more; new programs draw researchers away from older ones. Duplicate-submission findings were not clear from what I saw.
- Why it matters: a closed-population assumption fails over time (discovery effort and attacker skill drift). Include a time-stratified analysis or a Mt model; also a cautionary tale for "n red teams over weeks" if attackers improve.

**C7. "The benefits of vulnerability discovery and bug bounty programs: case studies of Chromium and Firefox." WWW 2023, doi 10.1145/3543507.3583352; arXiv 2301.12092.**
- Found (snippet): defines a duplicate as a later report of an already-known issue and treats duplicates from different hunters as independent rediscoveries.
- Why it matters: a publicly available duplicate-labelled corpus, a candidate dataset for a CR test with "later truth".

**C8. Industry duplicate figures (weak sources).** Intigriti reports about 3% of a program's reported vulnerabilities were previously addressed but resurfaced; their triage note says duplicates signal higher discoverability. Vendor blogs, not research. Mention only as colour.

**C9. Not in my searches but relevant, only seen as titles: "Timelines for in-code discovery of zero-day vulnerabilities and supply-chain attacks" (arXiv 1808.10062).** Unread.

### 2.D Static analysers, mutation testing (NOT COVERED)
My three searches on (a) CR with multiple static analysers, (b) estimating equivalent/unkillable mutants, (c) "estimate total bugs from tool overlap" were blocked by the search budget. From memory only, flagged `(unverified)`:
- Several benchmark papers compare the overlap of bugs found by different static analysers (for example on the Juliet suite and Defects4J-style data) and sometimes note that the union is a lower bound; I know of no CR application there. Needs searching.
- Equivalent mutants are usually handled by detection heuristics (trivial compiler equivalence, Offutt and Pan 1997) or prediction; a statistical richness estimate for unkillable mutants is not something I can confirm exists. Needs searching.

### 2.E Cross-field items found incidentally
- Dan Geer and others suggest vulnerability "stock" estimates; see C4.
- Systematic practice from epidemiology: arXiv 2008.00127 and 2211.13842 (see A16) for dependence.

### 2.F How these relate to adaptive red teams (analysis)
- Inspection CR: inspectors are independent but heterogeneous; the real violation is meeting contamination.
- Fuzzing STADS: single adaptive sampler; i.i.d. violated; Böhme's correction handles *within-run* adaptation.
- Red teams: both. Several attackers, each adaptive, sharing the same base model (positively correlated, which makes overlap too high and total N underestimated, like inspector dependence), and each adapting to feedback (adaptive bias, which also makes the discovery probability rise and the estimate of risk too low). Both biases push the same direction: **we will understate what was missed**. So all point estimates should be read as lower bounds, and the validation must quantify how far below.

### 2.G ML / LLM precedents (FROM MEMORY; none seen in a search result this session)
All entries `(unverified: not seen in a search result)`. IDs from memory; check before use.
- Lakkaraju, Kamar, Caruana, Horvitz (2017). "Identifying unknown unknowns in the open world: representations and policies for guided exploration." AAAI 2017. Finds model errors made with high confidence, with a bandit search over a partition of the input space. Complement: it searches for unknown unknowns instead of estimating how many.
- Nasr et al. (2023). "Scalable extraction of training data from (production) language models." arXiv 2311.17035 (ID from memory). Used a Good-Turing estimator to lower-bound total memorisation from the extracted set. The closest published use of species estimation in LLM safety.
- Kalai and Vempala (2024). "Calibrated language models must hallucinate." STOC 2024, arXiv 2311.14648 (ID from memory). Hallucination rate of calibrated model lower-bounded by the missing mass of facts seen once (Good-Turing).
- Si, Yang, Hashimoto (2024). "Can LLMs generate novel research ideas?" arXiv 2409.04109 (ID from memory). Reports that LLM-generated idea sets show heavy duplication, with only a small fraction non-duplicate out of thousands of generations. That is species richness saturation in an LLM sample; useful as a motivating example and as a testbed (a "ground truth" is unavailable, but saturation curves are).
- Jones et al. (2025). "Forecasting rare language model behaviors." arXiv 2502.16797 (ID from memory). Predicts the probability of rare behaviours at large query counts from elicitation probabilities at small query counts (power-law/extreme-value style). Competes with CR for the question "how likely is the worst case under N queries", but does not count distinct failure types.
- Wu and Hilton (2024). "Estimating the probabilities of rare outputs in language models." arXiv 2410.13211 (ID from memory). Importance sampling and activation extrapolation for rare outputs. Per-output probability, not number of types.
- Hughes et al. (2024). "Best-of-N jailbreaking." arXiv 2412.03556 (ID from memory). Attack success follows a power law in the number of samples; useful as a model for the attacker's discovery curve, and a reason for treating "number of samples" as the sampling effort variable.
Gaps to fill with the next search budget: capture-recapture for label errors or benchmark errors; independent-classifier estimates of missed positives; Good-Turing for LLM output diversity; any 2025/2026 paper that combines CR with LLM red-teaming or auditing. I found no evidence either way for these.

---

## 3. Leads, inspirations and experiment ideas

1. **STADS for red teaming (Phase 3 core).** Each attacker query is a sample; each attack strategy class (fixed rubric or embedding cluster) is a species. Report: f1, f2, Good-Turing coverage 1 - f1/n, Chao1 lower bound for richness, Chiu et al. coverage-based extrapolation (and jackknife), and a "singleton-doubleton equilibrium" stopping flag (from B6). Plant M known strategies in a toy monitor (for example M=40 injected prompt-injection templates of known detectability) and run K=5 to 10 attackers; compare to truth.
2. **Adaptive versus non-adaptive attackers on the same planted set (the key new experiment).** Arm A: attacker samples without feedback (i.i.d. prompts); Arm B: attacker sees monitor verdicts and adapts (a greybox-fuzzer analogue); Arm C: Arm B with the B4-style de-adaption (resample from the attacker's own transcript pool uniformly). Prediction from Böhme et al.: estimators calibrated on A will underestimate unseen mass on B; C should recover most of it. This is a direct test of whether fuzzing's fix transfers.
3. **Copy the inspection design for K.** Vary K from 2 to 10 and N, and plot bias against K as in Briand et al. Expect K of at most 3 to be badly biased low. Add the decision metric of El Emam and Laitenberger: probability of correctly calling "keep searching vs. stop" at a fixed threshold.
4. **Invariance test without ground truth (from B6).** For real SAEs or real red teams, change the unit of sampling (for example, 1 query vs. batches of 10; SAE width 16k vs. 65k pooled in different ways; matching threshold 0.7 vs. 0.9) and check the estimate does not drift. A drifting estimate flags unreliability even when truth is unknown.
5. **Singleton/doubleton diagnostics.** Make f1/f2 the headline: if f1 >> f2 the unseen mass is large. Report Lee-Böhme style estimators as a robustness check against Good-Turing (their MSE was about 80% of Good-Turing's).
6. **Later truth as a natural experiment.** Use post-release discovery as ground truth: Stringfellow (2002) did this for software; Chromium/Firefox bug trackers (C7) allow the same for security. For AI: red-team a model version, then use attacks found later against that same version (public jailbreak collections, bug-bounty reports) as held-out truth. Estimate the unseen count from the early red-team round and check whether the later-found set is consistent with it.
7. **Rediscovery as a cheap metric.** RAND and Herr et al. measure collision rate between independent finders. For red teams, report the pairwise collision rate (share of one team's strategies re-found by another within budget) with a clear definition of "same" and time window. Run the matching-rule sensitivity as in the proposal, since Herr et al. vs. RAND differ 2 to 4x because of matching and population definition.
8. **Anchor-stream independence trick** (from arXiv 2211.13842): add one non-adaptive, uniformly random attacker as a control list; it is independent of all the smart attackers by construction, so Lincoln-Petersen between "smart" and "random" lists estimates the share of the population that a smart search finds, at the cost of low overlap.
9. **Correlated and heterogeneous models.** Try the correlated CR model (A11) and log-linear models with interaction terms between attacker families (same base model = correlated); compare with Mh-Chao. Report which one has smaller bias under planted correlation.
10. **Time-stratified analysis.** Following Maillart (power-law decay 1/t^0.4), split attempts into early and late halves and test for decay in new-species rate; if the rate decays more slowly than Good-Turing predicts, adaptivity is present.
11. **Complementary LLM estimators.** Pair CR (number of strategy types) with Jones-style forecasting (probability of worst case over N queries) and BoN power law. A single table: for each tool, report (a) missing mass, (b) richness lower bound, (c) forecasted worst-case success at 10x budget. Needs the unverified ML papers to be checked first.
12. **Mutation-testing and static-analyser angle.** When search budget returns, check whether anyone applied CR to tool-overlap. If not, that is a gap and a cheap extension: use K existing static analysers as K lists on a benchmark with seeded bugs.

## 4. Pitfalls and warnings

- **Underestimation is the default.** Inspection literature (Vander Wiel and Votta; Briand; Wohlin) and fuzzing (Böhme 2021) both find estimates biased low, from heterogeneity, dependence and adaptivity. Expect to report lower bounds, and quantify the gap.
- **Few runs.** K=2 or 3 gives huge variance and bias; 4 to 5 is the stated minimum for inspections; more is better.
- **Dependence among attackers.** Inspection researchers worried about meeting contamination; LLM attackers share training data, base model, prompts and the monitor's feedback, so positive correlation is likely stronger than anything in inspections.
- **Adaptive sampling.** Standard Good-Turing and Chao assume non-adaptive sampling. Adaptive attackers reinvest in what works; the risk of unseen items rises over time, not falls (B2).
- **False plateaus.** Jackknife and Chao saw "false peaks" in 31 of 32 fuzzing targets (B3). A flat discovery curve may come from the attacker's limited strategy space, not from an exhausted population (the unreachable-by-this-attacker problem). CR estimates only the population that these attackers *could* find, not the population that exists. State this estimand explicitly ("catchable population").
- **Identity matching.** Herr et al. vs. RAND (about 2 to 4x apart) show how matching rules and population choice dominate. Report sensitivity to the matching threshold.
- **Richness is harder than coverage.** Prefer sample coverage / missing mass as headline; total N is only a lower bound.
- **Weak validation can mislead.** Eick (1992) validated by asking inspectors whether estimates looked plausible; pooled-team truth underestimates the true N. Use planted truth.
- **Registered reports are not results.** 2507.17093 and the NDSS 2026 paper are plans; do not cite them as findings.
- **Practice adoption.** Even valid estimators were not adopted if the interval was too wide to support a decision; provide a decision rule and calibrated intervals (Thelin and Runeson 2002 on CR confidence intervals was seen in a snippet but not read).
- **Claim hygiene.** B8 (2607.17061) has a contested central claim; ICLR year for B5 is 2025 not 2024; Ozment is not confirmed to use CR; "30 days" and "40% in a year" were NOT confirmed for RAND; the 40% figure is for 14 years or for still-unknown.

## 5. Datasets, code and tools

- Böhme FSE21 artifact (adaptive-bias estimators): https://github.com/Adaptive-Bias/fse21_paper270
- ICSE 2024 artifacts: Zenodo 10.5281/zenodo.10416794 (code), 10.5281/zenodo.10575734 (data and analysis scripts). Fuzztastic benchmark referenced there.
- Böhme's papers (PDF): https://mboehme.github.io/paper/TOSEM18.pdf, FSE21.pdf, ICSE23.Effectiveness.pdf, ICSE24.pdf, FSE20.Entropy.pdf.
- Wohlin group PDFs: https://wohlin.eu/jss04-1.pdf (review), https://www.wohlin.eu/icse98-2.pdf (DPM / defect estimation), https://www.wohlin.eu/ease99.pdf, https://www.wohlin.eu/esem08-1.pdf, https://wohlin.eu/issre01.pdf.
- Ozment dissertation: http://andyozment.com/papers/ozment_dissertation.pdf
- RAND data summary and slides: https://www.rand.org/pubs/research_reports/RR1751.html; Black Hat 2017 slides at blackhat.com (Ablon and Herr talks "Bug collisions meet government vulnerability disclosure").
- Herr et al. PDF: Black Hat link under blackhat.com/docs/us-17/thursday/ (Taking Stock) and SSRN 2928758.
- Maillart et al. data: HackerOne public programs (arXiv 1608.03445).
- Chromium/Firefox issue tracker duplicates study: arXiv 2301.12092.
- Software: R package Rcapture (log-linear and closed-population models), R package SPECIES / iNEXT for Chao and coverage-based extrapolation; python `scikit-bio` has Chao1; (from memory, `(unverified)`). Estimators are a few dozen lines anyway.
- Large continuous fuzzing corpus: arXiv 2510.16433 (1M sessions) for real saturation curves.

## 6. Search log (about 20 searches; budget then exhausted)

1. Petersson et al. 2004 review (extended) - got abstract-level summary only.
2. Briand et al. 2000 comprehensive evaluation (extended) - inspector-count and Mh-JK recommendation.
3. Böhme STADS TOSEM 2018 (extended).
4. arXiv 2607.17061 fetch (failed, DNS) then search - authors, claim, Pith critique.
5. Böhme/Liyanage/Wüstholz FSE 2021 residual risk - adaptive bias, artifact link.
6. Lee and Böhme "How much is unseen..." - ICLR 2025, 80% MSE.
7. Liyanage ICSE 2023 reachable coverage - jackknife, false peaks, 31 of 32.
8. "Extrapolating coverage rate" ICSE 2024.
9. Fuzzing species richness 2025 follow-ups - found 2507.17093, 2511.02927.
10. Risk estimation in differential fuzzing EVT.
11. "Assessing reliability of statistical maximum coverage estimators" 2507.17093.
12. RAND Ablon and Bogart.
13. Herr, Schneier, Morris.
14. Ozment WEIS 2005 and thesis.
15. Finifter et al. 2013.
16. Maillart et al. bug bounty.
17. Bug bounty duplicates and CR (no CR application found).
18. Eick 1992 and Vander Wiel and Votta 1993.
19. Runeson and Wohlin detection profile method.
20. Miller 1999 (paper itself not found).
21. El Emam and Laitenberger 2001.
22. Why CR not adopted in practice.
23. Crowdtesting "When is the party over?".
24. Liu et al. 2015 adoption SLR.
25. Independence-driven data selection (title not found).
26. Scott and Wohlin ESEM 2008 unit testing.
BLOCKED by budget (not run): Geer "The undiscovered"; static-analyser overlap and CR; equivalent-mutant estimation; Chao stopping criterion in TAR (2404.01176) details; all LLM/ML items (Lakkaraju; Nasr; Kalai and Vempala; Si et al.; Jones et al.; Wu and Hilton; best-of-N jailbreaking); CR for label errors/benchmark errors; Good-Turing for LLM output diversity; 2025-2026 CR + LLM red-teaming. These need a follow-up round.
