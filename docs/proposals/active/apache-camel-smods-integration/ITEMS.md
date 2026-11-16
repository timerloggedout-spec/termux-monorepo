# ITEMS — apache-camel-smods-integration

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| CAMEL-001 | Inspect source repository identity, revision, build baseline, license, and repository footprint | done | Public user-owned repo; main HEAD `12014575a8f2c71174a8f9f4cbef9a61e25439e8`; root POM Camel 4.24.0-SNAPSHOT / JDK 21; Apache-2.0 text; GitHub size 1,561,977 KB |
| CAMEL-002 | Distinguish Camel CLI MCP from Camel MCP Server and map principal opportunities | done | Official Camel docs distinguish assistant-authoring MCP from route-exposing MCP; see RFP §3 and §11 |
| CAMEL-003 | Map Camel against hub_mcp, Termux MCP, Actions, ATES, and existing credential authority | executing | Complete a verified adapter/permission map with explicit no-duplication decisions |
| CAMEL-004 | Define minimal read-only and side-effecting route fixtures plus MCP conformance/security tests | todo | Tests cover explicit tag admission, auth, collisions, schema validation, bounded output, timeout ambiguity, idempotency |
| CAMEL-005 | Measure Termux/JDK/resource compatibility against isolated runner baseline | todo | Capture device resource snapshot, Java version, startup, RSS, disk, and bounded throughput; no unsupported-runtime claims |
| CAMEL-006 | Verify fork ancestry and local delta against Apache upstream | todo | Exact upstream base and custom commit set documented; license/NOTICE obligations reviewed |
| CAMEL-007 | Decide metadata-only vs immutable shallow gitlink at refTemplates/smods/camel_fork-apache | blocked | Requires CAMEL-003–006 evidence, independent proposal acceptance, and both repository gates |
| CAMEL-008 | Implement the selected narrow adapter only after acceptance | blocked | Separate implementation PR cites `Implements: CAMEL-008`; no production enablement before validation |
