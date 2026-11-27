# Admin Desk Integration

Admin Desk is the governed operator information surface for observability, experiment, and promotion state. It reads canonical evidence and policy projections; it does not become a second event ledger.

## Views

1. Fleet/lane health: workflow, job, attempt, SHA, status, freshness.
2. Trace explorer: task → agent → tool → model/request, with evidence links.
3. Experiment desk: campaign, cohort, variant assignment, repetitions, outcome distributions.
4. Provider comparison: ingest completeness, query/eval coverage, latency, cost, resource use, exportability.
5. Profile explorer: profile artifacts and environment fingerprints.
6. Promotion desk: dual-gate state, task outcome, legal disposition, operator decision, immutable receipt.

## Authorization

- Use existing SSO and role model.
- Separate read-only analyst access from operator actions.
- Scope write actions to explicit capabilities and lane ownership.
- Confirm consequential actions and preserve actor, reason, target SHA, and resulting receipt.
- Derive role decisions from authenticated identity and policy records; browser-supplied role claims are display context only.

## Data flow

Admin Desk consumes projections from canonical JSONL/receipt artifacts, GitHub Actions metadata, and provider adapters. Every displayed result links to source run, commit, event digest, and provider observation.

Provider availability and dashboard state remain observational. Admin Desk actions request repository-owned workflows or policy transitions; GitHub checks and dual-gate remain authoritative. Preserve a static fallback view when optional providers are unavailable.
