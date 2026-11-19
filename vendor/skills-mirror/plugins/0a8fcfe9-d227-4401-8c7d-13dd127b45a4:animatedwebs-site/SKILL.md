---
name: animatedwebs-site
description: "Build a complete, premium animated website or landing page from an AnimatedWebs template (cinematic video heroes, WebGL scenes, scroll storytelling). Use when the user asks for a website, landing page, homepage or portfolio, or wants a site that looks premium, cinematic or award-worthy."
---

# Build a website with AnimatedWebs

AnimatedWebs (https://animatedwebs.com) is a library of more than 1,600 animated website templates, each with a complete build prompt and many with a live demo. The `animatedwebs` MCP server searches the library, returns a template's full build prompt, and supplies backgrounds, components and design systems.

## Steps

1. **Understand the brief.** Business name, what it offers, audience, mood, brand colours and the stack already in the repository (Next.js, Vite, Astro, plain HTML). Ask at most one question, and only if something essential is missing.
2. **Find the right template.** Call `search_catalog` with kind `templates` and the business type and mood, for example "AI research platform, dark", "boutique hotel, calm" or "fintech, chrome". Narrow it with filters when they help: `templateKind` `website` for full pages, `access` `free` for templates any account can use, `category` with a value from `list_categories`, and for 3D or WebGL briefs `technique` (`threejs`, `particles`, `shaders`, `3d-objects`, `scroll-3d` or `simulators`). Prefer templates with a live demo. For a specific trade, the industry pages at https://animatedwebs.com/industries list the closest matches (dentist, restaurant, law firm, hair salon and over 130 more). Show the top 3 with their live-demo links and let the user choose, or choose the best match if they asked you to decide.
3. **Check access before fetching.** `get_template` with the slug returns the details and access level and spends nothing. A Free template works on any signed-in account. A Pro template is included with Pro and Lifetime; on other accounts the first fetch of its prompt spends one Prompt Pack credit. If the template is Pro, call `get_account` to see the plan and credits, and tell the user before a credit is spent.
4. **Get the prompt.** Call `get_template` with `include_prompt` true for the chosen slug. If it returns an access message, explain it plainly (plans are at https://animatedwebs.com/pricing, or call `get_pricing`) and offer a Free template as an alternative.
5. **Adapt without diluting.** Replace the template's brand, copy and palette with the user's. Keep its layout, typography, motion and quality bar. Use the user's own licensed media, or a background from `search_catalog` (kind `backgrounds`); never invent stock URLs.
6. **Build it** in the user's stack, section by section, as the prompt describes.
7. **Verify before finishing.** Run it and open it in a browser. Confirm there are no console errors, hero media plays, the page works at 390px with no horizontal scroll, and `prefers-reduced-motion` is respected. Fix anything that fails.
8. **Hand over.** Summarise what was built, how to run it and which parts to customise (copy, colours, media). Offer to keep the template in the user's favourites with `save_item` (action `save`, type `template`).

## Other routes

- **Hosted builder.** If the user would rather start in Lovable, v0 or Bolt than build here, call `open_builder` with the slug and give them the links it returns. The access rule is the same as for the prompt.
- **Nothing fits.** After a real search, offer to send the brief to the AnimatedWebs team with `request_template`. Send it once: each call creates a new request. Use `manage_request` to list, check or cancel requests already sent.

## Licence

- Pro prompts are licensed to the signed-in user for their own and client projects. Never publish a Pro prompt in a public repository or document.
- No AnimatedWebs credit is required on the finished site.
