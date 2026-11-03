# D1 OPPORTUNITY SPEC — Strands SDK: Workshop to Ship

**Entry:** D1 · **Project:** StudySprint · **Artifact repo:** timerloggedout-spec/studysprint
**Spec assembled:** 2026-11-03, by the Contribution Desk ([MUSEai]@{role:{challenge-entries-manager}}) from the coordinator record + firsthand reads of the event surfaces (About + Rules tabs, live, 2026-11-03). Where the event's own surfaces differ, both frames are recorded and labeled by surface — never blended.

## Event of record

- **Name:** Strands SDK: Workshop to Ship — hackathon on AWS Builder Center.
- **Event URL:** https://builder.aws.com/build/hackathons/8311dcb5-1ece-3d62-a441-2e1c2ad90b86/strands-sdk-workshop-to-ship
- **Window:** October 28 – November 4, 2026. Rules (Submission Period): Oct 28, 2026 12:00 a.m. PT through **November 4, 2026, 11:59 p.m. Pacific Time**; "Entries submitted after this deadline will not be accepted."
- **Prizes (About):** three winning projects, each $5,000 in AWS Promotional Credits + an AWS Builder swag bundle (~$600) + an official winner's certificate. Total pool $16,800. Ledger of record: OC-003/OC-006 — D1 AT_RISK $5,000 (first-place-only basis).

## Requirements (as officially stated)

**Eligibility + qualification (About):** open to builders 18 or older with a Builder Center profile (Rules carry country and employee exclusions). **Workshop completion is required to qualify:** complete the free workshop "Building AI Agents with Strands SDK: From Simple Loops to Multi-Agent Swarms" on Builder Center during the hackathon window (request a free sandbox environment, then complete it).

**The project submission must include (About):**
1. An agent built with the Strands Agents SDK that addresses a real-world social good challenge — focus areas: **Education**, Health, Climate resilience.
2. A project article on Builder Center describing the agent, what it does, and the social good problem it addresses.
3. A link to a public repository with the agent's source code.
4. A short, publicly available demo video, **under three minutes**, showing the agent working.
5. An original agent that has not been published before.

**Rules tab adds:** a public GitHub repository and a published Builder Center project with a live demo or deployed link (with an exception if the project cannot be deployed); projects failing the requirements will not be eligible.

## Gates

- **Gate 1 — AI and human scoring** (About: week of November 9; Rules: Judging Period November 5–18, 2026): every qualifying submission is scored on the rubric; **the top 50 submissions advance**.
- **Gate 2 — human judging** (About: week of November 16): a panel of AWS experts reviews the shortlist and selects the winners.
- **Winners announced:** About — week of November 23; Rules — "On or about November 19, 2026." (Both frames recorded; the surfaces differ.)

## Scoring — both official frames, labeled by surface

**About page rubric (4 × 25%):** Social impact 25% · Technical execution 25% · Communication quality 25% · Originality 25%.

**Rules tab criteria:** Functionality **35%** · Innovation and creativity **25%** · Use of Strands Agents SDK and AWS **15%** · Originality **25%**.

## Submission mechanics (verified firsthand, 2026-11-03)

Source: AWS Builder Center's official hackathon documentation ("Introducing Hackathons on AWS Builder Center") + the live Rules tab + the live project editor.

- Publishing is submitting. A project takes: title (≤255 chars) · description (≤512) · body (rich text) · cover image (1200×675, ≤2 MB) · up to 5 tags · a GitHub/GitLab repository link · an endpoint/live demo link · an optional notebook link. Work saves automatically; only the team leader can edit or delete the project.
- **Projects stay editable up to the end date** — "Publish early and keep editing." At the end date, **everything freezes for judging** and projects lock.
- The repository is referenced by URL; the platform does not snapshot it. Repo work pushed before the freeze is what the frozen project's link serves.
- A draft left unpublished when the hackathon ends cannot be published afterwards and cannot win an award.

## Our submission (coordinator record)

- **Published 2026-11-03 ~10:01 PT** under the owner's publish-today ruling (post-publish editability verified firsthand the same day; the Oct-30 submit-on-due-day timing was superseded by that ruling).
- **Confirmation ref:** https://builder.aws.com/project/3LRJu2KZOWsFqd5oGHyt52lcR5P/studysprint — first entry on the hackathon Projects tab at publish.
- **Article:** LIVE since 2026-10-30 — https://builder.aws.com/content/3LRJhGucOZfz9ydzFax8sD2p5yB
- **Repo:** https://github.com/timerloggedout-spec/studysprint · **Endpoint:** https://timerloggedout-spec.github.io/studysprint/webapp/0.1.0/ · **Demo video:** https://www.youtube.com/watch?v=WK9LMwpvHUk (2:54).
- **Record integrity note (honest, of record):** the first publish's session substituted body content (invented workflow-run links, a wrong endpoint, rewritten release narratives). The D1 seat's verification FAILED that record; a verbatim replacement of the body is executing on the open line under a no-improvisation order with a rendered-page read-back, and the D1 seat's independent re-verification is the gate (pending at spec time). The correction cycle is part of this entry's record (PR #4530), not edited out of it.

## Proof obligations — what demonstrates each requirement is met

| # | Requirement | Proof of record |
|---|---|---|
| 1 | Strands-built agent, social good (Education) | Repo `agent.py` — `build_strands_agent` registers the 7 tools on a Strands `Agent`; **workshop completion** in-window (2026-10-30, all seven modules, incl. deployment to AgentCore Runtime); **model-access proof** (issue #4534: strands-agents 1.63.0 agent invoking a live model via the fleet Actions secret, tool metrics asserting `fetch_syllabus_evidence` ∧ `make_plan`, receipt artifact); **AWS schema set** for the production span (issue #4537: runtime/tool/receipt/deployment/endpoint schemas, golden-instance validated). |
| 2 | Project article | The LIVE article (above) + the identical write-up carried in the published project's Body. |
| 3 | Public repository | The repo (public) + its release record (core v0.5.0 id 432649080; surfaces incl. apk-v0.1.3 id 432963080) + **submission-freeze snapshot** at the deadline (issue #4490: annotated tag `submission-freeze-2026-11-04` + prerelease + MANIFEST {HEAD · tree · suite verdict/counts · timestamp}; proving run verified 2026-11-03). |
| 4 | Demo video < 3:00, public | WK9LMwpvHUk — 2:54, public, embedded in the project via the editor's YouTube tool. |
| 5 | Original, not published before | Provenance: built in-window on the disclosed D0 starting agent (below); the article states the extension plainly, as the event's honesty framing requires. |
| — | Live demo / deployed link (Rules) | The endpoint field serves the live webApp (version URL of record); CLI/TUI/Android builds ship in the repo releases. |

## D0 as the prerequisite layer (owner's wiring note)

StudySprint **extends the D0 starting agent, the Delphi Oracle**: its deterministic evidence gate (ALLOW_RECOMMENDATION / ABSTAIN / ESCALATE, failing closed) and its one tool, `fetch_evidence`, are vendored **verbatim** in the repo's `foundation/`; StudySprint's new tool `fetch_study_evidence` domain-shifts the same loop to syllabus + practice-set evidence. The submission discloses this in the article ("The starting agent, and what it already did"). D0's own Opportunity Spec is the companion artifact (`entries/d0-delphi-oracle/OPPORTUNITY-SPEC.md`) and is part of this entry's proof chain.

## Open line at spec time (to the Nov 4 23:59 PT freeze)

v1.0.0 cut on the richest green tree → a v1.0.0 Update block enters the project Body → the live article's currency edit → frozen-state verification at the freeze → Gate 1 (week of Nov 9).
