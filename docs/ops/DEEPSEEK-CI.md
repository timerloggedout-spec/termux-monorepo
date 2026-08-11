# DeepSeek CI (safe path) — Agentic

**Issue:** #109  
**Implements:** RL-18 (`docs/proposals/active/rate-limit-rotation/ITEMS.md`)  
**Supersedes destructive Jules PR:** #134  
**Folders:** `deepcli/` (PoW WASM + proxy), `multi-ai-cli/` (backends + `ci_mode.py`)

## What landed

| Artifact | Role |
|----------|------|
| `.github/workflows/deepseek-ci.yml` | Opt-in agentic workflow |
| `multi-ai-cli/ci_mode.py` | Non-interactive review loop |
| `deepcli/pow_solver.js` + `deepseek.wasm` + `package.json` (`type: module`) | PoW for web-wrapper |
| `tests/test_multi_ai_ci.py` | Offline unit tests |
| `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` | Second admin PAT runbook |
| `docs/ops/AGENT-MONIKERS.md` | Display moniker `deepCore` |

## Agentic triggers (no CLI)

| Trigger | How |
|---------|-----|
| Mention | Comment `@deepseek`, `@deepseek-ci`, or `@deepCore` (case-insensitive) on a PR/issue — OWNER/MEMBER/COLLABORATOR only |
| Label | Add `deepseek-ci` or `deepseek` |
| Dispatch | Actions → DeepSeek CI – Agentic (safe) → Run workflow |

Mirrors Gemini (`@gemini-cli` / `sparkFlux`) and Jules (`@jules` / `heyVern`) patterns.

## Secrets (repository-scoped)

Model auth — **first non-empty wins**:

1. `DEEPSEEK_TOKEN` (preferred)
2. `DEEPSEEK_API_KEY`
3. `DEEPSEEK_AUTH_TOKEN`
4. `NEXUSCLI_TOKEN`

GitHub writes: `ARCHWIZ_GITHUB_TOKEN` → `OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `GITHUB_TOKEN`.

**If the gate reports "No DEEPSEEK_TOKEN":**
- Confirm the secret is a **repository** secret (Settings → Secrets and variables → Actions → Repository secrets), not only an Environment secret.
- Environment secrets require `jobs.<id>.environment: <name>` in the workflow; this workflow uses repo secrets only.
- Name must match one of the four keys above exactly (case-sensitive).
- Empty value counts as unset.

Never use a GitHub PAT as DeepSeek model auth. Never use `DEEPSEEK_TOKEN` for `gh` / REST admin calls.

## Security policy

1. Auth: model secret only for model — never reuse `GITHUB_TOKEN` / OPERATOR as model auth.
2. Session: `HOME=$RUNNER_TEMP/deepseek-webwrapper-home` then **always scrub**.
3. No cookies/tokens in Actions cache or git.
4. Output JSON is **metadata only** (no model text).

## What #134 did wrong (do not merge)

- **Deleted** `.github/workflows/agent-continuous-ops.yml` (regressed #161)
- **Deleted** `.github/connectors/*` catalog
- **Deleted** `agent-context-store` composite action
- **Lowered** elevated soft budgets in `model_router.py`
- Ran on **every** `synchronize` (quota burn)

## ArchWiz admin token

See `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` — mint PAT in UI (API cannot create PATs), store as `ARCHWIZ_GITHUB_TOKEN`.

## Next (MCP / multi-ai-cli expansion)

After this path is stable, wire MCP template repos into `multi-ai-cli`.

Signed-off-by: Grok (OPERATOR) / archW1z
