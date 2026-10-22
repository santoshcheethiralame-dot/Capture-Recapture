# Lab notebook

This is the project's record of what we planned, what we ran, what happened,
and what we changed. If a result is not in here, it did not happen. If a plan
changed and the change is not in here, the paper cannot claim it was planned.

## What lives where

| File | What it is | How it changes |
|---|---|---|
| [`REGISTRY.md`](REGISTRY.md) | Every experiment: ID, tier, stage, status, dependencies, hypotheses | Edit status by hand; run counts are rendered |
| [`experiments/`](experiments/) | One page per experiment: question, **pre-registration**, contingencies, runs, results, deviations | Pre-registration is frozen; runs and results are appended |
| [`runs.csv`](runs.csv) | Every run, one row each. **Source of truth for runs.** | Only through `tools/notebook.py` |
| [`LOG.md`](LOG.md) | Dated journal: what was done, seen, and thought each working day | Append-only, newest at the bottom |
| [`DECISIONS.md`](DECISIONS.md) | Decision records: choices that shape the study, with alternatives and reasons | Append-only; supersede, never edit |
| [`DEVIATIONS.md`](DEVIATIONS.md) | Every departure from a frozen pre-registration | Append-only |
| [`RESULTS.md`](RESULTS.md) | One line per hypothesis: verdict, estimate, evidence link | Updated when an experiment's analysis is final |
| [`prereg-locks.csv`](prereg-locks.csv) | Hash of each frozen pre-registration block, with commit and date | Only through `tools/notebook.py freeze` |
| [`templates/`](templates/) | Blank experiment page, log entry, decision and deviation | Copy, do not edit in place |

The study-level pre-registration (the paper's confirmatory hypotheses) is in
[`../docs/PREREGISTRATION.md`](../docs/PREREGISTRATION.md). Experiment pages
refer to its hypotheses by ID (PH1 to PH6).

## IDs

- **Experiments:** `E00` to `E17`. IDs never change and are never reused. A
  dropped experiment keeps its ID with status `dropped`.
- **Runs:** `E02-R001`, `E02-R002`, ... assigned by the tool, in order of
  registration. A run is one execution of one configuration that produces
  one set of outputs. A replicate sweep launched as one job is one run. Its
  config lists the replicates.
- **Hypotheses:** study-level `PH1` to `PH6`. Experiment-level `H2a`, `H2b`
  (experiment number plus a letter).
- **Decisions and deviations:** `D-001`, `V-001`.

## Statuses

Experiments: `proposed` → `registered` (pre-registration written) → `frozen`
(locked by hash) → `running` → `analysed` → `done`. Also `blocked`,
`dropped`.

Runs: `planned` → `running` → `succeeded` | `failed` | `aborted`.
`superseded` marks a run replaced by a later one. Say which in the notes.

## The workflow for every experiment

1. **Write the page** from [`templates/experiment.md`](templates/experiment.md).
   Fill the pre-registration completely, including the contingency table.
2. **Freeze** before touching any data the hypotheses are about:
   `python tools/notebook.py freeze E02 --note "prereg v1"`, then commit. The
   commit is the timestamp. Tag study-level freezes (`prereg-v1`).
3. **Register each run before launching it:**
   `python tools/notebook.py new E02 --title "..." --config configs/e02/r001.yaml`.
   Planned runs can be registered ahead of time with the default status
   `planned`.
4. **Run.** Set `status=running` when it starts. The tool stamps the commit.
   Outputs go to `results/E02/E02-R001/` (data, figures) and the path goes in
   the `outputs` field. Large files stay out of git; record a hash and a
   location instead (see [`../docs/DATA.md`](../docs/DATA.md)).
5. **Close the run.**
   `python tools/notebook.py set E02-R001 status=succeeded summary="..."`.
   A summary is mandatory for succeeded and failed runs. Write the number
   that matters, not "done".
6. **Write the day's entry in `LOG.md`.** Say what you saw, including
   anything surprising and anything you did not expect to matter.
7. **Analyse.** Fill section 5 of the page: confirmatory results first,
   exactly as pre-registered, then a clearly labelled exploratory section.
   Then update `RESULTS.md`.
8. **Render and check:** `python tools/notebook.py render && python tools/notebook.py check`.
   Commit.

## When a run fails

Never delete a failed run or its outputs. Classify the failure first,
because the class decides what happens next.

| Class | Examples | What to do | Counts as a deviation? |
|---|---|---|---|
| **Infra** | OOM, preemption, API rate limit or outage, disk full, network | Fix, then re-launch as a **new run ID**, noting "retry of E02-R003". At most 2 retries per configuration before treating it as a design problem. | No, if the configuration is unchanged |
| **Bug** | Wrong output, crash in our code, failed sanity check | Mark the run `failed`. Fix the bug with a test. Re-run as a new run ID. If any result already reported used the buggy code, add a `LOG.md` entry naming the affected runs and mark them `superseded`. | No, unless the fix changes the analysis plan |
| **Data / access** | Model or dataset unavailable, licence or gating refused, artefact differs from its description | Follow the experiment's contingency table. Record the change in `DEVIATIONS.md` if the testbed changes. | Yes, if the testbed or estimand changes |
| **Design** | Estimator undefined (e.g. f2 = 0 everywhere), no overlap between runs, ceiling or floor effects, budget exhausted | Follow the contingency table. If a pilot shows the design cannot answer the question, stop, write it up, and amend the pre-registration **before** the confirmatory run. | Yes |
| **Scientific "failure"** (hypothesis not supported) | The estimator is biased; the correction does not work | **This is a result, not a failure.** Report it exactly as pre-registered. Do not re-run, re-tune or redefine to rescue it. Exploratory follow-up is allowed and must be labelled as such. | No |

Hard rules:
- **No silent re-runs.** Every execution gets a run ID, including the ones
  that failed in the first minute.
- **No silent exclusions.** If replicates, seeds or targets are dropped,
  the rule must be pre-registered or logged as a deviation, with counts.
- **No peeking.** Do not inspect confirmatory outcomes before the page is
  frozen. Pilots are allowed if declared as pilots and run on separate
  seeds, targets or worlds.
- **Estimator failures are data.** If an estimator returns NaN or infinity
  (for example, no recaptures), record the failure rate as a performance
  measure. Do not drop those replicates.

## Writing style for entries

Write for someone reading the notebook in a year, or a reviewer asking how a
number was produced. Give the number, the run ID, and what it means. Prefer
"Chao2 was 31% below N_rec (E02-R004, BatchTopK, L0 = 25)" over "Chao2 looks
low".
