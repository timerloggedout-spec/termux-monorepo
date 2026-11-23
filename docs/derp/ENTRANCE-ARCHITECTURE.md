# DERP public entrance architecture

**Status:** concept / design proposal · **Version:** 0.1.0-draft

## Purpose

Create a separate public web presence that introduces DERP to newcomers and guides them through a maze-like sequence of clues, rabbit holes, and capability discoveries.

The entrance acts as a teaching and navigation surface. The repository remains the canonical source for implementation, permissions, operational status, and capability evidence.

## Experience flow

1. **Landing / welcome** — explain DERP in plain language and offer a first low-friction puzzle.
2. **Lexicon garden** — teach leetspeak mappings and symbol families through examples.
3. **Rabbit holes** — reveal related concepts through registered rePointers and optional clue branches.
4. **Capability rooms** — present documented tools and projects with evidence-backed descriptions.
5. **Contributor portal** — link to the repository, contribution guidance, wiki, and open proposals.

## Three cooperating layers

- **Surface:** accessible HTML, visible copy, semantic links, search metadata, and canonical URLs.
- **Play:** riddles, decoy paths, visual effects, and optional Unicode experiments.
- **Resolution:** registry-backed rePointers with destination status and capability provenance.

## SEO and discovery

- Give each public route a descriptive title, meta description, canonical URL, and semantic heading structure.
- Publish useful visible copy for DERP, d3rpWiki, rePointers, and the documented repository capabilities.
- Maintain sitemap and robots policy as separate standard web-discovery controls.
- Keep llms.txt factual and synchronized with public routes.
- Provide plain Markdown or text alternatives for each important public page.
- Keep Agent Ready output plain and deterministic, using canonical descriptions and URLs.
- Measure discovery through search impressions, meaningful visits, clue completion, and successful destination resolution.

## Accessibility and trust

- Provide keyboard navigation and screen-reader labels for every clue.
- Give every visual or invisible clue an equivalent visible explanation.
- Keep puzzle data inert; resolve only registered IDs.
- Display capability status and source links beside each capability claim.
- Preserve an obvious route back to the repository and a plain-language explanation of the maze.

## Deployment boundary

The domain, host, analytics, visual system, and initial route list remain open decisions. Treat the public entrance as a separate deployment with its own review and release process. This proposal creates no production site or DNS changes.
