# Work Items — linguist-contact-projections

| ID | Work item | Status | Evidence |
|---|---|---|---|
| LCP-01 | Recover the legacy `AGENTS.hum.md` / `AGENTS.md` L33t parity pattern and isolate it from the closed broad PR payload. | done | Preserved PR #154/#177 heads and bounded diff review. |
| LCP-02 | Define canonical human sources, generated display/machine projections, and structural exceptions. | done | `docs/LINGUIST-CONTACT-PROJECTIONS.md`. |
| LCP-03 | Implement deterministic projection generation across root and ICM contact surfaces. | done | `scripts/cedrlang/render_contact_projections.py`; 24 projections. |
| LCP-04 | Add projection, structural-span, and stale-parity regression coverage. | done | `tests/test_contact_projections.py`. |
| LCP-05 | Validate projection parity and repository compatibility, then publish the focused PR. | done | 24 projections verified; 25 focused tests, registry validation, repository gate, Termux smoke, conflict scan, and whitespace check passed. |
