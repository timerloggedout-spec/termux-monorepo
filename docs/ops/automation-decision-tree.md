# Autonomous Development Automation Decision Tree

**Status:** Source-controlled operational map.
**Scope:** Current default-branch control plane, captured by the generated workflow catalog.
**Purpose:** Explain how GitHub-native automation decides **what runs**, **who or what may act**, **what waits**, **when a route stops**, and **how autonomous mutations are reviewed and reversed**.

> **Interpretation rule.** Issue bodies, pull-request text, comments, review text, provider output, and external API responses are inputs to bounded logic. They are not executable instructions, permission grants, branch names, shell commands, or rollback references.

The live inventory is maintained in the [generated workflow catalog](generated/automation-workflow-catalog.md). The companion JSON is intentionally machine-readable and is validated by `scripts/ci/automation_docs.py`.

## Reading the map

| Visual lane | Meaning | Typical outcomes |
|---|---|---|
| Blue | Event, decision, or routing context. | Select a supported lifecycle route or ignore an irrelevant event. |
| Green | Read-only, advisory, or successful bounded state. | Check, artifact, summary, catalog, or reviewable evidence. |
| Amber | Guard, trust, budget, cooldown, concurrency, or policy decision. | Continue, wait, defer, or stop. |
| Red | Attributable fixed-scope mutation. | Fixed-path reconciliation, bounded collaboration state, rollback, or writer freeze. |
| Purple | External/provider state or bounded pending state. | Provider invocation, current-SHA evidence, cache, cooldown, or opt-in peer route. |
| Gray | Rejection, skip, circuit-breaker, or separately accepted capability. | No mutation, explicit no-route, escalation, or policy hold. |

## 1. Full autonomous automation overview

![Repository automation overview](generated/automation-overview.png)

The overview separates entry events from the repository’s major automation lanes: lifecycle and validation work, agentic task routes, peer/provider review, model routing, governance/reconciliation, and scheduled operations. It deliberately treats a successful API call as insufficient proof for a writer lane: a writer must pass postcondition verification or enter bounded recovery.

The catalog currently records every registered top-level workflow and assigns each to one of five readable domains. The overview is intentionally layered; the detailed trees below expose the exact gates rather than encoding the entire repository in a single unreadable graph.

## 2. Issue and pull-request lifecycle decision tree

![Issue and pull-request decision tree](generated/issue-pr-decision-tree.png)

The lifecycle route is selected by event type, supported context, and trust. Pull-request work distinguishes same-repository and eligible lifecycle events from drafts, forks, and irrelevant paths. Issue/comment work separates trusted association and explicit supported trigger checks from untrusted content, which remains data. Provider evidence can only advance the orchestrator when it is provider-bound, cycle-bound, and current-SHA-bound.

| Event class | Primary gate | Safe terminal states |
|---|---|---|
| Pull request / review | Supported action, repository context, draft/path state. | Gate result, advisory check, reviewable provider state, or no-op. |
| Issue / comment | Trusted actor association and accepted trigger/marker. | Bounded triage, agent request, diagnostic state, or rejection. |
| Provider evidence | Exact provider, cycle, and current head SHA. | Completion, pending state, or status-only stale evidence. |
| Schedule / dispatch | Allowlisted inputs and capability charter. | Read-only report, bounded dispatch, fixed-scope reconciliation, or fail-closed state. |

## 3. Provider availability, 3L0 routing, quota, and cooldown

![Model availability and 3L0 routing](generated/model-routing-3l0.png)

The current router implements **Gemini primary** selection for the requested role and evaluates secondary peers only after the appropriate primary budget is exhausted. It uses the local 3L0/ELO-like model-success matrix together with role suitability. OpenRouter availability is not assumed: the router uses a one-hour model-catalog cache, attempts a bounded live catalog poll when necessary, falls back to a stale cache when available, and finally permits only the proven legacy allowlist. Only free-model candidates that satisfy the selected catalog/allowlist rule can be ranked and budget-checked.[1] [2]

Omni/OmniRoute remains a guarded code path but is **temporarily decommissioned operationally**. The diagram therefore shows it as a policy-gated path, not as an active fallback. If all eligible free routes are exhausted, the router emits an explicit no-route/skip outcome rather than claiming a false fallback.[1]

