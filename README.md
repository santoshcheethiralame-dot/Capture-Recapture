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
| [`pilot/`](pilot/) | Pilot simulation of the estimators under uneven detectability, heavy tails, similar catchers and matching errors. |
| [`tools/notebook.py`](tools/notebook.py) | Registers runs, renders run tables, locks pre-registrations, checks the notebook. |

## Quick start

```bash
pip install numpy scipy
python pilot/simulate.py                 # pilot simulation
python tools/notebook.py check           # validate the notebook
python tools/notebook.py new E01 --owner Santosh --title "Base cell"   # register a run
```

## Citation

See [`CITATION.cff`](CITATION.cff).
