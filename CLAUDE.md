# CLAUDE.md

Claude (and Claude-compatible) agents: follow **[`AGENTS.md`](AGENTS.md)**.

## Quick pointers

| Need | Path |
|------|------|
| Active work | `docs/proposals/registry.yaml` |
| How to review / close | `docs/proposals/PROCESS.md` |
| Gates | `docs/ARCHW1Z-GATE.md` |
| Status | `docs/ARCHW1Z-STATUS.md` |
| Permissions / human edges | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| Session SSOT | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |

## Defaults

- Base branch for PRs: **`master-staging`**
- Run before claiming done: `python3 scripts/ci/repo_gate.py` and `python3 scripts/ci/termux_smoke.py`
- Do not merge NO-GO PRs (#2, #6 wholesale)
- Record debate in MANIFEST Review log or `DEBATE.md`, not only chat
