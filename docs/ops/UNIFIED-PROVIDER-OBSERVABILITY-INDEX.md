# Unified Provider & Observability Index

**Status:** integration contract / inventory baseline  
**Created:** 2026-11-05  
**Canonical repository:** `timerloggedout-spec/termux-monorepo`  
**Machine-readable companion:** `ops/telemetry/integration-observability-index.json`

## Purpose

Join the provider, gateway, orchestration, deployment, attestation, quota, and evaluation surfaces into one navigable inventory without creating a competing telemetry database or scheduler. This index is a **projection and contract**, not a claim that every listed system is live, credentialed, or producing observations.

The existing `ops/telemetry/results-index.json` remains the canonical four-system results projection for **ATES, 3L0, Temporal, and HindSight**. This index links to it and adds the integration/provider dimensions; it does not replace or rewrite it.

## System topology

```text
Provider/model catalog ──► eligibility + quota policy ──► model-router / llm_api_hub
          │                            │                           │
          │                            └── quota observations      │ invocation
          │                                                        ▼
          ├── AgentRouter (key provisioned; account validation pending)                      Temporal / Actions
          ├── Bifrost (evaluation)                                  │
          └── native providers                                      ▼
                                                         sanitized event envelope
                                                                  │
                 ┌────────────────────────────────────────────────┤
                 ▼                 ▼                ▼             ▼
              ATES / 3L0       HindSight        Provenance      Witness
              quality &       retained         evidence        signed
              outcomes        memory           ledger          attestations
                 │                 │                │             │
                 └─────────────────┴────────────────┴─────────────┘
                                      │
                                      ▼
                         results-index + dashboard feeds
                                      │
                   n8n optional adapter / Platform201 host
                   Gravitee gateway analytics (when persistent)
```

**ForeSight:** this is the existing FOSS / emerging-technology horizon-scanning system, the intended ForeSight integration. Its canonical surfaces are `docs/research/FORESIGHT-RADAR.md`, `docs/ops/FORESIGHT-EVIDENCE-SPINE.md`, the `foresight` Python package, and `data/foresight/resource-registry.jsonl`. Integrate through its existing H0–H3 horizon and evidence-status contract; do not create a duplicate radar, registry, or evidence ledger.

## Consolidated system register

| System | Current evidence / state | Canonical role | Integration decision |
|---|---|---|---|
| Temporal | Existing engagement and self-host smoke Actions receipts; current results index says execution is ephemeral in-job, no persistent Temporal instance | Durable execution contract / workflow correlation | Reuse workflow/run receipts and identifiers. Do not create a second scheduler or infer persistent Temporal service health. |
| HindSight | Existing telemetry ingest and retain proof/state. Results index snapshot (2026-11-02) reports 3 attempts, 0 successful retained units, last error 402; snapshot is now stale until refreshed | Retention sink for sanitized telemetry payloads | Keep retention separate from Provenance. A failed retain must not block provenance emission. Credit/billing gate stays visible; no full population until proof gate passes. |
| ForeSight | Existing FOSS / emerging-technology radar, evidence spine, portable registry and CLI | Horizon scanning, research evidence and procurement/prototype signals | Consume the existing radar and evidence records; preserve H0–H3, evidence status, canonical source, hashes and append-oriented corrections. Do not duplicate its registry or turn weak signals into facts. |
| ATES | Existing `apps/tribute-dashboard/data/ates-feed.json`; workflow receipts are its evidence | Evaluation/quality outcomes | Keep ATES verdicts and receipt semantics; do not convert telemetry absence into zero. |
| 3L0 | Existing `ops/telemetry/session-history-3l0.jsonl` | Observational session history and confirmed-signal fold | Keep observational vs confirmed fields distinct. |
| Gravitee APIM | Self-host GitHub Actions workflow boots an ephemeral stack with dual gateways; connector/helper mock-verified; no persistent live instance | API gateway, plans, consumers, request/error/latency analytics | Use as an analytics and gateway policy surface only when deployed. CI boot proof is not production telemetry. |
| Witness (TestifySec / in-toto) | Existing registry/integration references and provenance design | Signed artifact/build attestations (materials, command, products, signer, policy verdict) | Attestation digest references the repository evidence envelope. Consume the placement decision owned by the provenance lane; do not create a second ledger or signing-key store. |
| n8n | Optional self-hosted Community Edition adapter, compose + importable workflow + sanitized SHE bridge exist | Visual composition and operator automation | GitHub Actions and repository evidence remain authoritative. n8n is not a second scheduler or system of record. Mark observed only after a real execution receipt exists. |
| Platform201 | Live help-wanted dashboard deployment and health endpoint verified 2026-10-27; console-only, no API token/Actions credential | Deployment host and deployment-surface metadata | Display project/environment/deployment/health/credits as sourced observations. Not a telemetry backend; do not invent API polling. Revalidate aged console facts. |
| Bifrost | Catalog/host/capabilities registered as evaluation; benchmark smoke runbook exists, results pending | Candidate LLM gateway / native MCP gateway | Keep evaluation-only. Promote only after benchmark `results.json` plus repository dual-gate evidence. Never wholesale-merge upstream workspace. |
| AgentRouter (`agentrouter.org`) | Authenticated dynamic catalog adapter and unit coverage added in this PR; owner reports the API key is provisioned; account-scoped model discovery still requires a successful authenticated observation | Multi-provider LLM gateway with OpenAI-compatible and Anthropic-compatible transports | Keep catalog discovery separate from inference admission. Use per-inference usage/quota/token and performance metrics as request-level evidence; never infer account-wide remaining balance from individual calls. |

