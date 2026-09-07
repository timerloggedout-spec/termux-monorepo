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

## Relationship to `hub_mcp`

This repo is not the same thing as [`hub_mcp/`](../hub_mcp), and one does not
replace the other:

- **`hub_mcp`** (added in [PR #221](https://github.com/timerloggedout-spec/termux-monorepo/pull/221))
  is the governed, signed job-envelope model: no public endpoint, capability
  tiers, replay prevention, redacted result envelopes. It's the accepted
  version-one path documented in
  [`docs/architecture/transport-and-identity-decision.md`](../docs/architecture/transport-and-identity-decision.md),
  which explicitly deferred any public-facing transport.
- **`mcp-hub`** (this repo, [PR #442](https://github.com/timerloggedout-spec/termux-monorepo/pull/442))
  is a deliberate, later exception to that default: the operator has a hard
  requirement for a persistent public access point, so this exists as a
  public Vercel HTTP surface, gated by a bearer token (`withMcpAuth` /
  `MCP_AUTH_TOKEN`, fails closed with 503 if unset) rather than by network
  boundary.

Pick per capability, not by habit: anything that doesn't need to be public
belongs behind `hub_mcp`'s job-envelope model, not bolted onto this router.
See the architecture doc's addendum for the full reasoning.

## Layout

```text
mcp-hub/
  termux-mcp/        git submodule -> github.com/timerloggedout-spec/termux-mcp
  android-mcp/       git submodule -> github.com/timerloggedout-spec/android-mcp
  api/
    auth.ts          withMcpAuth: timing-safe Bearer token check
    mcp/[server].ts  one dynamic router: /api/mcp/<server> dispatches by
                      name through a registry map, wrapped in withMcpAuth
  test/
    router.test.ts   covers server dispatch, unknown-server 404, and all
                      three auth outcomes (401 / 503 / forwarded)
  package.json       deps (mcp-handler, zod) + vercel/tsx dev tools
  vercel.json        one rewrite: /mcp/:server -> /api/mcp/:server
  tsconfig.json
```

## Endpoints (once deployed)

`https://<project>.vercel.app/mcp(-hub)/{termux, android, ...}` — both the
short `/mcp/` prefix and the `/mcp-hub/` prefix resolve to the same dynamic
router (`vercel.json` carries both rewrites), so either is a valid way to
address a host:

- `https://<project>.vercel.app/mcp/termux` or `/mcp-hub/termux`
- `https://<project>.vercel.app/mcp/android` or `/mcp-hub/android`

Both endpoints require `Authorization: Bearer <token>`, where the deployment's
token is configured through the `MCP_AUTH_TOKEN` environment variable.

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
same routes, not a replacement for them. `vercel.json` already defines two
equivalent rewrites — `/mcp/:server` and `/mcp-hub/:server`, both landing on
`/api/mcp/:server` — so `/mcp/termux` and `/mcp-hub/termux` are two spellings
of the same endpoint today, no custom domain required.

## Path pattern instead of one file per host

`/mcp/:server` is a Vercel rewrite wildcard, not a fixed list — every
`/mcp/<anything>` request lands on the single dynamic function at
`api/mcp/[server].ts`, which looks `<anything>` up in an in-code registry
map and delegates to that submodule's handler, after `withMcpAuth`
authenticates the request (validates the Bearer token; does not modify or
"clear" it). Adding a future MCP is a submodule + one registry-map line —
no new file, no `vercel.json` edit.

## One remaining manual step

This folder is designed to become the **Root Directory** of the existing
`termux-monorepo` Vercel project (Project Settings → General → Root
Directory → `mcp-hub`). That's a one-time dashboard change — nobody has done
it yet, so the endpoints above are not live yet. Until then, this is
reviewable code with no production effect.

Checked via this PR's own preview deployment: the project's Root Directory
is currently `deepseek-cli`, not the repo root — a different, unrelated
folder. Worth knowing before flipping it: that folder is where this repo's
documented credential exposure lives (`docs/CREDENTIAL-EXPOSURE.md` —
committed browser profile data with live session state). Repointing Root
Directory to `mcp-hub` stops deploying that folder, which is a net
improvement, but confirm nothing currently depends on whatever
`deepseek-cli`'s deployment outputs before switching.

If a Vercel token/PAT is provided instead, the same change can be made via
the Vercel API (`PATCH /v10/projects/{id}` with `rootDirectory: "mcp-hub"`)
without needing dashboard access. Either way, `MCP_AUTH_TOKEN` needs to be
set as an environment variable on the project before it's genuinely usable —
without it every request gets a 503, by design (fail closed, not open).

After the Root Directory switch, the next push (or this PR's preview
redeploy) is the real test: check the build log for successful submodule
checkout, then hit both endpoints with an `initialize` MCP handshake
(including the Bearer token) to confirm they respond like the previous
standalone deployment did.

## Adding a future MCP

1. `git submodule add <repo-url> mcp-hub/<name>` (or the manual gitlink
   equivalent if `git submodule` isn't available in your environment:
   `git update-index --add --cacheinfo 160000,<sha>,mcp-hub/<name>` plus a
   matching entry in the repo's `.gitmodules`).
2. Import that submodule's `GET`/`POST`/`DELETE` at the top of
   `api/mcp/[server].ts` and add one line to the `registry` map there —
   `withMcpAuth` already covers it, nothing extra needed for auth.
3. Add an entry to this folder's `catalog.json` with the new `/mcp/<name>`
   URL.

No new Vercel project, no new secrets, no new file, no `vercel.json` edit,
no second repo to keep in sync — it rides on this one deployment, this one
router, and this one catalog.
