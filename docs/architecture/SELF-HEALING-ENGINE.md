# Self-Healing Engine (SHE)

**Status:** Proposed P0 architecture  
**Scope:** GitHub control plane + Termux execution + dynamically allocated agent capabilities

## Purpose

SHE is the first end-to-end autonomous factory workload. It detects failures, creates a durable incident, diagnoses the cause, dynamically dispatches authorized capabilities, produces a bounded remediation, verifies the result, promotes or escalates it, and records the outcome for future diagnosis.

> Self-healing is controlled autonomous remediation, not unrestricted self-modification.

## Architecture

```text
                         EVENT SOURCES
        GitHub Actions / repo-gate / termux-smoke / Dependabot
              tests / runtime monitors / agent failures / humans
                                   |
                                   v
                         +-------------------+
                         | FAILURE INGESTION |
                         | normalize          |
                         | deduplicate        |
                         | correlate          |
                         | fingerprint        |
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         | INCIDENT MODEL     |
                         | identity / SHA     |
                         | severity / scope   |
                         | evidence / policy  |
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         | DIAGNOSIS ENGINE   |
                         | deterministic      |
                         | history            |
                         | static analysis    |
                         | agent investigation|
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         | REMEDIATION PLAN   |
                         | known fix / repair |
                         | rollback / research|
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         | DYNAMIC DISPATCH   |
                         | capability         |
                         | authority          |
                         | availability       |
                         | history / cost     |
                         +---------+---------+
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
               GitHub worker  Termux worker  Remote worker
                    |              |              |
                    +--------------+--------------+
                                   |
                                   v
                         +-------------------+
                         | REPAIR SANDBOX    |
                         | branch/worktree   |
                         | bounded execution |
                         | evidence capture  |
                         +---------+---------+
                                   |
                                   v
                         +-------------------+
                         | VERIFICATION      |
                         | targeted tests    |
                         | repo-gate         |
                         | termux-smoke      |
                         | regression/security|
                         +---------+---------+
                                   |
                         +---------+---------+
                         |                   |
                       PASS                FAIL
                         |                   |
                         v                   v
                   PROMOTION GATE       RE-DIAGNOSE /
                         |              RETRY / ESCALATE
                    +----+----+
                    |         |
                 AUTO       HITL
                    |         |
                    +----+----+
                         |
                         v
                     RESOLVED
                         |
                         v
                  KNOWLEDGE / EVIDENCE
```

## Dynamic-agent topology

Roles are allocated at dispatch time. `Research`, `Build`, `Security`, `RE`, `Tester`, `Reviewer`, and `Synthesizer` are temporary capabilities/roles, not permanent model identities.

```text
                              TASK / INCIDENT
                                     |
                              DISPATCH ENGINE
                                     |
             +-----------------------+-----------------------+
             |                       |                       |
       capability fit         authority fit          availability
             |                       |                       |
             +-----------------------+-----------------------+
                                     |
                              WORKER POOL
                                     |
             +----------------+-----+-----+----------------+
             |                |           |                |
          Research          Build     Security           RE
             |                |           |                |
             +----------------+-----+-----+----------------+
                                     |
                              Verification
                                     |
                              Promotion Gate
```

### MoneyBall / 3L0 integration

The dispatcher should treat existing MoneyBall / 3L0 LeaderBoards, matrices, and manager concepts as **decision-support inputs**, not as authority by themselves.

```text
                     WORKER CANDIDATES
                            |
             +--------------+--------------+
             |              |              |
        capability       reliability     availability
             |              |              |
             +--------------+--------------+
                            |
                    MoneyBall / 3L0
                  scoring + matrices
                            |
                    Manager / policy
                    selection layer
                            |
                    AUTHORITY CHECK
                            |
                     FINAL DISPATCH
```

Recommended scoring dimensions include capability match, historical success, verification quality, failure rate, latency, cost/quota, workload, environment compatibility, and policy/authority compatibility. LeaderBoard scores must never override hard authorization or safety constraints.

This permits dynamic allocation such as:

```text
TASK-42
  |
  +-- Research capability -> Worker A
  +-- Build capability    -> Worker B
  +-- RE capability       -> Worker C
  +-- Review capability   -> Worker D
                 |
                 v
            Synthesized repair
```