| State | Evidence source | Route behavior |
|---|---|---|
| Configured | Secret-presence preflight and policy/configuration. | May be considered only if the provider branch is enabled. |
| Catalog current | OpenRouter live result or cache younger than one hour. | Free candidates must appear in the observed catalog. |
| Catalog stale | Last successful cache remains available after a poll failure. | Can be used with a warning; no silent widening occurs. |
| Catalog unavailable | No fresh/stale catalog. | Only the proven legacy free allowlist is eligible. |
| Quota limited | Per-provider/model role counter meets the soft ceiling. | Candidate is skipped and the router tries only declared alternatives. |
| No eligible route | Every accepted candidate fails availability or budget gates. | Explicit bounded skip with a reason. |

### 3L0 leaderboard and routing interpretation

![3L0 leaderboard data lineage](generated/leaderboard-data-lineage.png)

The repository’s 3L0 matrix is a **local performance label** for role-aware routing; public leaderboard sources are contextual model features and are not sole routing authority. The policy constrains production fallback to free-tier candidates and explicitly identifies direct, mixed, and deferred randomized selection modes.[3] The diagrams therefore distinguish three different concepts that are often conflated:

| Input type | Function | Authority |
|---|---|---|
| Public model boards | Contextual feature/reference signal. | Never sufficient alone to select a production route. |
| Local 3L0/ELO and role suitability | Ranking input for the repository’s own workload categories. | Bounded selection input after availability and budget gates. |
| Live availability and counters | Operational eligibility, cache/cooldown, and quota evidence. | May reject a higher-ranked model; never invent a route. |

## 4. Peer-provider review orchestration

![Peer-provider review decision tree](generated/peer-provider-review.png)

AR-15 establishes CodeRabbit as the verified default provider. Qodo and Devin are explicit policy opt-ins. The orchestrator coalesces superseded PR events, preserves current-SHA evidence requirements, and publishes incomplete provider evidence as **advisory** unless the explicit enforcement variable is enabled.[4]

This distinction prevents routine provider latency from appearing as a workflow defect while still retaining a deliberate required-completion mode for future branch-protection policy. Operator markers are exact and authorized; nonmatching or stale comments remain status-only and cannot complete a current review cycle.

## 5. Autonomous-writer authority and rollback

![Autonomous writer transaction and rollback](generated/autonomous-writer-rollback.png)

Autonomous development includes writers. The security boundary is not “never write”; it is **write only under a documented capability charter with evidence, review, and a bounded recovery path**. The decision tree requires a trusted source, allowlisted fixed target, concurrency/idempotency control, deterministic dry-run/diff acceptance, pre-image/provenance, postcondition verification, and circuit-breaker behavior before it can claim success.

| Writer tier | Scope | Required safety properties | Recovery boundary |
|---|---|---|---|
| W0 | Read-only/advisory. | Minimal read permissions; safe outputs. | Preserve run evidence only. |
| W1 | Marked collaboration state. | Exact target/marker, trusted context, minimal write permission. | Amend only the workflow’s own attributable state. |
| W2 | Fixed-path generated repository content. | Deterministic source, allowlisted path/ref, lease, provenance, postcondition. | Fixed-scope revert/compensation with a manual dispatch/runbook. |
| W3 | Bot-owned branch or PR lifecycle. | Explicit acceptance, branch ownership, idempotency, review/check gates. | Close/revert bot-owned work; no self-merge. |
| W4 | External/provider/configuration state. | Separate threat model, approvals, audit, kill switch, staged rollout. | Verified compensation in a non-production/staged context. |

The writer map will be maintained as a catalog property. A writer is not considered healthy merely because it can invoke a GitHub write API; it must report the desired target, its pre-image, the postcondition, and any recovery/circuit-breaker state.

## 6. Waits, queues, cooldowns, schedules, and control-plane timing

![Timing and resilience map](generated/timing-resilience.png)

A wait is an explicit state, not a hidden failure. The timing map covers event coalescing, per-target queues, cached availability, bounded refresh, quotas, provider cooldowns, evidence waits, and terminal no-route outcomes. The weekly read-only operations report carries a daily AI-credit guardrail and finite artifact retention; the peer review route uses current-SHA evidence and advisory pending behavior by default.[4] [5]

