# Glossary

The paper uses safety vocabulary. The statistics literature uses ecology
vocabulary. This table maps one to the other so code, notebook and paper
stay consistent.

| Paper term (use this) | Statistics / ecology term | Meaning here |
|---|---|---|
| **failure mode**, **item** | individual, animal, species | One distinct thing a tool can find: a hidden behaviour, an attack strategy (blind spot), an SAE feature. |
| **catcher** | trapping method, list source | One configuration of a discovery tool (auditor agent + tools; attacker + prompt; SAE architecture + settings). |
| **run** | capture occasion, sample, list | One independent execution of a catcher. |
| **found / caught** | captured, detected | The run's findings include the item (by the identity rule). |
| **detectability** π_i | catchability, capture probability | Probability that one run finds item i. |
| **uneven detectability** | individual heterogeneity (model Mh) | Some failure modes are much easier to find than others. |
| **detection history** | capture history, incidence matrix | Item × run matrix of found / not found. |
| **singletons, doubletons** f1, f2 | frequency counts | Items found in exactly 1 (2) runs. The f_k are the sufficient statistics for coverage. |
| **audit coverage** C | sample coverage (Chao-Jost incidence) | Share of detectable failure mass already found; the probability that what a new run finds is already known. **Headline quantity.** |
| **new finds from more runs** Δ(m) | rarefaction / extrapolation (Chao et al. 2014; Good-Toulmin) | Expected number of new failure modes from m more runs. Reliable only for modest m (about log n). |
| **number of failure modes** N | population size, species richness | Count of catchable failure modes. **Not identifiable** under uneven detectability: report only as a lower bound. |
| **lower bound** (Chao2) | Chao's estimator | A floor on N; under-estimates whenever detectability is uneven. |
| **catchable population** U | closed population | Failure modes this kind of tool can find at this budget. Failures no run of this tool can find are invisible to every estimator. |
| **identity rule** | matching, record linkage, (photo-)identification | Procedure deciding when two findings are the same failure mode. |
| **ghost** | false non-match, split, spurious singleton | One failure mode counted as two. Inflates N, deflates coverage. |
| **merge** | false match, lumping | Two failure modes counted as one. |
| **correlated catchers** | list dependence, positive dependence | Runs that tend to find the same things (shared base model, prompts, data). Makes audits look more complete than they are. |
| **steered-apart runs** | negative dependence | Runs told to avoid earlier finds. Can make estimates too *high*. |
| **adaptive search** | behavioural response (model Mb), adaptive bias | A run that changes strategy based on what worked (sees monitor verdicts). Makes coverage look higher than it is. |
| **de-adaptation** | adaptive-bias correction (Liyanage et al. 2024) | Re-analysing adaptive runs as if sampled non-adaptively. |
| **effective number of runs** n_eff | effective sample size (Kish) | How many independent runs a set of correlated runs is worth. |
| **planted failure** | seeded defect, marked individual | A failure we put in on purpose, so the truth is known. |
| **planted-mark calibration** | mark-resight / seeded-defect calibration | Planting known items into a real system to measure detectability there (E15). |
| **detectability covariate** | individual covariate (Huggins / Alho) | A measurable property (frequency, strength, subtlety) that predicts detectability. |
| **stopping rule** | stopping criterion (technology-assisted review) | Stop adding runs when the lower confidence bound of coverage reaches a target. |
| **oracle history** | true capture history | The detection history computed with the true identity (testbeds only). |

## Symbols

| Symbol | Meaning |
|---|---|
| K | number of runs |
| S_obs | distinct failure modes found |
| f_k | number found in exactly k runs |
| U | catchable failure modes, \|U\| their number |
| N_all, N_in, N_rec | SynthSAEBench truths: all features (16,384), features within the SAE width (4,096), features recoverable by an oracle union of seeds |
| C, Ĉ | true and estimated coverage |
| Δ(m), Δ̂(m) | true and predicted new finds from m more runs |
| τ, τ_gt | matching threshold; ground-truth catch threshold |
| f, g | ghost (false non-match) rate; merge (false match) rate |
| n_sim | Monte Carlo replicates per simulation cell |
| MCSE | Monte Carlo standard error |
