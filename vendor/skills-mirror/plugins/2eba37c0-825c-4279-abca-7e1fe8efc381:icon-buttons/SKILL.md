---
name: icon-buttons
description: Collapses labeled toolbar controls to square icon buttons with required tooltips and shortcut kbd. Use when building toolbars, icon-only buttons, view toggles, export/filter/columns chrome, or reviewing icon button a11y.
title: Icon Buttons
category: interaction
severity: hard-rule
references:
- reference/icon-button-contract.md
---

If `.ux-profile.md` exists at the project root, read it before changing surfaces, forms, or focus behavior.

### Intent

Dense toolbars waste space on repeated chrome labels. Square icon buttons reclaim that space when the mark is conventional — but an unlabeled icon without a hover/focus name is opaque. This skill decides when to collapse a label to an icon, and requires a real tooltip (plus shortcut kbd when one exists) every time you do.

### Hard Rules (Non-Negotiable)

- **Every icon button shows a tooltip on hover and on keyboard focus.** Tooltip text is the same verb-first label the button would have had (`Export CSV`, not `CSV`). Match `verbs` capitalization and sentence case.
- **If the action has a shortcut, the tooltip must include the project’s Kbd component.** If the project has no Kbd primitive, append the shortcut as label text. Platform-aware: `⌘K` on Mac, `Ctrl+K` elsewhere — see `keyboard` keybinding matrix.
- **`title="..."` is not a tooltip.** Native `title` is too slow, cannot host a kbd, and fails this skill. Use a real tooltip surface (popover / tooltip primitive).
- **Accessible name is required separately.** Set `aria-label` (or visible text) matching the tooltip label. A tooltip is not an accessible name.
- **The control is square** (equal width and height). Hit-target size follows `viewports` (44×44 AA / 48×48 AAA). A 16px glyph is not the tap area.

See [reference/icon-button-contract.md](reference/icon-button-contract.md) for when/not tables, tooltip anatomy, and markup.

### Design Heuristics & Taste Principles

Prefer icon buttons for:

- Toolbar / chrome actions with a standard mark (export, filter, columns, more, close)
- View toggles (board vs list)
- Compact grouped controls in one cluster

Keep a visible label when:

- The control is the page primary CTA (e.g. Create job)
- The action is destructive (still needs named confirm from `surfaces`)
- The icon is ambiguous without words
- The control is a form submit

Heuristics are preference, not a must — collapsing is optional; tooltips are mandatory once collapsed.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Toolbar shows text “Export CSV”, “Board”, and “List” beside icon-only Filter and Columns. An icon-only Export uses `title="Export"` only — no hover tooltip, no shortcut. Board/List toggles are text-only and break the square chrome rhythm. Glyph is 16px with no padding to the profile hit floor.

#### ✅ Best Practice

Export, Board, and List become square icon buttons matching Filter and Columns. Each has `aria-label` plus a tooltip on hover and focus: “Export CSV” with Kbd for its shortcut when one exists; “Board” and “List” for the view toggle. Create job stays a labeled primary in the header. Hit targets meet the profile floor.

### Framework-Agnostic Implementation Blueprint

```html
<button
  type="button"
  class="icon-btn"
  aria-label="Export CSV"
  aria-describedby="tip-export"
>
  <!-- icon mark -->
</button>
<div id="tip-export" role="tooltip" hidden>
  Export CSV
  <kbd>⌘E</kbd>
</div>
```

```css
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;  /* 44px AA floor; 48px when profile is AAA */
  height: 2.75rem;
  padding: 0;
}
```

Show the tooltip on `:hover` and `:focus-visible`. Prefer the project’s tooltip + Kbd primitives when they exist. Never rely on `title`.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present (hit targets, voice).
- [ ] Inventory toolbar / chrome actions: prefer icons for conventional chrome; keep labels on primary CTAs, destructive actions, ambiguous marks, and form submits.
- [ ] Every icon button has a real tooltip (not `title`) on hover **and** focus.
- [ ] Tooltip label is verb-first and matches `aria-label`.
- [ ] Shortcut actions include Kbd (or appended platform-aware shortcut text).
- [ ] Controls are square; hit targets meet `viewports` floor.
- [ ] Cross-check [reference/icon-button-contract.md](reference/icon-button-contract.md).