The map also records the current Monday control-plane observation: the context-relationship reconciliation writer and the read-only fork audit share the `06:17 UTC` slot. Their responsibilities are intentionally distinct; moving only the read-only audit remains a queued, separate P1 runtime remediation and is not changed by this documentation PR.[6]

## 7. Roles, credentials, and authority hierarchy

![Role and authority hierarchy](generated/role-authority-hierarchy.png)

The role map distinguishes the human/operator from trusted collaborators, repository tokens, the OPERATOR lane, external provider credentials, agentic workflows, and writer workflows. It describes authority as a constrained graph—not a hierarchy of trust inherited from an issue/comment author. A provider credential authorizes only its bounded provider call; it does not authorize a repository write. A workflow token authorizes only the explicit job permission. A writer remains subject to its fixed-scope charter, postcondition, and review path.

## 8. Automatic documentation freshness and review routing

The freshness validator is intentionally deterministic. It reads trusted repository files as text data, regenerates the workflow catalog, and checks whether the committed generated outputs match the source fingerprint. It does not execute workflow YAML, interpolate issue/PR text, read secrets, create branches, or call a provider UI.

| Change class | Freshness result | Review communication |
|---|---|---|
| Unrelated source or documentation path | `no diagram impact`. | No new automation-doc requirement. |
| Governance/diagram/model-policy path | `documentation update required`. | Regenerate catalog/diagrams and include the change-impact summary. |
| Workflow, local action, router, role/routing schema, or operator-control path | `high-impact control-plane review required`. | Regenerate documentation; existing peer-review policy may evaluate the PR through the normal AR-15 route. |
| Generated catalog only | `generated-documentation-only`. | Verify it matches the current trusted control-plane source. |

A future CI job will invoke the validator in a read-only pull-request context, publish a summary and preview assets, and rely on the existing peer-review orchestration rather than creating a duplicate autonomous review agent. Rendering and freshness checking therefore improve communication without granting a new writer capability.

## 9. Text-only terminal-state runbook

| Terminal state | Meaning | Expected response |
|---|---|---|
| Ignored event | Event is outside a supported lifecycle, target, or path. | No mutation; preserve normal GitHub event context only. |
| Untrusted actor/context | Actor or repository association gate failed. | Do not interpret content as a command; surface only allowed diagnostic state. |
| No eligible model route | Availability, catalog, free-tier, or quota gates rejected every declared candidate. | Explicit skip/reason; do not substitute an undeclared paid or browser/session route. |
| Provider cooldown/pending | Evidence has not arrived or provider backoff applies. | Publish visible pending state; follow only the exact bounded retry rule. |
| Stale evidence | Provider evidence does not match the active SHA/cycle. | Preserve as status-only; do not advance completion. |
| Writer precondition failure | Target, lease, diff, provenance, or charter gate failed. | Do not mutate; leave actionable non-secret evidence. |
| Writer postcondition failure | A mutation did not create the declared state. | Circuit-break or execute only the accepted rollback path; verify recovery. |
| Separate-acceptance hold | Requested authority exceeds documented capability. | Stop and route to a reviewed threat-model/acceptance decision. |

## Source and maintenance record

The generated catalog records the exact control-plane fingerprint and workflow count for this snapshot. Update it by running:

```bash
python3 scripts/ci/automation_docs.py --write
python3 scripts/ci/automation_docs.py --check
python3 -m unittest tests.test_automation_docs
```

All Mermaid source is stored under [`docs/ops/diagrams/`](diagrams/). Rendered SVG/PNG assets are generated from those sources into [`docs/ops/generated/`](generated/). A documentation pull request must update source, generated catalog, and rendered assets together when material control-plane changes occur.

## References

[1]: ../../scripts/model_router.py "Model router: OpenRouter polling, cache, ranking, budgets, and explicit no-route state"
[2]: ../schemas/model-success-matrix.yaml "Local 3L0/ELO-like role-suitability matrix"
[3]: ../schemas/llm-leaderboard-matrix.yaml "Leaderboard policy and local-routing interpretation"
[4]: ../../.github/workflows/peer-review-orchestrator.yml "AR-15 provider policy, current-SHA evidence, and advisory pending mode"
[5]: ../../.github/workflows/agentic-repository-operations-report.lock.yml "Read-only operations report guardrails, schedule, and credit controls"
[6]: ../../.github/workflows/context-relationship-reconcile.yml "Monday writer reconciliation schedule"
