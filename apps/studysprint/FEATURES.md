# StudySprint — features a user would want (UI/UX first)

Owner-requested 2026-10-30. User = a first-gen college student with a
syllabus, a phone, a job, and no family playbook for college.
Priorities: **Now** = fits the pre-submission iteration window
(before Nov 4) · **Next** = v0.2–v0.3 · **Later** = v1.x.
Status tags: ✓ built · ◐ partial · ○ planned.

## The one-screen promise
Drop a syllabus → see *today's* plan in under 10 seconds. Every
feature below serves that screen or the daily loop around it.

## 1. Intake (getting a syllabus in)
- ✓ Syllabus file → verified evidence set → plan (`study_tools`)
- ○ PDF syllabus upload + parse (the concept's original input;
  today = structured JSON) — **Next**
- ✓ Trust receipt before planning: the UI shows *what was fetched*
  (course, weeks, due dates, hash) and only plans after the student
  confirms — the evidence gate made visible — **Now** (`format_trust_receipt` built + surfaced)
- ○ Paste-a-link intake (LMS page / Google Doc) — Next
- ○ Multi-course intake: 4–5 syllabi → one merged calendar with
  conflict flags (two midterms, same week) — **Next, high value**

**Built (v0.4.0, 2026-11-03; RFP-D1-4 / issue #4112):** multi-course intake, per-course exam countdowns, and .ics export of sessions + countdown milestones live in `study_courses.py` with tests — the §1a multi-course item above (N syllabi -> one merged view with conflict flags) plus the countdown/calendar surface.

## 1b. Reading pipeline (owner design, 2026-10-30)
The syllabus makes the *plan*; the assigned readings are the
*material*. Optimized options only — two anti-patterns ruled out
by the owner: ✗ speed-reading the syllabus itself, ✗ raw
direct-PDF chapter reading as the reading experience.
- ○ **Auto finder**: given the syllabus's texts (title / ISBN /
  author), find the book — PDF / EPUB / web edition — from legal
  open sources and the student's own library access; present the
  found edition for one-tap confirm (never plan from an unconfirmed
  edition — the evidence rule applies to books too) — Next.
  Census 2026-10-30 (Observatory): ∅ in index; the finders are
  APIs, not repos — OpenStax catalog API, archive.org
  AdvancedSearch, OpenLibrary (ISBN + covers), DOAB/OAPEN
  OAI-PMH feeds (quotas to verify at build).
- ○ **User uploads, any form**: PDF / EPUB / docs ∧ **photos and
  scans** of physical pages → OCR → the same structured pipeline
  (a photographed chapter is a first-class chapter) — Next.
  Refs: MinerU (PDF→structured markdown/JSON, ★82,831),
  tesseract (Apache-2.0) / PaddleOCR (Apache-2.0, ★92k) for
  OCR; an owned WebSend scanner fork already exists in-index.
- ○ **Structure extraction**: chapters → sections from the TOC;
  every reading assignment maps to chapter + section ranges, not
  page blobs — Next. Closest fit of record: GROBID (Apache-2.0,
  ★5,205 — scholarly structure: TOC/sections/references + NER);
  MinerU covers the TOC/structure half for general PDFs.
- ○ **Index + Glossary mining**: search the book's back-of-book
  Index and Glossary *by chapter* → a per-chapter term bank
  (term, glossary definition, index page refs, the sections it
  appears in). This term bank is the spine: it feeds term
  emphasis, quiz generation, SR cards, and flagging — Next.
  Extraction ≈ keyphrase class: KeyBERT (MIT, ★4,224) for
  per-chapter candidates, grobid-ner for entity-grade terms.
- ○ **Term Emphasis in every view**: glossary/index terms render
  emphasized wherever they appear (plan, reader, quiz); tap a
  term → its definition, its sections, its SR card — Next.
  ∅ purpose-built in index; UX pattern of record =
  obsidian-lexis (highlights known terms, atomic cards on tap);
  the hypothes.is selector substrate doubles as the highlight
  layer.
