# DoE panel record — webApp variant A vs variant B (#4478)

Doctrine of record (Vox, via the D1 seat): *"simple purpose,
simple architecture, simple design, simple implementation. Cut
taglines, helper text and secondary labels. If a screen needs
them to make sense, fix the layout."*

**Arms.** A = the shipped webApp (`web/`), untouched. B =
`web/variant-b/` — the same core, the **same `data/state.json`**
(B fetches `../data/state.json`), the same render logic; only
chrome differs. Captures: `evidence/web/ab/<view>-{a,b}.png`,
headless Chromium, 420×900, identical state, this tree.

**Panel form.** Three lenses scored from the capture pairs +
measured counts (builder-panel of record; D1 verifies and may
re-panel): **Doctrine** (is the chrome cut?) · **Task clarity**
(can the view's task be done, and is its safety property
visible?) · **Evidence** (do the numbers support the call?).

## Measured: visible words in <main>, per view

| View | A | B | Δ |
|---|---|---|---|
| Today | 44 | 26 | −41% |
| Plan | 108 | 101 | −6% |
| Reader | 45 | 39 | −13% |
| SR | 31 | 25 | −19% |
| Ingest | 38 | 2 | −95% |

## What B cut (the doctrine audit of A)

- Every view's `<h2>` restating its tab name (7 secondary labels).
- The footer (version line + "Works offline after the first
  load" — tagline + helper text).
- The Plan receipt's heading ("Trust receipt — what was
  fetched"); the receipt block itself is data and stays.
- The Reader's "Section" label, "Press Start" placeholder,
  "Previous/Next section" → Prev/Next.
- The SR scheduler's label + "(default)"/"(baseline)"
  parentheticals (the select shows its own value); "Flip card"
  → "Flip". Grade labels (Again/Hard/Good/Easy) are **primary**
  control labels and stay, in both arms.
- The Ingest helper paragraph and the inputs' long labels →
  "File" / "Photo".
- The sample-course disclosure paragraph — **proven redundant**:
  the course name itself reads "BIO 101 — Intro Biology
  (sample, synthetic)"; the paragraph repeated it at 18 words.
- Empty-state prose ("No calendar loaded…") → the empty layout.

## Per-view verdicts

- **Today — B.** Identical tasks and data; the disclosure was
  redundant with the course name; nothing a user acts on was lost.
- **Plan — B, narrowly.** The view is data (plan + receipt); the
  cut heading was the only chrome, and its removal costs nothing.
- **Reader — B.** Controls are self-evident in layout; the word
  area starting blank is unambiguous beside Start.
- **SR — B, narrowly.** Flip + grades carry the task. Recorded
  risk: "FSRS" without "(default)" — weighed acceptable; the
  select's selected option IS the default, visibly.
- **Ingest — A.** B's two-word view drops the one fact layout
  cannot carry: **placement is confirm-gated** — a syllabus is
  placed only after the student confirms. A first-time user
  cannot infer that safety property from two file inputs. The
  doctrine's own answer is a layout fix (a visible two-step
  sequence: 1 · File → 2 · Confirm), not the paragraph back;
  as built, B under-communicates here and A wins the view.

## Panel verdict

**B wins 4 of 5 views.** Direction for the post-submission UI:
adopt B's chrome discipline, with the Ingest view rebuilt as a
numbered two-step layout (the recorded amendment from this
panel) rather than B's bare form or A's paragraph. Neither arm
is deleted by this item: A stays the shipped surface, B stays
the recorded arm; the adoption decision is the D1 seat's, made
on this record.

*Method note: word counts are innerText of <main> with hidden
views removed, counted by the capture script at build time —
reproducible from the filed bundle. Both arms carry identical
logic, including the pre-#4473 SR receipt line; the experiment
varies chrome only, by design.*
