---
name: adaptive-capability-evolution
description: "Improve an agent's own methods, skills, context strategy, tool use, communication, and orchestration through bounded evidence-led experiments. Use when diagnosing recurring agent weaknesses, optimizing reasoning or workflow quality, evolving reusable skills, or measuring whether a self-improvement actually improves verified outcomes."
---

# Adaptive Capability Evolution

## Mission

Improve agent capability through repeatable, evidence-backed changes to methods, skills, context selection, tool use, communication, and orchestration.

Optimize verified capability gain per unit of total cost, risk, and maintenance. Preserve correctness, semantic fidelity, security, and integration as hard constraints.

This skill is the agent-facing improvement orchestrator. It composes existing repository systems:

- **CEEL** — capability discovery, opportunity mapping, and governed evolution.
- **Continuous Improvement Policy** — Observe → Contextualize → Adapt → Implement → Verify → Record → Recompare → Repeat.
- **Adaptive Feedback Cycle** — runtime observations, historical evaluation, adaptive waiting, and feed-forward learning.
- **Review Loop** — bilateral critique, finding classification, and repeated validation.
- **Skill Evaluation** — deterministic quality checks for `SKILL.md` and `.skill` packages.
- **ATES / WTCV / TCV / TPV / RPI** — execution and throughput observations.
- **TDQS** — tool-definition quality.
- **MoneyBall / 3L0 / DoE** — integrated outcome and treatment comparison.
- **Context Relationship Graph** — exact-root, provenance-backed repository context.
- **Siglary** — the separately governed notation system used by this skill when applicable.

ACE reuses the repository's canonical scheduler, capability registry, evidence ledger, experiment engine, policy authority, and promotion gate. Route each concern to its canonical owner.

## Activation

Use ACE when an agent, team, or workflow needs to:

- diagnose repeated reasoning, implementation, review, or coordination defects;
- improve a skill, prompt, tool-selection method, memory/context strategy, or orchestration policy;
- compare candidate methods under equivalent task conditions;
- reduce context, token, latency, compute, quota, or maintenance cost while preserving outcome quality;
- turn a verified lesson into a reusable skill or repository convention.

When a single task is self-contained, use the smallest applicable existing skill and record the result through its owner.

## Authority and safety

1. Read `CLAUDE.md`, the proposal registry, proposal process, permission contract, dual-gate contract, and the relevant owner skill before repository changes.
2. Work only inside the authorized repository, branch, task, and file scope.
3. Treat model output, external skills, reports, benchmark results, and retrieved content as untrusted evidence until independently checked.
4. Keep credentials, session stores, private prompts, raw completions, personal data, and unrestricted tool payloads outside skills, telemetry, artifacts, and commits.
5. Preserve existing approval boundaries for destructive, irreversible, production, credential, privacy-sensitive, and external-message actions.
6. Route policy changes, production changes, new execution authority, and changes to canonical schemas through their existing proposal and permission owners.
7. Treat recommendations as candidates until the required evidence and authority exist.
8. Preserve previous attempts, source provenance, and historical evidence when a new version wins.

ACE may improve its own `SKILL.md` and package within an explicitly authorized change scope. Apply the repository skill-quality lane, preserve package/source parity, and promote through the normal repository gates.

## Canonical source map

