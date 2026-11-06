# RIDP source census — verified repository surfaces

**Status:** active inventory; evidence captured 2026-11-06  
**Proposal:** `repository-intelligence-data-plane` · RIDP-02  
**Scope:** repository-visible implementation and operating contracts. No secret values, local VM state, or private connector files were inspected.

## Executive finding

The repository already has most of the *pieces* RIDP should connect. The primary gaps are cross-surface adoption, visibility, and explicit contracts—not a lack of components.

Do not create a second quota ledger, PAT helper, GitHub App, event receiver, lane-event store, repo tracker, context cache, or agent conductor.

## Verified surface inventory

| Surface | Evidence / path | Verified state | RIDP disposition |
|---|---|---|---|
| PAT request telemetry | `docs/ops/CADENCE-TICK-LEDGER.md` | QAC-009 phase 1 says every helper-routed PAT request emits a tick via `custom.github-pat/bin/github_pat.py::_tick`. The helper is outside this repository tree / VM-local connector; source code and live files are not available in this repo inspection. | Reuse the existing tick contract. Treat helper internals and local tick/spend files as externally owned until the lane exposes an approved interface. |
| PAT spend attribution | `docs/ops/RATE-LIMIT-2026-10-29.md`; `scripts/quota_self_counts.py`; `ops/quota/self-counts.json` | `spend.jsonl` is VM-local and not committed. The self-count report explicitly says PAT call volume is not tallied; wall events are counted. | First observability gap: approved, privacy-safe export/ingestion of existing tick evidence. No copying raw spend logs into Git. |
| Tick reducer | `scripts/cadence_tick_ledger.py`; `tests/test_cadence_tick_ledger.py` | Landed QAC-009 reducer summarizes per-principal/resource, endpoint, per-minute calls and latest remaining. The current validator checks JSON parse + required-key presence; it does not enforce field types/ranges or duplicate semantics. The documented tick includes `session`, but the current `REQUIRED` tuple does not require it. Existing tests cover required-field presence, counted/un-counted and resource separation. | Extend the QAC-owned reducer/tests through its owner; RIDP consumes its versioned feed. Do not fork it. |
| GitHub App collector | `scripts/github_app_token.py`; `scripts/github_app_bucket_proof.py`; `docs/ops/GITHUB-APP-PILOT.md`; `docs/ops/GITHUB-APP-MIGRATION-PLAN.md`; `ops/github-apps/collector-pilot/PROFILE.md` | A read-only Collector App is already created and installed on this repository. The recorded 2026-10-30 proof showed installation and PAT buckets distinct (App 5000/5000 while PAT 0). The migration plan records production workflow adoption as pending / zero at its 2026-10-30 snapshot. The minter itself directly calls the App token endpoint; it is not a fleet-wide API telemetry layer. | Do not create another App. Reconcile the current adoption state with the AppID owner and workflow evidence. Keep App, PAT and Actions installation principals distinct. |
| Actions installation quota | `docs/ops/RATE-LIMIT-2026-10-29.md`; `docs/ops/GITHUB-APP-MIGRATION-PLAN.md` | Recorded Actions `GITHUB_TOKEN` bucket is separate (1000/h per repo in the cited migration record), shared by repo workflows. QAC-009 workflow tick emission is an adoption phase. | Workflow-owner adoption and attribution remain a cross-lane task. Do not assume the PAT helper sees these requests. |
| Event intake | `docs/ops/RECEIVER-MESH.md`; `.github/workflows/receiver-process.yml`; `ops/receiver-mesh/processor/envelope.py` | Receiver Mesh is explicitly PROTOTYPE. Native GitHub Actions events are available. The processor validates a bounded envelope, but its Neon step is explicitly a stub that prints `ledger-pending`; it does not currently write to Neon even if the variable is present. | Prefer native Actions triggers for GitHub events. Reuse the existing envelope/receiver contract only where appropriate; do not create another receiver. Durable receiver ledger remains unproven. |
| Repository tracking | `docs/ops/REPO-TRACKING.md`; `scripts/tracking/fetch_snapshots.py`; `scripts/tracking/repo_tracking.py`; `.github/workflows/repo-tracking-collect.yml` | Existing snapshot fetcher owns network reads; offline reducer owns deterministic projection; a single-writer workflow owns refresh. | Consume tracking snapshots/records as domain evidence; do not create a competing project/lane tracker. |
| Dispatch-tree observation | `docs/ops/DISPATCH-TREE-FEED.md`; `scripts/dashboards/dispatch_tree_observe.py`; `scripts/dashboards/dispatch_tree_feed.py`; `.github/workflows/dispatch-tree-feed-collect.yml` | Existing observer performs network reads; pure feed builder materializes a read-only projection; daily scheduled and change/manual triggers are documented. | Treat as an existing cadence/admission observation surface. Avoid duplicating its collector or changing cadence outside cadence-owner review. |
| Agent throughput | `docs/ops/AGENT-THROUGHPUT-METRICS.md`; `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json` | ATES Phase A reducer/contract is already landed. It measures throughput and retry/parallel-yield signals; it explicitly is not a quality gate. | Add RIDP efficiency observations as separate, provenance-linked metrics; do not turn API savings or speed into merge gates. |
| SHE projection | `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md` | Existing read-only snapshot contract requires source SHA, generated time and coverage; missing evidence stays unverified/null. | Publish RIDP observations through existing projection patterns, not a new dashboard data store. |
| Agent context reuse | `docs/proposals/active/actions-refinements/IMPLEMENTATION-STATUS.md` (search result) | The repo records an existing composite action context cache: non-secret context only, strips token/cookie/secret/password/PoW-shaped fields, 32 KB cap, ephemeral runner auth state. Exact source path and API were not yet independently inspected in this pass. | Reuse after exact source/owner inspection; do not fork a new generic context cache. |
| Agent conductor / claims | `docs/ops/AGENT-TEAM-DEVELOPMENT-LANES.md` and dependency-phase/claim contracts | Conductor owns decomposition, manager selection, dependencies, claims, routing, execution, review and integration. | RIDP supplies evidence/freshness/context only. Never become a second conductor or work ledger. |

