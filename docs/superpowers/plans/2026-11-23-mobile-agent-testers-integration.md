# Mobile Agent Testers Integration — Implementation Plan

Proposal: mobile-agent-testers-integration
Work item: MAT-001
Branch: feat/mobile-agent-testers-integration
Base: master

## Task 1 — Register and scope

- Register the accepted proposal and itemized acceptance criteria.
- Keep Android hosted personas, deterministic emulator smoke, and physical Termux devices as distinct execution providers.
- Record the provider's real workflow inputs and artifact encryption boundary.

Verification: proposal validator; source workflow input inspection.

## Task 2 — StudySprint pilot brief and runbook

- Define app-specific exploratory goals for Today, Plan, Reviews, and Reader.
- Use synthetic learner content only.
- Document the custom SDK-direct Android build invocation and exact workflow inputs.
- Keep provider runs manual and budgeted.

Verification: all workflow input names match the inspected external YAML; app ID matches Android manifest.

## Task 3 — Evidence adapter

- Parse collected findings.json files from the trusted local collection directory.
- Emit one canonical integration event per issue, with stable event and idempotency IDs.
- Retain only bounded metadata and a SHA-256 reference to source evidence.
- Redact common email/phone/token patterns; omit report prose, screenshots, and raw transcripts.

Verification: stdlib-only unit tests, deterministic output, malformed input handling, schema-shape assertions.

## Task 4 — Catalog and integration docs

- Add mobile-agent-testers to machine and human registries.
- Add a provider-specific integration runbook.
- Link the new runbook from the integration index.

Verification: JSON parse, link/path checks, proposal registry validator.

## Task 5 — Delivery

- Review complete diff and security boundary.
- Run focused tests and repository gates in Actions.
- Open PR to master with Implements: MAT-001.
- WAIT for proposal, repo, and Termux checks on the same immutable SHA.
- Keep MAT-002 / MAT-003 queued until a bounded model budget and provider credentials are available.

## Non-goals

- No autonomous paid model runs.
- No provider private-key handling in CI.
- No production signing, learner-data access, app publication, physical device control, or changes to the device queue.
- No promotion of unverified AI findings to defects.
