# GitHub App process — AppID lane record (companion: ops/github-apps/PROCESS.json)

Owner: `[MUSEai]@{role:{appid-process}}` — GitHub App provisioning as fleet
specialist identities, end-to-end, programmatic-first (owner order
2026-10-29 21:17 PT; seed from quota-specialist). Creation route of record
stays the manifest flow (`docs/ops/GITHUB-APP-ROUTES.md`); this doc carries
custody, the permissions ladder, the distribution audit, the capacity
census, and the allocation queue. Credentials are names-only throughout.

## 1. Pilot state — verified firsthand 2026-10-30T04:18–04:26Z (App JWT)

| Fact | Value | Evidence |
|---|---|---|
| App | Termux Fleet Collector, ID `5535733`, client `Iv23liKMLj976ok6Cn3D`, slug `termux-fleet-collector`, PUBLIC | `GET /app` |
| Permissions | actions/checks/contents/issues/metadata/pull_requests = **read ×6**, events `[]` | `GET /app` |
| Installations | **1** — `176747357`, account `timerloggedout-spec`, `selected` repos | `GET /app/installations` |
| Repo scope | `timerloggedout-spec/termux-monorepo` only (total 1) | `GET /installation/repositories` |
| Bucket | installation core 5000/h, independent (remaining 4990 after audit calls while PAT core read 0 in the same window) | `GET /rate_limit` both principals |

Landed prerequisites: PR #2361 (pilot package), #2369 (manifest tool +
routes), #2385 (registry record `github.api.app_collector`), #2387
(provisioning record) — all read back merged via the app token itself.

## 2. Custody (queue item 1 — DONE)

- The bootstrap PEM and client secret moved out of the quota lane's
  scratch (`scratch/app-pilot/out/`, token file shredded) into the app's
  own connector home: `custom.github-app-collector` (local connector dir;
  `keys/collector.pem` + `keys/client_secret.txt`, both `0600`, dir
  `0700`). Public-key fingerprint (DER SHA-256, recordable):
  `3dfa81bd8f9deb303e521bf87f3999a404fdd2afd372a672ee723edd4c488d2a` —
  identical pre/post move; helper re-verified from the new home
  (`app` / `installations` / `rate` all live).
- Pattern rationale: vault-surrogate credentials travel as an HTTP header
  to a registered host; an app private key never travels — it signs the
  JWT locally. No swap point exists, so custody = a named local 0600 file
  in the app's connector dir, referenced by path/env name only.
- Key ID: GitHub exposes no API list of an app's private keys; keys are
  identified by fingerprint in app settings. Cap = 25 keys/app; keys do
  not expire; revocation is manual.
- Rotation (web-only residual): settings → Private keys → generate new →
  save over `keys/collector.pem` → verify helper → delete old key.
  Zero-downtime ordering is generate-first, delete-last.

## 3. Permissions matrix (queue item 2 — owner question, answered)

**Why the pilot is read-only.** (a) Least-privilege proof: the bucket
split — the thing being proven — needs reads only; a proof that requires
write proves nothing about discipline. (b) Public-install safety: the app
is public by design (any account may install it); read-only caps the
blast radius for every foreign installer and for us if the key leaks —
a leaked collector key yields reads on selected repos, never a publish
path. (c) Separation of duties: reads were the quota bleed (collectors
burned the PAT bucket); writes stay on the PAT until a dedicated writer
app exists. The collector is **never** expanded — the ladder adds new
apps per role.

