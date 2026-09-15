# CLAUDE.md

**Primary agent entry for this repository.** Load this first. Do not start from root `AGENTS.md`.

## Governance sequence (read in order)

1. **This file** — orientation + hard rules
2. [`docs/proposals/registry.yaml`](docs/proposals/registry.yaml) — what is active
3. [`docs/proposals/PROCESS.md`](docs/proposals/PROCESS.md) — post / debate / consensus / close
4. [`docs/ARCHW1Z-GATE.md`](docs/ARCHW1Z-GATE.md) — dual gates
5. [`docs/proposals/AGENTIC-PERMISSIONS.md`](docs/proposals/AGENTIC-PERMISSIONS.md) — human-only edges

Then route the task with **[`docs/icm/CLAUDE.md`](docs/icm/CLAUDE.md)** — one verified component or process card before loading deeper source.

## Hard rules

- Target **`master`** for integration work (base for small PRs may be `master-staging` when that lane is active).
- Both gates must pass before merge:
  - `python3 scripts/ci/repo_gate.py`
  - `python3 scripts/ci/termux_smoke.py`
- Do not invent work outside `docs/proposals/active/<id>/ITEMS.md` — add a row first.
- Cite `Implements: <ITEM-ID>` on PRs/commits.
- **No** wholesale merge of NO-GO mega-PRs (#2, #6) — extract-only.
- **No** Class 3/4 artifacts in git (session stores, browser profiles, tokens).
- Unposted chat is not consensus — write Review log or `DEBATE.md`.

## Preferred execution loop

```text
registry.yaml → pick todo item → branch from master
  → implement → PR with Implements: ID → dual gates green → merge
  → update ITEMS.md status
```

## Quick pointers

| Need | Path |
|------|------|
| Active work | `docs/proposals/registry.yaml` |
| How to review / close | `docs/proposals/PROCESS.md` |
| Gates | `docs/ARCHW1Z-GATE.md` |
| Status | `docs/ARCHW1Z-STATUS.md` |
| Permissions / human edges | `docs/proposals/AGENTIC-PERMISSIONS.md` |
| ICM task routing | `docs/icm/CLAUDE.md` |
| Session SSOT | `docs/schemas/session-ssot.md` |
| Provider caps | `docs/schemas/provider-capabilities.md` |
| Technical deep-dive (optional) | `AGENTS.md` |

## ICM + RinDig reference pins (smods)

Shallow gitlinks under `refTemplates/smods/` — reference only, not runtime control plane:

| Pin | Role |
|-----|------|
| `content-agent-routing-promptbase_fork` | Layered `CLAUDE.md` → CONTEXT routing (one agent, selective load) |
| `cost-of-remembering_fork` | Filesystem-memory cost evidence (~97% fewer tokens) |
| `AuditEngine_fork` | Audit adapt surface |
| `icm-architect_fork` | ICM hierarchy / cards method |

Gitlink ops: `workflow_dispatch` on `.github/workflows/ops-gitlink-lego-fork.yml` pattern (or specialized pin workflows). Gates never init submodules.

## Security

Credential rotation and history rewrite require Operator (human) authorization. See `docs/SECURITY-REMEDIATION.md`.
