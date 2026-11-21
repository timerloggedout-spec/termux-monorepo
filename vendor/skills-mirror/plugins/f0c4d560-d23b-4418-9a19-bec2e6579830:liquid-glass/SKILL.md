---
name: liquid-glass
description: 'Liquid Glass material best practices for SwiftUI, UIKit, and AppKit on iOS 26+/macOS 26+ (Tahoe) through iOS 27/macOS 27. Use when implementing, reviewing, or migrating to glass: glassEffect, Glass variants (.regular/.clear/.identity), tint, interactive(), GlassEffectContainer, glassEffectUnion, toolbar glass, ToolbarSpacer, scrollEdgeEffectStyle, sharedBackgroundVisibility, tabBarMinimizeBehavior, backgroundExtensionEffect, NSGlassEffectView, UIGlassEffect, Tahoe window chrome, glass accessibility (Reduce Transparency/Increase Contrast), pre-26 Material fallbacks, UIDesignRequiresCompatibility. Also fires on symptoms: glass renders dark or muddy, glass looks like a flat tinted rectangle, glass button doesn''t register taps, tap passes through glass, "''glassEffect'' is only available in iOS 26.0 or newer", "ambiguous use of ''opacity''", "''cornerRadius'' was deprecated", glass looks different in simulator vs device, screenshots of glass UI don''t match. For glass animation, morphing, glassEffectID, transitions, Metal shaders, or performance profiling use the liquid-glass-motion skill instead.'
---

# Liquid Glass — the material

Composed 2026-08 and verified against developer.apple.com and SDK interfaces. Every rule
carries an availability floor and a confidence tag: `[verified]` (checked against Apple
docs/SDK this composition), `[apple]` (Apple doc, unverified), `[multi]` (corroborated by
multiple independent accounts), `[single]` (one account — verify before relying),
`[version-pinned]` (bug workaround tied to OS versions; recheck on updates).

## Operating rules

1. ALWAYS read `references/availability-and-sdk27.md` before generating or reviewing glass
   code. It corrects availability errors present in most published material, including Apple's.
2. Load other references on demand via the router below — one topic, one file.
3. Glass belongs on the functional layer (controls, chrome) floating above the content layer.
   When asked to add glass to content (lists, media, text), first ask whether it should be
   glass at all.
4. Prefer standard components (toolbars, search, sheets, tab bars) that adopt glass
   automatically; custom `glassEffect` surfaces are for distinctive elements only.
5. Never present simulator rendering or exact screenshot pixels as evidence a glass change is
   correct — see `references/known-bugs-and-testing.md`.
6. Animation of glass (morphing, transitions, reduce-motion gating, performance) is owned by
   the companion **liquid-glass-motion** skill, installed alongside this one. Read its
   references when the task involves motion; do not improvise glass animation from here.

## Workflows

- **Review existing glass** → `references/review-checklist.md` (diff-checkable items +
  known-bad API table). Also flag where glass should NOT be used.
- **Adopt / migrate an app** → `references/fallback-and-migration.md` (deletion-first audit,
  5 phases), then per-surface references.
- **Implement from scratch** → `references/material-and-variants.md` +
  `references/containers-and-sampling.md`, then the platform file for your framework.

## Hard rules (the short list)

1. Availability-gate every glass API per platform with its real floor; fall back to Materials
   below 26. [verified]
2. Never wrap `glassEffect` in a `.if` conditional-modifier helper — ternary with `.identity`
   or a ViewModifier gate instead. [apple]
3. Apply `glassEffect` after layout and appearance modifiers. [multi]
4. Two or more glass views near each other → one `GlassEffectContainer`. Glass cannot sample
   other glass; the container is visual correctness, not just performance. [multi]
5. `interactive()` only on surfaces that actually respond to interaction; buttons already
   have it. [multi]
6. Never set `opacity < 1` on a glass view or any ancestor — refraction silently collapses.
   [multi]
7. Glass needs content to refract: over a flat single-color background it reads as a flat
   tinted rectangle. Give it a gradient/image/dynamic content, or don't use glass. [multi]
8. Never stack glass on glass. [multi]
9. Custom-shape glass buttons need `contentShape` or only the glyph hit-tests.
   [version-pinned]
10. Glass ignores `.allowsHitTesting(false)`; only `.disabled(true)` suppresses its visual
    reaction. [verified]
11. The system adapts the material for Reduce Transparency / Increase Contrast — don't
    fight it, and don't remove glass manually where the system would frost it. [multi]
12. Dark/muddy glass over bright backgrounds in Dark Mode is by design; fix the background
    colors, not the glass. [verified]

## Topic router

| Topic | Reference |
|---|---|
| Availability, SDK-27 breakages, renames, compat flag | `references/availability-and-sdk27.md` (always) |
| Variants, tint, shapes, interactive, when-to-use | `references/material-and-variants.md` |
| Containers, sampling, spacing, glass-on-glass | `references/containers-and-sampling.md` |
| Toolbars, scroll edge, tab bar, WWDC26 toolbar APIs | `references/toolbars-and-scroll-edge.md` |
| UIKit (UIGlassEffect, corners, hosting) | `references/uikit-glass.md` |
| AppKit, NSGlassEffectView, Mac windows, Tahoe chrome | `references/appkit-and-mac-windows.md` |
| Accessibility (transparency, contrast, hit targets) | `references/accessibility.md` |
| Fallbacks below 26, migration workflow | `references/fallback-and-migration.md` |
| Version-pinned bugs, testing/screenshot policy | `references/known-bugs-and-testing.md` |
| Review audit + known-bad (hallucinated) APIs | `references/review-checklist.md` |
| Morphing, glassEffectID, transitions, motion, Metal, profiling | liquid-glass-motion skill |

## Scope

SwiftUI first; UIKit and AppKit covered; WidgetKit briefly in platform files. visionOS
excluded — the SDK marks Liquid Glass unavailable there [verified]. watchOS/tvOS excluded —
no reliable source material exists; do not improvise.
