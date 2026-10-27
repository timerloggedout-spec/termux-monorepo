# Dashboard Surface Feeds — 3L0 / MoneyBall / MVT / DoE

The contract for the four surface pages in `apps/help-wanted-dashboard/`
(`3l0.html`, `moneyball.html`, `mvt.html`, `doe.html`), sibling to the
Oracle Panel feed contract (`docs/ops/ORACLE-PANEL-FEED.md`, owned by the
Delphi lane — that feed is separate and unchanged by this document).

## Feeds

| Surface | Feed | Page |
|---|---|---|
| 3L0 | `apps/help-wanted-dashboard/data/3l0-feed.json` | `3l0.html` |
| MoneyBall | `apps/help-wanted-dashboard/data/moneyball-feed.json` | `moneyball.html` |
| MVT | `apps/help-wanted-dashboard/data/mvt-feed.json` | `mvt.html` |
| DoE | `apps/help-wanted-dashboard/data/doe-feed.json` | `doe.html` |

Schema: `dashboard-surface-feed/v1` — `{schema, surface, generated_at,
sources, honesty_rules, data, gaps}`.

## Collector

`scripts/dashboards/surface_feeds.py` reads only repository records:

- **MoneyBall** — `ml/pipelines/moneyball/*.py` parsed as code (weights,
  stale cap, clamp bounds, explain output shape are extracted from the
  AST, never transcribed from prose), `docs/ops/HEX-MONEYBALL-INTEGRATION.md`,
  the hex evidence workflow.
- **3L0** — `docs/ops/AGENT-TEAM-ORCHESTRATION.md`,
  `docs/ops/SCOUT-ROSTER.md`, `scripts/model_router.py`,
  `.github/connectors/llm-peers.yaml`, `docs/ops/generated/reviewer-metrics.json`,
  `ops/delphi/panel.json` (cold-start seed defaults), plus the **observed
  live Delphi weighting** from ledger #1489 via the observation snapshot
  below. In the feed, seeds and observed values are separate blocks
  (`panel_defaults`, labeled `cold_start_seed`, vs `observed`, labeled
  `observed_live`); the observed block carries per-role effective weights
  derived from the panel formula and full provenance (source issue,
  newest weights comment, feedback issue/outcome, append history).
- **MVT** — `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md`,
  `docs/ops/corpus/EXPERIMENT.schema.json`, the two MVT workflows.
- **DoE** — `deepcli/deepcli/observatory/doe.py` (AST: functions +
  docstrings), `.agents/skills/multivariate-doe/SKILL.md`, the ATES doc,
  the DSPy lane design doc, the Delphi cycle IMPLEMENTATION record.

Workflow run counts come from `scripts/dashboards/workflow_observations.json`,
an Actions-API read stamped with its own `read_at`; refresh it by re-reading
the API and updating that file in the same PR as the feed refresh.

Delphi weights come from `scripts/dashboards/delphi_weights_observation.json`,
an issue-comments API read of the append-only weights ledger (issue #1489)
stamped with its own `read_at`. The ledger issue is the source of record —
the collector never calls the network and never forks the ledger; the
snapshot is its only route into the feeds. Refresh it the same way: re-read
the issue's `delphi-weights v1` comments, replace the snapshot, re-run the
collector, land both in one PR. `tests/test_surface_feeds.py` pins the
feed's observed block against this snapshot, so a feed cannot drift from
the ledger read silently.

## Rules

- Pages consume their feed and nothing else (pinned by
  `tests/test_surface_pages.py`); feed content is never hand-edited —
  refresh by re-running the collector and landing the result by PR.
- A value the record does not hold renders as absent; the feed names the
  gap in its `gaps` list and the page renders the gap as a first-class
  block. Defined-but-not-run renders as exactly that.
- Static narrative strings inside the collector (signal conditions, design
  rules, harness invariants) are verified against their source files by
  `tests/test_surface_feeds.py`; if a source changes, the test fails
  before the feed can drift from the record.
