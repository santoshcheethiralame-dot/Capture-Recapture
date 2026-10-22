# Standard protocols

Every experiment follows these protocols unless its pre-registration says
otherwise. Changing a protocol after a freeze is a deviation for every
frozen experiment that uses it.

## 1. Estimator suite

- **Code:** `src/crsafety/estimators/`, grown from `pilot/estimators.py`.
  Validated in E00. No estimator may be used as primary until E00 marks it
  validated.
- **Primary:**
  - Chao-Jost incidence coverage Ĉ, with the realized-coverage bootstrap
    interval `crsafety.coverage_interval` (B = 1,000; D-010). The iNEXT
    interval is reported as secondary;
  - Chao et al. (2014) Δ̂(m) for m ≤ K, with `crsafety.delta_interval`
    (bias-corrected, B = 1,000; D-010);
  - bias-corrected Chao2, labelled "lower bound".
- **Secondary:** iChao2 (K ≥ 4), jackknife 1 and 2, ICE, Chapman for every
  run pair, Darroch Mt.
- **As named in experiments:**
  - Huggins / Böhning (covariates);
  - log-linear models for K ≥ 3 with dependence: `crsafety.loglinear`
    (Rcapture's `closedp.t` models, plus run interactions as in
    `closedpCI.t`; validated in E00-R003). `dga` is not ported;
  - f1-free: `crsafety.rbridge.breakaway_nof1` (R `breakaway` through
    `Rscript`; needs R);
  - generalised Chao with covariates: `crsafety.generalized_chao`;
  - dependence-robust interval (Sun et al. 2023).
- **Always print** K, S_obs, f1 to f4, Ĉ, Δ̂(K), Chao2, and the identity
  rule with its threshold. See the reporting recipe (§8).
- **Undefined values:** if f2 = 0, use the bias-corrected form. Any NaN or
  infinity is recorded as a failure with a reason code and never silently
  dropped.

## 2. Identity rules

### SAE features

1. **Preprocess each SAE:**
   - drop dead latents (no activation on 10^6 samples);
   - merge within-SAE duplicates (\|cos\| ≥ 0.95, including antipodal
     pairs);
   - for JumpReLU SAEs, fold thresholds into the weights before comparing
     (SAE Match).
2. **Match across seeds:** default Hungarian on \|decoder cosine\| (M1),
   until E03 picks the winner. Clusters are the connected components of the
   accepted-match graph.
3. **Threshold:**
   - before E03: τ = 0.7;
   - after E03: the plateau rule (largest τ-interval of width ≥ 0.10 where
     the cluster count changes < 5%; take its midpoint);
   - with no plateau, report "no trustworthy threshold" and use
     E05-corrected sensitivity bands.
4. **Oracle catch (testbeds):** \|cos\| ≥ τ_gt = 0.7 to the true direction
   under one-to-one Hungarian assignment.

### Attack strategies and audit findings

1. **Instrumented identity first.** Where the testbed can label identity by
   construction (E10 monitor logs; AuditBench planted behaviour), that
   label is the truth.
2. **Judge-based identity:**
   - an LLM judge assigns each finding to a fixed rubric category, or to
     "new";
   - the judge must come from a **different model family than every
     catcher** in the experiment;
   - temperature 0;
   - prompt version-controlled in `prompts/`.
3. **Judge validation:**
   - 100 or more findings labelled by hand (stratified by category);
   - report Cohen's κ against the hand labels;
   - κ < 0.7 blocks use, until the rubric is fixed and re-validated.
4. **Granularity:** report estimates at each rubric level (family /
   mechanism / implementation). The mechanism level is primary.

## 3. Runs and independence

- **Runs must not see each other.** No shared memory, scratchpads or
  leaderboards between runs of the same experiment, unless dependence is
  the manipulated factor.
- **Fixed budgets** per run (tokens, queries, wall-clock), pre-registered.
- **Sampling:** temperature as the catcher's default, unless
  pre-registered. Every run's random seed is recorded.
- **Model versions:** open models are pinned to a Hugging Face revision
  (commit hash) and quantisation, recorded in the manifest. API models (E18
  only) are pinned to dated snapshots.
- **Local serving:** vLLM on Kaggle (fp16 or AWQ on T4). Record the vLLM
  version, `max_model_len` and the sampling parameters in the manifest.

## 4. Seeds

- One master seed per experiment (written in its pre-registration; default
  `20261022 + experiment number`).
- Child seeds come from `numpy.random.SeedSequence(master).spawn(n)`, one
  per cell, then one per replicate. The cell seed is written in every
  result row, so any cell can be re-run alone.
- For SAE training: seed the initialisation and the data order separately,
  and record both.

## 5. Run manifests

Each run writes `results/EXX/<run_id>/manifest.json` at start, and
completes it at the end:

```
run_id, experiment, prereg_tag, confirmatory (bool), git_sha, git_dirty,
diff_sha256 (if dirty), command, config (resolved), config_sha256,
env_lock_sha256, python_version, package_versions, hardware,
seeds {master, cell}, inputs [{path, sha256}], model_ids [{name, snapshot}],
started_utc, finished_utc, status, outputs [paths], cost {gpu_hours, api_usd}
```