## Provider and model registration contract

Provider discovery, model eligibility, quota, health, and inference are separate states:

1. **Discovery:** preserve provider/model ID, exact source URL, protocol, source type, observed-at timestamp, capability evidence, terms/data classification, region/account prerequisites, and confidence.
2. **Eligibility:** require an explicit allowlist, capability fit, region/data-class compatibility, accepted terms, and a credential present in approved secret storage.
3. **Quota:** use only documented provider headers or authenticated account APIs. Record source, scope, observed UTC time, units, reset basis, and authority. `unknown` is a first-class value; catalog pricing or advertised free tier is not remaining balance.
4. **Health:** catalog success is not inference health. Probes are separate, minimal, authorized, non-sensitive, bounded, and timestamped.
5. **Invocation:** record the exact provider/model/protocol actually used and the fallback reason. Do not silently rewrite the selected provider.
6. **Admission:** default deny for unknown/stale evidence, missing credentials, unapproved data class, exhausted quota, or absent spend policy. No account hopping or blind retry on auth/billing/policy failures.

### AgentRouter transport details

- OpenAI-compatible base URL: `https://co.agentrouter.org/v1`
- Anthropic-compatible base URL: `https://co.agentrouter.org` (do not append an OpenAI `/v1` suffix to this base).
- Secret name: `AGENTROUTER_API_KEY` (secret value must never enter chat, source, artifacts, or logs).
- Model source of truth: authenticated `GET /v1/models` for the configured key/resource pool.
- One key may be shared across agents with unified quota; attribute every usage observation by agent/workflow, model, request ID and a non-secret key alias, never by exposing the key.
- **Owner-confirmed operational behavior:** each AgentRouter inference call logs quota/token and related usage/performance metrics. Treat the provider's per-inference record as the primary request-level observation, preserving its exact returned metric names/values and source timestamp; normalize known fields (`input_tokens`, `output_tokens`, `total_tokens`, `quota_tokens`, `usage_cost`, `latency_ms`, `time_to_first_token_ms`, `tokens_per_second`) when present. Missing fields remain null/absent, never synthesized.
- Per-inference usage records do not automatically establish current account-wide remaining balance or reset time. Keep those aggregate fields `unknown` unless a separate account-authoritative source documents them.
- Catalog discovery is wired and credential-gated; owner reports the key is provisioned, but successful account-scoped discovery must be evidenced by the authenticated observation workflow. No inference route is admitted by this catalog change. Enable inference only after credential validation, account-scoped model discovery, approved data classification, an explicit spend ceiling, and the separate native-inference admission review.

