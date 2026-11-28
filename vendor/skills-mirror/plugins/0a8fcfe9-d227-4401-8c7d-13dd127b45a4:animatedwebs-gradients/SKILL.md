---
name: animatedwebs-gradients
description: "Add a live animated WebGL gradient background (liquid chrome, aurora, mesh, melt, fluted glass and more) to a hero or section using AnimatedWebs Gradient Studio. Use when the user asks for an animated gradient, a moving background without video, a shader background, or a lighter alternative to a video hero."
---

# Live gradient backgrounds from AnimatedWebs Gradient Studio

Gradient Studio is free at https://animatedwebs.com/gradients. It renders the background live in WebGL from one small shader, so there is no video file to host.

1. **Pick a direction with the user.** Name 2 or 3 of the 16 styles that fit the brand: Melt (domain-warped flow), Mesh (soft colour blobs), Ribbons, Halo, Aurora, Chrome (liquid metal), Plasma, Contours (topographic lines), Cells (living Voronoi), Vortex, Conic, Halftone, Silk, Tide (stacked waves), Fluted (reeded glass), Bars. Suggest colours from the project's own tokens, not stock purple-to-blue.
2. **Send them to the studio.** Ask the user to open https://animatedwebs.com/gradients, choose the style and colours, then press **Copy HTML embed** (plain sites), **Copy React** (React or Next.js) or **Copy settings** (the settings as JSON) and paste the result here.
3. **Integrate what they paste.** The export is self-contained: one `<canvas>` and one script, no libraries. Put the canvas behind the hero content (`position: absolute; inset: 0; z-index: 0`), keep content above it, and size it with CSS. In React, render the exported component and pass `className` for size. Never edit the shader string; change colours or speed only through the exported config object.
4. **Keep text readable.** The studio shows a live contrast grade. If the user did not check it, measure the headline against the background at its darkest and brightest points and add a soft scrim or change the text colour until it reaches 4.5:1 for body text and 3:1 for large headings.
5. **Respect the visitor.** The export already pauses when the tab is hidden and shows a still frame when the visitor prefers reduced motion. Add the **Copy CSS fallback** as the canvas element's background so the hero is never blank before WebGL starts or when WebGL is off.
6. **Verify it** in a browser at desktop width and at 390px: it animates smoothly, text stays readable, and nothing scrolls sideways.
