# Admin Interaction Graph — route and runtime pulse contract

**Status:** Route-event publisher and cursor-aware reader are staged in this change. The existing Worker/D1 deployment remains the live runtime endpoint; the Worker code update and publisher activation require merge plus deployment.

## Required behavior

Every recognized task-routing claim produces one durable task_routed event. The Admin Interaction Graph consumes that event and animates the Routing / Who? → Orchestrator edge. The event is correlated to subsequent workflow/job activity through the task issue reference and, where present, the dispatch ID.

The pulse certifies the observed routing transition. Execution, provider completion, review acceptance, and merge remain separate lifecycle states.

## Producers

- PRODUCER CLAIM comments emitted by scripts/dispatch/claim_task.py.
- PRODUCER CLAIM comments emitted by scripts/ops/dispatch_executor.py; the dispatch-executor role and arm/dispatch fields identify this route class.

The observer filters for these exact claim markers. It extracts only task reference, route role, provider or arm/model, dispatch ID, comment ID, timestamp, and actor identity for provenance verification. Actor identity and comment content remain outside the stored route payload. Producer labels, session identifiers, prompts, completions, tool arguments, credentials, and logs remain outside the event store.

## Event lifecycle

1. A routing producer posts its claim comment.
2. GitHub emits issue_comment.created for app-authored claim comments; the scheduled API reconciliation also scans recent issue comments to capture GITHUB_TOKEN-authored claims.
3. admin-graph-runtime-publisher.yml normalizes the claim into task_routed.
4. The Worker verifies the publisher run and retrieves the source issue comment through the GitHub API.
5. D1 inserts the event under deterministic ID route:{issue_number}:{comment_id}.
6. The graph polls by monotonic D1 row cursor, persists the last sequence in browser local storage, and animates every newly observed event after the saved position.
7. GitHub workflow_job events and bounded run snapshots supply execution-state pulses. The scheduled reconciliation uses a 15-minute overlap and deterministic comment IDs to recover token-suppressed webhook events.

Repeated webhook deliveries resolve to the same event ID. The event reader uses after_seq pagination so bursts preserve event order across poll windows.

## Event envelope

admin-graph-live-events/v1 carries bounded operational metadata:

- id, kind, event, status
- workflow, job, step
- repo, run_id, run_attempt, job_id
- head_sha, url, occurred_at, received_at, seq
- route payload: task_ref, issue_number, source_comment_id, source, route_role, provider, arm_id, model, dispatch_id

## Endpoints

- GET /health — intake health and row count.
- POST /ingest — authenticated publisher only; GitHub App token required.
- GET /events?limit=400 — recent read-only event projection.
- GET /events?after_seq=N&limit=400 — ordered incremental projection.

The Worker is admin-graph-live.timerloggedout.workers.dev. D1 is admin-graph-runtime-events; schema and binding remain in ops/admin-graph-live/.

## Verification

The normalizer tests cover producer claims, executor claims, unrelated comments, workflow jobs, snapshot reconciliation, stable IDs, and privacy filtering. The page contract pins the live route feed, cursor reader, and graph edge mapping.

Runtime health and route-event ingestion remain separate states: a healthy empty feed proves transport readiness, while a stored route event proves producer activation and end-to-end pulse delivery.
