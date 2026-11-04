# Changelog

All notable changes to StudySprint. Process: `VERSIONING.md`.
Entries are the GitHub Release notes, verbatim.

## [Unreleased]

### Surfaces 0.5.1

- **SR exports land on webApp + APK (#4673, qualifications
  closure ①):** the SR view gains Export Anki .apkg +
  Export Obsidian vault — browser ports of the core's
  writers over the web SR state (deck/model identity via
  the core's `_stable_id`; per-scheduler states mapped
  into the vault frontmatter). Battery-pinned in
  tests/test_sr_exports_web.py: .apkg semantic parity
  with the genanki writer (sqlite integrity, note/card
  content, referential integrity; 40-card + payload-
  overflow case), Obsidian note set byte-identical.
  The parity matrix's last absent row closes.

## [1.0.0] — 2026-11-04

**The submission cut.** Foundation **v1.0.0**: the version of
record (`VERSION`, read into every agent receipt as
`agent_version`) moves 0.5.0 → 1.0.0 on the tree that carries
the complete catch-up slate — parity iterations 1–4 binding
§1d calendar/geography, §1c memory methods, multi-course, and
§1b term-expansion + opt-in hardening on all three surfaces,
plus the second bundled sample course (STAT 210). Surfaces
version independently and stay at 0.5.0; post-1.0.0 foundation
motion is PATCH only (VERSIONING.md). Cut for the D1
submission freeze (Nov 4, 23:59 PT) on the D1 seat's sequence:
suite receipt-version tests green on this tree, or no cut.

Provider credit: command-dispatch (Swarm Optimizations &
Implementation Assurance seat), session
6628d41d-9519-4881-9063-3afe501df815.

### Foundation v1.0.0

- **Version of record 1.0.0** — `apps/studysprint/VERSION`
  bumped; the receipt pin in `tests/test_studysprint.py`
  follows it, and the parity matrix header names core v1.0.0.
  Everything below in this release section shipped on the
  0.5.0 foundation during the Nov 3 slate and is carried into
  1.0.0 unchanged: the foundation's capabilities at the cut
  are exactly the slate's sum (core pipeline · SR (FSRS-6 +
  SM-2 + Leitner) · memory methods · courses · reader/term
  bank · hardening (opt-in) · calendar/geography).
- **Evidence artifacts keep their 0.5.0 stamps** —
  `evidence/demo-run.json` and the strands-aws golden receipts
  record runs that happened under 0.5.0 and are not rewritten.


### Surfaces 0.5.0 (parity iteration 4, #4417 — hardening + §1b completion)

- **State recall + stress hardening binds on all three
  surfaces (opt-in only).** The core's study_hardening arrives
  as a Hardening view (web/APK) and tab (TUI): varied-context
  practice rotations, the mental-reinstatement script, and
  graduated SIT drill plans whose pressure elements are seeded
  by the drill id (receipt-reproducible). The mode is OFF by
  default; without the student's opt-in the plan is the core's
  refusal receipt and no drill exists. Ceilings ride verbatim
  ("performance under stress/anxiety — not recall gains");
  results record answered + 'not yet' counts with a supportive
  close — no score, deduction, or penalty field exists, by
  construction. Web runs browser ports battery-pinned to the
  core; the TUI runs the real functions.
