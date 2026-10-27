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
- Fix route: Delphi lane builds #1533.
- **Status: closed-on-evidence (2026-10-27).** Built as specced: PR #1824
  merged 89579fd8; the dry run reproduced the sweep's numbers exactly
  (169 keyed signals, sum -76.0, mean -0.45); the first live flow posted
  the 169 outcomes; a second dispatch deduped all 169 and posted nothing.
  Issue #1533 closed with the full record. Addition from the build: the
  first run exposed a pre-existing ledger-resolution bug (label-order
  found[0] sent outcome state to #1567 and a from-defaults weights update
  to #1784) — fixed by title resolution in PR #1833 merged 93859300, state
  migrated onto #1487, misdirected postings marked superseded, the batch's
  role-feedback step recorded as consumed-not-replayed. Current read for
  any future sweep: outcome ledger #1487's newest state (n=170 folded,
  169 digests).

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
  registry); challenge lane verifies. Status: fix-spawned — VERIFIED OPEN
  2026-10-27 (PR #1820): live re-check shows the profile unchanged
  (default placeholder avatar, About empty, no social links; display name
  + country set) — 3 of 5 mandatory fields still open. OWNER CORRECTION
  (2026-10-27): the "owner-only edit" framing is wrong — the profile
  follows the @N0n (4n0n) anonymous style setup and is completed BY THE
  AGENCY; the challenge lane is dispatched to complete it from the
  registry's prepared content through the fleet's signed-in session. Sole
  carve-out (per the 4n0n protocol): a genuinely forced real-name field
  returns to the owner; everything else is agency work.

### G-08 — D3/Builder.io: Clips account requirement UNVERIFIED
- Surface: challenges (D3, deadline Nov 2). Layers: claimed vs held.
- Evidence: proposal record `docs/proposals/active/delphi-desk-builder-io/
  ITEMS.md` DD-005 (read this sweep): "account requirement UNVERIFIED (open
  risk in the challenge log)". The submission step blocks on it.
- Severity: high, time-bound (earliest deadline in the slate).
- Fix route: challenge lane verifies against Builder publish docs / a trial
  publish; surfaces immediately if it turns out owner-gated.
- **Status: closed-on-evidence (2026-10-27)** — the question is RESOLVED
  (challenge log record, PR #1820 merged 8fafccc48b): recording on the
  hosted Clips instance (clips.agent-native.com) REQUIRES an account (the
  landing is the sign-in wall; no guest path; trial stopped at the wall),
  while viewing a public clip needs no login — satisfying the Official
  Rules' criterion — and the submission form is account-free. Correction
  to the earlier lean: the account is a free Clips app account, NOT a
  Builder.io CMS Space/plan. Successor item — DONE (2026-10-27): the
  owner approved the free Clips account and it was created the same day
  via the Google route on the fleet Google identity (registry record,
  PR #1835 merged 264c5d9771: account CREATED; no handle exists on this
  surface — none offered at sign-up; no personal-name field forced; no
  payment requested). D3's enforced check now shows the account branch
  satisfied. One in-app setup item remains for the build weekend:
  connect clip storage before recording.

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
- **Status: closed-on-evidence (2026-10-27).** (a) Desk composition landed
  via PR #1774 (merged before the dispatch crossed it): the master feed
  carries `sources {github-api: 115, challenge-log-packet-d3: 2}` over the
  117-item set with sha + assembled_at. (b) PR #1827 merged e1992587: each
  candidate's round now carries a distinct per-candidate `score` field
  read from the BALLOT records, with a distinctness test on non-tied
  fixtures (the Strands values themselves remain honestly tied at 23.269).
  Both halves re-verified firsthand in the master feed by the Gap Finder.

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
- **Status: closed-on-evidence (2026-10-27).** Collect workflow landed via
  PR #1770 merged b0ba36c62b (dispatch + Wed 06:41 UTC schedule + push
  triggers on the collector's sources; refresh-by-PR only; five feeds incl.
  ATES). Production proof: dispatch run 40506438873 → refresh PR #1773
  merged; push runs → refresh PR #1778 merged; master feeds stamped
  2026-10-27T13:09:19Z (moneyball feed stamp re-verified by the Gap
  Finder). Closure first recorded by the Web Design lane in PR #1823
  merged 3b01ebc6c613; that edit was inadvertently reverted by the Gap
  Finder's whole-file publish in PR #1830 and is restored here — ledger
  updates must henceforth rebase on current master content.

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
