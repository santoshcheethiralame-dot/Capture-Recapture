# §2 Setting and estimands, §3 Method (draft v0, Santosh, 2026-10-23)

> Status: first draft for the preprint (M4). Statistics sections only.
> Every number cites its run ID; numbers from runs not yet reviewed by
> Kushal are marked †. Vocabulary per `docs/GLOSSARY.md`.

## 2 Setting and estimands

**Catchers, runs, failure modes.** A *catcher* is one configuration of a
safety discovery tool: an auditor agent with its tools, an attacker with
its prompt, or an SAE architecture with its training settings. A *run* is
one independent execution of a catcher. A run outputs findings. An
*identity rule* decides when two findings, from the same run or different
runs, describe the same *failure mode*. After K runs, the result is a
*detection history*: a binary matrix X with one row per failure mode found
and one column per run. Its sufficient statistics are the frequency counts
Q_k, the number of failure modes found in exactly k of the K runs, and the
total number of detections U = Σ_k k Q_k.

**Detectability.** Failure mode i has detectability π_i, the probability
that one run of the catcher finds it. The *catchable population* is the set
of failure modes with π_i > 0. Failure modes that no run of this tool can
find are outside it and invisible to every estimator in this paper. We say
so whenever we report a number.

**Audit coverage (headline).** The realized coverage of the K runs is

  C = Σ_{i found} π_i / Σ_i π_i,

the share of detectable failure mass already found. Equivalently, it is the
probability that a failure mode found by one more run is already known.
C is a property of *these* K runs, not a fixed parameter. It is what an
auditor wants to know before stopping: how likely the next run is to
surface something new. It is also estimable without assumptions about how
detectability is distributed. **New finds from more runs**, Δ(m), is the
expected number of failure modes that m further runs would add. It turns C
into the quantity a lab plans with.

**Why we do not report the number of failure modes.** Under uneven
detectability, the total number N of catchable failure modes is not
identifiable from incidence data. Any number of failure modes with π_i
arbitrarily close to 0 is consistent with the same expected frequency
counts (Link 2003; Mao and Lindsay 2007). Estimators of N, such as Chao2,
are therefore reported only as **lower bounds** and labelled as such. In
the E01 simulation, Chao2 is below N in most cells. Its interval covers N
in only part of the replicates, falling below 0.5 once N ≥ 500 at K ≤ 10
(E01-R001, R004†). Coverage is estimated with |bias| ≤ 0.009 (MCSE 0.003)
in all 14 cells where its assumptions hold (E01-R001, R002, R004†).

**Assumptions, and what breaks them.** Coverage estimation needs (i) runs
that are exchangeable given the failure modes, (ii) a correct identity rule,
and (iii) a catcher that does not adapt to its own earlier findings. Each
failure has a known direction, and each is an experiment here:
- *correlated catchers* (shared base model or data) make the audit look more
  complete than it is (E01 H1f: +0.20 in a one-family vs six-family
  comparison, E01-R002†; E08);
- *ghosts* (one failure mode counted as two) make it look less complete
  (E01 H1e: Ĉ −0.16 at a 15% ghost rate, E01-R003†; E04, E05);
- *adaptive search across runs* biases it in the direction of the
  adaptation: revisiting earlier finds makes the audit look more complete
  (E01 H1d: +0.07), steering towards new holes less complete (−0.15;
  E01-R002†; E10).

## 3 Method

**Coverage estimator.** We use the Chao-Jost (2012) incidence estimator,

  Ĉ = 1 − (Q₁/U) · (K−1)Q₁ / ((K−1)Q₁ + 2Q₂),

with iNEXT's convention when Q₂ = 0. Implementation conventions match iNEXT,
SpadeR, vegan, Rcapture and VGAM exactly (D-008), and are validated against
the R packages (E00-R001 to R004†).

