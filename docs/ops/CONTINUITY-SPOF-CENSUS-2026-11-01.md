# CONTINUITY SPOF CENSUS — 2026-11-01

`role:backend-mesh-resiliency` ∘ census-pin: master `3a67aaedf899` (2026-11-02T00:38Z) ∘ spot-check window 2026-11-01 16:40–17:10 PT
Scope: READ-ONLY census + remediation scoping. ∅ failover executed, ∅ telemetry file touched, ∅ deployment changed.
Notation: `↦` evidence · `∅` none found · `?` UNKNOWN (¬verifiable from repo/API) · S/M/L = remediation size · claims w/o `↦` = fleet-record, labelled.

## §0 Doctrine

**Redundancy present ≠ redundancy proven.** A second deployment, key, arm, or route counts as continuity
only after a TEST has forced traffic across it pre-need ∧ the test evidence is in the record.
Every redundancy below is graded: `present?` × `TESTED?`. Ungraded redundancy = assumed redundancy = SPOF with decoration.
Trigger incident: HindSight population = 0 since 2026-11-01 on ONE empty credit balance, while TWO deployments exist.

---

## §1 HindSight — memory store ∧ telemetry sink

Function: fleet memory (`retain/recall/reflect`, bank `deepagent::{repo}`) ∧ telemetry-population target.
Population path: `telemetry-ingest.yml → scripts/telemetry_ingest/ingest.py → retain_payloads.py → POST {HINDSIGHT_BASE_URL}/v1/default/banks/{bank_id}/memories` (items+async, `document_id` upsert) ↦ `scripts/telemetry_ingest/retain_payloads.py:1-20`, `docs/ops/TELEMETRY-INGEST.md`

