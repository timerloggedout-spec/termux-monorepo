# Dashboard Surface Feeds — 3L0 / MoneyBall / MVT / DoE / ATES

The contract for the surface pages in `apps/help-wanted-dashboard/`
(`3l0.html`, `moneyball.html`, `mvt.html`, `doe.html`, `ates.html`),
sibling to the Oracle Panel feed contract
(`docs/ops/ORACLE-PANEL-FEED.md`, owned by the Delphi lane — that feed
is separate and unchanged by this document). MVT, DoE and ATES are
separate surfaces with separate records:
`docs/ops/MVT-DOE-ATES-SEPARATION.md` is the separation spec.

## Feeds

| Surface | Feed | Page |
|---|---|---|
| 3L0 | `apps/help-wanted-dashboard/data/3l0-feed.json` | `3l0.html` |
| MoneyBall | `apps/help-wanted-dashboard/data/moneyball-feed.json` | `moneyball.html` |
| MVT | `apps/help-wanted-dashboard/data/mvt-feed.json` | `mvt.html` |
| DoE | `apps/help-wanted-dashboard/data/doe-feed.json` | `doe.html` |
| ATES | `apps/help-wanted-dashboard/data/ates-feed.json` | `ates.html` (Web Design split — feed lands first, per the separation spec) |

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
- **MVT** — `docs/ops/corpus/EXPERIMENT.schema.json`, the two MVT
  workflows (`.github/workflows/agent-mvt-experiment.yml`,
  `.github/workflows/team-mvt.yml`).
- **DoE** — `deepcli/deepcli/observatory/doe.py` (AST: functions +
  docstrings), `.agents/skills/multivariate-doe/SKILL.md`, the ATES doc
  §DoE (first factorial slice), the DSPy lane design doc. The Delphi
  cycle IMPLEMENTATION record is presented in full as
  `executed_comparisons`, labeled `owner_surface: delphi` (required
  presentation — not DoE results).
- **ATES** — `docs/ops/ATES-ORCHESTRATOR-DOE-MVT.md` §MVT (the seven
  invariants), the benchmark and run-receipt workflows, the
  experiment-loop workflow as execution vehicle,
  `tests/fixtures/ates/orchestrator_mvt.json`.

Workflow run counts come from `scripts/dashboards/workflow_observations.json`,
an Actions-API read stamped with its own `read_at`; refresh it by re-reading
the API and updating that file in the same PR as the feed refresh.

## Refresh automation

`.github/workflows/surface-feeds-collect.yml` mirrors the Oracle Panel
collect pattern: a weekly scheduled run (Wed 06:41 UTC) plus
`workflow_dispatch`, and a master-push trigger on the collector's
source paths (the collector script, the checked-in API snapshot, and
the per-surface source records enumerated under Collector above), so a
landed source or collector change proposes a refresh promptly. One
workflow covers all five feeds because they share one collector
invocation (`--surface all`), one output directory, and one refresh
branch (`surface-feeds/refresh`). The workflow invokes the collector —
it carries no collection logic of its own — and proposes the refreshed
feeds as a refresh PR; it never commits to master directly. (Closes
GAP-LEDGER G-10.)

## Rules

- Pages consume their feed and nothing else (pinned by
  `tests/test_surface_pages.py`); feed content is never hand-edited —
  refresh by re-running the collector (by hand or via the collect
  workflow above) and landing the result by PR.
- A value the record does not hold renders as absent; the feed names the
  gap in its `gaps` list and the page renders the gap as a first-class
  block. Defined-but-not-run renders as exactly that.
- Static narrative strings inside the collector (signal conditions, design
  rules, harness invariants) are verified against their source files by
  `tests/test_surface_feeds.py`; if a source changes, the test fails
  before the feed can drift from the record.
- Separation (MVT / DoE / ATES): each feed emits payloads only from its
  own surface's records; cross-surface references travel in the feed's
  `citations` array as pointers with labels, never as copied payloads.
  Spec: `docs/ops/MVT-DOE-ATES-SEPARATION.md`.
