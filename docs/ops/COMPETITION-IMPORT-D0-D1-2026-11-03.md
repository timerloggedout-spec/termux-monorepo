# Exact competition import — D0 + D1 (2026-11-03)

*OSINT-template-shaped import (receipted rows, gap-species stamps),
run by the optimizations-assurance seat on owner order via main
("Who won D0? What were the top placements?"). Sources are the
official venue surfaces, read firsthand 2026-11-03. Where sources
conflicted, the conflict is recorded and resolved on the strongest
read — never averaged, never silently overwritten.*

## D0 — Weekend Challenge: Give your Agent a Tool (CONCLUDED Oct 26)

Venue: AWS Builder Center · event `2e275689-b202-316e-93b8-10cd6d6d1e4a`.

| Field | Imported value | Receipt |
| --- | --- | --- |
| Scoring | 4 × 25% — technical innovation and originality · craft and execution · usefulness and impact · creativity and storytelling (expanded text read verbatim) | {source_url: the event About page, captured_at_utc: 2026-11-03T18:34Z, method: text fetch, quote_or_locator: "How entries are judged" section} |
| Entries — joined | **252 participants** | {source_url: event page header, captured_at_utc: 2026-11-03T18:36Z, method: live browser read, quote_or_locator: page state line "252 participants"} |
| Entries — submitted projects | **30 projects** (fully enumerated; Load-more exhausted) — first "ScamScope - Teaching a phishing agent to verify links, not guess" · last "An IAM-Unforged Story: One IAM Role, Zero Forged Certificates" | {source_url: event Projects tab, captured_at_utc: 2026-11-03T18:36Z, method: live browser enumeration (10 → 20 → 30, Load-more disabled at end)} |
| Entries — drift note | podium dataset v1 (Recruitment) counted a field of **40** at an earlier as_of. Both reads stand; the delta (40 → 30) is drift-class (post-close unpublishing is the plausible mechanism, NOT established) and is flagged to the dataset owner for v2 — never merged into one number | dataset v1 stamp + this import |
| Awards | 5 × ($100 AWS Promotional Credits + AWS Builder Backpack), each valued **$200**; pool $1,000 | {About Awards section, 2026-11-03T18:34Z, text fetch} — **conflict resolved:** one automated browser pass reported tiered values ($200/$150/$100/$50/$50); the direct page read + the coordinator record both show the uniform $200 award ×5. The tiered reading is rejected on the triple-check and recorded here so it is not re-imported |
| Judges | **POOL_UNRESOLVED** — never publicly named in-window (coordinator record); no panel names on any surface read | spec + About/Projects/Discussion reads |
| Placements · winners | **NOT_ESTABLISHED — species: UNPUBLISHED-on-venue** | checked 2026-11-03: About (no winner names) · Projects (no badge/label on any of the 30) · Discussion (no winner post) · no announcement linked from the event page · winners-announcement web search (no result). Gate 2 selected 5 winners by design (About, verbatim); the venue simply has not published them on any surface reachable today. Resolution path + window: the venue's publication (sibling-challenge pattern: email + updated article); re-check leg held in capture issue #4547 |
| Our outcome | not_submitted ⇒ $0 won; $200 booked LOST (independent of this import) | D0 spec, submission state |

**The owner's question, answered exactly:** who won D0 cannot be
imported today because the venue has not published it — that is a
finding about the venue's surfaces, receipted above, not a gap in
the hunt. The moment the venue posts placements, the capture
leg (#4547) fills them from receipts.

## D1 — Strands SDK: Workshop to Ship (LIVE; window closes Nov 4 23:59 PT)

Venue: AWS Builder Center · event `8311dcb5-1ece-3d62-a441-2e1c2ad90b86`.

| Field | Imported value | Receipt |
| --- | --- | --- |
| Scoring | BOTH frames, verbatim, labeled by page: About 4×25 (social impact · technical execution · communication quality · originality) · Rules 35/25/15/25 (Functionality · Innovation and creativity · Use of Strands Agents SDK and AWS · Originality) | D1 spec, Scoring section (About + Rules tab reads, 2026-11-03) |
| Entries (field) | **PENDING — enumeration method proven, window still open.** The count is taken at the freeze (Nov 5) by the same Load-more enumeration proven on D0's Projects tab today; counting mid-window would stamp a moving number as final | method receipt: D0 enumeration above |
| Placements · winners | PENDING-JUDGING — Rules judging Nov 5–18; winners on/about Nov 19 (Rules) / week of Nov 23 (About). Imported when published, same receipts discipline | D1 spec, Outcomes (held open) |
| Judges | "a panel of AWS experts" (About) — no named persons published | D1 spec, Gates |
| Our entry | published 2026-11-03 · confirmation `project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint` | D1 spec, coordinator record |

## Dataset feed

Rows for the podium dataset (Builder Center = a new venue family
in the venue map), handed to the dataset owner (Recruitment lane)
for their versioned file — this import does not write their
dataset directly:

- venue `builder-center/weekend-challenge-give-your-agent-a-tool`
  (D0): field_joined 252 · field_projects 30 (as_of 2026-11-03;
  drift vs the v1 count of 40 recorded) · podium_n = 5 by design ·
  podium identities **UNPUBLISHED** · judges POOL_UNRESOLVED.
- venue `builder-center/strands-sdk-workshop-to-ship` (D1):
  field PENDING (freeze enumeration) · podium_n = 3 by design ·
  identities PENDING-JUDGING.
