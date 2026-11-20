---
name: plain-language
category: Writing & research
description: "Clear, friendly, jargon-free writing for non-technical readers: ticket text, QA steps, release notes, status updates, UI copy, business messages. Use when writing for QA, product, stakeholders or end users, or on a \"make this less technical\" pass. Scholarly prose is academic-writing; document structure is information-architecture.\n"
---

# Plain language — clear, engaging writing for non-technical readers

Goal: take something true-but-technical and say it so a smart non-engineer (a QA
tester, a product manager, a customer) understands it instantly and stays engaged —
without dumbing it down or making it inaccurate.

## Who you're writing for

Assume the reader is **intelligent but not technical**. They don't know the codebase,
the framework, the API, or the internal jargon. They know the *product* and what users
are trying to do with it. Write to that person.

## Core principles

1. **Plain words over jargon.** Replace engineering terms with what the user *sees* or
   *does*. Translate, don't transliterate:
   - "endpoint / API returns 403" → "the page shows a 'not allowed' error"
   - "null state / empty array" → "when there's nothing to show yet"
   - "auth / RBAC / token" → "who's allowed to do this / signing in"
   - "persisted to the DB" → "saved"
   - "the modal renders" → "a pop-up window opens"
   - "VIN-routed update" → name the actual user action instead
   When a technical term is genuinely needed, define it in one short aside.

## A quick method

When asked to write or rewrite copy:
0. **Read `LEARNINGS.md` beside this skill, when your copy keeps one, first** — the
   user's voice preferences, approved before→after rewrites, and the jargon→plain
   glossary live there; copy that ignores them gets corrected.

1. Identify the **reader** and what they need to *do* or *decide* after reading.
2. State the **one main point** in a single plain sentence — that's your opener/title.
3. Add only the supporting detail that reader needs, in scannable structure.
4. **De-jargon pass:** reread as if you'd never seen the code. Swap each technical term
   for what the reader observes. Flag anything you couldn't translate.
5. **Tighten pass:** cut filler, split long sentences, switch passive→active.
6. **Engagement check:** would a busy non-engineer keep reading? Is the opener
   compelling? Is the tone friendly, not robotic?

Editing copy that already exists (a page, UI copy, an email, a published article to refresh)?
Use [copy-sweep.md](copy-sweep.md): it picks the mode first (point edit, keep the voice, or
rewrite from the record), then runs the sweeps in order.

## Titles specifically

A good title is a plain-language headline: specific, action/outcome oriented, readable
at a glance, no internal codenames or file paths. Prefer the user-facing outcome.

- Weak: "Refactor the vehicle service to route through the new backend"
- Better: "Saving a vehicle's details now works for non-VIN updates"
- Weak: "Add validation decorators to the checkout endpoints"
- Better: "Checkout now tells you which field needs fixing"

(This install's original examples: `LOCAL.md` beside this skill, when your copy keeps
one — *Title examples*.)

## Output discipline

- Match the requested **format and length**. A ticket title is one line; a description
  has sections; a status update is a few sentences. Don't over-produce.
- When you simplified something where the precise technical detail still matters for an
  engineer, you may add a short **"Technical notes"** aside at the end — kept separate
  from the reader-facing copy, so the plain part stays plain.
- If you can't translate a term without losing necessary meaning, say so and ask,
  rather than guessing.

## Common failure modes — if you're about to do one of these, stop

- **Describing third-party services by function** ("our payment processor") — reference
  them by brand name (Stripe, Lyft); brand names are clearer to non-technical readers.

## Before you call this done

- [ ] LEARNINGS.md was read first; the copy matches the recorded voice and glossary.
- [ ] De-jargon pass done: reread as a non-engineer; every technical term translated
      or explicitly flagged.
- [ ] The first sentence states the point; sequential content is numbered; the whole
      thing scans.
- [ ] Nothing was made inaccurate by simplification.
- [ ] Engineer-only detail sits in a "Technical notes" aside, not the body.
- [ ] Format and length match what was asked for.

## Related skills

- [project-manager](../project-manager/SKILL.md): ticket titles, descriptions and QA steps are written in this voice.
- [status-update](../status-update/SKILL.md): a status report is a dashboard plus a short TLDR; this skill owns the TLDR's wording.
- [frontend](../frontend/SKILL.md): UI copy (labels, empty, loading and error states) is written here and placed there.
- [marketing](../marketing/SKILL.md): it decides what a landing, pricing or signup page must get the reader to do and which true evidence it may claim; this skill writes the words.

## Capturing the user's voice (session-handoff protocol)

Record voice/tone preferences, approved phrasings, and term→plain-language
translations the user liked in `LEARNINGS.md` beside this skill, when your copy keeps
one. On "update skills" / after a writing task where the user corrected tone or
wording: add the example (before → after), dedupe, and note the context. Read it before writing so future copy matches the
user's established voice. Keep a running **jargon → plain** glossary there for your
product's domain (this install's: `LOCAL.md` beside this skill, when your copy keeps
one — *Glossary domain*).
