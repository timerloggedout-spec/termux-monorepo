# GitHub App Fleet — Migration / Maintenance / Upgrade ITEMS

Checklist of record for `docs/ops/GITHUB-APP-MIGRATION-PLAN.md`.
An item checks only on firsthand evidence (run id, bucket reading, landed
PR) — never on a lane report alone. Owner lane in brackets.

## State snapshot (2026-10-30)

- [x] Collector proven: bucket split 5000/5000 @ PAT 0 (2026-10-30T02:18Z)
- [x] Collector recorded: `github.api.app_collector` + #1884 meta-pool slice
- [x] Collector custody: connector keys/ 0600, fingerprint recorded
- [ ] Collector standing: first production workflow on app token

## MIG — migration waves (plan §1; gates G1–G5 per item)

- [ ] MIG-01 Wave 0: `repository-observatory` → Collector (G1–G5) [migration-plan]
- [ ] MIG-02 Wave 1: `reviewer-metrics-collect` → Collector (~750 calls/run off PAT) [migration-plan]
- [ ] MIG-03 Wave 1: Delphi feed collectors' GitHub reads → Collector, one at a time (ledger, rfp, proposals, oracle-panel, linguist-panel, surface, traffic) [migration-plan]
- [ ] MIG-04 Wave 1: `provider-availability` GitHub probe steps → Collector [migration-plan]
- [ ] MIG-05 Wave 1: read-only recon/observer class → Collector (discovery, reconcile, issue-observatory, observer pollers, telemetry snapshot, osint reads) [migration-plan]
- [ ] MIG-06 Wave 2: workflow publishes/merges/comments → Publisher, on Publisher standing [migration-plan + appid]
- [ ] MIG-07 Wave 2: lane `pat_publish` opt-in to Publisher token, after AppID lane declares minter lane-usable; PAT fallback retained [appid]
- [ ] MIG-08 Wave 3: `peer-review-orchestrator` polling → Reviewer-ops, on its standing [migration-plan]
- [ ] MIG-09 Wave 4: gate check-runs/annotations → Gate/CI, on its standing [migration-plan]
- [ ] MIG-10 Wave 5: issue-lifecycle sweeps → Lifecycle, on its standing [migration-plan]
- [ ] MIG-11 Per-item calls/run recorded into quota registry at G4 (MEASURE-AT-GATE items: M1, M3, M4, M5) [quota]

## APP — new app graduations (plan §3.4: proven → recorded → planned → standing)

- [ ] APP-01 Publisher: naming final set (conference close) [registry]
- [ ] APP-02 Publisher: manifest package PR + creation + install [appid]
- [ ] APP-03 Publisher: proven + recorded (#1884 slice) + custody [appid + quota]
- [ ] APP-04 Publisher: standing (first workflow on token) [appid]
- [ ] APP-05 Reviewer-ops: same four steps (naming / package+install / proven+recorded / standing) [appid + registry + quota]
- [ ] APP-06 Gate/CI: same four steps [appid + registry + quota]
- [ ] APP-07 Lifecycle: same four steps [appid + registry + quota]

## TEL — telemetry integration (PR #2407 audit, 2026-10-30)

Acceptance rule (audit, adopted): an app is not operationally integrated
merely because it exists in the registry — identity, effective scope,
execution and evidence must be independently observable.

- [ ] TEL-01 #2407 declaration layer merged (registry.json + emitter + tests) [author lane; review: migration-plan]
- [ ] TEL-02 Collector registered in integration-mesh snapshot/diff (mesh 6h poll consumes registry.json; app visible with no check suites) [mesh lane]
- [ ] TEL-03 Emitter scheduled + mint-wired: weekly census run on a freshly minted installation token (never a stored token) — feeds MAINT-02 readings [quota + migration-plan] — MINT-WIRING DONE 2026-10-30: mint pattern proven by green probe run 41016897632 (app-id var TERMUX_FLEET_COLLECTOR_APP_ID + secret TERMUX_FLEET_COLLECTOR_PRIVATE_KEY); remains open for census scheduling only.
- [ ] TEL-04 Live permission readback on installation token vs manifest declarations (drift leg of MAINT-01); declared ≠ observed kept separate [appid]
- [ ] TEL-05 Negative-path tests pass: missing credentials, revoked installation, inaccessible repository, permission drift [author + appid]
- [ ] TEL-06 First runtime receipt (plan §1.4 G4 fields) captured on a real Collector-token collection run — closes MIG-01's evidence requirement [migration-plan]

## SEC — provisioning (owner items, names-only)

- [x] SEC-01 RESOLVED as identity separation (2026-10-30): the `APP_PRIVATE_KEY` + `APP_CLIENT_ID` referenced by `github-app-capability-probe.yml` belong to that probe's Checks:write app (PR #800 lineage) — NOT to the Collector. It is not provisioned, and must not be provisioned with the Collector PEM; it stops being a Collector blocker. Its own provisioning waits for the Gate/CI app (APP-06). [migration-plan]
- [x] SEC-02 Collector Actions pair provisioned (2026-10-30): secret `TERMUX_FLEET_COLLECTOR_PRIVATE_KEY` (sealed-box from custody PEM, value never in chat/files/logs) + variables `TERMUX_FLEET_COLLECTOR_CLIENT_ID` + `TERMUX_FLEET_COLLECTOR_APP_ID` (App ID 5535733; the action takes app-id, not client-id — fix PR #2427), proven by green `github-app-collector-mint-probe` run 41016897632 [migration-plan + owner order 2026-10-29]
- [ ] SEC-03 Per-app Actions secret names for future apps follow the SEC-02 pattern (`TERMUX_FLEET_<ROLE>_*`), provisioned + verified before any workflow references them [owner + appid]

## MAINT — recurring (all as GitHub Workflows; VM hosts none)

- [ ] MAINT-01 Weekly permission-drift audit workflow live (installed perms vs manifest of record; diff → one tracking issue) [appid]
- [ ] MAINT-02 Weekly bucket census live (per-app `GET /rate_limit` readings → registry via #1884 route; missing = null) [quota]
- [ ] MAINT-03 Monthly GitHub API changelog / version review; deprecations become items here with sunset dates [migration-plan]
- [ ] MAINT-04 Quarterly minter upkeep (pinned action release, JWT claims, token-expiry handling) [appid]
- [ ] MAINT-05 Collector PEM rotation due by 2027-04-29 (6-month anchor from 2026-10-29 creation); per-app anchors set at each creation [appid]
- [ ] MAINT-06 Rotation procedure test: zero-downtime dual-key overlap exercised once before first due date [appid]

## UP — upgrades (plan §3)

- [ ] UP-01 First permission expansion executed via PR-reviewed manifest diff + installation consent (template run) [appid]
- [ ] UP-02 First multi-repo install: own registry record + G3/G4 proof on the new repo [appid + quota]
- [ ] UP-03 Foreign-install census line added to weekly census (counts only) [quota]
- [ ] UP-04 PARKED (owner [later]): Marketplace publishing; user-authorization callback + device-flow user tokens — no design until unparked [owner]
