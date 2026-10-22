# Server Backend & Mesh Resiliency — Map, SPOF Register, and Staged Stack Proposal

**Staged:** 2026-10-21 ~21:45–22:10 PDT (fleet backend/mesh-resiliency specialist pass 1);
**published** to `docs/ops/` on 2026-10-22 — the canonical copy lives here.
**Mode:** READ-ONLY. Nothing in this pass changed the device, the repo, or any service.
Publishing this file is a doc landing only (the poller/commit quota rule is about
poller output, not authored docs): not a device change, and not an instruction
to any other chat.
**Fleet rules obeyed:** GitHub reads only via
`~/workspace/custom-connectors/custom.github-pat/bin/github_pat.py`; credential
**names only**; counts from live API at report time; no cleanup in this proposal
deletes telemetry/training data; all device proposals are lean/sparse and
adaptive-threshold, respecting the origin's disk/IO limits.

## Evidence base (all firsthand this pass unless marked)

| Source | Vintage | What was read |
|---|---|---|
| Live master via PAT helper, head `6f4f802e` | 2026-10-22T04:45Z | Full git tree (9,267 entries, not truncated); the workflow/script/doc files quoted below, fetched at `master` unless a ref is named |
| `~/workspace/github-integration-census/INTEGRATION-MESH-MATRIX.md` (PR #1490 staged copy) + `census*.json`, `secrets_plus.json`, `reviews_updated.json` | 2026-10-21; poll snapshots rotated 2026-10-22T04:48Z (the 6h census poll is alive) | Mesh census, secret-name stores, hook health, deployment mix |
| Live Actions run lists via PAT helper | 2026-10-22 ~04:50Z | tunnel-canary, tailscale-bridge-probe, deepagent-task, deepcli-agent-bridge, termux-bridge-connect, termux-remote-exec run counts/conclusions |
| `~/MEMORY.md` + `memory/2026-10-21.md` (fleet shared memory) | 2026-10-21 | Runable failures, Hark 08:08 PDT device report, canary timing, quota standings |
| `ops/quota/registry.json` on master | fetched this pass | 28 service records; backend-relevant limits in §1.4 |

Count note (fleet counting rule): the mesh matrix says **192 workflows** (census,
2026-10-21); the live master tree this pass contains **167 files** under
`.github/workflows/`. Both numbers are kept, labeled by source — the difference
is a live-moving surface (adds/removals between census and now, plus any
non-`.yml` entries), not a figure to average.

---

## 0. Time-critical — tonight's Runable reruns (already flagged to main chat separately)

Reruns: **~00:25 PDT** `GitHub Termux-monorepo engineering / Commit & Push all Work`
and **~01:05 PDT** DeepAgent.py trigger, both on the origin (BLU B160V,
`tmx-node-primary`), both failed 2026-10-21 at those times with error bodies that
exist **only inside the Runable app** (notifications truncated; unreachable from chat).

Verified state at 21:45 PDT — the device path has **not** recovered:

1. `ops/termux-bridge/current.json` on master is still the seeded placeholder:
   `status: "unknown"`, `ssh_user: null`, `observed_at: null`,
   `stale_reason: "Seeded from user-supplied device output; this session has no
   live Termux execution channel."` Last real publish: **2026-10-17**
   (per `docs/ops/DEVICE-ACCESS-DIRECTORY.md`, observed 2026-10-21).
2. Origin storage was **93% full** at 08:08 PDT (Hark); no later reading exists.
3. The Tailscale fallback is not armed (§2, SPOF-6): probe runs all failing,
   `ops/termux-bridge/tailscale.json` **does not exist** on master (404).
4. **Do not read green as recovery tonight.** `deepcli-agent-bridge.yml` (every
   30 min) exits 0 with a skip notice while the manifest is not active — its
   latest run (2026-10-22T01:24Z, "success") is a skip. `deepagent-task.yml`
   has **0 runs ever** and also warnings-out to exit 0 when unreachable.
   The only honest recovery signals: `current.json` flips to `active` with a
   fresh `observed_at`, or the Runable tasks themselves succeed in-app.

Owner-only item before 00:25 PDT: open Runable for last night's full error
bodies; if a device session exists (ADB via the secondary, or Hark), run the
publisher recovery in §3.4 step R2.

---

## 1. Resiliency map — what the mesh actually is today

### 1.1 Device layer (origin + secondary)

| Node | Role | State (evidence) |
|---|---|---|
| `tmx-node-primary` — origin, BLU B160V #1, **damaged screen**, ADB-only typing paths | Bridge / executor: runs DeepAgent, the repo checkout, all on-device jobs, both Runable tasks | Checkout **is `$HOME`** (not `~/termux-monorepo`), on branch `feat/dashboard-lanes-v2` with local changes; `~/scripts/` holds only `ci/`, `commit-msg.sh`, `entropy_scan.py`, `model_router.py` — **`scripts/termux/` is absent on the device** (DEVICE-ACCESS-DIRECTORY, 2026-10-21). Storage 93% full (Hark, 2026-10-21 08:08 PDT). Mitigation already real: ~70 `backup/tmx-node-primary-20261021/*` branches were pushed 2026-10-21 — the origin's work has an off-device copy |
| `tmx-node-55619bd5` — secondary, BLU View 5 B160V | Observer → Observer\|Controller\|Executor (proposal-evaluation provisioning) | Provisioning doc + scripts exist on master (`SECONDARY-NODE-PROVISIONING.md`, `scripts/termux/devices/provision-secondary.sh`); **not yet live**: branch `device-heartbeat` does not exist (404 this pass), so job 43110 has never published from either node |

On-device jobs (Termux JobScheduler, 15-min Android minimum period):

| Job | Script | State |
|---|---|---|
| 43107 | `termux-resource-sentinel.sh` → `termux-resource-snapshot.sh` | Hark at 08:08 PDT: "keeper and sentinel jobs scheduled" — but DEVICE-ACCESS-DIRECTORY says 43107–43109 are "unverified: likely lost". **Contested — no firsthand `--pending` output exists in any chat-reachable evidence** |
| 43108 | keeper (tunnel keeper/watchdog family) | Same contested state as 43107 |
| 43109 | `publish-pinggy-endpoint.sh` (Pinggy publisher) | **Missing** (Hark 08:08 PDT, confirmed). Root cause pinned in §2 SPOF-2 |
| 43110 | `publish-device-heartbeat.sh` → branch `device-heartbeat` | Never published (branch 404) |
| 43111 | `origin-status-notify.sh` (secondary only) | Not installed until secondary is provisioned |

Doc drift worth recording: `TERMUX-LIVE-BRIDGE.md` calls 43109 a "five-minute
refresh"; the installer default is `PERIOD_MS=900000` (15 min, the Android
minimum). The manifest TTL is 60 min — so even a healthy publisher can sit
3–4 missed cycles from stale before the canary's `age > ttl*2` test trips.

