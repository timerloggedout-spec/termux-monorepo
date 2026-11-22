# Model Selection Market — Decision Log

## MSM-025 — Incumbent versus VultrInspired catalogue

The owner clarified the architecture: Vultr's Python and TypeScript repositories are equivalent references used to inform our own schemas, normalization, cache and capability design. They are not modules to import, separate runtime catalogues or competing implementations. Their source revisions remain pinned as design provenance only.

The competing catalogue variants are repository-owned:

- **Incumbent v5.0.0:** the existing multi-provider collector and evidence contract at `scripts/provider_model_catalog.py`.
- **VultrInspired v1.0.0:** a native, standard-library-only projection at `scripts/provider_model_catalog_vultr_inspired.py`, initially consuming incumbent v5 documents and emitting a versioned richer projection.

The local projection uses the existing Python runtime and offline fixture data. It performs zero network requests, zero credential lookups and zero inference calls. Live catalogue refresh remains a separately authorized provider observation; inference requires a separately configured provider. Vultr compute provisioning and promotional capacity are outside the task.

DoE `DOE-VULTR-CATALOG-001` is versioned at v2.0.0. Its variants are Incumbent and VultrInspired; the Vultr Python and TypeScript commits are stored separately as source references. The design compares identical input rows across fixture families, record-quality cases and price representations. Result status remains planned until paired deterministic runs generate measurements and artifacts.

The first native projection preserves incumbent records and access evidence, structures limits/modalities/capabilities/lifecycle/provenance, retains unknown fields, isolates malformed rows and diagnoses binary-float pricing. It cannot recover decimal text already lost by the incumbent conversion path. Source-native exact-pricing capture and broader modality fixtures remain follow-on work.

Runtime activation, provider admission, routing weights, credentials, quota policy, live inference and schedules remain unchanged. Promotion requires separate review and same-head validation.
