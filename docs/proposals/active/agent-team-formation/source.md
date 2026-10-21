# Evidence Log — agent-team-formation

## Repository evidence

| Source | Observed fact | Consequence for this proposal |
|---|---|---|
| [Issue #129](https://github.com/timerloggedout-spec/termux-monorepo/issues/129) | The issue requests a broad, performance-evaluated team hierarchy, role creation based on observed needs, and a MoneyBall-style roster. | Preserve the desired experimental roster model, but separate capabilities and authority by role. |
| [PR #131](https://github.com/timerloggedout-spec/termux-monorepo/pull/131) | The PR describes a persistent roster, ELO tracking, culling/cloning, specialized role creation, internal points, and a betting arena. Live metadata captured on 2026-08-19 reports it open, dirty, and 94 commits ahead of its recorded base; captured checks include two failures. | Treat it as implementation evidence, but do not extend or automate the roster until the authoritative implementation state and gate disposition are reconciled. |
| [Lane Consolidation SSOT](../../../ops/LANE_CONSOLIDATION_SSOT.md) | Lane 4 assigns MoneyBall and agent mail to `termux-multi-agent/src/team_manager.py`, `roster.json`, and the mailbox action. It states that #129 / #131 is merged. | The disagreement with the live PR state is tracked as blocker ATF-03 rather than silently resolved. |
| [Builder/reviewer policy](../../../AGENTIC-BUILDERS-VS-REVIEWERS.md) | Jules is the primary builder; CodeRabbit and configured Gemini/Devin modes are reviewers or triage; agents must avoid overlapping claimed files. | Development and orchestration teams require an explicit independent review pairing and claimed-file discipline. |
| [Consensus rules](../../../CONSENSUS.md) | Accepted proposals need a non-author review or Operator self-acceptance; protected actions remain human-only. | This proposal remains a draft; it cannot authorize score-driven mutations or sensitive analysis. |
| Repository gate scripts | `python3 scripts/ci/repo_gate.py` passed on this documentation branch. The repository instructions also reference `scripts/ci/termux_smoke.py`, but that file was absent from the inspected branch. | The proposal records the missing invocation as blocker ATF-10; no claim is made that the dual gate passed. |
| [Issue #236](https://github.com/timerloggedout-spec/termux-monorepo/issues/236) | The issue is an APK investigation list containing game titles and labels for reverse engineering, forensics, Ghidra, and the combined sensitive-research label. | Establish a target-register, artifact-provenance, tool-profile, experiment, and evidence model for project-controlled or approved research artifacts. |
| [Issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243) | The issue is open in the team-planning Todo column, names an expandable game list, and carries `Roster:Teams:Games:Players` with ML, forensics, research, workflow, security, and reverse-engineering labels. | Add a first-class Game Player Machines & Genre Teams lane, with a game catalog, machine profiles, player roles, telemetry, reset evidence, and genre scorecards. |
| [Swarms framework](https://github.com/kyegomez/swarms) | Public Apache-2.0 multi-agent framework describing sequential, concurrent, hierarchical, MCP, telemetry, and test-oriented patterns. | Use as a reference for architecture comparison, not an assumed dependency. |
| [Swarms token-use-case repository](https://github.com/The-Swarm-Corporation/kyegomez-swarms-token-usecases) | Public MIT conceptual agent-economy/token material with limited repository history. | Inform the staged internal-points, simulation/testnet, and future real-wallet research architecture; do not treat it as a production dependency by default. |

## Target-register gap

The review found no complete, versioned target register for the mobile-analysis, game-player, security-research, or wallet lanes. The initial work therefore defines a **target-register-first intake**: project components, controlled labs, supplied test builds, and approved source material must be named together with provenance, experiment purpose, tool profile, expected evidence, and reset/cleanup requirements. This is the first artifact needed to route the labels into reproducible team work.

## Verification-gate discrepancy

The repository instructions and lane SSOT name `python3 scripts/ci/termux_smoke.py` as the second mandatory integration gate. The inspected branch contained `scripts/ci/repo_gate.py` but no `termux_smoke.py` or similarly named smoke script. The repository gate passed for this documentation-only change; the second gate could not be executed. This discrepancy is captured as blocker ATF-10 and requires a Delivery Reliability disposition before implementation work claims dual-gate readiness.

## Branch-base discrepancy

Repository instructions specify `master-staging` as the integration target. The remote inspected on 2026-08-18 exposed `origin/master` but no `origin/master-staging` reference. The documentation branch for this draft was created from `origin/master` solely to preserve the proposal as non-integrated documentation. No implementation change, merge request, or automation has been presented as ready for integration.

## Controlled-research interpretation

The project’s existing red-team, reverse-engineering, forensics, Ghidra, game-player, and combined sensitive-research labels are retained as research signals. The first implementation step is to attach each task to a project component, controlled lab, approved artifact, game catalog entry, or test environment and record the intended experiment and evidence chain. This keeps the taxonomy broad and expandable while making team outcomes reproducible and reviewable.

## References

[1] [Issue #129 — Development Teams & Emerging Technologies Research Team](https://github.com/timerloggedout-spec/termux-monorepo/issues/129)

[2] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[3] [Issue #236 — APK Investigation List](https://github.com/timerloggedout-spec/termux-monorepo/issues/236)

[4] [Lane Consolidation SSOT](../../../ops/LANE_CONSOLIDATION_SSOT.md)

[5] [Agentic builders vs reviewers](../../../AGENTIC-BUILDERS-VS-REVIEWERS.md)

[6] [Consensus rules](../../../CONSENSUS.md)

[7] [Issue #243 — Game Teams](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300)

[8] [MoneyBall implementation recon](../../../recon/team-formation/MONEYBALL_RECON.md)

[9] [Label recon and additive team taxonomy](../../../recon/team-formation/LABEL_TAXONOMY.md)

[10] [Game player fleet and genre teams](../../../recon/team-formation/GAME_PLAYER_FLEET.md)

[11] [Swarms reference and wallet research](../../../recon/team-formation/SWARMS_WALLET_RESEARCH.md)
