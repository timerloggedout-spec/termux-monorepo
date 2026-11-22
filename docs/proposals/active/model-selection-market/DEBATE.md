

## MSM-025 — Incumbent versus VultrInspired catalogue

The owner clarified the architecture: Vultr's Python and TypeScript repositories are equivalent references used to inform our schemas, normalization, cache and capability design. They are not modules to import, separate runtime catalogues or competing implementations. Their source revisions remain pinned as design provenance only.

The competing catalogue variants are repository-owned: **Incumbent v5.0.0** at `scripts/provider_model_catalog.py`, and **VultrInspired v1.0.0** at `scripts/provider_model_catalog_vultr_inspired.py`. The native projection consumes incumbent v5 documents and emits a versioned richer projection. It uses the existing Python runtime and offline fixtures, with zero network requests, credential lookups or inference calls. Live catalog refresh and inference remain separate provider integrations; Vultr compute and promotional capacity are outside scope.

DoE `DOE-VULTR-CATALOG-001` is versioned at v2.0.0. Its two variants are Incumbent and VultrInspired; Vultr Python and TypeScript commits are separate source references. The initial projection preserves incumbent records and access evidence, structures limits/modalities/capabilities/lifecycle/provenance, retains unknown fields, isolates malformed rows and diagnoses binary-float pricing. It cannot reconstruct decimal text already lost by incumbent float conversion. Source-native exact-price capture and broader modality fixtures remain follow-on work.

Runtime activation, provider admission, routing weights, credentials, quota policy, live inference and schedules remain unchanged. Promotion requires separate review and same-head validation.
