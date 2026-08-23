# Mintlify documentation surface

**Status:** ACTIVE  
**Repo root is the docs root** (not a nested `docs/` site tree).  
**Config:** [`docs.json`](../../docs.json)  
**App:** Mintlify GitHub App (deploy + PR preview checks)

## What agents use

| Path | Role |
|------|------|
| `docs.json` | Navigation, theme, site name — **must list every public page** |
| `*.mdx` at repo root and under `concepts/`, `components/`, `guides/`, `governance/`, `proposals/`, `reference/` | Published pages |
| Mintlify GitHub App | Sync on push; PR **Mintlify Deployment** check + preview |
| Hosted site `/mcp` | Auto-generated **search** MCP for AI clients (public docs only) |
| [Mintlify remote MCP](https://mcp.mintlify.com) | Official OAuth MCP for dashboard-linked edit/search (operator client setup) |

There is **no separate Mintlify connector** in the monorepo agent tool belt. Publish by **Git** (branch → PR → merge to the docs production branch, currently `master`).

## Operator rules

1. **Nav completeness** — If an MDX file is intended for the sidebar, it must appear under `navigation.tabs[].groups[].pages` in `docs.json`. Empty groups hide content that already exists on disk.
2. **One fat docs stream** — Prefer stacking Mintlify page + nav updates on a single branch over many micro-PRs (operator mega-PR preference).
3. **Gates still apply** — Docs-only PRs still run `repo_gate` / `termux_smoke` / hygiene when those workflows fire; do not skip on “docs only” without evidence.
4. **Preview before merge** — Wait for the Mintlify Deployment check on the PR when the App is installed.
5. **Do not hand-edit generated catalog noise** for Mintlify; edit MDX + `docs.json` only.

## Local CLI (optional)

```bash
npm i -g mint
mint dev          # local preview
mint validate     # config + page checks
mint broken-links # link audit
```

See [Mintlify CLI](https://www.mintlify.com/docs/cli/index).

## Related

- Issue #175 — operator priority matrix
- PR #323 — initial `docs.json`
- Dashboard landing commit — bulk MDX seed (`Mintlify-Source: dashboard-editor`)
- PR #326 — Notation Sets proposal page
