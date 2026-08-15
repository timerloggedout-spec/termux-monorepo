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
| Mention | Comment `@deepseek`, `@deepseek-ci`, or `@deepCore` (case-insensitive) on a **pull request** or **issue** — OWNER/MEMBER/COLLABORATOR only |
| Label | Add `deepseek-ci`, `deepseek`, or `deepCore` |
| Dispatch | Actions → DeepSeek CI – Agentic → Run workflow |

Mirrors Gemini (`@gemini-cli` / `sparkFlux`) and Jules (`@jules` / `heyVern`) patterns.

## Secrets (repository-scoped)

Model auth — **first non-empty wins** (see `deepcli/session_manager.py::_token_from_env` + Issue #184 catalog):

1. `DEEPSEEK_TOKEN_PRIMARY` / `DEEPSEEK_TOKEN_ACCOUNT_1`
2. `DEEPSEEK_TOKEN` (preferred short name)
3. `DEEPSEEK_API_KEY`
4. `DEEPSEEK_AUTH_TOKEN`
5. `NEXUSCLI_TOKEN`
6. Cookie imports: `DEEPSEEK_COOKIES` / `DEEPSEEK_COOKIES_1` / `COOKIES` (JSON browser-cookie dump or plain `ds_session_id`; preserves `aws-waf-token` when exported)
7. Explicit AWS WAF cookie: `DEEPSEEK_AWS_WAF_TOKEN` / `DEEPSEEK_WAF_TOKEN` / `AWS_WAF_TOKEN` / `WAF_AWS_TOKEN`
8. Secondary: `DEEPSEEK_TOKEN_SECONDARY` / `DEEPSEEK_COOKIES_2`

GitHub writes: `ARCHWIZ_GITHUB_TOKEN` → `OPERATOR_GITHUB_TOKEN` → `OPERATOR_TOKEN` → `GITHUB_TOKEN`.

**If the gate reports "DeepSeek model auth unset" / soft-skips:**
- Confirm the secret is a **repository** secret (Settings → Secrets and variables → Actions → Repository secrets), not only an Environment secret.
- Environment secrets require `jobs.<id>.environment: <name>` in the workflow; this workflow uses repo secrets only.
- Name must match one of the keys above exactly (case-sensitive).
- Empty value counts as unset.
- Cookie blobs: store the full exported cookie JSON whenever available; the probe preserves both `ds_session_id` and `aws-waf-token` automatically. A raw `ds_session_id` remains supported for the token-only path.

Never use a GitHub PAT as DeepSeek model auth. Never use `DEEPSEEK_TOKEN` for `gh` / REST admin calls.

## Security policy

1. Auth: model secret only for model — never reuse `GITHUB_TOKEN` / OPERATOR as model auth.
2. Session: persistent browser-compatible session cache is intentional for the web-wrapper; it may retain `ds_session_id`, `aws-waf-token`, chat-session state, and PoW-compatible metadata under the existing permission-restricted cache path. The Actions cache key is scoped to the repository and exact Git ref; it has no cross-ref restore prefix.
3. No cookies/tokens in Git or result artifacts; cache/session values are never logged. Cached WAF state wins on resume unless `DEEPSEEK_WAF_TOKEN_REFRESH=1` explicitly requests an environment-supplied replacement.
4. Output JSON is **metadata only** (no model text).
5. `pr_number` validated as positive decimal before any `gh pr` call.

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
