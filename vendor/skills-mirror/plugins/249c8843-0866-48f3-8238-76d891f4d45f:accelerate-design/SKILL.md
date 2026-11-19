---
name: accelerate-design
description: Design a new on-brand version of a block or a fresh section — "make me a variant of the hero", "design a new pricing section", "compose an on-brand version", "give me a bolder hero". Produces ready-to-use content; offers to put it in a test but never forces one. NOT for running or tracking an A/B test (use accelerate-test) or a multi-round optimization loop (use accelerate-evolve).
license: MIT
category: design
parent: accelerate
---

# Accelerate — Design an on-brand variant or section

You author a brand-fitting version of a block, or a brand-new section, on demand. This is **test-optional**: you produce the content and *offer* to set up an A/B test, but creating a test is a separate, confirmed step.

**Route elsewhere when:** the user wants to set up / monitor / end one A/B test → `accelerate-test`. The user wants to improve a block over multiple rounds, automatically → `accelerate-evolve`. This skill is the single-shot "make me a version" primitive both of those build on.

## Flow

1. **Load the brand pack.** Follow `docs/brand-pack.md` — the *whole-site* grammar: global styles + the **usage-grounded structure library** (real section fragments harvested from published pages, with synced patterns confirmed by page usage) + media. Never one page. Reuse the cached pack if it's fresh.
2. **Take the brief.** Which block or section, and what the user wants it to do (or "a new <kind> section"). If targeting an existing block, read its current content first: `accelerate/get-variants` if it already has variants; otherwise WP-CLI (`wp post get <id> --field=content`) or ask the user to paste it. Do not reconstruct it from memory.
3. **Compose by recombining the site's real fragments.** Work from the brand pack's `fragments[]` — the actual block markup the site uses, not summaries — and recombine and extend them; don't re-skin the control. **Prefer high-confidence (in-use) fragments**; treat low-confidence (registered-but-unused) ones with suspicion. Keep the fragments' semantic classes and preset-slug tokens intact as you splice. Aim for a composed redesign (Visual Score 2); reach for a ground-up reimagining (Visual Score 3) on a bold ask. Build it as a block tree, then serialize. Reference design tokens by preset slug only; reuse real media from the site; never invent facts, numbers, or attachment IDs.
4. **Run the Block Runner pre-flight, then validate silently against `docs/design-standards.md`.** Before showing a serialized Gutenberg candidate, follow `docs/block-runner.md`: `validate`; on exit `1`, `fix` then re-`validate`; use repaired markup only after the second check passes. Rework or withhold a candidate that remains invalid — never show it or hand it to a write ability. If `npx` is unavailable, times out, or headless Gutenberg cannot boot, use the §2 manual checks and tell the user automated markup validation was unavailable; exit `2` is a prominent broken-invocation warning before the same fallback. Then check slug-first (§1), anti-pattern bans (§3), differentiation rubric ≥3/7 with no zeros (§4), and no AI-slop copy (§5). For full-bleed sections / whole-page work, also honour the rendering & editability contract (§15: forgiving primitives over `wp:cover`, editor styles, full-width alignment, content width). Rework anything that fails before showing it.
5. **Present it, then offer the test.** Show what it is, the *concept* it argues, and the real fact it's grounded in. Then offer the next step — set it up as an A/B test (hand to `accelerate-test`), or just hand back the content to use as-is. Never create a test without explicit confirmation.

## Presenting

Lead with the concept, not the markup. Example:

> **Here's a bolder take on your hero — an outcome-led version.**
>
> Your current hero leads with what the product *is*. 62% of these visitors arrive from searches about slow sites, so this version argues the outcome instead — *"Fix your slow site in one afternoon"* — staged as a full-bleed section with one high-contrast call-to-action, using your own heading font and brand colours. *(Grounded in: 62% of hero traffic arrives from speed-related searches.)*
>
> Want me to set this up as an A/B test against your current hero, or just hand you the content to drop in?

Show the variant's copy in the presentation. Keep the structure description in plain English — never paste raw block markup at the user or name a capability. Apply the router's full terminology ban to the entire answer, including setup and verification notes; never call a site operation an "ability".

## Rules

- **Whole-site grammar, never one page.** Always load the brand pack (`docs/brand-pack.md`) before composing.
- **Compose, don't re-skin.** Recombine the site's own sections; a real version is a different experience, not the control with new words. Apply the bold-by-default doctrine in `docs/design-standards.md` §9.
- **Slug-first, real media, no invented facts.** Every token is a preset slug; every image already exists on the site; placeholder copy where you'd otherwise guess a number.
- **Test-optional.** Produce and offer. Never call create-ab-test (a mutation) without explicit confirmation — hand to `accelerate-test` once the user opts in.
- **No AI-slop copy** (`design-standards.md` §5) and no developer jargon in anything the user reads.
