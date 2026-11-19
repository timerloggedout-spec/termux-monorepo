---
name: keyboard
description: Full keyboard access, visible focus rings, and focus trap/restore for overlays. Use when building interactive UI, modals, shortcuts, or accessibility focus work.
title: Keyboard
category: interaction
severity: hard-rule
references:
- reference/keybinding-matrix.md
---

If `.ux-profile.md` exists at the project root, read it before changing surfaces, forms, or focus behavior.

### Intent

Pointer-only UI excludes keyboard and assistive-tech users and slows power users. Every control operable by mouse must work by keyboard; focus must always be visible; overlays must trap and restore focus predictably.

### Hard Rules (Non-Negotiable)

- **Every mouse-operable control must work via Tab, Shift+Tab, Enter, and Space.** Links, buttons, toggles, menus, tabs, and custom widgets expose correct roles and keyboard handlers. No hover-only actions without a keyboard equivalent.
- **Never `outline: none` without an immediate high-contrast replacement.** Use `box-shadow` focus ring or `outline` with `outline-offset: 2px` meeting contrast requirements from `.ux-profile.md`. Focus must be visible in both light and dark themes.
- **Modals and slide-overs trap focus internally; restore focus to the trigger on close.** Tab cycles within the overlay only; on dismiss, return focus to the element that opened the surface.

See [reference/keybinding-matrix.md](reference/keybinding-matrix.md) for Esc, Enter, Slash, Mod+K, and grid navigation conventions.

### Design Heuristics & Taste Principles

- Tab order follows visual reading order (DOM order matches layout unless `tabindex` manages roving indices in composite widgets).
- Skip link as first focusable: "Skip to main content."
- Custom components use roving `tabindex="0"` on one item in a group (toolbar, radio group, grid row).
- Shortcuts shown in tooltips must not override browser or OS reserved keys without modifier.
- Focus ring style is consistent system-wide: 2px offset, accent or high-contrast color — not per-component one-offs.

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

Icon buttons remove focus outline globally in CSS. Dropdown opens on hover only; keyboard users cannot reach menu items. Modal closes on Escape but focus vanishes to `<body>`. Data table cells clickable but not in tab order.

#### ✅ Best Practice

Global `:focus-visible` ring at 2px offset, 3:1 contrast minimum. Menu button opens on Enter/Space; arrows move items; Escape closes. Modal saves `triggerRef`, traps Tab, Escape closes and restores focus to trigger. Table rows focusable with Enter to activate primary row action.

### Framework-Agnostic Implementation Blueprint

```css
:focus {
  outline: none; /* only if replaced below */
}

:focus-visible {
  outline: 2px solid var(--focus-ring-color, #2563EB);
  outline-offset: 2px;
}

/* Alternative high-contrast pattern */
:focus-visible {
  box-shadow: 0 0 0 2px var(--surface), 0 0 0 4px var(--focus-ring-color);
}
```

```javascript
let triggerEl = null;

function openOverlay(fromEl) {
  triggerEl = fromEl;
  overlay.showModal();
  firstFocusable(overlay).focus();
  overlay.addEventListener('keydown', onTrapTab);
}

function closeOverlay() {
  overlay.close();
  overlay.removeEventListener('keydown', onTrapTab);
  triggerEl?.focus();
  triggerEl = null;
}
```

Composite widget pattern (tabs): selected tab `tabindex="0"`, siblings `tabindex="-1"`; ArrowLeft/ArrowRight move selection and focus.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present for contrast/focus targets.
- [ ] Tab through entire flow: every interactive element reachable and operable.
- [ ] Verify no global `outline: none` without `:focus-visible` replacement.
- [ ] Overlays trap focus; Escape closes; focus returns to trigger.
- [ ] Implement shortcuts per keybinding matrix where applicable.
- [ ] Custom widgets use correct ARIA roles and keyboard patterns.
