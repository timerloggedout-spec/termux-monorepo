# Deployment Lanes

Single source of truth for every Vercel project deployed from this org's
repos. A "lane" is one Vercel project — each has exactly one Root Directory,
so a monorepo with independent deployables needs one lane per deployable,
not one project reused for everything. Add a row here whenever a new lane
is created; update it whenever a lane's purpose or Root Directory changes.

| Vercel project | Source repo | Root Directory | Purpose | Owning proposal/PR | Status |
|---|---|---|---|---|---|
| mcp-hub | termux-monorepo | `mcp-hub` | Public, bearer-token-gated MCP router serving `termux-mcp` and `android-mcp` as submodules via dynamic `/mcp/:server` routes | PR #442, docs/proposals/active/vercel-lane-topology | live, production branch `master` |
| termux-monorepo | termux-monorepo | `deepseek-cli` | Pre-existing, undocumented at time of writing — the folder it serves is the same one named in `docs/CREDENTIAL-EXPOSURE.md` | docs/proposals/active/vercel-lane-topology (VLT-001, open) | fate undecided — see VLT-001 |

## Why lanes, not one project

Vercel's Root Directory is a single value per project. A repo hosting more
than one independently-deployable thing (an MCP router, a docs site, a demo
app, ...) needs one Vercel project per thing, each pointed at its own
subfolder, all against the same GitHub repo. Reusing one project for a new
purpose silently stops serving whatever it served before — that mistake is
exactly what created the ambiguity this file exists to prevent (see
`docs/proposals/active/vercel-lane-topology/DEBATE.md` for the incident).

## Adding a new lane

1. Create a new Vercel project against this repo, set its Root Directory to
   the new subfolder, set its production branch explicitly.
2. Add a row to the table above in the same PR that adds the folder.
3. If the lane needs its own environment variables/secrets, document what
   they are (not their values) in the folder's own README.
