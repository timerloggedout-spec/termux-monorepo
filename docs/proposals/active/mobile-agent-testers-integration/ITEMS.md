# ITEMS — mobile-agent-testers-integration

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| MAT-001 | P1 | executing | Add provider catalog entry, StudySprint pilot brief/runbook, and a privacy-safe adapter that converts locally collected persona findings into the existing Integration Intelligence event envelope. | Registry/catalog remain valid; adapter emits schema-compatible events; stable IDs and idempotency; raw report text and secrets excluded; fixture tests cover valid, malformed, duplicate, and redaction cases; docs preserve emulator/physical-device boundaries. |
| MAT-002 | P1 | queued | Add provider execution orchestration after cost, secret, and permission readiness are verified. | Manual dispatch only; explicit run budget; pinned source SHA; Android-only StudySprint matrix; encrypted artifacts; local trusted collection; no private key in CI; run record includes provider run ID and cost. |
| MAT-003 | P1 | queued | Run the first bounded StudySprint pilot and convert confirmed findings into deterministic regressions. | Owner-approved budget recorded; run artifacts collected locally; each finding triaged; confirmed findings reproduced; regression tests added; dual-gate evidence on the resulting SHA. |

## Validation

- python3 -m unittest discover -s tests -p 'test_mobile_agent_testers_adapter.py' -v
- python3 scripts/proposals/validate_registry.py
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

Provider-run cost and model credentials remain an explicit per-run boundary. MAT-002 and MAT-003 stay queued until that boundary is satisfied.
