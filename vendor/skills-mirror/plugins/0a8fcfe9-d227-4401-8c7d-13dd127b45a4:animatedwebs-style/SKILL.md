---
name: animatedwebs-style
description: "Give a project a coherent, premium visual style from AnimatedWebs design systems, covering colour tokens, type scale, radius and buttons, exported as DESIGN.md, a Tailwind theme or CSS variables. Use when the user asks for a design system, colour palette, typography or style direction, or wants a site to look top-tier."
---

# Apply an AnimatedWebs style

1. **Pick a direction.** Call `search_catalog` with kind `styles` to browse style references by mood, typeface, colour or theme, or kind `templates` when a full animated template fits better. Style queries match the whole text as one phrase, so keep them short. Show 3 options with their links.
2. **Pull the system.** `get_style_reference` returns the DESIGN.md, Tailwind v4 theme and CSS variables for a style. Every template page offers the same exports.
3. **Apply it as tokens**, not one-off values. Wire colours, fonts, radius and button styles into the project's theme (Tailwind configuration, CSS variables or design tokens), then update components to use them.
4. **Keep the work original.** A style reference describes a look. Never copy another company's logo, imagery, copy or trademarks.
