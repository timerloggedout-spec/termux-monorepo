# Implementation plan — PolyGlot Urdu-first Teammate Portal

Design: docs/superpowers/specs/2026-11-27-polyglot-urdu-portal-design.md
Work item: POLY-001
Branch: feat/polyglot-urdu-portal-20261127-v2

## Tasks
1. Register proposal polyglot-localization and itemize implementation.
2. Add locale registry, canonical catalogs, mapping, and translation manifest.
3. Add provider registry and pre-registered Urdu translation DOE design.
4. Add translation-run and optional-feedback schemas.
5. Render Teammate Portal in English and Urdu with accessible language navigation and RTL.
6. Add focused validation for JSON structure, locale mapping, and translation provenance.
7. Run focused tests, proposal registry validation, repository gate, Termux smoke, and relevant CI.
8. Re-fetch branch/PR state and report each gate by exact SHA.

## Execution notes
- Keep provider execution credentials outside repository content.
- Treat provider support and pricing as run-time observations; store provider/model/version and source evidence in each run.
- Publish only human-reviewed catalog entries.
- Keep the Teammate Portal separate from Tribute dashboard surfaces.
