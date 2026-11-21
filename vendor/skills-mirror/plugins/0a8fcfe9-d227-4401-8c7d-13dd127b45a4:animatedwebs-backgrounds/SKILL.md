---
name: animatedwebs-backgrounds
description: "Add a cinematic video background (a seamless looping film) to a hero or section using AnimatedWebs Cinematic Backgrounds. Use when the user asks for a video background, a looping hero video, a film-like hero, or wants the hero to move."
---

# Cinematic video backgrounds from AnimatedWebs

1. **Find candidates.** Call `search_catalog` with kind `backgrounds` and the mood or subject the user wants, for example "aurora", "liquid chrome", "deep ocean" or "abstract dark". Background queries match the whole text as one phrase, so keep them to one or two words. Show the best 3 with their preview links.
2. **Get the file.** Call `get_background` for the chosen slug. With Pro or Lifetime it returns the clean MP4 link and a ready `<video>` snippet. On other plans it returns the watermarked preview and names the plan that includes the clean file. Say so plainly, and never ship the watermarked preview as a final asset.
3. **Integrate it well.** Place the video behind the content as a muted, looping, inline, autoplaying layer with `object-fit: cover` and a poster image. Add a gradient or scrim so text meets WCAG contrast, and show the poster instead of the video when the user prefers reduced motion.
4. **Verify it** in a browser at desktop width and at 390px: it plays, loops without a visible jump, text stays readable and nothing scrolls sideways.
5. **Keep it for later.** Offer to save the background to the user's favourites with `save_item` (action `save`, type `background`).
