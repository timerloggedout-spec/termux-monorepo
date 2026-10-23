# RFP: Quota-Aware Adaptive Cadence System — Full-Thread Evaluation

Status: active — proposals requested
Reference issue: #1573 (quota consolidation blueprint)
Related: PR #1574 (Tier 0 dispatch tree), PR #1575 (Buildkite eval guard), PR #1576 (this RFP)

## 1. Mandate

This RFP evaluates the entire concept thread of the cadence program end to end,
from the state at session start to the current state, and requests proposals for
every remaining gap, improvement, extension, novel use, and integration target.
The objective: minimal calls for maximum ability — Formula 1 pit-crew cadences,
quota-aware, adaptive, nested and modularized as a decision tree across
GitHub Actions, Buildkite, Supabase, BigQuery, and Cloudflare.

## 2. Baseline state at session start (evaluated from)

- Buildkite org `founders-are-found-to-implement`, pipeline `termux-monorepo`
  mirroring github.com/timerloggedout-spec/termux-monorepo: build #1 failing,
  backlog of 23 queued builds, no cache paths (every build logged "No cache
  paths specified. Skipping cache mounting").
- 170 GitHub Actions workflows, 811 scheduled runs/day, nearly every lane on
  its own cron, no central admission, no quota accounting.
- GITHUB_TOKEN installation rate limit exhausted by unbounded recon sweeps.
- Buildkite github-actions plugin caps PR-build tokens at contents:read and
  hard-fails jobs requiring broader scopes (build 576).
- Supabase: connector provisioned, zero projects. BigQuery: auto-provisioned
  empty project. Cloudflare: deprecated Workers Bindings connector, docs only.
- No catalog, no decision-tree dispatcher, no drift guard.

## 3. Current state (already delivered — not re-proposed)

- Buildkite: build #1 fixed (pipeline env GITHUB_EVENT_NAME /
  BUILDKITE_GITHUB_EVENT: push), skip_queued_branch_builds and
  cancel_running_branch_builds on, backlog drained 23 -> 5, builds green.
  Cache volume now configured: top-level `cache: paths: [node_modules, .cache,
  vendor/bundle]` at 20g, verified live on build #2415 (nsc-cache-tag present).
- Tier 0 dispatcher `.github/workflows/quota-dispatch-tree.yml`: single */10
  cron, decision nodes A-F, conditional workflow_dispatch fan-out; 12 lanes
  taken off their own crons (fast lane, eval, recon, probe, bridge, and the
  help-wanted family). Lanes keep authorities; files not merged (interwired
  via repository_dispatch / workflow_run).
- Watermark mechanism: QUOTA_EVAL_WATERMARK repo variable advanced only after
  eval lanes wake. Admission guard: busy >= 6 pauses non-critical fan-out.
- Plugin-token guards (PR #1575): BUILDKITE_BUILD_NUMBER skips on
  pr-evidence-evaluation and workflow-surface-policy route jobs.
- Supabase project `termux-monorepo-lane-state` (us-west-1, free tier, $0/mo)
  created with the lane-state schema: lane_watermarks, dispatch_verdicts,
  stall_watch_events, recon_sweeps — all RLS enabled, service-role-only.
- Catalog at docs/ops/generated/automation-workflow-catalog.json with
  deterministic regeneration and hourly trusted refresh.

## 4. Gaps (proposals requested)

- ~158 of 170 workflows still own their own schedule triggers. Propose the
  Tier 3 migration tranche ordered by scheduled runs/day and decision-node
  reuse; new nodes must piggyback on existing probe results.
- Dispatcher state still lives in a GitHub repo variable; migrate watermarks
  and verdict history to the Supabase lane-state tables (service-role key as a
  GitHub Actions secret; fallback to repo variable on connection failure).
- No telemetry sink: BigQuery still has no project + dataset. Propose the
  per-run quota telemetry layout (runs/day per workflow, verdict fire rates,
  admission pauses) and how it is exported.
- Cache is path-configured but not policy-tuned: propose per-step cache keys
  (lockfile-based keys, branch-scoped restore/save scopes in the cache
  registry policy) and observed hit-rate targets.
- No drift guard: a migrated lane can silently re-add a schedule trigger in a
  PR. Propose a policy test or actionlint hook failing CI when it happens.
- No reconciliation: actual run counts are never diffed against the catalog.
  Propose a daily low-priority Tier 3 reconciliation fan detecting cadence
  drift repo-wide.
- Catalog lacks `runs_per_day` and `decision_node` fields; quota accounting
  should be derived, not hand-maintained.

## 5. Improvements and extensions (proposals requested)

- Extend the admission guard (busy >= 6) into a global admission service for
  pull_request workflows, deferring non-critical checks when the run pool is
  saturated.
- Generalize the watermark into a work-cursor for list-processing lanes
  (help-wanted family, recon sweeps) so each item wakes a lane exactly once.
- Dispatcher self-test: scheduled force_lane=all smoke run (weekly) proving
  every dispatch path targets a valid workflow file.
- Recon sweep mode now survives dispatcher takeover (workflow_dispatch
  `sweep` input); extend the same pattern to other formerly-scheduled-only
  lanes with distinct scheduled vs dispatched behavior.
- Buildkite pipeline currently mirrors one workflow; propose which additional
  high-value lanes deserve their own Buildkite pipelines or steps, with the
  cache volume reused.

## 6. Novel uses of the decision tree (proposals requested)

- Cross-platform dispatch: the same verdict fan-out pattern applied to
  Buildkite pipeline schedules (buildkite API create_build on verdict) so
  Buildkite lanes join the quota budget instead of running parallel crons.
- Supabase-backed verdict audit: dispatch_verdicts as the source of truth for
  post-hoc cadence tuning (fire-rate per node per hour -> adaptive thresholds
  stored in lane_watermarks).
- Cache-warm builds: use cache-hit telemetry as a dispatcher input — probe
  lanes only when the relevant dependency manifest changed.

## 7. Integration targets (proposals requested)

- Supabase (live: termux-monorepo-lane-state): lane-state cache home; watermark
  and verdict writes; lane health views.
- BigQuery (needs project + dataset): quota telemetry warehouse; cross-org
  run-rate dashboards.
- Buildkite (live cache, green pipeline): mirrored builds, cache volume,
  candidate for cross-platform dispatch membership.
- Cloudflare: deprecated Workers Bindings connector — docs only; only
  actionable if a replacement connector is provisioned.
- Linear / n8n / other connectors: propose any cadence-relevant integration
  (e.g. quota-breach incidents filed by the reconciliation fan).

## 8. Constraints (binding on all proposals)

- No new top-level cron entry points; every cadence must be reachable through
  the dispatch tree or document why it cannot be.
- Lanes keep their own authorities, permissions, and concurrency groups; the
  dispatcher holds actions:write + contents:read only.
- Buildkite PR builds cap GITHUB_TOKEN at contents:read; workflows run under
  that plugin must never require broader scopes (PR #1575 pattern).
- Catalog regeneration stays deterministic; --write-then---check must keep
  passing.
- Supabase access service-role only; RLS stays enabled; no anon policies.

## 9. Submission

Post proposals as comments on this PR or sub-issues of #1573. Each proposal
must state: problem, quota delta (scheduled runs/day saved or added), decision
nodes touched, risks, and validation plan.
