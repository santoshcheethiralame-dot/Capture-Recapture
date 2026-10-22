# Disclosure and dual-use policy

Written before Phase 3 begins. Most of this project carries no misuse risk:
estimators, synthetic SAEs, coverage statistics. The exposure is in the red
team and audit experiments, which produce attack transcripts and catalogues
of monitor weaknesses.

Under the $0 plan (D-007), all attackers, auditors and targets are open
models we run ourselves, and the red-team goal is a harmless proxy (a fake
token). This lowers the exposure. The rules below still apply, and become
central if E18 (frontier models) runs.

## Risk assessment

| Artefact | What a misuser gains | Tier |
|---|---|---|
| Estimator code, synthetic worlds, SAE checkpoints, configs | Nothing harmful | **Public** |
| Detection histories (which run found which item), coverage statistics, strategy-level labels and counts | Nothing actionable | **Public** |
| The E10 monitor with planted blind spots, and attacks against it | Attacks against a toy we built; little transfer | **Public**, after a review that no blind spot mirrors a weakness of a deployed product |
| Audit transcripts against open model organisms (AuditBench LoRAs, our organisms) | Little | **Public**, unless the upstream licence or gating says otherwise |
| Attack transcripts or payloads that work on **deployed** third-party models | Working exploits | **Withheld**. Shared only with the affected provider; gated access for researchers at most |
| Strategy catalogues naming specific blind spots of deployed monitors | Targeted evasion | **Gated**: a request stating the purpose, plus an agreement; approval by the repo owner |

## Rules

1. **Prefer our own targets.** Planted organisms, our own monitor, and open
   models come first. Testing deployed third-party systems is the
   exception, and needs a reason recorded in `DECISIONS.md`.
2. **Provider terms.** Before testing a third-party API at scale, read its
   usage policy and any research or safe-harbour terms. Record the status
   per provider below. Never use jailbreaks to make a model act as our
   red-teamer.
3. **Pre-publication notice.** If a finding is a working exploit on a named
   deployed model:
   - notify the provider through its official channel (for example
     Anthropic's HackerOne programme for jailbreaks) before any preprint;
   - the notice window is **30 days** (proposed; owner to confirm), unless the provider asks for a
     different one. This is our choice; no AI-specific standard exists. Log
     the reason for any change.
4. **Canary strings.** Every released file containing attack text or
   planted-failure labels carries a canary block. Use the BIG-bench canary
   string copied from the BIG-bench repository, plus a project GUID. Canaries
   help filter training data; they are **not** access control.
5. **Held-out split.** Any released benchmark keeps a private held-out
   portion for uncontaminated evaluation.
6. **Upstream gating.** Data obtained through gated access (for example
   SLEIGHT-Bench) is never re-released and never pasted into prompts that
   might be used for training. We use only its derived statistics.

## Provider status

| Provider | Usage policy read | Red-team research allowed? | Channel for disclosure | Date |
|---|---|---|---|---|
| Anthropic | | | HackerOne programme (cyber jailbreaks) | |
| OpenAI | | | | |
| Google | | | | |
| Open-weights host | | | | |

## Disclosure log

| Date | Recipient | What was shared | Response | Follow-up |
|---|---|---|---|---|

_Nothing disclosed yet._
