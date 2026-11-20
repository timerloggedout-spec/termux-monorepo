# Session && Context Management (GitHub Actions)

**Issue:** [#118](https://github.com/timerloggedout-spec/termux-monorepo/issues/118)  
**Related:** #109 · #112 (merged) · #114 · #72 · PR #3 (session-store untrack)

## Why “cached data was removed”

| Layer | What it holds | Persistence policy |
|-------|---------------|--------------------|
| **Auth session** | Cookies, Bearer tokens, PoW answers/signatures, browser profile | **Ephemeral only** — `$RUNNER_TEMP` / `$HOME` override inside the job; discarded at job end. Never Actions cache, never commit, never artifact. |
| **Work context** | Task key, last-reviewed SHA, provider `session_id` *hash* (not the token), last action type, short status flags | **Durable (non-secret)** — Actions cache + optional PR/issue comment marker. |

PR **#112 / #114** deliberately dropped DeepSeek session/cookie caching after CodeRabbit + Devin required that no session material land in the tree or cross-run secrets surface. That fixed a security class problem; it also removed the accidental ability to “pick up the same chat.”

#118 is the product follow-up: **continue the *work*, not the *credentials*.**

## What you can continue / regenerate / edit

Using `.github/actions/agent-context-store`:

1. **Load** prior context for a stable key (`pr-123-review`, `issue-118-triage`, …).
2. **Decide** whether to skip (same SHA already reviewed), re-diff only changed files, or regenerate.
3. **Save** updated non-secret fields after the run.
4. Optional **comment marker** `<!-- agent-ctx:<key> -->` so humans/agents see a pointer on the issue/PR.

Forbidden keys are stripped on both load and save: `token`, `cookie(s)`, `authorization`, `api_key`, `pow_*`, `password`, `secret`, and any key containing those substrings.

## Usage sketch

```yaml
- name: Load work context
  id: ctx
  uses: ./.github/actions/agent-context-store
  with:
    mode: load
    context_key: pr-${{ github.event.pull_request.number }}-review

- name: Agent step
  # use fromJSON(steps.ctx.outputs.context_json).last_sha etc.

- name: Save work context
  if: always()
  uses: ./.github/actions/agent-context-store
  with:
    mode: save
    context_key: pr-${{ github.event.pull_request.number }}-review
    context_json: |
      {"last_sha":"${{ github.event.pull_request.head.sha }}","last_action":"review","provider_session_hash":"${{ steps.hash.outputs.value }}"}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    target_number: ${{ github.event.pull_request.number }}
    repository: ${{ github.repository }}
```

## Auth session path (DeepSeek web-wrapper and similar)

Keep the #114 pattern:

```bash
export HOME="${RUNNER_TEMP}/deepseek-webwrapper-home"
mkdir -p "$HOME"
# … create_session / chat …
rm -rf "${RUNNER_TEMP}/deepseek-webwrapper-home"   # always()
```

If a provider returns a `session_id`, store only a **hash** (or the last 8 chars for logs) inside work context — never the full id + token pair.

## Gemini / peer review continuity

Existing Gemini review already uses soft-budget skip comments and router peers. Prefer embedding **SHA bookmarks** in work context rather than re-introducing cookie caches.

## Operator checklist

- [ ] Secrets stay in GitHub Secrets / local `~/.deepcli` (ignored).
- [ ] No `session.json` / `cookies_*.json` in the index (see `.gitignore` + #3).
- [ ] New workflows call `agent-context-store` for any multi-run agent task.
- [ ] Regenerating a response = new invoke with prior `last_sha` / task flags loaded, not replaying auth cookies.

## Trace

| Artifact | Role |
|----------|------|
| #118 | Continuity requirement |
| #109 | DeepSeek CI integration source |
| #112 | Executable workflow + ephemeral session policy (merged) |
| #114 | Peer routing + web-wrapper opt-in (open) |
| #72 | Quota + session continuation foundations |
| #3 | Untrack historical session stores |
