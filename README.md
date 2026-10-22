# How complete was the audit?

**Estimating what red teams, auditors and interpretability tools miss.**

Safety evaluations report what they found: hidden behaviours, working
attacks, interpretable features. They do not report how much they missed.
This project tests whether the overlap between repeated runs of a safety
discovery tool can estimate:
- **audit coverage**: the share of detectable failure mass already found;
- **how many new failure modes more runs would find**.

The method comes from capture-recapture statistics, and is first validated
on testbeds where the failures were planted and the truth is known.

**Team:** Santosh (statistics and interpretability) and Kushal (safety
testbeds and agents); see [`docs/TEAM.md`](docs/TEAM.md). **Budget:** $0:
open-weight models on CPU and free Kaggle GPUs (decision D-007).

**Status:** pre-registration drafting (v0.1). No confirmatory results yet.
Target venues: an arXiv preprint (December 2026), an ICLR 2027 workshop, and
NeurIPS 2027.

## Where things are

| Path | Contents |
|---|---|
| [`notebook/`](notebook/) | **Lab notebook.** Experiment registry (E00–E18), one pre-registered page per experiment with contingencies, run registry (`runs.csv`), daily log, decisions, deviations, results. Start with [`notebook/README.md`](notebook/README.md). |
| [`docs/`](docs/) | Study pre-registration, roadmap and gates, protocols, paper plan, risks, compute, data registry, disclosure policy, open questions, NeurIPS checklist, glossary. Index: [`docs/README.md`](docs/README.md). |
| [`research/`](research/) | Literature dossier ([`research/README.md`](research/README.md)), reading list, 13 underlying research reports, and the original proposal. |
| [`src/crsafety/`](src/crsafety/) | Estimator library: Chao2 and its interval, iChao2, jackknife, ICE, audit coverage, extrapolation, Chapman, Darroch Mt, Huggins, Chao bootstrap; detection-history I/O (`docs/PROTOCOLS.md` §10). Validated against R in E00. |
| [`tests/`](tests/), [`validation/e00/`](validation/e00/) | Property tests (pytest) and the R reference comparison for E00. |
| [`pilot/`](pilot/) | Pilot simulation of the estimators under uneven detectability, heavy tails, similar catchers and matching errors. |
| [`tools/notebook.py`](tools/notebook.py) | Registers runs, renders run tables, locks pre-registrations, checks the notebook. |

## Quick start

```bash
pip install -e ".[dev]"                  # crsafety + pytest
pytest                                   # property tests
python pilot/simulate.py                 # pilot simulation
python tools/notebook.py check           # validate the notebook
python tools/notebook.py new E01 --owner Santosh --title "Base cell"   # register a run
```

```python
import crsafety as cr
X = ...                    # items x runs, 1 = found by that run
cr.report(X)               # coverage, new items expected from K more runs, Chao2 lower bound, ...
```

## Citation

See [`CITATION.cff`](CITATION.cff).
