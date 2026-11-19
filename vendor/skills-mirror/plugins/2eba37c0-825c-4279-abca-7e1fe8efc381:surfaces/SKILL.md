---
name: surfaces
description: Routes tasks to inline edit, slide-over, or a page; requires named destructive confirmation and zero layout shift on single-field edits. Use when adding modals, drawers, dialogs, routes, inline rename, contenteditable cells, or destructive actions.
title: Surfaces
category: interaction
severity: hard-rule
references:
- reference/destructive-actions.md
---

If `.ux-profile.md` exists at the project root, read it before changing surfaces, forms, or focus behavior.

If the chosen surface is a **page / route**, read `page-patterns` and name the pattern before writing page markup.

### Intent

Users lose context when the wrong surface type interrupts their flow. Quick edits stay in place; longer work gets a dedicated route; destructive actions never fire without explicit, named confirmation. This skill routes tasks to the lightest surface that still supports the work.

### Hard Rules (Non-Negotiable)

- **Task <10s: slide-over, drawer, or non-modal popover.** Do not navigate away from the current page or replace the main view. The user must retain spatial context of where they started.
- **Task ≥10s or multi-step: dedicated sub-page with its own URL route.** Stacking modals is prohibited. A second modal on top of an open modal is a hard failure — promote to a route or collapse into one sequential flow on a page.
- **Single-field edits (rename, title, one value): in-place only, with 0 layout shift.** Display and edit share one reserved box — same width, height, and position. Stack the input on the label (CSS grid, one cell) or overlay it. Do not swap in a taller control, extra padding, or a new Save/Cancel row. Neighbors must not move: a sibling's `getBoundingClientRect().top` and `.left` before and after entering edit must match. Enter saves; Escape cancels. A modal or slide-over for one field is a hard failure.
- **All destructive operations: dedicated confirmation dialog** that (a) names the exact entity, e.g. "Delete workspace 'Analytics'?" — never "Are you sure?"; (b) uses a destructive verb on the confirm button in destructive color; (c) sets Cancel as default keyboard focus; Escape dismisses without executing.

See [reference/destructive-actions.md](reference/destructive-actions.md) for confirmation layout, focus trapping, and copy templates.

### Design Heuristics & Taste Principles

- One field + one action = **inline edit**. Never a slide-over or modal.
- Two or more fields and still <10s = slide-over. Three+ fields or branching steps = page.
- Slide-overs enter from the trailing edge (right in LTR); width 400–480px for forms, full-height on narrow (`viewports`).
- Inline edit: show a pencil or pointer affordance on hover/focus; keep the label and input in the same box. Prefer Enter / Escape. Add Save/Cancel only if that slot already exists in the display state.
- Prefer URL-updatable state for ≥10s tasks so refresh and share links preserve progress.
- Non-destructive dismiss (Escape, backdrop click on non-modal popover) must not lose unsaved work — persist draft per `defaults`.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Editing a project name opens a slide-over or a centered modal. The label is replaced by a taller padded input, or Save/Cancel wrap onto a new row, so the next list row jumps down ~40px. Deleting a folder shows "Are you sure?" with OK/Cancel.

#### ✅ Best Practice

Rename stays in the same cell: label and input occupy one stacked box, row height unchanged, neighbors do not move, Enter saves, Escape cancels. Delete folder opens a confirmation dialog: title "Delete folder 'Q4 Reports'?", body lists item count impact, red "Delete folder" button, Cancel focused by default. A 5-step onboarding wizard lives at `/onboarding/step-2` with browser back support — no modal chain.

### Framework-Agnostic Implementation Blueprint

```
function chooseSurface(estimatedSeconds, fieldCount, isMultiStep):
  if fieldCount == 1 and not isMultiStep:
    return "inline-edit"   // never slide-over or modal
  if estimatedSeconds < 10 and not isMultiStep:
    return "slide-over"
  return "route"   // never "stacked-modal"

function confirmDestructive(action, entityLabel):
  open dialog with title = action + " " + entityLabel + "?"
  focus trap inside dialog
  focus Cancel button on open
  on Escape or Cancel: close, restore focus to trigger
  on Confirm: execute action, then close and announce result
```

```html
<div class="cell-edit">
  <button type="button" class="cell-display">Project name</button>
  <input class="cell-input" hidden value="Project name" aria-label="Project name" />
</div>
```

```css
.cell-edit {
  display: grid;
  width: 100%;
  height: 2.5rem; /* lock height — min-height alone still jumps */
}
.cell-edit > * {
  grid-area: 1 / 1; /* stack in the same reserved box */
  box-sizing: border-box;
  width: 100%;
  height: 100%;
  margin: 0;
  border: 1px solid transparent; /* match the input box model */
}
```

Toggle `hidden` on the two children. Do not `replaceChildren` with a different-sized control. Do not baseline-align the row against the swapped control. After entering edit, if any sibling moved, the implementation failed.

Route-based flows update `history.pushState` or framework router; slide-overs use `role="dialog"` with `aria-modal="true"` only when modal; popovers use `role="dialog"` without trapping page scroll.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Classify task duration and step count; pick inline, slide-over, or route — never stacked modals.
- [ ] If the surface is a page / route, name a `page-patterns` pattern before writing markup.
- [ ] Single-field work is inline — not a drawer, modal, or new page.
- [ ] Measure a neighbor's `top`/`left` before and after entering edit; values must match.
- [ ] Confirm all destructive actions use named-entity confirmation per reference spec.
- [ ] Set Cancel as default focus; Escape dismisses without side effects.
- [ ] Restore focus to trigger element when any overlay closes.