| Role (function identity) | Permissions | Status | Kills / covers |
|---|---|---|---|
| `collector` — Termux Fleet Collector | metadata, contents, pull_requests, issues, checks, actions = read | **LIVE** 5535733 | Collector reads off the PAT bucket (proven) |
| `publisher` — `Edict` (draft template) | metadata read; checks read; **contents write; pull_requests write** | **LIVE** — App 5537873, installation 176799777, provisioned 2026-10-30 by quota-specialist under the owner's FINISH order (naming gate killed, draft template applied); self-published PR #2417 merged `88aa48f21f71` by its own token; custody → `custom.github-app-publisher/keys/` (fp `4f5515eb…`) | The pat_publish path (branch, file PUT, PR create, merge) dies when PAT core hits 0; the publisher bucket cannot be starved by collector traffic. **Delta vs the #2401 package:** as-submitted manifest has checks read and **no issues permission** (package carried issues write) — issue-comment routes are unavailable to this app; adding issues = write is an amendment and the UP-01 template candidate |
| `reviewer-ops` — name PROPOSED | metadata read; checks read; **pull_requests write** (reviews) | Proposed #2 (cadence bundle) | Peer-review orchestrator polling (≤180/h/event) + review comments off PAT |
| `gate-ci` — name PROPOSED | metadata read; **checks write** | Proposed #3 (cadence bundle) | Gate annotations + status posts (repo-gate, ECC-class surfaces; the PR #800 checks failure class) |
| `lifecycle` — name PROPOSED (supersedes this lane's earlier "steward" label) | metadata read; **issues write** | Proposed #4 (cadence bundle) | Issue lifecycle / triage sweeps, GAP-ledger sweeps |

**Bundle requirements (cadence handover, owner order 2026-10-29 21:36
PT — all apps, no exceptions):** manifest `public: true` from day one;
least-privilege only; no webhooks unless the function demands one;
custody per the §2 collector template; minter =
`scripts/github_app_token.py` pattern; installation scope
termux-monorepo first, distribution later; **books** per app = registry
record `github.api.app_<slug>` (5000/h/installation, hourly, reset =
x-ratelimit-reset) + allocations meta-pool slice + planner flow share,
via a #1884-citing re-split PR (quota-convergence executes; this lane
coordinates); **adoption proof** per app = first workflow run ON the app
token + a bucket reading (remaining while PAT low), Collector-style —
which is also the owner's DISTRIBUTED test (§4).

**Naming — CONFERENCE DRAFT received 2026-10-29 (registration-monikers
lane); DO NOT PROVISION on it.** Final set lands after marketing
conferral + owner. Draft sets (template = collector, of record):

| Role | appName | Slug (candidate) | Moniker | Alias |
|---|---|---|---|---|
| collector | Termux Fleet Collector | `termux-fleet-collector` | `Collector` | — (LIVE) |
| publisher | Termux Fleet Publisher | `termux-fleet-publisher` | `Edict` | Acta |
| reviewer-ops | Termux Fleet Reviewer | `termux-fleet-reviewer` | `Argus` | Panoptes |
| lifecycle | Termux Fleet Lifecycle | `termux-fleet-lifecycle` | `Janus` | Patulcius |
| gate-ci | Termux Fleet Gate | `termux-fleet-gate` | `Cerberus` | the Ward |

Bot username = `<slug>[bot]` in every case. Apps are FUNCTION
identities (Oracle/Delphi precedent), never lane monikers
(AGENT-MONIKERS.md scope rule untouched). Slug availability is verified
by this lane at creation; a taken slug returns to the registry lane for
a variant — never improvised in-lane. Creation of any bundle app waits
on the final set; package mechanics (manifest, custody, proof protocol)
do not.

Decision points reserved to the owner at publisher creation:
- `workflows: write` — required only to publish changes *to workflow
  files themselves*; without it the publisher lands everything except
  `.github/workflows/*`. Proposed as publisher rung 2, after first merges.
- `actions: write` (dispatch/rerun) — defer; dispatch needs are rarer
  and currently survivable.
- Publisher visibility: the prepared manifest ships `public: true`
  (fleet end-state: others may install). Switching to account-only is a
  one-field change before the single Create click.

