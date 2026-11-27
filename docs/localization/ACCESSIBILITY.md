# Localization accessibility standard

**Baseline:** WCAG 2.2 AA for published web surfaces, with manual keyboard and assistive-technology review before release.

## Locale requirements
- Set the document language to the active BCP 47 tag and the document direction to the locale direction.
- Use semantic landmarks, heading order, accessible names, visible focus, and keyboard-operable language navigation.
- Keep focus order aligned with the visual reading order in RTL layouts.
- Isolate embedded LTR material such as URLs, code, dates, identifiers, and technical tokens with appropriate direction and bidi isolation.
- Verify Urdu font shaping, joining, punctuation, numerals, and fallback on supported browsers and mobile browsers.
- Preserve contrast, text resizing, reflow, reduced-motion behavior, and touch target usability.
- Provide text alternatives for diagrams and meaningful non-text content; provide captions/transcripts for media.
- Keep untranslated fallback content explicitly marked with its actual language and direction.

## Release evidence
Automated checks cover markup, links, metadata, and selected contrast rules. Manual review covers keyboard-only navigation, screen-reader announcements, focus visibility, zoom/reflow, RTL reading order, and native Urdu typography. Combine automated checks with manual assistive-technology review as the WCAG conformance evidence set.
