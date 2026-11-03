# D0 OPPORTUNITY SPEC — Weekend Challenge: Give your Agent a Tool

**Entry:** D0 · **Project:** Delphi Oracle · **Artifact repo:** timerloggedout-spec/delphi-oracle
**Spec assembled:** 2026-11-03, by the Contribution Desk ([MUSEai]@{role:{challenge-entries-manager}}) from the D0 seat's record of record (official page reads 2026-10-26/10-28, landed in `ops/challenge/coordinator.json` via PR #2240; release API re-verified firsthand by the seat 2026-11-03). Requirements verbatim, cited; our state mapped per artifact at current state. **The honest center of this spec: D0 was never submitted — see Submission state. This artifact is a completion record and the prerequisite layer of D1's proof chain, and it says so.**

## Event of record

- **Name:** Weekend Challenge: Give your Agent a Tool — AWS Builder Center (Amazon Web Services).
- **Event URL:** https://builder.aws.com/build/hackathons/2e275689-b202-316e-93b8-10cd6d6d1e4a/weekend-challenge-give-your-agent-a-tool (challenge id 2e275689-b202-316e-93b8-10cd6d6d1e4a).
- **Window:** October 23, 2026 12:00 AM – **October 26, 2026 1:00 PM PDT** (8:00 PM UTC). Registration joined 2026-10-23 23:40 PDT.
- **Prizes:** pool $1,000 total award value — top 5 projects × ($100 AWS Promotional Credits + AWS Builder Backpack), each award valued $200 (credits subtotal $500). Ledger of record: OC-002, corrected by OC-005 — D0 LOST $200.

## Requirements — VERBATIM, cited

Source: the official event page (read 2026-10-28; coordinator record PR #2240):

> "Open to builders 18 or older with a Builder Center profile. See Rules for country and employee exclusions."

> "Submit a previously unpublished project that includes: The agent you started with and what it could already do"

> "The one new tool you added and why you picked it"

> "At least one AWS service as part of the agent or tool"

> "In the "demo" field of your project submission, include a link to a short (less than 3 minute) public video (e.g. YouTube, Vimeo, Facebook), showing what your agent can do now that it could not do before"

## Gates (as officially described; record 2026-10-26)

- **Gate 1** — AI + human scoring ⇒ top 50 advance.
- **Gate 2** — judge panel picks **5 winners**.
- Named checkpoint dates beyond the Oct 26 close: NOT_ESTABLISHED in the record (coordinator gates[] empty; judges never publicly named in-window).

## Scoring — official rubric

4 × 25% — **technical innovation · craft · usefulness · storytelling**.

## Submission mechanics + OUR SUBMISSION STATE

Mechanics: a Builder Center project submission (project form, including the demo field carrying the video link).

**Our state: submission = NONE. confirmation_ref = null.** The window closed October 26, 1:00 PM PDT before the entry completed. The owner ruled 2026-10-27: complete-anyway, as a completion record only. Outcome: not_submitted ⇒ $0 won; the $200 single-award value is booked as the loss (ledger above). Nothing in this spec dresses the completion record as a submission.

## The project as built (completion record)

**Delphi Oracle** — a Strands Decider agent (deterministic MVP kernel, `strands_oracle_mvp`): a deterministic evidence gate that judges a proposed action against an evidence set and returns ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE, failing closed. Built first in the monorepo (package PR #1702 merged aa110a5e), then ported byte-identical to its own repo.

- **The starting agent:** the mandate-practice Decider — asserted-evidence judging with stamped receipts.
- **The ONE new tool:** `fetch_evidence` — read-only artifact retrieval that assembles provenance-, freshness- and hash-stamped evidence sets. Why: the gate's trust problem — a judgment is only as good as the evidence it rests on, and asserted evidence is a claim, not a set.
- **The AWS-service-shaped component:** a Lambda packaging unit. **Honesty line of record: it runs locally — no AWS account was used.** The packaging is Lambda-shaped; no deployed AWS service is claimed.
- **Receipts of record:** asserted evidence only → ABSTAIN · a fetched pull request (103 stamped items) → ALLOW_RECOMMENDATION · a credential-mutation request → ESCALATE even with material evidence.

## Artifact map — CURRENT state (the D0 surface set)

| Artifact | State | Evidence pointer |
|---|---|---|
| Repo | Pinned at `main` HEAD **393e1f4b9f7f50da98fbfc0615041db3eebeb75d** (byte-identical port of the PR #1702 package) | Fresh-clone verification: pytest 5/5 · lambda smoke 200 ABSTAIN · demo receipts reproduced exactly |
| Release | **v1.0.0**, id **432016830**, published 2026-11-02T22:01:33Z; target_commitish "main" @393e1f4b at cut; **release notes carry the submissions=0 honesty line** | https://github.com/timerloggedout-spec/delphi-oracle/releases/tag/v1.0.0 (API re-verified 2026-11-03) |
| Video | `delphi-oracle-walkthrough.mp4` — 107.1s · 1280×720 · 2,340,102B; **YouTube AZSeqOI5H9M**, Public, published 2026-11-02 ~20:58 PT (channel LoggedOut Timer); mp4 + cover.png retained in the landing repo as durable master | https://www.youtube.com/watch?v=AZSeqOI5H9M — 107.1s < the 3-minute requirement |
| Article / landing | https://timerloggedout-spec.github.io/delphi-oracle/ — LIVE, served-verified | Copy PR #12 b37e60f98c72 · upgrade fold PRs #24 b9e707a0f70e · #25 3e0dd264a1c9 · #26 1275bdb4e579 (story copy verbatim) · #27 d07ff27f128b (YouTube embed) |
| Close stamp | **DELPHI UPGRADE closed 4/4 on 2026-11-02** (repo · release · video · landing) | Desk-feed close stamp PR #4071 merged df86607c4b1d |

## Proof obligations — requirement × our evidence

| # | Requirement (verbatim short form) | Proof of record |
|---|---|---|
| 1 | "The agent you started with and what it could already do" | The Decider gate + its receipt semantics, in the repo at the pin; demo receipts reproduced on a fresh clone |
| 2 | "The one new tool you added and why you picked it" | `fetch_evidence` in the repo; the why = the evidence-trust argument, stated in the landing copy verbatim; the three receipts above demonstrate the before/after |
| 3 | "At least one AWS service as part of the agent or tool" | The Lambda packaging unit — **with the honesty line: packaging-shaped, runs locally, no AWS account, no deployed service claimed.** This is the one requirement the completion record meets in shape rather than in deployed fact, and the spec records it that way |
| 4 | Demo-field video, "<less than 3 minute", public, "showing what your agent can do now that it could not do before" | AZSeqOI5H9M — 107.1s, Public; the walkthrough demonstrates the fetched-evidence judgment the starting agent could not make. (Landed Nov 2 — part of the completion record, after the window; not a submission) |
| 5 | "previously unpublished project" | Built in-window (package PR #1702); first published as the completion record on 2026-11-02 |

## D0 in D1's proof chain (the owner's wiring note)

D1 (StudySprint) extends this agent: the gate and `fetch_evidence` are vendored **verbatim** in StudySprint's `foundation/`, and D1's article discloses the starting agent in its own section. D0 is therefore D1's prerequisite layer — its completion record (this spec + the 4/4 artifact set) is part of D1's provenance evidence. D1's Opportunity Spec: `entries/d1-studysprint/OPPORTUNITY-SPEC.md`.
