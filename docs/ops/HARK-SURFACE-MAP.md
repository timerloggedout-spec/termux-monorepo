# Hark — Surface Map (WAF target record)

Target brief: #1794 (`hark`, cli-adapter, webWrapper → deepCLI spec) · Role: `[MUSEai]@{role:{foundry}}`
Evidence: signed-in browser mapping 2026-11-03 08:07–08:14 PT (owner session, read-only) ∧ public shell fetch same day. Notation per #320.
Account of record: LoggedOut Timer / timerloggedout@gmail.com · plan "Pro $0" · auth values ∅ recorded (names only, per Foundry boundary).

## 1 · Authenticated areas ∧ routes

| Area | Route | Content of record |
|---|---|---|
| Landing | `hark.com` → `hark.com/chat` | signed-in redirect, ∅ login wall |
| Home | panel on `/chat` (no own route) | weather card (approx-location) · Project Rooms summary ("2 blocked ∧ 3 waiting across 9 rooms", links → issue #1440, PR #1413 class) · Monorepo Ops card (Open PRs, Failing, Triage Failures) · Create-a-panel (not exercised) |
| Chat | `/chat` | date-grouped thread · "Open summary" groups · "Manage GitHub inbox signal digest" · composer (§3) |
| Project room | `/project/{uuid}` | room side-list (Tribute System 1 Lane Gates · Monorepo Ops · Hark Inbox Autopilot · Inbox Autopilot · Smart Inbox Summary ×4 Gmail variants) · thread w/ Reply/Copy · "New project" (not exercised) |
| Search | overlay on `/chat` (no route) | combobox "Search the page and your mail" · Results listbox · ∅ query submitted |
| Settings | `/settings` | Profile · Scheduled tasks · Accounts · Wallet · System Preferences · Security · Submit Feedback · About · Sign Out · "Upgrade to hark pro²" |
| Profile | `/settings/profile` | fields by name: Name, Nickname, Birthday, Email (display-only), Phone, Home, Work, Interests |
| Scheduled tasks | `/settings/scheduled-tasks` ∧ `/{uuid}` | 7 tasks ∀ Paused · detail: Name, Prompt, When, Repeat ∈ {day, weekday, week, month}, Notify me, Previous runs (Completed + timestamps) · Resume/Pause control |
| Accounts | `/settings/connected-accounts` | filters {All, Connections, Logins, API Keys} · Connected: GitHub, Google, Atlassian, Linear · API Keys filter NOT opened (read-only) ⇒ key surface = GAP-1 |
| Wallet | `/settings/connected-cards` | "No saved cards" · Add-card not exercised |
| System Preferences | `/settings/system-preferences` | Theme (Auto), App Language (English), Data Management (sub-pages not opened) |
| Security | `/settings/security` | 2FA = Off · Sessions = "3 active sessions" (detail not opened) |
| About | `/settings/help/about` | links only (x.com/harklabs, /privacy, /terms) · ∅ version/build |

## 2 · Network layer

- App shell: Next.js/Turbopack — bundles `/_next/static/chunks/*.js?dpl=<deployment-id>` (public shell, 2026-11-03 fetch). Deobfuscation targets = these chunks ∧ the inline RSC payload (carries an `apiBase` config key; value NOT extracted in this pass).
- Observed in public shell payload: same-origin `/api/sky/iplocate` · third-party weather chain {api.open-meteo.com, air-quality-api.open-meteo.com, geocoding-api.open-meteo.com, ipapi.co} → explains Home weather card.
- **Authenticated API surface = NOT OBSERVED.** The mapping browser exposed ∅ network/devtools view ⇒ backend host/paths, methods, payload shapes, stream endpoints (websocket/SSE), ∧ auth transport (cookie-vs-header, by name) are GAP-2 — ∅ guessed. Sampled public chunks (3) carry ∅ `/api/` literals.
- Next routes to close GAP-2 (named, ∅ executed): CDP capture on the signed-in session (Tier-1 engine tooling, session stays origin-side) · Accounts → API Keys filter read (owner-present) · chunk-set deobfuscation sweep keyed on `apiBase`.

## 3 · Wrapper interaction surface (stdin-endpoint mapping, 2026-10-22 curation)

Composer (identical in Chat ∧ room): textbox "Message Hark" / "Message Hark in this project room" · Add attachment {Upload file, Take photo} · Start dictation · Send (state-dependent visibility) · mode picker observed in a prior session, NOT confirmed this session = GAP-3.
Outputs: structured text blocks (bulleted), expandable {Open summary, View full message, View transcript}, per-message Reply/Copy.

stdin endpoints (wrapper contract candidates, probes named):
- `session.check` → probe: `/chat` avatar "LT" presence (auth liveness, read-only)
- `rooms.list` → Home panel ∧ room side-list enumeration
- `chat.read` / `room.read` → thread parse (date groups, summary blocks)
- `chat.send` / `room.send` → composer submit (WRITE — wrapper-side gate, ∅ exercised in mapping)
- `tasks.list` → `/settings/scheduled-tasks` enumeration (7, ∀ Paused)
- `digest.read` → Chat "GitHub inbox signal digest" surface
- `search.query` → Search overlay combobox

## 4 · Serving lines (owner statement 2026-11-03 ∧ observed content)

- **GitHub mapping**: Home Monorepo Ops card + room "Tribute System 1 Lane Gates" + issue/PR deep links — Hark mirrors fleet GitHub state (PRs, failing runs, issues) into its rooms.
- **Provenance**: room threads ∧ Chat summaries = the agent-surface record of fleet activity (who/what/when as pushed by Hark) → provenance feedstock class.
- **HindSight**: Scheduled tasks (Prompt/When/Repeat + Previous runs) = the recurring-signal driver; signal digests + blocked/waiting pushes = retain-class events when the wrapper reads them continuously.
- **Scoring**: Home summary counts {2 blocked, 3 waiting, 9 rooms} ∧ Monorepo Ops {Open PRs, Failing} = triage/scoring inputs per the owner's "GitHub mapping && scoring".

## 5 · Gaps ∧ unknowns

- GAP-1: API Keys surface (Accounts filter) unopened — whether Hark issues first-party API keys = UNKNOWN; if it does, the wrapper priority re-ranks (API > wrapper).
- GAP-2: authenticated network layer unobserved (§2) — endpoints/methods/payloads/auth-transport/streams all open.
- GAP-3: composer mode picker unconfirmed this session.
- GAP-4: scheduled-task creation form unopened (edit-view fields recorded as proxy); Data Management, Sessions detail, 2FA setup, Submit Feedback unopened under read-only.
- Session seam: owner-browser session only; ∅ transfer mechanism (Foundry cookie boundary stands) ⇒ continuous wrapper operation = origin-browser-bound until a CDP/API route closes GAP-2/GAP-1.
