---
name: transitions
description: Enter/exit patterns for overlays and lists without layout jump. Use when animating drawers, dialogs, popovers, route changes, or staggered lists.
title: Transitions
category: animation
severity: hard-rule
references:
- reference/enter-exit.md
---

If `.ux-profile.md` exists at the project root, read it before changing overlay or list motion. Pair with `surfaces` for which surface type to use, and `motion` for duration/easing tokens.

### Intent

Enter and exit should reinforce the surface model: slide-overs slide, popovers fade/scale lightly, routes swap without fighting focus. Motion must never steal Escape, trap focus incorrectly, or shove surrounding layout.

### Hard Rules (Non-Negotiable)

- **Overlay enter/exit matches `surfaces`:** slide-over uses horizontal translate; popover uses opacity (± slight scale ≤1.02); full-page routes do not fake a modal slide unless the surface skill chose a drawer.
- **Esc and focus stay available during motion.** Exit animation can cancel; never block Escape until the animation finishes. Focus trap rules from `keyboard` still apply while the overlay is open.
- **List stagger ≤30ms per item**, total stagger budget ≈200ms. Longer cascades feel theatrical and slow.
- **Reserve space** so open/close does not shift siblings (fixed drawer width, absolute overlay, or reserved inline-edit height). Zero layout jump — same spirit as inline edit in `surfaces`.

### Design Heuristics & Taste Principles

- Exit slightly faster than enter (e.g. enter 200ms, exit 150ms).
- Prefer animating the overlay panel, not the entire page backdrop blur radius.
- Backdrop opacity may fade in 150–200ms; keep backdrop static in reduced motion.
- Stagger only when it clarifies grouping (new list batch); never stagger every keystroke filter update.
- Coordinate with `loaders`: do not run a dramatic enter on a skeleton that will immediately swap.

See [reference/enter-exit.md](reference/enter-exit.md) for surface-specific patterns.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Opening a slide-over expands document height and pushes the list down. List items cascade in over 80ms × 40 rows (~3s). Escape is ignored until the 500ms close animation completes.

#### ✅ Best Practice

Slide-over is `position: fixed` with translateX enter/exit. Esc closes immediately (exit may continue visually). A 12-row list uses ≤30ms stagger with a 200ms total cap — or no stagger for filter updates.

### Framework-Agnostic Implementation Blueprint

```css
.slide-over {
  position: fixed;
  inset-block: 0;
  inset-inline-end: 0;
  width: min(420px, 100vw);
  transform: translateX(100%);
  opacity: 0;
  transition:
    transform var(--motion-200) var(--ease-out),
    opacity var(--motion-200) var(--ease-out);
}

.slide-over[data-open="true"] {
  transform: translateX(0);
  opacity: 1;
}

.list-item {
  transition: opacity var(--motion-150) var(--ease-out);
}
/* stagger via --i * 30ms, clamp total ≤200ms — see enter-exit.md */
```

### Agent Checklist

- [ ] Confirm surface type with `surfaces` before choosing enter/exit.
- [ ] Overlay is fixed/absolute so siblings do not reflow.
- [ ] Esc works during enter/exit; focus restore still happens on close.
- [ ] Stagger ≤30ms/item and ≤~200ms total (or none).
- [ ] Durations/easing match `motion` tokens.
- [ ] Review patterns in [reference/enter-exit.md](reference/enter-exit.md).
