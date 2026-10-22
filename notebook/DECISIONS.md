# Decision records

Append-only. To change a decision, add a new record that supersedes it.
Template: [`templates/entries.md`](templates/entries.md). Each record says
whether it affects a pre-registered analysis.

---

## D-001: The paper is an AI-safety paper; ecology is a methods citation (2026-10-22)

**Status:** accepted
**Context:** The method (capture-recapture) comes from ecology. The paper's
audience and venue are AI safety and ML.
**Options:**
- A: frame as "ecological estimators for ML";
- B: frame as "how complete was the audit?", with the estimators as
  methods.
**Decision:** B.
**Why:**
- The question that matters is a safety one: how complete is testing.
- Prior work already rules out "first use of species estimators in ML"
  (Mark-Evaluate 2020, STADS 2018, Kansal 2026).
- Safety venues reward the safety question.
**Consequences:**
- Safety vocabulary throughout (see `docs/GLOSSARY.md`).
- Experiments on audits and red teams lead.
- SAEs are one case study.
- Ecology appears in methods and related work only.
**Affects pre-registered analysis:** no.

## D-002: Coverage and new-find predictions are the headline; counts are labelled lower bounds (2026-10-22)

**Status:** accepted
**Context:** Total N is not identifiable under heterogeneous detection
(Link 2003; Mao and Lindsay 2007). The pilot shows coverage stays accurate
where N estimates fail.
**Decision:**
- Primary estimands: audit coverage C and new-item count Δ(m).
- Chao2 and iChao2 are reported only as labelled lower bounds.
**Why:** theory, the pilot, Kansal's pre-registered results, and the
fuzzing "false peaks" findings.
**Consequences:** PH1 and PH6 centre on coverage; PH2 documents why counts
are bounds.
**Affects pre-registered analysis:** defines it.

## D-003: Target venues (2026-10-22)

**Status:** accepted
**Decision:**
- arXiv preprint and Alignment Forum post in December 2026;
- an ICLR 2027 workshop around 1 February 2027;
- **NeurIPS 2027 main track** (about mid-May 2027, date to be confirmed) as
  the primary target;
- fallbacks: SaTML 2028 or ICLR 2028 (about September 2027), and TMLR for a
  validation or negative-results companion paper.

ICML 2027 (about 22 January) only if E02, E03 and E09 are complete by early
January.
**Why:** audit and red-team experiments need months. Rushing would leave an
SAE-only paper, which is the weakest framing and the most exposed to being
scooped.
**Affects pre-registered analysis:** no.

## D-004: Plain-git lab notebook; no tracking service yet (2026-10-22)

**Status:** accepted
**Options:** Weights & Biases, MLflow, DVC, or plain git with a run
registry.
**Decision:**
- `notebook/runs.csv` is the source of truth, maintained by
  `tools/notebook.py`;
- every run writes a manifest (`docs/PROTOCOLS.md` §5);
- pre-registration blocks are locked by hash.
**Why:**
- one researcher;
- traceability matters more than dashboards;
- no lock-in.

Revisit if the E06 or E11 GPU grids become large.
**Consequences:** discipline is manual; `notebook.py check` enforces the
basics.
**Affects pre-registered analysis:** no.

## D-005: Pre-registration in tiers, with prior knowledge disclosed (2026-10-22)

**Status:** accepted
**Context:** We are not starting blind (pilot, published numbers).
**Decision:**
- E01 is exploratory and may set the † thresholds.
- Study pre-registration v1.0 is frozen before any confirmatory data.
- Stage 3 experiments are frozen one by one.
- Prior knowledge is listed in `LOG.md` (2026-10-22) and in the
  pre-registration.
- The freeze chain is: hash lock → annotated tag → GitHub release → Zenodo
  DOI → OSF registration citing the commit and DOI.
**Why:** best practice for secondary-data and simulation pre-registration
(OSF secondary-data template; Siepe et al. 2024 ADEMP-PreReg; Hofman et al.
2023 two-stage protocol).
**Affects pre-registered analysis:** defines the process.

## D-006 (proposed): Licences: code MIT, documentation and released data CC BY 4.0 (2026-10-22)

**Status:** proposed. **Needs the repository owner's approval.**
**Context:** The repository is MIT-licensed. Datasheets and released data
usually use CC BY 4.0 (the precedent in Kansal's repos).
**Decision (proposed):**
- keep MIT for code;
- license `docs/`, `research/` text and released data tables under
  CC BY 4.0;
- never redistribute upstream data whose licence is unconfirmed: release
  derived statistics plus a regeneration script instead.
**Affects pre-registered analysis:** no.

## D-007: $0 plan: open-weight models on free compute; frontier APIs only as an optional extension (2026-10-22)

**Status:** accepted
**Context:** The available budget is $0 for now (resolves Q-B1).
Resources:
- this sandbox (CPU, R via conda-forge);
- free Kaggle GPUs (2 × T4 or P100, about 30 GPU-hours a week per account,
  roughly 12-hour sessions; check current limits). Two team members means
  two accounts.

**Options:**
- A: wait for funding;
- B: run everything at $0, with open 7–9B models as auditors, attackers,
  targets and judges, and scaled-down GPU grids;
- C: use free API tiers.

**Decision:** B. Frontier-model replication becomes E18 (proposed),
triggered only if credits arrive (for example the OpenAI researcher
programme).

**Why:**
- B keeps every confirmatory hypothesis testable.
- It is fully reproducible (open weights, no API drift, no provider terms).
- It fits the GPU quota: about 150 core GPU-hours across two accounts.

C was rejected for the confirmatory design: free tiers have rate limits,
often let providers train on our prompts, and some forbid red-team use.

**Changes (all before any freeze, so they are not deviations):**
- **E06:** a smaller synthetic world: 4,096 features, d = 256, width
  1,024; budgets 20M and 50M samples.
- **E08:** open-model auditor ladder: Qwen (L0, L1, L2 sizes); Qwen + Llama
  + Gemma (L3). Mistral target with the AuditBench system-prompt quirks. Phi
  or OLMo judge.
- **E09 → "AuditBench-lite":** the 14 AuditBench behaviours implanted by
  QLoRA fine-tuning into Gemma-2-2B-it. Three tool configurations, including
  a white-box Gemma Scope SAE tool.
- **E10:** open-model attackers; a harmless proxy goal (smuggling a fake
  secret token past the monitor).
- **E11:** Pythia-70M only, 8 + 4 + 4 seeds, 50M tokens.
- **E04, E12, E15, E17:** local models; QLoRA fine-tuning on Kaggle.

**Consequences:**
- The safety claims are "for auditors and red teams built on open 7–9B
  models". Generality to frontier models is a stated limitation, until E18.
- Risk of floor effects with small auditors; checked in every pilot before
  freezing.
**Affects pre-registered analysis:** yes; it defines the testbeds of E06,
E08–E11 before the v1 freeze.