**Amendment flow (how any permission change actually lands).** Existing
apps are amended in app settings (Permissions & events) — the manifest
flow creates new apps only, and there is no REST route for amending an
app. Adding a repository/organization/account permission emails every
installing account owner; the new permissions take effect on an
installation **only when that installation's owner approves** (banner in
the installation settings); until then the installation keeps its old
permissions. Removing permissions or webhooks takes effect immediately,
no approval. For fleet apps installed only on our own account that is one
owner click per app — which is exactly why the ladder prefers *new apps
per role* over amending the collector: a new app's consent is a fresh
install, and the collector's read-only grant is never re-opened.

Per-mint narrowing still applies on top: an installation token can be
scoped down at mint time (repository subset, permission subset), so a
role's app permissions are a ceiling, not a floor.

## 4. Distribution audit (queue item 3 — verdict: NOT DISTRIBUTED)

**Definition of record (owner, 2026-10-29 21:28 PT): `DISTRIBUTED` =
tested & installed in production replacement of parity structures** —
the app token actually runs the production work (collectors, publishers)
at parity with, and instead of, the PAT-based structures it succeeds.
Installs or secrets alone do not count. The D1–D3 checks below are the
supporting evidence ladder toward that state; under the owner's
definition the verdict is NOT DISTRIBUTED on every rung (0 production
workflows run on the collector token; PAT collectors remain the
production structure).

- **D1 — installations:** `installations_count > 1`, or any installation
  on an account other than `timerloggedout-spec`. Evidence 2026-10-30:
  `GET /app` → `installations_count = 1`; `GET /app/installations` → the
  sole installation is ours, selected-repos, termux-monorepo only.
  Neither cadence nor anyone else has installed it anywhere else.
- **D2 — workflow adoption:** any `.github/workflows/*` minting collector
  tokens (app id, slug, or collector secret names). Evidence: code search
  `termux-fleet-collector` in `.github/workflows` = **0 hits** (repo-wide
  hits are only the pilot PROFILE + pilot doc). The three workflows that
  use `actions/create-github-app-token` bind `vars.APP_CLIENT_ID` /
  `secrets.APP_PRIVATE_KEY` — the pre-existing capability-probe app
  (PR #800 lineage), a different app, not the collector.
- **D3 — Actions secret:** a repo Actions secret holding the collector
  PEM (names-only check). Evidence 2026-10-30T04:44Z: all **58** repo
  Actions secret names read via the PAT helper — **no collector PEM
  secret present**. Side finding: `APP_PRIVATE_KEY`, bound by the three
  capability-probe workflows, is also absent from the repo-level names;
  its source is org/environment-level or unprovisioned (NOT ESTABLISHED
  here; flagged, not this lane's fix).

Distribution, when ordered, = provision the PEM as a repo secret
(names-only, sealed-box route via the PAT helper — the Neon secrets
precedent) + a workflow that mints via `scripts/github_app_token.py`
or `actions/create-github-app-token` with the collector's client id.

## 5. Capacity census (queue item 4 — GitHub docs, firsthand read 2026-10-30)

| Limit | Value | Source |
|---|---|---|
| Apps registered per user / org / enterprise | **100** (no limit on how many apps an account can *install*) | GitHub Docs, Registering a GitHub App |
| Private keys per app | **25**; keys do not expire | GitHub Docs, Managing private keys; changelog 2024-11-08 |
| App JWT lifetime | ≤ 10 minutes | GitHub Docs, Generating a JWT |
| Installation token lifetime | 1 hour | GitHub Docs, Generating an installation access token |
| Installation rate limit | min **5,000/h**; non-Enterprise-Cloud scaling +50/h per repo beyond 20 and per org user beyond 20, cap **12,500/h**; Enterprise Cloud org/enterprise 15,000/h | GitHub Docs, Rate limits for the REST API |
| Our installation today | 1 repo, personal account → flat 5,000/h per (app × installation) | §1 evidence |

Fleet position: **1 owned app established** (collector). A REST route to
list an account's *owned* apps does not exist (`/user/installations` is
installations-on-us and refuses PATs by design), so any other
owner-registered apps are NOT ESTABLISHED via API — an owner-UI census
item of record, not a blocker. Arithmetic on the established floor:
each new specialist = +1 registration against 100 and, once installed on
termux-monorepo, **+1 independent 5,000/h bucket**. The full slate
(collector + the four bundle apps) = 5% of the registration cap and
25,000/h of separated installation quota.

**Real binding constraints are operational, not GitHub caps:**
(1) custody — one PEM + client secret per app under the §2 pattern;
(2) bookkeeping — one install consent + one permission-approval surface
per (app × account); (3) web-only residuals per app — one Create click,
one install consent, avatar upload, key rotation; (4) distribution —
one repo secret per (app × repo) before any workflow can mint;
(5) secondary rate limits still apply platform-wide (GitHub publishes
no single number; none is claimed here).

## 6. Allocation queue (queue item 5)

Build order (bundle of four, cadence handover 2026-10-29):

1. **Publisher — DONE (2026-10-30).** Provisioned by the quota-specialist
   lane under the owner's FINISH order (the naming gate was killed;
   conference draft template applied). App 5537873, installation
   176799777, bucket + write proof passed, record self-published as
   PR #2417, custody transferred to the §2 pattern
   (`custom.github-app-publisher`). Remaining publisher items: avatar
   upload (PNG, web-only) and the issues-write amendment decision
   (UP-01 candidate).
