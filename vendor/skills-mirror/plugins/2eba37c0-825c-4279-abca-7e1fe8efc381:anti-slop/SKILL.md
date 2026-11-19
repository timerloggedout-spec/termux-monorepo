---
name: anti-slop
description: Rejects glassmorphism, rainbow CTAs, cartoon empty states, and SaaS visual clutter. Use when reviewing AI-generated UI, polishing visuals, or removing decorative noise.
title: Anti Slop
category: visual-taste
severity: hard-rule
references:
- reference/slop-checklist.md
---

If `.ux-profile.md` exists at the project root, read it before changing layout, color, or type.

### Intent

AI-generated and template-driven UI converges on the same clichés: rainbow buttons, frosted glass panels, cartoon empty states, and decorative chrome that adds no function. This skill bans those patterns so interfaces stay purposeful, readable, and aligned with the rest of the visual-taste skills.

### Hard Rules (Non-Negotiable)

- **No multi-color radial rainbow gradients on standard CTA buttons.** Primary actions use a solid fill or a single-hue subtle gradient (same hue, ≤10% lightness shift). Ban `conic-gradient`, multi-stop rainbow `linear-gradient`, and purple-to-orange radial fills on default buttons.
- **No glassmorphic blur (`backdrop-filter`) without high-contrast boundary.** If blur is used at all, the panel must have a visible 1px border ≥3:1 against whatever shows through, opaque fallback when `backdrop-filter` unsupported, and sufficient text contrast. Default product UI should omit blur entirely.
- **No generic cartoon vector people** (waving, high-fiving, empty-box mascots) in empty states. Use text, actionable CTAs, simple monochrome icons, or product-relevant screenshots — not stock illustration people.
- **No icons inside inputs unless functional.** Allowed: search magnifier, clear/reset control, password visibility toggle. Banned: decorative leading icons on every text field, emoji-style adorners, brand icons inside standard inputs.
- **No unnecessary pill containers around standard text metadata.** Timestamps, author names, file sizes, and tags render as plain text or minimal chips only when they are interactive filters. Do not wrap static metadata in rounded pastel pills for decoration.
- **Anti-slop deletes decoration, not structure.** Remove pills, glass, cartoons, and decorative chrome. Do **not** delete the list frame, row dividers, or search chrome. An empty-looking table after a slop pass is a **fail**, not a pass.

### Design Heuristics & Taste Principles

- When a element's only job is decoration, delete it.
- Prefer one neutral border and whitespace over gradients, blobs, and floating shapes.
- Empty states sell the next action, not illustration budget.
- If it appears in a generic SaaS landing template, assume it is slop until proven functional.
- Cross-check `.ux-profile.md` banned list — it may extend these rules.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Sign-up uses a `conic-gradient` "Get Started" button. Login form inputs each have a leading gray icon. Empty project view shows a cartoon character high-fiving. Settings show "Last updated" inside a lavender pill. A modal uses `backdrop-filter: blur(20px)` with no border on a busy background.

#### ✅ Best Practice

Primary CTA is solid accent fill. Search field keeps one magnifier icon; other fields are label + input only. Empty state: heading, one sentence of value, "Create project" button, optional simple 24px monochrome icon. Metadata runs as 12px secondary text. Modal uses opaque L3 surface, 1px border, optional scrim — no blur.

### Framework-Agnostic Implementation Blueprint

**Audit pass (grep / search changed files):**

```
backdrop-filter
conic-gradient
linear-gradient.*(#.*,#.*,#)   /* multi-hue gradients on buttons */
illustration|empty-state.*svg  /* review for cartoon people */
border-radius: 999             /* pill wrappers on static text */
```

**Replace patterns:**

```css
/* ❌ Slop */
.btn-primary {
  background: conic-gradient(from 180deg, #f00, #ff0, #0f0, #00f, #f0f);
}
.panel {
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.2);
}

/* ✅ Restrained */
.btn-primary {
  background: var(--accent);
}
.panel {
  background: var(--surface-l3);
  border: 1px solid var(--border-l2);
}
```

Use [reference/slop-checklist.md](reference/slop-checklist.md) for the full identification matrix.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present; merge its ban list with this skill.
- [ ] Scan CTAs — no rainbow or multi-hue radial gradients.
- [ ] Scan overlays — no unbounded glassmorphism; border + opaque fallback if blur exists.
- [ ] Scan empty states — no cartoon people illustrations.
- [ ] Scan inputs — icons only where functional (search, clear, toggle).
- [ ] Scan metadata — no decorative pill wrappers on static text.
- [ ] After a slop pass: list frame, row dividers, and search chrome still present — an empty-looking table is a fail.
- [ ] Run slop checklist matrix on any AI-generated or imported component.
