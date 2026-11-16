# DO Phrasing and Framing Framework

**Status:** proposed repository-wide writing and task-intake standard  
**Scope:** user requests, agent prompts, work briefs, issues, PR descriptions, research tasks, operational handoffs, and retrospectives  
**Authority boundary:** this is a phrasing layer. It does not replace the dependency-phase engine, schemas, approval rules, review gates, or source-of-truth documents.

## 1. Discovery and terminology

A search of the repository's canonical documentation found strong adjacent contracts for work-unit specification, evidence, ownership, evaluation, and lifecycle control, but did not establish a canonical expansion or prior definition for the exact named **“DO Phrasing Framing Framework.”**

Until an authoritative definition is supplied, use **DO** as a descriptive label for **direct, action-first phrasing**. Do not invent an acronym expansion or imply that this document is an already-adopted external standard. If the originator supplies a source definition, reconcile this document against it and preserve the source terminology.

## 2. Core rule

Frame work as an observable action with an intended result—not merely a topic, aspiration, or open-ended command.

**Canonical structure**

`ACTION + TARGET + OUTCOME + SCOPE + CONSTRAINTS + ACCEPTANCE EVIDENCE + STOP / ESCALATION`

Not every small request needs every field written out. Include all fields that materially affect safe execution, correctness, or handoff. Unknown values must remain explicitly unknown rather than being fabricated.

### Field definitions

| Field | Question it answers | Example |
|---|---|---|
| Action | What must the agent do? | Inspect, compare, implement, test, document, reconcile |
| Target | Which system, files, behavior, or question? | The provider adapter and its contract tests |
| Outcome | What should be true afterward? | Malformed responses fail closed without losing valid records |
| Scope | Where may work occur? | Named paths, branch, issue, bounded research domain |
| Constraints | What must not happen? | Do not expose secrets or change unrelated APIs |
| Acceptance evidence | How will success be demonstrated? | Focused tests, regression tests, diff inspection, observed workflow evidence |
| Stop / escalation | When must the agent stop or ask? | Stop on ambiguous ownership, destructive changes, missing authority, or unresolved safety conflict |

## 3. Normative language

Use **MUST / MUST NOT** for mandatory contracts and safety boundaries, **SHOULD / SHOULD NOT** for strong defaults that may have justified exceptions, and **MAY** for optional behavior.

Avoid vague requirements such as “make it better,” “fully fix,” “do everything,” “ensure quality,” or “production-ready” unless they are decomposed into observable deliverables and acceptance evidence. Preserve the user's ambition, but translate it into bounded, verifiable work rather than silently narrowing it or treating it as unlimited authority.

## 4. Reusable DO patterns

### A. Implement or repair

> **Implement** [specific behavior] in [bounded scope]. Preserve [invariants]. Add or update tests for [expected behavior and failure cases]. Run [available checks] and report the exact evidence, changed paths, remaining risks, and anything not verified. Stop and explain if the change crosses the stated scope or an approval boundary.

### B. Research and find gaps

> **Research** [question/system] using [primary sources or specified evidence]. **Compare** observed state against [contract/baseline]. **Identify** confirmed facts, assumptions, contradictions, and missing evidence separately. **Rank** gaps by impact, likelihood, and dependency. Recommend the smallest high-value next actions, each with an owner or lane, acceptance evidence, and stop condition. Do not claim implementation from research alone.

### C. Review or audit

> **Review** [artifact/change] against [named requirements]. Check correctness, security/privacy, compatibility, tests, documentation, scope, provenance, and operational failure modes as applicable. Classify findings by severity and cite the affected path/line or evidence. For each finding, state the impact, reproduction/evidence, recommended correction, and regression test. Do not label a finding fixed until the corrected state is re-fetched and verified.

### D. Documentation update

> **Update** [canonical document] to reflect [verified change]. Preserve established terminology and source-of-truth boundaries. Link related contracts instead of duplicating them. Mark proposed, implemented, executed, validated, and promoted states separately. Verify links, examples, navigation, and consistency with the authoritative implementation.

### E. Maintain and continue

> **Re-fetch** current authoritative state. **Compare** it with the last known baseline. **Choose** the highest-value in-scope action whose dependencies are satisfied. **Act** on a bounded change, **verify** it, **record** evidence and unresolved gaps, then **repeat** while useful progress remains. During waits, do independent non-conflicting work. Stop on stagnation, missing authority, unresolved conflict, or an approval gate.

### F. Decision or recommendation

> **Decide** [specific question] using [criteria and evidence]. Separate facts from inference, compare feasible options, identify trade-offs and reversibility, and state the chosen option plus why. Name the evidence that would change the decision. Do not imply that a recommendation is authorization to execute it.

