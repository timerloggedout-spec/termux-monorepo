# CLAUDE.md

This is the primary agent entry point for `timerloggedout-spec/termux-monorepo`. Read this file first and use it to orient every repository task.

## Authority and adaptive priority

Apply this order while retaining the highest applicable authority:

1. Platform safety and explicit operator instructions.
2. The current user objective and its stated scope.
3. This entry point, followed by the closest applicable directory guidance.
4. Repository-native governance: `docs/proposals/registry.yaml`, the active proposal's `ITEMS.md`, permission boundaries, and recorded decisions.
5. Current repository evidence: source, tests, GitHub issues and pull requests, workflow results, and branch state.
6. External trackers and agent services as optional integrations and evidence mirrors.

Use **Adaptive Dynamic Awareness** to choose the next action from current scope, priority, risk, dependencies, blockers, freshness, available capabilities, and verifiable impact. Re-evaluate after each meaningful state change. Keep work in small reviewable batches, commit coherent increments, and merge only after the repository's required checks and review conditions pass.

A tool outage, quota limit, stale record, or missing external tracker item changes the execution route. It does not outrank the repository's active scope or stop independently verifiable work. Record material drift and continue through the repository-native path.

## Active protocols and migration

- `CLAUDE.md` is the agent entry point.
- `AGENTS.md` remains a compatibility surface while its name and protocol migration proceeds in parallel. Apply relevant scoped guidance and record conflicts for reconciliation; do not treat a stale pointer or generated projection as higher authority than this entry point and current operator direction.
- Linear is an optional execution mirror. Reuse a current `TER-*` issue when the integration is healthy and a matching issue exists. When Linear is unavailable, rate-limited, or blocks issue creation, record the state in `docs/ops/INTEGRATION-DRIFT-2026-11-19.md`, keep the proposal and item record current, and continue with GitHub and repository evidence. Report Linear synchronization as pending until verified.
- Jules / `google-labs-code/jules-action` automation is retired in this repository effective 2026-11-01. Use currently configured agent routes and repository-owned workflows; evaluate replacements by capability rather than assuming feature parity.

## Quick pointers

| Need | Path |
|---|---|
| Active work and priority | `docs/proposals/registry.yaml` |
| Proposal lifecycle | `docs/proposals/PROCESS.md` |
| Agent permissions | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| Repository gates | `docs/ARCHW1Z-GATE.md` |
| Current status | `docs/ARCHW1Z-STATUS.md` |
| Linear adapter protocol | `docs/LINEAR-AGENT-PROTOCOL.md` |
| Integration drift | `docs/ops/INTEGRATION-DRIFT-2026-11-19.md` |
| Accessibility integration | `docs/accessibility/INTEGRATION.md` |
| Session source of truth | `docs/schemas/session-ssot.md` |
| Provider capabilities | `docs/schemas/provider-capabilities.md` |

## Execution defaults

- Integration base branch: **`master-staging`**.
- Run `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py` before declaring a repository integration complete.
- Preserve the permanent staging spine. Promote only focused, reviewed changes to `master`.
- Keep commits small and evidence-bearing. Update the active proposal item and drift record as state changes.
- Keep credentials, session stores, browser profiles, private mapper material, and generated runtime state outside Git.
- Record debate and decisions in the proposal MANIFEST review log or `DEBATE.md`, not only in chat.
