# Bucket-headroom alerting (QUE #5230)

Origin: gap finding on QUE #5219 — the quota event register and audit
gate existed, but nothing paged on live bucket headroom; the
2026-11-12 shared-token exhaustion surfaced via failure annotations,
not an alert. Ruling of record: Cadence #5219 c.6823803635 (separate
small leg, no fold into #5160), QDesk acceptance c.6823811148.

## What runs

`.github/workflows/bucket-headroom-watch.yml` every 10 minutes
(Cadence poll floor is 5 minutes; 10 is inside the floor and on the
fleet cadence norm), plus `workflow_dispatch` with `dry_run` and
`drill` inputs. `scripts/ops/bucket_headroom.py` has two legs:

- `collect` — one `GET /rate_limit` read per token available to the
  run: the PAT (repo secret), the per-repo `GITHUB_TOKEN`, and freshly
  minted installation tokens for the fleet apps whose SEC-03 mint
  copies exist in this repo (Swarm — the mint path itself — Collector,
  CrossReference).
- `evaluate` — pure projection/transition logic. It enumerates every
  fleet app from `ops/github-apps/PROCESS.json` (10 apps) and merges
  the reads into the full bucket universe: PAT core, GITHUB_TOKEN
  class, and all 10 app installations. An app with no readable bucket
  is carried as `unreadable` with a named reason
  (`sec03_unprovisioned` / `mint_unavailable` / `no_read_supplied`) —
  never silently skipped.

## Derived thresholds (no hardcoded counts)

A bucket pages only when its **own observed burn rate** — from two
successive reads inside the same reset window — projects exhaustion
**before its own reset time** (`projected_used_at_reset > limit`, all
values from the live `/rate_limit` responses), or when it is already
at zero. A bucket sitting at remaining=100 with zero burn does not
page; a bucket at remaining=4900 burning fast does. There is no
remaining-count threshold constant to tune.

## Page and record

- **Page surface:** one standing issue labeled `bucket-headroom-alert`
  (created once, commented on transitions only — no issue per poll,
  no comment spam; sub-threshold polls produce no page and no event).
- **Record of record (ledger side):** every state transition appends a
  `que-governor-event/v1` row with `kind: headroom_alert` to
  `ops/que/events/governor-events-<date>.jsonl`, committed by the
  Swarm bot; the QUE collector folds it into the governor feed like
  every other governor batch. A GitHub-side outage degrades the page,
  never the alert history.
- **Headroom feed:** `ops/que/feeds/bucket-headroom.json`
  (`bucket-headroom/v1`) carries the latest read + projection + state
  per bucket. This is the live-headroom surface the dispatch executor
  (#5176) and the (c) attempt-2 pre-flight precondition consume.

## Drill

`workflow_dispatch` with `drill: true` injects a stamped synthetic
bucket (`synthetic-drill`, `synthetic_test: true` in the event detail)
whose two fabricated reads project a crossing — proving the page path
end-to-end without burning a real bucket. Drills dedupe like real
transitions.

## Probe consumption (Cadence countersign #5152 c.6842945679)

Every feed row carries **typed headroom** — never a bare invented
number: an authoritative `/rate_limit` read is `exact` (post-draw,
valid until the bucket's reset); an unread bucket is `unknown`
(value null). Buckets whose class has no authoritative read (the
executor's provider arms) resolve unknown by usage: a bounded
minimal-draw validation probe appends an immutable, hash-chained
`quota_probe` metering event (`record-probe` subcommand; field set
per the countersign), and the watcher's projection converts
unknown → measured under the countersigned rules:

- only `success` or an identified-dimension `quota_terminal`
  converts; transient/auth/route/inconclusive outcomes are evidence
  events and convert nothing;
- a successful probe yields `lower_bound` (value = the probe draw —
  it proves only that the draw was available at `observed_at`), or
  `exact` when an authoritative remaining value rides along;
- an identified-dimension terminal yields `zero_until_reset`;
- binding is exact-bucket (provider + account/project + model +
  route + quota dimension) — a replacement arm never measures a
  held arm's bucket, and provider open-bucket notices are
  candidate-discovery evidence only;
- one probe per unknown episode: a second probe in the same episode
  is refused, and every probe's draws are metered in its event.

Probe results are coverage evidence for the standing pre-flight
rules (attempt-2 gate included); they never admit an arm or weaken
a gate.

## Known gap (provisioning lane)

Only 3 of 10 fleet apps have Actions-side SEC-03 mint copies in this
repo today. The other 7 (Publisher, Reviewer, Gate, Lifecycle,
RepoStory, DelphiOracle, MoneyBall) are enumerated and reported
unreadable with the named reason until the provisioning lane lands
their `TERMUX_FLEET_<ROLE>_*` copies (names-only); the watcher picks
them up by adding their mint steps — the evaluation universe already
covers them.
