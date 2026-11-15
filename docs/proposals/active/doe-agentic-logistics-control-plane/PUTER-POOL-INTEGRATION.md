# Puter Pool — governed provider-transport integration

**Proposal item:** DPLC-010  
**State:** source-audited candidate · implementation queued · runtime ineligible  
**Source:** [timerloggedout-spec/puter-pool_fork](https://github.com/timerloggedout-spec/puter-pool_fork)  
**Pinned source commit:** `34d284fa616ad0f23fb755100ce0512185d02d71`  
**Canonical owners:** Integration Intelligence · provider/quota registry · QUE · DoE · ATES/3L0 · telemetry ingest

## 1. Decision

Register Puter Pool as a **transport-adapter candidate** for the existing Puter provider family. Preserve the current `g4f/Puter` population and `g4f.puter` quota record as the canonical provider-family/quota references.

`Puter` = upstream model/service provider.  
`Puter Pool` = OpenAI-/Anthropic-compatible gateway implementation.  
`g4f/Puter` = existing harvested provider-family record.  
`account_scope_ref` = opaque configured-account scope, never a token or token-derived fingerprint.

The fork is useful source material for protocol translation, model discovery, health observations and request scheduling. Its current multi-account credit aggregation and cross-account retry behavior are **outside the eligible design**. The initial adapter target is one explicitly authorized account scope per configured instance, one attempt per dispatch, exact model identity, and no paid or alternate-provider fallback.

No fork code, dependency, account token, runtime endpoint, live inference, schedule, deployment or production routing change is introduced by this proposal update.

## 2. Source audit and provenance

| Source | Pinned blob SHA | Finding |
|---|---|---|
| `README.md` | `95103458eee9aeedcda308f0d23d2df0cd65f2b8` | Claims 400+ models, account pooling, OpenAI/Anthropic routes and local dashboard; claims require independent verification |
| `package.json` | `d321094815175623455f0742bc9e1b656350e705` | Node 20+, TypeScript, Express, SQLite; declares Apache-2.0 |
| `src/scheduler/RequestScheduler.ts` | `c641ef993971e604da4f618038c375c72b2457b5` | Round-robin/least-used account selection; retries can select another account after failure |
| `src/accounts/AccountManager.ts` | `d47131fefa09f4e18785a506dda4239bd279f1d6` | Persists account token through the database adapter |
| `src/credit/CreditTracker.ts` | `df4f27613f8e113e0867fb885375162729d2e106` | Computes a synthetic per-account limit from account count; not provider-authoritative quota |
| `src/auth/AuthenticationManager.ts` | `d8695230757e975eb83eadb58f860aaee1fbe4c8` | Verifies account tokens against Puter `/whoami` |
| `src/api/openai.ts` | `235200ce0020a2c5ee02cfb7e849507053d8e1f3` | OpenAI-compatible model listing and chat-completion adapter |
| `src/api/anthropic.ts` | `9cde97d978cb927d7e8af655cf2864af0c251848` | Anthropic-compatible message adapter |
| `src/api/middleware.ts` | `f9f521dbc5b99a546e15f54f53155510001c8952` | API-key middleware exists; runtime wiring requires review |
| `src/index.ts` | `5abfb6f88b0904272fc7f310b38d43e9c9f8d992` | Express route/middleware ordering and startup process handling require review |
| `LICENSE` | `e48e0963459bf4c4e175956b657a8f4a91967880` | EPL-2.0 text conflicts with README/package metadata declaring Apache-2.0 |

Source commit and blob identities are provenance pins, not security certification or permission to redistribute source.

## 3. Adoption blockers

| Finding | Required disposition |
|---|---|
| README/package metadata declare Apache-2.0 while LICENSE contains EPL-2.0 | Resolve upstream licensing and fork provenance before copying or distributing source |
| Scheduler retries through another account after failure, including rate-limit/credit paths | Replace with one-attempt semantics; no cross-account failover |
| CreditTracker synthesizes limits from account count | Treat all internal credit totals as non-authoritative; use provider-documented account/model quota evidence only |
| SQLite schema stores account tokens and raw prompts/completions | Remove raw-content persistence from the integration path; secrets remain in approved secret storage |
| AccountManager stores bearer tokens in the database | Require approved secret handling, encryption/custody review and opaque account references |
| API authentication middleware is mounted after API route handlers in the inspected entry point | Correct middleware order and prove route-level authorization before any network exposure |
| Startup attempts to kill the process bound to port 3000 | Remove process-kill side effects; use managed lifecycle and explicit port ownership |
| Request records lack QUE/DoE task correlation and per-attempt normalized evidence | Add the canonical correlation envelope and contract tests |
| Provider request errors may contain raw response text | Normalize to fixed error classes/status metadata; scrub before persistence |

The source README itself instructs operators to retrieve `auth_token` from browser local storage. That browser-session extraction path is excluded from this integration. Use only a provider-supported, reviewed machine-authentication flow. Never request or store a token in chat, Git, artifacts, telemetry or dashboard feeds.

## 4. Provider identity and eligibility

Canonical configured-instance identity:

`(provider_family, exact_model_id, endpoint_or_route_id, protocol, account_scope_ref, configured_instance_key)`

- `provider_family = puter`
- `gateway_id = puter-pool`
- `protocol ∈ {openai-compatible, anthropic-compatible}`
- `exact_model_id` comes from a fresh, trusted model catalog observation.
- `account_scope_ref` is a random opaque reference for one authorized account scope.
- `configured_instance_key` is the existing DoE/dispatch stamp, not a credential fingerprint.

Eligibility states reuse the existing population contract: `discovered → catalog_observed → transport_wired → availability_verified → no_cost_entitlement_verified → quota_headroom_verified → policy_and_data_class_verified → eligible`. Any unknown, stale or contradictory gate yields `deferred` or `excluded`.

### Quota ruling

The existing `ops/quota/registry.json` record `g4f.puter` remains the quota authority pointer. Its current evidence says limit, window, reset and live account balance are unknown; runtime eligibility is false. Puter documentation describes a user-pays model/free allowance without an authoritative numeric account balance in the existing record.

Therefore:
- `limit = null`, `remaining = null`, `reset_at = null` until an account-authoritative source reports them;
- catalog model count, `:free` labels, README marketing, local CreditTracker totals and account count never establish free entitlement or quota;
- no-cost entitlement is verified per exact model + account scope + execution environment;
- a 429 is a terminal observation unless authoritative provider reset metadata and a separately approved policy establish a safe later attempt.

### Pooling rule

- One admitted dispatch → one configured account scope → one provider attempt.
- No cross-account retry, account hopping, aggregate credit arithmetic, shared-account substitution or hidden fallback.
- Multiple independently owned account scopes may be represented as distinct configured instances only after Puter's terms explicitly permit the use and the owner approves the experiment design.
- A provider-side policy/terms change triggers re-evaluation before further admission.

## 5. QUE → DoE → provider execution

Reuse the existing chain:

`Project Task → QUE admission → task/dispatch correlation → existing provider-batch/native inference executor → Puter transport adapter → normalized result → independent verification → DoE/ATES/3L0`

- QUE remains the admission authority. Issue-open listeners never invoke Puter before admission.
- The existing provider-batch/native inference path remains the executor; Puter Pool does not add a second queue, scheduler, worker fleet or dispatch workflow.
- DoE extends `util-1-provider-rotation` through its distinct, versioned free-inference cohort. Provider endpoint effects remain separate from later manager-policy effects.
- Every scored request must carry the existing rule-7 set/instance stamps: `instance_key`, `set_index`, `cumulative_n`, `selection_reason`, `trigger`, `task_or_entry_ref`, `entry`, `provider`, `exact_model_id`, `model`, `endpoint_or_route_id`, `workflow_run_id`, `run_attempt`, `observed_at`, `ts`. The producer emits intake-native `model`, `entry`, and `ts`; normalized fields map `exact_model_id ← model`, `task_or_entry_ref ← entry`, and `observed_at ← ts`; the existing auditor projection keeps `model_id` populated from `model`.
- The deferred-by-tier re-evaluation path, generic issue-open listener gate and #5195 admission issue retain their existing blocked states until separately proven/remediated.

## 6. Telemetry contract — one event, many projections

Emit one sanitized observation per actual upstream provider attempt, not merely per outer proxy request. Preserve retry/attempt identity even when the final task has one result.

Required identity and correlation:
- provider family, gateway/adapter version, exact model, protocol, endpoint/route;
- opaque account scope and configured-instance key;
- task/issue reference and QUE dispatch/admission reference from the canonical task packet;
- DoE campaign, experiment instance, set index and selection reason when assigned;
- GitHub workflow run, attempt, job and source SHA;
- provider request ID when returned.

Required measured outcomes, when actually available:
- start/end UTC and elapsed latency;
- time-to-first-token and tokens/second;
- input/output/total tokens;
- provider-reported quota tokens and usage cost;
- HTTP status, fixed error class, timeout/rate-limit state and retry-after metadata;
- task verification result, rework, retry count, integration result and attribution confidence.

Missing measurements remain `null` / `unknown`; never synthesize zero, quota balance, token usage or model success. Preserve source, scope, observed-at and provider-reported/derived attribution for each metric.

### Canonical destinations and responsibilities

| Surface | Puter Pool contribution | Authority / boundary |
|---|---|---|
| Integration Intelligence + provider catalog | Adapter identity, exact model/protocol and source provenance | Existing registries remain canonical; no duplicate catalog |
| Quota registry + quota poller | Account/model quota observations and freshness | Extend `ops/quota/registry.json`, provider manager and existing poller; unknown stays null |
| QUE / QDesk | Task, admission, dispatch and recipient correlation | Existing admission/dispatch records; provider does not self-admit |
| DoE / ATES | Stamped experiment attempt, deterministic outcome and quality evidence | Existing `util-1-provider-rotation`, ATES and manager tournament contracts |
| 3L0 | Session and longitudinal observation references | Existing observational/confirmed distinction |
| Temporal | Workflow/activity correlation where an actual Temporal execution exists | Current Actions evidence remains valid when Temporal is ephemeral; never invent a Temporal workflow ID |
| HindSight | Sanitized IDs/counts/statuses/hashes for retention | Existing independent sink; current stale 402 evidence requires refresh before claiming retained coverage |
| Provenance + Witness | Evidence digest and signed build/artifact attestation reference | Existing provenance ledger and in-toto/Witness placement; no second ledger or signing-key store |
| Bifrost | Optional comparative gateway arm | Evaluation-only until benchmark results and dual-gate evidence |
| n8n | Optional workflow composition/notification adapter | Actions/QUE remain authoritative; n8n is not another scheduler |
| Platform201 | Deployment/host metadata where supported | Host projection only; not a telemetry backend or invented API poller |
| Web interfaces / SHE | Read-only quota, task, execution and DoE projections | Extend existing quota/SHE/dashboard feeds; no new dashboard truth or browser-to-provider calls |

The existing telemetry ingest already declares `ops/quota/registry.json` and `data/g4f-working/providers.json` as sources and independently emits HindSight and Provenance records. Reuse `scripts/telemetry_ingest/sources.json`, `scripts/telemetry_ingest/ingest.py`, `ops/telemetry/results-index.json` and the existing dashboard feeds. Refresh and inspect the actual ingest receipt before claiming end-to-end coverage.

### Privacy

Exclude API keys, bearer tokens, Authorization headers, browser storage, raw prompts, completions, raw request/response bodies, account profile data and unredacted provider errors from every event, log, artifact, Hindsight payload, Witness statement and web feed. Use allowlisted scalar metrics, fixed error enums, opaque references and content hashes only.

## 7. Web-interface contract

The existing quota UI already carries the Puter family: `provider-quota-coverage.json` maps `g4f/Puter` to `g4f.puter` with `observation_method=manual_or_unknown`, while `quota.json` reports `status=unknown` and null `used`, `limit`, `reset` and `observed_at` (re-fetched 2026-11-13). Preserve this row and its unknown semantics. QUE/DoE task identity continues through the canonical `entry`/`task_or_entry_ref`, admission/dispatch receipt, experiment stamps and workflow run; the proposed correlation extension is specified above without creating a parallel task ledger.

Extend the existing quota and SHE projections with:
- provider family + exact model + gateway/protocol;
- configured instance and opaque account scope;
- eligibility state and reason code;
- quota value/limit/unit/window/reset/source/authority/observed-at/freshness;
- task/QUE dispatch and DoE experiment references;
- run/attempt, latency, usage, retries and terminal outcome;
- evidence/attestation references and validation state.

Use the existing quota UI and SHE feeds. Show `UNKNOWN`, `STALE`, `DEFERRED`, `EXCLUDED`, `SUCCEEDED`, `FAILED` as distinct states. Keep unknown quota separate from zero and committed separate from executed/validated/promoted. Account identifiers remain opaque; secrets and private content never enter browser payloads.

## 8. Phased acceptance

| Phase | Deliverable | Acceptance |
|---|---|---|
| P0 | Source/license/security disposition | License mismatch resolved; source provenance pinned; auth ordering, token custody, raw-content storage and process lifecycle remediated |
| P1 | Native single-account adapter | Exact model identity; OpenAI/Anthropic contract tests; one-attempt behavior; no cross-account rotation or paid fallback |
| P2 | Quota + telemetry contract | Provider-authoritative quota; task/QUE/DoE/run correlation; schema validation; privacy tests; idempotent event IDs |
| P3 | Existing pipeline integration | Existing provider-batch path; QUE admission proof; DoE versioned cohort; independent verification; existing sink/read-model receipts |
| P4 | Web projections | Existing quota/SHE feeds updated with source, freshness, instance, task and experiment correlation |
| P5 | Bounded live smoke | Separate explicit owner authorization, exact endpoint/account scope, public synthetic task, request/token budget and stop switch; no schedule or automatic retry |

### Required tests

1. Exact model/endpoint identity and source freshness.
2. Single account scope per attempt; 429/402/401 never trigger another account.
3. No paid, alternate-model or alternate-provider fallback.
4. Unknown quota/entitlement blocks admission.
5. Prompt/completion/token redaction and secret-canary tests across logs, DB, artifacts and feeds.
6. QUE admission and issue-open listener regression coverage.
7. DoE stamps, task correlation, idempotency and one-event-per-upstream-attempt.
8. Temporal ID is nullable when absent; Actions run/attempt remains authoritative.
9. HindSight and Provenance sink failures remain independent.
10. Existing dashboard feeds render stale/unknown/deferred states without inventing balances.

## 9. Current disposition

- **Source repository:** pinned and inspected.
- **Transport concept:** useful candidate.
- **Provider family:** existing Puter/g4f record reused.
- **License:** contradictory; resolution required.
- **Terms/account pooling:** not established for this integration.
- **Account entitlement/quota:** unknown.
- **Runtime adapter:** not implemented.
- **QUE/DoE admission:** existing gates retained.
- **Telemetry destinations:** mapped to existing canonical systems; runtime receipt refresh required.
- **Production routing / live inference / scheduling:** not authorized by this proposal update.

**Promotion invariant:** `DISCOVERED → SOURCE_REVIEWED → LICENSE_CLEARED → ADAPTER_TESTED → ENTITLEMENT_VERIFIED → QUOTA_VERIFIED → QUE_ADMITTED → EXECUTED → INDEPENDENTLY_VALIDATED → PROMOTED`.

See also [Unified Provider & Observability Index](../../../ops/UNIFIED-PROVIDER-OBSERVABILITY-INDEX.md), [Telemetry Ingest](../../../ops/TELEMETRY-INGEST.md), [Integration Adapter Contract](../../../integrations/ADAPTER-CONTRACT.md), and [free-inference tournament order](./FREE-INFERENCE-TOURNAMENT-ORDER.yml).
