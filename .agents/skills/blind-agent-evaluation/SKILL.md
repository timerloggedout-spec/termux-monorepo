---
name: blind-agent-evaluation
description: Design and operate blinded or partially blinded comparisons of agent, skill, model, prompt, tool, and orchestration treatments while preserving protected provenance and correctness-first evaluation.
---

# Blind Agent Evaluation

## Purpose

Reduce evaluator bias when provider, model, skill, tool, or manager identity could influence judgment. This is a **blinded evaluation control**, not a guarantee of perfect statistical blindness.

Use with `.agents/skills/approxination-lane/SKILL.md` for substantive skill competitions and with `.agents/skills/multivariate-doe/SKILL.md` for controlled multi-factor designs.

## Required procedure

1. Define the decision, estimand, task cohort, acceptance criteria, safety constraints, and primary outcome before execution.
2. Identify the incumbent and competing treatments. For substantive skill creation/upgrades, use incumbent, sourced candidate, and independent candidate when feasible.
3. Assign opaque treatment IDs before evaluation. Store the treatment-to-identity mapping separately from evaluator-visible artifacts.
4. Remove unnecessary provider/model/vendor/skill/reputation metadata from evaluator-visible outputs. Normalize formatting only when it does not erase meaningful differences.
5. Execute each treatment under matched task, solver, environment, permissions, and output contract where possible.
6. Freeze raw evidence and hashes before judging or unblinding.
7. Run deterministic checks first: tests, schema validation, exact output assertions, security checks, and task-specific oracles.
8. Evaluate correctness and task completion before completeness, grounding, tool-use appropriateness, regressions, and efficiency.
9. Record missingness, failures, timeouts, quota/cooldown, execution non-admission, evaluator disagreement, and identity leakage.
10. Unblind only after the evaluation is frozen, unless safety/debugging requires earlier access; record the exception.
11. Compare per-task and per-category outcomes; use pairwise preference/ELO as one view, not the sole selection rule.
12. Replicate promising candidates on held-out or fresh tasks before recommending adoption.
13. Feed verified findings into AEF, MoneyBall/3L0, and BIUDL with source and cohort provenance.

## Approxination competition contract

The Approxination Benchmark's A/B/C/D labels describe tool-layer modes, not candidate skill versions. Preserve both dimensions separately:

- **Tool mode:** A cold/no-tools baseline; B Approx CLI + Brave; C skills.sh + Brave; D Brave-only.
- **Skill treatment:** incumbent, sourced/adapted candidate, independent candidate, and any justified additional arms.

Do not assume every skill comparison needs all four tool modes. Choose a design that isolates the actual question and record why.

## Blinding limits

- Do not call a trial double-blind if identity is inferable from output style, citations, tool traces, or unique behavior.
- Prefer partial blindness with explicit leakage notes over unsafe removal of operational metadata.
- Preserve attribution securely; never erase source identity from the authoritative evidence record.
- Evaluators must not see treatment rankings, brand reputation, stars, popularity, or prior ELO when scoring correctness.
- Keep judge model/version, prompt, rubric, and temperature/settings fixed within a cohort.
- If multiple judges are used, report agreement and adjudication separately.

## Outcome and ranking rules

Primary outcomes:
- independently verified task correctness;
- task completion and required deliverables;
- safety/policy compliance and regression severity.

Secondary outcomes:
- completeness, evidence grounding, tool-use appropriateness;
- integration quality and maintainability;
- latency, tokens, tool calls, retries, cost, and human intervention.

A failed admission is not a model failure. A provider outage is not a skill failure. A successful HTTP call or workflow is not task success. A fast incorrect answer cannot outrank a slower verified correct answer.

Report:
- sample size and task coverage;
- per-task and per-category results;
- pairwise wins/losses/ties;
- ELO or other ranking with uncertainty/limitations;
- missing/skipped/censored observations;
- evaluator disagreement and leakage;
- replication result and decision.

No winner is declared from a single aggregate score when primary correctness or safety evidence is missing.

## Multi-agent coordination

Scouts propose candidate treatments. Managers assign treatments under the approved design. Execution telemetry records actual runs. Blinded evaluators assess frozen evidence. Protected provenance enables unblinding. MoneyBall/3L0 consumes the evidence after the evaluation boundary.

## Continuous improvement

Every use can produce a retrospective: leakage, evaluator disagreement, selection imbalance, task contamination, unbalanced order, replication failure, or regression. Update the next cohort or skill version without rewriting prior evidence.