## Shared telemetry envelope

Emit one sanitized event per provider/gateway invocation or deployment/workflow observation. Suggested versioned contract:

| Field | Meaning | Rule |
|---|---|---|
| `schema` | Envelope version | `provider-observation/v1` |
| `event_id` | Stable idempotency key | Hash of canonical non-secret identity fields |
| `provider_id`, `model_id` | Actual selected provider and model | Exact identifiers; nullable only with explicit reason |
| `protocol` | Transport family | e.g. `openai-compatible`, `anthropic-compatible`, `native-mcp` |
| `workflow_id`, `run_id`, `run_attempt`, `temporal_workflow_id` | Execution correlation | Use available authoritative IDs; never fabricate missing IDs |
| `request_id` | Provider request identifier | Only if returned by provider |
| `doe_campaign_id`, `experiment_instance_key` | Experimental attribution | Only when the dispatch is stamped and eligible |
| `started_at`, `ended_at`, `latency_ms`, `time_to_first_token_ms`, `tokens_per_second` | Timing/performance | UTC; use provider-reported metrics when available; derive only elapsed wall latency from timestamps |
| `input_tokens`, `output_tokens`, `total_tokens`, `quota_tokens`, `usage_cost` | Usage/quota | Normalize only metrics actually returned by the provider; preserve exact raw metric provenance and null/unknown semantics |
| `quota_observation_ref` | Quota evidence reference | Link to source/time/scope, not a guessed balance |
| `http_status`, `outcome`, `error_class`, `retry_after` | Result | Preserve raw status and documented retry metadata |
| `data_class`, `attribution_confidence` | Safety/evidence | Explicit classification and confidence |

**Never emit:** API keys, Authorization headers, prompts, completions, arbitrary request/response bodies, private context, raw environment variables, or unredacted provider errors. Error excerpts must pass the repository's secret/content scrubber before persistence.

## Quota model and dashboard contract

Extend the existing quota registry, passive provider quota managers, quota poller, and existing dashboard feeds. Do not create a competing poller or a second quota dashboard.

Each quota observation must carry:

- `provider_id` and optional `model_id`
- `scope` (`account`, `key`, `model`, `project`, `organization`, or provider-defined scope)
- `status`: `observed`, `documented`, `unknown`, `stale`, or `error`
- `value`, `limit`, `unit`, `window`, `reset_at`, `reset_basis`
- `source`, `authority` (account-authoritative vs public/catalog claim), `observed_at`
- `evidence_ref`, `credential_alias` (names-only), and `confidence`

Rules:
- Null means not observed, never zero.
- Separate entitlement from remaining account balance.
- Preserve provider reset headers and `Retry-After` exactly when documented.
- Do not assume 402 or 429 universally means quota exhaustion; classify from provider-specific evidence.
- Unknown/stale quota cannot authorize paid fallback or routing.
- Usage cost is recorded only when the provider returns a trustworthy usage/cost value or a separately documented price calculation is explicitly labelled estimated.

## DoE pool participation

The existing `util-1-provider-rotation` campaign is the correct live campaign to extend; do not create a duplicate campaign. Its design already observes live dispatches, uses desk-assigned rotation, requires provider/selection-reason/timestamp stamps, and records returned quota cost in usage slots when available.

AgentRouter is now a **pre-registered conditional arm** in `experiments/doe/util-1-provider-rotation/DESIGN.json`; it remains non-dispatchable until its credential, account model discovery, separate inference admission, spend ceiling, data classification and stop-switch gates pass. Once activated, the first real desk-stamped dispatch is an observation requirement, not an activation gate; the auditor retains exact model/protocol identity, workflow/run/attempt correlation and returned usage metrics before scoring. Any future gateway arm still requires a design amendment that names:
- provider arm and exact model/protocol identity;
- eligibility and credential gate;
- quota/spend ceiling and kill switch;
- randomization/rotation rule and no-consecutive-dispatch constraints;
- task strata and frozen outcome definitions;
- per-run usage, latency, retries, errors, first-pass success, rework and human-intervention fields;
- sample-size/window and cull/promote thresholds;
- evidence location and owner approval.

