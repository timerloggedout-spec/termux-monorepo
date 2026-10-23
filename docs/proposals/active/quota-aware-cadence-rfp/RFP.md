# RFP: Quota-Aware Cadence Extensions and Automation Gaps

Status: active — proposals requested
Reference issue: #1573 (quota consolidation blueprint)
Related: PR #1574 (Tier 0 quota dispatch tree), PR #1575 (Buildkite eval guard)

## 1. Purpose

The Tier 0 quota dispatch tree (quota-dispatch-tree.yml, PR #1574) replaces 12
independent scheduled lanes with a single 10-minute decision run and conditional
workflow_dispatch fan-out, cutting fast-lane scheduled runs from ~610/day toward
~300/day repo-wide. This RFP requests proposals for the remaining gaps,
extensions, novel uses, and new integration targets so the cadence system can
reach its ~300/day target and stay there under growth.

## 2. Scope of proposals requested

Proposals may cover any of the following. Each must state quota impact
(scheduled runs/day saved or added) and blast radius.

### 2.1 Remaining Tier 3 candidates

~158 workflows still own their own schedule triggers (of 170 total). The
decision-tree pattern is proven; propose the next tranche to migrate, ordered by
scheduled runs/day and by decision-node reuse (new nodes should piggyback on
existing probe results wherever possible).

### 2.2 Catalog extensions

- Add a `runs_per_day` field per workflow to
  docs/ops/generated/automation-workflow-catalog.json, computed from cron
  expressions and dispatcher verdicts, so quota accounting is derived rather
  than hand-maintained.
- Add a `decision_node` field mapping each dispatched lane to the dispatcher
  node that wakes it, enabling static verification that no lane is orphaned.

### 2.3 Cross-platform telemetry targets

- BigQuery (auto-provisioned project, currently empty): propose a project and
  dataset layout for per-run quota telemetry (runs/day per workflow, verdict
  fire rates, busy-admission pauses), plus an access policy for the
  dispatch-tree to publish or for a lane to export.
- Supabase (connector provisioned, zero projects): propose the lane-state
  cache home — watermark values, verdict history, stall-watch state — so the
  dispatcher no longer relies on repo variables for watermarks.
- Buildkite (org founders-are-found-to-implement): agent cache paths are
  unconfigured ("No cache paths specified" on every build). Propose the cache
  path set (e.g. ~/.cache/pip, node_modules, .termux-build) and cache
  population policy.

### 2.4 Novel uses of the decision tree

- Reuse the dispatcher's admission guard (busy >= 6) as a global admission
  service for pull_request workflows, deferring non-critical checks when the
  run pool is saturated.
- Extend the watermark mechanism to a generic "work cursor" for any
  list-processing lane (help-wanted family, recon sweeps) so each item wakes a
  lane exactly once.

### 2.5 Feature proposals

- Tier 3 reconciliation fan: a daily low-priority lane that diffs actual
  workflow runs against the catalog to detect cadence drift (new crons merged
  outside the tree, lanes re-adding schedule triggers).
- Dispatcher self-test: force_lane=all smoke run on a schedule (weekly) to
  prove every dispatch path still targets a valid workflow file.
- Drift guard in CI: actionlint or a policy test failing when a migrated lane
  file reintroduces a schedule trigger.

## 3. Constraints (binding on all proposals)

- No new top-level cron entry points; every cadence must be reachable through
  the dispatch tree or document why it cannot be.
- Lanes keep their own authorities, permissions, and concurrency groups; the
  dispatcher holds actions:write + contents:read only.
- Buildkite PR builds cap GITHUB_TOKEN at contents:read; any workflow run under
  that plugin must not require broader scopes (see PR #1575 pattern).
- Catalog regeneration stays deterministic; the --write-then---check sequence
  must keep passing.

## 4. Submission

Post proposals as comments on this document's PR or as sub-issues of #1573.
Each proposal should include: problem, quota delta, decision nodes touched,
risks, and validation plan.
