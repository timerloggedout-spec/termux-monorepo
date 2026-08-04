# jules-ade — Agentic Development Environment (in-repo)

> **Branch:** `feature/jules-ade` (multi-agent workstream — do not merge wholesale until roster + bridge green)  
> **HOME monorepo:** `timerloggedout-spec/termux-monorepo`  
> **Gate path:** branch → `master-staging` (repo-gate + termux-smoke) → cherry-pick → `master`

This directory is the **in-tree home** for getting Jules + Antigravity operational from Termux and GitHub Actions. Upstream forks listed in the Create Project UI are **scavenge templates only** — never vendored wholesale.

## Layout

```
jules-ade/
  README.md                 # this file
  AGENTS.md                 # multi-agent contract for this package
  roster.yaml               # machine-readable repo + focus roster
  research/                 # researched upstream surfaces (no secrets)
  scavenge/templates/       # metadata pointers to forks (SOURCE.txt style)
  bridge/                   # Python scaffold: config + dispatch helpers
  mcp/                      # MCP client/server wiring notes for Termux + cloud
  tasks/                    # YAML task definitions agents can claim
  scripts/doctor.py         # offline health check (stdlib)
```

## Mission

1. Delegate coding work to Jules (cloud sessions) from Termux / agents **now**.
2. Wire Antigravity orchestration patterns as scavenged references, not runtime deps.
3. Keep deepcli / multi-ai-cli as primary local drivers (DeepForge path).
4. Connect MCP where allowed (Jules MCP, Termux MCP, Linear) without committing secrets.

## Multi-agent rules

- All implementation for this package lands on **`feature/jules-ade`** until an agent opens a focused PR to `master-staging`.
- Claim work via `tasks/*.yaml` or Linear TER-* with `Implements:` citation.
- Operator is **not** the assignee — only Tier-4 (credentials, history rewrite) + temporary `termux-smoke` cherry-pick.
- Lean monorepo rules apply: no session dumps, no model weights, no temp branches left behind.

## Quick start (agents)

```bash
# offline doctor
python3 jules-ade/scripts/doctor.py

# read contract
# jules-ade/AGENTS.md → jules-ade/roster.yaml → research/
```

Related ops docs (already on `master-staging`):
- `docs/ops/JULES_ADE_PROJECT.md`
- `docs/ops/JULES_REPO_ROSTER.yaml`
- `docs/ARCHW1Z-GATE.md`
