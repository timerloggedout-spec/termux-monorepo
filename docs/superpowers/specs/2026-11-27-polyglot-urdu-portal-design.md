# PolyGlot localization and Urdu-first Teammate Portal

## Intent
Make repository-published web surfaces and documentation extensible multilingual products. Deliver Urdu as the first prioritized locale for the Teammate Portal (hackathon-desk), with right-to-left rendering, locale-aware labels, explicit source mappings, translation provenance, provider comparison, and optional teammate feedback.

## Goals
- Define one locale registry and canonical message-key namespace.
- Track translations against source revision, target locale, provider/model, review state, and reviewer.
- Map canonical source IDs to portal and documentation artifacts.
- Compare multiple translation providers under the existing multivariate DOE contract.
- Publish an Urdu-first portal shell with deterministic English fallback.
- Collect optional, consent-based feedback linked to an exact translation revision.
- Include language metadata, RTL, keyboard navigation, focus, semantic labels, contrast, and screen-reader names in locale acceptance.

## Non-goals
- Automatic publication of machine-generated translations.
- Live provider API calls or secret provisioning in the portal renderer.
- Translation of all historical repository documents in this first slice.
- Treating automated accessibility checks as WCAG conformance certification.

## Approaches
1. Inline translations in the renderer: smallest initial change, but couples content, provider logic, and presentation.
2. Versioned JSON catalogs + mappings + manifest + provider adapters: recommended; static runtime output, auditable provenance, replaceable providers, reusable across web/docs.
3. External translation-management platform as source of truth: useful later, but adds service coupling before repository contracts and evaluation criteria exist.

## Chosen design
Use repository-owned JSON catalogs and registries as the canonical interface. The Teammate Portal renderer consumes reviewed catalog entries. Provider registry describes candidates; provider execution remains a separate adapter/workflow concern. The Urdu DOE is pre-registered before runs. Human review is the publication gate. Feedback is optional, explicitly consented, and revision-linked.

Initial locales: en (source) and ur (Urdu, RTL). The regional profile is ur-PK; the locale key remains ur so regional variants can be added later without changing the language namespace.

## Source and provenance model
Each message has a stable key, canonical source text, source path, and source hash. Each locale catalog records the key, translated value, state, source hash, provider/model (or human), reviewer, and revision. Mapping files bind stable source IDs to catalog keys and published paths. Missing or stale translations resolve to the declared English fallback and appear in coverage reporting.

## Provider DOE
Compare Azure AI Translator, DeepL, Google Cloud Translation, and OpenAI API as candidate treatments. Verify Urdu capability, account/region availability, exact model/version, and pricing at run time. Factors include provider, model/version, prompt/glossary treatment, task family, and review condition. Use a fixed, versioned Urdu task cohort; randomize treatment order; blind reviewer identities; preserve failed/unavailable cells. Primary response: blinded human quality score. Secondary responses: adequacy, fluency, terminology consistency, RTL/rendering defects, latency, cost, and correction effort. Treat latency as an operational measure alongside correctness. Human-reviewed source remains the publication baseline.

## Feedback
Feedback is opt-in. Capture consent, locale, stable message key, translation revision, rating, issue category, and optional comment. Default to anonymous feedback; collect contact details only in a separately authorized workflow. Feedback informs evaluation and prioritization; designated human review approves translations.

## Acceptance
- Locale registry validates BCP 47 tags, direction, fallback, and status.
- Teammate Portal exposes English and Urdu variants with correct lang and dir metadata.
- Urdu shell labels render in Urdu and RTL; navigation remains keyboard-accessible.
- Mapping and translation manifests validate source/catalog consistency.
- Provider DOE is pre-registered and emits provenance-bearing records.
- Feedback remains optional and revision-linked.
- Repository gate, proposal registry validation, Termux smoke, and relevant workflow checks run on the candidate SHA.
