# Antigravity surface — scavenge guidance

## Mental model

Antigravity is Google’s **agent runtime** (tools, policy engine, multi-turn state, MCP attachment). Official access is primarily:

- `pip install google-antigravity` (Python SDK + platform wheels)
- Gemini Managed Agents (`base_agent: antigravity-…`)
- Antigravity IDE / CLI products

For **this monorepo**, Antigravity is a **pattern source**, not a required CI dependency. Termux may not ship the binary wheels cleanly; keep doctor/CI offline-safe.

## What to scavenge

| Pattern | Where it helps HOME |
|---------|---------------------|
| Agent + LocalAgentConfig lifecycle | Bridge design for long sessions |
| MCP attach (stdio / SSE / streamable HTTP) | Termux MCP + Jules MCP side-by-side |
| Skills / rules / workflows (ag-kit style) | `jules-ade/tasks`, archwiz procedures |
| Multi-agent SDLC roles | Mapping to Linear TER-* + proposal ITEMS |
| Safety policy / PreToolUse gates | Align with repo-gate spirit |

## What not to do

- Vendor full Antigravity forks into `jules-ade/`
- Require `google-antigravity` import in `scripts/doctor.py`
- Treat community orchestration kits as production runtime without review

## Optional later slice

JULES-ADE-0x: optional extras probe `import google.antigravity` behind `--with-optional`, never required for gate green.
