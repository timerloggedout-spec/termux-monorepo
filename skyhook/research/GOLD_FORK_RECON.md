# 🥇 Gold fork RECON — Create Project instructions

Source: Jules Create Project UI project instructions (screenshot 2026-08-03).

> Focusing on these, to start, first: multi-ai-cli; deepcli/deepseek-cli/deepterm;
> then the Jules (+ listed) forks. Delegate **Now**.

## A. Local HOME (first-class — already in monorepo)

| Path | Role | Skyhook angle |
|------|------|----------------|
| `multi-ai-cli/` | Multi-provider CLI | Local orchestrator that can emit Jules task plans |
| `deepcli/` | Primary driver (DeepForge) | Session/stream → optional handoff prompt to Jules |
| `deepseek-cli/` | Related CLI | Pattern parity |
| `deepterm` | Model for deepcli | Reference behavior only |

No scavenge required — improve wiring **into** skyhook bridge/MCP docs.

## B. Jules gold forks (scavenge order)

### Tier 1 — Delegate now

| Fork | Steal |
|------|--------|
| **jules-dispatch-cli_fork** | YAML task batching, concurrency limits, poll-for-PR, MCP mode |
| **jules-mcp-server_fork** | Tool shapes: create/list/get session, send_reply, diffs; env `JULES_API_KEY` |

Upstream anchors: `@google/jules-mcp`, community jules-dispatch.

### Tier 2 — SDK + CI

| Fork | Steal |
|------|--------|
| **jules-sdk-fork-rs** | Rust SDK patterns; fleet `all()`-style concurrency ideas for local planners |
| **jules-action_fork** | GH Action inputs for prompt/source/branch → Jules session |
| **gh-jules-workflow-development_fork** | Workflow YAML that targets `master-staging` |

### Tier 3 — Skills

| Fork | Steal |
|------|--------|
| **jules-skill_fork** | Skill packaging layout |
| **jules-skills_fork** | Skill collection / lockfile ideas |
| **google-jules-skill_fork** | Google-side skill contract |

### Tier 4 — Orchestration UI / multi-agent

| Fork | Steal |
|------|--------|
| **jules-foreman_fork** | Task foreman / queue semantics |
| **jules-studio_fork** | Studio UX patterns (docs only unless thin) |
| **jules-multi-agent** | Multi-agent split of work units |

### Tier 5 — Secondary

| Fork | Steal |
|------|--------|
| **google-jules-workflow_fork** | Extra workflow templates |
| **cjules_fork** | Alternate client notes |
| **jules_api_cli_fork** | Raw API CLI flags |
| **jules-awesome-list_fork** | Catalog of community tools |
| **pi-jules_fork** | Pi agent bridge ideas |

## C. Visibility

Public GitHub search for `user:timerloggedout-spec` Jules forks returned empty at research time → **likely private**. Agents with repo scope must open each fork and fill `scavenge/templates/<name>/SOURCE.txt`.

## D. Explicitly not in active RECON

Antigravity / AGY / Feishu AGY / Lego / STMoE — listed in Create Project but **deferred**. See `DEFERRED_ANTIGRAVITY.md`.
