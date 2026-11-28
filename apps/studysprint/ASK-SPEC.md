# Ask-a-question spec — in-app question-sending (issue #4462)

**Status: SPEC — for the D1 seat's ruling. The build files as a
follow-on under the ruling; nothing here is built yet.**

Owner feature (2026-11-03): a one-tap **"ask a question"**
affordance reachable from study context — a Today session, an
SR card, a reader section — that composes a question **with
that context attached**, addressed by default to the instructor
contact from the student's OWN syllabus.

## 1. The channel rule, and its boundary

Default destination = the instructor contact in the student's
own syllabus document, on their own device. This is their data
and their correspondent; composing a message to that address is
the natural act the feature exists to make one tap away.

The boundary is explicit, because a neighboring rule cuts the
other way: the catalogue/corpus feeds of #4295 strip
instructor/contact data at ingest (harvested and opt-in
documents about OTHER people's courses). Nothing from any
corpus, harvest, or prior ever addresses a question here. The
only source is the syllabus the student loaded for their own
course, read on their device at compose time.

And the app's own boundary: **StudySprint composes, never
sends.** The composed question leaves the device only when the
student presses send in their own mail app or share target.
No network call, no account, no queue inside StudySprint.

## 2. Destination resolution (never invent an address)

The syllabus schema today carries `{course, weeks}` — no
instructor field exists yet (verified in the example syllabus
and the parsers: neither `study_pipeline.py` nor
`study_tools.py` reads one). The build adds:

- **Schema:** an optional `instructor: {name, email}` on the
  syllabus document, passed through into surface state beside
  `course` (core `build_state` + `web/build_data.py`), so every
  surface resolves the destination from the same field.
- **Extraction:** syllabi in the wild commonly print
  "Instructor: … / Email: …" — the syllabus parser
  (`parse_syllabus_text`) gains an instructor-line extraction
  in the #4294 parser-iteration family; until a given syllabus
  yields one, the fallback chain governs. (Extraction quality
  rides the parser rounds; the feature must not block on it.)
- **Fallback chain, in order:** instructor email → instructor
  name only (compose with an empty To and the name in the
  greeting — the student addresses it) → no instructor at all
  (compose with empty To, no greeting name). At every step the
  composition is complete and useful; at no step is an address
  guessed, completed, or looked up.

## 3. Composition — one function of record

`compose_question(context, course_ctx, question_text)` — a pure
core function (study_tools, beside the plan/evidence builders)
returning `{to, subject, body}`. All surfaces render the same
composition: the TUI and CLI call it directly; the web bundle
carries the faithful port (the FSRS-port pattern, battery in
the suite). One composition of record, no per-surface drift.

- **Subject:** `Question — {course}: {context label}` —
  e.g. `Question — BIO 101: SR card "What does the cell
  membrane do?"`, `…: Week 2 · cell structure (Today)`,
  `…: Reader — Week 2, "Cell structure"`.
- **Body:** the student's text first (they write the actual
  question in the compose view; the context never replaces it),
  then a bounded context block under a `— context from
  StudySprint —` rule. Plain text only (mailto bodies are
  plain text; the share sheet gets the same text).

**Context payloads (bounded, per type):**

- **Today session:** course · date · week · session topic,
  kind (learn/retrieve) and minutes.
- **SR card:** the card's front AND back (a "why is the answer
  X" question needs the answer it disputes), its topic/section
  when known, and — if graded this session — the scheduler and
  last grade. It is the student's own study data going to their
  own instructor; nothing here is sensitive to a third party.
- **Reader section:** course · chapter · section title. When
  the ask starts from a **flagged term** (the reader's flag
  machinery is the natural ask-point), the term and its
  banked definition ride too.

## 4. Channel mechanics per surface (the spec decision)

- **Web bundle (browser):** the **Web Share API**
  (`navigator.share`) where available — the OS share sheet is
  the platform idiom and lets the student pick mail, messages,
  or anything else; **mailto: fallback** (a composed
  `mailto:{to}?subject=…&body=…` anchor) where it is not.
  The choice is capability-detected at tap time, stated in the
  UI ("Share…" vs "Open in mail…") so the student knows the
  channel before tapping.
- **APK (WebView shell):** same bundle code, one shell
  addition — the WebView currently never intercepts navigation,
  and a `mailto:` tap inside a bare WebView goes nowhere. The
  build adds a **narrow `shouldOverrideUrlLoading`**: `mailto:`
  (and only `mailto:`) is handed to an `ACTION_SENDTO` intent;
  every other URL keeps loading in the WebView. Small,
  auditable, and pinned in the android surface tests. Where no
  mail app answers the intent, the bundle's fallback is to show
  the composed text for copying — never a dead tap.
- **TUI:** a compose view per context (Today tab · SR Review ·
  Reader) — the context block prefilled, an editable field for
  the question, and **"Open in mail app"**, which hands the
  composed mailto to the OS opener (`webbrowser` →
  xdg-open / Termux's `termux-open-url` where present). The
  composed text is always fully visible in the view, so the
  copy-by-hand path exists on every terminal. The TUI sends
  nothing itself (§1).

## 5. Entry points

- **Today:** an "Ask about this session" action beside each
  session row (web + TUI; the APK is the bundle).
- **SR Review:** an "Ask about this card" action on the card
  view, available pre- and post-flip (the back rides the
  context either way once flipped; pre-flip it attaches front
  + topic — a student asking mid-recall hasn't seen the answer
  yet, and the composition should say what they saw).
- **Reader:** an "Ask about this section" action in the reader
  controls, plus the flagged-term path (§3) when a term is
  flagged.

## 6. Evidence the build ships (defined now, owed then)

1. **Compositions from all three context types on all three
   surfaces** — the actual `{to, subject, body}` artifacts in
   evidence (text captures + the TUI compose view + the web
   share/mailto state), including one fallback-chain case (no
   instructor in the syllabus → clean empty-To composition).
2. **Suite pins on `compose_question`** — subject shapes,
   context blocks per type, the fallback order, and the
   no-invented-address invariant; the web port battery-matched
   against the core function like the other ports.
3. **The APK mailto hand-off proven** in the emulator gate's
   manner: the override fires an intent for `mailto:` and for
   nothing else (harness assertion on the shell behavior, or a
   pinned unit test on the URL classifier if the gate can't
   observe intents — the build states which).

## Ruling requested

D1 rules: (a) the channel mechanics as specced (share-sheet-
first on web, narrow mailto override in the shell, OS-opener
in the TUI); (b) the context payloads, in particular the SR
card's back riding the composition; (c) the instructor-field
schema + parser-extraction sequencing (feature first on the
fallback chain, extraction riding #4294). The build files as a
follow-on under the ruling.