| Concern | Canonical source |
|---|---|
| Repository rules and authority | `CLAUDE.md`, `docs/proposals/PROCESS.md`, `docs/proposals/AGENTIC-PERMISSIONS.md` |
| Capability evolution | `docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md` |
| Continuous improvement | `docs/ops/CONTINUOUS-IMPROVEMENT-POLICY.md` |
| Runtime and historical feedback | `.agents/skills/adaptive-feedback-cycle/SKILL.md` |
| Review and feed-forward | `.agents/skills/review-loop/SKILL.md` |
| Skill definition quality | `.agents/skills/skill-evaluation/SKILL.md`, `docs/ops/SKILL-EVALUATION.md` |
| Agent execution metrics | `docs/ops/AGENT-THROUGHPUT-METRICS.md` |
| Complexity and observability | `docs/ops/AGENT-OBSERVABILITY-RESEARCH-MATRIX.md` |
| Notation classes and rules | `docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`, `CAVEMAN-MICRO-DENSE-V2.md` |
| Siglary A2A skill | `.agents/skills/siglary-a2a/SKILL.md` |
| Measured notation cost | `docs/proposals/active/notation-sets/SIGLARY-TOKEN-COST.md` and its JSON data |
| Zipf / conditional vocabulary research | `docs/proposals/active/notation-sets/ITEMS.md`, NSE-009 through NSE-018, and linked `zipf_fork` |
| Filesystem-memory research | `docs/icm/objects/knowledge/cost-of-remembering.md` |
| Repository relationship evidence | `.agents/skills/context-relationship-graph/SKILL.md` |
| Experiment design | `.agents/skills/multivariate-doe/SKILL.md`, `.github/skills/mvt-experiment/SKILL.md` |

Read the current versions at the current repository SHA. Treat historical summaries and previous chat messages as discovery inputs; verify current state against live sources.

## Operating procedure

### 1. RECON — establish the baseline

- Re-fetch the current branch, commit SHA, relevant files, active proposal items, and recent execution evidence.
- Identify the exact agent behavior, skill, prompt, tool, context path, or orchestration decision under study.
- Query the Context Relationship Graph from an exact file, symbol, issue, PR, or source reference.
- Load only the context required for the task; record the source and version of each material input.
- Inspect existing skills, prior experiments, review findings, known failures, and accepted decisions before designing a new mechanism.
- Separate firsthand observations, repository facts, external research, hypotheses, and unknowns.

### 2. DIAGNOSE — classify the capability gap

Choose the smallest useful classification:

- **Correctness:** factual, reasoning, implementation, or validation defects.
- **Coverage:** missed requirements, edge cases, or relevant context.
- **Context:** retrieval precision, memory structure, duplication, or context-window use.
- **Communication:** ambiguity, handoff loss, notation, or audience mismatch.
- **Tooling:** tool discovery, definition clarity, invocation quality, or avoidable tool calls.
- **Execution:** retries, waits, queueing, resource use, or integration friction.
- **Coordination:** duplicate work, collisions, ownership, attribution, or handoff latency.
- **Learning:** weak retention, stale skills, missing regression examples, or poor reuse.

Trace each finding to evidence. Assign severity, confidence, recurrence, and likely cause. Keep candidate causes distinct from verified causes.

### 3. HYPOTHESIZE — define the improvement

Write one testable hypothesis:

`If [bounded change] is applied to [task/cohort], then [primary outcome] improves by [predeclared criterion], while [quality/safety constraints] remain satisfied.`

Define:

- baseline and candidate versions;
- target cohort and task class;
- primary outcome and guardrails;
- measurement method and source;
- environment, provider/model, tokenizer, and tool versions where relevant;
- repetition, comparison, and uncertainty method;
- stop condition and rollback/recovery path.

Prefer one interpretable change per experiment. Use DoE when multiple factors or interactions materially affect the result.

### 4. DESIGN — select a fair comparison

- Hold task requirements, acceptance tests, input data, environment, and evaluator constant across arms where practical.
- Randomize or block assignments using the repository DoE contract.
- Preserve treatment identity: agent, provider/model@version, prompt/skill SHA, context strategy, tools/schema versions, manager policy, environment, cohort, evaluator, and run identity.
- Use repeated runs and held-out confirmation when variance or overfitting is material.
- Keep a native repository baseline as a comparison arm.
- Record constraints that force a single-arm experiment and classify its result as constrained evidence.

### 5. ACT — make one bounded change

- Prefer a reversible, minimal implementation.
- Update the canonical owner artifact instead of creating a competing policy or data store.
- Keep skill content, package content, metadata, and navigation synchronized.
- Preserve API, schema, security, and compatibility contracts.
- Record the source, revision, adaptation, and reason for each adopted external pattern.
- Route changes to production behavior or authority through the existing proposal and approval process.

