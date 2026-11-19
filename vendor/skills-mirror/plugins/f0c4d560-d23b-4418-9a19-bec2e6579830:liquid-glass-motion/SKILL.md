---
name: liquid-glass-motion
description: 'Animation, morphing, and shader best practices for Liquid Glass and SwiftUI motion on iOS 26+/macOS 26+ through iOS 27. Use when animating glass or building UI motion: glassEffectID, @Namespace morphing, GlassEffectContainer spacing, glassEffectUnion, glassEffectTransition (.matchedGeometry/.materialize), withAnimation, springs, UnitCurve, PhaseAnimator, KeyframeAnimator, @Animatable, matchedTransitionSource, navigationTransition zoom, scrollTransition, visualEffect, Metal shaders (colorEffect, distortionEffect, layerEffect, [[stitchable]]), accessibilityReduceMotion gating, Instruments/xctrace profiling of hangs and animation hitches. Also fires on symptoms: glass morph not animating, view pops in instead of morphing, glass fades instead of materializing, morph flickers with Reduce Motion, menu glass morphs as a rectangle, animation runs on insert but not removal, PhaseAnimator loops forever or fires once, shader shows clipped edges (maxSampleOffset), animation hitches or main-thread hangs while scrolling glass chrome. For static glass, availability gating, toolbars, UIKit/AppKit glass, or accessibility of the material itself use the liquid-glass skill first.'
---

# Liquid Glass — motion, animation, and shaders

Companion to the **liquid-glass** skill (`~/.claude/skills/liquid-glass/`). Same tag system:
`[verified]` / `[apple]` / `[multi]` / `[single]` / `[version-pinned]` — see that skill's
SKILL.md. Composed 2026-08 and verified against Apple documentation and SDK interfaces.

## Operating rules

1. Before generating code, ALWAYS read the availability firewall in the companion
   **liquid-glass** skill (installed alongside this one):
   `references/availability-and-sdk27.md`. Motion code trips the same SDK-27 breakages
   (`.if` ban, `@ContentBuilder`, renames).
2. Load references on demand via the router — one topic, one file.
3. The motion model: Liquid Glass and its motion were designed together. Glass does not
   fade — it materializes by modulating lensing; when glass grows, its material gets
   thicker (deeper shadow, stronger lensing). Size change is a material change, which is
   why morphs must be the system animation, never hand-faked.
4. Verify motion claims against `references/` before repeating them — circulating write-ups
   get several of these facts wrong; the corrected facts live in these files.
5. Profiling evidence beats reasoning: record an Instruments trace with `xctrace` before
   optimizing, and never trust the iOS Simulator for the SwiftUI instrument — see
   `references/performance-and-instrumentation.md`.

## Hard rules (the short list)

1. Never animate glass with `.opacity` / fades — use `glassEffectTransition`
   (`.materialize` is the sanctioned fade-like option). [multi]
2. Morphing silently no-ops unless ALL four hold: same `GlassEffectContainer`;
   `glassEffectID` per element in one shared `@Namespace`; the change is view
   insertion/removal (not a value change); the state change is inside `withAnimation`.
   Plus geometry: nearest edges within the container's `spacing`. [multi]
3. The interactive "squish" is one boolean — `.interactive()`. No public spring/damping/
   stiffness knobs exist; do not promise tunable jelly. [multi]
4. Gate every glass animation on `accessibilityReduceMotion` — the default morph is a
   kinetic effect, and reduce-motion users have experienced it as flickering. The system
   does NOT gate your `withAnimation` for you. [multi]
5. One animation source per property — never mix implicit `.animation`, `withAnimation`,
   and scroll-driven updates on the same property. Implicit later in the view tree silently
   wins over explicit. [multi]
6. The animation context must live OUTSIDE a conditional — an `.animation()` inside the
   `if` is destroyed with the view and removal never animates. [multi]
7. Prefer renderer-side motion for scroll: `scrollTransition` / `visualEffect(in:)` over
   observable scroll-offset plumbing. [apple]
8. Animate transforms first (scale/offset/rotation), frames second, identity changes last.
   [multi]

## Topic router

| Topic | Reference |
|---|---|
| Springs, curves, precedence, Transaction, @Animatable, CA bridge | `references/animation-fundamentals.md` |
| Glass morphing, glassEffectID, union, glassEffectTransition | `references/morphing.md` |
| Navigation zoom, custom Transition, sheets, touch-vs-trackpad | `references/transitions-and-navigation.md` |
| Scroll-driven motion, scrollTransition, visualEffect, chrome interplay | `references/scroll-driven.md` |
| PhaseAnimator, KeyframeAnimator, symbol effects | `references/phase-and-keyframe.md` |
| Reduce Motion gating, replacement tables | `references/reduce-motion.md` |
| Metal shaders with/under/instead-of glass | `references/metal-and-glass.md` |
| Performance model, xctrace profiling | `references/performance-and-instrumentation.md` |
| Static glass, availability, toolbars, platform APIs, a11y of the material | liquid-glass skill |
| Choosing the actual spring/damping/duration values | apple-motion-feel skill |

## Scripts

`scripts/record_trace.py` and `scripts/analyze_trace.py` (+ `instruments_parser/`) — vendored
from Antoine van der Lee's SwiftUI-Agent-Skill (MIT; licence ships beside them as
`scripts/LICENSE-AvdLee-SwiftUI-Agent-Skill`). Record and parse Instruments traces (Time
Profiler, Hangs, Animation Hitches, SwiftUI lanes) into JSON/markdown. Usage and interpretation:
`references/performance-and-instrumentation.md`.

