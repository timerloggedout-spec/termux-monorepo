# Jules ADE Project — Fully Agentic Development Environment

> **Status:** LIVE definition  
> **Source:** Jules Create Project UI (2026-08-03) + ArchW1z gate spine  
> **Human role:** Tier 4 only (credentials, history rewrite) + `termux-smoke` cherry-pick until automated

## Core principle

**`timerloggedout-spec/termux-monorepo` is the HOME Project Repo.**  
Everything else is a **template to be scavenged from**. Agents own execution.

```
repo-gate (master-staging)  →  termux-smoke  →  master (cherry-pick promotion)
```

Do **not** integrate large TER-* work straight onto `master`.

---

## Mission (from project instructions)

> We need the fastest way to get Jules & Antigravity working from Termux and from GitHub Actions workflows. It will be continuously refined.
>
> Focusing on these, to start, first:
> - multi-ai-cli
> - deepcli / deepseek-cli / deepterm  (# our deepcli is modeled on it)
> - jules-sdk forks
> - antigravity orchestration
> - agy-sdk-agents / dispatch-cli / studio / google-jules-*
>
> We need to be able to delegate **Now**.  
> If you can install MCP Server integrations connections for our own Access, do so.

---

## Repository roster (Create Project)

### HOME (first-class runtime)

| Repo | Role |
|------|------|
| `timerloggedout-spec/termux-monorepo` | Core HOME — deepcli, archwiz, multi-agent, gates, sessions |

### Jules family (scavenge templates)

| Repo | Role |
|------|------|
| `timerloggedout-spec/jules-sdk-fork-rs` | Rust SDK surface |
| `timerloggedout-spec/jules-action_fork` | GitHub Action wiring |
| `timerloggedout-spec/jules-awesome-list_fork` | Catalog / discovery |
| `timerloggedout-spec/jules-multi-agent` | Multi-agent orchestration patterns |
| `timerloggedout-spec/jules-foreman_fork` | Task foreman |
| `timerloggedout-spec/jules-skill_fork` | Skills packaging |
| `timerloggedout-spec/jules_api_cli_fork` | API CLI |
| `timerloggedout-spec/jules-dispatch-cli_fork` | Dispatch CLI |
| `timerloggedout-spec/jules-skills_fork` | Skills collection |
| `timerloggedout-spec/jules-mcp-server_fork` | MCP server for Jules |
| `timerloggedout-spec/cjules_fork` | C Jules variant |
| `timerloggedout-spec/gh-jules-workflow-development_*` | GH workflow development |
| `timerloggedout-spec/pi-jules_fork` | Pi agent + Jules |
| `timerloggedout-spec/google-jules-workflow_fork` | Google Jules workflow |
| `timerloggedout-spec/google-jules-skill_fork` | Google Jules skill |
| `timerloggedout-spec/jules-studio_fork` | Studio UI/patterns |

### Antigravity / AGY family (scavenge templates)

| Repo | Role |
|------|------|
| `timerloggedout-spec/antigravity-jules-orchestration_fork` | Jules↔Antigravity orchestration |
| `timerloggedout-spec/llm-antigravity-orchestrator_fork` | LLM orchestrator |
| `timerloggedout-spec/Antigravity_cli_sdk_fork` | CLI SDK |
| `timerloggedout-spec/Antigravity_2.0_fork` | Antigravity 2.0 |
| `timerloggedout-spec/agy-sdk-agents_fork` | AGY agents SDK |
| `timerloggedout-spec/run-agy-sdk_fork` | Run harness |
| `timerloggedout-spec/feishu-agy-sdk-bridge_fork` | Feishu bridge |
| `timerloggedout-spec/lego_fork` | Composition blocks |
| `timerloggedout-spec/STMoEOrchestrator_fork` | ST MoE orchestrator |

**Scavenge rule:** depth-1 / sparse / metadata-first. Never vendor full histories into HOME. Prefer pointers in `refTemplates/` style.

---

## Focus order (production impact)

1. **Gates green** — repo-gate + termux-smoke on every PR to `master-staging`
2. **deepcli + multi-ai-cli** — primary drivers (DeepForge path)
3. **Termux MCP** — on-device control so cloud agents can delegate to Termux
4. **Jules MCP / skills / dispatch** — scavenged patterns wired into HOME
5. **Antigravity orchestration** — scavenged patterns, not full clones
6. **Session SSOT + credential hygiene** — agent-owned except rotation (Operator)

---

## Agent ownership (Tier map)

| Actor | Owns |
|-------|------|
| **Jules / Devin / Grok / other agents** | Branch, implement, PR → `master-staging`, gates, merge when green |
| **Operator (human)** | Credential rotation, history rewrite auth, App permission grants |
| **Operator (temporary)** | `termux-smoke` branch cherry-pick until that path is automated |

**Nothing is assigned to the Operator for routine TER-* work.**

---

## How agents start work

```text
1. Read docs/ARCHW1Z-GATE.md + docs/proposals/PROCESS.md + this file
2. Branch off master-staging (not master)
3. Smallest atomic change; cite Implements: TER-N or ITEM-ID
4. Push → repo-gate + termux-smoke
5. Green → merge to master-staging
6. Promotion to master = gated cherry-pick (Operator may assist until automated)
```

Lean rules: `docs/ops/LEAN_TERMUX_MONOREPO.md` — no temp branches left behind, no session dumps, no model weights.

---

## Connector map

| System | Role |
|--------|------|
| GitHub | Code, PRs, gates, merge |
| Linear | Task SSOT (delegate to agents, not Operator) |
| Vercel | Preview signal |
| Notion | Human cockpit mirror (non-blocking) |
| Jules web UI | Manual task starts until MCP loop is closed |

---

## Non-goals

- Recursive submodule checkout of scavenger forks
- Treating `commingle-swarm` or Antigravity forks as first-class runtime
- Assigning routine implementation to the Operator
- Integrating large branches straight onto protected `master`
