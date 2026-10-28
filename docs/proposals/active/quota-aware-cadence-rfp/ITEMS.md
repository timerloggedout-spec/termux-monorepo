# ITEMS — quota-aware-cadence-rfp

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| QAC-001 | Register the existing active RFP in the canonical proposal registry | done | registry.yaml entry added on proposal branch |
| QAC-002 | Add required lifecycle manifest and items file | done | MANIFEST.md and ITEMS.md added |
| QAC-003 | Revalidate lifecycle registry | executing | proposal-lifecycle validate-registry must pass on exact PR SHA |
| QAC-004 | Revalidate underlying cadence implementation claims | posted | Separate evidence review; not implied by registry repair |
| QAC-005 | Cadence provider auto-onboarding: one registry entry checked against every cadence surface (catalog endpoint/secret, availability env, quota family, review-bot maps), with scaffold generator + derived matrix | executing | `scripts/cadence_provider_onboarding.py check` = 0 drift on live surfaces; tests in `tests/test_provider_onboarding.py`; record in `docs/ops/CADENCE-PROVIDER-ONBOARDING.md` |