### 1a. What population consumes — ONE credit pool
- Retain ⇒ server-side extraction ⇒ LLM call + embeddings call per batch. Configured providers (both deployments): LLM=`openrouter`, embeddings=`google` ↦ `deploy/fly/fly.toml [env]`, `.github/workflows/koyeb-hindsight-deploy.yml` service env, `.github/workflows/fly-hindsight-config.yml` secret-set block.
- Credit = the extraction-credit balance behind the single `OPENROUTER_API_KEY` account ∧ `GEMINI_API_KEY` account. SAME secret names feed Fly-config ∧ Koyeb-create ⇒ **one pooled balance, shared by both deployments**. Deployment redundancy ≠ credit redundancy: failover Fly→Koyeb spends the same empty pool.
- Lived proof: run `41367527296` — ingest 326 attempted + density 62 attempted, ∀ batches HTTP 402 `{"detail":"Insufficient credits"}` ↦ fleet record (MEMORY 2026-11-01, PR #3399). Still current at census: `ops/telemetry/ingest-receipt.json` (generated 2026-11-02T00:32:25Z) `live_retain{attempted 326, ok 0, failed 326, first_error 402}` ∧ `ops/telemetry/hindsight-retain-density.json` `{attempted 62, ok 0, first_error 402}`.
- Prior incident, same shape: 2026-10-31 scaffold contract (`POST /retain`, never a server route) failed 316/316 → fixed from fork source ↦ `retain_payloads.py:11-13`, PR #2874/#3399 records.

### 1b. Fly ∧ Koyeb divergence (concrete)
| axis | Fly A — `deploy-hindsight.yml` | Fly B — `deploy/fly/fly.toml` | Koyeb — `koyeb-hindsight-deploy.yml` |
|---|---|---|---|
| app | `hindsight-termux` | `hindsight-deepagent` | `hindsight-deepagent` (name collision, other platform) |
| image | `hindsight:latest-slim` (unpinned, inline Dockerfile) | `hindsight:0.5.1` (pinned) | `hindsight:0.5.1` (pinned) |
| env dialect | `HINDSIGHT_BIND_*` + `HINDSIGHT_DATA_DIR=/data` | `HINDSIGHT_API_*` | `HINDSIGHT_API_*` |
| LLM model | set by config wf: `openai/gpt-4o-mini` | `meta-llama/llama-3.1-8b-instruct:free` | `meta-llama/llama-3.1-8b-instruct:free` |
| embeddings model | config wf: `text-embedding-004` | `gemini-embedding-001` | `gemini-embedding-001` |
| region | `sjc` (input) | `sjc` | `was` |
| scaling | `auto_stop=stop`, min 0, 1024 MB | `auto_stop=false`, min 1, 256 MB | free instance, 1 service |
| persistence | volume → `/data` | volume → `/home/hindsight/.pg0` | **∅ volume; deploy step DELETES existing app → clean slate ⇒ bank destroyed on redeploy** |
| auth secret (store-verified 2026-11-01) | `FLY_IO_ORG_TOKEN` ✓ present | (same) | `KOYEB_API_TOKEN` **∅ absent from 66-name store ⇒ workflow cannot authenticate as written** |
| last deploy evidence | success 2026-09-28 run `36374852700`; config success 2026-09-28 `36378823599` | (same surface) | ∀ runs 2026-09-30 failure/cancelled, latest `36663110251` |

- Koyeb push trigger lists `deploy/koyeb/**` — that directory does not exist in tree (∅) ⇒ trigger path dead; dispatch/path-on-workflow only.
- Which deployment `HINDSIGHT_BASE_URL` targets = **?** (secret value; name last updated 2026-09-30T04:59:20Z, ≈Koyeb window — timing correlation only, ¬proof). Current live health of either deployment = **?** (∅ probe in census scope; last deploy evidence ≈5 weeks old).

### 1c. Failover
- Mechanism: **∅**. ∅ DNS/CNAME indirection (clients address `*.fly.dev` / `*.koyeb.app` directly), ∅ health-based switch, ∅ dual-write. `HINDSIGHT_BASE_URL` = one static secret ⇒ switch = manual secret edit + repoint; bank data is per-deployment local volume ⇒ **data does ¬follow**.
- Failover TEST evidence in repo history: **∅** (code search `hindsight+failover` → 3 planning docs, ∅ mechanism/drill).
- Redundancy grade: present = partial (2 platforms, divergent ∧ 1 unauthenticatable) · TESTED = **∅**.

### 1d. Ingest-path SPOFs
`telemetry-ingest.yml` = ONE workflow (weekly Wed 07:23Z + push-on-source-paths + dispatch) ∘ ONE endpoint ∘ ONE bank (`HINDSIGHT_BANK_ID`) ∘ ONE key name (`HINDSIGHT_API_KEY`) ∘ ONE retain client.
**Buffering ✓ (strongest property in this domain):** payloads persist in-repo (`ops/telemetry/hindsight-payloads.jsonl`, 326 units; `density-hindsight.jsonl`, 62) + `document_id` upsert ⇒ replay = re-run post-top-up, idempotent, ∅ data loss while the gate lasts ↦ receipt files above.

### 1e. Remediation scope (sequenced) ∧ proof tests
1. `R1.1[S]` credit decoupling — separate LLM key/balance per deployment (or 2nd provider key on one) ⇒ pool SPOF split.
2. `R1.2[S]` restore Koyeb auth — provision `KOYEB_API_TOKEN` (name-only store op) ∨ retire the workflow honestly.
3. `R1.3[M]` config convergence — ONE canonical spec (app, image pin, env dialect, model set) generating both platform configs; kill Fly A/B split.
4. `R1.4[M]` Koyeb persistence — volume/external PG; delete-recreate step removed.
5. `R1.5[S]` repoint runbook — documented `HINDSIGHT_BASE_URL` switch + bank-export snapshot to repo/Neon on schedule.
- **TEST T1 (failover):** seed canary memories on A → stop A → repoint BASE_URL→B → `recall` canary ∧ retain 1 probe batch; pass = recall hit ∧ retain `ok>0`, evidence = receipt JSON committed.
- **TEST T2 (credit):** revoke/drain A-side key in drill → population continues on B-side key; pass = retain `ok=attempted` on B pool.

---

## §2 Provenance ingest — attribution/evidence ledger

Function: provenance envelopes (`telemetry-provenance/v1`, evidence_hash) ∧ lane-event ledger. Sinks `{|separate|}` by doctrine ↦ `docs/ops/TELEMETRY-INGEST.md`.

- Landing: `ops/telemetry/provenance-ledger.jsonl` (326 records at census receipt) — **git/GitHub is the store**; generated by the SAME single workflow+script as §1d (`ingest.py` + `sources.json` manifest). Separation proven under fire: provenance emitted 326/326 in the same runs where HindSight retain scored 0/326 ↦ `ingest-receipt.json`.
- Buffering/replay ✓✓: sources = repo files, per-source SHA-256 in receipt ⇒ ledger is a deterministic regeneration, ¬ a stream capture; any cycle re-derivable from a clone (this census's clone = de-facto unmanaged replica).
- SPOFs:
  - `P2.1` single generator (`telemetry-ingest.yml`/`ingest.py`) + refresh-PR merge dependency for outputs to land on master (pattern ↦ refresh PR #2914).
  - `P2.2` density step DEFERs on Actions rate-limit (committed table stands) — degradation is silent-by-design ↦ `telemetry-ingest.yml` density step.
  - `P2.3` `rindig-provenance-audit.yml` output → Actions artifact ONLY, retention 14d, written to `/tmp` ⇒ audit evidence evaporates; ¬ a store ↦ workflow `Publish provenance evidence` step.
  - `P2.4` Neon lane-events (`ops/lane-events/`, store for lane events ≠ telemetry provenance): ONE Neon project `lane-events` (aws-us-east-2, free tier), writer `scripts/ops/lane_event.py` never-fails-caller ∧ no-ops silently without `LANE_EVENTS_DATABASE_URL`/`NEON_API_KEY` ↦ `ops/lane-events/README.md`. Idempotent `event_key` ⇒ replay-safe, but source events = workflow runs (¬ re-emittable) ⇒ missed window = permanent gap. Current row count / last successful write = **?** (recorder runs at census 2026-11-02T00:43Z conclude `skipped`).
- Redundancy grade: provenance ledger — present = git replication (unmanaged) · TESTED = ∅ (∅ restore drill). Lane-events — present = ∅ second copy · TESTED = ∅.
- Remediation: `R2.1[S]` mirror ledger+receipts to Neon (or 2nd remote) on schedule · `R2.2[S]` rindig output → committed repo path, ¬ 14d artifact · `R2.3[S]` lane-events no-op → written receipt (silence ⇒ signal).
- **TEST T:** skip one ingest cycle → re-run → ledger diff = ∅ loss; bare-clone regeneration hash-matches receipt SHA-256s. Pass = both, evidence committed.

---

## §3 PAT — fleet GitHub access

Asset: ONE classic PAT, name `MUSE_ADMIN_GH`, broad admin scopes, **no expiration** ↦ `~/workspace/custom-connectors/custom.github-pat/CONNECTOR.md` (owner screenshot 2026-10-20).

- Depends on it: ∀ Muse-lane GitHub work via `custom.github-pat` helper — the connector doc names it "the only GitHub route available" (built-in GitHub connector = DENY, owner setting); `pat_publish` pattern (code search: `pat_publish` 17 hits, `github_pat.py` 24 hits); sealed-box secret provisioning (this lane's `CLOUDFLARE_*`/`DEVICE_QUEUE_*` deploys); mesh-census scripts `scripts/github/mesh_census_legacy/*`; this census's own publication.
- Quantified: token×attribution correlation (PR #3399, `ops/telemetry/token-attribution-correlation.json`): backfill window 325 owner-login PRs vs App-history `github-actions` 244 · Publisher ×23 · Swarm ×2 · Jules ×5 ⇒ agent output overwhelmingly PAT-attributed; the attribution fix (PR #3361) exists because a PAT collapses ∀ riders to the owner identity.
- Blast radius (revoke / leak / owner-account lock — no-expiry ⇒ these are the loss modes): ∀ lane publish/merge/comment/provisioning halts. ¬ affected: in-Actions `GITHUB_TOKEN` workflows, App-token workflows (below), owner's own web access (¬ agent-usable — fleet rule prohibits agent browser GitHub sign-in).
- Mitigation — GitHub App specialists (8; custody `~/workspace/custom-connectors/custom.github-app-*`, names-only):
  `Collector 5535733` (collection) · `Gate 5539499` (checks write) · `Lifecycle 5539639` (issues write) · `Publisher 5537873` (contents+PR write; **∅ issues permission ⇒ comment flows still PAT**) · `Reviewer 5539430` (reviews) · `Swarm 5560920` (contents/PR/issues/actions/checks — broadest) · `CrossReference 5564430` (contents read + issues write, apk-xref belts) · `RepoStory 5565297` (repo-story ONLY, ¬ this repo).
  - Migrated ∧ live: Swarm-actor workflows mint via `create-github-app-token` (`cert-unit`, `commit-replay-index`, `graph-matrix-census`; code search `TERMUX_FLEET_SWARM` 13 hits, `create-github-app-token` 28 hits incl. `docs/ops/GITHUB-APP-MIGRATION-PLAN.md`); `github-app-telemetry.yml` scheduled runs success, latest `41359189737` 2026-11-01T22:51Z.
  - Custody gap: Actions-store minting copies = **4/8** — termux-monorepo store (66 names, 2026-11-01) holds 3 `TERMUX_FLEET_*_PRIVATE_KEY` secrets (`COLLECTOR` 2026-10-30 · `SWARM` 2026-10-31 · `CROSSREFERENCE` 2026-11-01) ∧ RepoStory's copy `TERMUX_FLEET_REPOSTORY_PRIVATE_KEY` lives on timerloggedout-spec/repo-story (2026-11-01) ⇒ backed {Collector, Swarm, CrossReference, RepoStory}; VM-only = **4/8** {Publisher, Reviewer, Gate, Lifecycle} = local 0600 files on THIS VM only (∀ 8 hold custody `.pem` on the VM) ⇒ §4 coupling.
  - **ERRATA 2026-11-01:** VM-only count corrected 5→4 (RepoStory backed via `TERMUX_FLEET_REPOSTORY_PRIVATE_KEY` on repo-story, set 2026-11-01T10:29:15Z; original count used a termux-monorepo-only secrets scope ∧ missed it — correct by design, that App is scoped to repo-story only).
  - Other GitHub tokens in store (`OPERATOR_GITHUB_TOKEN`, `ARCHWIZ_GITHUB_TOKEN`, `RECON_INTEL_GITHUB_WRITE_TOKEN`, names only) = ¬ registered Muse routes ⇒ ¬ tested fallback.
- Redundancy grade: present = partial (Apps cover narrow classes) · TESTED = partial (App telemetry/swarm pilots live; **PAT-outage drill = ∅**).
- Remediation: `R3.1[S]` Publisher issues-write amendment (UP-01 template per its connector doc) · `R3.2[S]` Actions-store minting copies for Gate/Lifecycle/Reviewer/Collector · `R3.3[M]` PAT rotation runbook + 2nd registered route · `R3.4[M]` migrate top-3 PAT publish lanes → Publisher/Swarm actors.
- **TEST T (quarantine drill):** one lane, 24h, helper disabled → publish + merge + comment via App actors only; pass = 0 PAT calls ∧ all 3 ops land, evidence = App-bot attribution in correlation file.

---

## §4 Browser profile lineage — signed-in web sessions

Anchor: fleet's signed-in console sessions live in the Muse browser profile on **ONE VM** (this host).
Anchored surfaces (fleet record): Cloudflare dashboard (token route now primary — proven 2026-10-22), Neon console, AI Studio/Gemini, HuggingFace, provider consoles used by provisioning flows. GitHub web = owner-driven only (agent sign-in prohibited, fleet rule).

- Persistence: VM home dir survives restart/replacement (platform property) ⇒ profile persists iff it lives under home; **portability = ?** — ∅ export/sync/backup mechanism found (code search `browser+profile+backup` → ∅ mechanism; hits are portability counts below).
- Repo-side partial replica: repo intentionally tracks captured browser-profile material — `docs/PORTABILITY.md`: browser profile files 607→567 tracked, browser credential stores 115→109 (intentional environment replication, owner rule). Currency = snapshot-class, restorability = **UNTESTED** (∅ restore drill on record).
- Lived incidents: Neon key saga 2026-10-28 — a key value existed ONLY in the VM browser clipboard; vault capture page blocked inside the agent browser; value lost, key revoked/recreated ×3 (fleet record, memory 2026-10-28). Cloudflare 2026-10-22 — usable session existed only on the 2nd device; hours burned; resolved via API-token route instead.
- Recovery path if profile lost/corrupt: per-service owner re-login (several flows prompt-gated to the B160V origin phone — broken screen), ∨ token routes where provisioned (Cloudflare ✓, GitHub = PAT ¬ browser). ∅ single recovery runbook.
- Redundancy grade: present = stale repo snapshot + token routes (partial) · TESTED = ∅.
- Remediation: `R4.1[S]` session-dependency inventory (browser-required vs token-route per surface) · `R4.2[M]` token-route conversion for console-only flows · `R4.3[M]` scratch-profile restore drill, vault-handled materials only.
- **TEST T:** blank profile → restore ONE non-critical console session using only the documented recovery steps, timed; pass = session usable ∧ ∅ unplanned owner-phone prompts.

---

## §5 Builder arms — spot-check 2026-11-01 (baseline = fleet record, tasking 2026-11-01)

Baseline (fleet record): Jules DOWN (entry builds created 3 / completed 0 / errored 3) · Gemini CLI OUT (smoke failed 14:12Z) · DeepSeek tunnel DOWN (runs `41301295882` + `41321691938` tunnel-unresolved, agent never invoked) ⇒ command-dispatch ALONE.

| arm | NOW (spot-check firsthand) | verdict |
|---|---|---|
| Jules | API alive. Latest session 2026-11-02T00:14Z `AWAITING_USER_FEEDBACK`; completion 2026-11-01T23:26Z; **but** webWrapper entry-build class FAILED ×3 on 2026-11-01 (14:12/14:32/14:56Z) + ×2 earlier (03:56/04:11Z). Lifetime census 374 {COMPLETED 345, FAILED 19, AWAITING 7, PAUSED 3} ↦ `custom.jules jules.py census/list-sessions` live | **DEGRADED** — general sessions complete; build-dispatch class ¬ restored/proven |
| Gemini CLI | Latest `gemini-interactions-smoke` run `41315002638` = failure 2026-11-01T14:12:07Z; 5/5 recent = failure; `gemini-dispatch` runs 2026-11-02T00:42Z = skipped (comment triggers, ∅ invocation) ↦ Actions runs API | **OUT** — ∅ restoration evidence |
| DeepSeek agent | Workflow converts tunnel-unresolved → `exit 0` "success" (vacuous green) ↦ `deepseek-termux-agent.yml:134-142`; latest runs 2026-11-02T00:40Z job = `skipped`; ∅ invocation evidence; `DEEPSEEK_AGENT_URL` = one static secret (2026-10-05) aimed at a rotating tunnel endpoint ⇒ structural staleness | **DOWN** — ¬ restored |
| command-dispatch | `provider-invoke.yml` success 2026-11-01T16:19Z (`41325724792`); `provider-batch.yml` success 21:53Z (`41354262886`); carried the 2026-11-01 inference batch (24 fired; cohere/sealion proven — fleet record) | **ALIVE** — sole arm with same-day production proof |

- Concentration: effective redundancy = **1 of 4 arms**. Cross-SPOF: `GEMINI_API_KEY` (one name) feeds Gemini smoke ∧ HindSight embeddings on BOTH deployments (§1) — one key loss hits two domains. Arm-health gating in dispatch (route-around-dead-arm automation) = **?** ¬ evidenced in repo.
- Remediation: `R5.1[S]` arm-health probe receipts (per-arm, scheduled, committed) so DOWN is a record ¬ a discovery · `R5.2[S]` DeepSeek: resolve agent URL from the published bridge manifest (device-queue install pattern) instead of a static secret · `R5.3[M]` dispatch auto-failover between arms on probe-red.
- **TEST T:** monthly arm drill — one trivial real task per arm, rotated; pass = completion evidence (PR/session/invoke receipt) per arm; failures stay on the record until a pass replaces them.

---

## §6 Summary — worst SPOF × redundancy × test state

| domain | worst SPOF | redundancy present? | TESTED? |
|---|---|---|---|
| HindSight | ONE OpenRouter credit pool behind both deployments (§1a) | partial — 2 platforms, divergent, Koyeb unauthenticatable, ∅ failover mechanism | **∅** |
| Provenance | ONE generator workflow + GitHub-as-store (§2) | partial — deterministic regeneration + unmanaged clones | **∅** |
| PAT | ONE no-expiry admin PAT = ∀ Muse-lane GitHub access (§3) | partial — 8 App specialists, narrow classes, custody split (4/8 backed, 4/8 VM-only; errata §3) | partial (pilots live; outage drill ∅) |
| Browser profile | ONE VM profile anchors ∀ console sessions (§4) | partial — stale repo snapshot + token routes | **∅** |
| Builder arms | 3/4 arms down/degraded/out; command-dispatch alone (§5) | ∅ at census time (1 effective arm) | n/a — lived failure, ¬ drill |

**∅ domain in this census has a completed failover test on record.** That — ¬ any single row — is the finding.

## §7 UNKNOWN register (¬ filled, ¬ guessed)
1. Which deployment `HINDSIGHT_BASE_URL` targets. 2. Live health of Fly/Koyeb deployments at census.
3. Neon lane-events current row count / last successful write. 4. Browser-profile portability + restore procedure.
5. Arm-health gating in dispatch routing. 6. Whether Fly A (`hindsight-termux`) or Fly B (`hindsight-deepagent`) is the live Fly app.
