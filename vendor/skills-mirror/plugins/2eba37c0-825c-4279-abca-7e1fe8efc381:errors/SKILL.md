---
name: errors
description: Writes error copy that never blames the user and always offers recovery. Use when writing errors, toasts, failure states, or support-facing messages.
title: Errors
category: voice
severity: hard-rule
references:
- reference/error-taxonomy.md
---

If `.ux-profile.md` exists at the project root, read it first — especially **Brand tone and microcopy voice** (Utilitarian vs Warm vs Direct).

### Intent

Errors are system conversations, not accusations. Copy should reduce anxiety, preserve trust, and give one clear next step. Users should never feel they "failed"; the product failed to complete their intent and must help them recover.

### Hard Rules (Non-Negotiable)

- **Never blame the user.** Ban phrasing like "You entered an invalid email." Use "Enter an email address like name@domain.com."
- **Errors answer three things in fewer than two sentences:** (1) what happened in plain language, (2) why it matters to their work or data, (3) the immediate step that recovers state.
- **Technical errors:** provide a one-click **Copy error details** action for support. Never dump stack traces, raw HTTP codes, or database errors into the primary UI.

### Design Heuristics & Taste Principles

- Lead with recovery, not diagnosis: "Check your connection and try again" before "Network request failed."
- Use neutral subject: "This email isn't valid" or "We couldn't save your changes" — not "Your password is wrong."
- Match severity to surface: inline field errors for fixable input; toasts for transient failures; banners for blocked workflows; full-page only when the entire view is unusable.
- Destructive failure (data loss risk): state what was preserved and what was not.
- Warm voice profiles may add brief empathy ("Something went wrong on our end") but still stay under two sentences and include a recovery step.

See [reference/error-taxonomy.md](reference/error-taxonomy.md) for toast vs inline vs banner vs full-page templates.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

"You entered an invalid email address." A red toast shows `Error 500: INTERNAL_SERVER_ERROR` with a stack trace. A failed save says "Submission failed. Bad request."

#### ✅ Best Practice

"Enter an email address like name@domain.com." A toast reads "We couldn't save your changes. Check your connection and try again." with a Try again button. A server error shows "Something went wrong" with Copy error details and Try again — details copied to clipboard, not displayed inline.

### Framework-Agnostic Implementation Blueprint

```html
<!-- Inline field error (blameless + format hint) -->
<p id="email-error" role="alert">
  Enter an email address like name@domain.com
</p>

<!-- Transient failure toast -->
<div role="status" aria-live="polite">
  <p>We couldn't save your changes. Check your connection and try again.</p>
  <button type="button">Try again</button>
</div>

<!-- Technical failure (support path) -->
<div role="alert">
  <p>Something went wrong. Try again or copy details for support.</p>
  <button type="button" data-copy="error-ref-abc123">Copy error details</button>
  <button type="button">Try again</button>
</div>
```

Copy handler: serialize `{ code, ref, timestamp, route }` to clipboard — never the full stack in the visible message.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present (tone).
- [ ] Scan all error strings for "you/your" blame patterns and rewrite.
- [ ] Confirm each error is ≤2 sentences and includes a recovery step or action.
- [ ] Replace raw codes/traces in UI with Copy error details.
- [ ] Match error surface to taxonomy in [reference/error-taxonomy.md](reference/error-taxonomy.md).
- [ ] Verify recovery actions use verb-first labels (Try again, Copy error details).