- **§1b completes on a real book.** The demonstration book —
  Darwin, On the Origin of Species, 6th edition (Project
  Gutenberg #2009), Chapter XIV plus the book's complete
  Glossary and Index (typographic normalization only) — is
  ingested through the core pipeline on every surface. The
  ingest receipt shows the counts on each surface: **62 terms
  mined · 62 with definitions · 2 with index refs**
  (Embryology p.386 · Morphology p.382). Chapter XIV is the
  demonstration chapter because its own title names two
  indexed headwords, so every leg of the machinery fires on
  real data.
- **Inline term expansion in all three readers.** The book's
  sections render with the core's emphasized terms; selecting
  one expands its tap payload inline — glossary definition,
  index pages, and the sections it appears in (the web renders
  the core-computed segments and payloads from the build-time
  bundle; the TUI computes them live).
- **Hypothes.is annotations view.** Annotations over the
  book's sections render in the W3C Web Annotation model (the
  core's make_annotation), anchored by TextQuoteSelector. The
  API leg syncs with an account token — not configured on
  these surfaces, so nothing leaves the device.
- **OCR seam, wired where the platform allows.** The TUI/CLI
  path runs the core's tesseract default through ingest_any
  (provenance stamped `ocr`); on web/APK a photographed page
  is recorded as awaiting core OCR — the browser cannot run
  tesseract, and the surface says so.
- **Core fix carried by this iteration:** ingest_any no
  longer extracts a textbook's structure from its own back
  matter — a single-file book's Glossary/Index are the term
  bank's spine, not a chapter, so mined counts never count
  the glossary against itself (185 → the honest 62 on the
  demonstration book). ingest_any's textbook receipt now also
  carries the with-definitions / with-index-refs counts every
  surface shows.

### Surfaces 0.4.0 (parity iteration 3, #4416 — multi-course)

- **Multi-course binds on all three surfaces.** The course set
  (both bundled samples + the student's own courses) is intaken
  through the core's course-set machinery (study_courses:
  per-course plans + countdowns + merged totals + conflict
  flags) and every surface switches between courses with
  per-course state: on web, SR state and check-ins persist
  under per-course storage keys (the pre-0.4.0 global keys are
  adopted once, by the first course only); on the TUI,
  check-ins persist per course in checkin-logs.json while the
  flat checkin-log.json keeps carrying the active course's log.
- **Countdowns + .ics per course.** Each course's header/pane
  shows its exam countdown from the intake (honestly "unset"
  when the syllabus carries no exam date); the .ics download
  (web) / file export (TUI) is the core's export_ics over that
  course alone — validated, and carrying no other course's
  events.
- **Create-a-course on both surfaces.** Web: paste a syllabus
  document in Ingest — plan and countdown come from browser
  ports of build_study_plan / exam_countdown, battery-pinned
  to the core in tests. TUI: a Courses-tab form persists the
  syllabus document under ~/.studysprint/courses and the set
  re-intakes through the real core. A created course's progress
  lives under its own keys from its first minute.
- **Honest edges, kept:** the STAT 210 sample's calendar uses
  an assessment kind the core calendar intake refuses
  ("problem set"); the refusal is recorded on the course's
  bundle and shown in its Calendar view — the course itself
  ships whole. A created course's .ics export and memory
  bundle arrive with its first bundle build; its views say so
  rather than borrowing another course's.

### Surfaces 0.3.0 (parity iteration 2, #4415 — memory methods)

- **§1c memory methods bind on all three surfaces.** The core's
  five surface-named methods (study_memory) arrive as one
  Memory surface per client: the palace walk runs over
  iteration 1's temple route (the student's real walk, core-
  built placements), scored by the core's ordered-recall rule
  with misses named and the claims ceiling attached; the
  Feynman pane grades an explanation by key-term coverage of
  the verified section text — abstain/escalate/graded, the
  kernel's discipline, never semantic claims; retrievability
  reminders fire at R ≤ 0.9 over the student's own reviewed
  FSRS cards, each carrying a one-tap grade that IS the review.
- **Leitner rotation joins SR** as the third scheduler on
  webApp + TUI (boxes 1–5, plain-language move receipts, its
  own per-card state line), and the **Plan view gains the
  interleaved session**: today's sessions + due cards mixed by
  the core's deterministic rotation.
- **Binding shape:** the TUI runs the real core functions
  (`walk_review` · `explain_back` ·
  `retrievability_notifications` · `leitner_review` ·
  `interleave_sessions`); the webApp/APK run browser ports of
  the same scorers over the core-built bundle
  (`state.memory` from `web/build_data.py`), equivalence-pinned
  by `tests/test_iteration2_memory.py` (node-executed ports vs
  core outputs on shared fixtures). Foundation stays 0.5.0;
  `android:versionCode` stays 1 (its bump rides the APK trust
  line, not the surface line).

### v1.0.0 content — second bundled sample course (#4593)

