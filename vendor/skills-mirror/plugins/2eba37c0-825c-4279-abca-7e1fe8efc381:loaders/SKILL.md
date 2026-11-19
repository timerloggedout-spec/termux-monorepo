---
name: loaders
description: Chooses loaders by duration — none under 100ms, inline to 1s, skeletons beyond. Use when adding spinners, skeletons, async fetches, or fixing flicker.
title: Loaders
category: feedback
severity: hard-rule
references:
- reference/timing-benchmarks.md
---

If `.ux-profile.md` exists at the project root, read it before adding loading UI.

### Intent

Loading feedback should match wait time so the interface feels instant when it is, honest when it isn't, and stable when content is slow. Wrong loader choice causes flicker, anxiety, or layout jump.

### Hard Rules (Non-Negotiable)

- **Duration < 100ms:** show no loader. Execute immediately; a spinner under 100ms flickers and feels slower.
- **Duration 100ms–1000ms:** use an inline spinner or status indicator on the triggering control (button disabled state + spinner, or adjacent inline status). Localize feedback to where the user acted.
- **Duration > 1000ms for full-page or content blocks:** render a **structural skeleton** matching the incoming layout geometry. Never use a giant centered full-page spinner for content loads.

### Design Heuristics & Taste Principles

- Delay showing any loader until ~100ms has elapsed (debounce) so fast responses never flash chrome.
- Skeleton blocks mirror real layout: same column widths, row heights, avatar circles, and text line stubs.
- Prefer reduced motion: respect `prefers-reduced-motion` — static skeleton blocks or opacity pulse, not aggressive shimmer.
- Button loading: keep label readable or swap to verb + ing (Saving…) with `aria-busy="true"` on the control.
- Parallel requests: one skeleton for the container, not a spinner per cell unless cells load independently >1s.
- Why (Laws of UX): Keep the loop tight so neither side waits (Doherty Threshold, Jon Yablonski). https://lawsofux.com/doherty-threshold/

See [reference/timing-benchmarks.md](reference/timing-benchmarks.md) for perceptual thresholds and skeleton shimmer rhythm.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Every API call shows a full-screen spinner for 150ms, causing a flash. A dashboard with 2s load time shows a centered spinning logo on a blank white page. Save button shows no feedback for 800ms then jumps to success.

#### ✅ Best Practice

Fast saves complete with no loader. An 800ms save disables the Save changes button and shows an inline spinner beside the label. A 2s dashboard render shows a skeleton with sidebar, header, and three card-shaped placeholders matching the final grid.

### Framework-Agnostic Implementation Blueprint

```javascript
const LOADER_DELAY_MS = 100;
const SKELETON_THRESHOLD_MS = 1000;

async function onSubmit(button, fetchContent) {
  const t0 = performance.now();
  button.setAttribute('aria-busy', 'true');
  button.disabled = true;

  const showInlineTimer = setTimeout(() => {
    button.classList.add('is-loading'); // inline spinner
  }, LOADER_DELAY_MS);

  try {
    await fetchContent();
  } finally {
    clearTimeout(showInlineTimer);
    button.removeAttribute('aria-busy');
    button.disabled = false;
    button.classList.remove('is-loading');
  }
}

// Content block: after 1s, swap spinner for skeleton matching layout
```

```css
.skeleton-card {
  height: 120px;
  border-radius: 8px;
  background: var(--surface-muted);
}

@media (prefers-reduced-motion: no-preference) {
  .skeleton-shimmer {
    animation: shimmer 1.5s ease-in-out infinite;
  }
}
```

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Classify each async operation by expected duration band.
- [ ] Apply 100ms debounce before showing any loader.
- [ ] Use inline control feedback for 100ms–1s waits.
- [ ] Use layout-matched skeletons for >1s content loads — no full-page spinners.
- [ ] Honor `prefers-reduced-motion` per [reference/timing-benchmarks.md](reference/timing-benchmarks.md).