### 1.2 Transport layer — four named paths, one half-alive

| Path | Mechanism | State |
|---|---|---|
| **Pinggy free TCP** (primary) | Device reverse-SSH to `127.0.0.1:8022`; endpoint scraped from the reverse-SSH log; publisher commits it to `ops/termux-bridge/current.json` | Tunnel itself reported up (Termux:API "Pinggy connected"; Hark pushed a fresh tunnel address 07:59 PDT 2026-10-21). **Manifest path dead** since Oct 17 (publisher, §2). Free tier: ephemeral, rotating, unauthenticated — endpoint is public metadata, auth is the device sshd key |
| **Tailscale — GitHub-identity tailnet** (`timerloggedout-spec.github`) | Tailscale Android app on origin | Origin **connected** (DEVICE-ACCESS-DIRECTORY). **No Actions runner joins this tailnet** — nothing automated can use it |
| **Tailscale — Google tailnet** (`tailf2ee94.ts.net`) | App on origin (account switch, taps only); Actions runner joins ephemerally as `tag:ci` via OIDC workload identity (`tailscale-bridge-probe.yml`, every 30 min) | Origin node **offline since 2026-08-14** on this tailnet. All recent probe runs **failure** (latest 2026-10-22T00:57Z); probe fails red by design when not `active`. `tailscale.json` never published (404). Grok's 2026-10-21 12:02 PDT "Tailscale probe fail" matches this workflow |
| **Cloudflare tunnel** | `cloudflared` on device (logs exist on device, Sep 25–27) | **Blocked**: cfapi.net consent (DEVICE-ACCESS-DIRECTORY). Named as Pinggy's parallel redundancy in `docs/ops/sessions/RESILIENCE.md` — on paper only |
| ADB via BugJaeger (secondary → origin, wireless debugging) | Operator-driven mirroring | Working; **typing** path — last-resort, human-in-the-loop |

### 1.3 Actions → device dispatch — three lanes, three different rendezvous, none proven end-to-end

