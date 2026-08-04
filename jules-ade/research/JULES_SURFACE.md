# Jules surface — what we integrate

## Mental model

```text
Orchestrator (Termux agent / Grok / Claude / Codex)
    → MCP or CLI (jules-mcp / jules-dispatch)
        → Jules API (JULES_API_KEY)
            → Cloud VM session bound to GitHub source
                → PR on target branch
```

Jules is **not** a local model runner. It is a **cloud coding agent fleet** with GitHub integration. Our job in `jules-ade/` is to make HOME agents able to **delegate** reliably.

## Official tools we care about

### SDK (`@google/jules-sdk`)

- `jules.session({ prompt, source, ... })` — start work
- `jules.all([...])` — parallel fleet with concurrency control
- Session result → PR URL when complete
- Repoless sessions exist (no GitHub) for pure compute tasks

### MCP (`@google/jules-mcp`)

Typical tools:

- `create_session` / `list_sessions` / `get_session_state`
- `send_reply` (including plan approval)
- `get_code_review_context` / `show_code_diff`
- `query_cache`

Config shape (illustrative — secrets via env only):

```json
{
  "mcpServers": {
    "jules": {
      "command": "npx",
      "args": ["@google/jules-mcp"],
      "env": { "JULES_API_KEY": "${JULES_API_KEY}" }
    }
  }
}
```

### Dispatch pattern (jules-dispatch)

- Tasks as YAML: title, repo, branch, prompt
- Batch create with concurrency limit
- Poll → collect PR links
- Usable as MCP tool from other agents

## HOME integration targets

| Target | Why |
|--------|-----|
| `feature/jules-ade` task YAML | Agents claim work offline; dispatch online when key present |
| Termux MCP (PR #7) | Cloud Jules cannot see device FS; Termux MCP closes that loop |
| Linear | Already connected — Jules has native Linear MCP on Jules side |
| `master-staging` | All Jules PRs should target staging per gate spine |

## Non-goals

- Reimplementing Jules cloud VMs locally
- Storing API keys in git
- Forcing Antigravity runtime as a hard dependency of doctor/CI
