# Connector path evaluation (2026-11-19)

## Q: Is Composio more effective than the direct GitHub connector?

| Operation | Direct GitHub (GitHub_CoPilot_MCP) | Composio GitHub | Verdict |
|---|---|---|---|
| Search code and issues | ✓ (search_code, search_issues) | not tested | Direct |
| Read file contents | ✓ | ✓ (GITHUB_GET_REPOSITORY_CONTENT) | Tie |
| Repo metadata | ✓ (search_repositories) | not tested | Direct |
| Create branch | ✗ 403 | ✓ (GITHUB_CREATE_A_REFERENCE) | Composio |
| Commit one file | ✗ 403 | ✓ (CREATE_OR_UPDATE_FILE_CONTENTS) | Composio |
| Commit many files | ✗ 403 (push_files) | ✓ (COMMIT_MULTIPLE_FILES) | Composio |
| Compare commits | not tested | ✓ (GITHUB_COMPARE_TWO_COMMITS, basehead) | Composio |
| Open draft PR | not tested | ✓ (CREATE_A_PULL_REQUEST, draft) | Composio |

Result: Composio is the write path. Direct is the search path. Use each for its verified operations.

## Shortlist: MCP connectors to communicate with and leverage

| Rank | Connector | Use | Verified state |
|---|---|---|---|
| 1 | Composio (GitHub) | All repo writes, PRs, compares | Writes verified |
| 2 | GitHub_CoPilot_MCP | Search, read, repo metadata | Reads verified; writes 403 |
| 3 | Supabase lane-state | SQL, migrations, ledger | Writes verified |
| 4 | Todoist | Tasks and comments | Writes verified |
| 5 | Notion | Cockpit pages | Writes approved and verified |
| 6 | cloudflare (API) | Full Cloudflare API | Authenticated |
| 7 | Linear | Issues and triage | Reads verified |
| 8 | Sentry, Grafana Cloud | Errors, alerts | Reads verified |
| 9 | Figma, Lucid, Framer | Design surfaces | Writes verified; Figma quota tight |
| 10 | OpenSEO | SEO research | 500 credits; confirm above 2,000 |

Deferred: Product Velocity (read verified; quota fields absent), Elicit (Pro needed), Scite (inactive), ElevenLabs (auth incomplete).
