# REPO-TRACKING — one surface: lane × project × state × last-merge × next

`[MUSEai]@{role:{main}}` task `tracking-system` (2026-10-31): repo-org
tracking was started and revised many times. This surface **builds on**
those systems — it replaces none of them.

## Demand and cadence interaction

The Quota Dispatch Tree is a hybrid adaptive admission controller: PR lifecycle
events, completed lane-events recorder runs, and pushes to canonical source
records wake it immediately. The hourly schedule is only a cadence clock
for time-only slots; it is not a ten-minute polling sweep and is not the Lane
Matrix refresh mechanism. State changes wake demand work immediately.
Phase-window dispatches run only on scheduled wakes, while event wakes evaluate
current demand/staleness. See [Adaptive Dispatch](ADAPTIVE-DISPATCH.md) for the
trigger matrix, admission rules, and authenticated Issue HITL force path.

## Authority map

This is the repository's **cross-domain lane×project state projection**. Its
canonical feed is `ops/tracking/tracking.json`; the Markdown board and dashboard
feed are generated projections. It supersedes the legacy #175 issue as an
operator-priority/status surface.

Scope boundaries are deliberate:
- `docs/ops/generated/lane-matrix-status.*` is the narrower open-PR disposition
  board, not lane×project state.
- `docs/agentic/dependency-phases.json` plus
  `docs/agentic/phase-approvals.json` own dependency-phase lifecycle and approvals.
- `ops/lane-events` is an append-only execution-evidence ledger, not project state.
- Domain registries remain authoritative within their domains; this feed joins
  them but does not overwrite them.
- Desk.html and the owning GitHub Issue/PR capture human decisions and exceptions;
  no generic issue is a global hub.


## Recon — existing systems + verdicts (firsthand, master @ 2026-10-31)

| System | Where | Verdict |
|---|---|---|
| Challenge coordinator | `ops/challenge/coordinator.json` + `docs/ops/CHALLENGE-SCHEMA.md` | **KEEP — record of record** for challenge events/dates/submissions. Entries-lane single-writer. Challenges-domain only. |
| Desk feed | `ops/challenge/desk-feed.json` (`desk-feed/v1.2`) + render copy `apps/tribute-dashboard/data/desk-feed.json` | **KEEP — record** for desk traversals (status/evidence/next per D-entry). Hand-refreshed by desk lane via PR; challenges/desk only. |
| Lane-events (Neon) | `ops/lane-events/{schema,insert}.sql`, `scripts/ops/lane_event.py`, `lane-events-recorder.yml` | **KEEP — event ledger.** Append-only workflow-run events (`lane, workflow, conclusion, head_sha`); durable, queryable. Not project state. |
| Lane-matrix sweep | `scripts/ops/lane_matrix_sweep.py` → `docs/ops/generated/lane-matrix-status.{json,md}` | **KEEP — PR-disposition board** (EXTRACT/CANDIDATE/NEED_EVIDENCE/SUPERSEDE). PR-centric, not lane×project; last generated 2026-10-29 at recon. |
| Surface feeds | `scripts/dashboards/surface_feeds.py` → `apps/tribute-dashboard/data/*-feed.json` (3L0/MoneyBall/MVT/DoE/ATES) | **KEEP — pattern of record**: stamped observation snapshots, collector never calls network, honesty rules, refresh automation. Per-surface only. |
| Dispatch-tree feed | `scripts/dashboards/dispatch_tree_feed.py` | KEEP — quota cadence/admission only. |
| Domain boards | challenge-osint / countdowns, `ops/quota/*.json`, operator-matrix, reviewer-metrics, telemetry-ingest | KEEP — each is its domain's record; none spans domains. |
| Monikers/roster | `docs/ops/AGENT-MONIKERS.md`, `AGENT-TEAM-ROSTER.md` | KEEP — lane identity source. |

**Historical gap statement (before this surface):** no single surface joined
`lane × project × state × last-merge × next` across
{challenges ∘ quota ∘ doe ∘ classifiers ∘ desk ∘ webdev/viz ∘ marketing ∘
opportunities ∘ swarm ∘ providers ∘ replay}, and none auto-derives that
join from the PR feed + lane-events. Every prior board is per-domain,
hand-refreshed, or PR-centric.

## The surface

