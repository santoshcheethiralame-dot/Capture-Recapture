# Capture-Recapture for Safety Tools

**Question.** Safety tools report what they found: SAE features, red-team
attacks, hidden behaviours. Can we estimate what they missed? Ecologists
answer this for animal populations by comparing overlapping catches. This
project tests whether the same estimators work for AI-safety discovery tools,
first where the truth is known, then where it is not.

## Contents

- [`research/README.md`](research/README.md): **start here.** The research
  dossier: novelty and closest prior work, findings that change the plan, the
  updated design for each phase, the experiment menu, the reporting recipe,
  and risks.
- [`research/reading-list.md`](research/reading-list.md): prioritised reading
  list, datasets and code.
- [`research/notes/`](research/notes/): the 11 underlying research reports,
  with paper-by-paper detail and search logs.
- [`research/proposal.md`](research/proposal.md): the original proposal.
- [`pilot/`](pilot/): a small simulation of the estimators under the expected
  violations: uneven catchability, heavy tails, similar catchers, and matching
  errors.

## Quick start

```bash
pip install numpy scipy
cd pilot && python simulate.py
```
