# Temporal — MCP recon + wiring

**Lane:** temporal-integration (maintenance owner for the fleet
Temporal integration). **Date:** 2026-10-28. **Seed-before-claims:**
every surface below was checked at its source (GitHub API /
README / vendor docs) on this date, not from secondary summaries.

## Verdict

An **official** Temporal MCP server exists:
[`temporalio/temporal-mcp`](https://github.com/temporalio/temporal-mcp)
— read-only, MIT, pre-release (v0.0.3, pushed 2026-10-28, "not
ready for production use" per its README). It is **adopted** for
the fleet self-host in read-only stdio mode (proof below). The
write-capable community server is **not** adopted.

## Surfaces found

| Surface | Owner | Shape | Disposition |
|---|---|---|---|
| `temporalio/temporal-mcp` | Temporal (official) | Read-only MCP: namespaces, workflow state/history, task-queue pollers/backlog, search attributes, Visibility search/count. stdio or streamable HTTP, YAML target config | **ADOPTED** (read-only fits ops-investigation; pre-release → pin version, re-check on upgrade) |
| Temporal Knowledge Base MCP (`https://temporal.mcp.kapa.ai`) | Temporal docs (Kapa) | Docs Q&A only, MCP OAuth; no cluster access | Optional docs aid; not an integration surface for the cluster |
| `temporal-mcp-server` (PyPI / Docker `mcp/temporal`, Code Exchange) | Community (Mike Toscano) | 19 tools, read **+ write** (start/signal/cancel/terminate/batch, schedules) | NOT adopted — write power from an unvetted community server against the fleet cluster; revisit only if the official server stays read-only and a write need is proven |
| `temcp` (Temporal Cloud MCP) | Temporal | Cloud-account ops (namespaces, service accounts, API keys) | Irrelevant — owner decision is self-host, no Temporal Cloud |
| `temporalio/ai-cookbook` | Temporal (official) | Recipes for AI apps on Temporal, incl. durable MCP tool-call patterns (tool calls as activities) | Reference for future workflow builds (already in the RFP P0 set, PR #1867) |
| `temporalio/edu-ai-workshop-mcp`, `temporalio/edu-durable-mcp-tutorial-template` | Temporal (official, education) | Workshop/tutorial material for MCP + Temporal | Reference only |
| In-repo `mcp-docker/temporal/` | This repo | Docker-compose Temporal stack (README + dynamicconfig) | Pre-existing container variant; the live fleet host is the systemd dev-server in `docs/ops/TEMPORAL-SELF-HOST.md` |
| In-repo LangSmith adapter | This repo | `docs/ops/TEMPORAL-LANGSMITH-ADAPTER.md` | Pre-existing observability bridge; unchanged |

## Wiring (live, 2026-10-28)

- Binary: official installer `https://temporal.download/mcp.sh`
  → `~/.temporalio/bin/temporal-mcp`, version **0.0.3**
  (env install, never committed — same pattern as the CLI).
- **Migration note (2026-10-28):** the standing `selfhost` target
  retires with the VM instance (docs/ops/TEMPORAL-MIGRATION.md,
  stage 4). The MCP is used **per-engagement**: point the target
  at the engagement's server (`localhost:7233` inside a GitHub
  Actions engagement run, or a sandbox-local dev server) while it
  runs. There is no standing target on the migrated home.
- Config: `~/workspace/temporal-selfhost/mcp/config.yaml`,
  mirrored in-repo at `scripts/temporal/selfhost/mcp-config.yaml`.
  One target, `selfhost` → `localhost:7233`, namespace `default`,
  plaintext, no key (local dev-server).
- Launch (stdio, agent-spawned):
  `temporal-mcp --stdio --config ~/workspace/temporal-selfhost/mcp/config.yaml`

## Proof of record (2026-10-28, vs the fleet self-host)

- MCP `initialize` → serverInfo `temporal` / `0.0.3`.
- `tools/list` → 8 tools, all read: `check_connection`,
  `count_workflows`, `get_task_queues`, `get_workflow_history`,
  `get_workflows`, `list_available_targets`,
  `list_search_attributes`, `search_workflows`.
- `check_connection(target=selfhost)` → server **ok** (152 ms),
  namespace **ok** (100 ms), `complete: true`.
- `count_workflows` → **3**. `search_workflows`
  (`WorkflowType="DurableUnitWorkflow"`) returned the same day's
  §6 harness run `kill-resume-unit-1793192868` as Completed —
  the MCP read path sees real fleet executions.

## Maintenance

- Owner: temporal-integration lane. Duties: keep the self-host
  green (`docs/ops/TEMPORAL-SELF-HOST.md`), re-run
  `check_connection` + the §6 harness after any VM replacement or
  Temporal upgrade, and track `temporalio/temporal-mcp` releases
  (pre-release, fast-moving; upgrade = deliberate pin bump +
  re-proof, never silent).
- Boundary: this MCP is read-only by design. Workflow writes stay
  on the SDK/CLI path (`scripts/temporal/`) until an official
  write-capable server exists and is separately evaluated.
- Mesh caveat (unchanged): no tailscale interface in this VM's
  network namespace — single node; mesh redundancy NOT
  established.
