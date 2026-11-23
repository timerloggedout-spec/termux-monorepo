# DERP Language Specification B — Visible-first token grammar

**Version:** 0.1.0-draft  
**Status:** competing proposal  
**Profile:** robust / indexable / accessible

## Intent

Make DERP a readable playful dialect that works in ordinary HTML, Markdown, search snippets, terminals, screen readers, and agent-readable exports. Use visible leetspeak and rePointer tokens as the canonical syntax. Use invisible Unicode as optional decoration; express essential meaning through visible tokens.

## Model

- **Visible surface:** plain language plus a documented leetspeak lexicon.
- **Play layer:** clue phrases, decoy paths, riddles, and rabbit-hole navigation.
- **Resolution layer:** stable rePointer IDs mapped to canonical URLs and capability records.

## Proposed token grammar

    DERP-B := DOCUMENT
    DOCUMENT := SECTION*
    SECTION := HEADING BODY [CLUE]
    CLUE := "d3rp{" CLUE_ID "}"
    CLUE_ID := lowercase-ascii identifier
    REPTR := "rptr:" NAMESPACE "/" SLUG

Examples:

- d3rp{welcome-rabbit-hole}
- rptr:wiki/lexicon
- rptr:capability/termux-cockpit

Each token MUST have a visible label and a canonical link in the rendered page.

## RePointer registry

Each record contains an ID, human-readable label, canonical URL or repository-relative path, lifecycle status (active, experimental, retired), audience (newcomer, contributor, operator), concise purpose and capability boundary, and the specification version that introduced it.

Unknown IDs render as unresolved text and are reported by validation.

## Invisible-character policy

Invisible marks MAY appear as optional decorative puzzle texture. Express each clue, destination, instruction, permission, and crawler policy through visible, documented forms; use invisible marks as optional decoration. The page MUST remain fully functional after all such marks are removed.

## SEO and agent-readable surfaces

- Put meaningful terms such as DERP language, d3rpWiki, rePointer, Termux monorepo, and documented capabilities in visible titles and prose.
- Keep canonical URLs, descriptions, headings, semantic links, and sitemap entries accurate.
- Keep robots.txt in standard crawler-policy syntax.
- Keep llms.txt factual and aligned with the public site.
- Generate Agent Ready content from the plain visible surface and canonical registry; omit puzzle decoration.

## Acceptance tests

- Parse and validate every token against the registry.
- Verify canonical destinations and HTTP status.
- Render equivalent accessible labels.
- Verify search-facing HTML and Markdown contain the same essential meaning.
- Strip all invisible characters and confirm complete functionality.
