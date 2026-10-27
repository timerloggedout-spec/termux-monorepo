# BOINC — fleet free-compute donations & rankings

Owner order 2026-10-27: a donations-style lane — put free compute to work on
BOINC science projects under the fleet account, gamified for platform-ranking
competitiveness. **Free only, opportunistic, never a fleet dependency**
(mortality rule: nothing critical is single-homed on volunteered cycles).

Identity: `entrant{entrantBoinc}[platform:boinc]` (see
`config/registration_monikers.json`, `docs/ops/4N0N-REGISTRATION-PROTOCOL.md`).
Profile content lives in `docs/ops/PROFILE-REGISTRY.md` (BOINC lane section).
Science United was deliberately **not** used: its shared anonymous account
erases per-fleet ranking identity. All project accounts are individual, under
the moniker username, on the fleet Gmail (one cross-project ID).

## Accounts (verified 2026-10-27)

| Project | Account | Route | Client |
|---------|---------|-------|--------|
| NumberFields@Home | created (`entrantBoinc`) | Project Web RPC `create_account.php` | attached |
| SRBase | created (`entrantBoinc`) | Web RPC + the project's publicly posted invitation code (anti-spam speedbump, published on its homepage/FAQ) | attached |
| Einstein@Home | created (`entrantBoinc`, BOINC user ID 1066683) | Web only — the project refuses RPC creation ("Account creation is done through our Web site"); registered via the site's emailed one-time login, password set to the fleet BOINC password | attached (authenticator via Web RPC lookup) |

Authenticators/passwords are credentials: they live host-local only
(client data dir + `~/workspace/boinc/keys/`, 0600) — never in this repo,
never in chat. Password recovery is via the fleet Gmail.

## Host rule (owner, 2026-10-27) + assessment

**BOINC runs only on remote services the quota system allows, via GitHub
providers — and only on quota that repo development failed to use before
it expires.** BOINC is the sink for stranded quota, never a competitor
with repo work. (This supersedes the lane's earlier ToS caution on
GitHub surfaces: the account is the owner's, the ruling is the owner's,
and the control is the leftover-only bound below.)

| Surface | Verdict | Basis |
|---------|---------|-------|
| GitHub Codespaces | **EXCLUDED (owner, 2026-10-27, interim TBD)** | The fleet once burned a whole Codespaces allocation in an afternoon on a setup error; `gh` Codespaces is excluded until the owner reopens it. Not a BOINC surface. (Its data/spaces backup-and-restart-by-Oct-30 item belongs to another lane.) |
| GitHub Actions | **The burn surface** | The remaining GitHub-provider quota surface under the host rule. Leftover-only: the burn decision reads actuals from the GitHub billing usage API (`/users/<owner>/settings/billing/usage` — verified reachable via the PAT helper 2026-10-27), never the entitlement record alone. Guardrails baked in from the Codespaces incident: dispatch-only (never scheduled), one job at a time, a hard `timeout-minutes` cap, and an explicit budget input — a setup error must not be able to burn the month again. Activation needs one owner provisioning item: an Actions secret holding the project authenticators (names-only discipline; the lane does not invent it). Until it exists, no workflow references it. |
| Agent VM (this sandbox) | **Not a compute host** | Owner rule (remote GitHub-provider services only) — and independently walled: its egress proxy hangs POSTs to project schedulers (verified directly against 4 endpoints; GETs pass, allowlisted API POSTs pass). Role: provisioning/verification bench — the accounts and client attach were proven here; the kit is portable to the burn surface, whose egress is open. |
| Oracle / GCP / AWS / Azure free tiers | Out of scope | Not GitHub providers under the host rule (and card-gated besides). |
| Cloudflare surfaces | N/A | No general background compute exists there. |
| B160V (Android, official BOINC app) | Out of scope | Not a remote GitHub-provider service; device lanes own it regardless. |