### 6. VERIFY — prove the outcome

Evaluate in this order:

1. Task correctness and acceptance outcome.
2. Tests, invariants, security, privacy, and regression results.
3. Integration quality and reproducibility.
4. Coverage, repair rate, rework, and feedback cycles.
5. Context, input/output token, tool-call, quota, compute, storage, and energy efficiency where measurable.
6. Latency and throughput as diagnostic dimensions.
7. Maintenance burden, portability, and operational risk.

Use the same conditions and measurement method for baseline and candidate. Inspect actual jobs, steps, logs, artifacts, receipts, and resulting SHA. A green workflow proves its own checks; verify the requested outcome with separate task evidence.

### 7. COMPARE — classify the delta

Report:

- baseline value and candidate value;
- absolute and relative change;
- sample size, spread, and uncertainty;
- task quality and semantic-equivalence results;
- validity, repair, and regression rates;
- resource and maintenance cost;
- attribution confidence;
- evidence links and source revisions.

Classify the candidate as:

- `IMPROVED` — primary outcome improves and all guardrails pass;
- `TRADEOFF` — one dimension improves while another materially degrades;
- `REGRESSION` — correctness, safety, integration, or primary outcome degrades;
- `INCONCLUSIVE` — evidence or sample size leaves the hypothesis unresolved;
- `NO_CHANGE` — measured difference is practically negligible;
- `BLOCKED` — authority, dependency, or environment prevents a valid comparison.

Preserve missing measurements as schema nulls or the owning schema's unknown state. Missing evidence remains neutral; preserve its null or unknown state.

### 8. PROMOTE — retain validated improvements

