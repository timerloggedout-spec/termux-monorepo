# MCP Hub

Consolidated host for this org's MCP (Model Context Protocol) servers, served
from a single Vercel deployment instead of one project per server.

## Why this exists

`termux-mcp` and `android-mcp` started as two separate repos, each with its
own Vercel project, each needing its own `VERCEL_TOKEN` / `VERCEL_ORG_ID` /
`VERCEL_PROJECT_ID` secret trio. That's tedious to keep in sync and doesn't
scale as more MCPs get added. This hub mounts each MCP server as a git
submodule and re-exports its handler through a thin wrapper function, so
they all deploy together as one Vercel project with one set of credentials.

The submodule repos remain the source of truth for their own tool
implementations, history, and CI (`ci.yml`, `vercel-deploy.yml` in each stay
as-is and keep working independently if ever needed standalone). This hub
only adds the routing layer on top.

## Layout

```
mcp-hub/
  termux-mcp/       git submodule -> github.com/timerloggedout-spec/termux-mcp
  android-mcp/      git submodule -> github.com/timerloggedout-spec/android-mcp
  api/
    termux.ts       re-exports termux-mcp's handler
    android.ts      re-exports android-mcp's handler
  package.json      shared deps (mcp-handler, zod) the wrappers need to build
  vercel.json       routes /mcp/termux and /mcp/android to the wrappers
  tsconfig.json
```

## Endpoints (once deployed)

- `https://<project>.vercel.app/mcp/termux`
- `https://<project>.vercel.app/mcp/android`

## Hosts and their real status

This table (and the machine-readable version in `catalog.json`) used to live
in a separate `mcp-multi-host` repo. That repo had no server code of its own
— it was just this table plus a client-config snippet, kept in sync by hand
in a second place. It's folded in here instead: one hub, one catalog, one
place that can drift out of date instead of two.

| ID | Repo | Status |
|----|------|--------|
| `termux-mcp` | [termux-mcp](https://github.com/timerloggedout-spec/termux-mcp) | Live today at `termux-mcp.vercel.app/mcp` (its own standalone project). Moves to `/mcp/termux` on this hub once the Root Directory switch below happens. |
| `android-mcp` | [android-mcp](https://github.com/timerloggedout-spec/android-mcp) | Never deployed — no `android-mcp.vercel.app` project exists. This hub is now the deploy path instead of standing up a second project. |
| `github-remote` | GitHub-hosted | Externally hosted, not part of this deployment: `https://api.githubcopilot.com/mcp/` |
| `gh-aw-mcpg` | [gh-aw-mcpg_fork](https://github.com/timerloggedout-spec/gh-aw-mcpg_fork) | Fork present, not folded into this hub yet |

## Can this be a subdomain instead of `/mcp/*` paths?

Short answer: this hub already satisfies "one deployment, not one project per
server" — that part doesn't need a subdomain. A literal subdomain like
`mcp.termux-monorepo.vercel.app` isn't something Vercel's free `vercel.app`
domain allows — subdomains of `vercel.app` are one-level project slugs
(`<project>.vercel.app`), not further subdividable by anyone but Vercel
itself. If a custom domain is ever attached to this project, an alias like
`mcp.yourdomain.com` pointing at the *same* project is possible and would
still be "one deployment" — it would just be a nicer front door over the
same `/mcp/termux` and `/mcp/android` routes, not a replacement for them.

## One remaining manual step

This folder is designed to become the **Root Directory** of the existing
`termux-monorepo` Vercel project (Project Settings → General → Root
Directory → `mcp-hub`). That's a one-time dashboard change — nobody has done
it yet, so the endpoints above are not live yet. Until then, this is
reviewable code with no production effect.

If a Vercel token/PAT is provided instead, the same change can be made via
the Vercel API (`PATCH /v10/projects/{id}` with `rootDirectory: "mcp-hub"`)
without needing dashboard access.

After the Root Directory switch, the next push (or this PR's preview
redeploy) is the real test: check the build log for successful submodule
checkout, then hit both endpoints with an `initialize` MCP handshake to
confirm they respond like the previous standalone deployments did.

## Adding a future MCP

1. `git submodule add <repo-url> mcp-hub/<name>` (or the manual gitlink
   equivalent if `git submodule` isn't available in your environment:
   `git update-index --add --cacheinfo 160000,<sha>,mcp-hub/<name>` plus a
   matching entry in the repo's `.gitmodules`).
2. Add `mcp-hub/api/<name>.ts` re-exporting that server's handler, same
   pattern as `termux.ts` / `android.ts`.
3. Add a rewrite + function entry for it in `vercel.json`.
4. Add an entry to this folder's own `catalog.json` with the new `/mcp/<name>` URL.

No new Vercel project, no new secrets, no second repo to keep in sync — it
rides on this one deployment and this one catalog.