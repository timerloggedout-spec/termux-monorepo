# Research sources (no secrets)

Collected 2026-08-03 by grok-archw1z for `jules-ade/` scaffold.

## Jules (Google Labs)

| Resource | Notes |
|----------|-------|
| https://jules.google | Product / sessions UI |
| https://github.com/google-labs-code/jules-sdk | Official JS SDK — fleet of cloud coding agents |
| https://www.npmjs.com/package/@google/jules-mcp | Official MCP server (`create_session`, `list_sessions`, …) |
| https://jules.google/docs/changelog/2026-02-02/ | Built-in MCP connectors (Linear, etc.) — allowlisted |
| Community MCP | CodeAgentBridge/jules-mcp-server, Godzilla675/google-jules-mcp, savethepolarbears/jules-mcp-server |
| Batch dispatch | jules-dispatch (YAML tasks, parallel sessions, MCP mode) |

Env contract (never commit values):

```text
JULES_API_KEY=...          # preferred for @google/jules-mcp
GOOGLE_JULES_API_KEY=...   # alternate used by some community servers
```

## Antigravity

| Resource | Notes |
|----------|-------|
| https://antigravity.google/blog/introducing-google-antigravity-sdk | SDK announcement |
| `pip install google-antigravity` | Official Python SDK (runtime binary in wheels) |
| github.com/google-antigravity/antigravity-sdk-python | Source view — install from PyPI for binary |
| Gemini Managed Agents | base_agent antigravity-preview-*; remote environments |
| Community kits | ag-kit, project-team-ag — orchestration / skills patterns |

## HOME monorepo surfaces to integrate with

- `deepcli/`, `multi-ai-cli/` — local drivers
- `archwiz/` — dispatch + Sentinel
- `termux-multi-agent/` — parallel agents on device
- PR #7 Termux MCP — on-device control plane
- Gates: `scripts/ci/repo_gate.py`, `scripts/ci/termux_smoke.py`

## Visibility note

GitHub search for `user:timerloggedout-spec jules OR antigravity` returned **0 public** repos at research time. Forks in the Create Project screenshot are likely **private**. Agents with repo access should verify and fill `scavenge/templates/*/SOURCE.txt`.
