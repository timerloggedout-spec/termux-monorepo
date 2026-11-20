---
name: internationalization-and-localization
description: Structures i18n and l10n work for user-facing software. Use when adding multiple languages, regional formats, RTL layouts, or locale-aware content. Use when extracting strings, choosing i18n libraries, or verifying translated UX.
---

# Internationalization and Localization

## Overview

Internationalization (i18n) makes software capable of multiple locales; localization (l10n) supplies the actual translations and regional conventions. Done late, i18n becomes a expensive retrofit. Done as a process, it is string extraction, plural and gender rules, layout that survives translation expansion, and validation that every locale renders correctly.

For general UI quality and accessibility, combine with `frontend-ui-engineering` and `references/accessibility-checklist.md`.

## When to Use

- Adding a second language or planning for multilingual support
- User-visible strings hardcoded in components or APIs
- Dates, numbers, currencies, or calendars shown to users
- RTL languages (Arabic, Hebrew, etc.) or mixed-direction content
- Sorting, search, or collation that must respect locale

## When NOT to Use

- Internal-only admin tools explicitly single-locale forever (document that assumption)
- Pure backend services with no locale-sensitive responses (unless API returns user-facing messages)

## Process

### 1. Inventory and strategy

- List **surfaces**: web, mobile, email, PDF, push notifications, error messages from APIs.
- Choose **source of truth** for keys and default locale (usually resource files or a TMS pipeline).
- Define **fallback** behavior: missing key → default locale string + dev warning, never silent blank in prod.

### 2. Extract and key strings

- Replace literals with stable keys (`checkout.title`, not `string_42`).
- **No string concatenation** for sentences — translators need full sentences with placeholders.
- **Interpolate** with named parameters: `{name}`, `{count}` — order differs by language.
- **Pluralization** and **select** (gender, enum-like variants) use ICU MessageFormat or library equivalent — not `if (n === 1)`.

### 3. Layout and CSS

- Design for **text expansion** (German often ~30% longer than English).
- Avoid fixed widths on labels; prefer flex/grid that wraps.
- **RTL:** Use logical properties (`margin-inline-start` vs `margin-left`) where possible; test mirroring of icons and directional cues.
- **Fonts** must cover scripts for target locales.

### 4. Locale data

- **Dates/times:** Use timezone-aware APIs; store UTC, display in user timezone.
- **Numbers/currency:** Format with locale; never hand-roll separators.
- **Calendars:** Respect locale week start and holidays if product requires.

### 5. Quality gates

- **Pseudo-localization** in CI: lengthen strings, add accents — catches clipping and missing keys.
- **Review** with native speakers for at least one high-traffic flow per new locale.
- **Test** RTL as a first-class layout pass, not an afterthought.

### 6. API and contracts

- If the backend returns user-visible messages, version and locale-negotiate (`Accept-Language`) or return keys for client-side resolution — pick one strategy and document it in `api-and-interface-design` style.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We'll i18n after launch" | Retrofit cost grows with every hardcoded string and layout assumption. |
| "Google Translate is enough" | MT can bootstrap; shipped UX needs human review for tone, idioms, and errors. |
| "English default is fine for errors" | Non-English users get a worse security and support experience. |
| "Concatenation works in English" | It breaks in many languages; use full sentences with placeholders. |

## Red Flags

- Same string used in different contexts (translator cannot disambiguate)
- Images with embedded text without localized variants
- Sorting UTF-8 by byte order instead of locale-aware collation
- Missing plural rules leading to "1 file(s)" in some locales
- RTL layout broken because only physical `left`/`right` CSS was used

## Verification

- [ ] No user-visible hardcoded strings in scope (or explicit exception list)
- [ ] Keys stable; renames handled with migration or alias policy
- [ ] Pseudo-locale run passes in CI or manual check documented
- [ ] At least one non-default locale manually verified (layout + critical flows)
- [ ] RTL verified if any RTL locale is in scope
- [ ] Documented fallback behavior for missing translations
