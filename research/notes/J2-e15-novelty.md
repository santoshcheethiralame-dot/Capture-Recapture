# E15-R001: novelty check for Q-N1 (2026-10-23, Santosh)

**Question (Q-N1).** Has anyone planted known items into a real ML system,
fitted a detectability curve from them, and used it to calibrate unseen-
failure (coverage) estimates for the real items? Mark-resight analogues and
software seeded-defect work were also to be checked.

**Method.** Four web searches on 2026-10-23: planted features in LM
activations for SAE evaluation; error seeding / planted backdoors to
calibrate audits; mark-resight or seeded defects for LLM red teaming;
planted quirks and alignment-auditing detection rates. arXiv is blocked
here (Q-D1); re-read PDFs before citing.

**Answer: no prior work does the full design (plant → fit detectability →
calibrate coverage of real items → validate on held-out marks). Q-N1 closed
as "novel, as far as we can tell".** The closest work:

- **Kansal, `undiscovered-failures`** (GitHub; already in H1). Plants
  failures in tabular ML and tests Chao1/ACE on them, with a bias-calibrated
  bootstrap. Its planted failures are the whole population. There is no
  transfer of a fitted detectability curve to real items and no held-out
  marks. This is the closest prior work for E15 (and for the project, see
  G/H1); cite it prominently.
- **SAE ground truth in real models.** SAGE (arXiv 2410.07456) builds
  supervised dictionaries as approximate ground truth. The "Sanity checks"
  paper (arXiv 2602.14111) uses synthetic data, and SynthSAEBench is fully
  synthetic. None injects synthetic directions into real activations to
  calibrate detectability, which is what E15's SAE arm does.
- **Alignment auditing.** AuditBench (arXiv 2602.22755) and "Training
  alignment auditors via RL" (arXiv 2608.25460, Anthropic, Aug 2026) use
  planted behaviours, including held-out ones, to *score auditors*. They
  report detection rates (AuditBench's default agent about 37%) but do not
  use them to estimate what remains undiscovered in a model.
- **Software reliability.** Error seeding (Mills 1972) and the comparison of
  removal, marking and seeding designs by Lloyd, Yip and Chan (1999,
  IEEE). These are the methods ancestors of E15. Cite them in one sentence
  alongside mark-resight.
- **Privacy auditing with canaries** (Carlini et al. 2019; Steinke, Nasr,
  Jagielski 2023; from prior knowledge, not re-found in this search: verify
  before citing). Inserted canaries measure memorisation and leakage. This
  is the closest ML precedent for "plant a known item to measure
  detectability", but it is not used for coverage. Worth one sentence in
  related work.
- **Planted backdoors** (Goldwasser et al. 2022) show that some planted
  items can be made undetectable. This is a caveat for E15's H15c: marks
  may not behave like real items. H15c tests exactly that.

Sources (searched 2026-10-23):
- https://github.com/ParitKansal/undiscovered-failures
- https://arxiv.org/pdf/2410.07456
- https://arxiv.org/pdf/2602.14111
- https://arxiv.org/pdf/2602.22755
- https://alignment.anthropic.com/2026/training-alignment-auditors/
- https://repository.hku.hk/bitstream/10722/43501/1/49240.pdf
- https://arxiv.org/abs/2204.06974