| Workflow | Rendezvous | Credential names | Failure semantics | Runs (live) |
|---|---|---|---|---|
| `deepagent-task.yml` | **Static secrets** `MANUS_SSH_HOST/PORT/KEY` pointing at "the Termux reverse-tunnel endpoint (Pinggy)" | `MANUS_SSH_*` — **present** in the 31 repo Actions secrets | Unreachable/missing secrets → `::warning::` + `reachable=false`, **exit 0** | **0 runs, ever** |
| `deepcli-agent-bridge.yml` | **Dynamic manifest** `ops/termux-bridge/current.json` | `TERMUX_MCP_SSH_PRIVATE_KEY`, `TERMUX_MCP_KNOWN_HOSTS` — **absent** from the 31 repo Actions secrets (names checked this pass) | Manifest not `active` → write skip file, **exit 0**, every 30 min on schedule | 135 runs; recent "successes" are skips |
| `termux-bridge-connect.yml` | Dynamic manifest | Same `TERMUX_MCP_*` pair (absent) | Hard-fails on missing secret / non-active manifest | **0 runs** |
| `termux-remote-exec.yml` (Hark lane) | **Manual inputs** (endpoint/port/user typed into dispatch) | `TERMUX_MCP_*` pair (absent) | Hard-fails | 1 run, 2026-10-21T14:39Z, **failure** |

So: the one lane whose credentials exist dispatches to a *static* host:port for
an *ephemeral* Pinggy endpoint; the lanes that read the live manifest need a
credential pair that is not in the repo secret store; and the fixed health
check has never run. The publisher→manifest→dispatch chain has **no verified
end-to-end success on record**.

### 1.4 Hosted backends the fleet leans on

| Backend | Role | Quota / state (registry + census) |
|---|---|---|
| GitHub Actions | Execution substrate for everything repo-side; also the rendezvous host (manifests live in the repo) | 167 workflow files on master tree this pass (census: 192). Actions minutes free for public repos; `GITHUB_TOKEN` 1,000 req/hr/repo vs user token 5,000/hr. Default workflow permissions = **write**, workflows **can approve PR reviews**. All 31 Actions secrets + 7 Codespaces secrets are **repo-scoped**; org stores and all 14 environment stores are **empty** |
| Vercel | App deploys (primary) | **100 deployments/day rolling 24h**; daily cap tripped 2026-10-20; API count undercounts enforcement by ≥13. Mitigation live: `vercel-batch-deploy.yml` hourly, adaptive budget with learned offset, 6h cooldown. 76/300 sampled deployments |
| Render | Previews / services; Jules-side MCP connected | 500 pipeline min/mo, 750 instance hrs/mo, 5 GB bandwidth/mo (Hobby); exhaustion suspends free services for the month |
| Mintlify | Docs previews | 186/300 sampled deployments — biggest deployment producer, feeds the same deploy-quota pressure |
| GitHub Pages | Site/docs fallback deploy | 38/300 deployments; legacy build from `gh-pages` |
| Fly.io (+ Koyeb alt workflow) | HindSight hosting (`deploy-hindsight.yml`, manual dispatch only; `koyeb-hindsight-deploy.yml` exists) | Manual-dispatch deploys = no automatic recovery on crash; RESILIENCE.md lists fly-diag/fly-hindsight-config as the response lane |
| Neon | Postgres lane; Jules MCP **connected** (verified 2026-10-20 23:35 PDT; fleet memory flags a same-day discrepancy — treat as contested until a Jules-UI re-verification) | Free: 100 CU-h/project/mo, 1 GB storage/project (20 GB total), 5 GB egress/mo. Registry note: batch ledger writes hourly (~15 CU-h/mo) vs per-event (~180 CU-h/mo) |
| Supabase | Second DB lane | **Supabase → Jules still open** (only remaining path is Supabase's own email/password sign-in; the GitHub-sign-in route is closed by the fleet credential rule). Muse-side custom connectors for Neon + Supabase: vault capture links issued 2026-10-20, key entry + helper build still pending. Registry `supabase.free` record has **no live reading** |
| GitLab mirror | Repo redundancy lane | **Degraded**: mirror webhook last response **400** (project 85129320); 3 GitLab token names exist to support it. Mesh matrix item I2 |
| ZenHub | PM board (duplicates Linear) | Webhook **422 misconfigured**, 12 event types firing into noise. Mesh matrix item I3 |
| Linear | PM spine (webhook all events, last 200 OK; API key; Jules MCP; Muse connector) | The one fully healthy cross-surface spine |
| Codespaces | Off-device compute lane (mesh matrix C2) | 3 codespaces exist; 7 Codespaces secrets (HindSight ×5, OpenRouter, vault age key) |

### 1.5 Monitoring / watchers — who watches what, today

| Watcher | Watches | Cadence | Honesty |
|---|---|---|---|
| `tunnel-canary.yml` | `current.json` freshness + TCP to the Pinggy endpoint | Hourly (:17) | **Split vintage**: the version at the scheduled runs' head (`f8fe2c3c`) fails red on problems — recent runs all failure, correctly. The version now on master reclassifies stale/inactive/unreachable as `lag_operational` **notice, exit 0** "to avoid notification spam". Once the new version's runs begin, the hourly red signal disappears by design |
| `tailscale-bridge-probe.yml` | Origin reachability on the Google tailnet | Every 30 min (:17/:47) | Honest red (fails when not `active`) — but it has been red/continuous for a path dead since Aug 14, i.e. alarm fatigue by standing condition |
| `deepcli-agent-bridge.yml` | Manifest + DeepAgent dispatch smoke | Every 30 min | **False-green**: skip = success (§1.3) |
| Census poll (`github-integration-matrix-poll`, goal-owned cron) | Integration mesh drift (apps, hooks, secret names, deployments) | 6h | Healthy: snapshots rotated 2026-10-22T04:48Z; output never committed — correct per quota rule |
| Origin sentinel (43107) | Memory <150 MiB avail, swap <128 MiB free, storage ≥95% or <1 GB avail → "Termux resource pressure" notification | 15 min (if installed) | Threshold gap: **93% full does not trip the storage rule** unless free space is also <1 GB. Silent-when-OK design means "no alert" cannot distinguish healthy / job-missing / Termux:API absent (sentinel exits 0 silently if `termux-notification` is missing) |
| Hark (device-side agent surface) | Tunnel canary pushes, resource pressure, tunnel address pushes | Push | Caught everything real on 2026-10-21 (02:15 canary flag, 07:59 new address, 08:08 keeper/sentinel/storage report) — currently the **de facto primary watcher**, and a single one. Mobile Harness "Software caused connection abort" 09:51 PDT shows the watcher path itself drops |
| Secondary origin-status (43111) | Origin heartbeat + manifest + TCP probe → on-device notification card | 15 min | Not installed yet (secondary unprovisioned; heartbeat branch absent) |

---

## 2. SPOF / failure-mode register

Severity = blast radius on the fleet's stated priorities (DeepAgent is
mandatory-high-priority; the 00:25 commit/push task is the origin's work leaving
the device). "Evidence" is firsthand or the named in-repo/memory source.

