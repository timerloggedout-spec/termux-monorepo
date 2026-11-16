# ITEMS — provider-family-doe-observatory

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| PFDO-001 | P1 | executing | Repair Family and Swarm Quota source links, freshness language and shared navigation. | Both pages use the canonical Nested Family twin; no stale refresh-pending claim; navigation exposes DoE Settings. |
| PFDO-002 | P1 | executing | Publish the existing DoE version/settings register as a structured, provenance-carrying projection and dashboard view. | Values match DOE-FAMILY.md; singular DoE version remains NOT_ESTABLISHED; unknown settings are not inferred; validator tests pass. |
| PFDO-003 | P1 | executing | Surface configured-instance identity on Family task rows without changing nested-family/v1. | Existing instance_key is displayed verbatim; missing remains NOT ESTABLISHED; collector never enriches or synthesizes it. |
| PFDO-004 | P1 | executing | Document source ownership, joins, freshness and QDesk boundaries; add regression tests. | Docs identify all canonical owners; tests pin paths/schema/unknown semantics; no duplicate scheduler or ledger introduced. |
| PFDO-005 | P1 | queued | Align participant identity and QDesk dispatch lineage with #5136 and PR #5145. | Produce mapping and acceptance evidence only; issuance/provisioning/admin actions remain gated by their own task and explicit evidence. |

## Validation

- `python3 -m pytest tests/test_doe_settings_register.py tests/test_tribute_family_integrity.py -q`
- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