**Interval for realized coverage.** The interval iNEXT reports,
Ĉ ± z·sd(Ĉ*), describes the sampling spread of Ĉ. It does not describe the
error Ĉ − C, because C itself varies from one set of runs to the next. At
nominal 95%, it covered the realized C in about 76% of simulated audits
(E01-R005†). We bootstrap the error directly:
1. Build the Chao pseudo-population from X (Chao et al. 2014; iNEXT).
   Detected failure modes get their observed rates y_i/K, shrunk toward 0.
   ⌈f̂₀⌉ undetected ones share the estimated undetected mass.
2. Draw B = 1000 bootstrap histories X* of K runs from it.
3. For each, record Ĉ* and the realized coverage C* = Σ_{found*} π̂ / Σ π̂.
   C* is known because the pseudo-population's detectabilities are known.
4. Report Ĉ ± z·sd(Ĉ* − C*), clipped to [0, 1], with the one-sided lower
   bound Ĉ − z₁·sd(Ĉ* − C*) for stopping rules.

On fresh simulated datasets, this interval covers the realized C in
0.90–0.95 of replicates across the clean cells (base 0.906, MCSE 0.013;
E01-R008†, exploratory, adopted as primary in D-010). The interval for Δ(m)
is built the same way: each bootstrap draw adds m further runs from the
pseudo-population, so the realized number of new finds is known.

**New finds.** Δ̂(m) = f̂₀ [1 − (1 − Q₁/(K f̂₀ + Q₁))^m] (Chao et al. 2014),
with f̂₀ the Chao2 estimate of undetected failure modes. Following Orlitsky,
Suresh and Wu (2016), we extrapolate only to m ≤ K.

**Lower bounds.** Chao2 (with its log-normal interval, Chao 1987),
improved Chao2 (Chiu et al. 2014), and the second-order jackknife and ICE as
sensitivity checks. Where detectability covariates are measured (SAE
firing frequency, judge-rated subtlety), we fit the Huggins (1989)
conditional likelihood with Horvitz-Thompson N̂ and its Huggins variance,
which matches VGAM's to 10⁻⁷ (E07).

**Identity rule and its diagnostics.** For SAE features, we match latents
across runs by one-to-one assignment on |decoder cosine| and take connected
components across all run pairs. The threshold is the midpoint of the
widest interval over which the number of failure modes changes by less than
5% (the plateau rule). If no plateau exists, we report that no trustworthy
threshold was found rather than picking one (E03). For red-team attacks and
audit findings, a judge labels findings against a rubric, followed by
embedding clustering (E10). Identity errors are corrected from a labelled
sample of candidate pairs (E05): a first-order correction of the frequency
counts for ghosts, and multiple imputation calibrated on the labels.

**Dependence diagnostics.** We report the effective number of runs
n_eff = K / (1 + (K−1) ρ̄) (Kish), with ρ̄ the mean pairwise correlation of
runs' detection indicators, and the ratio of observed to expected pairwise
overlap. Log-linear models with run interactions (Rcapture) are a
sensitivity analysis.

**De-adaptation.** For adaptive campaigns we apply Liyanage et al. (2024,
Algorithm 1) and the reset estimator of Liyanage et al. (2021), and convert
discovery rates to coverage via 1 − Ĉ = Û·t/U. In simulation, both
over-correct at audit scale (E01-R009†, exploratory). We therefore also
report a design-based analysis (D-012, proposed).

**Reporting recipe** (`docs/PROTOCOLS.md` §8). For every audit, report:
- K, S_obs, Q₁–Q₄ and the identity rule;
- Ĉ with its 95% interval (headline);
- Δ̂(K) and Δ̂(2K);
- Chao2 labelled "lower bound";
- jackknife-2 and ICE;
- n_eff/K and the overlap ratio;
- sensitivity to the identity threshold.

## Notes for revision
- Fig. 1 (concept) and the E01 figures (`analysis/e01/figures.py`, fig. 1
  is the planned paper Fig. 3 core) are ready to drop in.
- Cite primary sources only after re-reading them (arXiv is blocked here).
  Link 2003, Mao and Lindsay 2007, Chao-Jost 2012, Chao et al. 2014,
  Orlitsky et al. 2016 and Liyanage et al. 2021/2024 are in
  `research/README.md`.
- The † numbers become final once Kushal has reviewed E00/E01 (four-eyes).
