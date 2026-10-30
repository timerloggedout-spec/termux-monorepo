# Telemetry Visualization — Recon + Seeded Design (2026-10-29)

**Lane:** telemetry-viz (seeded by Web Design PM, owner order 2026-10-29).
**Surface boundary:** published pages belong to the Web Design lane
(`apps/help-wanted-dashboard/`, design system + data-feed contracts,
read-only projections, no embedded credentials, no browser mutation).
This lane owns the telemetry-viz design + data shaping; render work is
coordinated through the Web Design chat.

**Method:** firsthand recon at master `0e2a336a73` (2026-10-29) — repo
tree, dashboard feeds (schema + keys read per file), lane-events schema,
recorder workflow, and the template platforms' own documented patterns.
Counts below are derived from the files read at that HEAD, not copied
from prose.

## 1. Telemetry streams that exist (fleet's own)

| # | Stream | Store / feed | Shape (verified) |
|---|--------|--------------|------------------|
| S1 | Lane events | Neon `lane-events` (project `dawn-breeze-73523999`, db `neondb`), table `lane_events` (`ops/lane-events/schema.sql`); recorder `.github/workflows/lane-events-recorder.yml` + `scripts/ops/lane_event.py` | Append-only (trigger blocks UPDATE/DELETE), idempotent `event_key = sha256(lane\|workflow\|run_id\|run_attempt\|subject\|event_type)`; fields: lane, workflow, event_type (`run_completed`, `pr_state:*`), repo, run_id/attempt, subject_url, phase_id, conclusion, head_sha, payload jsonb, occurred_at/recorded_at. Watches 6 workflows (help-wanted ×4, SHE ×2 incl. `n8n SHE bridge`); success-only recording. |
| S2 | Help-Wanted outcome ledger (HindSight-adjacent receipts) | `apps/help-wanted-dashboard/data/status.json` (1,503,197 B at HEAD) | `receipts: 3962`, `kinds` (9: upstream_pr, followup_* …), `outcomes {actioned: 221, skipped: 3741}`, 132 tributes, 107 issues, `outcome_semantics`, policy block. Contract: `docs/ops/AUTOMATED-TELEMETRY-AUDIT.md` — every observer ends `emitted\|partial\|skipped\|deferred\|failed`; absence is never zero. |
| S3 | Provenance / Delphi ledger | `data/delphi-ledger-feed.json` + `data/delphi-ledger-feed-db.json` (~84–86 KB) | `{schema, ledgers, living_records, invariants, summary}` — the Provenance ledger projection. **Retention red line: HindSight telemetry + Provenance ledger are NEVER deleted.** |
| S4 | Quota readings | `data/quota.json` (156 readings) | `{schema, generated_at, source, readings[]}` — per-resource `{resource_id, status, used, limit, unit, reset, evidence_status, horizon, observed_at}`; honest nulls (`used: null` = not observed, never 0). |
| S5 | Quota usage pack | `data/quota-usage.json` + `data/quota-allocations-feed.json` (191 KB) + `data/provider-quota-coverage.json` (88 KB) | series1 API core / series2 snapshots / series3 Actions, annotations, stamps + stamps_provenance, cadence_timeline; allocations carry pools + gantt + cadence constraints (smooth-flow: flow = limit ÷ window, phase-aligned to reset). |
| S6 | Actions run corpus | GitHub Actions (workflows incl. lane-events-recorder, surface-feeds-collect, delphi-*, challenge-*, receiver-process, quota-*) | Run lists + conclusions are the raw execution telemetry behind S1; no consolidated run-corpus feed exists yet — **gap G1**. |
| S7 | Dashboard surface feeds | `apps/help-wanted-dashboard/data/` — 23 JSON feeds + 1 JSONL series at HEAD | Uniform envelope `dashboard-surface-feed/v1 {schema, surface, generated_at, sources, honesty_rules, data, gaps}` (3l0, moneyball, mvt, doe, ates, dispatch-tree) + specialised feeds (pr-lane, oracle-panel, linguist-panel, proposals, referral, free-tier-value, fb-traffic, challenge-countdowns). Collector: `scripts/dashboards/surface_feeds.py`, workflow `surface-feeds-collect.yml`. Contract: `docs/ops/DASHBOARD-SURFACE-FEEDS.md`. |
| S8 | Challenge admin metrics | `data/challenge-admin-metrics.json` | `challenge-admin-metrics/v1 {events[]: win_probability, field_size_status}` — **internal/Admin-panel only, never public render** (`docs/ops/ADMIN-INTERNAL-METRICS.md`). Design must keep this designation boundary. |
| S9 | Receiver Mesh events | Neon DDL `ops/receiver-mesh/processor/receiver_events.sql`; processor `.github/workflows/receiver-process.yml` | Webhook intake envelope (Cloudflare edge → Actions processor → Neon ledger); dedupe/dead-letter semantics per `docs/ops/RECEIVER-MESH.md`. Provisioning (secrets/deploy) still owed — stream is contract-live, data-thin. |
| S10 | Agent telemetry stream (legacy) | `agent_telemetry_stream.json` (repo root, JSONL) | `{timestamp, level, agent, target, attempt, message}` lines from 2026-05 — historical agent run log; candidate backfill source, not a live feed — **gap G2** (no collector). |
| S11 | PR lane classification | `data/pr-lane-feed.json` (`pr-lane-feed/v1`) + `data/pr-lane-series.jsonl` | Feed: `{open_prs, counts, prs[], fetch_warnings}` — per-PR lane routing state. Series (mirrored from `ops/ml/pr-lane-series.jsonl`): one counts-only line per collector run `{generated_at, open_prs, counts, delta_vs_previous, fetch_warnings}` — the fleet's existing **time-series/trend substrate pattern**, reused by Slice 2 for run/quota trends instead of inventing a new one. |

