---
description: Transform a vague feature idea into a sharp one-pager BEFORE /one-shot fires. Output is a problem statement + MVP scope + "not doing" list + key assumptions. Cuts /one-shot iteration cost by making sure the architect agent gets a concrete contract. Inspired by Addy Osmani's idea-refine skill.
argument-hint: "<vague feature idea in quotes>"
allowed-tools: Read, Write, Grep
destructive: true
read-only: false
---

# /refine — sharpen a vague idea before /one-shot

You are running the **idea-refine** workflow. The user has a vague feature
idea (`$ARGUMENTS`). Your job is to produce a concrete one-pager they
can review and then hand to `/one-shot` as a precise feature request.

This is NOT code generation. This is requirements compression. You
write Markdown, not Python.

## Process

Run three phases. Don't skip any.

### Phase 1 — Expand (divergent thinking, 1 minute)

List **3-5 plausible interpretations** of the user's idea. For each:
- What problem would it actually solve?
- Who's the user?
- What's the smallest version that would prove it works?

Don't filter yet. Surface assumptions you'd otherwise make silently.

### Phase 2 — Evaluate (stress-test, 1 minute)

For each interpretation:
- What's the strongest objection to building it?
- What's the cheapest thing that could go wrong on day 1 of production?
- Is there a simpler version that gets 80% of the value?

Eliminate interpretations that fail under their strongest objection.

### Phase 3 — Sharpen (output, the final 80%)

Produce a Markdown one-pager and write it to the appropriate path:

If the user's project has `docs/`, write to `docs/refined/{kebab-slug}.md`.
Otherwise write to `.refined/{kebab-slug}.md` at the project root.

**Template:**

```markdown
# Refined: {one-line restatement of the idea}

## Problem

One paragraph. Whose pain is this? When does it happen? What does
"solved" look like?

## Recommended direction

The single interpretation that survived Phase 2. State it in one sentence.

## MVP scope (what gets built)

A bullet list. Each bullet is something a /one-shot architect can spec.
Avoid adjectives ("robust", "scalable"); use nouns + verbs.

- [ ] {entity or capability 1}
- [ ] {entity or capability 2}
- [ ] {API surface, e.g. "POST /api/v1/carts/{id}/checkout"}

## NOT doing (explicit non-scope)

A bullet list of things the user might EXPECT but we're excluding. This
is the single most valuable section — it prevents scope creep mid-build.

- {feature deliberately not in MVP}
- {edge case explicitly deferred}

## Key assumptions

A bullet list. Each one is something that, if wrong, invalidates the
recommendation. State them so future-you knows what to re-check.

- {assumption 1 — about user behaviour or system state}
- {assumption 2 — about scale or load}

## Suggested /one-shot invocation

```bash
/one-shot "{the precise, sharpened feature description}" @./{project-path}
```

If the user passes `--review` to that, they'll get a chance to inspect
the spec.json before any expensive agents fire.

## Why this is the right slice

One paragraph. What makes this version (vs the larger ideas in Phase 1)
the cheapest path to learning whether the underlying premise is true?
```

## Hard rules

1. **Output the file path you wrote.** The user needs to know where to find it.

2. **Never skip the "NOT doing" section.** It's the single most valuable
   output. If you can't think of anything to exclude, you haven't
   sharpened enough — go back to Phase 2.

3. **Never include implementation detail** (ORM choice, framework
   version, table schema). That's `/one-shot`'s job. The refine output
   stays at the requirements layer.

4. **Don't pad.** Bullets > paragraphs. Each section should fit on
   one screen.

5. **Surface uncertainty explicitly.** If you can't tell what the user
   meant, write a `## Open questions` section at the top with 2-3
   specific questions and stop. Don't guess.

6. **No timelines, no team sizes, no business cases.** Those belong in
   product docs. /refine is purely the technical-scope sharpening.
