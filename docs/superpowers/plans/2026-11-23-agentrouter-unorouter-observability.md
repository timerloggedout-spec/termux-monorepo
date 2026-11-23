# Plan — AgentRouter / UnoRouter observation correction

**Date:** 2026-11-23  
**Proposal:** MSM-027  
**Branch:** fix/agentrouter-unorouter-observability-20261123  
**Base:** master

## Outcome

Correct the provider observation control plane using existing credentials and trusted GitHub Actions workflows. Keep catalog visibility, key-level usage, account-level balance, upstream pool capacity, consent, and inference admission as distinct evidence classes.

## Scope

1. Add the existing AGENTROUTER_API_KEY to .github/workflows/provider-availability.yml and pin the behavior with offline tests.
2. Preserve AgentRouter as catalog-only / community-pool evidence until an authoritative account balance/reset contract is verified.
3. Update UnoRouter manager and quota registry metadata from its current official docs: per-model request window, shared upstream caps, /api/usage/token/ key usage, separate access-token account routes, provider-level consent/objection.
4. Correct the proposal-lifecycle regression so it validates actual trigger configuration and the vote job's secret boundary, rather than rejecting harmless text in a concurrency expression.
5. Extend .github/workflows/operator-wake.yml with one owner-only, allowlisted wake-provider-availability command. It dispatches the trusted master workflow through the existing Actions PAT chain and reports a run receipt without reading credential values.

## Non-goals

- Provider inference, runtime admission, routing weights, paid fallback, or automatic retries.
- Creating or rotating API keys, account access tokens, provider accounts, or terms acceptance.
- Exposing PAT or provider secret values to the sandbox, PR code, logs, or artifacts.
- Changing the open quota-router PR #1441 or adding a duplicate quota service to it.

## Test sequence

- RED: add offline regressions for AgentRouter secret resolution, manager semantics, proposal workflow safety, and operator-wake dispatch allowlisting.
- GREEN: apply the minimal workflow/registry/test changes.
- VERIFY: run focused tests and workflow validators through exact-head GitHub Actions; run scripts/ci/repo_gate.py and scripts/ci/termux_smoke.py on the same head SHA.
- LIVE: after trusted workflow code is on master, use operator-wake and its existing owner PAT chain to dispatch provider-availability.yml; inspect the run and sanitized artifact. Catalog GETs only.

## Evidence / acceptance

- AgentRouter credential_env_resolved=AGENTROUTER_API_KEY with catalog observation and inference_ok=false.
- UnoRouter manager row distinguishes the gateway request window from upstream pool capacity and account usage.
- Provider-availability workflow reports provider catalog evidence without inference.
- No secret values appear in records, tests, comments, artifacts, or chat.
- All required exact-head checks are terminal and green before promotion.
