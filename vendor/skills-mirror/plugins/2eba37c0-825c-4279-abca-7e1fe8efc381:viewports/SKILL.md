---
name: viewports
description: "Keeps layouts usable from 375px to 1280px: no page overflow, collapsed chrome, profile touch targets, and tap-first actions. Use when building or reviewing any page, layout, chrome, sidebar, table, or overlay that renders in a browser."
title: Viewports
category: visual-taste
severity: hard-rule
references:
- reference/breakpoint-tokens.md
---

If `.ux-profile.md` exists at the project root, read it before changing layout, color, or type.

### Intent

Desktop-first layouts break on a phone: a locked sidebar, a 1440px canvas, hover-only actions, and type squeezed below 12px. This skill locks three viewport tokens and a short contract so every screen works at 375px and 1280px. Pattern-specific stacking lives in `page-patterns`, not here.

### Hard Rules (Non-Negotiable)

- **No page-level horizontal overflow at 375px or 1280px.** `document.documentElement.scrollWidth` must not exceed `clientWidth` at either width. Tables and boards may scroll *inside* one region. Never shrink type below 12px to fit (`typography`).
- **Hit targets match `.ux-profile.md`.** WCAG AA: 44×44px. AAA: 48×48px. If the profile is missing, use 44×44. Icon-only controls get padding to meet the floor; a 16px glyph is not the tap area.
- **Hover is extra, not the only path.** Every primary action exists in the layout without hover. Hover-only chrome is allowed only inside `@media (hover: hover)`.
- **Cap the main page, not the app.** `html`, `body`, `.app`, and chrome (sidebar, header) are `width: 100%` with **no** max-width. Apply `max-width: var(--vp-wide)` only to the main page content (`main`, `.page`). Ban a root, shell, or card locked to a pixel width ≥768px with no wrap or inner-scroll plan.
- **Three tokens only — narrow / medium / wide.** Do not invent a fourth breakpoint for a single screen. Values live in [reference/breakpoint-tokens.md](reference/breakpoint-tokens.md).
- **Chrome collapses on narrow.** A persistent sidebar (≥200px) on a 375px viewport is a fail. Use a menu control that opens the same nav. Then apply the named pattern’s **Narrow** line in the `page-patterns` catalog.

### Design Heuristics & Taste Principles

- Dense desktop profiles (Linear, Raycast) may still lead with the wide layout. Prove 375px before done.
- Prefer wrap and stack over a second horizontal scrollbar on the page. One inner overflow region per view is enough.
- Slide-overs go full-height on narrow (`surfaces`).
- Safe-area insets and native device chrome are out of scope. This skill is viewport CSS.
- Why (Laws of UX): Bigger, closer targets are faster to hit (Fitts’s Law, Jon Yablonski). That is why the hit area is 44×44 or 48×48, not the glyph. https://lawsofux.com/fittss-law/

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

App shell is `width: 1440px` or `max-width: 1280px` on `.app` / `.shell`, so the sidebar and header sit in a centered column. Sidebar stays 240px on a phone. Row “Delete” appears only on hover. Icon buttons are 24×24. The projects table shrinks cells to 11px so every column fits.

#### ✅ Best Practice

Shell and sidebar span the viewport. `main` (or `.page`) is `width: 100%` with `max-width: var(--vp-wide)` and centered. At narrow, a menu button opens the same nav; the sidebar rail is gone. Delete lives in the row ⋯ menu and is always tappable. Icon buttons are at least 44×44. The table keeps 12px+ type and scrolls inside its region.

### Framework-Agnostic Implementation Blueprint

```css
:root {
  --vp-narrow: 375px;
  --vp-medium: 768px;
  --vp-wide: 1280px;
}

.app,
.shell {
  width: 100%;
  max-width: none;
}

main,
.page {
  width: 100%;
  max-width: var(--vp-wide);
  margin-inline: auto;
}

.hit {
  min-width: 44px; /* 48px when profile is AAA */
  min-height: 44px;
}

@media (max-width: 767.98px) {
  .sidebar { display: none; }
  .nav-menu { display: inline-flex; }
}

@media (hover: hover) {
  .row-extra { opacity: 0; }
  .row:hover .row-extra,
  .row:focus-within .row-extra { opacity: 1; }
}
```

```
pageOverflows = document.documentElement.scrollWidth
              > document.documentElement.clientWidth
```

Prove both 375 and 1280 (browser tools or a resized window) before marking UI done. If there is no browser, the overflow row is Unproven — do not mark it pass.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present; note hit-target size (44 or 48).
- [ ] Use only narrow / medium / wide from [reference/breakpoint-tokens.md](reference/breakpoint-tokens.md).
- [ ] `max-width: var(--vp-wide)` is on `main` / `.page` only — not `html`, `body`, `.app`, `.shell`, sidebar, or header.
- [ ] Primary actions work without hover; hover extras sit inside `(hover: hover)`.
- [ ] Hit targets meet the profile floor.
- [ ] Narrow: sidebar rail gone; the same destinations are reachable from a menu.
- [ ] Apply the named pattern’s **Narrow** line in the `page-patterns` catalog (or marketing).
- [ ] Prove `scrollWidth <= clientWidth` at 375 and 1280.
