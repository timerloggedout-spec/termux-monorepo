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
  it, add a staleness alarm. **Status: closed-on-evidence (2026-10-27).**
  Closure verified firsthand by the Gap Finder: PR #1759 merged 12:39Z
  (staleness rule + `help-wanted-audit-staleness.yml` watchdog, on master),
  PR #1767 merged 12:43Z (ledger closure), PR #1815 merged 14:16Z
  (age-based firing for the four sibling lanes starved by the
  quota-dispatch-tree cadence move, #1573). Master's generated audit reads
  `generated_at 2026-10-27T14:18:07Z` and carries the SendAm #492/#607 rows
  as closed_unmerged — the exact rows the silence had missed. The Tribute
  lane independently re-verified the same record from its side.

### G-03 — Delphi outcome flywheel: no automated ingestion
- Surface: Delphi Oracle. Layers: done vs executed.
- Evidence: outcome ledger #1487 carried no postings 2026-10-21 → 2026-10-26
  (next posting 2026-10-27 = the Strands pass ballot/calibration, posted by
  hand through the cycle tooling). Ingestion build is open issue #1533
  ("ingest Tribute System 1 outcomes"), state open at sweep time.
- Severity: medium (the method improves only when outcomes flow).
- Fix route: Delphi lane builds #1533. Status: fix-spawned (Delphi lane,
  dispatched 2026-10-27).

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
  Status: open (owner decision); disposition-prep chat spawned 2026-10-27
  to re-audit at current heads and prepare per-PR packets.

### G-07 — Builder profile incomplete → D1 entry validity at risk
- Surface: challenges (D1, deadline Nov 4). Layers: claimed vs held.
- Evidence: `docs/ops/PROFILE-REGISTRY.md` (read this sweep): AWS Builder
  Center @1337dia590r1c8u1ldr — "Status: exists — INCOMPLETE (observed live
  2026-10-26: default avatar, no bio)"; official terms require full name,
  country, profile image, about section, ≥1 social link.
- Severity: high, time-bound (entries invalid without a complete profile).
- Fix route: owner completes the profile (prepared content sits in the
  registry); challenge lane verifies. Status: open (owner-gated);
  challenge lane dispatched 2026-10-27 to re-verify the live profile and
  itemize what remains.

### G-08 — D3/Builder.io: Clips account requirement UNVERIFIED
- Surface: challenges (D3, deadline Nov 2). Layers: claimed vs held.
- Evidence: proposal record `docs/proposals/active/delphi-desk-builder-io/
  ITEMS.md` DD-005 (read this sweep): "account requirement UNVERIFIED (open
  risk in the challenge log)". The submission step blocks on it.
- Severity: high, time-bound (earliest deadline in the slate).
- Fix route: challenge lane verifies against Builder publish docs / a trial
  publish; surfaces immediately if it turns out owner-gated. Status:
  fix-spawned (challenge lane verification, dispatched 2026-10-27).

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
  Status: fix-spawned (Delphi lane, dispatched 2026-10-27).

### G-10 — Dashboard surface feeds refresh by manual PR only
- Surface: dashboard (MoneyBall / 3L0 / MVT / DoE feeds). Layers: held vs
  executed.
- Evidence: no collect workflow exists for `scripts/dashboards/
  surface_feeds.py` outputs, while `oracle-panel-feed-collect.yml` and
  `reviewer-metrics-collect.yml` refresh their feeds on a schedule. Surface
  feeds carry `generated_at`, so staleness is visible but unbounded.
- Severity: low–medium (structural — pages will silently age).
- Fix route: add a collect workflow mirroring the oracle pattern, or accept
  manual refresh with a staleness threshold alarm. Status: fix-spawned
  (Web Design lane, dispatched 2026-10-27).

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
  held. Severity: medium. Route: separation chat spawned 2026-10-27.
- (b) 3L0 weighting: page renders seed defaults and points at ledger #1489;
  the observed live values (0.68 / 1532 lineage) are not held in the feed.
  Severity: medium. Route: backfill chat spawned 2026-10-27.
- (c) Quota readings lack `observed_at` (evidence gate H0/confirmed/≤15 min
  can never pass on the published readings) — evidence dated 2026-10-21
  (web-design assessment); current readings not re-read this sweep (API rate
  limit). Severity: medium. Route: quota gaps chat spawned 2026-10-27;
  re-verify readings first.

## Sweep 1 dispatches (2026-10-27, owner-approved)

- G-02 → Tribute lane efficacy audit lane (existing): restore refresh +
  staleness surfacing.
- G-03 + G-09 → Delphi Oracle lane (existing): ingestion build #1533;
  oracle feed evidence-set + per-candidate scores.
- G-07 + G-08 → Challenge entries lane (existing): profile re-verification;
  Clips account question resolution.
- G-10 → Web Design Specialist lane (existing): surface-feeds collect
  workflow.
- G-06 → new chat "ECC findings — disposition prep": at-head re-audit +
  per-PR disposition packets (decision stays the owner's).
- G-12a → new chat "MVT / DoE / ATES separation". G-12b → new chat
  "3L0 weighting backfill". G-12c → new chat "Quota gaps — readings,
  registry, text lane".
- G-04 / G-05 remain owner-gated with their owning lanes (Devin Wiki lane;
  Data Agent Kit lane) — no dispatch changes them.
- G-11 already fix-spawned (Tier 1 Classifiers steward).

## Sweep notes
- API core rate limit was hit mid-sweep (2026-10-27 12:27 UTC); items marked
  "deferred" get first call on next sweep's budget.
- Counts and states above are live-derived at sweep time, never copied from
  dated documents without a re-check.
