# D1 OPPORTUNITY SPEC — Strands SDK: Workshop to Ship

**Entry:** D1 · **Project:** StudySprint · **Artifact repo:** timerloggedout-spec/studysprint
**Spec assembled:** 2026-11-03, by the Contribution Desk ([MUSEai]@{role:{challenge-entries-manager}}) from the coordinator record + firsthand reads of the event surfaces. **Amended 2026-11-03 (owner order): requirements verbatim from the official surfaces with citations — no paraphrase — and every requirement joined with our current surface state, pulled from the live parity matrix + release record, not from packet language.** Where the event's own surfaces differ, both frames are recorded and labeled by surface — never blended.

## Event of record

- **Name:** Strands SDK: Workshop to Ship — hackathon on AWS Builder Center.
- **Event URL:** https://builder.aws.com/build/hackathons/8311dcb5-1ece-3d62-a441-2e1c2ad90b86/strands-sdk-workshop-to-ship
- **Window:** October 28 – November 4, 2026 (see the Rules citation below for the exact Submission Period).
- **Prizes (About page):** three winning projects, each $5,000 in AWS Promotional Credits + an AWS Builder swag bundle (~$600) + an official winner's certificate. Total pool $16,800. Ledger of record: OC-003/OC-006 — D1 AT_RISK $5,000 (first-place-only basis).

## Requirements — VERBATIM, cited

