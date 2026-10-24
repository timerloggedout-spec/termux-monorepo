# Mintlify documentation surface

**Status:** ACTIVE  
**Repo root is the docs root** (not a nested `docs/` site tree).  
**Config:** [`docs.json`](../../docs.json)  
**App:** Mintlify GitHub App (deploy + PR preview checks)

## Documentation surfaces and tools

| Surface | Role | Trust boundary |
|------|------|------|
| Git-tracked `docs.json` | Navigation, theme, site name, site-wide Markdown/agent instructions | Version-controlled publication input |
| Root-level and documented subdirectory `*.mdx` pages | Published documentation | Source content; navigation must include intended public pages |
| Mintlify GitHub App | Git sync, deployment and PR preview checks | Preview/deployment signal, not engineering correctness |
| Hosted `/mcp` | Documentation-search MCP surface for AI clients, when enabled | Public documentation retrieval; not an admin editor |
| Mintlify remote MCP (`https://mcp.mintlify.com`) | Authenticated operator-side search/edit/navigation/configuration workflows when authorized | Deployment/account permissions apply; inspect scope before mutation |
| Context7 MCP | Current, library-specific API/framework documentation and examples | Research input; version-match and verify consequential claims |
| GitHub | Reviewable repo history, branches, commits, PRs and CI | Repository source of truth and review trail |

**Important distinction:** an operator may have an authenticated Mintlify MCP connector in ChatGPT without that connector being installed in every repo-local agent runtime. The current repository baseline separately configures Context7 in `.codex/config.toml`. Never infer local runtime capability from the availability of a connected ChatGPT tool.

## Operator rules

1. **Navigation completeness** — If an MDX file is intended for the public sidebar, include it in the appropriate `navigation.tabs[].groups[].pages` entry in `docs.json`. A file existing on disk does not mean it is published or discoverable.
2. **Research before changing technical guidance** — Use Context7 to resolve the exact library and version, query a focused topic, and compare the answer with repository pins/configuration. Treat retrieved examples as evidence to adapt, not code to paste blindly.
3. **Inspect before edit** — Search for duplicate guidance, read the complete target page and inspect navigation/configuration before structural changes.
4. **Use the right edit surface** — MDX body changes belong in page content; frontmatter and navigation metadata require structured node operations; site-wide settings belong in `docs.json`/the appropriate configuration operation.
5. **Prefer coherent, reviewable changes** — Batch related documentation changes on one feature branch/PR rather than scattering micro-PRs. Keep the diff narrow enough to review.
6. **Gates still apply** — Docs-only PRs still run repository gates and relevant hygiene when those workflows fire. Do not skip checks without observed evidence.
7. **Preview before promotion** — Inspect the Mintlify Deployment check/preview when available. A preview, save, or open PR is not a production deployment.
8. **No implicit production publishing** — Use a review-first branch/PR for substantive changes. Publish/merge only when explicitly requested; verify the returned merge/deployment state afterward.
9. **Do not hand-edit generated catalog noise** — Edit source MDX and `docs.json`; treat generated diagrams/catalogs as outputs of their documented automation.
10. **Keep private configuration private** — MCP credentials, user-specific endpoints and secrets belong in external/local configuration, never in committed docs or source.

## AI-agent discoverability

For Mintlify-hosted docs, evaluate the actual deployed output rather than assuming every feature is enabled:

- `/llms.txt` provides a structured index and descriptions based on site metadata/navigation.
- `/llms-full.txt` and `/.well-known/llms-full.txt` may provide combined Markdown context for agents.
- Hosted `/mcp` may provide documentation search for AI clients.
- Mintlify remote MCP is the authenticated operator workflow and is distinct from the public search surface.
- `markdown.instructions` in `docs.json` can provide concise site-wide instructions for Markdown/agent consumers; use it only when stable and useful, and avoid duplicating full governance documents.

Verify exact URLs, visibility rules, and generated content on the target deployment. Do not assume private/hidden pages are exposed or public pages are automatically in navigation.

## Local CLI (optional)

```bash
npm i -g mint
mint dev          # local preview
mint validate     # config + page checks
mint broken-links # link audit
```

See [Mintlify CLI](https://www.mintlify.com/docs/cli/index).

## Related

- [Context7 + Mintlify MCP operating contract](CONTEXT7-MINTLIFY-INTEGRATION.md)
- Issue #175 — operator priority matrix
- PR #323 — initial `docs.json`
- Dashboard landing commit — bulk MDX seed (`Mintlify-Source: dashboard-editor`)
- PR #326 — Notation Sets proposal page
