# Initial Team Charter

## Purpose

The Termux multi-agent roster should route work according to **demonstrated capability in a bounded role**, not a single global score. The existing MoneyBall concept provides a useful mechanism for candidate tracking, internal points, and controlled experimentation. This charter narrows that mechanism into a team model that is auditable, task-relevant, and safe to operate.

> **Routing principle:** A high score in one discipline is evidence for that discipline only. It does not transfer authority, access, or expertise to another discipline.

All role assignment remains subject to the repository's dual gates, issue/PR coordination rules, and human-only authority boundaries. Scores are operational signals, not permission grants.

## Team map

| Team | Mission | Primary deliverables | Explicit boundary | Initial evidence source |
|---|---|---|---|---|
| **Research & Reconnaissance** | Convert uncertainty into cited, reproducible decision material. | Research briefs, source maps, benchmark plans, risk registers. | Does not merge production code or make security claims without review. | Issue #129 research intent; existing researcher candidates. |
| **Development** | Implement scoped changes in isolated branches with focused tests. | Small commits, tests, migration notes, PRs. | Does not self-approve, bypass gates, or modify files claimed by another open agent PR. | Builder/reviewer policy. |
| **Delivery Reliability (DevOps / CI-CD)** | Keep the dual-gate spine, workflows, and on-device compatibility reliable. | CI repairs, gate evidence, safe workflow changes, incident notes. | Does not broaden workflow credentials, alter app permissions, or write secrets. | Existing lanes 2 and 5. |
| **Game Player Machines & Genre Teams** | Operate designated player machines against the approved game catalog and generate reproducible, genre-specific session evidence. | Game catalog records, machine profiles, session traces, genre scorecards, reset evidence. | Each game/build, test profile, telemetry policy, and reset procedure is registered before scoring. | Issue #243 and `Roster:Teams:Games:Players`. |
| **Game QA & Accessibility** | Independently test and verify project-owned, open-source, or explicitly supplied game builds for quality and accessibility. | Reproduction steps, compatibility matrix, test fixtures, accessibility findings. | Reviews player-machine evidence and keeps QA verdicts separate from player performance. | Issue #243 game list and team-planning project. |
| **Mobile Analysis & Forensics** | Analyze registered project-owned or approved Android artifacts to establish reproducible facts and remediation needs. | Provenance record, static analysis notes, SBOM/license observations, tool profiles, remediation recommendations. | Artifact hash, target record, tool version, experiment objective, and evidence classification are required. | Issue #236, Ghidra label, and forensics context. |
| **Security Research & Red Team** | Test the project’s own software, agents, workflows, and controlled labs, then support remediation. | Threat models, controlled test cases, findings, patches, regression tests. | Every task names a project-owned component or controlled lab target and a review partner. | Security lane, Sentinel guardrails, and current research labels. |
| **Wallet & Economic Systems** | Research internal points, agent incentives, ledger integrity, and staged agent-wallet architecture. | Ledger specification, simulations, policy model, threat model, architecture decision records. | Internal points, simulation/testnet, and future real-wallet work are separately versioned stages. | MoneyBall PR #131 and Swarms ecosystem research. |
| **Orchestration & Quality Control** | Route tasks, preserve context, enforce claims, calibrate role metrics, and manage additive registry records. | Assignment records, score events, review pairing, audit logs, registry changes. | Does not autonomously promote, cull protected roles, or approve its own work. | MoneyBall lane plus context/workflow lanes. |

## Role assignment contract

Every task assigned through the roster must carry a compact, durable task card. The task card is the minimum evidence needed for routing, scoring, and later audit.

| Field | Requirement |
|---|---|
| `task_id` | Stable issue, PR, or local task identifier. |
| `team` | One accountable team; supporting teams are named separately. |
| `scope` | Files, systems, artifacts, or experiment boundaries that may be touched. |
| `target_record` | A project-owned component, controlled lab, approved artifact, game-catalog entry, or wallet environment reference. |
| `authority` | `internal`, `owned`, `open_source`, or an approval reference tied to the target record. |
| `machine_profile` | Required for player-machine or controlled-tool work; identifies environment, limits, and reset procedure. |
| `tool_profile` | Required research tools and versions, generated evidence type, and cleanup/reproducibility requirements. |
| `expected_evidence` | Tests, sources, logs, reproduction, telemetry, or review required for success. |
| `risk_tier` | Standard, elevated, or human-only. |
| `review_pair` | A distinct reviewer or reviewer team for development, delivery, and security work. |
| `score_event` | The role-specific measures that will be updated only after verdict. |
| `context_manifest` | Versioned roster-context record that resolves lane, team, role, skills, agent, target, machine, task, run, source labels, and review pair. |

