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
4. Update `mcp-multi-host`'s `catalog.json` with the new `/mcp/<name>` URL.

No new Vercel project, no new secrets — it rides on this one deployment.