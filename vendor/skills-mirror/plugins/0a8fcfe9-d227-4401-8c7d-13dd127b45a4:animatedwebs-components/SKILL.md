---
name: animatedwebs-components
description: "Add polished animated UI components (buttons, text effects, backgrounds, cards, loaders, sections) from the AnimatedWebs UI Library, or generate a new one. Use when the user asks for an animated button, heading effect, background effect, hover interaction or loader, or wants a section to feel more premium."
---

# Animated UI components from AnimatedWebs

1. **Find candidates.** Call `search_catalog` with kind `components` and what the user wants, for example "magnetic button", "text scramble" or "aurora background". `list_categories` with kind `components` shows the categories, the `runtime` filter narrows to one runtime such as `react`, `three` or `css`, and an empty query with `cursor` pages through everything. Show the best 3 with their live preview links.
2. **Get the code.** Call `get_component` with the id for details, then again with `include_source` true for the code. Source needs Pro; if the account does not have it, say so plainly and offer `generate_component` instead. A large component may list files it could not fit under `code.omitted`: fetch each one with `path`.
3. **Nothing fits?** Call `generate_component` with a clear `prompt` (content, layout and motion) and a `style` (`luxury`, `editorial`, `glass` or `brutalist`). It returns one self-contained HTML document, so port it to the project's framework. Use `refine_component` to iterate, one change at a time, for example "make the cards glass" or "use brand colour #7d5bff". Generations share a daily allowance (5 on Free, 100 on Pro); `get_account` shows what is left.
4. **Integrate cleanly.** Match the project's framework, styling system and naming. Keep focus states, a reduced-motion fallback and readable contrast.
5. **Verify it** in a browser at desktop width and at 390px before finishing.
6. **Keep it for later.** Offer to save a library component to the user's favourites with `save_item` (action `save`, type `component`). If the user needs something the library and the generator cannot give, offer `request_template` once, and use `manage_request` to follow up.