## Score architecture

### Shared score components

Every active candidate retains three **shared**, non-transferable signals. A candidate must meet the shared safety floor before any role-specific score is used for routing.

| Component | Meaning | Measurement rule | Use |
|---|---|---|---|
| `quality_reliability` | Whether the candidate delivers evidence-backed work that survives review. | Accepted deliverables divided by evaluated deliverables; weighted by reopened defects. | Minimum routing threshold. |
| `scope_discipline` | Whether the candidate stays inside approved task and file boundaries. | Clean scope events minus verified boundary violations. | Hard safety/routing gate. |
| `collaboration_hygiene` | Whether the candidate claims work, preserves context, and responds to review. | Claim correctness, handoff completeness, and review-response timeliness. | Tie-breaker and pairing signal. |

The current global ELO/3L0 field may remain as a **displayed aggregate**, but it must not be the sole task-routing metric. The aggregate must be traceable to role-specific score events, use confidence bounds for small samples, and never overwrite the raw event history. The roster-context manifest defined in [ROSTER_CONTEXT_SCHEMA.md](../../../recon/team-formation/ROSTER_CONTEXT_SCHEMA.md) is the canonical binding between a score event and its lane, team, role, skills, agent, target, machine, task, run, source labels, and review pair.

### Role-specific scorecards

| Team | Primary measures | Negative signals | Minimum evidence before score update |
|---|---|---|---|
| Research & Reconnaissance | Source quality and coverage; claim traceability; reproducibility; decision usefulness; forecast calibration where applicable. | Unsupported claims; stale or contradictory sources ignored; irreproducible methods. | Linked sources, method, uncertainty statement, and reviewer disposition. |
| Development | Gate pass rate; post-review rework; defect escape rate; test relevance; diff focus. | Regressions; unrelated changes; unaddressed review findings; skipped required tests. | Commit/PR, targeted tests, gate output, and reviewer disposition. |
| Delivery Reliability | Pipeline success rate; mean time to safe recovery; flaky-check reduction; Termux compatibility; least-privilege adherence. | Credential expansion; nondeterministic or unpinned changes; repeat incidents; broken smoke compatibility. | Workflow/job evidence, gate logs, rollback/recovery note, and reviewer disposition. |
| Game Player Machines & Genre Teams | Approved scenario coverage; objective completion; session stability; telemetry completeness; reset correctness; genre-specific performance. | Missing session evidence; unregistered machine/build; incomplete reset; cross-genre score leakage. | Game catalog entry, machine profile, session trace, objective verdict, and reviewer disposition. |
| Game QA & Accessibility | Unique reproducible defects; device/variant coverage; accessibility impact; fix verification quality. | Incomplete reproduction; duplicate reports without added evidence; player performance scored as QA evidence. | Catalog record, build identity, reproduction steps, expected/actual result, and reviewer verdict. |
| Mobile Analysis & Forensics | Provenance completeness; analytical reproducibility; finding validity; remediation value; tool/evidence discipline. | Missing target record; unverifiable artifact; evidence handling failure; no reproducible method. | Target record, artifact hash, acquisition provenance, tool profile, method, and finding or null result. |
| Security Research & Red Team | Validated finding quality; risk framing; remediation acceptance; regression prevention; false-positive control. | Unregistered target; destructive test without recovery; exploitability inflation; no remediation path. | Target/lab record, controlled test evidence, impact analysis, remediation proposal, and independent review. |
| Wallet & Economic Systems | Ledger invariants; policy coverage; simulation fidelity; threat-model quality; reviewability. | Non-replayable accounting; unclear custody stage; unreviewed key/signer design; missing transaction policy. | Ledger/test vectors, policy results, architecture decision record, and security review. |
| Orchestration & Quality Control | Correct routing; balanced utilization; conflict avoidance; score calibration; audit completeness; additive-registry integrity. | Self-dealing; opaque routing; inappropriate cull/clone action; missing task cards or registry lineage. | Assignment log, outcome record, review pairing, registry change, and calibration note. |

## Guardrails for MoneyBall mechanics

The roster begins with an internal-points ledger for simulated bids and score-linked incentives. Its economic-system roadmap is staged: **Stage A** internal non-transferable points and deterministic accounting; **Stage B** simulation or testnet policy experiments; and **Stage C** a separately approved future real-wallet architecture with explicit custody, signer isolation, spend-policy, transaction-preview, recovery, and independent security-review records. A rotation must be dry-run capable, reversible, and auditable at every stage.