- **Confirmatory runs refuse to start from a dirty tree.** Exploratory runs
  may, and are flagged.
- Large outputs (activations, SAE weights, transcripts) stay out of git.
  The manifest records their location and sha256 (see `DATA.md`).

## 6. LLM calls

- **Cache every call.** Key: sha256 of (model id, full prompt, parameters,
  seed). One file per generation under `cache/llm/`, which is git-ignored
  and backed up. A script can then stop and resume without paying twice.
- **Log token usage and cost** per run in the manifest.
- **Never use jailbreaks** to make a model act as a red-teamer. If a model
  refuses, use a model or provider that permits red-team use (`DISCLOSURE.md`).

## 7. Uncertainty

- **Simulations:** report MCSE for every bias, coverage and RMSE.
  - MCSE(bias) = SD(θ̂)/√n_sim.
  - MCSE(coverage) = √(p(1−p)/n_sim).
  - n_sim = 500 gives about 0.01 at p = 0.95.
- **Paired comparisons:** use the same simulated datasets for every method,
  and compute the MCSE of the paired differences. A difference counts only
  if it exceeds 2 × its MCSE.
- **Real-tool testbeds:**
  - bootstrap over **targets / items** (and over runs, where runs are
    exchangeable);
  - when K-subsets are drawn from M collected runs, the subsets overlap;
    report the number of distinct subsets, and do not treat them as
    independent replicates.
- **Verdicts** follow the study pre-registration §7: supported / not
  supported / inconclusive.

## 8. Reporting recipe (every tool, every table)

1. K, S_obs, f1 to f4, identity rule and threshold.
2. **Coverage Ĉ with 95% CI** (the headline).
3. **Δ̂(m) for m = K and 2K**, with CI. Flag m > K as long-range.
4. **Chao2 labelled "lower bound"**, with its CI described as an interval
   for the bound, not for N.
5. Jackknife-2 or ICE as a comparison.
6. **Dependence:**
   - n_eff;
   - pairwise observed/expected overlap;
   - Chapman for every pair (range);
   - drop-one-run trajectory.
7. **Sensitivity:**
   - estimates across the threshold or granularity sweep;
   - an f1-free estimate;
   - a singleton-corrected Chao2.
8. **The estimand:** "catchable by <tool> at <budget>", plus known blind
   spots.

## 9. Code and environment

- Python ≥ 3.11. Dependencies are locked in `requirements.lock` (`uv pip
  compile` or `pip-tools`), and its hash goes in every manifest.
- R packages run through `rpy2`. The R version and package versions are
  recorded.
- Tests (`pytest`) must pass before any run is registered as confirmatory.
- Every figure and table in the paper is produced by a script from
  `results/`. No hand-edited numbers.

## 10. Data interface: detection histories

This is the handoff format between whoever produces runs (Kushal for audits
and red teams; Santosh for SAEs) and the analysis code. Agreed by both;
changing it after a freeze is a deviation.

Each experiment cell writes one directory
`results/EXX/<run_id>/histories/<cell_id>/` containing three CSV files:

**`detections.csv`**: one row per (item, run) where the item was found.
Rows for "not found" are implicit.

| column | type | meaning |
|---|---|---|
| `cell_id` | str | experiment cell (e.g. `L0`, `T3`, `btk_l0-25`) |
| `run_idx` | int | 1..K, the occasion index inside the cell |
| `item_id` | str | identity of the finding under the stated identity rule |
| `identity` | str | `oracle`, `instrumented`, `judge:<rubric_version>`, or `matched:<matcher>@<tau>` |
| `evidence` | str | pointer to the raw finding (file path, latent index, report line) |
| `score` | float | match score or judge confidence (blank if instrumented or oracle) |

**`runs.csv`**: one row per run in the cell (including runs that found
nothing).

| column | type | meaning |
|---|---|---|
| `cell_id` | str | |
| `run_idx` | int | |
| `catcher` | str | model, revision, scaffold and configuration |
| `seed` | int | |
| `role` | str | `estimation` or `reference` |
| `status` | str | `ok`, `crashed_rerun`, `failed_counted_as_none` |
| `cost_gpu_h` | float | |

**`items.csv`**: one row per known item, in testbeds with truth.

| column | type | meaning |
|---|---|---|
| `item_id` | str | |
| `planted` | bool | true for planted or known items |
| `covariates` | json | e.g. `{"p": 0.003, "subtlety": "hard"}` |

Rules:
- Item IDs under `oracle` or `instrumented` identity are stable across
  cells, so cells can be compared. Matched or judge IDs are only meaningful
  within a cell.
- A cell's estimation and reference runs are in the same files, separated
  by `role`.
- The analysis code reads only these files. If an analysis needs anything
  else, add a column here first, through a PR approved by both people.
- Before handing a cell over, run
  `python -m crsafety.histories check results/EXX/<run_id>/histories/*/`.
  It lists every violation of the rules above (exit code 1 if any).
