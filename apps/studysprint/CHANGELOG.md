# Changelog

All notable changes to StudySprint. Process: `VERSIONING.md`.
Entries are the GitHub Release notes, verbatim.

## [0.4.0] — 2026-11-03

Fourth versioned state: MINOR feature batch (v0.4.0 batch) — the
reading pipeline §1b in full (RFP-D1-3, issue #4111), multi-course
intake, exam countdowns, and .ics export (RFP-D1-4, issue #4112),
and the memory-methods expansion (RFP-D1-5, issue #4113).

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