| Mechanic | Required control |
|---|---|
| Task routing | Match on role-specific score and confidence, then apply shared safety floor; do not route solely on aggregate ELO. |
| Culling | Never automatically cull security reviewers, orchestration controls, or newly created roles. Require a minimum sample, a recent review, and an Operator-approved policy. Deactivation preserves training history and must be reversible. |
| Cloning | Create a distinct candidate identity with lineage, bounded mutation, sandboxed trial tasks, and separate score history. A clone cannot inherit authorization or reviewer status. |
| Score updates | Apply only after a recorded verdict and preserve raw evidence. Failed infrastructure must not be counted as an agent failure until triaged. |
| Internal-points simulation | Use deterministic, non-transferable ledger events for early incentive and bidding experiments; retain full event history. |
| Wallet-stage promotion | Move from internal points to simulation/testnet, then to a future real-wallet architecture only through a separate decision record and security review. |
| Protected roles | Security review, delivery controls, and roster governance require separation of duties and cannot be self-scored by the candidate. |

## Game-player fleet protocol

Issue #243 creates the **Game Player Machines & Genre Teams** lane. Each game-playing task must reference an approved game-catalog entry, a declared genre role, a machine profile, a test profile, a session objective, telemetry requirements, and a reset procedure. The lane begins with the issue’s listed titles and can append new games, genres, machines, and roles through the additive registry without redesigning the roster.

| Record | Minimum contents |
|---|---|
| Game catalog entry | Stable game ID, title, genre tags, build identity, approval source, objectives, and review partner. |
| Machine profile | Stable machine ID, platform/image, hardware class, input mode, game manifest, telemetry policy, resource limits, and reset procedure. |
| Player task card | Genre role, assigned game/build, scenario, success evidence, score-event type, and reviewer. |
| Session evidence | Session ID, build/machine IDs, objective verdict, trace/log location, errors, and reset outcome. |
| Genre scorecard | Scenario coverage, objective completion, session stability, telemetry completeness, reset correctness, and resource efficiency. |

## Mobile-analysis and controlled-lab protocol

Issue #236 and related research labels enter this model through a **target-register-first intake**. The project’s own artifacts, controlled labs, supplied test builds, and approved source material are recorded with provenance, purpose, tools, and evidence expectations before work is assigned.

| Step | Required record | Stop condition |
|---|---|---|
| 1. Target intake | Target record, owner, intended research question, handling contact, and assigned lane. | No target record or unclear project relationship. |
| 2. Artifact provenance | SHA-256, source URL or owner-provided transfer record, version, and license/terms snapshot. | Artifact cannot be identified or reproduced. |
| 3. Tool and experiment design | Tool profile, method, data handling, publication audience, environment, and reset plan. | Method cannot be reproduced or the environment cannot be reset. |
| 4. Static or sandboxed analysis | Tool version, method, observations, null findings, and limitations. | Analysis requires resources outside the declared target/lab record. |
| 5. Research output | Finding, limitations, proof evidence appropriate to the target, remediation, and regression check. | Output lacks evidence, impact analysis, or a remediation path. |
| 6. Independent review | Reviewer verifies target record, evidence, reproducibility, and release classification. | Reviewer cannot validate the task card or evidence chain. |

## Initial operating cadence

The proposed cadence is a weekly review of task cards, completed score events, blocked authorization records, and reliability trends. It should be scheduled only after the proposal is accepted and the roster implementation status is reconciled. Continuous automation may collect evidence, but no scheduled process may autonomously expand permissions, select an unapproved mobile target, approve a sensitive finding, or merge a change.

## Open decisions

The first review must answer whether the repository wants the current role names to remain playful display labels or to map to the canonical charter names above. It must also set a minimum sample size, confidence method, and protected-role list before any score-driven roster rotation can occur. These decisions are itemized in [ITEMS.md](./ITEMS.md).

## References

[1] [Issue #129 — Development Teams & Emerging Technologies Research Team](https://github.com/timerloggedout-spec/termux-monorepo/issues/129)

[2] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[3] [Issue #236 — APK Investigation List](https://github.com/timerloggedout-spec/termux-monorepo/issues/236)

[4] [Lane Consolidation SSOT](../../../ops/LANE_CONSOLIDATION_SSOT.md)

[5] [Agentic builders vs reviewers](../../../AGENTIC-BUILDERS-VS-REVIEWERS.md)

[6] [Consensus rules](../../../CONSENSUS.md)
