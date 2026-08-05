# 🥇 Gold fork RECON — Create Project instructions

Source: Jules Create Project UI + public org scan (2026-08-03).
**Device lens:** BLU B160V Termux — see `DEVICE_B160V.md`.

> Focusing on these, to start, first: multi-ai-cli; deepcli/deepseek-cli/deepterm;
> then the Jules (+ listed) forks. Delegate **Now**.

## Policy

Templates are **use directly OR rewrite** into HOME systems. On B160V, default is **rewrite protocol into Python/stdlib**; heavy runtimes stay host/CI.

## A. Local HOME (first-class — already in monorepo)

| Path | Role | Skyhook angle |
|------|------|----------------|
| `multi-ai-cli/` | Multi-provider CLI | Local orchestrator → Jules task plans |
| `deepcli/` | Primary driver (DeepForge) | Session/stream → handoff to Jules |
| `deepseek-cli/` | Related CLI | Pattern parity |
| `deepterm` | Model for deepcli | Reference behavior only |

## B. Jules gold forks (public under timerloggedout-spec)

### Tier 1 — protocol to rewrite on-device

| Fork | Steal | B160V |
|------|--------|--------|
| **jules-dispatch-cli_fork** | `--json`, session states, PR bridge | **Rewrite** — do not require Bun |
| **jules-mcp-server_fork** | MCP tool names / session lifecycle | **Rewrite thin HTTP** or host MCP |

Full notes: `TIER1_DISPATCH_MCP.md`.

### Tier 2 — SDK + CI

| Fork | Steal | B160V |
|------|--------|--------|
| **jules-sdk_fork-rs** | API surface (not cargo on phone) | Protocol only |
| **jules-action_fork** | `jules-invoke` inputs, allowlists | **Use on CI** |
| **gh-jules-workflow-development_fork** | Workflow YAML → `master-staging` | **Use on CI** |

### Tier 3 — Skills

| Fork | Steal |
|------|--------|
| **jules-skill_fork** / **jules-skills_fork** / **google-jules-skill_fork** | Skill packaging layout |

### Tier 4 — Orchestration

| Fork | Actual name | Steal |
|------|-------------|--------|
| multi-agent | **jules-cli_fork-multiAgent** | Work-unit split |
| foreman / studio | jules-foreman_fork, jules-studio_fork | Queue semantics / docs |

### Tier 5 — Secondary

google-jules-workflow_fork, cjules_fork, jules_api_cli_fork, jules-awesome-list_fork, pi-jules_fork — catalog + flags only.

## C. Visibility

**Public.** Prior “private” assumption was wrong. SOURCE.txt filled for tier-1 + action + sdk-rs name fix.

## D. Deferred

Antigravity / AGY / Feishu AGY / Lego / STMoE — `DEFERRED_ANTIGRAVITY.md` (Jules implements later; optional Colab credits).
