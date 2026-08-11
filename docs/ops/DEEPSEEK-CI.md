# DeepSeek CI (safe path)

**Issue:** #109  
**Implements:** RL-18 (`docs/proposals/active/rate-limit-rotation/ITEMS.md`)  
**Supersedes destructive Jules PR:** #134  
**Folders:** `deepcli/` (PoW WASM + proxy), `multi-ai-cli/` (backends + `ci_mode.py`)

## What landed

| Artifact | Role |
|----------|------|
| `.github/workflows/deepseek-ci.yml` | Opt-in workflow (`deepseek-ci` / `deepseek` label or `workflow_dispatch`) |
| `multi-ai-cli/ci_mode.py` | Non-interactive review loop |
| `deepcli/pow_solver.js` + `deepseek.wasm` + `package.json` (`type: module`) | PoW for web-wrapper |
| `tests/test_multi_ai_ci.py` | Offline unit tests |
| `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` | Second admin PAT runbook |

## What #134 did wrong (do not merge)

- **Deleted** `.github/workflows/agent-continuous-ops.yml` (regressed #161)
- **Deleted** `.github/connectors/*` catalog
- **Deleted** `agent-context-store` composite action
- **Lowered** elevated soft budgets in `model_router.py`
- Ran on **every** `synchronize` (quota burn)

## Security policy

1. Auth: `DEEPSEEK_TOKEN` secret only for model — never reuse `GITHUB_TOKEN` / OPERATOR as model auth.
2. GitHub writes: `ARCHWIZ_GITHUB_TOKEN` → `OPERATOR_GITHUB_TOKEN` → `GITHUB_TOKEN`.
3. Session: `HOME=$RUNNER_TEMP/deepseek-webwrapper-home` then **always scrub**.
4. No cookies/tokens in Actions cache or git.
5. Output JSON is **metadata only** (no model text).

## How to run

```bash
gh pr edit N --add-label deepseek-ci
gh workflow run deepseek-ci.yml -f pr_number=N
```

## ArchWiz admin token

See `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` — mint PAT in UI (API cannot create PATs), store as `ARCHWIZ_GITHUB_TOKEN`.

## Next (MCP / multi-ai-cli expansion)

After this path is stable, wire MCP template repos into `multi-ai-cli`.

Signed-off-by: Grok (OPERATOR) / archW1z
