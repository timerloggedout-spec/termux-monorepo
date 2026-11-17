# Admin Interaction Graph — live runtime events

**Status:** runtime event intake deployed; dashboard integration in this change.
**Source of truth:** GitHub Actions `workflow_job` lifecycle events plus authoritative workflow-run state from the Actions API.
**Transport:** Cloudflare Worker `admin-graph-live` + D1 `admin-graph-runtime-events`.
**Read model:** `GET /events`; publisher: `.github/workflows/admin-graph-runtime-publisher.yml`.

## Event path

1. GitHub emits `workflow_job` queued/in-progress/completed events for all
   workflows. The Worker resolves each job's authoritative workflow-run record
   through the Actions API and stores both workflow-level and job-level state.
   A two-minute bounded run snapshot reconciles final workflow conclusions that
   can arrive just after the last job-completed delivery.
2. The observer workflow mints a read-only GitHub App installation token
   with Actions read scope. It never checks out or executes the triggering SHA.
3. `scripts/ops/admin_graph_runtime_event.py` emits a closed metadata
   envelope: run/attempt, job ID/name, state, SHA, timestamps, URL and actor.
   It excludes logs, prompts, completions, tool arguments, credentials and
   arbitrary payloads.
4. The Worker verifies the token against the repository's Actions API,
   verifies each run and job ID, and inserts events idempotently into D1.
5. The dashboard polls the read-only event feed and animates only observed
   lifecycle transitions. The initial load may show currently active jobs;
   historical completed events are listed but not replayed as fresh pulses.

## Endpoints

- `GET /health` — intake health and row count.
- `POST /ingest` — authenticated publisher only; GitHub App token required.
- `GET /events?limit=200` — public read-only event projection for GitHub Pages.

The Worker is deployed on `admin-graph-live.timerloggedout.workers.dev`.
The D1 database is `admin-graph-runtime-events`; its schema is versioned at
`ops/admin-graph-live/schema.sql`, and deployment bindings are declared in
`ops/admin-graph-live/wrangler.toml`. CORS is restricted to
`https://timerloggedout-spec.github.io`.

## Semantics and limits

- This is near-real-time event delivery, not a fabricated animation. GitHub
  webhook-triggered Actions runs publish state changes as separate events.
- Browser refresh interval is 10 seconds; the scheduled workflow-state
  reconciliation runs every two minutes. Delivery latency also includes
  GitHub's webhook scheduling and the observer workflow startup time.
- Workflow and job lifecycle are observed. Step-level detail, agent tool-call
  spans and handoffs are not claimed unless a producer emits them under a
  separate approved event contract.
- The existing Neon `lane_events` ledger and ATES artifacts remain intact;
  this read projection does not replace them.
- Missing delivery is visible as stale feed health; no synthetic pulse or
  heartbeat event is generated.


## Walkthrough

A narrated implementation preview is published in the public video library:
[Admin Interaction Graph — live runtime walkthrough](https://timerloggedout-spec.github.io/videos.html).
The video is an explanatory motion-graphics walkthrough, not a screen recording of
a production-active dashboard. It describes the workflow/job event path, metadata
boundary, API verification, D1 projection, dashboard polling and health semantics.
Production activation remains conditional on merge, deployment and live-event
verification.
