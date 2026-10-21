# Team-Formation Recon Index

## Scope and Status

This directory contains the first evidence package for the `agent-team-formation` proposal. It was captured on **2026-08-19** after the project expanded the team model to include the `Roster:Teams:Games:Players` lane, genre-specific player machines, continuing mobile/forensics research, controlled security research on project systems, and the staged wallet/economic-systems research path.

The package is planning and evidence work. It does not modify the active MoneyBall implementation, start an automated roster rotation, provision a game-playing machine, use a wallet, or create a production integration. The implementation blockers and required next artifacts are explicit in the linked records.

| Record | What it establishes | Primary proposal item |
|---|---|---|
| [Label Recon and Additive Team Taxonomy](./LABEL_TAXONOMY.md) | Current label counts and specialist issue map; a registry model that allows teams, lanes, roles, tools, machines, games, and scorecards to be appended. | ATF-11 |
| [Game Player Fleet and Genre Teams](./GAME_PLAYER_FLEET.md) | `Roster:Teams:Games:Players` as a first-class fleet, including catalog, machine profile, player-role, telemetry, reset, and score-event contracts. | ATF-12 |
| [Initial Target Register Template](./TARGET_REGISTER.md) | Stable, versioned intake record for repository components, controlled labs, mobile artifacts, game builds, player machines, and wallet stages. | ATF-11, ATF-12, ATF-13 |
| [Anchored Roster Context and Identity Schema](./ROSTER_CONTEXT_SCHEMA.md) | Canonical entity references, relationship records, context manifests, aliases, temporary batches, and validation rules for custom team/run notation. | ATF-14 |
| [Provider-Agnostic Role Label Dispatch Contract](./ROLE_LABEL_DISPATCH.md) | Maps approved labels to the user’s own roster policies, stable context manifests, and auditable dispatch intents without treating providers as roles. | ATF-15 |
| [MoneyBall Implementation Recon](./MONEYBALL_RECON.md) | Live #131 status, branch/check evidence, SSOT discrepancy, and branch/gate blockers. | ATF-03, ATF-09, ATF-10, ATF-11 |
| [Swarms Reference and Wallet Research](./SWARMS_WALLET_RESEARCH.md) | Public Swarms reference evaluation and staged internal-points, simulation/testnet, and future real-wallet architecture. | ATF-13 |

## Current Evidence Summary

The captured repository evidence identifies [issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243) as the explicit seed for **Game Teams**. The issue is open, in the team-planning Todo column, carries the `Roster:Teams:Games:Players` label together with ML, forensics, security, research, workflow, and reverse-engineering signals, and names an expandable game list. [1]

The MoneyBall source is less settled: [PR #131](https://github.com/timerloggedout-spec/termux-monorepo/pull/131) remains open and dirty in live metadata even though the lane SSOT describes its work stream as merged. It is 94 commits ahead of its recorded base; the captured check state includes failures in the peer-review orchestrator and a GitLab pipeline. The branch and gate policy discrepancies must be closed before implementation changes are described as ready for integration. [2] [3]

The public [Swarms framework](https://github.com/kyegomez/swarms) supplies mature reference material for multi-agent orchestration, including sequential, concurrent, and hierarchical patterns, tests, telemetry work, and MCP integration. The separate public token-use-case repository supplies economic-system concepts but is appropriately treated as a conceptual source rather than a direct production dependency. [4] [5]

## Review Sequence

The next review should first select the authoritative MoneyBall implementation and integration-gate policy. It should then approve the additive roster registry, initial game catalog and player-machine schema, target-register template, role-label dispatch contract, and wallet-stage decision record. This sequence allows the project to add teams and research roles without freezing the taxonomy, conflating providers with roles, or treating labels as implementation readiness.

## References

[1] [Issue #243 — Game Teams](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300)

[2] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[3] [Lane Consolidation SSOT](../../ops/LANE_CONSOLIDATION_SSOT.md)

[4] [kyegomez/swarms](https://github.com/kyegomez/swarms)

[5] [Swarms token-use-case repository](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases)
