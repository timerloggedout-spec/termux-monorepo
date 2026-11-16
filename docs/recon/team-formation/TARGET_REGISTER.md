# Initial Target Register Template

## Purpose

This register is the canonical intake surface for work performed by the new teams. It allows the roster to keep all existing research labels in scope while grounding each assignment in a specific project component, controlled environment, approved artifact, game build, or wallet research stage. A record may be appended as the project grows; no registry entry grants task routing by itself until it has an owner, evidence requirement, and reviewer pairing.

## Required Fields

| Field | Meaning |
|---|---|
| `target_id` | Stable identifier such as `repo:termux-monorepo`, `game:unciv:pending-build`, or `wallet:points-ledger:v1`. |
| `target_class` | Repository component, controlled lab, mobile artifact, game build, player machine, workflow, wallet environment, or external reference. |
| `owner` | Accountable project team or Operator-recognized owner. |
| `source_or_provenance` | Repository path/commit, artifact hash, project issue, owner-supplied transfer, license/source URL, or environment image reference. |
| `purpose` | The research, development, QA, performance, or reliability question being addressed. |
| `lane_and_roles` | Responsible lane, supporting roles, and independent review partner. |
| `tool_profile` | Allowed tools, versioning requirement, output/evidence form, and cleanup/reset expectations. |
| `environment` | Device, emulator, VM, test service, workflow, repository branch, simulation, or testnet setting. |
| `evidence_policy` | Required logs, tests, traces, findings, remediation notes, and retention classification. |
| `status` | `candidate`, `registered`, `active`, `blocked`, `archived`, or `superseded`. |

## Seed Records

The following are planning records only. They identify what must be registered before workload assignment; they do not claim that a game build, APK, test account, wallet, or machine has already been provisioned.

| target_id | target_class | source_or_provenance | purpose | lane_and_roles | status |
|---|---|---|---|---|---|
| `repo:termux-monorepo` | Repository software | `timerloggedout-spec/termux-monorepo`; current default-branch commit recorded per task. | Team formation, workflow reliability, orchestration, and controlled code evaluation. | Development; Delivery Reliability; Security Research; Orchestration. | registered |
| `pr:131:moneyball` | Implementation evidence | [PR #131](https://github.com/timerloggedout-spec/termux-monorepo/pull/131); head/base commits recorded in [MoneyBall Recon](./MONEYBALL_RECON.md). | Reconcile roster behavior before reuse or refactor. | Orchestration; Development; Delivery Reliability. | blocked |
| `issue:236:apk-research` | Mobile-analysis intake | [Issue #236](https://github.com/timerloggedout-spec/termux-monorepo/issues/236); artifact list not yet normalized. | Build artifact-provenance and tool-profile records for mobile/forensics research. | Mobile Analysis & Forensics; Security Research. | candidate |
| `issue:243:game-teams` | Game catalog intake | [Issue #243](https://github.com/timerloggedout-spec/termux-monorepo/issues/243); titles need build/version/provenance records. | Create player-machine and genre-team catalog entries. | Game Player Machines; Game QA; ML Game Research. | candidate |
| `wallet:internal-points:v1` | Wallet/economic-system simulation | MoneyBall internal-points research; no external asset or signer. | Define deterministic ledger events and incentive experiments. | Wallet & Economic Systems; Orchestration. | candidate |
| `wallet:testnet-policy:v1` | Testnet/simulation environment | To be created only after a wallet architecture decision record. | Test policy, signer isolation, previews, monitoring, and recovery. | Wallet & Economic Systems; Security Research. | candidate |

## Game and Machine Registration Addendum

A game-player assignment may be opened only after both a `game_catalog` entry and a `machine_profile` exist. The catalog entry supplies title, genre, build identity, approval source, objectives, and evidence requirements. The machine profile supplies platform/image, hardware class, input mode, test profile, telemetry policy, resource limits, and reset procedure. This provides a reproducible implementation of the `Roster:Teams:Games:Players` lane without hard-coding the initial game list as the final catalog.

## Review and Change Control

A new record is proposed in the relevant issue or proposal item, reviewed by the owner team and review partner, and then added with a durable provenance reference. Changes that alter a game build, artifact hash, tool profile, or wallet stage create a new versioned record rather than silently editing prior evidence. Records with missing provenance or environment details remain `candidate` and cannot produce score events.

## References

[1] [Label Recon and Additive Team Taxonomy](./LABEL_TAXONOMY.md)

[2] [Game Player Fleet and Genre Teams](./GAME_PLAYER_FLEET.md)

[3] [MoneyBall Implementation Recon](./MONEYBALL_RECON.md)

[4] [Swarms Reference and Wallet Research](./SWARMS_WALLET_RESEARCH.md)
