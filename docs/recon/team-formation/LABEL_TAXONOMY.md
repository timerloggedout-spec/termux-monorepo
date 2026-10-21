# Label Recon and Additive Team Taxonomy

## Purpose

This document records the label evidence captured from the repository on **2026-08-19** and maps it into an expandable team model. The mapping is additive: existing labels remain visible in GitHub and retain their research signal, while the roster gains canonical lanes, teams, roles, target records, machine profiles, and scorecards. A label identifies a topic or routing signal; the associated task card identifies the concrete project-owned component, approved artifact, or controlled test environment.

## Current Evidence Snapshot

The capture found **11** issues carrying `Search'n'Re-Search`, **9** carrying `Reverse_Engineering`, **7** carrying `H@× & Cπ@¢k$ && W4π3z && 3×9£017$`, **4** carrying `FORENSICS`, and **1** carrying `Roster:Teams:Games:Players`. The last label is attached to [issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243), which is open, located in the team-planning project’s Todo column, and names Astro Loop, 2 Minutes in Space, UnCiv, Pixel StarShips, and an expandable “MOAR!!” list. [1]

| Existing label | Observed use | Canonical planning lane | Additive role family |
|---|---|---|---|
| `Search'n'Re-Search` | Research tasks and exploratory work. | Research & Intelligence. | Source analyst, benchmarker, hypothesis designer, evidence reviewer. |
| `Reverse_Engineering` | Present on current APK, game-team, dependency, and process issues. | Mobile Analysis & Forensics; Security Research. | Artifact analyst, binary/toolchain analyst, dependency analyst, remediation researcher. |
| `FORENSICS` | Present on APK, game-team, ML-pipeline, and Termux-environment issues. | Mobile Analysis & Forensics. | Provenance analyst, reconstruction specialist, evidence curator. |
| `Ghidra` | Present on the APK investigation issue. | Mobile Analysis & Forensics. | Native-code analyst; toolchain maintainer. |
| `H@× & Cπ@¢k$ && W4π3z && 3×9£017$` | Present on issues covering APK investigation, game teams, dependencies, logins, and polling. | Security Research / Controlled Lab Research. | Security researcher, adversarial test designer, remediation verifier. |
| `ML Pipelines` | Present on the game-team and ML-pipeline issues. | Game Player Machines; Research & Intelligence. | ML-stack evaluator, telemetry analyst, model benchmarker. |
| `Roster:Teams:Games:Players` | Present on the game-team issue. | Game Player Machines & Genre Teams. | Player-machine operator, genre specialist, game telemetry analyst, reviewer. |
| `` `gh`ActionsWorkflows `` | Present on game-team and workflow-related issues. | Delivery Reliability / CI-CD. | Workflow engineer, gate maintainer, release verifier. |
| `ToDo-2-Ta'Dã!n!!🪄` | Current planning and completion tracking signal. | Orchestration & Quality Control. | Task router, acceptance-evidence maintainer, roster coordinator. |
| `security` | Broad security prioritization signal. | Security Research / Delivery Reliability. | Security reviewer, workflow-permission reviewer, incident analyst. |

## Specialist Issue Set

The following recently created or recently active issues form the first evidence set for the new teams. This is an intake map, not a claim that every issue requires the same workflow or assigned agent.

