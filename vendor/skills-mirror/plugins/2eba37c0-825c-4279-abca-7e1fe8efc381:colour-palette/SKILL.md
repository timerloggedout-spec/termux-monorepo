---
name: colour-palette
description: Applies 60-30-10 colour distribution and elevation via borders then soft shadows. Use when choosing surfaces, accents, borders, shadows, or dark-mode depth.
title: Colour Palette
category: visual-taste
severity: hard-rule
references:
- reference/elevation-tokens.md
---

If `.ux-profile.md` exists at the project root, read it before changing layout, color, or type.

### Intent

Restrained interfaces feel layered, not loud. Color budget follows 60-30-10 so the eye knows where to act. Depth comes from subtle borders and soft shadows — not heavy drop-shadows or saturated surface fills. This skill keeps surfaces readable in light and dark mode without decorative noise.

### Hard Rules (Non-Negotiable)

- **60% canvas/background, 30% structural surface (cards/sidebars), 10% accent (interactive).** Measured on a **screenshot** of a typical viewport — not token counts, class names, or “accent is on the CTA.” Sample major regions from the image. One primary accent hue carries CTAs, links, and focus; neutrals carry everything else. See surface roles in [reference/elevation-tokens.md](reference/elevation-tokens.md). Fail if structural area is ~0%.
- **A list, table, or board is an L1 surface.** It must have a 1px subtle border, **or** a one-step background shift **and** hairline row/column dividers. A table of text on L0 canvas is a fail.
- **“Borders rare” / paper profiles still require hairlines on lists.** Stripping decorative card chrome is fine. Stripping the table frame is not.
- **Elevation via 1px subtle border first.** Every raised surface (L1+) defines separation with a 1px border at low contrast before any shadow. Light mode: border alpha ~6–12% of foreground. Dark mode: border alpha ~8–14% of foreground or a +4–8% lightness step.
- **Soft diffused shadows: alpha <0.08 in light mode.** If shadow is used, `box-shadow` color alpha must stay below 0.08. Prefer large blur, low spread, y-offset 1–4px. **Never hard drop-shadows** (high alpha, tight blur, strong offset, or `filter: drop-shadow` mimicking a sticker edge).
- **Dark mode: subtle edge lighting, not glow stacks.** Use top-edge highlights (`inset 0 1px 0 rgba(255,255,255,0.04–0.08)`) and border contrast instead of bright outer glows. Shadow alpha may be higher on dark canvas but must remain diffuse — no crisp dark halos.

### Design Heuristics & Taste Principles

- Accent color appears on primary buttons, active nav, links, and focus — not on large background fills.
- Structural surfaces (cards, sidebars) differ from canvas by one neutral step, not a new hue.
- Hover states deepen border contrast slightly before adding shadow.
- Overlays (modals, menus) use L2/L3 tokens; never the same flat fill as the page canvas.
- Respect `.ux-profile.md` contrast target when picking border and text pairs.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

A dashboard background is saturated blue (40% area), cards are pure white with `box-shadow: 0 8px 24px rgba(0,0,0,0.25)`, and every section header has a gradient pill. Five accent colors compete on one screen. Dark mode uses neon outer glow on cards. A Client Groups list is ~95% empty white canvas: table text sits on L0 with no panel, no border, and no hairlines — 60-30-10 fails in the viewport even though the CTA uses accent.

#### ✅ Best Practice

Canvas neutral (60% visual weight), sidebar and cards one neutral step up (30%), primary buttons and active links use a single accent (10%). Cards use `border: 1px solid` at 8% alpha plus optional `box-shadow: 0 1px 3px rgba(0,0,0,0.06)`. Dark mode adds a 1px top inset highlight; no hard shadows. The list/table sits in a quiet L1 panel with a 1px subtle border and hairline row dividers — paper profiles keep the frame, not a blank spreadsheet on the canvas.

### Framework-Agnostic Implementation Blueprint

```css
:root {
  --surface-canvas: /* L0 */;
  --surface-raised: /* L1 */;
  --border-subtle: color-mix(in srgb, var(--foreground) 8%, transparent);
  --shadow-soft: 0 1px 3px rgba(0, 0, 0, 0.06);
  --accent: /* single interactive hue */;
}

.card {
  background: var(--surface-raised);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-soft);
}

[data-theme="dark"] .card {
  box-shadow: none;
  border-color: color-mix(in srgb, var(--foreground) 12%, transparent);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.btn-primary {
  background: var(--accent);
}
```

Map L0–L3 surfaces and z-index from `reference/elevation-tokens.md`. Audit shadow alpha in DevTools computed styles.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Estimate 60-30-10 from a **screenshot** of the changed screen (not token counts); fail if structural area is ~0%; reduce accent area if >10%.
- [ ] List / table / board is an L1 surface (1px border, or one-step bg shift **and** hairlines) — not bare text on L0.
- [ ] Every raised surface has a 1px subtle border before shadow.
- [ ] Light-mode shadow alphas are <0.08; no hard drop-shadows.
- [ ] Dark mode uses edge lighting/inset highlights, not outer glow stacks.
- [ ] Single primary accent hue for interactive elements.