- ○ **Hypothes.is layer**: annotations, highlights and selections
  via hypothes.is — the student's customizations live in an open
  annotation layer (portable, not locked in our app), and a
  hypothes.is selection can become a flag / term / card in one
  tap — Next. **Strongest-covered surface in the census**:
  hypothesis/client is *already ours* (owned fork
  timerloggedout-spec/client_fork, fork note "Agentic Teams",
  verified firsthand) + pdf.js-hypothes.is starred (annotate the
  PDF directly); h (API) + via (proxy) = MOAR; annotations are
  W3C Web Annotation JSON-LD — highlight→structured-data is
  native to the model, not a scrape.

**Built (v0.4.0, 2026-11-03; RFP-D1-3 / issue #4111):** all six §1b stages are implemented in `study_pipeline.py` with tests — finder (confirm-before-plan) -> OCR intake -> structure -> per-chapter term bank (behind the reader's term-lookup hook) -> term emphasis -> hypothes.is layer. The hypothes.is leg implements option (3) of the #3697 evaluation — API-only annotations over reader sections in the W3C Web Annotation model; the owned client_fork revival and the hosted embed remain view-surface choices that render on top of the same annotation data.

## 1c. Memory methods (RFP-D1-5; built v0.4.0, 2026-11-03)

How material gets encoded, paced, and recalled in the moment —
`study_memory.py`, all six with tests. Each entry carries its
evidence grade and its claims ceiling; the ceilings bind the copy.

- ✓ **Method of loci (Temple Memory)**: syllabus chapters -> a
  palace route; term-bank items placed at loci; walk-mode review
  scores ordered recall. Evidence: Dresler et al. 2017 (Neuron)
  26 -> 62 of 72 words, durable 4 months; BJOP 2025 meta-analysis
  d = 0.88 serial recall, GRADE low. **Ceiling: ordered/concrete
  recall, not understanding.**
- ✓ **Pomodoro session engine**: 25/5 blocks x4 + long break;
  check-in = block completion; adaptive block length on streaks.
  Evidence: fatigue down ~20%, self-rated focus up; no learning
  gain proven. **Ceiling: pacing/starting, not memory.**
- ✓ **Retrievability notifications**: fire when a card's FSRS
  retrievability crosses the threshold; the reminder carries the
  cue + a one-tap grade (retrieval inside the reminder) and
  implementation-intention phrasing.
- ✓ **Feynman explain-back**: graded against verified evidence
  only (key-term coverage); no verified evidence -> abstain;
  thin coverage -> escalate with the missing terms named.
- ✓ **Interleaved quiz/card sessions**: quiz prompts and due SR
  cards mixed round-robin across topics, deterministically.
- ✓ **Leitner boxes**: the plain-language onboarding scheduler —
  five boxes, knew it -> up, missed -> back to box 1, every move
  receipt-stamped with a plain-language explanation.

## 1d. Calendar, geography, state (RFP-D1-6; built v0.5.0, 2026-11-03)

Where and when studying happens, as first-class records —
`study_calendar.py` (build A). Claims ceiling for the whole
section: logistics support (pacing, timing, no-surprises) — no
learning-gain claim.

- ✓ **Calendar intake**: class meetings {days · times ·
  building/room} and assessments {quiz/midterm/final · date ·
  time · location} normalized into records the geography leg
  consumes.
- ✓ **Assessment-frequency engine**: question/card frequency
  ramps in deterministic tiers as an assessment approaches; an
  assessment at a shifted time or place gets an explicit ramp +
  a briefing naming the shift.
- ✓ **Quiet hours**: notifications landing inside a scheduled
  class are suppressed and batched to just after the block,
  receipt-stamped.
- ✓ **Maps**: location records for classes + assessments from
  the student's own calendar (open data first); route +
  travel-time assistance to the assessment room — injected
  travel provider, offline coordinate estimate by default.
- ✓ **Temple routes on real geography**: the method of loci over
  the student's actual campus path — waypoints as loci, term-bank
  items placed along the walk, an audio-cue script for the walk,
  and voice-input route customization (rename/move) as data.
  Ceilings: logistics support + ordered/concrete recall, not
  understanding.

## 2. The plan (the core screen)
- ✓ Week-by-week plan: learn + retrieve block per topic
- ✓ Re-plan on missed week (sessions carried forward, flagged)
- ✓ **Today view**: one card — today's sessions, one tap to start,
  one tap "I missed this" → instant re-plan, no guilt UI — **Now**
  (`render_today_view` built + wired into agent receipt)
- ✓ Time-budget slider: "I have 25 min today, not 45" → plan
  re-flows around the student's real day (job shifts, commute) — **Now**
  (`reflow_plan_budget` built)
- ○ Exam countdown mode: inside 7 days of a due date the plan
  shifts weight to retrieval + practice sets automatically — Next
- ○ Drag-to-edit sessions; the agent re-balances the rest of the
  week around the edit ("view, edit, and act on its work") — Next
  (judges' usefulness axis)
- ○ Calendar export (.ics / Google Calendar) — Next
- ○ Print / share a week (PDF) for a study group or advisor — Later

## 3. Daily loop (retention lives here)
- ◐ Recall quizzes per week (generated from topics) ✓ ·
  practice-set quiz path ✓
- ✓ Daily check-in (30 seconds): done / partial / missed per
  session → feeds re-plan; streaks shown as *recovered weeks*,
  never as broken chains — **Now** (`record_daily_checkin` data model built), Next (UI)
- ○ Spaced repetition: quiz misses resurface on FSRS intervals
  (retrievability-targeted; the 1d / 3d / 7d ladder stays only as
  the cold-start fallback) — Next. Seed census 2026-10-30
  (Observatory lane, signals ¬ adoption orders; spot-verified by
  this seat via PAT API). **Stacks are multi-lingual by design
  (owner correction 2026-10-30): we take templates + concepts and
  adapt them — language is not a filter.** Seeds: scheduler =
  **py-fsrs** (MIT, ★519) for the Python agent core ∧ **ts-fsrs**
  (MIT, ★838) for the TS UX layer we need anyhow — both, not
  either/or; .apkg interop = genanki (MIT, ★2,776, already an
  index dependency-candidate), bridge = anki-connect (live-Anki
  sync only), card/UX refs = orbit, carden, memo. Already ours:
  forks of fsrs4anki, fsrs4anki-helper, anki-llm, AnkiAIUtils,
  AnkiconnectAndroid.
  Algorithm note (corrected 2026-10-30): SM-2 is not a footnote —
  it is Anki's long-standing default-scheduler lineage and lives
  on in its scheduler/plugin ecosystem; "Anki shipped it" argues
  nothing by itself, for either side. The FSRS case rests on the
  merits: a DSR memory model with per-user optimized weights and
  retention-targeted intervals, benchmarked against SM-2-class
  schedulers by the open-spaced-repetition org. Default = FSRS;
  SM-2 stays a legitimate simple/predictable baseline — and the
  comparison baseline in our own evals.
  **Obsidian layer — REQUIRED (owner ruling via main, 2026-11-02):**
  the Agents SR stack of record = FSRS seeds {py-fsrs agent core ∧
  ts-fsrs UX layer · SM-2 baseline} + the **Obsidian layer** as the
  vault surface for the agent SR system — vault-compatible
  card/notes export ∧ sync points are a REQUIRED component of the
  SR module, ¬ optional. Seed-census candidates
  **obsidian-spaced-repetition** ∧ **Obsidian_to_Anki** are promoted
  candidate-grade ⇒ required seeds for this layer (concepts adapted
  per the multi-lingual rule; census facts per 2026-10-30).
- ○ RSVP **multi-pass reading** (owner-shaped 2026-10-30): RSVP
  is not how a syllabus gets read (anti-pattern, §1b) and not a
  single pass over raw PDF either — it runs **section by
  section, in passes**: pass 1 = very fast skim (high wpm —
  get the shape of the section), pass 2+ = slower, focused
  re-reads of the same section. **During any pass the student
  flags sections and terms/concepts** — a flag is one tap and
  lands in the term bank (§1b), the SR deck, and the quiz focus
  list; hypothes.is selections flag the same way. References:
  **Fovea** — a real Android app (Google Play
  com.revolvotech.fovea, "Fovea - RSVP Spritz E-Reader",
  verified firsthand 2026-10-30: adjustable WPM, pause/rewind/
  resume, paste-text, works on PDFs + study text, focus/ADHD
  positioning) ∧ Reedy (Chrome). Census 2026-10-30
  (Observatory): ∅ in-index (0/3,639) as *repos* — Fovea lives
  on the Play store, not GitHub. Templates (MOAR):
  **primusread** (TS, MIT, ★539 — fixation-point reader, best
  web-stack template), **speeedy** (TS, MIT — local-first RSVP
  for PDF/EPUB), Reedy-for-Chrome (GPL-2.0 ⇒ concepts only,
  ¬ code), LetoReader (chunking + pacing), stutter (embeddable
  player).
  UX spec (copy): ORP anchor ≈⅓ into the word, never moving ·
  per-pass wpm (skim fast, re-read slow), per-user saved ·
  punctuation- + length-aware dwell (flat fixed-rate = the
  failure mode) · chunk 1 → 2–3 words as wpm rises · pause/
  resume + 10-word rewind + progress (rewind replaces eye
  regression) · **flag control always under the thumb**.
  UX spec (avoid): the single-pass reading of dense text —
  comprehension holds ≈400–500 wpm on easy text and drops on
  new/complex material; the multi-pass shape is the fix, and
  paragraph mode stays available per section — Next
- ○ "Explain it back" voice/text answer → agent checks against the
  topic and stamps what was missed — Later
- ○ Gentle nudges (push/SMS) at the student's chosen hour, quiet
  by default, off during exams week unless asked — Next

## 4. Trust + accessibility (why first-gen users stay)
- ✓ Hashed receipts: every decision shows its evidence set —
  in UI terms: "Planned from *your* BIO 101 syllabus, fetched
  09:12, 3 weeks, 6 topics" — **Now** (surface existing receipts)
- ✓ Plain-language mode: no jargon anywhere; every agent action
  explains itself in one sentence ("I moved Tuesday's session
  because you marked it missed") — **Now** (`plain_language_action` built)
- ○ Spanish + multilingual UI and quiz prompts — Next
- ○ Works offline / low-end Android: plan + quizzes cached,
  sync when back — Next (our users' actual devices)
- ✓ Screen-reader + large-text clean; color never the only signal
  (ABSTAIN/ALLOW states also carry icons + words) — **Now** (`format_accessible_status` built)
- ✓ Privacy plainly stated: syllabus stays yours; no account
  needed to try; delete = one tap, actually deletes — **Now** (`PRIVACY_STATEMENT` copy built),
  Next (impl)

## 5. Social proof + help
- ○ Study-buddy mode: share a week's plan, co-check-in — Later
- ○ Advisor/tutor view: read-only plan + progress for a mentor
  the student invites — Later
- ○ "I'm lost" button → maps the current topic to campus resources
  (tutoring center hours, office hours from the syllabus itself) — Next

## UX principles (binding on every screen)
1. Today first. The plan is a means; *today* is the product.
2. No guilt mechanics. Missed = re-planned, never red, never a
   broken streak.
3. Evidence visible. If the agent claims it, the receipt is one
   tap away (the D0 pattern, as a UI rule).
4. One thumb, one hand, on a bus. Primary actions bottom-reach,
   ≥48px targets.
5. Plain words. If a first-gen freshman needs a dictionary, the
   copy is wrong.

## Anti-features (deliberately never)
- No leaderboard / no comparing students.
- No paywall on re-planning or quizzes (the core loop is the
  social-good surface).
- No planning from an unverified syllabus claim (gate ABSTAINs —
  a feature, surfaced honestly, not an error state).
