---
name: spacing
description: Enforces optical alignment, 4/8pt spatial rhythm, and container/line-length constraints. Use when laying out screens, aligning icons to text, setting spacing, or reviewing uneven whitespace.
title: Spacing
category: visual-taste
severity: hard-rule
references:
- reference/optical-offsets.md
---

If `.ux-profile.md` exists at the project root, read it before changing layout, color, or type.

### Intent

Spatial taste is geometric discipline, not decoration. Layouts feel calm when spacing follows a predictable rhythm, text stays within readable line lengths, and icons align to typographic cap-height rather than raw bounding boxes. This skill keeps screens optically balanced and structurally consistent.

### Hard Rules (Non-Negotiable)

- **8pt grid for major components; 4pt for micro-spacings.** Stack heights, section gaps, card padding, and column gutters snap to multiples of 8px. Icon padding, inline gaps, and label offsets snap to multiples of 4px. Reject odd values (e.g., 13px, 22px) unless documented as an optical correction from [reference/optical-offsets.md](reference/optical-offsets.md).
- **Max body line length 65–75ch.** Prose containers set `max-width: 65ch` to `75ch`. Wider blocks require a narrower inner column or multi-column layout; never stretch body copy edge-to-edge in wide viewports. Narrow overflow, chrome collapse, and hit targets are `viewports`.
- **Uniform optical baselines within a hierarchy level.** Siblings at the same heading or list level share one baseline grid. Mixed font sizes in one row require explicit vertical alignment (flex `align-items: baseline` or calculated offsets), not default box-center alignment.
- **Icon-to-text aligns to font cap-height, not full bounding box.** Inline icons sit on the cap-height centerline of adjacent text. Do not vertically center icons to the text element's total line box unless the icon is taller than one line and the reference doc says otherwise.

### Design Heuristics & Taste Principles

- Prefer fewer spacing tokens: 4, 8, 12, 16, 24, 32, 48, 64. Larger jumps signal section breaks; smaller steps stay within one component.
- Group related controls with tighter internal spacing (4–8px) and separate unrelated groups with 16–24px.
- When in doubt, add whitespace between sections rather than between items inside a section.
- Optical corrections (±1–2px nudges) are allowed only for icons, chevrons, and SVG marks — never for arbitrary layout gaps.
- Reserve space for async content (badges, counts) to avoid layout shift when data loads.
- Why (Laws of UX): Things close together read as a group (Law of Proximity). A shared boundary makes the group obvious (Law of Common Region). Tight gaps inside a group, larger gaps between groups, and a clear container. Jon Yablonski, Laws of UX. https://lawsofux.com/law-of-proximity/ https://lawsofux.com/law-of-common-region/

### Concrete Scenarios (Before vs. After)

#### ❌ Anti-Pattern

A settings row uses a 24px icon vertically centered to a 14px label inside a 48px-tall row with 13px top padding and 19px bottom padding. Body copy spans 120ch on a 1440px monitor. Section gaps alternate between 20px, 28px, and 36px.

#### ✅ Best Practice

The row uses 16px vertical padding (8pt grid), 8px gap between icon and label, icon shifted +1px per cap-height formula, label at 14px with `align-items: baseline`. Body copy lives in a `max-width: 70ch` column. All section gaps are 32px.

### Framework-Agnostic Implementation Blueprint

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
  --prose-max: 70ch;
}

.prose {
  max-width: var(--prose-max);
}

.inline-icon-row {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.inline-icon-row svg {
  /* Apply cap-height offset from reference/optical-offsets.md */
  transform: translateY(var(--icon-cap-offset, 0));
}
```

For measurement without a design tool: select adjacent text, read computed `font-size` and `line-height`, compute cap-height ratio from the reference file, apply `translateY` to the SVG wrapper.

### Agent Checklist

- [ ] Read `.ux-profile.md` if present.
- [ ] Audit spacing values: major gaps on 8pt grid, micro gaps on 4pt grid.
- [ ] Set body/prose `max-width` between 65ch and 75ch.
- [ ] Verify sibling elements at the same hierarchy share baselines.
- [ ] Align inline icons using cap-height math, not box-center defaults.
- [ ] Document any optical offset applied and link to the reference formula used.
