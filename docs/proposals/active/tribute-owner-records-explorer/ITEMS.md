# ITEMS — tribute-owner-records-explorer

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| TROE-001 | P1 | executing | Deliver the metadata-only Owner Records explorer, strict envelope validation, build identity, D4-safe deployment behavior, Vercel envelope staging, and regression coverage. | Repo gate and Termux smoke pass on the final PR head; deployment build does not inject shared navigation or the all-pages version menu into Owner Records; public surface never fetches or decrypts record bodies; Admin + Tracking remain the only discovery links; store validation passes. |
| TROE-002 | P1 | blocked | Separately assess and implement browser-side age decryption, only after a dedicated threat model, browser-compatible cryptographic design, zero-network plaintext handling, and independent security review. | Explicitly verified decryption design and tests; until then capability remains NOT_IMPLEMENTED / NOT_VERIFIED and no body or plaintext is exposed by this surface. |

## Validation

- `python3 -B -m unittest discover -s tests -p 'test_owner_records_page.py' -v`
- `python3 scripts/proposals/validate_registry.py`
- `python3 scripts/ci/repo_gate.py`
- `python3 scripts/ci/termux_smoke.py`