| # | SPOF / failure mode | Evidence | Blast radius | Detection today | Gap |
|---|---|---|---|---|---|
| SPOF-1 | **Single origin device** for all device-side execution: DeepAgent runs, both Runable tasks, the repo's only full checkout-with-local-work, the tunnel endpoint | DEVICE-ACCESS-DIRECTORY; memory 2026-10-21 | Everything device-side stops; local unpushed work strands | Hark pushes; canary | Damaged screen makes every recovery a typing/ADB path; no second executor exists yet |
| SPOF-2 | **Publisher cannot run as installed**: job 43109 missing, and `scripts/termux/` absent from the device checkout (checkout is `$HOME` on `feat/dashboard-lanes-v2`; publisher lives on master) | Hark 08:08 PDT; DEVICE-ACCESS-DIRECTORY layout note; manifest unchanged since Oct 17 | Manifest never refreshes → every manifest consumer (§1.3) is dead or skipping, even when the tunnel itself is up | Canary flagged it Oct 21 02:15 | The fix is documented in-repo but needs a device session no chat has; installer also assumes `~/termux-monorepo` while the real checkout is `$HOME` (`TERMUX_MONOREPO_ROOT` override exists but the documented runbook path doesn't use it) |
| SPOF-3 | **Placeholder manifest as sole rendezvous**, with three divergent consumer semantics (hard-fail / skip-green / warn-green) | `current.json` content this pass; §1.3 table | Silent divergence: operators see green while dispatch is dead | None — divergence is the failure | No single "bridge state" truth surface; each consumer invents its own |
| SPOF-4 | **Credential-family split for one sshd**: `MANUS_SSH_*` present, `TERMUX_MCP_*` absent — the manifest lanes can't authenticate even if the manifest heals | `secrets_plus.json` names vs workflow env names, checked this pass | termux-bridge-connect / remote-exec / bridge dispatch steps fail at secret check | Only when someone runs them (0 and 1 runs) | Names-only fix path exists (owner adds the pair via vault/UI); no chat can mint device keys |
| SPOF-5 | **Pinggy free as primary transport**: ephemeral rotating endpoint, unauthenticated, discovered by scraping one log file with an anchored regex (`/^tcp:\/\//`) | `publish-pinggy-endpoint.sh`; diagnose script explicitly warns the endpoint may be embedded mid-line and the awk filter then finds nothing | Endpoint rotation + one log-format change = total device unreachability, indistinguishable from device death | Canary TCP check | No second live transport (SPOF-6/7); publisher's own log dependency is a single file under `~/.local/state/termux-mcp/` |
| SPOF-6 | **Two-tailnet Tailscale confusion**: origin is *connected* on the GitHub-identity tailnet, *offline since 2026-08-14* on the Google tailnet — and the automated probe only joins the Google one | DEVICE-ACCESS-DIRECTORY; probe runs all failure; `tailscale.json` 404 | The "fallback" has never once been observed working from Actions; failover runbooks that say "Tailscale preferred" (canary header) describe a path that isn't armed | Probe (red, fatiguing) | Someone must switch the app's active tailnet on-device (taps), or the probe must join the tailnet the origin actually sits on |
| SPOF-7 | **Cloudflare redundancy is fictional today**: named "parallel to Pinggy" in RESILIENCE.md and step 3 of BRIDGE-REDUNDANCY, but blocked on cfapi.net consent and needs typing to install | DEVICE-ACCESS-DIRECTORY | Plans that count 3 transports really have 1 (Pinggy) + 1 manual (ADB) | None | Either unblock deliberately or strike it from redundancy counts |
| SPOF-8 | **Runable as sole scheduler for the two most important nightly jobs**: closed app, config and error bodies live only in-app, no repo/Actions visibility, no evidence of retry/queue persistence | Memory 2026-10-21 L141/L202 | A second straight missed night for DeepAgent triggering is invisible until morning notifications; root cause unknowable from anywhere else | Notification (truncated) next morning | No mirror of task definitions or last-run receipts anywhere the fleet can read |
| SPOF-9 | **Origin storage exhaustion**: 93% full; heavy-op precheck denies below 500 MB free (RESILIENCE.md); DeepAgent CAB already established that a full `git worktree add` materializes a $HOME-sized tree on this repo | Hark 08:08 PDT; MEMORY.md DeepAgent constraints | 00:25 "commit & push ALL work" is the op most likely to wedge at 93%; failed git ops mid-state on a checkout with local changes compounds SPOF-1 | Sentinel (but see threshold gap, §1.5) | Any cleanup is fenced by the retention red line: telemetry/training data is **never** the relief valve; relief = caches, worktrees, build artifacts only, after the backup branches (already pushed) are verified |
| SPOF-10 | **Monitoring inversion**: the highest-cadence bridge check false-greens (bridge smoke, 30 min), the honest hourly canary is being downgraded to notice-only on master, and the honest 30-min probe alarms forever on a known-dead path | §1.5 | Real outages drown between green-skips and permanent red; "responded ≠ resolved" failure mode the fleet already got burned by | — | No three-state (up / degraded-known / down-new) reporting anywhere |
| SPOF-11 | **GitHub as sole control plane + rendezvous**: manifests, dispatch, secrets (100% repo-scoped; org/env stores empty), mesh polling — all ride one account, one PAT family, one repo | Census §5A/§6; secrets_plus | GitHub outage or account-level restriction halts dispatch, monitoring, and steering simultaneously; GitLab mirror (the designated repo redundancy) is broken (400) so there is no second copy path in working order | Census poll (which itself rides GitHub) | Mirror repair is mesh item I2, still open |
| SPOF-12 | **Quota coupling between healing and harming**: every manifest publish is a commit to master; commits are the deploy trigger the quota system rations (Vercel 100/day, API undercounts ≥13; Render monthly buckets) | Publisher script (PUT contents on master); quota registry; MEMORY.md poller rule | A chatty publisher (endpoint flapping) burns deploy quota; conversely the tailscale probe already spends commits on master (mitigated by "unchanged → no commit" + `[skip render]` in its message; the Pinggy publisher's message carries **no** skip marker, and the heartbeat design uses a side branch + `[skip ci]` — the publisher predates both mitigations) | vercel-batch-deploy ledger | Publisher commit cadence/message predates the quota discipline the rest of the mesh adopted |
| SPOF-13 | **Secondary node is a plan, not a node**: provisioning requires `gh auth login --web` **in Termux on the device** (typing + browser flow on the new phone), contradicting the fleet's no-typing preference and the fleet credential rule's spirit for GitHub sign-in (the rule binds chats' browser use; the device flow is the owner's own login — legal, but it is the provisioning bottleneck) | SECONDARY-NODE-PROVISIONING.md runbook A; heartbeat branch 404 | Observer/controller redundancy, the no-typing recovery order in DEVICE-ACCESS-DIRECTORY step 3, and heartbeat-based origin watching all wait on this one manual session | None | No pre-staged, paste-free provisioning path yet |
| SPOF-14 | **DeepAgent trigger chain has two inconsistent rendezvous designs**: Runable (on-device, opaque) OR `deepagent-task.yml` (static-secret SSH to a rotating endpoint) OR bridge smoke (manifest, missing keys) — three triggers, zero verified end-to-end | §1.3; deepagent-task header comment admits the secrets precondition | The user's mandatory-high-priority project depends on the most fragile chain in the mesh | None end-to-end | No task queue that survives tunnel death (see proposal P1) |
| SPOF-15 | **HindSight single-instance, manual-deploy**: Fly app deployed only by manual dispatch; telemetry is retention-red-line data | `deploy-hindsight.yml`; MEMORY.md standing policies | A Fly crash/outage silently degrades the attribution layer (Provenance/HindSight) the whole weighting system (3L0/Moneyball) reads | fly-diag workflows (manual) | No scheduled status check; Koyeb alt exists as a workflow, not as a failover |

---

## 3. Resiliency-stack proposal (nothing here is executed by this document; P1 Phase 1 has since landed — PR #1507)

Design constraints honored throughout: lean origin (sparse/no-checkout,
adaptive measured thresholds, no hardcoded ceilings — per the DeepAgent CAB
direction); retention red line (no telemetry/training-data deletion, ever, as a
recovery step); quota discipline (poller output never committed; commits are a
scarce bucket); names-only credentials; provider-neutral early layer with
per-provider parallel quota threads (standing owner direction); never
clear/disable a participant to solve volume — thread cadence instead.

### P1 — Invert device tasking: pull queue first, tunnel second (the structural fix)

Today every dispatch **pushes** into the device through a fragile tunnel.
Invert the default:

- **Task queue as repo state**: a queue file (e.g. `ops/device-queue/` on a
  dedicated `device-queue` branch, following the heartbeat design's precedent:
  side branch, `[skip ci]` commits, never master) written by Actions workflows
  and by chats via the PAT helper. Entries: task id, payload path, role,
  expiry, receipt slot.
- **Device poller**: one JobScheduler job (reuse the 43110 heartbeat slot's
  pattern, 15-min period) that `git fetch`es the queue branch — the device
  already has `gh`/git auth when healthy — claims a task by committing a claim
  receipt, runs it locally (`scripts/termux/run-deepagent-task.sh` already
  emits a receipt JSON), and pushes results + receipt to the same branch.
  Works behind any NAT, on any network, **with the tunnel fully dead**.
- **Tunnel demoted** to what it's good at: interactive/operator SSH and the
  Hark remote-exec lane — no longer on the critical path for scheduled work.
- **Runable demoted** to a redundant local trigger for the same queue-drain
  script (so a Runable failure no longer loses the night: the poller drains
  the queue anyway; a Runable success is a bonus run, deduped by task id +
  receipt). Runable task definitions and last receipts get mirrored into the
  queue branch by the poller, ending SPOF-8's opacity.

### P2 — What runs where (target state)

| Layer | Runs | Where | Cadence |
|---|---|---|---|
| Queue drain + receipts | Device poller job (new id, e.g. 43112 origin / shared script) | Origin; later secondary as hot spare claimant (first-claim wins, receipts dedupe) | 15 min |
| Heartbeat | 43110 publisher (already scripted) | **Both** nodes → `device-heartbeat` branch | 15 min |
| Resource sentinel | 43107, thresholds made **adaptive**: pressure = free < max(500 MB, 2× largest expected op footprint) or used% ≥ 95, whichever trips first; adds a *pre-pressure* notice at 90% so 93% is never silent again | Origin (secondary watches its own) | 15 min |
| Publisher | 43109 (Pinggy manifest) | Origin only (secondary must never publish it — already the documented rule) | 15 min, commit message gains `[skip ci]` + unchanged-check (already idempotent) |
| Tunnel keeper/watchdog | 43108 family | Origin | Existing |
| Origin-status card | 43111 | Secondary | 15 min |
| Honest bridge state | One workflow writing a **three-state** status (up / degraded-known / down-new) as an artifact + a single tracking issue update — replacing skip-green and notice-only alike | Actions | 30 min |
| Mesh census poll | Existing goal-owned cron | Muse side (workspace snapshots, never committed) | 6h (existing) |
| HindSight status | Add `status` action of `deploy-hindsight.yml` to a scheduled, artifact-only check | Actions | 6h, aligned with census poll |
| Deploys | vercel-batch-deploy (existing adaptive budget) + Render via its own bucket | Actions | Existing |

### P3 — Failover order for reaching the origin (corrected to today's facts)

1. **Queue pull (P1)** — no reach needed; device comes to us. (Target state;
   until P1 lands, start at 2.)
2. **Pinggy via manifest** — only when `current.json` is `active` and fresh.
3. **Tailscale, GitHub-identity tailnet** — the tailnet the origin is actually
   on: usable today by operator/Hark surfaces that can join it; an Actions
   path requires a runner-join design for *this* tailnet (the current probe
   joins the wrong one — repoint or retire it, don't let it alarm forever).
4. **Tailscale, Google tailnet** — only after the on-device account switch is
   done (taps); until then it is **not** a failover step, it's a known-dead
   path, and the probe should report it as degraded-known, not page as new red.
5. **ADB via secondary (BugJaeger)** — human-in-the-loop last resort;
   also the channel that performs R2 recovery below.
6. **Cloudflare** — struck from the order until the consent block is
   deliberately resolved; restore it here when real.

### P4 — Recovery sequence for a dead origin (runbook, staged)

- **R0 — Declare**: bridge-state surface shows down-new (manifest stale >
  2×TTL **and** heartbeat stale >45 min **and** queue receipts stopped).
  One tracking issue, one owner notification (Hark + main chat) — not per-workflow spam.
- **R1 — Hands-off window (30 min)**: JobScheduler jobs are persisted;
  Android revives Termux jobs after reboot/network return on its own.
  Watch heartbeat/manifest only. Most overnight deaths are power/network.
- **R2 — Secondary/ADB session**: from the secondary, ADB to the origin and
  run, in order: `termux-job-scheduler --pending` (ground truth for
  43107–43109) → `bash scripts/termux/diagnose-pinggy-publisher.sh`
  (read-only) → the documented layout fix from DEVICE-ACCESS-DIRECTORY
  (`git checkout origin/master -- scripts/termux` in `$HOME`, honoring the
  `$HOME` checkout and `TERMUX_MONOREPO_ROOT`) → `install-pinggy-publisher-job.sh`
  → one `--publish`. Verify `current.json` flips to `active`.
- **R3 — Storage triage (only if df confirms pressure)**: relief order is
  caches → stale worktrees (sparse re-materialization) → build artifacts →
  rotated logs **outside** telemetry/training trees. Telemetry/HindSight data
  is never in scope (red line). Before any removal: confirm the
  `backup/tmx-node-primary-20261021/*` branches (or a fresher owner clone/archive)
  cover the tree in question.
- **R4 — Credential-family check**: if manifest is `active` but dispatch still
  fails, the missing `TERMUX_MCP_*` pair (SPOF-4) is the suspect — owner adds
  the names via the vault/UI route; chats verify presence by name only.
- **R5 — Secondary promotion (only if origin is hardware-dead)**: secondary
  takes the executor role via the role schema (`NODE-ROLE-SCHEMA.md`):
  identity re-init as executor, queue claimant enabled, publisher stays
  **off** until its own tunnel exists (never overwrite the origin manifest
  with a different node's endpoint under the origin's device id).
- **R6 — Post-recovery**: backfill receipts for the dead window, note which
  nightly tasks were lost vs drained late, and record the death cause in the
  mesh matrix's next hand refresh.

### P5 — Hosted-backend guardrails (no new builds, just ordering)

- Vercel/Render/Mintlify: keep the existing quota-first posture (batch deploy,
  learned offset, per-provider parallel threads each reconciling its own cap).
  Add the publisher/probe commits to the same accounting so device healing
  can't silently spend deploy quota (SPOF-12).
- GitLab mirror (I2): repair the 400 webhook — this is the cheapest real
  redundancy in the whole mesh (a second full repo copy off-GitHub) and it
  de-risks SPOF-11 more than any new tool.
- Neon/Supabase: finish the open lanes in order — Jules-UI re-verify Neon
  (contested), Supabase via its own email/password path, Muse-side helpers
  after vault key entry. Registry records stay entitlement-only until a live
  reading exists; `supabase.free` has none today.
- HindSight: scheduled status check (P2) + documented Fly→Koyeb failover
  trigger; no data moves without the retention preconditions.

### P6 — Monitoring honesty rules (apply to every watcher above)

1. **Skip is a state, not a success.** Any workflow that didn't do its job
   reports `skipped_not_active` as its own conclusion class in summaries —
   never green-as-done. (Bridge smoke is the template violation.)
2. **Three states only**: up / degraded-known (with the known-cause ticket
   linked) / down-new. Permanent red gets reclassified degraded-known within
   one cycle, or fixed — never left paging.
3. **Every watcher is watched**: census poll diff includes watcher-run
   conclusions (canary/probe/bridge-smoke) so a dead watcher shows up in the
   6h diff even if its own alerts stop.

## 4. Explicitly NOT proposed

- Deleting or pruning telemetry/training data for storage relief (red line).
- Disabling/muting any bot, canary, or probe to reduce noise — cadence and
  classification fixes only.
- Any browser GitHub sign-in, for any chat, for any of these steps
  (fleet credential rule).
- Committing census/poller output to the repo (quota rule) — this proposal
  itself stays a workspace file until the owner routes it.
- Rotating/revoking any credential named here (names-only; redundancy +
  owner clone/archive + dependency evaluation are preconditions for any
  future credential move).

## 5. NOT ESTABLISHED (stated, not filled in)

- Actual Runable error bodies for 2026-10-21 00:25 / 01:05 PDT (in-app only).
- Whether jobs 43107/43108 are truly scheduled on the origin right now
  (Hark's 08:08 report vs DEVICE-ACCESS-DIRECTORY's "likely lost" — no
  firsthand `--pending` output exists chat-side).
- Origin storage *now* (93% is the 08:08 PDT reading; no newer one).
- Whether the tunnel itself is up *now* (Hark's 07:59 PDT address push is the
  latest evidence; the manifest path is dead regardless).
- Neon → Jules current state (contested in fleet memory; needs Jules-UI check).
- Why `tunnel-canary` runs at head `f8fe2c3c` carried the older fail-red
  version while master already carries the notice-only version — vintage
  boundary noted, landing commit not traced in this pass.
- Hark's own connection set (not enumerated Muse-side; mesh matrix §10).

## 6. Evidence index

- Mesh matrix + census: `~/workspace/github-integration-census/`
  (`INTEGRATION-MESH-MATRIX.md`, `census.json`, `census2.json`, `census3.json`,
  `secrets_plus.json`, `reviews_updated.json`) — PR #1490.
- Repo files read at master this pass: `.github/workflows/deepagent-task.yml`,
  `deepcli-agent-bridge.yml`, `termux-bridge-connect.yml`,
  `termux-remote-exec.yml`, `tunnel-canary.yml` (also at `f8fe2c3c`),
  `tailscale-bridge-probe.yml`, `vercel-batch-deploy.yml`,
  `deploy-hindsight.yml`; `ops/termux-bridge/current.json`;
  `ops/quota/registry.json`; `scripts/termux/publish-pinggy-endpoint.sh`,
  `install-pinggy-publisher-job.sh`, `diagnose-pinggy-publisher.sh`,
  `run-deepagent-task.sh`, `connect-live-bridge.sh`,
  `scripts/termux-resource-sentinel.sh`, `scripts/termux-resource-snapshot.sh`,
  `scripts/termux/devices/install-device-jobs.sh`, `devices/boot/20-tmx-device-jobs.sh`;
  `docs/ops/DEVICE-ACCESS-DIRECTORY.md`, `BRIDGE-REDUNDANCY.md`,
  `TERMUX-LIVE-BRIDGE.md`, `SECONDARY-NODE-PROVISIONING.md`,
  `docs/ops/sessions/RESILIENCE.md`.
- Fleet memory: `~/MEMORY.md`; `memory/2026-10-21.md` L141–L145, L202
  (Runable failures, Hark device report, tunnel-canary timing).

*End of proposal. Next action belongs to main chat / the owner:
route P1–P6, or send this chat a scoped build order. Nothing above executes itself.*
