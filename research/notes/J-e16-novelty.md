# E16-R001: novelty check for Q-N2 (2026-10-23, Santosh)

**Question (Q-N2).** Has anyone bounded the missed SAE feature mass from
above using the reconstruction residual, or bracketed it together with a
seed-overlap lower bound?

**Method.** Five web searches on 2026-10-23 (standard and extended). Search
terms: SAE "dark matter", residual upper bound, missed / unlearned features,
capture-recapture / Chao / species richness with SAE seeds, and feature
recovery bounds. arXiv itself is blocked from the sandbox (Q-D1), so
abstracts were read through search snippets and mirrors. Anything we cite
must be re-read from the PDF first.

**Answer: no prior bracket found. Q-N2 is closed as "novel, as far as we
can tell"; re-check in the weekly scoop check.**

Closest work:
- **Engels, Riggs Smith, Tegmark, "Decomposing the dark matter of sparse
  autoencoders"** (TMLR 2025; arXiv 2410.14670). They split the SAE error
  into a linearly predictable part (they suggest this is unlearned linear
  features; about half the error vector, over 90% of its norm) and nonlinear
  error. E16's upper bound is built on this decomposition. They do not
  convert it into a bound on missed feature mass, and they do not pair it
  with a lower bound.
- **"Sanity checks for sparse autoencoders: do SAEs beat random baselines?"**
  (ICML 2026; arXiv 2602.14111). In a synthetic world with ground truth,
  three of four SAE architectures recover 7–9% of true features at about
  71% explained variance, and recovery is biased toward frequent features.
  This is evidence that reconstruction says little about coverage, which
  motivates both bounds. It is an empirical finding, not a bound. Cite it
  in the intro.
- **"A dominant diffuse phase in the sparse autoencoder phase diagram"**
  (arXiv 2609.10299, Sep 2026). L1 SAEs reach a diffuse solution that
  reconstructs well but does not align with true features. If that holds,
  oracle catch rates in E06-type worlds could be low for L1 SAEs; E06 uses
  BatchTopK. Relevant to E06/E11 interpretation.
- **"Diagnosing and fixing latent recovery in sparse autoencoders"** (ICLR
  2026). Gives upper and lower bounds on latent recovery error, in terms of
  dictionary coherence and sparsity. These are a-priori recovery
  guarantees, not data-driven bounds on what a trained SAE missed.
- **OthelloGPT report** (LessWrong): SAEs find 9/180, later 33/180, board
  features. This is a ground-truth recovery rate, a planted-truth analogue
  for E15.
- No source applies capture-recapture, Chao or richness estimators to
  features across SAE seeds. This is also the weekly scoop check for the
  project as a whole (RISKS.md): **no scoop as of 2026-10-23**.

**Consequence for E16.** The bracket (lower = 1 − Ĉ in energy units,
upper = Engels-style linearly predictable residual energy) appears new.
The upper-bound construction should credit Engels et al. directly.

Sources (searched 2026-10-23):
- https://openreview.net/forum?id=5IZfo98rqr
- https://mlanthology.org/tmlr/2025/engels2025tmlr-decomposing/
- https://icml.cc/virtual/2026/79403
- https://www.arxiv.org/abs/2602.14111
- https://arxiv.org/pdf/2609.10299
- https://iclr.cc/virtual/2026/10022177
- https://www.lesswrong.com/posts/BduCMgmjJnCtc7jKc/research-report-sparse-autoencoders-find-only-9-180-board
