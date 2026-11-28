# Label consumer census

Snapshot: `feat/trigger-workflow-registry`, 2026-11-27. This census maps source-referenced labels to producers and consumers. It is a selected, source-backed relationship set, not a live exhaustive repository label inventory.

| Label | Role | Producer | Consumer | State |
|---|---|---|---|---|
| `project-task` | intake-selector |  | `.github/workflows/project-task-dispatch.yml` | routing-input |
| `jules` | agent-selector | `operator-applied issue label` | `.github/workflows/agent-jules-on-issues.yml` | agent-dispatch-input |
| `dispatch-queued` | queue-state | `.github/workflows/project-task-dispatch.yml`, `.github/workflows/game-development-dispatch.yml` | `scripts/dispatch/claim_task.py`, `scripts/dispatch/auto_claim.py` | queue-ready |
| `dispatch-claimed` | queue-state | `scripts/dispatch/claim_task.py` | `scripts/dispatch/auto_claim.py` | claimed |
| `intake-incomplete` | intake-outcome | `.github/workflows/project-task-dispatch.yml`, `.github/workflows/game-development-dispatch.yml` |  | validation-failure |
| `swarm-admitted` | admission-outcome | `.github/workflows/swarm-admission.yml` |  | admitted |
| `deferred-by-tier` | admission-outcome | `.github/workflows/swarm-admission.yml` |  | deferred |
| `delphi:rfp` | domain-queue | `.github/ISSUE_TEMPLATE/delphi-rfp.yml` | `.github/workflows/delphi-gate.yml`, `scripts/delphi/rfp_flood_fetch.py` | domain-intake |
| `target-brief` | intake-selector | `.github/ISSUE_TEMPLATE/target-brief.yml` | `.github/workflows/target-intake.yml` | routing-input |
| `hark:queue` | external-work-queue | `.github/workflows/hark-enqueue.yml`, `scripts/que/self_repair.py` | `docs/hark-bridge.md`, `scripts/que/self_repair.py` | queued-for-hark |
| `delphi:shadow` | domain-state | `Delphi gate award/state process` | `scripts/delphi/signals.py` | shadow-monitoring |
| `sr:verified` | learning-outcome | `self-repair verification close-out` | `scripts/que/self_repair.py` | positive-learning-signal |
| `sr:regression` | learning-outcome | `self-repair regression close-out` | `scripts/que/self_repair.py` | negative-learning-signal |

## Confirmed behavior

- `project-task` is an intake selector; `dispatch-queued` is a queue state consumed by claim machinery; `dispatch-claimed` records the claim transition.
- `jules` is a trusted label-triggered agent route. The comment mention arm is a separate selector and is catalogued in the workflow-trigger census.
- `swarm-admitted` and `deferred-by-tier` are admission outcomes written by `swarm-admission`; the current census has not established downstream label consumers for either.
- `delphi:rfp` gates the Delphi workflow; `target-brief` gates target intake; `hark:queue` is a scheduled external work queue.
- `delphi:shadow` gates the shadow-success signal; `sr:verified` and `sr:regression` feed self-repair learning weights.
- The deterministic issue-lifecycle triage script proposes only from its fixed `KNOWN_LABELS` allowlist and applies only to unlabelled issues; this is a narrow label producer, not the full repository taxonomy.

## Coverage limits

The GitHub read connector used for this pass supports repository content and code search but rejected the repository labels collection endpoint. Therefore this artifact records labels evidenced in source and documentation; it does not claim a current live label count, description, color, or complete label list. The `ISSUE-LIFECYCLE.md` label counts are historical snapshots (97 on 2026-10-27; 106 on 2026-11-02), so they remain historical evidence rather than current counts.

Several producer/consumer entries are source-level references. Workflow runs and current issue states are separate runtime evidence and are outside this static census.
