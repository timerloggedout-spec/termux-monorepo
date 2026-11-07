# Competitive Orchestration Lab — LangGraph BIUDL

## Purpose

Compare orchestration approaches as replaceable treatments, then combine independently validated patterns. The lab is not a framework popularity contest and does not authorize a production routing change by itself.

## Treatment portfolio

| Treatment | Primary hypothesis | Strengths to test | Failure modes / costs |
|---|---|---|---|
| Native manager (control) | Existing policy and adapters provide the best baseline | Lowest integration cost, current governance, existing receipts | Routing complexity, hidden coupling, weak graph introspection |
| LangGraph | Explicit graph state and transitions improve complex workflows | Branching, fan-out, checkpointing, interrupt/resume, subgraphs | Dependency/runtime footprint, state leakage, checkpoint complexity |
| Deep Agents | Higher-level harness reduces agent-loop implementation effort | Planning, filesystem context, subagents, skills, memory | Excess abstraction, token/cost overhead, reduced control |
| Swarm / handoff | Peer or specialist handoffs improve parallel expertise | Specialization, delegation, task decomposition | Coordination overhead, loops, ownership ambiguity |
| Supervisor / tool-routed | Central supervisor improves task allocation | Central policy, tool routing, bounded delegation | Bottleneck, supervisor bias, archived package risk |
| Hybrid | Best-fit components outperform any single treatment | Graph control + native policy + specialized harness + durable execution | Integration complexity, duplicate state, unclear authority |

Candidate rows describe patterns, not endorsements. Archived packages remain reference-only; candidate frameworks must pass current maintenance, license, security, and dependency review before execution.

## Benchmark corpus

Use the same immutable task fixtures and acceptance tests across treatments. Start with a small, representative set:

1. **Deterministic tool workflow:** typed inputs, bounded tool call, structured result.
2. **Branching triage:** classify evidence, select a lane, route to a deterministic verifier.
3. **Parallel research:** independent source collection, deduplication, synthesis, citation checks.
4. **Human approval:** pause before a consequential side effect, resume on the same run identity, prove idempotency.
5. **Long-running recovery:** simulate worker interruption, resume from a checkpoint or durable workflow, verify no duplicate effect.
6. **Repository change:** inspect, plan, patch, run tests, produce evidence, stop before merge.
7. **Adversarial input:** prompt injection, malformed tool output, permission escalation attempt, data-exfiltration bait.

Every task has a fixed fixture, expected artifacts, deterministic verifier, side-effect budget, timeout, and explicit stop condition. Never use production secrets or uncontrolled external side effects in the benchmark corpus.

## Measurement contract

Record run-level measurements through existing orchestration treatment and receipt contracts. Use existing OTEL/ATES only where event semantics match. Do not encode graph nodes as tools or put prompts, completions, tool arguments, checkpoint blobs, or private state into telemetry.

Minimum measures:

- **Quality:** verifier pass rate, requirement coverage, factual/citation accuracy where applicable.
- **Reliability:** completion rate, retry rate, recovery success, duplicate-side-effect count.
- **Efficiency:** wall-clock time, model/tool calls, token usage, compute/runtime cost.
- **Governance:** policy violations, approval bypasses, unauthorized effects, evidence completeness.
- **Operability:** setup burden, dependency footprint, observability coverage, reproducibility.
- **Maintainability:** code surface, failure localization, upgrade burden, operator comprehension.

Report distributions and confidence intervals where sample size permits; never rank on one aggregate score alone. Hard safety or governance failures disqualify a treatment regardless of speed or quality score.

## Experiment protocol

1. Freeze task corpus, verifier versions, model/provider configuration, tool permissions, resource budgets, and source SHA.
2. Define one treatment variable at a time; keep all other conditions equivalent.
3. Run baseline and candidate on the same fixtures. Randomize execution order where practical.
4. Repeat enough runs to expose variance; report sample size and missing runs.
5. Separate deterministic harness failures from model variance and external-service failures.
6. Preserve sanitized run receipts, source/config hashes, verifier output, and failure classifications.
7. Review failures blind to framework where practical; record the evidence and reviewer rationale.
8. Repeat after each material improvement; compare against both the prior candidate and native control.

No promotion from a single successful demo. Do not compare treatments with different task difficulty, permissions, model budgets, or acceptance criteria.

## Pattern extraction and recombination

After each comparison, classify patterns as:

- **Keep:** independently validated improvement with no material regression.
- **Adapt:** promising concept requiring a repository-native implementation or stronger boundary.
- **Combine:** two or more validated patterns with compatible state/authority boundaries.
- **Defer:** insufficient evidence, incomplete test coverage, or unresolved dependency/security risk.
- **Reject:** repeatable regression, unsafe behavior, unacceptable cost, or unmaintained upstream.

For every adopted pattern, preserve source attribution, local adaptation rationale, benchmark evidence, owner, rollback route, and upgrade watch. Do not import entire frameworks merely to obtain one useful pattern.

## Hybrid architecture guardrails

- Native manager retains policy and treatment selection authority.
- LangGraph may own graph-local control flow; it does not grant permissions.
- Deep Agents may be evaluated as a harness inside a bounded treatment.
- Temporal remains the durable cross-worker execution layer when required.
- Provider and MCP adapters retain credentials, allowlists, and tool authorization.
- GitHub remains the source of truth for code, PRs, checks, and workflow runs.
- OTEL/ATES/evidence receipts remain the canonical sanitized measurement plane.
- Human approval remains external to agent self-assertion and graph state.
- A treatment cannot approve, score, or promote itself.

## Promotion rule

Promote a treatment or hybrid only when it:

1. Passes all hard safety, privacy, authorization, and deterministic correctness gates.
2. Meets or exceeds the native control on task quality and evidence completeness.
3. Shows a material, repeatable benefit in at least one declared objective (reliability, latency, cost, capability, or maintainability).
4. Has no unexplained material regression in other dimensions.
5. Has reproducible results, a rollback path, and current-SHA repository/Termux validation.

If results are inconclusive, retain the native control and continue measurement. A failed or inconclusive candidate is useful evidence, not wasted work.

## Work items

- **LGB-009:** implement and maintain this treatment portfolio, task corpus, metrics, and decision ledger.
- **LGB-010:** design and test hybrid compositions from validated patterns; add no production routing change until promotion criteria pass.
