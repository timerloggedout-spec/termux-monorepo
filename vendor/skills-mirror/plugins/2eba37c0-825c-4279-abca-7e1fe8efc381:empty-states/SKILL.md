---
name: empty-states
description: Builds actionable empty and filtered-zero states with clear CTAs. Use when building empty views, onboarding zeros, or no-search-results screens.
title: Empty States
category: feedback
severity: hard-rule
references:
- reference/activation-patterns.md
---

If `.ux-profile.md` exists at the project root, read it first — especially banned anti-aesthetics (no cartoon illustration slop) and voice tone.

### Intent

Empty views are onboarding moments, not dead ends. A zero state should explain what belongs in the space, why filling it matters, and offer one obvious action to start. Filtered empties must help users escape the trap they created.

### Hard Rules (Non-Negotiable)

- **Zero states are never dead ends.** Every empty state includes: (1) a header stating what belongs here, (2) one sentence on the value of populating the view, (3) a primary CTA to create or import immediately.
- **Filtered search empty:** include a one-click **Clear all filters** action (or equivalent reset) in addition to explaining no matches.

### Design Heuristics & Taste Principles

- Primary CTA uses verb-first labels from `verbs`: Create project, Import contacts — not Get started alone unless paired with a specific verb button.
- Keep copy short: headline + one supporting sentence + one primary action; secondary link optional (Learn how importing works).
- First-use empty may add a minimal 2–3 step hint list; filtered empty should not repeat onboarding.
- Respect `.ux-profile.md` ban list: no generic cartoon people waving; prefer typography, simple icon, or whitespace.
- Tables and lists: empty state occupies the content region at the same footprint as populated data to avoid layout jump.

See [reference/activation-patterns.md](reference/activation-patterns.md) for first-use vs filtered-out templates.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Projects page shows only "No data." with no action. Search with filters applied shows "No results found." and nothing else. A cartoon illustration of people high-fiving fills the screen with no CTA.

#### ✅ Best Practice

Projects page: headline **No projects yet**, body "Create a project to organize tasks and track progress.", button **Create project**. Filtered search: **No projects match your filters**, body "Try broader terms or reset filters.", buttons **Clear all filters** and **Create project**.

### Framework-Agnostic Implementation Blueprint

```html
<section class="empty-state" aria-labelledby="empty-title">
  <h2 id="empty-title">No projects yet</h2>
  <p>Create a project to organize tasks and track progress.</p>
  <a href="/projects/new" class="button-primary">Create project</a>
</section>

<!-- Filtered zero -->
<section class="empty-state" aria-labelledby="filter-empty-title">
  <h2 id="filter-empty-title">No projects match your filters</h2>
  <p>Try broader terms or reset filters.</p>
  <button type="button" data-action="clear-filters">Clear all filters</button>
</section>
```

State machine: `loading → populated | first-use-empty | filtered-empty`. Never render a blank content area without choosing the correct empty variant.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present (voice, banned visuals).
- [ ] Identify empty type: first-use vs filtered vs permission-denied (different copy).
- [ ] Include header, value sentence, and primary create/import CTA.
- [ ] Add Clear all filters for filtered-zero states.
- [ ] Use verb-first primary button labels.
- [ ] Match template structure in [reference/activation-patterns.md](reference/activation-patterns.md).
