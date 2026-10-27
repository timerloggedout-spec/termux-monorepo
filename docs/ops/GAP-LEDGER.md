# Gap Ledger — fleet surfaces & substrates

Standing record of the Gap Finder sweep (side chat: Gap Finder — sweep, verify,
ledger). An entry exists only with firsthand evidence (file / API / run state),
a severity, an owning surface, and a proposed fix route. Statuses: `open` /
`fix-spawned` (a lane owns the fix) / `closed-on-evidence`. The Gap Finder does
not fix; main chat spawns one fix chat per accepted entry. Re-verified each
sweep; entries close only on evidence.

Layers key: **claimed** (pages/docs assert) vs **held** (feeds/records contain)
vs **done** (code/workflows implement) vs **executed** (runs/artifacts prove).

## Sweep 1 — 2026-10-27 (~05:25 PT)

### G-01 — Values board PR stalled after takeover assignment
- Surface: dashboard / help-wanted. Layers: done vs executed.
- Evidence: PR #1589 ("feat: add Free-Tier Use Value Board") sat open at head
  `beb693156933`, last updated 2026-10-27T09:01Z, after the takeover was
  assigned (~04:34 PT) — then landed during this sweep.
- Severity: was high. **Status: closed-on-evidence** — PR #1589 merged
  2026-10-27T12:20:28Z; merge commit `ba71a16d1820` found in master history.

### G-02 — Tribute diagnostics silently stale (refresh silent since Oct 23)
- Surface: Help-Wanted Tributes → Help-Completed diagnostics. Layers:
  executed vs recorded.
