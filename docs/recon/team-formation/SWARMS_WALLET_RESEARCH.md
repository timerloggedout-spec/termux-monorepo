# Swarms Reference Evaluation and Wallet Research Architecture

## Purpose

This record evaluates public Swarms material as a seed/reference for the Termux multi-agent roster and defines the project’s staged economic-system research path. It separates three concerns that should not be conflated: orchestration patterns, MoneyBall internal points, and future real-wallet capabilities.

## Public Reference Assessment

The official [Swarms repository](https://github.com/kyegomez/swarms) describes a Python multi-agent orchestration framework with sequential, concurrent, and hierarchical architectures; agent objects composed of an LLM, tools, and memory; MCP integration; tests and examples; and an Apache-2.0 license. Its project structure and current emphasis on telemetry, retries, MCP management, and graph execution make it useful as an architectural reference. [1]

The [Swarms token-use-case repository](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases) is a separate, MIT-licensed repository with a small commit history. It describes conceptual token economics such as marketplace activity, subscriptions, agent incentives, and auctions. It is appropriate as a concept source for the internal-points and agent-economy research lane, but its size and recency profile do not make it a production dependency by default. [2]

| Reference attribute | Swarms framework | Token-use-case repository | Termux-monorepo decision |
|---|---|---|---|
| Main value | Orchestration patterns, agent abstraction, concurrency/hierarchy, tool/MCP interoperability, telemetry concepts. | Economic-system concepts and agent-marketplace framing. | Use as documented research input; do not copy or vendor before review. |
| License | Apache-2.0. | MIT. | Record the source, version, and license before any code reuse. |
| Maturity signal | Large repository with examples, tests, security material, and active changes. | Small repository with limited history. | Prefer architecture extraction over dependency adoption for the first increment. |
| Immediate reuse candidate | Task delegation, role composition, event/telemetry vocabulary, graph workflow concepts. | Internal-points terminology and incentive hypotheses. | Compare to current MoneyBall implementation rather than replace it. |

## Recommended Orchestration Design

The Termux roster should remain repository-native. Swarms concepts are useful only where they strengthen existing design goals: role-specific capabilities, explicit task state, observable handoffs, bounded concurrency, tool profiles, and replayable evidence. The first architecture decision record should compare three alternatives: evolve the current `termux-multi-agent` implementation, adapt selected public patterns without adding a dependency, or introduce Swarms as an optional experimental adapter.

| Decision criterion | Repository-native evolution | Pattern adaptation | Optional framework adapter |
|---|---|---|---|
| Termux compatibility | Highest control over package/runtime constraints. | High, because dependencies remain chosen case by case. | Requires full dependency and Android/Termux verification. |
| Migration risk | Lowest initial migration risk. | Moderate documentation and implementation effort. | Highest integration and lifecycle risk. |
| Observability | Must be implemented/extended locally. | Can adopt portable event/telemetry concepts. | May inherit framework conventions but also framework coupling. |
| Recommended next step | Baseline option. | Research and prototype option. | Defer until measured benefit justifies it. |

## Economic-System Stages

The roadmap supports the user’s future real-wallet direction without treating it as an immediate change to the team roster. Each stage has independent artifacts, test evidence, and a promotion decision.

| Stage | Scope | Required artifacts | Promotion condition |
|---|---|---|---|
| A — Internal points | Deterministic, non-transferable points for MoneyBall simulations, incentives, task bounties, and audit exercises. | Versioned ledger schema, event types, double-entry-style invariants, replay test suite, policy document. | Invariants and replay tests pass; score events are auditable; no real asset or private-key handling. |
| B — Simulation / testnet | Policy engine, signer-boundary experiments, transaction previews, monitoring, failure/recovery exercises, and testnet-only workflows. | Wallet ADR, threat model, policy tests, signer-isolation design, testnet/simulation evidence, recovery plan. | Independent security review and Operator approval of the test environment. |
| C — Future real-wallet architecture | User-selected real wallet/custody model, transaction authorization, spending policy, incident response, and auditability. | Custody decision, signer/key-isolation design, transaction-preview/approval flow, limits, recovery plan, compliance/security review. | Separate explicit approval before any real transaction or key-connected deployment. |

## Wallet and Ledger Contract

A wallet/economic-system task must identify the stage, ledger/wallet environment, custody model, signer boundary, policy reference, maximum test value or testnet asset, expected evidence, and review partner. The team-roster score is never a proxy for financial authority; it is evidence of role performance only.

| Contract field | Stage A | Stage B | Stage C |
|---|---|---|---|
| Value type | Internal non-transferable point. | Simulated or testnet asset. | User-selected real asset. |
| Signing | None. | Isolated test signer or test wallet. | Explicit custody/signer design; no blanket agent key access. |
| Authorization | Task-card verdict and ledger policy. | Task-card verdict, policy test, and approved test environment. | Transaction preview and explicit user authorization for each irreversible action. |
| Audit | Append-only event history and deterministic replay. | Event history, test evidence, policy decision logs. | Full transaction, approval, policy, and recovery audit trail. |
| Scoring use | Incentive simulation only. | Research/evaluation evidence only. | Never a substitute for custody or spending authority. |

## Initial Research Backlog

The first deliverables are a ledger event vocabulary, an internal-points invariant checklist, a wallet architecture decision record template, and a testnet policy/threat-model outline. These artifacts will be reviewed alongside the MoneyBall reconciliation rather than wired into the currently open PR #131.

| Research item | Owner team | Evidence of completion |
|---|---|---|
| Internal-points event vocabulary | Wallet & Economic Systems + Orchestration. | Ledger event schema includes issue/task references, amount type, debit/credit semantics, verdict, and immutable evidence links. |
| Replay and invariant specification | Wallet & Economic Systems + Development. | Deterministic test cases for balance conservation, idempotency, reversal, and invalid-event handling. |
| Wallet ADR template | Wallet & Economic Systems + Security Research. | Template captures stage, custody, signing, transaction policy, recovery, dependencies, and reviews. |
| Swarms pattern comparison | Research & Intelligence + Development. | Comparison matrix ties each candidate pattern to current monorepo components and Termux constraints. |
| Testnet policy outline | Wallet & Economic Systems + Security Research. | Defines isolated test environment, test assets, monitoring, reset, and escalation path. |

## References

[1] [kyegomez/swarms — official repository](https://github.com/kyegomez/swarms)

[2] [The-Swarm-Corporation/kyegomez-swarms-token-usecases](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases)

[3] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[4] [MoneyBall Implementation Recon](./MONEYBALL_RECON.md)

[5] [Initial Team Charter](../../proposals/active/agent-team-formation/TEAM_CHARTER.md)
