---
name: typography
description: Defines typographic scales, weight limits, and line-height pairing. Use when setting type styles, headings, body copy sizes, or fixing noisy type hierarchies.
title: Typography
category: visual-taste
severity: hard-rule
references:
- reference/scale-math.md
---

If `.ux-profile.md` exists at the project root, read it before changing layout, color, or type.

### Intent

Readable interfaces use a small, predictable type system. Hierarchy comes from size and spacing — not from piling on font weights. This skill limits weight noise, enforces a minimum readable size, and pairs line-height inversely with font size so headings feel tight and body copy feels open.

### Hard Rules (Non-Negotiable)

- **Maximum 3 font weights app-wide (e.g., 400 / 500 / 600). Never use >700.** Bold at 700+ creates harsh contrast and encourages weight-based hierarchy instead of size-based hierarchy. If emphasis is needed beyond 600, use size, color, or spacing — not heavier weight.
- **Body 1rem (16px); secondary 0.875rem (14px); meta 0.75rem (12px). No text below 12px.** These three sizes cover UI copy, supporting text, and legal/meta. Display and heading sizes scale up from 1rem using the modular scale in [reference/scale-math.md](reference/scale-math.md).
- **Primary content is body or secondary — never meta.** Table cells, board cards, list rows, and form values use body (16px) or secondary (14px). `text-xs` / 12px is **meta only** (timestamps, legal, kbd, helper). A whole table at 12px is a fail even though 12px is the floor.
- **Line-height decreases as size increases.** Display and headings: `1.1`–`1.25`. Body and secondary: `1.5`–`1.6`. Meta at 12px may use up to `1.4` for multi-line legal text. Reject unitless line-heights below 1.1 on any size or above 1.6 on body text.

### Design Heuristics & Taste Principles

- One typeface family for UI; a second only for marketing/display if the profile allows it.
- Create hierarchy with at most 4–5 distinct sizes on one screen (meta, secondary, body, subheading, heading).
- Prefer medium (500) for interactive labels and semibold (600) for page titles — not bold (700).
- Letter-spacing: default for body; slight tightening (`-0.01em` to `-0.02em`) only on large display sizes ≥2rem.
- If titles use a **variable font** + negative letter-spacing (`tracking-tight`), screenshot for last-letter ghosting. If glyphs double or smear, reduce tracking or drop the variable cut for UI.
- Truncate with ellipsis only after layout constraints are exhausted; never shrink below 12px to fit.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

A dashboard uses 400, 500, 600, 700, and 800 weights. Table cells are `text-xs` (12px) — the legal floor used as the body of the page. Headings use `line-height: 1.6` while body uses `1.3`. Six arbitrary font sizes appear on one page. Page titles on a variable font with `tracking-tight` show last-letter ghosting that the a11y tree cannot see.

#### ✅ Best Practice

Weights locked to 400 (body), 500 (labels/buttons), 600 (headings). Sizes: 12px meta only (timestamps, legal, kbd), 14px secondary or 16px body for table cells and list rows, scale steps for H3/H2/H1 per Minor Third. H1 at 2rem uses `line-height: 1.2`; body at 1rem uses `line-height: 1.55`. No size below 12px. Computed `font-size` on the primary region matches body or secondary — not class-name guesses.

### Framework-Agnostic Implementation Blueprint

```css
:root {
  --font-regular: 400;
  --font-medium: 500;
  --font-semibold: 600;

  --text-meta: 0.75rem;      /* 12px */
  --text-secondary: 0.875rem; /* 14px */
  --text-body: 1rem;          /* 16px */

  --leading-tight: 1.2;
  --leading-body: 1.55;
  --leading-meta: 1.4;
}

body {
  font-size: var(--text-body);
  font-weight: var(--font-regular);
  line-height: var(--leading-body);
}

h1, h2, h3 {
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
}

.text-meta {
  font-size: var(--text-meta);
  line-height: var(--leading-meta);
}
```

Generate heading sizes from the scale table in `reference/scale-math.md`; do not hand-pick pixel values.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Count distinct font weights in changed files — must be ≤3, none >600.
- [ ] Confirm no computed font-size below 12px (0.75rem at 16px root).
- [ ] Read **computed** `font-size` on the primary region (table cells, list rows, form values) — body (16px) or secondary (14px); class names alone are not enough.
- [ ] Confirm 12px / `text-xs` is used only for meta (timestamps, legal, kbd, helper) — not the whole table.
- [ ] Verify body/secondary/meta map to 1rem / 0.875rem / 0.75rem.
- [ ] Check line-height: headings 1.1–1.25, body 1.5–1.6.
- [ ] Replace weight-based emphasis with size or spacing where needed.