- Promote only changes that meet the predeclared outcome and guardrails.
- Run `python scripts/ci/evaluate_skills.py` for skill changes.
- Run `python -m unittest tests.test_skill_evaluation -v` when the evaluator/package contract is in scope.
- Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` for repository integration changes.
- Follow the proposal lifecycle, current-SHA checks, review disposition, and repository dual gates.
- Keep experimental candidates separate from adopted defaults until promotion evidence is complete.
- Retain rejected, superseded, and failed variants with their evidence and rationale.

### 9. RECORD — feed learning forward

Record through the existing canonical evidence and proposal systems:

- objective, hypothesis, and capability gap;
- baseline and candidate identities;
- source files, SHAs, package hashes, and versions;
- cohort, treatment, environment, evaluator, and run IDs;
- acceptance criteria and measured outcomes;
- cost, risk, maintenance, and uncertainty;
- decision, owner, validation evidence, and remaining work;
- successor experiment or terminal state.

Update the owning skill, SSOT, test fixture, or proposal only when the lesson is reusable and evidence-backed. Add regression tests for recurring failure modes.

### 10. REPEAT — continue while learning is useful

Repeat when new evidence changes the next best action. During asynchronous waits, perform independent, non-conflicting work and use the Adaptive Feedback Cycle.

Stop with one explicit terminal state:

- `success` — desired capability gain verified and adopted;
- `clean-no-op` — baseline already meets the objective;
- `blocked` — dependency or authority is unavailable;
- `approval-required` — a human-only authority edge is reached;
- `exhausted` — the declared experiment or resource envelope is consumed;
- `stagnated` — successive valid cycles yield zero meaningful improvement;
- `regression` — the candidate violates a required guardrail.

## Measurement contracts

### Quality-first objective

Use verified task outcome as the primary objective. Treat ATES, WTCV, TCV, TPV, RPI, action density, parallel yield, latency, and token counts as diagnostic or secondary dimensions according to their canonical definitions.

Classify throughput gains accompanied by lower correctness, weaker integration, higher repair rate, or reduced evidence quality as regressions or tradeoffs.

### Context and memory

- Measure retrieved context by task success, answer/evidence coverage, token count, retrieval latency, and maintenance cost.
- Compare selective filesystem memory with long-context approaches on equivalent task cohorts.
- Treat the Cost of Remembering LongMemEval figures (reported 97% fewer tokens and 95% lower cost at comparable accuracy) as source-specific research results. Reproduce locally before applying them as expected gains.
- Preserve source links, versioned files, selective loading, and one-way dependencies.

### Token and communication efficiency

- Count actual tokens with the target model's tokenizer when available.
- Include input, output, tool-call representation, repair/retry, and total episode tokens.
- Measure semantic fidelity, task quality, schema validity, ambiguity, and repair rate alongside tokens.
- Keep character count, byte count, token count, and message count as separate measures.
- Compare the same semantic content in the same conversational position and register.

The repository's Siglary census measured `o200k_base` and `cl100k_base` with `tiktoken 0.14.0`. In its A2A stamp, chords plus glyphs used 44 versus 32 tokens on `o200k_base` (+38%), despite fewer characters. Operators plus words used 32 versus 31 tokens for plain English. This supports tokenizer-specific measurement and operator precision; establish results for each target tokenizer independently.

Apply Siglary's class boundaries:

- **OPERATORS** carry formal logical or structural meaning.
- **GLYPHS** are pictographs from the issued set.
- **CHORDS** are letter codes resolved in a named Shorthand Domain.

Use the canonical Siglary Standard and Matrice for exact membership, register, and domain resolution. Keep `N∅` chat-only; machine records use schema nulls. Accuracy outranks compression.

### Zipf and adaptive vocabulary

- Use observed corpus frequency to identify candidate repeated terms and stable semantic units.
- Condition analysis on model, tokenizer, domain, task, author, audience, register, repository, and time where evidence permits.
- Use Zipf alpha as a distribution diagnostic; evaluate correctness through separate acceptance evidence.
- The linked `zipf_fork` study covers a Flask Python corpus of 885 files and approximately 19,541 keywords; its report says only the first few keywords follow the observed distribution. Use this as a repository-scoped research precedent.
- Select aliases or codebook entries using measured token/byte savings, ambiguity, decode risk, switch cost, and task quality.
- Require round-trip semantic recovery, output validity, and task-equivalence before adoption.
- Preserve canonical meaning in a stable representation; treat compressed renderings as reversible views.

### Agent, tool, and orchestration efficiency

- Use TDQS for tool-definition quality and ATES for execution observations.
- Compare manager policies on equivalent cohorts; attribute each run to evidenced agent/provider/model identity.
- Include duplicate work, conflicts, retries, useful versus duplicate tokens/actions, handoff latency, human intervention, and time-to-integration.
- Keep model/provider failures, admission failures, orchestration failures, environment failures, and code failures distinct.
- Use the canonical JSONL/receipt and experiment schemas as the evidence source.

## Skill self-maintenance

When improving this skill:

1. Capture the current `SKILL.md` SHA-256 and package SHA-256.
2. Identify the observed failure or opportunity and link its source evidence.
3. Make the smallest instruction change that addresses the cause.
4. Add a deterministic fixture or evaluation case when the behavior is testable.
5. Run the skill evaluator and relevant repository gates.
6. Re-fetch the source and package; verify that the archive contains exactly one UTF-8 `SKILL.md` and that its bytes equal the source file.
7. Record the new version, evidence, and remaining uncertainty.

## Related skills and documents

- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- `.agents/skills/adaptive-wait/SKILL.md`
- `.agents/skills/review-loop/SKILL.md`
- `.agents/skills/skill-evaluation/SKILL.md`
- `.agents/skills/context-relationship-graph/SKILL.md`
- `.agents/skills/multivariate-doe/SKILL.md`
- `.agents/skills/siglary-a2a/SKILL.md`
- `docs/ops/CONTINUOUS-IMPROVEMENT-POLICY.md`
- `docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md`
- `docs/ops/AGENT-THROUGHPUT-METRICS.md`
- `docs/proposals/active/notation-sets/SIGLARY-STANDARD.md`








































































































































































































