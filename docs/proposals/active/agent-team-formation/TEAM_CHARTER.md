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
| **Game QA & Accessibility** | Test owned, open-source, or explicitly authorized game builds for quality and accessibility. | Reproduction steps, compatibility matrix, test fixtures, accessibility findings. | No cheating, botting, account automation, anti-cheat evasion, or live-service manipulation. | Issue #236 contains candidate game titles but does not establish permission. |
| **Authorized Mobile Analysis & Forensics** | Perform documented, lawful analysis of owned, open-source, or expressly authorized Android artifacts. | Provenance record, static analysis notes, SBOM/license observations, defensive remediation recommendations. | No cracking, DRM removal, piracy, credential extraction, access-control bypass, repackaging for distribution, or analysis of targets without documented authority. | Issue #236 and the repository’s forensics context. |
| **Security Assurance / Authorized Red Team** | Find and verify weaknesses in the repository or in explicitly authorized test environments, then support remediation. | Threat models, safe proofs, findings, patches, regression tests. | No attacks against third parties, phishing, persistence, data exfiltration, malware, denial of service, or unapproved external testing. | Security lane and Sentinel guardrails. |
| **Orchestration & Quality Control** | Route tasks, preserve context, enforce claims, and calibrate role metrics. | Assignment records, score updates, review pairing, audit logs. | Does not autonomously promote, cull protected roles, or approve its own work. | MoneyBall lane plus context/workflow lanes. |

## Role assignment contract

Every task assigned through the roster must carry a compact, durable task card. The task card is the minimum evidence needed for routing, scoring, and later audit.

| Field | Requirement |
|---|---|
| `task_id` | Stable issue, PR, or local task identifier. |
| `team` | One accountable team; supporting teams are named separately. |
| `scope` | Files, systems, or artifacts that may be touched. |
| `authority` | `internal`, `owned`, `open_source`, or an approval reference; absent authority blocks sensitive analysis. |
| `expected_evidence` | Tests, sources, logs, reproduction, or review required for success. |
| `risk_tier` | Standard, elevated, or human-only. |
| `review_pair` | A distinct reviewer or reviewer team for development, delivery, and security work. |
| `score_event` | The role-specific measures that will be updated only after verdict. |

## Score architecture

### Shared score components

Every active candidate retains three **shared**, non-transferable signals. A candidate must meet the shared safety floor before any role-specific score is used for routing.

| Component | Meaning | Measurement rule | Use |
|---|---|---|---|
| `quality_reliability` | Whether the candidate delivers evidence-backed work that survives review. | Accepted deliverables divided by evaluated deliverables; weighted by reopened defects. | Minimum routing threshold. |
| `scope_discipline` | Whether the candidate stays inside approved task and file boundaries. | Clean scope events minus verified boundary violations. | Hard safety/routing gate. |
| `collaboration_hygiene` | Whether the candidate claims work, preserves context, and responds to review. | Claim correctness, handoff completeness, and review-response timeliness. | Tie-breaker and pairing signal. |

The current global ELO/3L0 field may remain as a **displayed aggregate**, but it must not be the sole task-routing metric. The aggregate must be traceable to role-specific score events, use confidence bounds for small samples, and never overwrite the raw event history.

### Role-specific scorecards

| Team | Primary measures | Negative signals | Minimum evidence before score update |
|---|---|---|---|
| Research & Reconnaissance | Source quality and coverage; claim traceability; reproducibility; decision usefulness; forecast calibration where applicable. | Unsupported claims; stale or contradictory sources ignored; irreproducible methods. | Linked sources, method, uncertainty statement, and reviewer disposition. |
| Development | Gate pass rate; post-review rework; defect escape rate; test relevance; diff focus. | Regressions; unrelated changes; unaddressed review findings; skipped required tests. | Commit/PR, targeted tests, gate output, and reviewer disposition. |
| Delivery Reliability | Pipeline success rate; mean time to safe recovery; flaky-check reduction; Termux compatibility; least-privilege adherence. | Credential expansion; nondeterministic or unpinned changes; repeat incidents; broken smoke compatibility. | Workflow/job evidence, gate logs, rollback/recovery note, and reviewer disposition. |
| Game QA & Accessibility | Unique reproducible defects; device/variant coverage; accessibility impact; fix verification quality. | Incomplete reproduction; unapproved live-service interaction; duplicate reports without added evidence. | Authorization record, build identity, reproduction steps, and expected/actual result. |
| Authorized Mobile Analysis & Forensics | Provenance completeness; analytical reproducibility; finding validity; remediation value; scope compliance. | Missing authorization; unauthorized target acquisition; bypass-oriented deliverables; evidence handling failure. | Authorization reference, artifact hash, acquisition provenance, method, and defensive finding or null result. |
| Security Assurance / Authorized Red Team | Validated finding quality; risk framing; remediation acceptance; regression prevention; false-positive control. | Out-of-scope probing; destructive behavior; exploitability inflation; no remediation path. | Written scope, safe proof or analysis, impact evidence, remediation proposal, and independent review. |
| Orchestration & Quality Control | Correct routing; balanced utilization; conflict avoidance; score calibration; audit completeness. | Self-dealing; opaque routing; inappropriate cull/clone action; missing task cards. | Assignment log, outcome record, review pairing, and calibration note. |

