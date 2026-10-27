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
  `ops/delphi/panel.json` (defaults only; live weights live on ledger #1489).
- **MVT** — `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md`,
  `docs/ops/corpus/EXPERIMENT.schema.json`, the two MVT workflows.
- **DoE** — `deepcli/deepcli/observatory/doe.py` (AST: functions +
  docstrings), `.agents/skills/multivariate-doe/SKILL.md`, the ATES doc,
  the DSPy lane design doc, the Delphi cycle IMPLEMENTATION record.

Workflow run counts come from `scripts/dashboards/workflow_observations.json`,
an Actions-API read stamped with its own `read_at`; refresh it by re-reading
the API and updating that file in the same PR as the feed refresh.

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
