# DeepSeek CI (safe path) — Agentic

**Issue:** #109  
**Implements:** RL-18 (`docs/proposals/active/rate-limit-rotation/ITEMS.md`)  
**Supersedes destructive Jules PR:** #134  
**Folders:** `deepcli/` (PoW WASM + proxy), `multi-ai-cli/` (backends + `ci_mode.py`)

## What landed

| Artifact | Role |
|----------|------|
| `.github/workflows/deepseek-ci.yml` | Automatic PR review plus trusted, on-demand comment replies and manual dispatch |
| `deepcli/ci_mode.py` | Preflight comment trust/command before provider credentials or session initialization |
| `deepcli/ci_agent.py` | PR review, issue reply, and threaded review reply; GitHub content is treated as untrusted data |
| `deepcli/comment_gate.py` | Shared fail-closed moniker parser and trusted-human association gate |
| `.github/workflows/deepseek-termux-agent.yml` | Separate Termux device-agent route; comment gate hardened, assignment triggers retained |
| `deepcli/pow_solver.js` + `deepseek.wasm` + `package.json` (`type: module`) | PoW for web-wrapper |
| `tests/test_deepseek_comment_gate.py` | Offline tests for aliases, trust, preflight, prompt boundary, and permissions |
| `docs/ops/ARCHWIZ-ADMIN-TOKEN.md` | Second admin PAT runbook |
| `docs/ops/AGENT-MONIKERS.md` | Display moniker `deepCore` and exact callable aliases |

## Agentic triggers (no CLI)

| Trigger | How |
|---------|-----|
| PR review | `pull_request` opened/synchronize/reopened; this existing automatic review route is unchanged |
| Mention | A **created** `issue_comment` or `pull_request_review_comment` beginning with `@deepseek`, `@deepseek-ci`, or `@deepCore` (case-insensitive), authored by a human OWNER/MEMBER/COLLABORATOR |
| Dispatch | Actions → DeepSeek CI – Agentic → Run workflow; manual payload may request a PR review, but cannot spoof an issue/review comment event |

Comment mentions embedded in ordinary prose are not commands. The exact-prefix parser and trusted-comment check run again in Python before provider credentials or session/PoW initialization. No label-event trigger is implemented by the current DeepSeek workflows; labels are metadata only.

The separate `.github/workflows/deepseek-termux-agent.yml` accepts the same trusted exact-prefix comment aliases. Its existing `issues: assigned` and `pull_request: assigned` triggers are retained unchanged by this hardening; they are a separate legacy invocation path, not a label route.

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

**Getting a fresh value for any of the above**: see `docs/DEEPSEEK-CAPTURE-PIPELINE.md` for the actual working capture pipeline (manual on-device login via Termux:X11, then automatable cookie-normalize + token-extract steps). `code=40003 "Authorization Failed (invalid token)"` from `create_chat_session` means the value currently in `DEEPSEEK_TOKEN_PRIMARY`/`DEEPSEEK_COOKIES` is stale - most likely because the session was correctly rotated per `docs/CREDENTIAL-EXPOSURE.md`. Never resurrect a token/cookie from the already-exposed `deepcli/browser-data/` or `deepseek-cli/browser-data*/` directories to patch this - capture a fresh one instead.

## Security policy

1. Comment trust: only a created comment from a human OWNER/MEMBER/COLLABORATOR may invoke a comment route; the body must begin with one exact registered moniker. Both workflow expressions and Python enforce the gate.
2. Manual dispatch: a supplied event payload cannot impersonate `issue_comment` or `pull_request_review_comment`; comment events are accepted only when `GITHUB_EVENT_NAME` identifies the real webhook event.
3. Prompt boundary: issue titles, comment text, PR titles, and PR diffs are untrusted reference data. They are JSON-quoted in user messages and must never override system/developer policy or request credentials, environment variables, hidden prompts, or private data.
4. Least privilege: checkout uses the read-only `github.token` with `persist-credentials: false`; workflow permissions are `contents: read`, `issues: write`, and `pull-requests: write`. Operator and DeepSeek provider secrets are scoped to the DeepSeek invocation step, not the whole job.
5. Device route: the Termux agent uses `contents: read` plus issue/PR comment permissions; its agent token is scoped to the POST/poll steps and the GitHub token is scoped to reply steps. Existing assignment triggers remain unchanged.
6. No schedule, provider route, automatic PR-review trigger, credential, or runtime activation was added by this hardening.
7. Auth: model secret only for model — never reuse `GITHUB_TOKEN` / OPERATOR as model auth.
8. Session: persistent browser-compatible session cache is intentional for the web-wrapper; it may retain `ds_session_id`, `aws-waf-token`, chat-session state, and PoW-compatible metadata under the existing permission-restricted cache path. The Actions cache key is scoped to the repository and exact Git ref; it has no cross-ref restore prefix.
9. No cookies/tokens in Git or result artifacts; cache/session values are never logged. Cached WAF state wins on resume unless `DEEPSEEK_WAF_TOKEN_REFRESH=1` explicitly requests an environment-supplied replacement.
10. Output JSON is **metadata only** (no model text).
11. `pr_number` validated as positive decimal before any `gh pr` call.

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
