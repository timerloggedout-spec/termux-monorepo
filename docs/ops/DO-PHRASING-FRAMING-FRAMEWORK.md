# DO Phrasing and Framing Framework

**Status:** proposed repository-wide writing and task-intake standard  
**Scope:** phrasing substantial requests, prompts, issues, briefs, handoffs, and acceptance criteria  
**Authority boundary:** this is a writing/specification layer. It does not replace execution workflows, approval rules, evaluation contracts, or source-of-truth documents.

## 1. Purpose

Turn an idea or request into a clear, actionable, bounded, verifiable work instruction without losing the requester's intent.

Use **DO** as a descriptive label for **direct, action-first phrasing** unless an authoritative origin definition is supplied. Do not invent an acronym expansion or present this guide as an external standard.

The guide should answer: **What should be done, to what, toward which outcome, within what boundaries, and how will we know?**

## 2. The core pattern

`ACTION + TARGET + OUTCOME + SCOPE + CONSTRAINTS + ACCEPTANCE EVIDENCE + STOP / ESCALATION`

Not every small request needs seven explicitly labeled fields. Include every field that materially affects correctness, safety, execution, or handoff. Preserve unknowns as unknown; do not fill gaps with invented facts.

| Field | Question | Example |
|---|---|---|
| **Action** | What should happen? | Inspect, compare, implement, test, document, reconcile |
| **Target** | What system, artifact, behavior, or question? | Provider adapter and contract tests |
| **Outcome** | What should be true afterward? | Malformed responses fail closed without losing valid records |
| **Scope** | Where may work occur? | Named files, branch, issue, bounded research domain |
| **Constraints** | What must remain true or not happen? | Do not expose secrets or change unrelated APIs |
| **Acceptance evidence** | What will demonstrate the outcome? | Focused tests, regression tests, inspected diff, observed run evidence |
| **Stop / escalation** | When must work pause or be escalated? | Ambiguous ownership, destructive scope, missing authority, unresolved safety conflict |

## 3. Writing rules

- Use **MUST / MUST NOT** for mandatory contracts and safety boundaries; **SHOULD / SHOULD NOT** for strong defaults with justified exceptions; **MAY** for optional behavior.
- Start substantial requests with an observable action, not only a topic or aspiration.
- Decompose phrases such as “make it better,” “do everything,” “upgrade,” “continue,” and “production-ready” into outcomes, boundaries, and evidence.
- Preserve the ambition of the request while bounding execution to granted authority and available evidence.
- Separate **fact**, **observation**, **assumption**, **hypothesis**, **recommendation**, **implementation**, and **verified outcome**.
- A recommendation is not authorization. A plan is not implementation. A commit is not runtime proof. Missing evidence is **unknown**, not success.
- Link canonical process contracts instead of copying their rules into every prompt.

## 4. Reusable patterns

### Implement or repair

> **Implement** [behavior] in [bounded scope]. Preserve [invariants]. Add or update tests for [expected behavior and failure cases]. Run [available checks] and report exact evidence, changed paths, remaining risks, and what was not verified. Stop if work crosses scope or an approval boundary.

### Research and find gaps

> **Research** [question/system] using [primary sources]. **Compare** observed state with [baseline/contract]. Separate confirmed facts, assumptions, contradictions, and missing evidence. Rank gaps by impact and dependency. Recommend bounded actions with acceptance evidence and stop conditions. Do not claim implementation from research alone.

### Review or audit

> **Review** [artifact/change] against [requirements]. Classify findings by severity and cite paths/lines or evidence. For each finding, state impact, reproduction/evidence, correction, and regression test. Do not label a finding fixed until the corrected state is re-fetched and verified.

### Documentation change

> **Update** [canonical document] to reflect [verified change]. Preserve terminology and source-of-truth boundaries. Link related contracts instead of duplicating them. Distinguish proposed, implemented, executed, validated, and promoted states. Check links and consistency.

### Continue / maintain

> **Re-fetch** current authoritative state. **Compare** it with the last known baseline. Choose the highest-value in-scope action with satisfied dependencies. Act on a bounded change, verify it, record evidence and unresolved gaps, then repeat while useful progress remains. During waits, do independent non-conflicting work. Stop on stagnation, missing authority, unresolved conflict, or an approval gate.

## 5. Adapt framing to the work

| Work type | Framing emphasis |
|---|---|
| Bug fix | Expected vs observed behavior, reproduction, regression boundary, tests |
| Feature | User-visible outcome, API/data contracts, scope, acceptance scenarios |
| Research | Question, source quality/date/version, uncertainty, gap ranking |
| Security | Threat model, trust boundary, safe reproduction, remediation evidence |
| Operations | Current state, immutable run/ref identity, expected effect, watcher, recovery boundary |
| Documentation | Canonical source, intended readers, terminology, links, consistency |
| Multi-agent work | Owner, file/resource claims, dependencies, handoff, integration owner |
| Evaluation | Baseline, cohort/treatment, repeatability, outcome, missing data, attribution |
| Release/promotion | Required approvals, current SHA, review state, checks, rollback/recovery |

These are request-writing hints, not replacements for the relevant operational or technical contracts.

## 6. Keep adjacent systems in their own lanes

This guide owns **how work is expressed**. It does not own:
- execution scheduling, adaptive waits, workflow retries, or production reconciliation;
- telemetry/evidence storage, provenance schemas, or outcome ledgers;
- agent performance psychology, reward design, or evaluation methodology;
- architecture decision authority, review gates, release promotion, or deployment policy.

Use the existing contracts for those concerns:
- [Adaptive Feedback Cycle](../../.agents/skills/adaptive-feedback-cycle/SKILL.md)
- [Adaptive Wait](../../.agents/skills/adaptive-wait/SKILL.md)
- [Gemini Performance Psychology](../../.agents/skills/gemini-performance-psychology/SKILL.md)
- [Production Reconciliation](../../.github/skills/production-reconciliation/SKILL.md)
- [Agent Evaluation Framework](../architecture/AGENT-EVALUATION-FRAMEWORK.md)
- [Agent Team Orchestration](AGENT-TEAM-ORCHESTRATION.md)
- [Agentic-Agile Process Integration](AGENTIC-AGILE-PROCESS-INTEGRATION.md)
- [BIUDL Execution and Provenance](BIUDL-EXECUTION-AND-PROVENANCE.md)

For a concise explanation of how phrasing, decision cycles, execution lifecycle, and outcome learning relate, see [DO Framing and Feedback Architecture](DO-FRAMING-AND-FEEDBACK-ARCHITECTURE.md).

## 7. Adoption

1. Use this guide for new substantial requests, issues, briefs, and agent handoffs.
2. Improve existing prompts when touched; avoid noisy mass rewrites without measurable benefit.
3. Do not add automated enforcement until representative examples, exceptions, and false-positive behavior are tested.
4. Revisit this guide if an authoritative origin definition for “DO” is supplied or evidence shows the structure is too heavy for a request class.

## 8. Quick checklist

- [ ] Starts with a clear action.
- [ ] Names the target and intended outcome.
- [ ] Bounds scope and relevant dependencies/owners.
- [ ] States important invariants and prohibited actions.
- [ ] Defines acceptance evidence and verification conditions.
- [ ] Distinguishes fact, inference, and unknown.
- [ ] Names stop, escalation, and approval conditions.
- [ ] Says how results and unresolved work will be recorded.
