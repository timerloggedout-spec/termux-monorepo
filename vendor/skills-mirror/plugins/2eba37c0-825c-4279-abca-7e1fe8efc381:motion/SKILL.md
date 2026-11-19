---
name: motion
description: Defines duration tokens, easing, and which properties may animate. Use when adding CSS transitions, keyframes, motion tokens, or reviewing decorative animation.
title: Motion
category: animation
severity: hard-rule
references:
- reference/timing-tokens.md
---

If `.ux-profile.md` exists at the project root, read it before adding motion — especially aesthetic reference (Linear ≈ instant, Stripe/Notion restrained, Apple short and purposeful).

### Intent

Motion should clarify change, not decorate. Short, consistent durations and restrained easing make interfaces feel calm and fast. Animating layout properties or using bounce/elastic curves on product chrome feels cheap and hurts performance.

### Hard Rules (Non-Negotiable)

- **Duration tokens only:** 100ms, 150ms, 200ms, or 300ms. No one-off values (e.g. 180ms, 450ms, 800ms) unless documented as an optical exception in [reference/timing-tokens.md](reference/timing-tokens.md).
- **Easing:** ease-out on enter; ease-in on exit. Ban bounce, elastic, spring-overshoot, and back curves on product chrome (toolbars, dialogs, buttons, lists).
- **Animatable properties:** `transform` and `opacity` only. Never animate `width`, `height`, `top`, `left`, `margin`, or `padding` for UI chrome.
- **No infinite decorative loops** on static chrome (pulsing borders, forever-rotating logos, looping blob backgrounds). Functional loops (progress indeterminate, live activity) are allowed when they convey ongoing work.

### Design Heuristics & Taste Principles

- Match aesthetic density: Linear → prefer 100–150ms or none; Stripe / Notion → 150–200ms; Apple Native → up to 300ms when purposeful.
- Prefer opacity fades for state changes; use small translates (4–8px) for enter from edge, not large slides across the viewport.
- One motion language per surface family — do not mix bounce buttons with linear drawers.
- Prefer CSS transitions / `@keyframes` over JS animation libraries unless the stack already depends on one.
- Skeleton shimmer (from `loaders`) may use a longer loop; still honor `reduced-motion`.

See [reference/timing-tokens.md](reference/timing-tokens.md) for the token table and property whitelist.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

A drawer animates `height` from 0 to auto over 800ms with `cubic-bezier` bounce. Buttons use elastic scale on hover. A marketing-style looping gradient pulse sits behind the settings page.

#### ✅ Best Practice

Drawer enters with `transform: translateX(100%) → 0` and opacity over 200ms ease-out; exits 150ms ease-in. Hover uses opacity or a 1px border change — no scale bounce. Static pages have no looping decoration.

### Framework-Agnostic Implementation Blueprint

```css
:root {
  --motion-100: 100ms;
  --motion-150: 150ms;
  --motion-200: 200ms;
  --motion-300: 300ms;
  --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in: cubic-bezier(0.7, 0, 0.84, 0);
}

.drawer {
  transition:
    transform var(--motion-200) var(--ease-out),
    opacity var(--motion-200) var(--ease-out);
}

.drawer.is-exiting {
  transition-timing-function: var(--ease-in);
  transition-duration: var(--motion-150);
}
```

### Agent Checklist

- [ ] Read `.ux-profile.md` aesthetic notes for motion restraint.
- [ ] Map every duration to 100 / 150 / 200 / 300ms.
- [ ] Confirm enter uses ease-out and exit uses ease-in.
- [ ] Confirm only `transform` / `opacity` animate (no layout properties).
- [ ] Remove bounce, elastic, and infinite decorative loops on chrome.
- [ ] Cross-check tokens in [reference/timing-tokens.md](reference/timing-tokens.md).