## 2. Templates → patterns borrowed (build ours, borrow patterns)

| Template | Pattern taken | NOT taken |
|----------|---------------|-----------|
| **n8n** | Execution-list → per-execution drill-down: run list (status, started, duration, mode) → execution detail with **per-node state** (each node: status, runtime, error) + a global **Error Workflow** surface (hard failures pushed, not pulled) + heartbeat/absence alerting (a missing run is a signal). Executions view is the model for S1/S6. | The workflow editor/canvas as telemetry; n8n instance hosting. |
| **Platform201** | Deployment-surface patterns from the live fleet deployment (`docs/ops/PLATFORM201-LIVE-2026-10-27.md`, PR #1983 wiring): project → environment → nodes (container/function/gateway/scheduler) graph, deployment history with per-deployment state (Deployment 2 failed / 3 deployed), health endpoint as a first-class tile (`/health {"ok":true}`), credits/caps tiles (Solo caps as quota-style gauges). Model for the surface/deployment strip over S5/S7 hosts (Pages, Vercel, Platform201). | Platform201 as a telemetry backend — it is a host + registry entry (`platform201.projects`, `ops/delphi/surfaces.json`), console-only, no API token. |
| **Gravitee APIM** (connector `custom.gravitee`, Management API v2 shapes; no live instance) | Gateway analytics grammar: top row = requests / error-rate % / avg latency; breakdowns by dimension (api, application, plan, path, status, tenant, host); projections = hits, global/api/proxy latency, content lengths; status-class time series; Top-N consumers table; customisable dashboard tabs + query filter + events log. Model for S4/S5 quota + any future gateway-shaped stream, and for PAT/API call telemetry generally (rate = flow, errors = 4xx/5xx classes, duration = latency percentiles). | A live Gravitee instance (none exists; connector is mock-verified only) — shapes only. |
| **Witness (TestifySec / in-toto)** | Evidence-chain view: per-artifact attestation chain — step → attestations (materials in, command, products out) → signer → policy verdict (pass/fail with reason); DSSE envelope as the unit; Archivista-style store/retrieve by subject digest. Model for S3 Provenance ledger rendering. **Placement is owned by lane 0c2e1f46 — this lane consumes its placement decision, does not duplicate it.** | Witness adoption/placement decisions; signing infrastructure. |
| **Grafana / SRE** (surfaced in recon — relevant) | Page grammar: golden signals (latency, traffic, errors, saturation) top row; RED (rate, errors, duration) per service/lane; USE for resources; consistent thresholds/colours; variables (lane, workflow, window) that repeat panels; annotations on time series (= S5 stamps). | Grafana/Prometheus as a dependency — grammar only, rendered in the fleet's own static dashboard. |
| **OpenTelemetry** (surfaced in recon — relevant) | Correlation model: one `trace_id` across spans — fleet analogue = `event_key` / run_id+attempt / head_sha linking S1 ↔ S6 ↔ S3, so a lane run can be traced recorder → Actions run → PR → ledger entry. | OTLP collectors/exporters (no live telemetry pipeline justifies them yet). |

## 2b. Diagram imagery — REUSE the fleet's mmd → png process (owner addendum 2026-10-29)

No new renderer is built. The hardened process already on master
(verified firsthand at `f3aba7c980`, 2026-10-29; lineage: the #455
closure analysis):

- **Workflow:** `.github/workflows/automation-docs-continuous-refresh.yml`
  ("Automation Documentation Continuous Refresh") — triggers:
  `workflow_dispatch` + push-to-master / PR on path filters that include
  `docs/ops/diagrams/**` (cadence owned by `quota-dispatch-tree.yml`).
- **Render step (in BOTH jobs** — `validate-pull-request`, contents:read,
  and `refresh-trusted`, contents:write, which commits renders back to
  master; job timeout 20m, render step timeout 10m):
  "Render Mermaid decision trees (mmdc)".
- **Exact invocation:** `npx --yes @mermaid-js/mermaid-cli@11.4.2 -i <src>
  -o docs/ops/generated/<stem>.png -b transparent -s 2
  --puppeteerConfigFile /tmp/puppeteer-config.json`, where the config is
  written inline by the step:
  `{"args":["--no-sandbox","--disable-setuid-sandbox"]}`.
- **Scope of the glob:** only `docs/ops/diagrams/*.mmd` → 
  `docs/ops/generated/*.png` (asset manifest:
  `docs/ops/generated/automation-diagram-assets.json`). Standalone `.mmd`
  files elsewhere (e.g. `docs/agentic/dependency-phases.mmd` — a Gantt,
  `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd`) are NOT rendered by it.
- **Consequence for this lane:** telemetry diagram sources (flow,
  process, Gantt) are authored as `.mmd` under `docs/ops/diagrams/`
  (e.g. `telemetry-flow.mmd`, `telemetry-quota-gantt.mmd`) and the page
  consumes the generated PNG from `docs/ops/generated/`. Any need to
  render sources outside that directory is a glob-extension change to
  that workflow — proposed, never forked into a second renderer.

## 3. Template → stream mapping

| Stream | Primary template | Secondary | View seeded |
|--------|------------------|-----------|-------------|
| S1 lane-events | n8n executions | OTel correlation | Run list → run detail (per-event timeline) |
| S6 Actions corpus | n8n executions | Grafana RED per workflow | Workflow health board (needs G1 feed) |
| S2 outcome ledger | n8n outcome layer* | Witness verdicts | Outcome funnel + audit-outcome strip (emitted/partial/skipped/deferred/failed) |
| S3 Provenance ledger | Witness evidence chain | — | Attestation/evidence chain per subject (consume 0c2e1f46 placement) |
| S4 quota readings | Gravitee top-row + breakdowns | Grafana USE/saturation | Resource table with honest-null state |
| S5 quota usage/allocations | Gravitee time series | Grafana annotations + smooth-flow target line (limit ÷ window) | Flow-vs-reset chart pack |
| S7 surface feeds | Platform201 nodes | Grafana variables | Feed-health strip (generated_at age, gaps count per feed) |
| S9 receiver events | n8n error workflow | Witness envelope | Intake → dedupe → dead-letter funnel |
| S11 PR lanes | n8n run list | — | Existing `pr-lanes.html` pattern extended, not replaced |
| Diagrams (flow/Gantt/process, all streams) | Fleet mmdc process (§2b) | — | `.mmd` in `docs/ops/diagrams/` → PNG in `docs/ops/generated/` via `automation-docs-continuous-refresh.yml`; reused, never rebuilt |
| S8 admin metrics | — (no public template) | — | Admin panel only, unchanged boundary |

\* n8n community pattern: execution success ≠ business success — a separate
outcome layer beside the execution view (S2 beside S1/S6).

## 4. Seeded design — what we build, on which surface

**Product:** one new dashboard page **`telemetry.html`** in
`apps/help-wanted-dashboard/` (Web Design lane renders; this lane shapes
data + owns this design), fed by a new collector in the existing pattern:

- **Feed:** `telemetry-viz-feed/v1` — same envelope discipline as
  `dashboard-surface-feed/v1` (`{schema, surface, generated_at, sources,
  honesty_rules, data, gaps}`), file
  `apps/help-wanted-dashboard/data/telemetry-feed.json`, produced by
  `scripts/dashboards/telemetry_feed.py` and collected by a workflow in
  the `surface-feeds-collect.yml` pattern (GitHub Workflows = the
  continuous mechanism; VM = sandbox only).
- **Page grammar (Grafana order, n8n drill-down):**
  1. Top row — fleet golden signals: runs (24h/7d), failure rate,
     deferred (rate-limit) count, quota saturation vs smooth-flow target.
  2. Executions — n8n-style run list from S1 (lane, workflow, conclusion,
     duration where derivable, head_sha) → row expand = event timeline.
  3. Outcomes — S2 funnel (actioned vs skipped kinds) + ATES audit strip.
  4. Quota — S4/S5 Gravitee-style breakdown + flow chart with reset
     phase line; nulls rendered as "not observed", never 0.
  5. Evidence — S3 Provenance chain summary (counts + latest subjects),
     deep-linking the existing `delphi-ledger.html`; full Witness-style
     chain view waits on lane 0c2e1f46's placement.
  6. Feed health — S7 strip: per-feed age + gaps (absence = signal).
- **Rules inherited:** read-only projection; no embedded credentials;
  names-only secrets; internal metrics (S8) never render; absence ≠ zero
  (ATES outcomes vocabulary is the page's state vocabulary).

## 5. Build slices

| Slice | Content | Depends on |
|-------|---------|------------|
| **1 (first)** | `telemetry_feed.py` v1 shaping **S1 + S2 + S4** from already-committed sources (status.json, quota.json, quota-usage.json) + `telemetry.html` skeleton with top row + executions + quota sections. No new external reads. | This recon landing |
| 2 | Actions corpus feed (G1): workflow-run collector → S6 joins S1 by run_id; RED per workflow. | Slice 1; PAT-budgeted collector design (QAC gates) |
| 3 | Evidence chain section (S3 full) + receiver funnel (S9) once provisioning lands. | 0c2e1f46 placement; Receiver Mesh provisioning |
| 4 | Legacy JSONL (S10) backfill + feed-health alerting (absence heartbeat). | Slice 1 |

## 6. Gaps / honest blanks

- G1: no consolidated Actions run-corpus feed (S6 is API-only today).
- G2: `agent_telemetry_stream.json` has no collector; vintage 2026-05.
- G3: lane-events Neon table is not directly readable from a static page —
  Slice 1 shapes committed projections only; a Neon → feed exporter is a
  Slice 2 design question for the DB lane (e3055a9c), not assumed here.
- G4: Gravitee + Witness are pattern sources only (no live instance /
  placement owned elsewhere) — no integration is claimed.
