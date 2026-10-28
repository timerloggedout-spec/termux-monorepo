# Comment Quality on Record Surfaces — Standard, Census, Prevention

`[MUSEai]@{role:{comment-quality}}` · Owner order 2026-10-28 via the Delphi lane:
**improve the comments to be productive instead of spam.**
Ledger semantics coordinated with the Delphi lane; the noise definition below is the
Delphi ledger store's own (registry note, `ops/delphi/ledgers.json`; collector
`scripts/delphi/ledger_feed.py`), confirmed with the database lane's feed partition
(events carried, noise counted and excluded).

## 1. Record surfaces

A **record surface** is an issue whose comments (or body) are a fleet record, not a
conversation thread:

- the continuous ledgers pinned in `ops/delphi/ledgers.json` — outcomes + generation
  (#1487), weights (#1489);
- the living records in the same registry — Temporal self-host status (#2028,
  body-carried) and the results board (#1474, body-carried);
- the Delphi queue: issues labelled `delphi:rfp` (applicants) and
  `delphi:participant` (research participants), whose per-issue gate ledgers
  (`<!-- delphi-ledger v1 -->`) are their scoring record.

## 2. What belongs (productive)

A comment on a record surface is productive iff it carries state, evidence, a
decision, or a correction:

- **ledger events** — body starts with a registered marker
  (`<!-- delphi-outcomes v1 -->`, `<!-- delphi-weights v1 -->`,
  `<!-- delphi-generation-* -->`, `<!-- delphi-ledger v1 -->`, …);
- **signed appendices** — body starts with `[MUSEai]@{role:{…}}` (coordination,
  corrections-as-new-events; corrections never edit an earlier event);
- **completed automation output** — e.g. a triage comment carrying an actual
  classification/labels/recommendation;
- **human/operator substance** — evidence, audits, decisions, priority rulings.

## 3. What is noise (removable)

Exactly two classes are removable, both verified firsthand in the census below:

- **vendor-promo** — the Blocks GitHub App's identical onboarding pitch
  (`blocksorg[bot]`, body starts "Mention Blocks like a regular teammate"),
  dropped once on every new issue regardless of content. Carries no state,
  evidence, decision, or correction about the issue it lands on.
- **automation-failure** — a peer-router stub (`<!-- openrouter-triage -->` and
  sibling provider markers) whose entire content is "invocation incomplete"
  (HTTP 429 in every census case): no classification was produced. The failure
  is already recorded in the workflow's step summary / telemetry; the comment
  adds nothing.

Everything not in these two classes is **never** deleted by a cleanup: not ledger
events, not signed appendices, not completed automation, not human comments.
Unknown shapes default to productive (keep) — classification is conservative by
design, and the sweep (`scripts/comment_quality_sweep.py`) encodes exactly this.

## 4. Census 2026-10-28 (live, PAT API at audit time)

Population: 77 issues — #1487, #1489, #2028, #1474 + 28 `delphi:rfp` + 48
`delphi:participant` (the 48 research filings carry the participant label; their
titles carry the `[delphi:rfp]` prefix). 373 comments total.

| class | count | share |
|---|---|---|
| ledger events + signed appendices + substantive | 262 | 70.2% |
| completed triage (productive automation) | 1 | 0.3% |
| vendor-promo (Blocks) | 71 | 19.0% |
| automation-failure (triage stubs, all HTTP 429) | 39 | 10.5% |
| **noise total** | **110** | **29.5%** |

Per surface: #1487 12 comments (11 productive / 1 Blocks); #1489 5 (4 / 1);
#2028 2 (0 / 1 Blocks + 1 failure stub — the trigger case: a living-body record
whose only comments were noise); #1474 1 (0 / 1 Blocks); `delphi:rfp` queue 196
(151 productive incl. the 1 completed triage / 28 Blocks / 17 stubs);
`delphi:participant` queue 157 (96 / 39 Blocks / 22 stubs). 9 participant issues
had no Blocks drop — the app does not fire on every issue class, but no pattern
exempts record surfaces.

## 5. Cleanup 2026-10-28 (executed, verified)

All **110 noise comments were deleted** via the API (maintainer PAT route):
71 vendor-promo + 39 automation-failure. No ledger event, signed appendix,
completed automation output, or human comment was touched. Post-clean re-census
of the same 77 issues: **263 comments remain, 0 noise** — exactly the productive
set (262 + 1 completed triage). The ledger feed's noise counters will read 0 for
these issues on its next refresh; this census is the preserved count of record
for what was removed.

## 6. Prevention

1. **Failure stubs no longer post.** `.github/actions/http-llm-invoke` posted the
   "invocation incomplete" text as a comment on every failed peer call. It now
   records failures only in its telemetry (step summary + observations), and
   posts a comment only on a completed invocation. This kills the
   automation-failure class at the source for every provider/role using the
   action.
2. **Weekly sweep.** `.github/workflows/comment-quality-sweep.yml` runs
   `scripts/comment_quality_sweep.py` weekly (report to the step summary) and on
   dispatch, with an explicit `delete=true` dispatch input for a maintainer-run
   cleanup of the two removable classes only.
3. **Vendor-promo source is an owner UI item.** The Blocks drop is posted by the
   Blocks GitHub App, not by any workflow in this repo, so no repo change can
   stop it; the app-side switch is the "Disable this message" / integration
   setting in the Blocks workspace (linked from the pitch itself). Until that is
   toggled owner-side, the sweep is the containment. Recorded here as an
   owner-UI item of record; it does not block any lane.
4. **Posting rule for agents.** Fleet agents posting on a record surface use the
   signed form (`[MUSEai]@{role:{…}}`) or a registered marker, and post only
   state, evidence, a decision, or a correction. Discussion that is none of
   those goes on the working issue/PR it concerns, not on a ledger or
   living-record issue.

## 7. Who may post / remove

- Post: the gate and registered collectors (marker events), fleet lanes (signed
  appendices), the operator, and automation whose output is complete.
- Remove: a maintainer lane may delete the two §3 classes on record surfaces via
  the API. Nothing else is removable by cleanup; a wrong substantive comment is
  answered by a signed correction event, never by an edit or deletion — the
  append-only invariant of the ledger store applies to comments of record.