## Bucket identity — preserve separate dimensions

The rate-limit and AppID records distinguish at least:

- PAT user core (all same-user PATs share the user bucket);
- Actions `GITHUB_TOKEN` installation bucket;
- GitHub App installation bucket (the Collector App is a distinct installation principal);
- Search and Code Search resource buckets;
- GraphQL point/rate bucket.

A token string is not a principal identity. A different token for the same user is not a new user-core pool. An App installation and Actions' repository installation are not interchangeable. Preserve the resource name and reset epoch on every observation.

## Explicitly unverified / owner-gated

1. Exact current source and runtime behavior of the external `custom.github-pat` helper and its local `ticks.jsonl` / `spend.jsonl` files.
2. Current production workflow adoption of the Collector App after the 2026-10-30 migration-plan snapshot.
3. Complete census of every Actions workflow/API caller, its principal, resource bucket, calls/run and trigger cadence.
4. QAC-009 App-token tick adoption, workflow tick adoption and durable Neon ingestion status after the recorded adoption snapshot.
5. Actual durable Receiver Mesh/Neon writes; current processor source is a stub.
6. Exact source and owner contract for the existing Actions composite context cache.
7. Whether current cache/single-flight behavior is shared across agents or only within a helper/runner boundary.

These unknowns are deliberate. Do not infer adoption from an App being installed, a secret name existing, a workflow being present, or a prototype design document.

## Recommended execution order from this census

1. **Adoption evidence first:** ask the AppID, cadence, workflow and DB owners for current, source-SHA-bound adoption receipts. No credentials are needed.
2. **Close the attribution blind spot:** expose existing PAT ticks through an approved privacy-safe ingestion path; keep local raw spend logs private.
3. **Complete the workflow census:** map event trigger, workflow file, principal/bucket, network read path, cadence owner, telemetry emission and single-writer/concurrency rule.
4. **Reuse existing reducers and projections:** extend QAC's reducer and SHE/ATES feeds under their owners; keep RIDP as the cross-surface contract.
5. **Only then implement shared read coalescing/context envelopes**, using explicit authorization scope and source-SHA freshness. Preserve the Collector Bootstrap exclusion for writes, pre-write reads and verify-after-write reads.

## Safety and ownership invariants

- Never read, print, copy, commit or infer secret values.
- No new GitHub App, PAT, credential rotation, receiver, database or scheduled poller in this census phase.
- Ticks are evidence, not quota-control inputs.
- Admission uses authoritative live quota evidence and owner-approved reserve/defer policy.
- No cadence changes without cadence-owner approval and trigger accounting.
- Native GitHub event triggers first; bounded reconciliation remains owner-governed.
- Existing domain records remain authoritative; RIDP indexes and references them.
- Preserve incomplete coverage as explicit gaps, not zero.
