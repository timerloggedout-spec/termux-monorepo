# GitHub App Fleet — Migration, Maintenance & Upgrade Plan

Status: PLAN OF RECORD (2026-10-30). Owner order 2026-10-29 21:37 PT.
Companions: `docs/ops/GITHUB-APP-PROCESS.md` (AppID lane — process, custody,
permission ladder), `ops/github-apps/PROCESS.json`, `ops/github-apps/ROUTES.json`,
`ops/quota/registry.json` + `ops/quota/allocations.json` (issue #1884),
checklist: `ops/github-apps/MIGRATION-ITEMS.md`.

Fleet rules bind throughout: GitHub access via the vault PAT helper or an app
token only (never a browser sign-in as a credential route); credentials
names-only in chat, files and commits; the VM is a sandbox — every recurring
mechanism below lives in a GitHub Workflow, never a local daemon or cron.

## 0. State of record (verified firsthand 2026-10-30T04:40Z)

| Fact | Value | Evidence |
|---|---|---|
| Apps registered | 1 of 100 cap | Termux Fleet Collector |
| Collector | App ID 5535733, slug `termux-fleet-collector`, public | App JWT read |
| Installation | 176747357, `timerloggedout-spec/termux-monorepo` only | installations_count=1 |
| Collector perms | actions, checks, contents, issues, metadata, pull_requests — all **read** | minted token metadata |
| Bucket split | PROVEN 2026-10-30T02:18Z: app 5000/5000 while PAT core 0 | quota-specialist firsthand |
| Registry record | `github.api.app_collector` in the github meta-pool, limit 5000/h/installation | PR #2385/#2391, #1884 re-split |
| Minter | `scripts/github_app_token.py` (stdlib + openssl RS256; key path via env, never in chat) | landed on master |
| Custody | `custom.github-app-collector/keys/collector.pem`, 0600, dir 0700; SHA-256 fingerprint `3dfa81bd…c488d2a` recorded in that connector's CONNECTOR.md | AppID lane transfer 2026-10-30 |
| Adoption | **PENDING — 0 production workflows run on an app token.** PAT-driven collectors are still production (owner DISTRIBUTED test: tested ∧ installed ∧ production-replacement of parity structures ⇒ not yet distributed) | workflow scan 2026-10-30 |
| Workflow surface | 257 workflows on master | Actions API via app token |
| In-flight probe | `.github/workflows/github-app-capability-probe.yml` mints via `actions/create-github-app-token` from `APP_PRIVATE_KEY` / `APP_CLIENT_ID` — those names belong to that probe's **Checks:write** app (PR #800 lineage), **not** the Collector; not provisioned, and never to be provisioned with the Collector PEM (identity separation, resolved 2026-10-30, MIGRATION-ITEMS SEC-01). The Collector's own Actions pair is `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY` + `TERMUX_FLEET_COLLECTOR_CLIENT_ID` (SEC-02), proven by `github-app-collector-mint-probe.yml` | workflow sources |

Slate when built (build order per AppID lane): Collector + Publisher +
Reviewer-ops + Gate/CI + Lifecycle = **5 principals × 5000/h = 25,000/h
separated**, each an independent bucket with independent defer rules (§2.5).
Proposed names are a naming-conference DRAFT (registry lane, 2026-10-29,
DO-NOT-PROVISION until marketing conferral + owner close): Publisher `Edict`,
Reviewer-ops `Argus`, Lifecycle `Janus`, Gate/CI `Cerberus`; slugs
`termux-fleet-<function>` are candidates verified at creation by the AppID
lane. This plan is naming-independent: it binds to permission classes.

Principal classes — never conflated anywhere in this plan (quota lane
confirmation, 2026-10-30, ∅ corrections): **installation token = 5000/h per
installation** (one bucket per installation; the planning figure stays 5000 —
any scaling with install/repo counts is NOT ESTABLISHED until measured);
**user PAT = 5000/h per USER**, shared across every same-account PAT
(rotating PATs adds no bucket); **Actions `GITHUB_TOKEN` = 1000/h per repo**.
Per-bucket flow target = limit ÷ window phase-aligned to the reset epoch
(5000/60 ≈ 83.3/min per installation bucket; PR #2381), split per consumer
slice — slice flow = bucket flow × slice share, re-derived on every #1884
re-split and every new app allocation (PR #2384); reserve = timing slack,
releasing into lower priority classes as the reset nears.

## 1. Deliverable 1 — Migration map

Calls/run are estimates of record where a lane has measured them; where no
measurement exists the entry says MEASURE-AT-GATE — the first app-token run
records the real count into the quota registry (§2.4) and no number is
invented here.

### 1.1 Wave 0–1 → Collector (exists now; read-only ×6 is sufficient)

| # | Consumer | Current bucket / credential | Calls/run | Gate | Rollback |
|---|---|---|---|---|---|
| M1 | `repository-observatory.yml` (daily 04:17Z) | PAT-class repo secret (`OPERATOR_GITHUB_TOKEN` lane) | — | **DISPOSITIONED 2026-10-30: NOT MIGRATABLE as a whole.** Firsthand app-token probe: public owned = 30 vs index owned = 692 (the account's owned inventory is overwhelmingly private; `/users/{owner}/repos` under an installation token sees public only), `/user/subscriptions` = 403 and `/user` = 403 for installation tokens. The observatory core is a user-identity surface (§1.5) and stays on the user token. Only its repo-issues intake step is app-compatible; it is not split out (trivial call count, shared run, degradation risk). Wave 0 re-picked = M2 | — |
| M2 | `reviewer-metrics-collect.yml` (weekly Mon 05:17Z) — the PAT-wall driver | PAT (`GH_TOKEN` env) | ~750/run (lane-measured) | G1–G5; run once on demand before the Monday slot | same env flip |
| M3 | Delphi feed collectors' GitHub reads: `delphi-ledger-feed-collect` (Tue 06:47Z), `delphi-rfp-feed-collect`, `proposals-feed-collect`, `oracle-panel-feed-collect`, `linguist-panel-feed-collect`, `surface-feeds-collect`, `traffic-feed-collect` | user-token reads inside PAT bucket | MEASURE-AT-GATE per collector | G1–G5 per collector, one at a time; the Neon mirror/export steps are not GitHub reads and do not move | env flip per collector |
| M4 | `provider-availability.yml` — GitHub-API probe portion only | PAT bucket for GitHub probes; provider APIs stay on their own provider keys | MEASURE-AT-GATE | G1–G5 scoped to the GitHub probe steps | env flip on those steps |
| M5 | Read-only recon/observer class: `recon-intel-discovery`, `recon-intel-reconcile`, `issue-observatory`, `observer-poller-scheduled`, `shared-observer-poller`, `github-telemetry-snapshot`, `challenge-osint-watch` GitHub reads | PAT bucket / `GITHUB_TOKEN` mixed | MEASURE-AT-GATE | G1–G5 per workflow; any step that writes (PR creation in osint-watch refresh pattern) splits: reads → Collector, the write step stays until Publisher (§1.2) | env flip per workflow |

### 1.2 Wave 2 → Publisher (when built: contents+PR+issues write)

| # | Consumer | Current | Target behaviour | Gate |
|---|---|---|---|---|
| M6 | Workflow-side publishes / merges / coordination comments: `merge-promotion-queue*`, `self-integrate`, `context-relationship-publish`, osint refresh-PR writes (from M5) | PAT-class secrets / `GITHUB_TOKEN` | mint Publisher token in-workflow; comments and merges carry the app identity | Publisher graduation (§3.4) + G1–G5 |
| M7 | Lane `pat_publish` paths | chat-side PAT | **Stay PAT** until Publisher custody + minter are lane-usable from chat side (connector-pattern helper, AppID lane); then PAT remains the fallback, never removed | AppID lane declares lane-usable; per-lane opt-in, no flag day |

### 1.3 Wave 3–5 → Reviewer-ops / Gate/CI / Lifecycle (when built)

| # | Consumer | Current | Target app | Notes |
|---|---|---|---|---|
| M8 | `peer-review-orchestrator.yml` polling + review-state comments | PAT-class operator tokens | Reviewer-ops (checks read, PR write) | ≤180 calls/h/event (lane figure); polling moves, the operator-token publish leg moves only when its write class matches Reviewer-ops perms — otherwise that leg waits for Publisher |
| M9 | `repo-gate.yml` check-runs/annotations; `skill-quality-lane` and ECC-class annotation posts | `GITHUB_TOKEN` / PAT mixed | Gate/CI (checks write) | Reason is identity + audit separation (verdicts issued by the gate identity), not PAT relief |
| M10 | `issue-lifecycle-triage.yml` (Tue 07:17Z), `proposal-lifecycle`, GAP-ledger issue sweeps | `GITHUB_TOKEN` (triage today) | Lifecycle (issues write) | Same: identity/audit win + own bucket; `GITHUB_TOKEN` keeps working as rollback |

### 1.4 Migration gates (every item, no exceptions)

- **G1 Manifest ∧ install**: app created from its PR-reviewed manifest
  package (`ops/github-apps/<role>-pilot/`), installed on termux-monorepo only.
- **G2 Minter wired**: workflow mints via `scripts/github_app_token.py`
  pattern or the SHA-pinned `actions/create-github-app-token` action; the
  private-key secret name is a provisioning fact — provisioned by the owner,
  recorded names-only, never assumed (see §0, `APP_PRIVATE_KEY`).
- **G3 Shadow run**: one run on the app token with output diffed against the
  PAT-path output (same inputs); diff = ∅ or explained in the migration PR.
- **G4 Bucket proof**: during the shadow run, record `GET /rate_limit` on the
  app token (remaining > 0 while PAT low/0 is the strong form, Collector-style)
  into the registry readings (§2.4). The proof is a **runtime receipt**, not a
  lone reading (amended 2026-10-30 per the #2407 telemetry audit): mint
  outcome, rate-limit before AND after the batch, API call count by status,
  repositories inspected, workflow run id / attempt / head SHA, duration and
  terminal conclusion — emitted by the #2407 telemetry emitter
  (`scripts/github/github_app_telemetry.py`) or an equivalent receipt with
  the same fields. Manifest declarations are never G4 evidence.
- **G5 Fallback retained one cycle**: the old credential path stays wired
  (env-selected) for one full schedule cycle after cutover, then is removed by
  a follow-up PR. Rollback at any point = flip the token-source env back;
  tokens are ephemeral (~1h) and no state migrates, so rollback is instant
  and lossless.

### 1.5 NOT migratable (with reason per item)

| Item | Why not |
|---|---|
| Workflows already on `GITHUB_TOKEN` whose function fits its perms (e.g. checkout + artifact steps) | Already their own per-repo bucket (1000/h class); moving adds a custody surface for zero bucket gain. Only identity-motivated moves (M9/M10) excepted, case by case |
| Surfaces needing the user's own identity (account settings, app settings pages, installation approvals, billing, secret provisioning) | Apps act as installations, never as the user; these stay owner-session surfaces — and are never a browser credential route for API access |
| App settings / PEM generation / permission-consent pages | GitHub design: web-only residual, owner session (see §2.1 rotation route) |
| Chat-side lane steering that must attribute to the owner account (reviews requested of the owner, owner-PAT comments of record) | Attribution is the function; an app identity would falsify provenance |
| Anything whose permission class no slate app holds (e.g. actions/secrets administration, org administration) | No app holds it by least-privilege design; acquiring the class is an upgrade decision (§3.2), never a migration shortcut |
| Non-GitHub provider calls inside mixed workflows (Neon, provider APIs in M3/M4) | Not GitHub buckets at all; they keep their own credentials and quotas |

## 2. Deliverable 2 — Maintenance & update plan

### 2.1 PEM custody + rotation

- Custody pattern (of record): one connector dir per app under
  `~/workspace/custom-connectors/custom.github-app-<role>/keys/`, PEM 0600,
  dir 0700, fingerprint (DER SHA-256) recorded in that connector's
  CONNECTOR.md and in `ops/github-apps/PROCESS.json`. Names/paths only
  anywhere else. The key never travels — it signs a JWT locally; there is no
  vault-surrogate swap point (AppID lane finding, adopted).
- Actions-side custody: the workflow-facing copy lives as a repo Actions
  secret whose name is an owner provisioning item (names verified against
  the provisioned list before any workflow references them — phantom-secret
  rule).
- Rotation cadence (derived): GitHub app keys do not expire and an app may
  hold up to 25, so rotation is calendar-anchored, not expiry-forced:
  **every 6 months from the app's creation date** (Collector created
  2026-10-29 ⇒ first rotation due by 2027-04-29) **plus event-driven**
  rotation on custody change, lane handover, or any suspected exposure.
- Rotation procedure (zero-downtime): generate new key in app settings
  (owner session) → install to custody + Actions secret → mint-verify with
  the new key (fingerprint recorded) → delete the old key in settings →
  record the rotation in PROCESS.json. Never delete the old key before the
  new key has minted successfully.

### 2.2 Token-minter upkeep

- Two sanctioned minters: `scripts/github_app_token.py` (chat/CI scripts)
  and `actions/create-github-app-token` pinned by SHA in workflows.
- Quarterly upkeep item: re-check the pinned action's current release,
  the JWT lifetime claims (iat −60s / exp ≤10 min), and installation-token
  expiry handling (~1h); changes land as ordinary PRs citing this plan.

### 2.3 Permission-drift audit

- Weekly workflow (GitHub-hosted, per VM rule) `github-app-drift-audit`:
  for each installed fleet app, read installed permissions via App JWT
  (`GET /repos/{owner}/{repo}/installation` / installation read) and diff
  against the manifest of record in `ops/github-apps/<role>-pilot/manifest.json`.
- Pattern follows the cadence provider-onboarding check: diff = ∅ ⇒ silent
  success artifact; diff ≠ ∅ ⇒ opens/updates one tracking issue with the
  per-permission delta. Drift is never auto-corrected — a permission change
  is a §3.2 upgrade (PR-reviewed manifest + installation consent).

### 2.4 API deprecation / version watch + weekly bucket census

- Monthly: review the GitHub API changelog + REST API version calendar;
  breaking-change or deprecation entries touching apps/auth/permissions
  become MIGRATION-ITEMS entries with the sunset date. Workflows keep
  sending the pinned `X-GitHub-Api-Version` until a PR moves it.
- Weekly census workflow: vehicle of record = the #2407 telemetry emitter
  (`scripts/github/github_app_telemetry.py` + `ops/github-apps/registry.json`
  declaration layer), scheduled and mint-wired as TEL-01..03 in
  MIGRATION-ITEMS; for each installed app, mint + `GET /rate_limit`,
  and record the reading (limit / used / remaining / reset, timestamp) as
  registry readings for `github.api.app_<role>` via the established
  #1884-citing quota feed/PR route. **Readings only — a missing reading is
  null, never an invented balance.** The census feeds the allocation
  planner, which re-derives per-bucket smooth-flow targets
  (flow = limit ÷ window, phase-aligned to the reset epoch; per-slice
  shares per #1884) independently for every app bucket.

### 2.5 Incident playbook (per-bucket separation)

| Incident | Detection | Response | Explicit non-response |
|---|---|---|---|
| App bucket wall (403 + that app's reset header) | consumer workflow fails on app token | Defer that app's consumers to its own `x-ratelimit-reset`; cadence re-derives that bucket's flow only | Do NOT silently fall back to PAT — fallback is a declared, logged migration-state change (G5 path), because silent fallback re-creates the PAT wall this fleet exists to remove |
| PAT wall | chat-side helper 403 / remaining 0 | App-token consumers continue unaffected; PAT work defers to the PAT reset (failsafe web-merge protocol is the documented exception path, AppID lane) | Do not borrow an app bucket for owner-attributed actions (§1.5) |
| `GITHUB_TOKEN` bucket wall | Actions-native failures | Independent of both above; defer per its reset | — |
| Suspected PEM exposure | owner/lane report | Event-driven rotation (§2.1) + revoke the exposed key in app settings immediately; audit the app's recent installation-token activity | Never paste, move or "verify" the key value in chat/files |
| App suspended / deleted / installation revoked | mint fails, JWT rejected | Consumers revert via G5 rollback to the retained credential path; incident issue opened; re-registration is a new §3 graduation, not a repair | Do not re-create the app under an improvised slug — naming returns to the registry lane |
| Permission drift found | §2.3 audit issue | Treat as §3.2: either the manifest PR ratifies it or the installation consent is reverted in settings (owner session) | No in-workflow auto-fix |

## 3. Deliverable 3 — Upgrade plan

### 3.1 New app classes

- The slate is closed at 5 until every built app reaches **standing**
  (§3.4). A sixth class is proposed only with: the permission class no
  slate app holds, the consumer list that needs it, and a naming-conference
  set (appName / slug / bot / role / moniker / alias) from the registry
  lane — provisioning never precedes naming.
- Headroom is not a reason: 100 registrations/owner, 5 used by the slate;
  each new principal is a new custody + audit surface, justified by
  permission-class separation only.

### 3.2 Permission expansions

- Expansion = PR-reviewed manifest diff in `ops/github-apps/<role>-pilot/`
  + owner consent on the installation (GitHub prompts for new permissions;
  until consented, the new perms are inert — plan consumer cutovers after
  consent, never before).
- One class at a time per app; the PR states the consumer that requires it
  and the blast radius if the app token leaks (write classes re-reviewed
  against §1.5).
- Contraction (removing a perm) follows the same PR route and takes effect
  without consent friction; prefer contraction when a consumer migrates off.

### 3.3 Multi-repo installs + public distribution

- Multi-repo: install an existing app on additional fleet repos one at a
  time. Rate limits are **per installation** — each new installation is its
  own 5000/h bucket and gets its own registry record
  (`github.api.app_<role>` per-installation readings under the same
  meta-pool service, distinguished by installation id) + its own G3/G4
  adoption proof on that repo. No bulk installs.
- Public distribution: all slate apps are `public: true` from day one;
  a foreign installation spends that account's bucket, never ours, and
  appears in the app's installation census as foreign (counted, never
  named beyond the public account name GitHub itself shows).
- Marketplace publishing and user-authorization flows (callback URL,
  device-flow user tokens) are on the owner's [later] list — parked here
  by reference, not designed in this plan.

### 3.4 Graduation criteria (per app, in order)

1. **Proven** — bucket-split reading: app bucket limit/remaining observed
   while the PAT bucket is low/0 (Collector ✓ 2026-10-30T02:18Z).
2. **Recorded** — registry record + #1884 meta-pool slice + PROCESS.json
   entry + custody fingerprint on file (Collector ✓).
3. **Planned** — manifest package + this migration plan names its
   consumers and gates (Collector ✓; Publisher package in AppID lane).
4. **Standing** — first production workflow runs ON the app token (G3+G4
   passed) and custody sits in the connector pattern. **Collector is not
   yet standing**; no app is called adopted/distributed before this step.

## 4. Ownership

| Surface | Owner lane |
|---|---|
| This plan + migration execution per wave | appid-migration-plan (this lane) |
| App creation, manifest packages, custody, PROCESS record | AppID process specialist |
| Registry records, #1884 slices, census readings, flow math | Quota specialist / quota-convergence |
| Naming sets (any new app or slug variant) | Registry/monikers lane via conference |
| Secret provisioning (names of record) | Owner only |
| Cadence re-derivation per bucket | Cadence lane |

Citations: issue #1884 (quota allocations), PR #2361/#2369 (Collector
manifest package), PR #2385/#2391 (registry record + meta-pool).