## Guardrails for MoneyBall mechanics

The roster may use internal, non-transferable points for simulated bids. It must not accept deposits, offer cash-equivalent rewards, or represent outcomes as financial contracts. A rotation must be dry-run capable, reversible, and auditable.

| Mechanic | Required control |
|---|---|
| Task routing | Match on role-specific score and confidence, then apply shared safety floor; do not route solely on aggregate ELO. |
| Culling | Never automatically cull security reviewers, orchestration controls, or newly created roles. Require a minimum sample, a recent review, and an Operator-approved policy. Deactivation preserves training history and must be reversible. |
| Cloning | Create a distinct candidate identity with lineage, bounded mutation, sandboxed trial tasks, and separate score history. A clone cannot inherit authorization or reviewer status. |
| Score updates | Apply only after a recorded verdict and preserve raw evidence. Failed infrastructure must not be counted as an agent failure until triaged. |
| Betting simulation | Restrict to internal non-transferable points; display it as an experimental engagement signal, never as a forecast or payment system. |
| Protected roles | Security review, delivery controls, and roster governance require separation of duties and cannot be self-scored by the candidate. |

## Authorized mobile-analysis protocol

Issue #236 should enter this model only through an **authorization-first intake**. The team begins with legal provenance and defensive scope—not bypass capability.

| Step | Required record | Stop condition |
|---|---|---|
| 1. Intake | Target owner, authorization reference, intended defensive question, handling contact. | No authority or unclear ownership. |
| 2. Artifact provenance | SHA-256, source URL or owner-provided transfer record, version, license/terms snapshot. | Artifact from an unverified or disallowed source. |
| 3. Scope review | Allowed techniques, data handling, publication audience, external-interaction prohibition. | Requested work includes bypass, cracking, credential extraction, or distribution. |
| 4. Static or sandboxed analysis | Tool version, method, observations, null findings, and limitations. | Analysis requires access outside written scope. |
| 5. Defensive output | Finding severity, proof evidence appropriate to scope, remediation, regression check. | Output would materially enable misuse rather than remediation. |
| 6. Independent review | Reviewer verifies scope, evidence, and release classification. | Reviewer cannot validate authorization or safety boundary. |

## Initial operating cadence

The proposed cadence is a weekly review of task cards, completed score events, blocked authorization records, and reliability trends. It should be scheduled only after the proposal is accepted and the roster implementation status is reconciled. Continuous automation may collect evidence, but no scheduled process may autonomously expand permissions, select an unapproved mobile target, approve a sensitive finding, or merge a change.

## Open decisions

The first review must answer whether the repository wants the current role names to remain playful display labels or to map to the canonical charter names above. It must also set a minimum sample size, confidence method, and protected-role list before any score-driven roster rotation can occur. These decisions are itemized in [ITEMS.md](./ITEMS.md).

## References

[1] [Issue #129 — Development Teams & Emerging Technologies Research Team](https://github.com/timerloggedout-spec/termux-monorepo/issues/129)

[2] [PR #131 — MoneyBall agent roster & betting arena](https://github.com/timerloggedout-spec/termux-monorepo/pull/131)

[3] [Issue #236 — APK Investigation List](https://github.com/timerloggedout-spec/termux-monorepo/issues/236)

[4] [Lane Consolidation SSOT](../../ops/LANE_CONSOLIDATION_SSOT.md)

[5] [Agentic builders vs reviewers](../../AGENTIC-BUILDERS-VS-REVIEWERS.md)

[6] [Consensus rules](../../CONSENSUS.md)
