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
| RR-1 | **Repo Replay telemetry-ingest — RESCOPED 2026-10-30 (owner, via repo-replay lane): HELD until gate.** Repo Replay builds in its OWN repo (`timerloggedout-spec/repo-replay`) ∧ compares; **∅ writes to termux-monorepo until repo-replay is validated ∧ submoduled** — the monorepo is a read-only validator/compare surface until that gate. The 2026-10-28 ingest (Provenance ledger + HindSight payloads) therefore does NOT land as a monorepo PR; telemetry, where used, enters repo-replay as replay input/evidence in its own repo. Gate = replay validation proof + submodule step. The earlier Collector-verify + Publisher-landing sequencing is WITHDRAWN | — (held) | — | gate: validation proof ∧ submodule | n/a |
| RR-2 | **Repo Replay publish route PAT → AppID**: `revwright/{appid,harvest,publish}.py` + MIGRATIONS.md (repo-replay lane scaffold) publishes via Publisher once installations extend to the replay target repos (extension = AppID lane task, requested 2026-10-30) | PAT | per-publish | G1–G5 per target repo | PAT (fallback of record) |
| M3 | Delphi-class feed collectors (7) | mixed (see verdict) | — | **DISPOSITIONED 2026-10-30 (firsthand token + endpoint audit): ZERO PAT-bucket reads to migrate.** `delphi-ledger-feed-collect`, `delphi-rfp-feed-collect`, `oracle-panel-feed-collect`, `linguist-panel-feed-collect`, `surface-feeds-collect` authenticate with `GITHUB_TOKEN`/`github.token` (per-repo bucket, never the user PAT bucket). `proposals-feed-collect`: its script makes ZERO GitHub API calls (local files only); the OPERATOR||github.token env serves only the refresh-PR write → M6/Publisher class, not a read migration. `traffic-feed-collect`: OPERATOR by necessity — Collector app-token probe of traffic/views, traffic/clones, traffic/popular/referrers = 403 ×3 (traffic API requires push-class access; Collector is read-only) → NOT MIGRATABLE to Collector. The M3 premise (user-token reads inside the PAT bucket) did not survive contact with the workflows | — |
| M4 | `provider-availability.yml` | provider keys only | — | **DISPOSITIONED 2026-10-30: NOT APPLICABLE.** Firsthand audit: the workflow carries NO GitHub token env (permissions: contents: read; checkout persist-credentials: false) and `scripts/provider_availability_probe.py` contains ZERO GitHub references — every probe targets a provider API on its own key. There is no GitHub-API probe portion to migrate; the M4 premise was phantom | — |
| M5 | Read-only recon/observer class (7 workflows) | `GITHUB_TOKEN`/`github.token` (per-repo bucket) | — | **DISPOSITIONED 2026-10-30 (firsthand token audit, 7/7): NO PAT-bucket reads.** `recon-intel-discovery`, `recon-intel-reconcile`, `issue-observatory`, `observer-poller-scheduled`, `shared-observer-poller`, `github-telemetry-snapshot`, `challenge-osint-watch` all authenticate with the per-repo token (reconcile: dedicated write token || github.token). The real pressure on this class is the shared 1000/h per-repo bucket (issue-observatory records outage receipts under contention) — Collector migration remains AVAILABLE as repo-bucket relief for the pollers, reprioritized BELOW M6/M8 (which carry actual PAT/user-token load); if taken, write steps (osint-watch refresh PR) split per the original rule | — |

### 1.2 Wave 2 → Publisher (when built: contents+PR+issues write)

| # | Consumer | Current | Target behaviour | Gate |
|---|---|---|---|---|
| M6 | Workflow-side publishes / merges / coordination comments (named set) | `github.token` (per-repo Actions identity) | — | **DISPOSITIONED 2026-10-30 (firsthand audit): ZERO PAT-class writes in the named set.** `merge-promotion-queue` v1/v2/v3 + `merge-promotion-steward` (incl. its `gh pr merge`) and `context-relationship-publish` all run on `github.token`; the osint refresh-PR writes (from M5) likewise. `self-integrate` performs NO GitHub writes in-workflow — it dispatches an external agent over HTTPS (that agent's own credential surface, out of scope). Publisher adoption for these remains an identity/audit-separation choice (§3.4 graduation), NOT quota relief — reprioritized as optional, behind M7/M8 | — |
| M7 | Lane `pat_publish` paths | chat-side PAT | per-lane opt-in | **GATE SATISFIED 2026-10-30 (firsthand): Publisher custody + minter ARE lane-usable chat-side** — `custom.github-app-publisher/bin/github_app_publisher.py mint` verified from this lane (token perms {contents write, pull_requests write, checks read, metadata read}; bucket 4985/5000 at proof). Publisher also self-published PR #2417 by its own token. This plan amendment PR is itself published via the Publisher token as end-to-end path proof. Rollout = per-lane opt-in (AppID lane declares + schedules; NO flag day); PAT remains the fallback, never removed | PAT (fallback of record) |

### 1.3 Wave 3–5 → Reviewer-ops / Gate/CI / Lifecycle (when built)

| # | Consumer | Current | Target app | Notes |
|---|---|---|---|---|
| M8 | `peer-review-orchestrator.yml` polling + review-state steps | mixed (see verdict) | — | **DISPOSITIONED 2026-10-30 (firsthand step-level audit of the 875-line workflow):** the polling/evidence step (Collect controls and provider response evidence — the call-volume step) takes NO token input → runs on the workflow `GITHUB_TOKEN` (per-repo bucket, ∅ PAT). The OPERATOR-token steps are IDENTITY-BOUND BY DESIGN and STAY: Publish SHA-bound peer response state + Dispatch verified second pass resolve an *authorized state publisher* (login-checked, OPERATOR_INTERACTIVE_ACTIONS), and Request supported provider reviews requires the operator identity for provider triggers. Reviewer-token adoption for the evidence step remains available as per-repo-bucket relief (optional, M5-poller class) | — |
| M9 | `repo-gate.yml` + annotation surfaces | Actions job identity | — | **DISPOSITIONED 2026-10-30 (firsthand audit):** repo-gate verdicts ARE its own job check-runs (Actions identity) — the workflow carries no PAT and no separate annotation-posting token; it evaluates `scripts/ci/repo_gate.py` against the checkout/base ref. Skill-quality/ECC annotation posts are those reviewers' own app surfaces. Gate-app (5539499, checks write) adoption = optional identity graduation (gate reads under Gate identity), NOT quota relief | — |
| M10 | `issue-lifecycle-triage.yml`, `proposal-lifecycle`, GAP-ledger sweeps | Actions job token | — | **DISPOSITIONED 2026-10-30 (firsthand audit):** issue-lifecycle-triage runs on `github.token`; proposal-lifecycle's own receipt text states 'Authentication: Actions job token' — per-repo bucket, ∅ PAT. Lifecycle-app adoption = optional identity graduation (issues write under app identity), NOT quota relief. (Lifecycle app existence NOT ESTABLISHED from PROCESS.json, which is stale — AppID lane to refresh) | — |

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
