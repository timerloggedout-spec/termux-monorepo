# Research cycle — D0 + D1 Opportunity Specs (2026-11-03)

*One complete cycle under the swarm research template
(`docs/ops/SWARM-RESEARCH-TEMPLATE.md`), run by the
optimizations-assurance seat on owner order via main ("complete a
research cycle ++ gather materials|skills|tools"). Intake: the two
Opportunity Specs as amended (exact + surface-mapped) —
`entries/d1-studysprint/OPPORTUNITY-SPEC.md` ·
`entries/d0-delphi-oracle/OPPORTUNITY-SPEC.md`. Atoms = every
requirement in both specs. Cross-check order per the template:
fleet record first (stamped HELD / IN-FLIGHT / GAP with pointers),
then research only the gaps. Outcomes sections in both specs are
HELD OPEN per main's amendment — this cycle feeds them, it does
not close them.*

## D1 atoms — StudySprint (Strands SDK: Workshop to Ship)

| # | Atom (requirement, short form) | Fleet verdict | Pointer |
| --- | --- | --- | --- |
| D1-1 | Eligibility (18+, Builder profile) | HELD | published project exists ⇒ profile of record; coordinator record |
| D1-2 | Workshop completion in-window | HELD | 2026-10-30, all 7 modules incl. AgentCore Runtime deployment |
| D1-3 | Strands agent for social good (Education) | HELD | `agent.py` — `build_strands_agent`, 7 tools on a `strands.Agent` |
| D1-4 | Model-access proof (live leg) | **IN FLIGHT** | issue #4534 · PR #4535 merged `31c5c98719bf` · run `41692801359` dispatched, queued under fleet saturation at cycle time; receipt returns to the D1 seat on completion |
| D1-5 | AWS schema set (production span) | **IN VERIFY** | issue #4537 · the `strands-aws/` artifact (5 schema sections, 35/35 golden validations) in the D1/Desk queue at cycle time |
| D1-6 | Project article on Builder Center | HELD | LIVE since 2026-10-30 (`content/3LRJhGucOZfz9ydzFax8sD2p5yB`); currency edit on the open line |
| D1-7 | Published project + confirmation | HELD | published 2026-11-03 ~10:01 PT · `project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint`; the body's verbatim-correction cycle is part of the record (PR #4530) |
| D1-8 | Public repo + releases | HELD | studysprint repo public · core v0.5.0 (432649080) · apk-v0.1.3 · webapp-v0.1.0 · tui-v0.1.0 |
| D1-9 | Demo video < 3 min, public | HELD | WK9LMwpvHUk — 2:54, embedded via the editor |
| D1-10 | Original agent, provenance (D0 vendored) | HELD | `foundation/` carries the D0 gate + `fetch_evidence` verbatim; D0 spec = companion artifact |
| D1-11 | Live demo endpoint | HELD-WITH-CAVEAT | version URL of record serves webApp 0.1.0; the Pages pipeline failure is GitHub-side (repo exonerated), recovery watch at Web Dev; Desk ruling: the submission does not ride Pages |
| D1-12 | Rubric — both frames, labeled | HELD | About 4×25 (social impact · technical execution · communication · originality) vs Rules 35/25/15/25 — quoted verbatim in the spec, never blended |
| D1-13 | Surface family at current state | PARTIAL-BY-SEQUENCE | parity matrix @ master: 0.2.0 in-tree (it-1 merged); 0.2.0 cuts gated on sync parity — **parity restored + race-fix verified at cycle time** (ss sync run 41689992475 SUCCESS, all steps incl. the parity gate; stamp #4456 `6612318198`) ⇒ the cuts' precondition is now met |
| D1-14 | Freeze machinery | HELD | snapshot workflow proven both halves (publish-on-red + loud failure; proving run `41689697108`) · re-arm DONE at the Desk · the ss-layout test settled (PR #4546 merged `e3ddc96c52`) ⇒ Nov 5 06:30Z capture takes the v1.0.0 state, TEST PRIOR clean on merit |
| D1-15 | Open line to the Nov 4 freeze | PENDING (scheduled work) | v1.0.0 cut on the richest green tree ⇒ Body update block ⇒ article currency ⇒ frozen-state verification |
| D1-16 | Outcomes section | HELD OPEN | stamped PENDING-JUDGING; scoring imported; entries/placements/winners fill from the competition import post-judging (Rules Nov 5–18; winners ~Nov 19 / week of Nov 23) |

## D0 atoms — Delphi Oracle (Weekend Challenge: Give your Agent a Tool)

| # | Atom | Fleet verdict | Pointer |
| --- | --- | --- | --- |
| D0-1 | The starting agent, documented | HELD | Decider gate + receipt semantics at the repo pin; receipts reproduced on a fresh clone |
| D0-2 | The one new tool + why | HELD | `fetch_evidence`; the evidence-trust argument verbatim in the landing copy |
| D0-3 | At least one AWS service | **SHAPE-ONLY (the D0 gap of record)** | Lambda packaging unit — runs locally, no AWS account; the spec's honesty line stands. NOT closable retroactively (the window closed Oct 26); its forward closure is D1's production span (D1-5) + the #4534 live proof discipline |
| D0-4 | Demo video < 3 min, public, before/after | HELD | AZSeqOI5H9M — 107.1s, Public |
| D0-5 | Previously unpublished | HELD | built in-window (PR #1702 `aa110a5e`); first published as the completion record 2026-11-02 |
| D0-6 | Submission itself | **NONE — LOST** | window closed before completion; $200 booked lost (OC-002/OC-005); owner ruled complete-anyway 2026-10-27 |
| D0-7 | Artifact set 4/4 | HELD + RE-VERIFIED | repo pin `393e1f4b…` · release v1.0.0 id 432016830 · video · landing LIVE; D0 seat re-verified the release firsthand 2026-11-03 |
| D0-8 | Outcomes import (5 winners × $200) | **NOT_ESTABLISHED at this pass** | gap research below |
| D0-9 | Prerequisite wiring into D1 | HELD | gate + tool vendored verbatim in D1's `foundation/`; disclosed in D1's article |

## Gap research (only the gaps were researched)

**D0-8, winners.** Firsthand read of the official event page
(2026-11-03, this cycle): requirements + rubric confirmed verbatim
against the spec (including the expanded criterion text the spec
carries in short form) — and **no winners are named on the About
surface**. A winners-announcement search found no announcement;
the venue's pattern on sibling challenges is notification by email
plus an updated article. Verdict: **NOT_ESTABLISHED / no-surface
yet** — resolution path = the event's Projects surface + recap
watch, i.e. the podium-crawl class of tooling under an OSINT
charter; filed in the cycle's capture issue. Nothing was
inferred, averaged, or filled.

**Field calibration (materials-grade, from the same search):** the
visible top of D0's field ran the deployed shape — e.g. a
rain-alert Strands entry on Bedrock AgentCore with ONE DynamoDB
tool, least-privilege IAM (`dynamodb:Query` on two partitions),
and measured before/after (streak mentions 0/6 → 6/6, n=9/side).
That is the standard D0-3's shape-only leg is measured against,
and the standard D1's production span (D1-5) is built to. Cited as
field evidence, not as a winner claim.

**D1-13, the last mechanical gap:** closed during the cycle
itself (sync parity, above) — the gathered set reflects the
post-fix state.

## Gathered set — D1 (ranked; IN HAND vs GAP)

**Materials** (evidence/docs the entry must hold):
1. IN HAND — the published project + confirmation ref; the LIVE
   article; both rubric frames verbatim (spec).
2. IN HAND — the proof chain: demo-run receipts · emulator-gate
   attempt-4 PASS · device PASS recordings · parity matrix.
3. IN HAND — the freeze record machinery: snapshot workflow
   (proven), re-armed; TEST PRIOR settlement merged.
4. IN FLIGHT — the #4534 live-model receipt (the one proof that
   turns "agent built with the SDK" from code-reading into a
   stamped live execution).
5. IN VERIFY — the #4537 AWS schema set (production-span
   credibility for the Rules frame's 15% "Use of Strands + AWS").
6. GAP (scheduled) — the v1.0.0 freeze record itself (Nov 4 line).

**Skills** (competency → fleet home):
1. Strands agent construction + tool discipline → the D1 seat's
   build record (`agent.py`, vendored-kernel pattern).
2. Verification-before-relay (firsthand reads, blob parity) →
   this seat + the D1 seat's independent re-read gate.
3. Release/sync automation (release-cut · machine sync ·
   snapshot) → this seat's lanes, all workflow-resident.
4. Evidence capture (device recordings, header-crop rule,
   emulator gate) → the #4283 harness + owner device leg.

**Tools** (named stack, by fit):
1. strands-agents 1.63.0 + the fleet Gemini route (proof) /
   Bedrock-first config (span) — provider as data.
2. GitHub Actions as the execution home (gate · cuts · sync ·
   snapshot · proof) — per the owner's ACTIONS rule.
3. resync_parity.py (blob-SHA parity) — the sync gate.
4. EpubCheck + the EPUB evidence workflow — the eReader leg.
5. podium_crawl.py — held for the D1-16 import (post-judging).

## Gathered set — D0 (ranked)

**Materials:**
1. IN HAND — the 4/4 artifact set (repo pin · release · video ·
   landing), re-verified 2026-11-03.
2. IN HAND — the completion record itself (this spec): the
   not_submitted state + the $200 loss, first-class.
3. GAP — the winners import (D0-8): NOT_ESTABLISHED; resolution
   path + window in the capture issue.

**Skills:**
1. Deterministic-gate design (fail-closed, stamped receipts) →
   the Delphi/D0 seat lineage; inherited by D1 verbatim.
2. Honest-shape recording (shape vs deployed fact) → the Desk's
   spec discipline, now the slate's template.

**Tools:**
1. The vendored kernel (`strands_oracle_mvp`) — the reusable
   asset; D1 is its second production use.
2. podium_crawl.py + the OSINT template — the import machinery
   for D0-8 when the venue publishes.

## Capture filings

One capture issue carries this cycle's gaps: D0-8's import leg
(charter + Projects-surface crawl when the winners publish) and
the standing note that D0-3 closes forward-only through D1's
span. D1-16's import is scheduled by the judging calendar, not
filed as a defect.
