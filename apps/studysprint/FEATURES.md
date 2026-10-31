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
- ◐ Trust receipt before planning: the UI shows *what was fetched*
  (course, weeks, due dates, hash) and only plans after the student
  confirms — the evidence gate made visible — **Now** (receipt data
  exists; surface it)
- ○ Paste-a-link intake (LMS page / Google Doc) — Next
- ○ Multi-course intake: 4–5 syllabi → one merged calendar with
  conflict flags (two midterms, same week) — **Next, high value**

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

## 2. The plan (the core screen)
- ✓ Week-by-week plan: learn + retrieve block per topic
- ✓ Re-plan on missed week (sessions carried forward, flagged)
- ○ **Today view**: one card — today's sessions, one tap to start,
  one tap "I missed this" → instant re-plan, no guilt UI — **Now**
  (re-plan logic exists; render it)
- ○ Time-budget slider: "I have 25 min today, not 45" → plan
  re-flows around the student's real day (job shifts, commute) — **Now**
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
- ○ Daily check-in (30 seconds): done / partial / missed per
  session → feeds re-plan; streaks shown as *recovered weeks*,
  never as broken chains — **Now** (data model), Next (UI)
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
- ○ Plain-language mode: no jargon anywhere; every agent action
  explains itself in one sentence ("I moved Tuesday's session
  because you marked it missed") — **Now** (copy standard)
- ○ Spanish + multilingual UI and quiz prompts — Next
- ○ Works offline / low-end Android: plan + quizzes cached,
  sync when back — Next (our users' actual devices)
- ○ Screen-reader + large-text clean; color never the only signal
  (ABSTAIN/ALLOW states also carry icons + words) — **Now** (standard)
- ○ Privacy plainly stated: syllabus stays yours; no account
  needed to try; delete = one tap, actually deletes — **Now** (copy),
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