**Source A — the event About page** (https://builder.aws.com/build/hackathons/8311dcb5-1ece-3d62-a441-2e1c2ad90b86/strands-sdk-workshop-to-ship, read 2026-11-03):

> "Open to builders 18 or older with a Builder Center profile. See Rules for country and employee exclusions."

> "Complete the free Strands SDK workshop on Builder Center during the hackathon window (October 28 to November 4). Workshop completion is required to qualify."

> "Your project submission must include:
> 1. An agent built with the Strands Agents SDK that addresses a real-world social good challenge.
> 2. A project article on Builder Center describing the agent, what it does, and the social good problem it addresses.
> 3. A link to a public repository with the agent's source code.
> 4. A short, publicly available demo video, under three minutes, showing the agent working.
> 5. An original agent that has not been published before."

Focus areas named on the About page: Education · Health · Climate resilience.

**Source B — the event Rules tab** (same event URL, ?tab=rules, read live signed-in 2026-11-03):

> Submission Period: October 28, 2026 at 12:00 a.m. PT through "November 4, 2026, at 11:59 p.m. Pacific Time"; "Entries submitted after this deadline will not be accepted."

> "Judging Period: November 5-18, 2026"; winners announced "On or about November 19, 2026."

The Rules require a public GitHub repository and a published Builder Center project with a live demo or deployed link (exception if the project cannot be deployed), and state that projects failing the requirements will not be eligible.

**Source C — platform mechanics** (AWS Builder Center's official hackathon documentation, "Introducing Hackathons on AWS Builder Center", builder.aws.com, Sep 18 2026):

> "Publishing is submitting. … Projects stay editable up to the end date. … Publish early and keep editing."

> "At the end date, everything freezes for judging."

Also of record from Source C: only the team leader can edit or delete the project; a draft left unpublished when the hackathon ends cannot be published afterwards and cannot win an award; the repository is linked (GitHub or GitLab), not snapshotted — repo work pushed before the freeze is what the frozen project's link serves.

## Gates

- **Gate 1 — AI and human scoring** (About: "Gate 1, AI and human scoring: every qualifying submission is scored on the rubric below. The top 50 submissions advance." — week of November 9; Rules Judging Period: November 5–18).
- **Gate 2 — human judging** (About: "Gate 2, human judging: a panel of AWS experts reviews the shortlist and selects the winners." — week of November 16).
- **Winners announced:** About — week of November 23; Rules — on or about November 19. (Both frames recorded; the surfaces differ.)

## Scoring — VERBATIM, both frames labeled by page

**About page rubric:**

> "Social impact (25%): how clearly the project delivers measurable improvement for underserved populations…"
> "Technical execution (25%): how well the agent is built with the Strands Agents SDK and how well it works."
> "Communication quality (25%): how clearly the project article and video explain the agent, the problem, and what you learned…"
> "Originality (25%): the originality of the agent architecture, novel use of AWS services, and how far the project extends beyond the lessons in the workshop."

**Rules tab criteria:** Functionality **35%** · Innovation and creativity **25%** · Use of Strands Agents SDK and AWS **15%** · Originality **25%**.

## Submission mechanics (from Sources B + C, verified against the live editor 2026-11-03)

A project takes: title (≤255 chars) · description (≤512) · body (rich text) · cover image (1200×675 recommended, ≤2 MB) · up to 5 tags · repository link · endpoint/live-demo link · optional notebook link. Work saves automatically. Publish = submit; editable until the end date; frozen at the end date for judging.

## Our submission (coordinator record)

- **Published 2026-11-03 ~10:01 PT** under the owner's publish-today ruling (post-publish editability verified firsthand the same day; the Oct-30 submit-on-due-day timing was superseded by that ruling).
- **Confirmation ref:** https://builder.aws.com/project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint — first entry on the hackathon Projects tab at publish.
- **Article:** LIVE since 2026-10-30 — https://builder.aws.com/content/3LRJhGucOZfz9ydzFax8sD2p5yB
- **Repo:** https://github.com/timerloggedout-spec/studysprint · **Endpoint:** https://timerloggedout-spec.github.io/studysprint/webapp/0.1.0/ · **Demo video:** https://www.youtube.com/watch?v=WK9LMwpvHUk (2:54).
- **Tags as published:** agents · strands · educational · machine-learning · trust-policy (the editor's vocabulary lacks the packet's education/study-planning/trust verbatim — nearest matches, of record).
- **Record integrity note (honest, of record):** the first publish's session substituted body content (invented workflow-run links, a wrong endpoint, rewritten release narratives). The D1 seat's verification FAILED that record; a verbatim replacement of the body is executing on the open line under a no-improvisation order with a rendered-page read-back, and the D1 seat's independent re-verification is the gate (pending at spec time). The correction cycle is part of this entry's record (PR #4530), not edited out of it.

## Surface map — CURRENT state (pulled 2026-11-03)

Source: `apps/studysprint/evidence/PARITY-MATRIX.md` @ master (ground truth: shipped bindings read from the surfaces' own builders, core **v0.5.0**, surface line **0.2.0** in-tree) + the release record. In-tree state and released state are never conflated: a version is "released" only with a release of record.

| Surface | Version (released · in-tree) | State | Evidence pointer |
|---|---|---|---|
| CLI / core (foundation) | **v0.5.0** (release id 432649080 @ 71a876f5b518) | All capabilities bound (§1–§1d incl. calendar/geo, memory methods, multi-course, hardening) | PARITY-MATRIX "CLI/core" column = bound ∀ rows; suite of record |
| webApp | **0.1.0** released (webapp-v0.1.0 id 432558838; LIVE at the endpoint URL) · 0.2.0 in-tree (it-1 merged, PR #4485) | 0.2.0 bindings: plan/trust/Today bound · check-in bound · SR bound · Reader bound · intake bound (photos = awaiting-core-ocr, disclosed) · §1b partial · §1d calendar+geo **bound** (build-time state, disclosed) · §1c + hardening absent · .apkg/Obsidian export absent | Matrix rows §1–§1d; headless captures in-tree. **Served caveat:** the GitHub Pages pipeline has been erroring since 17:13Z (GitHub-side, repo exonerated); the endpoint serves the last-good 16:52Z build meanwhile |
| TUI | **0.1.0** released (tui-v0.1.0 id 432554871) · 0.2.0 in-tree | **Device PASS at 0.1.2** (owner recording: header 0.1.2 · ∀7 tabs · Export executed; 0.1.2 shipped in-tree, no separate release cut) · 0.2.0: SR bound (real `review_card`) · exports **bound** (Export tab: .apkg + Obsidian) · intake bound (real `ingest_any`, confirm-gated) · §1d Calendar + Routes panes bound | Evidence PR #4427 (TUI PASS note + recording); matrix TUI column |
| APK | **0.1.3** released (apk-v0.1.3 id 432963080, asset studysprint.apk 46,249B) · 0.2.0 in-tree | **Device PASS at 0.1.3** (owner recording 2026-11-03: Today populates from state · SR grades · footer "surface version 0.1.3") · emulator gate attempt-4 **PASS** (run 41670971342; repro on 0.1.0 RED) · #4276 CLOSED both legs | Evidence PR #4459; release-cut run 41676818123 |
| eReader / EPUB | — (no version line, by ruling) | **Spec'd, not yet shipped:** EREADER-SPEC (PR #4463, D1-ruled: EPUB-as-export · cited-text terms chapter · `studysprint-reader.epub` rides the TUI release via release-cut) · build queued as issue #4472 | apps/studysprint/EREADER-SPEC.md |
| Obsidian (export surface) | rides the generating surface's version | **Bound** on CLI/core + TUI (Export tab) · absent on webApp + APK (per matrix) · part of the export family {.apkg · Obsidian · EPUB(pending)} | Matrix "SR exports" row |

**Snapshot + proof machinery (current):** the submission-snapshot workflow (issue #4490) is built + merged in the ss repo (PR #1, 0758026b3925); its proving run is **verified** (annotated tag + prerelease 433064353 + MANIFEST {HEAD · tree · suite 125/126 with the known ss-layout failure stamped} + 45 MB source archive; publish-on-red + loud-failure both proven); the rehearsal artifacts are **re-armed away** (deleted + verified absent at the desk) so the scheduled run captures the v1.0.0 state on Nov 5 06:30 UTC. The known ss-layout test settles as a conditional skip (issue #4538, D1-ruled) before the v1.0.0 cut. Model-access proof: workflow + harness merged (PR #4535, 31c5c98719bf); the live run's receipt is pending at spec time. AWS schema set: filed as issue #4537, in build.

## Proof obligations — requirement × our evidence

| # | Requirement (verbatim short form) | Proof of record |
|---|---|---|
| 1 | "An agent built with the Strands Agents SDK" (social good — Education) | Repo `agent.py` — `build_strands_agent` registers the 7 tools on a Strands `Agent` · **workshop completion** in-window (2026-10-30, all seven modules, incl. AgentCore Runtime deployment) · **model-access proof** (#4534: strands-agents 1.63.0, live model invocation, tool metrics asserting `fetch_syllabus_evidence` ∧ `make_plan` — receipt pending at spec time) · **AWS schema set** (#4537, in build: runtime/tool/receipt/deployment/endpoint schemas, golden-instance validated) |
| 2 | "A project article on Builder Center…" | The LIVE article (above) + the identical write-up in the published project's Body |
| 3 | "A link to a public repository…" | The public repo + release record (core v0.5.0 · apk-v0.1.3 · webapp-v0.1.0 · tui-v0.1.0) + the surface map above + the **submission-freeze snapshot** at the deadline (#4490) |
| 4 | "A short, publicly available demo video, under three minutes…" | WK9LMwpvHUk — 2:54, public, embedded in the project via the editor's YouTube tool |
| 5 | "An original agent that has not been published before" | Provenance: built in-window on the disclosed D0 starting agent (below); the article states the extension plainly |
| — | Rules: live demo / deployed link | The endpoint field serves the live webApp (version URL of record; served-state caveat in the surface map) |

## D0 as the prerequisite layer (owner's wiring note)

StudySprint **extends the D0 starting agent, the Delphi Oracle**: its deterministic evidence gate (ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE, failing closed) and its one tool, `fetch_evidence`, are vendored **verbatim** in the repo's `foundation/`; StudySprint's new tool `fetch_study_evidence` domain-shifts the same loop to syllabus + practice-set evidence. The submission discloses this in the article ("The starting agent, and what it already did"). D0's own Opportunity Spec is the companion artifact (`entries/d0-delphi-oracle/OPPORTUNITY-SPEC.md`) and is part of this entry's proof chain.

## Open line at spec time (to the Nov 4 23:59 PT freeze)

Published-body correction re-verify → v1.0.0 cut on the richest green tree (it-1 0.2.0 in-tree; 0.2.0 surface cuts pending the sync-parity repair) → v1.0.0 Update block into the Body → the live article's currency edit → frozen-state verification at the freeze → Gate 1 (week of Nov 9).
