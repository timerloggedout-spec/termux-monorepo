# ITEMS — quota-aware-cadence-rfp

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| QAC-001 | Register the existing active RFP in the canonical proposal registry | done | registry.yaml entry added on proposal branch |
| QAC-002 | Add required lifecycle manifest and items file | done | MANIFEST.md and ITEMS.md added |
| QAC-003 | Revalidate lifecycle registry | executing | proposal-lifecycle validate-registry must pass on exact PR SHA |
| QAC-004 | Revalidate underlying cadence implementation claims | posted | Separate evidence review; not implied by registry repair |
| QAC-005 | Cadence provider auto-onboarding: one registry entry checked against every cadence surface (catalog endpoint/secret, availability env, quota family, review-bot maps), with scaffold generator + derived matrix | done | Landed PR #2027 merged e59b51ffa3 (history-scan + byte-match verified) |
| QAC-006 | Make onboarding automated & programmatic: quota-registry as 6th checked surface, `apply` command writing every surface, `autofix` + workflow (surface-change triggers + weekly) opening one auto-extend PR for missing-entry drift, hard drift fails loudly | executing | `check` covers `ops/quota/registry.json` (27/27 families mapped); `tests/test_provider_onboarding.py` covers quota surface, autofix, apply; workflow `.github/workflows/cadence-provider-onboarding.yml` |
| QAC-007 | Enact rate-limit P1 (derived-reserve preflight on the PAT publish path); disposition P2 (headroom-posting workflow) | executing | `pat_publish.py` preflight live-verified 2026-10-29 (remaining 4743/5000, planned 8, threshold 508, safe); enactment recorded in `docs/ops/RATE-LIMIT-2026-10-29.md` |
| QAC-009 | Tick ledger: per-request HFT-style quota telemetry — every response's x-ratelimit-* headers logged per request instance at chokepoints (PAT helper phase 1), summarized into cadence-tick-ledger/v1 (burn measured, per-session attribution, Δused = total fleet burn) | executing | Helper `_tick` live-proven 2026-10-30 (used 548→549→550 across consecutive calls); `scripts/cadence_tick_ledger.py` check/summarize + tests; spec `docs/ops/CADENCE-TICK-LEDGER.md`; phases 2–4 (app consumers, workflow steps, Neon ingest) = adoption items |
