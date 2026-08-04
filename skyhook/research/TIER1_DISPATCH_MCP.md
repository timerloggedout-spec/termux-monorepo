# Tier-1 RECON — public forks (2026-08-03)

**Agent:** Grok (skyhook). Forks are **public** under `timerloggedout-spec`.

## jules-dispatch-cli_fork

| Field | Value |
|-------|--------|
| URL | https://github.com/timerloggedout-spec/jules-dispatch-cli_fork |
| Default branch | `main` |
| Stack | TypeScript, Bun, Commander.js |
| Upstream-ish | AVANT-ICONIC/jules-dispatch-cli (clone URL in README) |
| Auth | `JULES_API_KEY` → header `X-Goog-Api-Key` |
| API host | `https://jules.googleapis.com` (v1alpha) |

### Steal for skyhook

1. **JSON-first agent loop** — always `--json` on workflow commands; poll session state machine.
2. **Session states:** `QUEUED` → `IN_PROGRESS` → `AWAITING_PLAN_APPROVAL` / `AWAITING_USER_FEEDBACK` / `PAUSED` → `COMPLETED` | `FAILED`.
3. **Commands:** `sessions create|run|get|list|message|approve|activities|outputs`, `sources list`, `prs list|view|merge|comment`.
4. **Agent pattern:** create → capture `.id` → poll every ~30s → on plan approval call `approve` → `prs list` filter by session → optional merge via `gh`.
5. **Docs:** `AGENTS.md`, `docs/agent-guide.md`, `docs/jules-api-notes.md`, `docs/command-reference.md`.

### Termux note

Bun may be heavy on device; prefer **MCP path** or thin shell wrappers calling Jules HTTP API from Python already in HOME. Scavenge **protocol**, not necessarily Bun runtime.

## jules-mcp-server_fork

| Field | Value |
|-------|--------|
| URL | https://github.com/timerloggedout-spec/jules-mcp-server_fork |
| Default branch | `main` |
| Stack | Python 3.13+, FastMCP, `jules-agent-sdk` |
| Run | `uv run fastmcp run jules_mcp/jules_mcp.py:mcp` or `python -m jules_mcp` |
| Auth | `JULES_API_KEY` |

### MCP tools (steal names)

- Sources: `get_source`, `list_sources`, `get_all_sources`
- Sessions: `create_session(prompt, source, starting_branch?, title?, require_plan_approval?)`, `get_session`, `list_sessions`, `approve_session_plan`, `send_session_message`, `wait_for_session_completion`
- Activities: `get_activity`, `list_activities`, `list_all_activities`

### Steal for skyhook

1. Map `skyhook.bridge.plan_task` → `create_session` args (`prompt`, `source`, `starting_branch`, `require_plan_approval`).
2. Prefer this MCP over Bun CLI on Termux if Python 3.13+ available; else document host-side MCP only.
3. `MCP.json` / `fastmcp.json` as template for local agent MCP config (no secrets in git).
4. `wait_for_session_completion` is the cloud equivalent of dispatch-cli poll loop.

## jules-action_fork (tier-2, quick pass)

| Field | Value |
|-------|--------|
| URL | https://github.com/timerloggedout-spec/jules-action_fork |
| Action | `google-labs-code/jules-invoke@v1` (upstream) |
| Inputs | `prompt`, `jules_api_key`, `starting_branch` (default `main`), commit context flags |

### Steal

- Workflows that pass `starting_branch: master-staging` for HOME.
- Issue-trigger allowlists (security).
- Example: bug-fixer / ci-failure-fix patterns under `examples/`.

## Name corrections vs Create Project UI

| Screenshot / roster guess | Actual public repo |
|---------------------------|--------------------|
| jules-sdk-fork-rs | **jules-sdk_fork-rs** |
| jules-multi-agent | **jules-cli_fork-multiAgent** |
| jules-mcp-server_fork | exact |
| jules-dispatch-cli_fork | exact |
