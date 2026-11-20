# Integration Drift Record — 2026-11-19

**Scope:** repository entry-point authority, Linear execution tracking, Jules automation, and the accessibility-agents integration.

## Disposition

Repository-native governance remains active. This record supersedes stale integration assumptions where external services have changed or become unavailable.

| Surface | Observed drift | Current disposition |
|---|---|---|
| Agent entry point | Root `CLAUDE.md` delegated authority directly to `AGENTS.md`, while the operator is migrating the protocol naming and entry hierarchy. | `CLAUDE.md` is the primary entry point. `AGENTS.md` remains a compatibility surface during the parallel migration. |
| Linear | The legacy protocol made a `TER-*` issue a hard admission gate. The operator reports sustained Linear problems for more than a month. In this run, issue discovery found no matching accessibility item and issue creation was rejected by the workspace's free-plan issue cap. | Treat Linear as an optional mirror. Continue under accepted repository proposal scope, record item status, and use GitHub evidence. Synchronization remains pending until verified. |
| Jules | Two repository workflows still triggered on issue and review activity. | Retire automated Jules dispatch effective 2026-11-01. Keep the workflow paths as manual-only retirement notices for traceability. |
| Accessibility framework | Existing upstream fork instructions and workflows are designed for their own package and clients. | Pin the user-owned fork as a reference submodule; adapt its skills and evidence contracts to repository-native routing and gates. |

## Jules timeline: local policy and vendor status

- **2026-11-01:** repository-local Jules automation retirement date, per operator direction.
- **2026-10-29:** Google published its Jules wind-down notice.
- **2026-11-11:** Google stated that Jules would become read-only after this date.
- **2026-12-31:** Google stated the Jules service would wind down.

Primary source: <https://jules.google/docs/changelog>

The local retirement date and Google's product timeline are separate facts. Antigravity is a potential migration target, not an assumed drop-in replacement. Rebuild workflows around repository-owned prompts, scripts, permissions, test commands, and review gates.

## Linear evidence

- Operator report: Linear has experienced sustained problems for more than one month as of this record.
- Current connector observation: the attempted issue creation returned the workspace free-plan issue-cap error.
- Current search: no matching accessibility issue was found in the searched results.
- Exact start date and full historical outage window: pending independent verification.

The current observation supports a degraded issue-creation path. It does not prove that all Linear reads or updates are unavailable. Keep each capability's status separate.

## Accessibility source pin

- Repository: <https://github.com/timerloggedout-spec/accessibility-agents_fork>
- Upstream parent: <https://github.com/Community-Access/accessibility-agents>
- License: MIT
- Pinned source commit: `a538edc9edfb98cdd8bae96d6b79542874b478f7`
- Integration location: `refTemplates/smods/accessibility-agents_fork`

The pinned source supplies accessibility skills, shared dispatch and findings contracts, scanner guidance, report generation, and package-specific workflows. The monorepo adapter selects reusable skills and evidence contracts while retaining its own entry point, proposal process, workflow policy, and CI gates.

## Reconciliation rules

1. Read current repository state before every consequential action.
2. Prefer existing accepted scope and active item records.
3. Route around unavailable integrations with durable local evidence.
4. Keep upstream source changes and monorepo adaptations distinguishable.
5. Recheck drift when an external integration changes state.
6. Report verified, pending, and operator-reported facts separately.