The same task can select a completely different worker set tomorrow.

## Dependabot integration

Dependabot is already an autonomous GitHub security signal. SHE should ingest Dependabot alerts/PRs into the same incident/evidence fabric instead of inventing a permanently assigned Security Agent.

```text
Dependabot -> security signal -> incident/task -> dynamic dispatch
```

Possible routing:

- safe dependency update -> maintenance capability
- breaking update -> compatibility/research capability
- suspicious or novel vulnerability -> security/RE capabilities
- policy conflict -> escalation/HITL

## Healing levels

### L0 — Automatic recovery

No source mutation: retry, restart, reconnect, refresh, regenerate transient state, reacquire locks, or rollback a known transient state.

### L1 — Automatic repair

Bounded code/config mutation: dependency update, known syntax repair, workflow repair, generated artifact regeneration, or other policy-approved remediation. Must produce evidence and pass gates.

### L2 — Evolutionary repair

Novel failure: generate competing hypotheses, run isolated experiments, benchmark candidates, produce a repair proposal, and promote only through the applicable gate.

## Core state machine

```text
DETECTED -> TRIAGED -> DIAGNOSING
                     |       |
                     |       +--> RESEARCH --> PLANNED
                     +----------> KNOWN FIX -> PLANNED

PLANNED -> DISPATCHED -> REMEDIATING -> VERIFYING
                                      |          |
                                      |          +--> FAILED -> RETRY / RE-DIAGNOSE
                                      |
                                      +--> PASSED -> PROMOTING
                                                      |
                                              +-------+-------+
                                              |               |
                                           AUTO-PROMOTE       HITL
                                              |               |
                                              +-------+-------+
                                                      |
                                                   RESOLVED
                                                      |
                                                   LEARNED

Other terminal/escalation states: QUARANTINED, ESCALATED, ROLLED_BACK, ABANDONED.
```

## GitHub execution flow

```text
GitHub event
  -> Actions ingestion
  -> incident creation/update
  -> evidence persistence
  -> diagnosis
  -> dynamic dispatch
  -> repair branch/worktree
  -> commit + PR
  -> repo-gate / termux-smoke / domain checks
  -> review + policy gate
  -> merge/promotion
  -> post-merge validation
  -> incident resolution + learning
```

The repair PR is itself a durable healing artifact. Autonomous operation must remain inspectable and attributable.

## Termux execution flow

```text
GitHub dispatch
  -> Termux daemon
  -> verify handoff + authority
  -> isolated workspace
  -> diagnostics
  -> remediation
  -> tests
  -> evidence/result
  -> GitHub
```

Termux is an execution/edge environment, not the authoritative durable state store.

Local Termux recovery may independently handle daemon crashes, stale processes, transient services, cache corruption, resource exhaustion, and interrupted jobs before escalating to GitHub.

## Incident requirements

Every incident should carry:

- stable incident ID
- source and event provenance
- repository/ref/SHA
- severity and classification
- evidence references
- allowed actions / authority scope
- state and transition history
- selected capabilities/workers
- remediation plan
- verification results
- promotion/rollback result
- learning record

## Retry and rollback

Retries are reason-aware. Deterministic failures should trigger re-diagnosis rather than blind repetition. Provider failures may select an alternate worker. Repeated identical remediation failure escalates.

Every autonomous promotion needs a reverse path:

```text
PROMOTED -> POST-MERGE MONITOR -> REGRESSION -> ROLLBACK / HITL
```

## Knowledge loop

```text
INCIDENT -> DIAGNOSIS -> REMEDIATION -> RESULT
    -> PATTERN EXTRACTION -> KNOWLEDGE -> FUTURE TRIAGE
```

Learned remediation must retain provenance: source incident/SHA, diagnosis, remediation, verification, success/failure history, scope, confidence, and promotion context.

## Priority

SHE is **P0**. ArchW1z and deepcli-TUI remain parallel Termux UI lanes and are intentionally lower priority than the underlying resilience/control-plane primitives. Their eventual convergence should occur through the shared protocols rather than by making either UI the protocol authority.