- Evidence: efficacy audit (PR #1736, merged) records the generated audit last
  refreshed 2026-10-25T05:09Z and the status-refresh schedule silent since
  Oct 23 — it missed the SendAm stake closures (2026-10-26).
  `.github/workflows/help-wanted-status-refresh.yml` exists on master.
- Severity: high (fleet decisions read these diagnostics as current).
- Fix route: repo-automation fix chat — diagnose the refresh schedule, restore
  it, add a staleness alarm. Status: fix-spawned 2026-10-27.
- **Root cause (diagnosed 2026-10-27, run-id evidence):** commit e0f661b29d
  (2026-10-23, Tier 2 cadence takeover, #1573) removed the lane's own schedule;
  sole cadence owner `quota-dispatch-tree.yml` set
  `dispatch_hw_refresh = (UTC minutes < 10)` — a phase window assuming its
  */10 cron lands hourly in minutes 0–9. GitHub delivers that schedule
  ~6×/day at jittered minutes: the refresh's only two post-takeover
  dispatches (runs 40037960621, 40164462301) each landed ~30s after the only
  two tree runs at minute 08; all 13 tree runs after 2026-10-25T05:08Z landed
  at minutes 11–59, so the refresh never fired and no run could fail (the
  audit step is `continue-on-error`; no staleness check existed).
- **Resolution: closed-on-evidence 2026-10-27.** PR #1759 merged
  `f81e659d96c6` (master-history + landed-content verified): (1) tree Node F0
  measures the lane's real age and fires when stale > 75m, phase-independent;
  (2) the refresh workflow fails red if the committed audit's `generated_at`
  is > 20m old after a run; (3) new watchdog
  `help-wanted-audit-staleness.yml` (every 2h at :41) fails red and dispatches
  a recovery refresh when audit age > 180m. Proof: refresh dispatch run
  40505526019 success; audit regenerated `generated_at`
  2026-10-27T12:41:17Z with EF-CHAIN/SendAm #492/#607 recorded
  `closed_unmerged`, `realized_effect_verified: false` (the missed closures,
  now captured as non-conversions); first watchdog run 40505822630 success.
- Follow-up (not part of this gap): the sibling lanes' tree nodes
  (execute/followup/scout/assist, silent since Oct 23) carry the same
  firstCycle∧hour-mod starvation pattern, and
  `tests.test_actions_incident_dedupe.test_cadence_emits_lag_failure_incidents`
  still asserts the pre-takeover cadence cron — both recorded on PR #1759.

### G-03 — Delphi outcome flywheel: no automated ingestion
- Surface: Delphi Oracle. Layers: done vs executed.
- Evidence: outcome ledger #1487 carried no postings 2026-10-21 → 2026-10-26
  (next posting 2026-10-27 = the Strands pass ballot/calibration, posted by
  hand through the cycle tooling). Ingestion build is open issue #1533
  ("ingest Tribute System 1 outcomes"), state open at sweep time.
- Severity: medium (the method improves only when outcomes flow).
- Fix route: Delphi lane builds #1533. Status: open.

### G-04 — Devin Wiki indexer built and gated, credential never provisioned
- Surface: Devin Wiki indexing. Layers: done vs executed.
- Evidence: verified 2026-10-27 — 39 Actions secrets, none DEVIN-named; zero
  DEVIN Actions variables. `DEVIN_API_KEY` sits on the phantom-secret
  remediation checklist by reference (PR #1728). Indexer refuses all Devin
  calls until `DEVIN_API_KEY` + `DEVIN_ORG_ID` + `DEVIN_WIKI_EFFORT` exist.
- Severity: medium (account-wide backfill at free effort waits on one act).
- Fix route: owner provisions via the custom.devin connector (capture link
  already issued in the Devin Wiki lane); lane then verifies + backfills.
  Status: open (owner-gated).

### G-05 — Data Agent Kit wired, activation blocked on owner GCP session
- Surface: Data Agent Kit. Layers: done vs executed.
- Evidence: full wiring merged (PR #1689); card route closed (PR #1691);
  activation runbook `docs/ops/DATA-AGENT-KIT-ACTIVATION.md`; status
  `wired_full_pending_gcp_project` (live config re-read deferred this sweep —
  API rate limit). No BigQuery read path exists until the owner creates a
  billing-less GCP project and completes the gcloud sign-in session.
- Severity: medium. Fix route: one owner session; lane verifies read path.
  Status: open (owner-gated).

### G-06 — ECC findings: 14 action_required, undispositioned
- Surface: PR review (ECC Tools). Layers: executed vs recorded.
- Evidence: `docs/ops/generated/reviewer-metrics.json` → providers/ecc:
  `findings_action_required: 14` (Security Evidence 8, PR Config Audit 6),
  `current_head_findings: 1`, across PRs #125 / #143 / #1514 at their last
  audited heads. No disposition is recorded.
- Severity: medium. Fix route: owner disposition + author fixes at head.
  Status: open (owner decision).

### G-07 — Builder profile incomplete → D1 entry validity at risk
- Surface: challenges (D1, deadline Nov 4). Layers: claimed vs held.
- Evidence: `docs/ops/PROFILE-REGISTRY.md` (read this sweep): AWS Builder
  Center @1337dia590r1c8u1ldr — "Status: exists — INCOMPLETE (observed live
  2026-10-26: default avatar, no bio)"; official terms require full name,
  country, profile image, about section, ≥1 social link.
- Severity: high, time-bound (entries invalid without a complete profile).
- Fix route: owner completes the profile (prepared content sits in the
  registry); challenge lane verifies. Status: open (owner-gated).

### G-08 — D3/Builder.io: Clips account requirement UNVERIFIED
- Surface: challenges (D3, deadline Nov 2). Layers: claimed vs held.
- Evidence: proposal record `docs/proposals/active/delphi-desk-builder-io/
  ITEMS.md` DD-005 (read this sweep): "account requirement UNVERIFIED (open
  risk in the challenge log)". The submission step blocks on it.
- Severity: high, time-bound (earliest deadline in the slate).
- Fix route: challenge lane verifies against Builder publish docs / a trial
  publish; surfaces immediately if it turns out owner-gated. Status: open.

### G-09 — Oracle feed: two substrate thin spots
- Surface: Oracle Panel. Layers: held vs claimed.
- Evidence (feed read this sweep):
  (a) Delphi Desk `evidence_basis.sources` / `claim_areas` = null — its
  117-item evidence set was never committed, so composition cannot be
  recomputed; the feed states the absence honestly (rendering is correct;
  the substrate record is what is missing).
  (b) Every Strands candidate carries the same pass-level `rounds` block;
  only `rank_of_this` differs — per-candidate weighted scores are not held
  as distinct feed fields (owner-flagged "each have the same score"). The
  candidates' identical evidence *composition* is by construction (one
  shared 123-item set) and is not a gap.
- Severity: medium. Fix route: Delphi-lane collector extension — commit or
  reference the Delphi Desk evidence set; carry per-candidate scores.
  Status: open.

### G-10 — Dashboard surface feeds refresh by manual PR only
- Surface: dashboard (MoneyBall / 3L0 / MVT / DoE feeds). Layers: held vs
  executed.
- Evidence: no collect workflow exists for `scripts/dashboards/
  surface_feeds.py` outputs, while `oracle-panel-feed-collect.yml` and
  `reviewer-metrics-collect.yml` refresh their feeds on a schedule. Surface
  feeds carry `generated_at`, so staleness is visible but unbounded.
- Severity: low–medium (structural — pages will silently age).
- Fix route: add a collect workflow mirroring the oracle pattern, or accept
  manual refresh with a staleness threshold alarm.
- **Resolution: closed-on-evidence 2026-10-27.** PR #1770 merged
  `b0ba36c62b3b` (master-history + landed-content verified):
  `.github/workflows/surface-feeds-collect.yml` mirrors the oracle pattern
  — `workflow_dispatch`, weekly schedule (Wed 06:41 UTC), and a
  master-push trigger on the collector's source paths; it invokes
  `scripts/dashboards/surface_feeds.py --surface all` and proposes the
  refresh as a PR from `surface-feeds/refresh`, never committing
  directly. One workflow covers all five feeds (the separation lane
  added ATES mid-fix; the workflow and contract were extended to it).
  Proof: dispatch run 40506438873 success; the run opened refresh PR
  #1773, merged `2b1a0ca30bbc` — the five feeds regenerated from current
  records, the 3L0 feed now carrying the separation collector's shape.
  (First filing #1758 was closed unmerged by a branch reset during
  rebase-by-content; nothing landed from it — state record on that PR.)

### G-11 — Tier 1 classifiers: code healthy, never executed
- Surface: classifiers (Mev/Jev/Kev/Laya). Layers: done vs executed.
- Evidence: `deepcli/deepcli/observatory/` on master with 34 passing tests;
  the `deepcli.llm.adapters` package Mev routes to does not exist (404);
  the quartet's only importer is its test file (both verified 2026-10-27).
- Severity: medium. Fix route: **fix-spawned** — Tier 1 Classifiers steward
  lane owns the adapter build + dispatch workflow. Status: fix-spawned.

### G-12 — Owner-named surface concerns (verification state recorded)
- (a) MVT / DoE / ATES conflation — MVT page renders the ATES harness; DoE
  page cites a Delphi record as its executed comparison. Layers: claimed vs
  held. Severity: medium. Route: separation fix chat (main to spawn).
- (b) 3L0 weighting: page renders seed defaults and points at ledger #1489;
  the observed live values (0.68 / 1532 lineage) are not held in the feed.
  Severity: medium. Route: backfill fix chat (main to spawn).
- (c) Quota readings lack `observed_at` (evidence gate H0/confirmed/≤15 min
  can never pass on the published readings) — evidence dated 2026-10-21
  (web-design assessment); current readings not re-read this sweep (API rate
  limit). Severity: medium. Route: quota fix chat; re-verify readings first.

## Sweep notes
- API core rate limit was hit mid-sweep (2026-10-27 12:27 UTC); items marked
  "deferred" get first call on next sweep's budget.
- Counts and states above are live-derived at sweep time, never copied from
  dated documents without a re-check.