Burn procedure (v1): (1) read the billing usage API for actuals and
confirm repo development has no claim on the remaining quota before
expiry; (2) dispatch the BOINC burn workflow (dispatch-only, single
job, hard timeout cap, explicit budget input) — it installs the client
from `ops/boinc/`, attaches with the owner-provisioned authenticator
secret, and crunches to the budget; (3) record standings in this doc
from the run's uploaded (credential-free) summary; (4) nothing persists
on the runner — hosts are ephemeral by design, accounts are
server-side.

## The kit (`ops/boinc/` in this repo + a host-local data dir)

- `ops/boinc/provision.sh` — per-project account create/lookup via the
  project Web RPCs + attach. Adding a project = one line. Reads
  credentials from the environment / an untracked local file; the repo
  copy carries no secrets.
- `ops/boinc/start.sh` — installs the client if missing
  (`apt-get install -y boinc-client`, 7.24.1 verified) and starts it
  against the host-local data dir given as `$1`.
- The **data dir is the host's identity** (account XMLs, client state).
  On the burn surface it is created fresh per window from `provision.sh`
  (accounts are server-side; hosts are cheap). On the bench VM it
  persists at `~/workspace/boinc/data`.
- `global_prefs_override.xml`: 100% CPUs, 50% RAM busy cap, 10% disk
  cap — volunteered cycles must never starve the host's real work.
- Credentials live host-local only (0600) — never in this repo. The
  one sanctioned exception is the burn's authenticator secret, and
  only once the owner provisions it (provisioning item, above).

First scheduler contact from the burn surface completes setup: work
fetches, credit populates, and this doc's status section gets its first
numbers.

## Projects & competitive strategy

Picked for a 2-core CPU host class; shares start equal, tuned on measured
recent average credit (RAC) after the first week of crunching:

- **Einstein@Home** (science anchor) — gravitational-wave searches;
  flagship peer-reviewed project, reliable work supply, strong badges.
- **NumberFields@Home** (reliability) — small, steady workunits; a
  low-power host always has work.
- **SRBase** (credit engine) — short CPU workunits with historically
  strong credit-per-hour; the ranking climber of the three.

Mechanics that move rankings, in order:
1. **Never waste a stranded quota window** — RAC is a decayed average;
   under the host rule the fleet crunches in pre-expiry bursts, so the
   mix is tuned for credit-per-core-hour inside a window, and every
   window is actually used.
2. **Project mix by measured RAC/hour** — re-weight resource shares
   monthly from the client's own numbers, not from folklore.
3. **Team** — `entrantBoinc` team founded on each project (below);
   team credit and team rank are separate ladders from user rank.
4. **Events** — BOINC Pentathlon (May) and Formula BOINC sprints are
   where small fleets move: concentrated crunching on announced
   projects. The lane watches the calendars and pre-positions the mix.
5. **Badges/milestones** — per-project badge tiers and BOINCStats
   milestones are the visible scoreboard; the status section tracks
   them firsthand (project stats pages / stats export), never scraped
   folklore.

## Status

- 2026-10-27 — lane stood up. Accounts: 3 created + attached
  (Einstein@Home — BOINC user ID 1066683, NumberFields@Home, SRBase),
  one identity `entrantBoinc` on the fleet Gmail. Credit 0 / RAC 0 —
  no host has fetched work yet (the bench VM is egress-walled and is
  not a compute host under the host rule). Team: **SRBase founded**
  (team 323, founder `entrantBoinc`, verified on the project's team
  page). NumberFields team outstanding — the project refuses RPC team
  creation and its web form needs a vault-backed browser login (two
  attempts died waiting on it); Einstein team state unverified (the
  founding browser task died before reporting; the account's team
  state is login-walled). Both residuals close at the first operator
  session that completes those logins; they gate nothing else.
  Next unlock: the owner-provisioned Actions authenticator secret,
  then the first leftover-quota burn window (billing-API actuals) and
  this section's first standings. WCG account (web registration) is
  the phase-2 project #4.