- **STAT 210 — Data & Chance (sample, synthetic)** joins BIO
  101 as the second bundled example course: a structurally
  different subject AND assessment shape (weekly problem
  sets + a final project, vs quiz/lab/midterm), riding the
  same pipeline with no new code paths — fixtures
  `examples/{syllabus,calendar,readings,practice_set}_stats.json`
  + demo evidence in `tests/test_second_sample.py` (ingest →
  plan → SR over the new fixtures; counters Findings
  Register F-O4 cap 1, the mirror baseline's "single sample
  course" cap).

### Surfaces 0.2.0 (parity iteration 1, #4414 — calendar + geography)

- **§1d calendar awareness + geography bind on all three
  surfaces.** One core assembler —
  `study_geo.surface_calendar_geo` — computes the whole binding
  from a calendar document: intake, assessment briefings
  (frequency ramps + SHIFTED time/place notices), the day's
  frequency plan, quiet-hours probes against the class blocks,
  deduped locations, per-assessment routes (coordinate
  estimates with leave-by times), and the temple route (loci
  placements over the student's real walk) with audio cues.
- **TUI** gains Calendar and Routes tabs (8 panes), assembled
  live at runtime. **webApp** gains Calendar and Routes views
  over the same assembler, computed at build time like the
  rest of the bundle's state (disclosed in the parity
  statements). **APK** follows the bundle.
- Bundled example calendar (`examples/calendar.json`, synthetic
  like the other examples): BIO 101 Tue/Thu in Science Hall
  204, a quiz tomorrow (final-stretch ramp ×3), and a final
  SHIFTED to 18:00 in the Gym Annex — the shift briefing and
  its route are in the demo data, not just the tests.
- Honest edges kept: a calendar without coordinates yields
  locations and NO routes (omitted, never faked); a root
  without a calendar file renders a named empty state on the
  new panes/views.

### Surfaces 0.1.3 (#4412 — APK https-origin asset serving)

- **APK shell serves the bundle from a secure https origin** —
  MainActivity loads
  `https://appassets.androidplatform.net/assets/web/index.html`
  and intercepts that reserved domain's `/assets/` tree onto the
  APK assets (the WebViewAssetLoader pattern, implemented with
  framework APIs only: the SDK-direct build has no dependency
  resolver and androidx.webkit is not in android.jar). The #4283
  emulator gate proved the 0.1.1-era file:// interception
  insufficient in older WebViews (intercepted fetch from a file
  origin still blocked at the fetch layer); page + state fetch
  now share one https origin, so no CORS or file-origin rules
  apply. The legacy `/android_asset/` interception remains as a
  fallback. Browser path, state format, and web app logic are
  untouched. Surfaces version 0.1.3 in-tree; foundation stays
  0.5.0.

### Surfaces 0.1.2 (RFP-D1-8 set 2 — scheduler integrity + web contract)

- **#4231 FSRS generation pinned + aligned** — the core pins the
  FSRS-6 parameter tuple in study_sr (constructed explicitly,
  fuzzing off; a test alarms if a library upgrade moves the
  defaults), receipts and the UX export name the generation, and
  the web surface's scheduler is a faithful FSRS-6 port of the
  same algorithm (learning/relearning steps included), proven by
  a core↔web battery test over identical review sequences. The
  app warns in the SR view if a bundle's stamped generation ever
  differs from its own.
- **#4232 SM-2 pass boundary restored** — the surface grade map
  is {1: 1, 2: 2, 3: 3, 4: 5} on web and TUI: Hard (quality 2)
  resets like the core's SM-2 says, instead of landing on the
  quality-3 pass threshold.
- **#4228 Today actions render** — the core's designed actions
  (primary "Start Today's Sprint", subtle no-guilt "I missed
  this") render from state.today.actions and act on the same
  persisted check-ins.
- **#4230 Reader bodies teach their topics** — examples gain
  readings.json (one authored passage per syllabus topic); both
  builders use it, append only the topic's own check questions,
  and fall back to an honest stub — never another topic's text.
- **#4234 No pre-flip grading** — grade buttons stay disabled
  until the card is flipped (web + TUI); grade() also guards.
- **#4237 Load failure state** — a failed/unparsable state.json
  now renders a named error with an explanation and a retry
  button instead of hanging on "Loading your course…".

### Foundation

- study_sr: FSRS generation pin (FSRS_PARAMETERS /
  FSRS_GENERATION), generation stamped on receipts and the UX
  export; the export's per-card state now carries the learning
  step the surfaces schedule from.

## [0.5.0] — 2026-11-03

Fifth versioned state: MINOR feature batch (v0.5.0 batch, parts 1+2+3+4 of 4) — the calendar core
(build A, issue #4157) + maps and temple routes (build B,
issue #4158) + state recall and hardening (build C, issue
#4159) + ingestion on every surface (build D, issue #4242)
of RFP-D1-6.

Provider credit: command-dispatch (Swarm Optimizations &
Implementation Assurance seat), session
6628d41d-9519-4881-9063-3afe501df815.

### Added
- Calendar core (`study_calendar.py`), RFP-D1-6 items 1-3:
  (1) calendar intake — class meetings {days, times,
  building/room} + assessments {quiz/midterm/final, date, time,
  location} normalized into records; (2) assessment-frequency
  engine — deterministic frequency ramps as an assessment
  approaches, with an explicit ramp + briefing for assessments at
  a SHIFTED time or place vs the class pattern; (3) quiet hours —
  notifications landing inside a scheduled class are suppressed
  and batched to the block's end. Claims ceiling (in receipts +
  FEATURES): logistics support — pacing, timing, no-surprises;
  no learning-gain claim.
- Tests: `tests/test_study_calendar.py` covers every public
  function in `study_calendar.py`.
- Geography (`study_geo.py`), RFP-D1-6 items 4-5, consuming the
  calendar core's records: (4) location records for classes +
  assessments (from the student's own calendar — open data first)
  + route/travel-time assistance to the assessment room (injected
  travel provider; offline coordinate estimate by default);
  (5) temple routes on real geography — the method of loci over
  the student's actual campus path, an audio-cue script for the
  walk, and voice-input customization (rename/move) as data.
  Ceilings: logistics support + the loci ceiling (ordered/concrete
  recall, not understanding).
- Tests: `tests/test_study_geo.py` covers every public function
  in `study_geo.py`.
- State recall + hardening (`study_hardening.py`), RFP-D1-6
  item 6 as its own mode: varied-context practice rotation +
  the Smith (1979) mental-reinstatement script (encoding
  specificity; context effect modest, meta d~0.28 — NOT
  single-room matching), and adaptive hardening as graduated
  stress-inoculation drills (SIT phases 1-3) — OPT-IN ONLY, off
  by default, the flag in every receipt; NO-GUILT by
  construction (no score/penalty fields exist; pressure never
  carries penalties). Ceiling: performance under
  stress/anxiety, not recall gains.
- Tests: `tests/test_study_hardening.py` covers every public
  function in `study_hardening.py`, incl. the opt-in refusal and
  the no-guilt field ban.
- Ingestion on every surface (build D, issue #4242), one core
  path (`study_pipeline.ingest_any` / `run_syllabus_upload`):
  syllabus text — typed or OCR'd from a photographed page
  (provenance `source: ocr`) — parses into `study_calendar`
  records {times · buildings · kinds} and places ONLY on the
  student's confirm (confirm-gated placement; no confirm ⇒ no
  placement); textbook uploads run the content flow (structure
  → term bank → SR cards). Surface legs: CLI `ingest` command
  on the demo/agent entry; a TUI Ingest screen (file-path entry
  + Confirm placement); the webApp Ingest view (file picker +
  camera capture — text parses in-browser under the same line
  grammar; photographs are recorded as awaiting core OCR, OCR
  does not run in the browser); the APK shell wires the system
  file chooser / camera to the bundle's inputs
  (WebChromeClient.onShowFileChooser).
- Tests: syllabus parse + confirm gate + OCR provenance +
  per-surface legs in `tests/test_study_pipeline.py`,
  `tests/test_tui.py`, `tests/test_web_surface.py`,
  `tests/test_android_surface.py`.

### Surface patch line 0.1.1 (RFP-D1-7 award batch, #4277)

The three surfaces patch to **0.1.1** on their independent lines
(VERSIONING.md): webApp SR review is due-aware and never recycles
a graded card in-session (#4218) · TUI SR review state is
per-card and accumulates (#4224) · webApp check-ins persist and
a missed session shifts (#4215) · TUI check-ins record today's
real week/day and persist to disk (#4223) · webApp Today
advances with the calendar from `plan_start` (#4214) · the
service-worker cache carries the surface version and state.json
is network-first (#4219) · all six Reader sections are
reachable (#4217) · the APK signs with the committed project
keystore and ships a brand launcher icon (#4222) · APK.md leads
with its build-time-core architecture (#4220) · the webApp
discloses its bundled sample course on the first screen (#4216).
Records: surface version-line ruling in VERSIONING.md (#4212) ·
APK evidence record in-tree (#4221) · web parity statement names
foundation v0.5.0 (#4225).

## [0.4.0] — 2026-11-03

Fourth versioned state: MINOR feature batch (v0.4.0 batch) — the
reading pipeline §1b in full (RFP-D1-3, issue #4111), multi-course
intake, exam countdowns, and .ics export (RFP-D1-4, issue #4112),
and the memory-methods expansion (RFP-D1-5, issue #4113).

Provider credit: command-dispatch (Swarm Optimizations &
Implementation Assurance seat), session
6628d41d-9519-4881-9063-3afe501df815.

### Added
- Reading pipeline (`study_pipeline.py`): the six §1b stages —
  edition finder over legal open sources (OpenLibrary, archive.org)
  with a student-confirm step before anything plans from an edition;
  upload intake in any form (text native, photos/scans via OCR,
  PDF/EPUB via an injected structured extractor); structure
  extraction (chapters -> sections) mapped onto the reader core's
  Section type; per-chapter Index+Glossary term bank implementing
  the reader's term-lookup hook and feeding SR cards; term emphasis
  segmentation + tap payloads; hypothes.is annotations as W3C Web
  Annotation JSON-LD with an API client (the API-only option from
  the #3697 evaluation; selections convert to SR cards and flagged
  terms to annotations). All network/OCR touches are injected
  callables — the module is offline by default.
- Tests: `tests/test_study_pipeline.py` covers every public
  function in `study_pipeline.py`.
- Multi-course intake (`study_courses.py`): N syllabus documents ->
  N plans (via the existing plan builder) in one stamped bundle
  with merged totals and deadline conflict flags (same-week exams;
  exams within 7 days).
- Exam countdown per course: from the syllabus `exam_date` —
  days/weeks remaining, urgency tier, the implied study pace
  (sessions per day), and countdown milestones (T-14, T-7, T-3,
  exam day).
- .ics export: every plan session plus countdown milestones and
  exam days as iCalendar VEVENTs (CRLF, stable UIDs, RFC 5545
  escaping), with a parse-back validator (`validate_ics`).
- Tests: `tests/test_study_courses.py` covers every public
  function in `study_courses.py`.
- Memory methods (`study_memory.py`), all six RFP-D1-5 items, each
  carrying its evidence grade and claims ceiling in code, receipts,
  and FEATURES: (1) method of loci — chapters -> palace route,
  term-bank items at loci, walk-mode review of ordered recall
  (ceiling: ordered/concrete recall, not understanding);
  (2) Pomodoro session engine — 25/5 blocks x4 + long break,
  check-in = block completion, adaptive block length (ceiling:
  pacing/starting, not memory); (3) retrievability notifications —
  fire at the FSRS threshold with the cue + one-tap grade in the
  reminder, implementation-intention phrasing; (4) Feynman
  explain-back graded against verified evidence only (abstain with
  no evidence, escalate on thin coverage); (5) interleaved
  quiz/card sessions (deterministic rotation, mixed topics);
  (6) Leitner boxes — the plain-language onboarding scheduler,
  receipt-stamped.
- Tests: `tests/test_study_memory.py` covers every public
  function in `study_memory.py`.

## [0.3.0] — 2026-11-02

Third versioned state: MINOR feature batch adding the
spaced-repetition module (FEATURES Next #1, issue #3050 as amended:
Obsidian vault surface included as a required component).

Provider credit: command-dispatch (Swarm Optimizations &
Implementation Assurance seat), session
6628d41d-9519-4881-9063-3afe501df815.

### Added
- Spaced-repetition module (`study_sr.py`): cards built from the
  existing quiz/term data (practice-set q/a, question/answer, and
  term/definition shapes); two schedulers behind one interface,
  selectable by name — FSRS (default, via py-fsrs) and SM-2 (classic
  baseline). Every review returns a stamped receipt naming the
  scheduler that produced it; an unknown scheduler name raises a
  clear error.
- Anki export: `export_apkg` writes a genanki `.apkg` (deck
  "StudySprint") and returns a receipt with the file hash.
- Obsidian vault surface: `export_obsidian_vault` writes
  obsidian-spaced-repetition-format notes (sync state in
  frontmatter, `#flashcards` tag, front `?` back) plus an index
  note; `read_obsidian_card_state` / `import_obsidian_states` read
  the state back (the vault -> core sync point). Device sync
  points (`ObsidianBridge`, `push_cards_to_vault`,
  `pull_states_from_vault`) adapt the fleet's existing adapter
  `bin/obsidian_server.py` (token-authenticated HTTP bridge, port
  8085, symlink-rejecting token read) — seeded from it, not a
  cold build.
- ts-fsrs UX seed: `to_ts_fsrs_state` / `export_ux_state` map
  py-fsrs card state onto the ts-fsrs Card shape for the UX layer.
- Tests: `tests/test_study_sr.py` covers every public function in
  `study_sr.py`.

## [0.2.0] — 2026-10-31

Second versioned state: MINOR feature batch implementing all five
`FEATURES.md` Now items, automated re-sync parity verification, and
refreshed evidence snapshots.

Provider credit: Jules, PR #2635, session 17326020844735872479.

### Added
- Trust receipt formatting (`format_trust_receipt` in `study_tools.py`):
  surfaces verified course metadata, deadline counts, source path, and
  short content hash before student confirmation; wired into agent receipt
  `trust_receipt` payload.
- Today view card (`render_today_view` in `study_tools.py`): renders
  single-screen card of today's study sessions with estimated minutes,
  "Start Today's Sprint" primary action, and guilt-free "I missed this"
  action; wired into agent receipt `today_view`.
- Plan-budget reflow (`reflow_plan_budget` in `study_tools.py`):
  dynamically re-scales session duration (e.g. 25 min vs 45 min) to match
  the student's real daily schedule.
- Daily check-in data model (`record_daily_checkin` in `study_tools.py`):
  tracks session completion (done/partial/missed), re-plan recommendations,
  and streaks framed as active/recovered weeks rather than broken chains.
- Plain-language mode & accessible statuses (`plain_language_action`,
  `format_accessible_status`, `PRIVACY_STATEMENT` in `study_tools.py`):
  plain-language explanations without jargon, high-contrast accessible
  gate decision tags (`[✓ ALLOW]`, `[⚠ ABSTAIN]`, `[⛔ ESCALATE]`), and
  local-device privacy guarantee in every receipt.
- Automated re-sync parity auditor (`tools/resync_parity.py` and
  `tests/test_resync_parity.py`): computes Git blob object SHAs
  (`sha1("blob " + len + "\0" + content)`), comparing monorepo tree
  against upstream `timerloggedout-spec/studysprint` (GitHub API or local
  dir) with offline baseline manifest support.
- Extended Strands agent tool declarations in `agent.py`: added tools
  `get_today_view`, `adjust_time_budget`, and `checkin_session`.

### Changed
- Receipts: schema `studysprint-agent-receipt/v1` updated to carry
  `agent_version: "0.2.0"`, `decision_accessible`,
  `plain_language_explanation`, `trust_receipt`, `today_view`, and
  `privacy`.
- VERSION bumped to 0.2.0.

### Evidence
- Tests: 17 passed (offline suite: `tests/test_studysprint.py` +
  `tests/test_resync_parity.py`).
- Demo decisions (`evidence/demo-run.json` at `agent_version: "0.2.0"`):
  scenario 1 ABSTAIN on asserted-only evidence; scenario 2
  ALLOW_RECOMMENDATION on fetched syllabus (12 sessions, week-1 quiz,
  re-plan, trust receipt, today view); scenario 3 ESCALATE on
  credential_mutation.

## [0.1.0] — 2026-10-30

First versioned state: the complete D1 build on the D0 foundation.

### Added
- G2 study artifact kinds (`study_tools.py`): syllabus +
  practice_set evidence sets in the D0 stamped shape
  (provenance / freshness / sha256), plus build_study_plan,
  generate_quiz, replan_on_missed.
- G3 Strands-wired agent (`agent.py`): the D0 evidence-gate loop on
  the vendored Delphi Oracle kernel, tools registered on a
  Strands `Agent` when the SDK is present; hashed receipts
  (`studysprint-agent-receipt/v1`, now carrying `agent_version`).
- D0 foundation vendored verbatim in `foundation/`:
  oracle_kernel.py (blob 9a4a1c78), fetch_evidence.py (8442d813),
  D0-FOUNDATION.md census + reuse map.
- Demo (`demo.py`, `demo-script.md`), Builder Center article
  (`article.md`, published 2026-10-30), sample syllabus +
  practice set in `examples/`.
- `requirements.txt`: zero required dependencies;
  strands-agents optional.
- FEATURES.md (user-wanted features, UI/UX) and this process
  (VERSIONING.md + VERSION + CHANGELOG.md).

### Changed
- Polish(1): the practice_set artifact path now yields a quiz
  from the fetched set (previously only the syllabus path built
  outputs); README + article aligned to the live assets (article
  URL, demo video, D0 repo URL).

### Evidence
- Tests: 7 passed (offline suite, tests/test_studysprint.py).
- Demo decisions (evidence/demo-run.json): ABSTAIN on asserted
  evidence → ALLOW_RECOMMENDATION on the fetched syllabus
  (12-session plan + week-1 quiz + re-plan) → ESCALATE on
  credential_mutation.
- Workshop qualifier: Strands workshop completed in-window
  2026-10-30 (all 7 modules EXIT:0; gate D1-WORKSHOP cleared).
- Live assets: article on Builder Center; demo video on YouTube
  (1:10, public). Project submission: Nov 4, per owner ruling.
