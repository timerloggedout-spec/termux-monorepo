---
name: reduced-motion
description: Honors prefers-reduced-motion with instant or opacity-only fallbacks. Use when adding animation, transitions, parallax, autoplay, or accessibility motion work.
title: Reduced Motion
category: animation
severity: hard-rule
references:
- reference/motion-a11y.md
---

If `.ux-profile.md` exists at the project root, read accessibility target notes, then apply this skill whenever motion exists.

### Intent

Some users need minimal motion for vestibular, attention, or preference reasons. The interface must remain fully usable and understandable when motion is reduced. Motion is never the only way to communicate state.

### Hard Rules (Non-Negotiable)

- **Honor `prefers-reduced-motion: reduce`:** under that preference, use **instant** changes or **opacity-only** fades ≤150ms. No translate, scale, or parallax.
- **No parallax, autoplay decoration, or bounce** when reduced motion is requested (and avoid them in product chrome generally per `motion`).
- **Do not convey meaning by motion alone.** Pair every animated state with a non-motion cue: text, icon change, color/contrast (meeting a11y target), or `aria-live` / `aria-busy`.

### Design Heuristics & Taste Principles

- Default stylesheet can assume motion; always provide a `@media (prefers-reduced-motion: reduce)` override that disables or replaces transforms.
- Prefer `animation: none` and `transition: none` (or opacity-only) rather than long alternate choreography.
- Video/Lottie in empty states: pause or show a static frame under reduced motion.
- Loading skeletons: static muted blocks, not shimmer, under reduced motion (aligns with `loaders`).
- Test both preference values before shipping UI that moves.

See [reference/motion-a11y.md](reference/motion-a11y.md) for CSS patterns and meaning-pair examples.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Success is shown only as a green check that bounces in. Drawer still slides 300px when the user has reduced motion enabled. A hero parallax ignores the media query.

#### ✅ Best Practice

Success shows the word **Saved** (or toast) plus a static check icon; optional 100ms opacity. Under `prefers-reduced-motion: reduce`, the drawer appears/disappears with opacity only or instantly. Parallax is disabled.

### Framework-Agnostic Implementation Blueprint

```css
.drawer {
  transition:
    transform var(--motion-200) var(--ease-out),
    opacity var(--motion-200) var(--ease-out);
}

@media (prefers-reduced-motion: reduce) {
  .drawer {
    transition: opacity var(--motion-100) ease;
    transform: none !important;
  }

  .drawer[data-open="false"] {
    opacity: 0;
  }

  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    /* Prefer scoped overrides; global reset is a last resort */
  }
}
```

Prefer scoped overrides per component over a blunt universal reset when possible.

### Agent Checklist

- [ ] Every new transition/animation has a `prefers-reduced-motion: reduce` path.
- [ ] Reduced path is instant or opacity-only (no translate/scale/parallax).
- [ ] State meaning also exists in text, icon, or ARIA — not motion alone.
- [ ] Skeletons/loaders disable shimmer under reduced motion.
- [ ] Verify against [reference/motion-a11y.md](reference/motion-a11y.md).