## 5. Frame by work type

| Work type | Required framing emphasis |
|---|---|
| Bug fix | Expected vs observed behavior, reproduction, regression boundary, tests |
| Feature | User-visible outcome, API/data contracts, scope, acceptance scenarios |
| Research | Question, source quality, date/version, uncertainty, gap ranking |
| Security | Threat model, trust boundary, exploitability, safe reproduction, remediation evidence |
| Operations | Current state, immutable run/ref identity, expected effect, watcher, recovery boundary |
| Documentation | Canonical source, intended readers, terminology, links, consistency checks |
| Multi-agent work | Work-unit ownership, file/resource claims, dependencies, handoff format, integration owner |
| Evaluation | Frozen baseline, cohort/treatment, repeatability, outcome, missing data, attribution |
| Release/promotion | Required approvals, current SHA, review state, checks, rollback/recovery plan |

## 6. Required evidence and state discipline

The phrasing framework must honor the repository's existing lifecycle distinctions:

- A plan is not an implementation.
- A commit is not execution evidence.
- A queued or running workflow is not success.
- A successful workflow is not automatically proof of the intended effect.
- A resolved inline review thread is not a formal review approval.
- A recommendation is not authorization.
- Missing evidence is unknown, not zero and not success.
- A failure or cancellation is retained as an observation, not rewritten as success.

For operational work, use the canonical repository loop:

`RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT`

Do not create a parallel lifecycle engine, telemetry store, or competing source of truth to implement this writing standard.

## 7. Gap findings from the documentation review

### Existing strengths

1. Agentic-Agile already defines bounded work units, dependencies, ownership, acceptance evidence, and review gates.
2. The Agent Evaluation Framework separates task outcome from latency and other operational signals.
3. Production Reconciliation requires fresh runtime observation, re-fetch, comparison, classification, and recording.
4. BIUDL execution/provenance rules distinguish observed identity from inferred attribution and protect sensitive context.

### Gaps this standard addresses

1. **No discovered canonical DO definition:** terminology/origin remains unresolved; this document does not fabricate it.
2. **Prompt composition is distributed:** good requirements exist across several contracts but no compact, reusable action-first writing guide was found in the searched canonical docs.
3. **Broad commands can remain underspecified:** “everything,” “upgrade,” “continue,” and “production-ready” need explicit outcome, boundaries, evidence, and stop conditions.
4. **Research and execution can blur:** requests should explicitly separate finding a gap, proposing a change, implementing it, and proving its effect.
5. **Acceptance evidence can be implicit:** each substantial request should say how the result will be checked.
6. **Maintenance can become status narration:** “continue” should trigger fresh-state reconciliation and a useful bounded action, not unsupported progress claims or idle waiting.

### Not claimed

This documentation review does not prove that every prompt, issue, skill, workflow, or branch uses the new structure. Repository-wide adoption requires a separate inventory, targeted integrations, and tests or review criteria where machine enforcement is justified.

## 8. Adoption and maintenance

1. Use this guide when drafting new substantial work requests, issues, task briefs, and agent handoffs.
2. Prefer links to canonical contracts over copied policy text.
3. For existing prompts, upgrade them when touched; avoid a noisy mass rewrite without a measurable benefit.
4. During retrospectives, classify recurring ambiguity as a specification gap and improve the relevant template, skill, validator, or test.
5. Revisit this guide when the originating definition of “DO” is provided, the repository's canonical phase contract changes, or evidence shows this structure is too heavy for a class of tasks.
6. Do not add automated enforcement until examples, exceptions, and false-positive behavior are tested.

## 9. Quick checklist

Before handing off a substantial task, confirm:

- [ ] Starts with a clear action verb.
- [ ] Names the target and intended outcome.
- [ ] Bounds scope and identifies relevant dependencies/owners.
- [ ] States important invariants and prohibited actions.
- [ ] Defines acceptance evidence and verification conditions.
- [ ] Distinguishes fact, inference, and unknown.
- [ ] Names stop, escalation, and approval conditions.
- [ ] Specifies how results and unresolved work will be recorded.

## Related canonical contracts

- [Agent Evaluation Framework](../architecture/AGENT-EVALUATION-FRAMEWORK.md)
- [Agent Team Orchestration](AGENT-TEAM-ORCHESTRATION.md)
- [Agentic-Agile Process Integration](AGENTIC-AGILE-PROCESS-INTEGRATION.md)
- [BIUDL Execution and Provenance](BIUDL-EXECUTION-AND-PROVENANCE.md)
- [Production Reconciliation Skill](../../.github/skills/production-reconciliation/SKILL.md)
- [Collaborator entry](../../SKILLS.md)
