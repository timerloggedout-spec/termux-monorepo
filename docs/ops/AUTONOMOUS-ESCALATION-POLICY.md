# Autonomous Escalation Policy Contract

**Status:** normative P1 contract for the autonomous-escalation treatment  
**Schemas:** [ESCALATION-PACKET.schema.json](./ESCALATION-PACKET.schema.json), [ESCALATION-DECISION.schema.json](./ESCALATION-DECISION.schema.json)

## Invariants
1. Escalation changes executor, capability, strategy, or scrutiny; it never changes authorization.
2. Every handoff uses a versioned packet. Evidence is referenced by stable IDs; raw prompts, completions, credentials, tokens, browser profiles, and checkpoint payloads are excluded.
3. The manager resolves candidates from the current roster, capability metadata, concrete adapter availability, permission scope, provider health, and quota. A roster declaration alone is not callable proof.
4. Route selection, dispatch, invocation, completion, verification, and promotion are distinct events. Never infer one from another.
5. The same executor + same strategy + same input after the same normalized failure is not a valid retry. A retry requires a transient classification and a changed condition/backoff.
6. Each escalation consumes its own budget. No unbounded retries, cycles, or parallel duplicate side effects.
7. A policy denial is terminal for that action (BLOCKED_PERMISSION); changing executor cannot bypass it. Missing an eligible adapter is BLOCKED_CAPABILITY.
8. Containment is branch-scoped where possible. Unrelated safe work continues; unsafe work is quarantined.
9. Independent verification evaluates evidence and acceptance criteria. It cannot grant permission, alter policy, or self-certify success.
10. If all safe routes are exhausted, return a typed terminal state and preserve verified partial results.

## Reason taxonomy
| Code | Meaning | Required response |
|---|---|---|
| CAPABILITY_MISMATCH | No suitable capability on current executor | Resolve eligible specialist or BLOCKED_CAPABILITY |
| TOOL_FAILURE | Adapter/tool returned normalized failure | Repair or alternate adapter; bounded transient retry only |
| STAGNATION | No accepted progress/evidence delta | Local repair, then specialist or manager replan |
| CONTRADICTION | Material disagreement among results | Manager arbitration; independent verification for consequential claims |
| VERIFIER_REJECTION | Acceptance test or verifier rejected output | Route exact failing evidence to responsible capability |
| CONTEXT_SATURATION | Context loss/truncation or unstable state | Build minimal provenance-preserving packet and clean specialist context |
| PROVIDER_DEGRADATION | Outage, rate limit, quota or latency degradation | Cooldown and re-resolve eligible candidates |
| SECURITY_ANOMALY | Injection, exfiltration attempt, policy mismatch | Contain affected branch and invoke independent security lane |
| RESOURCE_PRESSURE | Deadline or cost budget threatens useful completion | Re-plan, narrow scope, or return verified partial result |
| ESCALATION_CYCLE | Route repeats without new evidence or executor/strategy change | Exclude cycle and arbitrate or terminate |
| HIGH_IMPACT_RESULT | Consequential output requires independent challenge | Route to a distinct eligible verifier with independent-verification capability; otherwise do not certify success |

## Deterministic decision order
1. Validate task identity, immutable source revision, acceptance criteria, packet schema, and expiry.
2. Enforce policy preflight before any dispatch. A denial cannot be repaired by routing.
3. Classify the failure using observable evidence; self-reported confidence is advisory only.
4. Check the relevant counter and total budget before selecting a transition.
5. Reject a candidate if capability, adapter, credential, permission, health, quota, or attribution requirements are unmet.
6. Prefer a materially different executor or strategy after a repeated failure; require evidence for every repeat.
7. Use manager arbitration for conflicting outputs or coordination deadlock.
8. Require independent verification for high-impact results and promotion candidates.
9. Record a typed decision and evidence references; do not claim execution from route selection.
10. If no safe candidate remains, emit a terminal classification and continue unrelated safe branches.

## Terminal-state semantics
- TASK_PASS: all required acceptance criteria independently verified.
- TASK_FAIL: task completed unsuccessfully with evidence.
- BLOCKED_CAPABILITY: no eligible callable adapter/capability exists.
- BLOCKED_PERMISSION: policy or tool boundary denies the requested action.
- STAGNATED: bounded recovery produced no accepted progress.
- BUDGET_EXHAUSTED: relevant retry/escalation/resource budget depleted.
- QUARANTINED: affected branch isolated due to security or integrity risk.
- UNKNOWN: evidence is insufficient to classify; never treated as success.

## Compatibility and rollout
- Preserve native orchestration IDs and receipts. Do not add graph-node events to the closed throughput schema without a versioned schema change and privacy tests.
- The packet is a handoff contract, not a canonical execution log or checkpoint format.
- Temporal remains the candidate owner for distributed durable execution; do not duplicate durable history in a second checkpointer without a tested ownership boundary.
- Initial numerical limits belong in policy configuration and fixtures, not graph nodes. Calibrate production thresholds from measured cohort evidence.
- This contract specifies behavior only. Runtime integration remains a separate implementation phase and must pass deterministic tests before provider/model wiring.
