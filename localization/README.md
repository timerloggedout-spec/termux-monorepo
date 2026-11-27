# PolyGlot localization

Repository-owned localization contract for websites, Teammate Portal, and documentation.

## Canonical layout
- registry/locales.json: BCP 47 locale IDs, direction, fallback, regional profile, rollout state.
- catalogs/<surface>/<locale>.json: stable message keys and localized values.
- mappings/<surface>.json: canonical source IDs → source paths → catalog keys → published artifacts.
- manifests/<surface>.json: source hashes, translation revision, provider/model, review, freshness.
- providers/registry.json: provider adapter capabilities and configuration references.
- doe/<campaign>/DESIGN.json: pre-registered experiment design.
- schemas/: translation-run, experiment, and feedback record contracts.

## Rules
1. Keep canonical source text in English unless a surface declares another source locale.
2. Use BCP 47 language tags; use ur for Urdu and ur-PK for its initial regional profile.
3. Set dir=rtl for Urdu surfaces and isolate embedded LTR tokens (URLs, code, identifiers).
4. Keep stable message keys independent of translated wording.
5. Bind each translation to a source hash and translation revision.
6. Publish reviewed translations only; route missing/stale entries to the declared fallback.
7. Record provider, model/version, glossary, prompt, and evaluation cohort for every DOE treatment.
8. Preserve raw outcomes and uncertainty; rank quality before latency or cost.
9. Keep feedback optional, consent-based, anonymous by default, and revision-linked.
10. Treat human review and assistive-technology checks as release evidence.

## Provider adapter boundary
Adapters implement translate(source, target_locale, context, glossary, options) and return normalized output with provider/model/version, request ID, detected source, latency, usage/cost metadata when available, and warnings. Adapters never write directly to published catalogs.

## Teammate Portal
The portal shell is rendered by scripts/ops/render_teammate_portal_status.py. Locale catalogs provide interface strings; proposal documents remain source-linked English until a reviewed translation is registered in mapping and manifest.
