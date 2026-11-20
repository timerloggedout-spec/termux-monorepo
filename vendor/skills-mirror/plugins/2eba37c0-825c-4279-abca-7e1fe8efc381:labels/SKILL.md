---
name: labels
description: Requires visible labels on every input; placeholders only for format hints. Use when building form fields, fixing a11y labeling, or reviewing placeholders.
title: Labels
category: voice
severity: hard-rule
references:
- reference/placeholder-rules.md
---

If `.ux-profile.md` exists at the project root, read it first — especially accessibility target and voice settings.

### Intent

Labels identify fields; placeholders hint at format. Placeholders disappear on focus and fail screen readers when used as the only identifier. Visible labels keep forms scannable, accessible, and usable under stress or distraction.

### Hard Rules (Non-Negotiable)

- **Placeholders NEVER substitute for labels.** Every input must have a persistent visible label.
- **Placeholders only for formatting examples:** e.g., `acme-corp`, `MM/YY`, `name@company.com` — not "Email address" or "Enter your name."
- **Every form input has an associated visible label** programmatically bound to the control (`<label for>` + `id`, or `aria-labelledby` with visible text).
- **Search: `aria-label` without a visible label is allowed only on narrow toolbars** (viewports Narrow / 375). On medium and wide, Search has a visible label or equivalent persistent text (visible “Search” or a search icon + visible name). Aria-label-only on a 1280px page is a fail.

### Design Heuristics & Taste Principles

- Put enduring instructions in helper text below the label, not in the placeholder.
- Labels use nouns or short noun phrases: Email, Company name, Expiry date — not "What's your email?"
- Placeholder contrast must still meet accessibility targets from `.ux-profile.md`; if contrast is weak, drop the placeholder and rely on helper text.
- On Narrow / 375, Search may use `aria-label` (or icon + accessible name) without a visible “Search” label — never placeholder-only. On medium/wide, follow the hard rule above.
- Floating-label patterns are allowed only if the label remains visible after focus (does not rely on placeholder-as-label).

See [reference/placeholder-rules.md](reference/placeholder-rules.md) for accessible bindings and helper text placement.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

An email field shows only placeholder text "Email address" inside the box. A credit card form uses "MM/YY" as the only hint with no Expiry label. A signup form stacks five inputs with placeholders as the sole identifiers.

#### ✅ Best Practice

Each field has a visible label above the control. Email label reads Email; placeholder reads `name@company.com`. Expiry label reads Expiry date; placeholder reads `MM/YY`. Helper text under Password reads At least 8 characters.

### Framework-Agnostic Implementation Blueprint

```html
<div class="field">
  <label for="email">Email</label>
  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    placeholder="name@company.com"
    aria-describedby="email-hint"
  />
  <p id="email-hint" class="hint">We'll send receipts here.</p>
</div>

<div class="field">
  <label for="expiry">Expiry date</label>
  <input
    id="expiry"
    name="expiry"
    inputmode="numeric"
    placeholder="MM/YY"
    aria-describedby="expiry-hint"
  />
</div>
```

Audit: flag any `<input>`, `<select>`, or `<textarea>` without a visible associated label or with placeholder text that reads like a field name.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present (a11y target).
- [ ] Inventory all form controls in scope.
- [ ] Confirm each has a visible, associated label.
- [ ] On medium/wide: Search has a visible label or icon + visible name (aria-label-only only on Narrow / 375).
- [ ] Rewrite placeholders that duplicate or replace labels.
- [ ] Move lasting guidance to helper text per [reference/placeholder-rules.md](reference/placeholder-rules.md).
- [ ] Verify programmatic association (`for`/`id`, `aria-labelledby`, or documented pattern).
