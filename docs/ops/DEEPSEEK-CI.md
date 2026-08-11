# DeepSeek CI (safe path)

**Issue:** #109  
**Supersedes destructive Jules PR:** #134  
**Folders:** `deepcli/` (PoW WASM + proxy), `multi-ai-cli/` (backends + `ci_mode.py`)

## What landed

| Artifact | Role |
|----------|------|
| `.github/workflows/deepseek-ci.yml` | Opt-in workflow (`deepseek-ci` / `deepseek` label or `workflow_dispatch`) |
| `multi-ai-cli/ci_mode.py` | Non-interactive review loop |
| `deepcli/pow_solver.js` + `deepseek.wasm` | PoW for web-wrapper |
| `tests/test_multi_ai_ci.py` | Offline unit tests |

## What #134 did wrong (do not merge)

- **Deleted** `.github/workflows/agent-continuous-ops.yml` (regressed #161)
- **Deleted** `.github/connectors/*` catalog
- **Deleted** `agent-context-store` composite action
- **Lowered** elevated soft budgets in `model_router.py`
- Ran on **every** `synchronize` (quota burn)

## Security policy

1. Auth: `DEEPSEEK_TOKEN` secret only — never reuse `GITHUB_TOKEN` as model auth.
2. Session: `HOME=$RUNNER_TEMP/deepseek-webwrapper-home` then **always scrub**.
3. No cookies/tokens in Actions cache or git.
4. Output JSON is non-secret summary only (`deepseek_output.json` gitignored).

## How to run

```bash
# Label a PR
gh pr edit N --add-label deepseek-ci

# Or dispatch
gh workflow run deepseek-ci.yml -f pr_number=N
```

## Next (MCP / multi-ai-cli expansion)

After this path is stable, wire MCP template repos into `multi-ai-cli` (user-supplied templates). DeepSeek remains one backend among peers (Omni / OpenRouter / Gemini residual).

Signed-off-by: Grok (OPERATOR)
