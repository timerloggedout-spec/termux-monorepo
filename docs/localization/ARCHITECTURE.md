# PolyGlot localization architecture

## Directory contract
- `localization/registry/`: supported BCP 47 locales, direction, fallback, and regional profile.
- `localization/catalogs/<surface>/<locale>.json`: stable UI message keys and translations.
- `localization/mappings/`: canonical source IDs, source paths, message keys, and publication routes.
- `localization/manifests/`: source/catalog revisions, provider/model, glossary/prompt versions, reviewer, freshness, and publication state.
- `localization/providers/`: normalized adapter contract and provider registry.
- `localization/doe/<campaign>/`: pre-registered provider comparison designs and run records.
- `localization/schemas/`: machine-readable contracts for locale, mapping, manifest, experiment, and feedback records.
- `docs/locales/<locale>/`: localized repository documentation, organized by source path.

## Runtime boundary
The portal renderer reads repository-owned static catalogs. Missing message keys resolve to the source-locale catalog. A stale locale catalog falls back to the source locale; a fresh, unapproved locale remains visible only as a review-required preview. The manifest controls freshness, review status, and publication state. Provider adapters create draft outputs and provenance records; publication requires explicit human approval and a fresh source hash.

## Urdu rollout
The initial language key is ur, with regional profile ur-PK and direction rtl. The source locale is en. Teammate Portal interface labels are the first translation cohort. Linked proposal documents retain English language metadata until translated artifacts pass review.

## Provider comparison
The Urdu campaign uses the existing DOE method in .agents/skills/multivariate-doe/SKILL.md. Provider, model/version, prompt/glossary, and review condition are treatment factors. Human quality is primary; adequacy, fluency, terminology, RTL defects, correction effort, latency, and cost are secondary. Record provider availability and exact versions during execution. Human approval remains the publication gate.

## Feedback boundary
Optional feedback requires explicit consent and records locale, stable message key, exact translation revision, rating, category, and optional comment. Anonymous feedback is the default. Feedback supports evaluation and prioritization; publication requires human approval.