2. **Reviewer-ops** — orchestrator poll burn is the largest steady PAT
   drain after publishes.
3. **Gate/CI** — checks publication, the PR #800 failure class.
4. **Lifecycle** — sweeps are the lowest-frequency drain; last.

Four roles landed = 4 registrations of the 100 cap and 20,000/h of
separated installation quota on termux-monorepo (§5).

## 7. Per-app repos + submodules (owner question, 2026-10-29 21:28 PT)

Current state: **no** — no fleet app has its own repo. The collector
lives as a plain package dir (`ops/github-apps/collector-pilot/`) inside
termux-monorepo; `.gitmodules` (read firsthand 2026-10-30) carries only
forks/vendors/mcp submodules, none for apps. Repo precedent is mixed:
repo-replay got its own repo with import-by-reference (NOT a submodule).

Proposal (this lane, for the publisher creation point): each app gets
its **own repo** `timerloggedout-spec/<app-slug>` holding manifest,
profile, avatar, app-specific tooling and docs (never secrets — custody
stays §2), and termux-monorepo includes it as a **shallow submodule** at
`ops/github-apps/<role>-pilot/`, replacing the plain dir. Gains: an
independent lifecycle/version history per app, a public home per app
(the Marketplace-readiness direction, §8), and monorepo pinning by
gitlink SHA exactly like the existing fork submodules. Cost: one extra
repo per app + gitlink bumps on app-package changes.

## 8. Later queue (owner, 2026-10-29 21:28 PT — parked, not this pass)

- **User-access tokens vs installation tokens:** evaluate the user
  authorization callback URL and the device flow for generating a user
  access token (owner-supplied docs:
  `docs.github.com/en/apps/creating-github-apps/registering-a-github-app/about-the-user-authorization-callback-url`,
  `docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#using-the-device-flow-to-generate-a-user-access-token`)
  against the installation-token-only posture — where acting *as the
  user* through an app beats acting *as the installation*.
- **Marketplace publishing** of the fleet's apps (listing, review gate,
  plans) — the public apps are built public from day one; listing is a
  separate later step.

## 9. Rules carried

Caveman-micro reporting; outcomes = PR# + merge SHA (history-verified);
credentials names-only, values never in chat/files/commits; GitHub API
via the PAT helper or App JWT — never a browser sign-in as a credential
route; VM = sandbox only (custody files are local secrets at rest, not a
service; all continuous work stays in repo automation).
