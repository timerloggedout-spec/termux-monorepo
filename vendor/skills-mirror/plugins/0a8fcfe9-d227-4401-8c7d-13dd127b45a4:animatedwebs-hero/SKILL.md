---
name: animatedwebs-hero
description: "Give an existing website a cinematic hero section (looping video, WebGL or shader background, oversized type, refined navigation) using AnimatedWebs templates. Use when the user wants a more impressive first screen, an animated or video background, or a hero that stops visitors scrolling."
---

# Upgrade a hero with AnimatedWebs

1. **Read the current site.** Open the home page and hero, and note the stack, fonts and brand colours.
2. **Find directions.** Call `search_catalog` with kind `templates` and the brand mood plus "hero", for example "dark particle hero" or "calm water video hero". `templateKind` `section` narrows it to single sections, and `technique` (`threejs`, `particles`, `shaders`, `3d-objects`, `scroll-3d`, `simulators`) narrows it to a 3D or WebGL approach. For a video hero, `search_catalog` with kind `backgrounds` lists ready-made cinematic loops. Show the top 3 with their live-demo or preview links.
3. **Apply only the hero.** Call `get_template` with `include_prompt` true (or `get_background` for a loop) and implement the hero part. A Pro template on an account without Pro or Lifetime spends one Prompt Pack credit on its first fetch, so say so first.
   - **Video hero:** full-bleed, muted, looping, inline video with a poster image and a gradient scrim for legible text.
   - **WebGL or shader hero:** implement it in code exactly as the prompt describes; no video file is needed.
   - **Type and navigation:** oversized headline, refined navigation and one clear primary action, with an entrance animation.
4. **Respect the rest of the site.** Keep the user's copy, brand and other sections unchanged.
5. **Verify in a browser.** No console errors, fast first paint (lazy-load anything below the fold), no horizontal scroll at 390px, and a calm fallback for `prefers-reduced-motion`.
