# NeurIPS checklist (living)

Fill this as the work happens, not the week of the deadline. Each row says
what will satisfy the item and where it lives.

> **Item names follow the 2025/2026 checklist from memory (unverified).**
> Re-read <https://neurips.cc/public/guides/PaperChecklist> and the 2027
> handbook as soon as they are published, and update this table.
> Confirmed facts: the checklist is mandatory (no checklist means desk
> rejection) and sits after the references. Each item is Yes / No / N/A
> with a short justification. The 2026 handbook asks authors to describe
> LLM or agent use when it is part of the core method.

| # | Item | Planned answer | What satisfies it | Where | Done |
|---|---|---|---|---|---|
| 1 | Claims match results | Yes | Claim → evidence map; confirmatory / exploratory labels | `PAPER-PLAN.md`, `notebook/RESULTS.md` | ☐ |
| 2 | Limitations | Yes | Section 7 of the paper, drafted from `RISKS.md`: catchable population only, synthetic-to-real gap, planted ≠ real, K cost, judge-based identity, model drift | paper §7 | ☐ |
| 3 | Theory assumptions and proofs | N/A or Yes | Only if we state a bound. Cite Link 2003 and Mao & Lindsay 2007 for non-identifiability rather than re-prove it | paper §2 | ☐ |
| 4 | Reproducibility of results | Yes | Pre-registrations, configs, seeds, manifests, scripts that regenerate every figure | `docs/PROTOCOLS.md`, `notebook/` | ☐ |
| 5 | Open access to data and code | Yes | Anonymised repo at submission; exact commands; data release plan with licences | `docs/DATA.md` | ☐ |
| 6 | Experimental settings / details | Yes | Grids, thresholds, budgets, all pre-registered | experiment pages | ☐ |
| 7 | Statistical significance | Yes | MCSE for simulations; bootstrap CIs over targets/runs; per-campaign success rates (not only means) | `docs/PROTOCOLS.md` §7 | ☐ |
| 8 | Compute resources | Yes | GPU-hours and API cost per experiment, **including failed and exploratory runs**, summed from the manifests | `docs/COMPUTE.md` | ☐ |
| 9 | Code of ethics | Yes | Review the code; dual-use covered in item 11 | — | ☐ |
| 10 | Broader impacts | Yes | **Positive:** better reporting of how complete safety testing is. **Negative:** false reassurance from coverage numbers; mitigated by lower-bound framing and "catchable population" wording | paper | ☐ |
| 11 | Safeguards | Yes | Release tiers; attack payloads withheld; canaries | `docs/DISCLOSURE.md` | ☐ |
| 12 | Licences for existing assets | Yes | Licence of every upstream asset (SynthSAEBench, SAELens, AuditBench, Petri, Bloom, ControlArena, R packages, models) | `docs/DATA.md` | ☐ |
| 13 | New assets | Yes | Model cards (SAE replicates), datasheets (detection histories), Croissant if hosted | `docs/templates/` | ☐ |
| 14 | Crowdsourcing / human subjects | N/A (or Yes if we hire labellers for judge validation) | If yes: instructions, pay | — | ☐ |
| 15 | IRB | N/A (unless item 14 = Yes) | — | — | ☐ |
| 16 | LLM usage | **Yes** | LLM judges, investigator agents and attackers are core methods: name models and snapshots, give prompts in the appendix, report judge-vs-human validation (κ). **Also disclose LLM assistance in writing and code**: an AI coding assistant drafted code, analysis scripts and first drafts of paper sections, which the authors reviewed, ran and revised. Wording draft below; authors to edit | `docs/PROTOCOLS.md` §2, §6 | ☐ |

## LLM-use statement (draft; authors to edit before submission)

> We used an AI coding assistant to write and test parts of the estimator
> library and the analysis scripts, and to draft sections of this paper.
> The authors specified the study, pre-registered it, reviewed all code and
> text, ran the experiments and are responsible for every claim. LLMs used
> as auditors, attackers and judges in the experiments are described in
> §4 and the appendix.

## Submission-day steps

1. Regenerate all figures and tables from `results/` with one script.
2. Check that every number in the paper cites a run ID.
3. Check that confirmatory / exploratory labels match `notebook/RESULTS.md`.
4. Run `tools/notebook.py check`. It must pass, with deviations reconciled.
5. Make an anonymised snapshot (strip names, the git history and
   `notebook/LOG.md` personal notes) for reviewers.
6. Upload the deviation table as an appendix.
