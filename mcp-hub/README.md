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

## Endpoints (live)

Deployed as its own Vercel project (`mcp-hub`, not a Root-Directory takeover
of the pre-existing generic `termux-monorepo` project — that project hosts a
different, unrelated lane and was left untouched; see "Why a separate Vercel
project" below):

- `https://mcp-hub-lime.vercel.app/mcp/termux` or `/mcp-hub/termux`
- `https://mcp-hub-lime.vercel.app/mcp/android` or `/mcp-hub/android`

Both the `/mcp/` and `/mcp-hub/` prefixes resolve to the same dynamic router
(`vercel.json` carries both rewrites) — either is a valid way to address a
host. Both endpoints require `Authorization: Bearer <token>`, where the
token is the project's `MCP_AUTH_TOKEN` environment variable. Verified live
with a real `initialize` handshake against both hosts, through both prefixes,
and confirmed a missing/wrong token still gets a 401.

## Hosts and their real status

This table (and the machine-readable version in `catalog.json`) used to live
in a separate `mcp-multi-host` repo. That repo had no server code of its own
— it was just this table plus a client-config snippet, kept in sync by hand
in a second place. It's folded in here instead: one hub, one catalog, one
place that can drift out of date instead of two.

| ID | Repo | Status |
|----|------|--------|
| `termux-mcp` | [termux-mcp](https://github.com/timerloggedout-spec/termux-mcp) | Still independently live at `termux-mcp.vercel.app/mcp` (untouched standalone project) *and* now live at `/mcp/termux` on this hub — both work, hub is the recommended one going forward. |
| `android-mcp` | [android-mcp](https://github.com/timerloggedout-spec/android-mcp) | Never had its own standalone deployment — this hub is its only live deployment, at `/mcp/android`. |
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

## Why a separate Vercel project

Earlier drafts of this doc planned to repoint the existing, pre-existing
`termux-monorepo` Vercel project's Root Directory at `mcp-hub`. That plan
changed: this repo hosts several distinct production lanes, and a
project's Root Directory is a single value, not a list — hijacking the one
existing generic project for `mcp-hub` would just move the "only one lane
gets to be deployed" problem instead of fixing it, and would still depend
on `master` always carrying whatever the pre-existing project actually
serves. Vercel's own supported pattern for a monorepo with multiple
independently-deployable lanes is multiple projects against the same
GitHub repo, each with its own Root Directory — so `mcp-hub` got its own
dedicated project instead. This also sidesteps the fact that changing an
*existing* project's production branch isn't exposed by Vercel's public API
at all (confirmed against Vercel's own engineering responses) — a brand
new project just declares its production branch (`master`) at creation.

The pre-existing `termux-monorepo` Vercel project (currently rooted at
`deepseek-cli`, where `docs/CREDENTIAL-EXPOSURE.md`'s committed browser
profile data lives) was left untouched — repointing or retiring it is a
separate decision for whoever owns that lane, not something this PR forces.

Two real bugs only surfaced once this was actually deployed and hit with a
live request, not by reading the code:

1. `mcp-hub/package.json` sets `"type": "module"`, so Node's ESM loader
   resolves relative imports literally — `tsconfig`'s
   `moduleResolution: "Bundler"` let extensionless imports (`"../auth"`)
   pass type-checking, but Vercel's zero-config build doesn't bundle these
   functions into one file, so it crashed at invocation with
   `ERR_MODULE_NOT_FOUND`. Fixed by adding explicit `.js` extensions.
2. Both `termux-mcp` and `android-mcp` call `createMcpHandler(...)` with no
   `basePath` override, so each only recognizes requests whose path is
   literally `/mcp` (its hardcoded default). Forwarded as-is through this
   router, a request that actually arrives as `/mcp/termux` failed that
   internal check and the submodule returned its own silent 404 — never
   reaching this router's own `unknownServerResponse`, since that only
   fires for names *absent* from the registry. Fixed by rewriting the
   forwarded request's path back to `/mcp` before delegating.

Also disabled Vercel's own "Deployment Protection" (SSO wall) on the new
project — it defaults to protecting every `*.vercel.app` URL behind a
Vercel login, which would have made the endpoint unreachable by any real
MCP client regardless of the `MCP_AUTH_TOKEN` check. That check is the
intended gate now; the platform-level one was redundant with it for this
project's purpose.

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