One dispatched/executed run = one experiment observation. A catalog/registry entry is not an executed DoE observation. AgentRouter's conditional pre-registration does not make it dispatchable. No campaign result or provider promotion may be claimed until actual run records exist. The campaign observes desk assignment; it does not mutate the desk's routing rule.

## Integration sequence and acceptance gates

| Phase | Deliverable | Acceptance gate |
|---|---|---|
| P0 | Consolidated inventory, schema, ownership and status | No duplicate systems of record; ForeSight existing radar/evidence spine linked |
| P1 | AgentRouter authenticated model discovery | Adapter and unit coverage added in this PR (pending merge); owner reports key provisioned; authenticated account model observation pending; inference remains disabled pending separate admission review |
| P2 | Quota manager and dashboard projection | Provider-specific documented signals only; unknown/stale states preserved; tests cover null/zero, resets, 401/402/429/5xx |
| P3 | Temporal/HindSight/Provenance/Witness correlation | Shared IDs and evidence digests; independent sink failures; no prompt/secret leakage |
| P4 | n8n/Gravitee/Platform201/Bifrost integration edges | Each edge has live evidence; no mock/console/evaluation state promoted to production |
| P5 | DoE campaign amendment + ATES/3L0 outcome joins | Committed design + per-run records; no synthetic observations; evidence-based cull/promote |
| P6 | Unified dashboard projection | Existing results-index remains intact; every card exposes source, observed-at, state, gaps and drill-through |

### Required regression coverage

- schema validation and unique IDs;
- stale/unknown/null quota semantics;
- secret and prompt scrubbing;
- provider model discovery failure and malformed catalog;
- protocol/base-URL separation;
- request correlation across retries and workflow attempts;
- independent HindSight and Provenance failure behavior;
- idempotent event ingestion;
- DoE stamp missing → observational-only;
- Bifrost evaluation and Gravitee ephemeral status cannot be promoted by catalog presence alone;
- ForeSight uses its existing radar and evidence-spine records; no duplicate research registry is introduced.

## Source of truth and supporting records

- `docs/ops/TELEMETRY-VIZ-RECON.md` — stream inventory and n8n/Platform201/Gravitee/Witness visualization boundaries.
- `scripts/telemetry_ingest/results_index.py` + `ops/telemetry/results-index.json` — ATES/3L0/Temporal/HindSight record-of-record projection.
- `docs/ops/TELEMETRY-INGEST.md` — independent HindSight and Provenance sinks.
- `docs/ops/ROUTING-ORCHESTRATION-MAP.md` — three-plane routing boundary and Bifrost evaluation gate.
- `docs/ops/GRAVITEE-SELFHOST.md` + `docs/ops/gravitee-connector/CONNECTOR.md` — ephemeral Gravitee self-host evidence.
- `docs/ops/N8N-FREE-COMMUNITY-WIRING.md` + `ops/n8n/` — optional n8n adapter.
- `docs/ops/PLATFORM201-LIVE-2026-10-27.md` — Platform201 deployment evidence and API credential gap.
- `docs/proposals/active/bifrost-gateway-integration/ITEMS.md` — Bifrost status; benchmark results pending.
- `config/agent_stack_integrations.json` + `docs/research/RUNTIME-PROVENANCE-AIBOM.md` — Witness integration/provenance references.
- `scripts/provider_model_catalog.py`, `scripts/provider_extension_catalogs.py`, `scripts/provider_quota_managers.py`, `ops/quota/provider-managers.json` — provider discovery and passive quota normalization. AgentRouter is authenticated catalog-only; per-inference usage/quota metrics are captured as request-level evidence when returned, while aggregate balance/reset remains unknown pending an account-authoritative signal.
- `experiments/doe/util-1-provider-rotation/DESIGN.json` + `docs/ops/DOE-FAMILY.md` — live provider-rotation experiment contract.

This document records an integration baseline. It does not assert that all integrations are credentialed, deployed, healthy, or approved for production traffic.