| Piece | Path |
|---|---|
| Canonical feed | `ops/tracking/tracking.json` (`repo-tracking/v1`) |
| Human board | `ops/tracking/tracking.md` (generated; this doc's render surface) |
| Desk/viz render copy | `apps/tribute-dashboard/data/tracking-feed.json` (byte-identical payload; pages consume the feed and nothing else) |
| Generator | `scripts/tracking/repo_tracking.py` (offline; reads records + snapshots only) |
| Snapshot fetcher | `scripts/tracking/fetch_snapshots.py` (workflow-side network only) |
| Snapshots | `scripts/tracking/pr_feed_snapshot.json`, `scripts/tracking/lane_events_snapshot.json` |
| Seed registry | `ops/tracking/projects.json` — identity + match rules + lane of record **only; no state** |
| Nested-family record | `ops/tracking/nested-family.json` (`nested-family/v1`) + twin `apps/tribute-dashboard/data/nested-family-feed.json` — provider ⊃ model ⊃ {roles, tasks run} with dispatch connection; spec: [NESTED-FAMILY.md](NESTED-FAMILY.md) |
| Backup-state record | `ops/tracking/backup-state.json` (`backup-state/v1`) + twin `apps/tribute-dashboard/data/backup-state-feed.json` — backup export history, drill verdicts, current marker (metadata only); spec: [BACKUP-STATE.md](BACKUP-STATE.md) |
| Single-writer | `.github/workflows/repo-tracking-collect.yml` |
| Tests | `tests/test_repo_tracking.py` |

**Feed top-level:** `{schema, generated_at, generated_by, sources{pr_feed, lane_events, records}, honesty_rules[], summary{rows, by_domain, by_state}, rows[], doe_join{summary, campaigns[]}, gaps[]}` — summary counts live under `summary{}` (viz note, PR #2941); renders read them there.

**Row:** `{lane, project, domain, project_id, state, last_merge{pr, sha, at, title}, next, next_basis, evidence[], updated_at}`.

## Derivation (deterministic; generator code is the spec)

- **last-merge** — newest merged PR in the PR-feed snapshot whose
  title/branch/labels match the project's seed match rules.
- **state** — record terminal state (coordinator/desk-feed:
  landed/closed/blocked) wins → else open PR ⇒ `in-flight` → else
  last-merge age ≤14d `active`, ≤45d `quiet`, else `stale` → else
  `unknown`. Lane-event failures are **never** a state (a red workflow
  ≠ a blocked lane); they appear in evidence.
- **next** — fixed priority: record `next` (desk-feed) → coordinator
  deadline → oldest-signal open PR (`land/close PR #N`) → latest
  lane-event failure (`investigate …`) → `NOT_ESTABLISHED`.
- **lane-events join** — snapshot carries the latest 200 Neon
  `lane_events` rows (SQL-over-HTTP, `LANE_EVENTS_DATABASE_URL` by name
  only); per-lane latest + failures join rows whose seed lane matches.
  Secret absent ⇒ `status=not_configured`, a named gap, never a failure.
- **classification** — first-match over `projects.json` in file order
  (specific projects precede generic domain buckets). Unclassified
  merged PRs are counted in `gaps` — the fix is a match-rule PR to the
  seed, never a hand-edit of the outputs.
- **provider × DoE join (`doe_join`)** — the joined view the quota
  surface does not carry (quota page = pools, its own scope; this join
  = which configured instances are planned/recorded/dispatched, per
  campaign). Per campaign (dir under `experiments/doe/` with a readable
  `DESIGN.json`): identity + `design_factors` verbatim from
  `DESIGN.json` (context only — never a source of instance rows);
  instance tuples collected recursively from `PLAN*.json` (planned),
  `records/**/*.json` (recorded) and `dispatch/**/*.json`
  (dispatched) — every `instance` dict carrying
  provider/model/instance_key (`treatment.instance` in EXPERIMENT
  records, `rows[].instance` in plans) — normalized to `{provider,
  model_at_version, role, prompt (system_prompt ref#sha12), moniker,
  context, instance_key}`, grouped by `instance_key` (DOE-FAMILY
  doctrine: never by model alone), per-source occurrence counts.
  `experiment_records`/`experiment_records_with_instance` count the
  campaign's EXPERIMENT records (top-level `treatment`) and how many
  carry an instance tuple; records without one (arm-only treatments)
  are counted, never joined. A campaign with no instance tuple
  anywhere is `join_state: design_only`, rendered `NOT_ESTABLISHED`.

## Rules

- **Single-writer:** only `repo-tracking-collect.yml` writes the three
  outputs + snapshots. PR lifecycle events refresh PR state immediately;
  `workflow_run` after `lane events recorder` refreshes the append-only event
  join; pushes to source-record/seed paths refresh domain changes. A daily
  07:23 UTC anti-entropy pass remains only for external backup-repository
  metadata because no authenticated cross-repository event hook is established.
  There is no manual `workflow_dispatch` entry point.
  Anyone hand-editing an output creates a fork the next run overwrites.
  Reads + commit run on a **Swarm App token** (own 5000/h bucket): the
  shared `GITHUB_TOKEN` bucket (1000/h/repo) returned HTTP 403 during a
  merge storm and degraded the 2026-11-01T04:11Z generation (fail-soft
  recorded it in the snapshot status + feed gaps). Push triggers exclude
  the snapshots/outputs themselves — the writer's own commits never
  retrigger the collect.
- **VM = sandbox:** the standing mechanism is this workflow. No VM
  cron/daemon participates.
- **Honesty:** values no source holds render as `NOT_ESTABLISHED` or a
  named gap. Counts are derived from the stamped snapshots at
  generation time (`sources.pr_feed.read_at`, `sources.lane_events.*`
  ride in every output) — never copied forward.
- **Desk/viz:** render `tracking-feed.json` only; a render need that
  the feed cannot serve is a generator/seed change, landed by PR and
  picked up on the next collect run.