| Issue | Title | Labels relevant to the team model | Initial lane relationship |
|---|---|---|---|
| [#243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243) | Game Teams | `Roster:Teams:Games:Players`, `ML Pipelines`, `FORENSICS`, `Reverse_Engineering`, research, workflow, security labels. | Seed issue for player machines, genre teams, game catalog, and controlled game-research artifacts. |
| [#236](https://github.com/timerloggedout-spec/termux-monorepo/issues/236) | .APK Investigation List | `Reverse_Engineering`, `FORENSICS`, `Ghidra`, research, combined sensitive-research label. | Seed issue for APK target register, provenance, static-analysis reports, and remediation research. |
| [#213](https://github.com/timerloggedout-spec/termux-monorepo/issues/213) | GitHub ML Pipelines init | `ML Pipelines`, `FORENSICS`, research. | ML and telemetry research input for game-player and orchestration systems. |
| [#202](https://github.com/timerloggedout-spec/termux-monorepo/issues/202) | Dependabot Signals | `security`, `Reverse_Engineering`, dependencies, workflow, combined sensitive-research label. | Software supply-chain and workflow-security research. |
| [#201](https://github.com/timerloggedout-spec/termux-monorepo/issues/201) | AGENTS.md | `security`, `Reverse_Engineering`, dependencies, workflow, Linguist, combined sensitive-research label. | Governance, instructions, and dependency/repository-analysis research. |
| [#197](https://github.com/timerloggedout-spec/termux-monorepo/issues/197) | FORENSICS: ReBIUDL! Re 🏗️ Local Termux on Render | `FORENSICS`, `Reverse_Engineering`, `termux`. | Environment reconstruction, reproducibility, and Termux-first compatibility. |
| [#195](https://github.com/timerloggedout-spec/termux-monorepo/issues/195) | Evaluations | Research, `Reverse_Engineering`, Linguist. | Evaluation and score-calibration input. |

## Additive Registry Model

The roster must not be modeled as a closed list of roles. The canonical registry uses separate, versioned records so that new teams, player genres, tools, and research scopes may be appended without renaming or erasing the labels that led to them.

| Registry collection | What it records | Example append |
|---|---|---|
| `lanes` | High-level responsibility boundaries and integration ownership. | Add a dedicated Mobile Performance lane. |
| `teams` | Cohesive groups working inside one or more lanes. | Add a Game Strategy team. |
| `roles` | Concrete operating roles, skill expectations, and reviewer pairings. | Add a 4X player or APK provenance analyst. |
| `skills` | Evidence-backed capabilities, tool knowledge, and confidence. | Add Android resource inspection or testnet policy simulation. |
| `target_register` | Project-owned components, approved artifacts, games, labs, or test services. | Add a project test APK with hash and test objective. |
| `machine_profiles` | Player-machine or research-machine capability, platform, limits, and reset method. | Add an Android emulator with a defined game manifest. |
| `game_catalog` | Game build, genre, ownership/approval source, objectives, and assigned machine profiles. | Add a strategy title to the approved catalog. |
| `scorecards` | Role-specific score-event definitions, evidence requirements, and confidence rules. | Add a multiplayer session-stability scorecard. |
| `tool_profiles` | Approved tool use, version, environment, evidence format, and cleanup requirement. | Add a Ghidra analysis profile or Kali lab profile. |

## Tooling Interpretation

Ghidra, JADX, Apktool, Android Studio/emulators, Kali Linux, model-training frameworks, and game-playing stacks are all legitimate entries in the project’s research-tool profile. Their use is recorded together with tool version, test target, experiment objective, generated evidence, and reset/cleanup procedure. This provides reproducibility across the research teams and allows the roster to evaluate work quality rather than tool possession alone.

## Required Next Artifacts

The label map requires four implementation-facing records before automatic routing is enabled: an issue/PR inventory, a target register, a game catalog with machine profiles, and a role-score event schema. These are tracked in the expanded `agent-team-formation` proposal rather than hidden in a dashboard-only configuration.

## References

[1] [Issue #243 — Game Teams](https://github.com/timerloggedout-spec/termux-monorepo/issues/243#issue-5185983300)

[2] [Issue #236 — .APK Investigation List](https://github.com/timerloggedout-spec/termux-monorepo/issues/236)

[3] [Issue #213 — GitHub ML Pipelines init](https://github.com/timerloggedout-spec/termux-monorepo/issues/213)

[4] [Issue #202 — Dependabot Signals](https://github.com/timerloggedout-spec/termux-monorepo/issues/202)

[5] [Issue #197 — FORENSICS: ReBIUDL! Re 🏗️ Local Termux on Render](https://github.com/timerloggedout-spec/termux-monorepo/issues/197)
