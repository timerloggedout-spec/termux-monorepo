# SYNAPSE Experiment Lane

Use this directory for bounded, reproducible tests of proposed cognitive subsystems.

## Experiment record

Each experiment should include:

- hypothesis and target gap;
- baseline and treatment;
- frozen cohort/task definition;
- source SHA and relevant configuration hashes;
- input and exclusion criteria;
- success, failure, and safety metrics;
- sample size and uncertainty;
- artifact/evidence locations;
- conclusion: reject, iterate, retain as candidate, or recommend promotion.

## Suggested first experiments

1. **Salience replay:** replay historical CI/provider events and compare alert ranking against known severity.
2. **Handoff contract:** compare current agent coordination with a typed acknowledgement envelope.
3. **Context retrieval:** evaluate graph retrieval against a fixed set of known related PR/file/symbol questions.
4. **Consolidation:** compare retrieval precision before and after reversible source-linked summaries.
5. **Manager plasticity:** compare a fixed manager policy with a bounded adaptive policy on matched cohorts.

## Guardrails

- Experiments do not mutate production routing by default.
- Never use secrets, prompt bodies, completions, or arbitrary tool payloads as shared evidence.
- A failed experiment is retained as evidence.
- No promotion based solely on speed, activity, or a composite score.
- No automatic retry just to obtain a passing result.
