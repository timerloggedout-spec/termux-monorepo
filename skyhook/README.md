# skyhook

> **Termux ground station → Jules cloud fleet.**  
> Branch: `feature/skyhook` (multi-agent) · Target: `master-staging` → cherry-pick `master`

**skyhook** is the in-repo package that moors Google Jules to this HOME monorepo so agents can **delegate now** from Termux and from GitHub Actions.

Former name: `jules-ade` (retired on this branch).

## Strategy

| Phase | Scope |
|-------|--------|
| **Now** | Jules only — MCP, dispatch, skills, actions, workflows |
| **Later** | Antigravity on Termux (heavy). Let Jules implement it. Explore Colab / free-tier cloud compute if device is too thin. |

HOME repo remains `timerloggedout-spec/termux-monorepo`. Every other Create Project repo is a **scavenge template**.

## Layout

```
skyhook/
  README.md AGENTS.md roster.yaml
  research/          # Jules surface + 🥇 fork RECON + deferred Antigravity
  scavenge/templates # metadata SOURCE.txt per gold fork
  bridge/            # config + session plan helpers (stdlib)
  mcp/               # Jules MCP wiring (no secrets)
  tasks/queue/       # multi-agent claimable YAML
  scripts/doctor.py  # offline health check
```

## 🥇 Focus (from Project Instructions)

**Local HOME (already in monorepo):**
- `multi-ai-cli`
- `deepcli` / `deepseek-cli` / `deepterm` (deepcli is modeled on deepterm)

**Jules forks — RECON + scavenge order:**
1. `jules-dispatch-cli_fork` · `jules-mcp-server_fork` — delegate **now**
2. `jules-sdk-fork-rs`
3. `jules-action_fork` · `gh-jules-workflow-development_fork`
4. `jules-skill_fork` · `jules-skills_fork` · `google-jules-skill_fork`
5. `jules-foreman_fork` · `jules-studio_fork` · `jules-multi-agent`
6. `google-jules-workflow_fork` · `cjules_fork` · `jules_api_cli_fork` · `jules-awesome-list_fork` · `pi-jules_fork`

**Parked (not RECON-active):** all `antigravity-*`, `agy-*`, `feishu-agy-*`, `lego_fork`, `STMoEOrchestrator_fork` — see `research/DEFERRED_ANTIGRAVITY.md`.

## Agent quick start

```bash
python3 skyhook/scripts/doctor.py
# claim a task under skyhook/tasks/queue/
```

Gate spine unchanged: `repo-gate` → `termux-smoke` → `master`.
