# Workflow discovery and self-optimization — implementation plan

**Proposal:** CCEL-007  
**Base:** `master` at `056a4eea26f55f73fe01c60cddec1add0cba80b8`  
**Branch:** `feat/workflow-discovery-optimization-20261122`

## Objective

Extend the existing GitHub Actions telemetry and Tribute Pages pipeline into a continuously refreshed, read-only workflow topology and operations view. Preserve the repository's existing telemetry owner, source-of-truth hierarchy, DoE family, and Pages publishing path.

## Existing owners reused

- Workflow inventory: `scripts/ci/automation_docs.py` → `docs/ops/generated/automation-workflow-catalog.json`.
- Live run sampling: `scripts/dashboards/actions_observe.py` → `scripts/dashboards/actions_observations.json`.
- Job-duration evidence: `ops/github_telemetry/collect.py`, `ops/github_telemetry/reduce.py`, and `she.metrics.job_timestamps`.
- Telemetry page feed: `scripts/dashboards/telemetry_feed.py` → `apps/tribute-dashboard/data/telemetry-feed.json`.
- Public Pages publication: `.github/workflows/tribute-dashboard-deploy.yml` → `timerloggedout-spec.github.io/tribute/`.

## Implementation

1. Register CCEL-007 in the active CEEL work ledger.
2. Add a pure feed builder that joins the generated workflow catalog to the stamped Actions run observation and derives:
   - inventory counts by domain, trigger, schedule, and authority;
   - nested `workflow_run` edges;
   - reusable-workflow call edges;
   - observed run counts, failure rates, event mix, and duration statistics where present;
   - freshness, coverage, source fingerprint, and explicit gaps.
3. Add unit tests for nested edge extraction, unresolved upstream names, repeated references, empty/stale observations, and feed provenance.
4. Add a read-only Tribute Pages view that consumes exactly one generated feed and renders inventory, nested dependencies, schedule map, observed run statistics, and evidence gaps.
5. Wire the view into shared navigation and the sitemap; add page-contract tests.
6. Extend the existing daily/manual Actions snapshot workflow to refresh the existing run observer and generate the discovery feed. Keep the current daily cadence and avoid a second poller.
7. Preserve raw source snapshots and existing append-only history. Keep public Pages as a projection, with repository files as the durable source.
8. Add a DoE candidate design for isolated workflow-topology experiments. Keep experiments opt-in and keep synthetic benchmark findings separate from production-run evidence.

## Acceptance

- `python3 scripts/ci/automation_docs.py --check`
- `python3 -m unittest tests.test_workflow_discovery_feed -v`
- `python3 -m unittest tests.test_workflow_discovery_page -v`
- `python3 -m unittest tests.test_actions_observe -v`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
- Same immutable PR head has both repository gates green; deployment run and published source SHA are re-fetched before claiming Pages publication.

## Measurement semantics

- Workflow definition count ≠ enabled workflow count ≠ observed workflow count.
- Run count ≠ job count ≠ billable minutes.
- Public-repository standard hosted-runner minutes are free; the dashboard reports operational runner time and event volume, not private-repository billing consumption.
- Job-duration sums and workflow wall time are distinct metrics and are labeled separately.
- Missing or stale observations render as UNKNOWN / STALE, never as zero.
- The workflow observer is a bounded sample; the feed reports exact page/call/sample bounds.

## Boundaries

- Reuse the existing daily/manual collector; no parallel scheduled collector.
- Keep public dashboard pages read-only and secret-free.
- Preserve existing quota dispatcher, workflow authorities, and merge gates.
- Production workflow changes require same-SHA dual-gate evidence.
- DoE experiment arms remain opt-in and produce separate experiment evidence; synthetic tests do not establish production savings.
