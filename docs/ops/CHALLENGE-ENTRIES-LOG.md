# Challenge Entries Log

Durable record of the fleet's challenge, hackathon, and proposal-call entries —
registrations, submissions, and prepared candidates — for
`timerloggedout-spec/termux-monorepo` and its public material.

**Rules of this log**

- Every entry carries its evidence. A fact without a source is logged as
  UNVERIFIED, never reconstructed from plausibility.
- A *registration* (joining a platform event) and a *submission* (an entry
  actually filed) are different states and are never conflated.
- Deadlines are recorded with their timezone, verified from the official page
  where possible; otherwise marked UNVERIFIED.
- Drafts are prepared automatically from existing public material. Actual
  third-party submission happens only when it needs no new account, no
  payment, and no owner-gated step, AND the challenge is one the owner has
  already entered or approved. Everything else surfaces to the owner as a
  prepared packet. AWS account creation is always owner-approved.
- Sweep cadence: weekly (Mondays, America/Los_Angeles) — a scheduled lane
  check re-scans the sources in §5, refreshes this log by PR when something
  changed, and reports new candidates. Log last verified 2026-10-26.

Builder identity used throughout: AWS Builder Center profile
[@1337dia590r1c8u1ldr](https://builder.aws.com/community/@1337dia590r1c8u1ldr),
display name "'Founders' are 'found' to implement.", created 2026-10-23.

---

## 1. Verified registrations (platform joins)

Evidence for all three: platform confirmation emails to the owner's Gmail
from `notifications@builder.aws.com` (message IDs cited).

| # | Event | Window (PT) | Joined (PT) | Evidence |
|---|-------|-------------|-------------|----------|
| R1 | Agent Experience Hackathon: Strands Decider (AWS Builder Center) | Oct 16 12:00 AM – Oct 23 11:59 PM PDT | 2026-10-23 17:27 | Gmail msg `1a16b4e87bbf0c55`; platform ID `4f50957c-1d08-37ab-b11c-97516b9adeb4` |
| R2 | Weekend Challenge: Give your Agent a Tool (AWS Builder Center) | Oct 23 12:00 AM – Oct 26 1:00 PM PDT | 2026-10-23 23:40 | Gmail msg `1a16ca3f96d0508c`; platform ID `2e275689-b202-316e-93b8-10cd6d6d1e4a` |
| R3 | Strands SDK: Workshop to Ship (AWS Builder Center) | Oct 28 12:00 AM – Nov 4 11:59 PM PDT | 2026-10-23 23:40 | Gmail msg `1a16ca3fb608dcf9`; platform ID `8311dcb5-1ece-3d62-a441-2e1c2ad90b86` |

Account creation itself is also verified: "Welcome to the AWS Builder Center
community", 2026-10-23 17:20 PT (Gmail msg `1a16b477c91e5b07`). The complete
set of Builder Center emails in the mailbox is five — welcome, the three join
confirmations above, and one "ends soon" reminder for R2 (2026-10-25 13:00 PT,
msg `1a174a6e288f140a`). There are no others.

## 2. Submission status — none verified

As of 2026-10-26, **zero submissions are verified for any of the three
registrations**, including R1 and R2, whose windows have closed. Sources
checked:

- **Gmail** — the full Builder Center set (above) contains join, welcome, and
  reminder mail only. No submission-confirmation, project-published, or
  article-published message exists.
- **This repo** — the fleet's own proposal manifest for the Strands Decider
  material states explicitly: "No AWS account, resources, invocation, or
  hackathon submission is claimed."
  (`docs/proposals/active/aws-free-tier-strands-delphi-oracle/MANIFEST.md`)
- **Platform public lists (read-only check, 2026-10-26)** — Weekend Challenge
  Projects tab loaded to exhaustion: 40 entries, none matching this profile;
  in-list searches for the handle and for "Founders" returned 0. Strands
  Decider Projects tab: same searches returned 0 (5,918 participants; list not
  exhaustively counted — the platform's own in-list search is the filter of
  record). Caveat: the public list view does not display author names, so the
  exclusion rests on the full title scan plus the platform's targeted search;
  no signed-in author view was used.
- **Web search** — no Builder Center article or project under this profile was
  found.
- **Builder profile state (observed 2026-10-26)** — default avatar, no bio.
  These challenges require a complete profile (image, country, About) for an
  entry to be valid, so even an unlisted submission would not have qualified
  as-is. **Owner item:** complete the profile before the next entry window.

**Discrepancy note.** The working assumption entering this log was "a few
entries." The evidence supports exactly three *registrations* and zero
*submissions*. If "entries" meant filed submissions, the verified count is 0,
not a few. Prepared material did exist — the Delphi Oracle RFP (PR #1611,
merged) and an offline Oracle MVP (PR #1620, open; intake hardening PR #1630,
open draft) — but per the manifest it was never submitted, and it records zero
external/AWS calls by design.

## 3. Candidate opportunities (deadline after 2026-10-26)

Ranked by fit. Fleet assets referenced: **(A)** Delphi Oracle — Strands
Decider decision-layer RFP + offline MVP (this repo:
`docs/proposals/active/aws-free-tier-strands-delphi-oracle/`,
`scripts/delphi/strands_oracle_mvp.py`); **(B)** Web Adapter Foundry
(`ops/web_adapter_foundry/`, `docs/ops/WEB-ADAPTER-FOUNDRY.md`); **(C)**
free-tier / mesh-resiliency engineering (device pull queue, quota systems);
**(D)** infrastructure CMDB / reconciliation design (PR #1655).

| # | Opportunity | Deadline (verified) | Entry requires | Gates | Fit |
|---|-------------|--------------------|----------------|-------|-----|
| C1 | Strands SDK: Workshop to Ship — AWS Builder Center. **Already joined (R3).** | Projects due **Nov 4, 2026**; platform email states 11:59 PM PDT (official page lists dates only — time UNVERIFIED on page) | Complete the free Strands SDK workshop in-window (hard qualifier); original unpublished Strands agent for social good (education / health / climate resilience); Builder Center article; public repo; demo video < 3 min | Builder profile; 18+; no purchase; no AWS account needed to enter | A — patterns reuse; entry itself must be new |
| C2 | Vultr Agent Rush Hackathon — Vultr × lablab.ai | Submissions end **Nov 8, 2026, 3:00 PM PST** (lablab official schedule) | Register on lablab.ai + join its Discord (both mandatory); teams 1–6; web agent that writes/runs code or operates a real browser, sandboxed on Vultr | Free; Vultr account for sandbox credits ($200 participant credit; no card spend to compete online) | **B** — strongest Foundry match |
| C3 | Builder.io Agent-Native Hackathon | Submit by **Nov 2, 2026, 11:59 PM PT** (official page) | Working app on Builder's Agent-Native framework; public Clips demo; project details; no registration | Free; worldwide; 18+ | A/D — human-in-the-loop decision-review UI |
| C4 | Kiroween 2026 — Kiro (AWS) on Devpost | Submissions Oct 30 1:00 PM PDT – **Dec 4, 2026, 2:00 PM PST** (Devpost dates page) | **New project built in-window** with Kiro; pre-existing projects ineligible; registration open now | Free; Kiro user ID **or** AWS account ID (Kiro ID suffices) | D/B — spec-first in-window build |
| C5 | PayPal AI Hackathon 2026 — Devpost | **Nov 12, 2026, 12:00 PM PT** — UNVERIFIED from the official page (corroborated across secondary listings) | Working prototype meaningfully integrating PayPal developer platform (free sandbox) + AI; public repo w/ license; demo video < 3 min; existing projects eligible with in-window updates | Free; Devpost + PayPal Developer sandbox accounts; regional exclusions apply | A — "Best Use of Agentic Commerce" category |
| C6 | Next AWS Builder Center Weekend Challenge | **Not yet published** (checked 2026-10-26). Recurring pattern from official October pages: opens Fri 12:00 AM PT, closes Mon 1:00 PM PT; November theme unannounced | Per pattern: Builder Center article (≥ 500 words, required sections, week tag) or comment-format entry; **complete Builder profile required for validity** | Builder profile only; no AWS account needed at entry | A/B — lowest-effort venue; fleet already writes this format |
| C7 | Lexsi AI Safety & Alignment Hackathon — Lexsi Labs × Cohere Labs | Nov 1–21, 2026 per secondary source — **UNVERIFIED** | ≥ 2 Lexsi toolkits with Cohere open-weight models; before/after measurements; artifacts on Hugging Face | Free; HF account | Weak — governance-adjacent tracks only |

Prizes (official pages): C1 — 3 × $5,000 AWS credits + ~$600 swag (pool
$16,800). C2 — $9,000 cash pool + $5,000 Vultr credits; $200 credits per
participant. C3 — $10,000 cash across 5 places. C4 — $100,000 cash pool. C5 —
$67,500+ incl. category awards. C6 — first 100 qualifying entries $100 AWS
credits each + 10 backpack draws (October pattern).

### Checked and excluded

- Strands Decider hackathon (R1) — closed Oct 23; Gate 1 scoring week of
  Oct 26, winners week of Nov 9. Watch for a second edition.
- Build, Ship, Shape: Amazon Developer Hackathon (Devpost) — closed
  Oct 23, 2026, 3:00 PM EDT.
- Google/Gemini — Gemini 3 Hackathon closed Feb 2026; XPRIZE winners already
  announced; a "Vibe Code with Gemini 3 Pro" contest appears on no official
  page — treated as noise.
- Microsoft — no open online agent hackathon for Nov–Dec 2026 (spring event;
  current listings are in-person EMEA labs).
- Anthropic "Built with Claude: Japan 2026" — applications close Oct 26,
  screened, Japan residents only.

## 4. Entry packets

**Owner decision (2026-10-26 23:41 PT): "ALL of them"** — D1, D2, D3, and D4
are all approved and in play. Integrated schedule (windows protected against
each other):

| When (PT) | Focus |
|-----------|-------|
| Oct 27–29 | D3 scaffold + core actions (build window open since Oct 19); D1 agent drafted locally, published in-window; D2 registration/sandbox recon |
| Oct 28 | D1 window opens — workshop completion (owner account) + agent repo goes public |
| Oct 30–Nov 1 | **D3 build weekend (concentrated)**; Kiroween window opens Oct 30 — no project creation (owner sequencing) |
| Nov 2 | D3 Clips demo + submit by 11:59 PM PT |
| Nov 3–4 | D1 finish: article, video, submission packet → owner submits by Nov 4 11:59 PM PDT; D2 registration + sandbox prep in parallel |
| Nov 5–8 | D2 build (lablab online build is Nov 3–8) → submit by Nov 8, 3:00 PM PST |
| After Nov 8 | D4 build (deadline Dec 4, 2:00 PM PST) |

**Standing blocker for every platform submission: the incomplete Builder
profile (§2).** It gates D1 directly and is the first blocker surfaced wherever
a submission path reaches an owner-account step.

### D1 — for C1, Workshop to Ship — IN PROGRESS (owner already joined)

- **Concept:** "Proof Before Help" — a climate-resilience agent (cooling-center
  / shelter router for extreme-heat events) whose consequential tool calls are
  gated by a Decider-style evidence check: the agent must cite a current,
  sourced fact (weather alert, facility status) before it may recommend or
  route, and escalates to a human-readable receipt when evidence is stale or
  conflicting. Directly reuses the Delphi decision-layer patterns (asset A) in
  a new, unpublished, social-good build, as the rules require.
- **Source packet (all public, this repo):**
  `docs/proposals/active/aws-free-tier-strands-delphi-oracle/` (RFP,
  EXPERIMENT-MATRIX, DEBATE); `scripts/delphi/strands_oracle_mvp.py` +
  `tests/fixtures/delphi_oracle_mvp.json` (PR #1620); free-tier recon
  `docs/ops/FREE-TIER-BACKEND-RECON-2026-10-21.md` (PR #1511).
- **Requirement checklist:** ☐ complete the free Strands workshop in-window
  (Oct 28–Nov 4) — hard qualifier, **owner account step**; ☐ new Strands
  Agents SDK agent in a public repo (build Oct 27–29, publish in-window);
  ☐ Builder Center article (draft in repo, posted under owner account);
  ☐ demo video < 3 min (script/storyboard in repo; recording is an owner
  step); ☐ complete Builder profile (§2 — **first blocker**).
- **Submission class:** submission itself happens under the owner's Builder
  account → prepared packet surfaces to the owner when ready; not
  auto-submittable.

### D2 — for C2, Vultr Agent Rush (Foundry entry) — IN PROGRESS

- **Concept:** the Web Adapter Foundry as a sandboxed browser-operating agent:
  given a target brief, the agent plans a bounded adapter probe, executes it
  in the Vultr sandbox, and returns an evidence envelope (what was fetched,
  what was refused, why) — the Foundry's existing registry/envelope/SSRF-barrier
  design running as the competition agent.
- **Source packet:** `ops/web_adapter_foundry/` (registry, envelope
  validation, bounded probe planner, HTTP/SSE facade), taxonomy
  `ops/web_adapter_foundry/taxonomy.json`, `docs/ops/WEB-ADAPTER-FOUNDRY.md`,
  `.agents/skills/web-adapter-foundry/SKILL.md`.
- **Requirement checklist:** ☐ lablab.ai registration + Discord join (owner
  approved 2026-10-26; account steps surfaced if they hit verification gates);
  ☐ Vultr account for sandbox credits (no-card path only — the card is a
  block); ☐ sandbox deployment of the facade (build Nov 5–8, prep earlier);
  ☐ demo per lablab format.
- **Submission class:** approved by owner; submission follows the standing
  boundary — any step needing a card or an owner-only verification is surfaced,
  never worked around.

### D3 — for C3, Builder.io Agent-Native Hackathon — IN PROGRESS (scoped 2026-10-26)

- **Verified from the official page (2026-10-26):** no registration required;
  build window open since Oct 19; final weekend Oct 30–Nov 1; submit by
  **Nov 2, 11:59 PM PT**; entry = working Agent-Native app + public Clips demo
  + project details. Judged shape: "an agent with a purpose; an interface that
  puts users in control; a connected experience" — UI and agent call the same
  actions, defined once with `defineAction()` (`@agent-native/core`, zod
  schemas, React UI).
- **Concept:** "Delphi Desk" — a human-in-the-loop decision-review cockpit. A
  Delphi-style agent panel drafts engineering decision proposals with evidence
  receipts (the fleet's Delphi Oracle pattern); every consequential move —
  approve, request changes, escalate, annotate, apply-with-conditions — is a
  shared `defineAction()` action callable identically by the human in the UI
  and by the agent. The human can edit a proposal, redirect the panel, and
  watch the decision ledger update; the agent revises in response. Data model
  mirrors the repo's own structures: proposals, evidence items, ballots, and a
  reconciliation ledger (Delphi DEBATE envelope + CMDB conflict matrix, PR
  #1655). This is a **new build** on the framework, seeded only with
  synthetic/public fixture data — not repurposed material.
- **Build plan:** Oct 27–29 scaffold, action set, seed fixtures, agent loop
  (deterministic panel locally, so the demo never depends on an API key);
  Oct 30–Nov 1 concentrated build (review flows, ledger, agent revision loop);
  Nov 2 polish, Clips demo, submit.
- **Open risk to verify during prep:** whether publishing a public Clips demo
  requires a Builder account — if it does, that step is owner-gated and gets
  surfaced immediately, not at the deadline.
- **Source packet:** `docs/proposals/active/aws-free-tier-strands-delphi-oracle/`
  (DEBATE.md envelope, EXPERIMENT-MATRIX), `scripts/delphi/strands_oracle_mvp.py`
  (receipt pattern), PR #1655 CMDB design (conflict matrix / reconciliation).

### D4 — for C4, Kiroween 2026 — REGISTERING (build sequenced after Nov 8)

- **Verified from the official page (2026-10-26):** registration open now;
  full rules publish and submissions open **Oct 30, 1:00 PM PDT**; deadline
  **Dec 4, 2:00 PM PST**; **only new projects created during the submission
  period are eligible** ("Do not start building your project yet"); themes:
  Resurrection, Frankenstein, Skeleton Crew, Costume Contest; $100,000 pool.
  Registration requires a valid **Kiro user ID or AWS account ID** (per the
  official page: "Create or sign in to your Kiro account at kiro.dev").
- **Sequencing rules (owner, 2026-10-26):** register now; do NOT create the
  project or start building before the window; the build itself waits until
  after Nov 8 (D1/D2/D3 windows first).
- **Registration status:** ATTEMPTED 2026-10-26, stopped at the account gate
  exactly as briefed. Verified flow: Join hackathon → Cloudflare human check →
  redirect to Devpost sign-up ("Please sign up or log in to continue" /
  "Join Devpost to register for Kiroween 2026"; options: GitHub, Facebook,
  Google, LinkedIn, or email). No signed-in Devpost session exists. Past that
  gate, registration needs a valid Kiro user ID or AWS account ID (official
  overview; the ID form field itself sits past the gate — UNVERIFIED). Kiro
  sign-in (app.kiro.dev) offers Google, GitHub, Builder ID, or organization —
  no email/password. Team info is not a gate (solo entry allowed, team
  decidable later). **Owner items: (1) Devpost account sign-in/creation;
  (2) a Kiro user ID (or AWS account ID).** No credentials were entered and
  nothing was submitted.
- **Concept (to finalize after rules publish Oct 30):** spec-first build in
  Kiro — leading candidate is a CMDB/reconciliation viewer (asset D) under
  Skeleton Crew or Frankenstein; decided once full rules land.

## 5. Sweep sources

AWS Builder Center hackathons listing; Devpost (AI/agent, Nov–Dec 2026);
lablab.ai events; Builder.io hackathon page; vendor developer-competition
pages (Google, Microsoft, Anthropic, Hugging Face). Each sweep re-verifies
deadlines from the official page before touching §3.
