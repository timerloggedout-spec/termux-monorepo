# ops/que — QUE feeds (producer: Optimizations & Assurance)

The QUE side of the Desk-upgrade commission (owner order
2026-11-04): the Desk holds the board; this directory is the
producer's served state. One collector
(`scripts/que/que_feed_collect.py`, workflow
`que-feed-collect.yml`, cron */10, single-flight, commits
via the Termux Fleet Swarm App) refreshes:

| File | Schema | Contents |
|---|---|---|
| `feeds/que-queue-feed.json` + mirror `apps/tribute-dashboard/data/que-queue-feed.json` | `que-queue-feed/v1` | **The producer-of-record feed for the Desk surface** (Desk-upgrade LEG ①): run-queue state by tier + dispatch claims folded live at publish from `ops/challenge/dispatch-state-feed.json`. Byte-identical canonical + mirror pair. Provenance carries the design input under its issued brand, Stagefoil (Registry issuance PR #4817). The governor + priority-windows feeds also mirror into the dashboard under the que- prefixed names the QUE page fetches (`data/que-governor.json` · `data/que-priority-windows.json`). |
| `feeds/queue-by-tier.json` | `que.queue-by-tier/v1` | Queued + in-progress census classified by tier (`ops/quota/dispatch-tiers.json`: first pattern match wins on workflow name, default tier 4). Wedged ancients (>7d queued) are excluded from counts and listed. |
| `feeds/priority-windows.json` | `que.priority-windows/v1` | Priority windows from the tiers `priority_window` stanza, state computed against the cycle time. Ships `windows: []` with the source named until the stanza lands (PR #4740). |
| `feeds/governor.json` | `que.governor/v1` | The governor plane of the four-feed design (Desk FREEZE, 2026-11-04 — the governing note; two intervening rulings void): admission thresholds + the deferral census folded from swarm-admission stamps (`deferred-by-tier` label), plus flow-governor state folded verbatim from Cadence's T1 emitter batches (`que-governor-event/v1` in `events/governor-events-*.jsonl`, tallied by kind) — `NOT_ESTABLISHED` until the first batch lands, `populated` after; the Desk tracks that flip as leg ②'s completion. Cadence's leg is the emitter only (#4814 stays closed). No seam note acts without FREEZE-LIFT from the Desk. |
| `events/YYYY-MM-DD.jsonl` | transition events | The T1 measurement plane (QUE.md): `{at, run_id, workflow, tier, event: queued\|started\|completed\|cancelled\|vanished, queue_wait_s?, conclusion?}` diffed per cycle against `feeds/state.json`. Repo snapshots are the store of record; `vanished` rows are the gap class for the ≤1% census-gap measure. Governor batches land alongside as `events/governor-events-<date>.jsonl` (Cadence's emitter; this collector folds, never authors). |
| `feeds/state.json` | internal | The differ's working state (active runs + watermark). Working copy, not a consumer surface. |

Consumers: the Desk surface (board) · Quota/Cadence · DoE —
per the consumer contracts in `docs/ops/QUE.md` (PR #4624).

## SIE lifecycle integration

The existing QDesk self-repair workflow consumes master gate failures through
filtered `workflow_run` events and retains its three-hour reconciliation pass.
The event adapter reads the canonical `ops/challenge/dispatch-state-feed.json`
watchdog output; unclaimed escalation and stall receipts become deterministic,
issue-bound SIE intake groups. Claimed dispatches remain with their current owner.

QUE improvement work is tracked through the QDesk self-improvement loop (SIE).
The lifecycle contract and implementation plan are registered at
`docs/proposals/active/que-sie-pipeline-integration/` and QUE task #5389.

- Stage receipt schema: `docs/schemas/que-sie-stage-v1.schema.json`
- Deterministic stage validator: `scripts/que/sie_pipeline.py`
- Evidence-bounded research packet and Oracle Method brief adapter: `scripts/que/sie_research_packet.py`
- Research packet schema: `docs/schemas/que-sie-research-packet-v1.schema.json`
- Delphi package manifest builder and QDesk consumer verifier: `scripts/delphi/proposal_package.py`
- Delphi package manifest schema: `docs/schemas/delphi-proposal-package-v1.schema.json`

Build a research packet from a validated SIE receipt, a diagnosis JSON file and
one or more `delphi-evidence-set/v1` files:

```sh
python3 scripts/que/sie_research_packet.py \
  --receipt /path/to/stage-receipt.json \
  --diagnosis /path/to/diagnosis.json \
  --evidence /path/to/evidence-set.json \
  --out /tmp/que-sie-research
python3 scripts/delphi/generate_proposal.py \
  --brief /tmp/que-sie-research/oracle-brief.json \
  --evidence /tmp/que-sie-research/evidence/evidence-001.json \
  --out /tmp/que-sie-rfp
```

Pass each emitted fresh evidence file with a repeated `--evidence` flag.
The packet builder preserves stale/missing claims as unverified; the Oracle
Method generator remains the canonical proposal renderer.
- Intake source: existing QDesk self-repair workflow and watchdog/stall-gap feed
- Queue authority: existing QUE ranker, dispatch watchdog and auto-claim/lease machinery
- RFP authority: Oracle Method generator
- Award authority: Delphi signed gate and package digest
- Experiment authority: DoE family / EXPERIMENT records
- Outcome authority: ATES and independent task verification

The stage receipt is a compact pointer. Canonical workflow, issue, RFP, ballot,
experiment, claim and outcome evidence remains with its owning producer.
PDDL is a Siglary formal-planning subdomain; the Linguist-owned Matrice governs
notation additions.


### QSI-004 package build and consumer verification

Build the package manifest from an immutable commit checkout after the proposal
documents land. Keep mutable provenance/telemetry outside the explicit inventory:

```sh
python3 scripts/delphi/proposal_package.py --build \
  --root . --source-ref "$PACKAGE_COMMIT_SHA" \
  --package-id "que-sie-<item-key>" \
  --package-path "docs/proposals/active/que-sie-<item-key>" \
  --package-author "$PROPOSAL_AUTHOR" \
  --file "docs/proposals/active/que-sie-<item-key>/MANIFEST.md" \
  --file "docs/proposals/active/que-sie-<item-key>/ITEMS.md" \
  --file "docs/proposals/active/que-sie-<item-key>/RFP.md" \
  --exclude "docs/proposals/active/que-sie-<item-key>/PROVENANCE.json" \
  --out proposal-package.json

python3 scripts/delphi/proposal_package.py \
  --manifest proposal-package.json --root . \
  --checkout-sha "$PACKAGE_COMMIT_SHA" \
  --award signed-award.json --reviewer "$AUTHENTICATED_REVIEWER_LOGIN"
```

The verifier returns exit 0 only for VERIFIED and exit 2 for HELD. Supply the
reviewer identity from the authenticated GitHub actor at the consumer boundary;
the package author is bound by the manifest digest. Keep the Delphi award writer
and QDesk consumer integration on the QD-039/#5156 acceptance path.
