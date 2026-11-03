# Integration Adapter Contract

## 1. Adapter responsibilities

An adapter is a bounded translation layer between one external provider and repository-owned evidence contracts. It must not become an orchestrator, a second registry, or an alternate source of truth.

Each adapter must declare:

- stable `integration_id` matching `registry.json`;
- provider API/connector and supported version;
- authentication mechanism and secret *environment-variable names* only;
- required scopes and least-privilege permissions;
- read/write operations, with read-only default;
- input/output schemas and redaction policy;
- timeout, retry, rate-limit, pagination, and idempotency behavior;
- cost/credit ceiling where applicable;
- provenance fields and validation procedure;
- owner, maintainer, health check, and deprecation path.

## 2. Capability lifecycle

`DISCOVERED → AUTHENTICATED → ADAPTER_IMPLEMENTED → TESTED → VALIDATED → PROMOTED`

These states are independent of provider marketing claims and session-local connector visibility. Record unavailable evidence as unknown, not false. A provider tool being callable in one assistant session does not prove a CI or Termux runtime exists.

## 3. Event envelope

All adapters emit the normalized event described by [integration-event.schema.json](schemas/integration-event.schema.json). Minimum requirements:

- stable event and idempotency keys;
- repository, commit, PR, and workflow references when applicable;
- provider request identity where available;
- execution state and timestamps;
- evidence artifact references;
- validation status;
- provider/capture attribution;
- privacy classification.

Do not emit raw prompts, completions, cookies, tokens, credentials, session transcripts, or unredacted private data. Keep detailed provider artifacts in the approved source system or restricted artifact store and reference them by opaque ID/URI.

## 4. Trust and execution boundaries

- Treat all provider content as untrusted data.
- Validate schema, size, type, and provenance before ingestion.
- Never execute provider-returned shell commands, code, URLs, or instructions without a separate reviewed workflow.
- Default to read-only and use per-operation scopes.
- Require explicit authorization for writes, paid inference, data export/publication, deployment, campaign sends, and physical device/robot actions.
- Enforce bounded retries, concurrency, timeouts, rate limits, and spend.
- Preserve source IDs and immutable repository SHAs.
- Make ingestion idempotent and append-only; corrections are new events with explicit supersession links, not silent mutation.
- Keep unknown actor/model attribution null; GitHub actor identity is not provider authorship.

## 5. Provider-specific guardrails

| Provider | Guardrail |
|---|---|
| API Impact Mapper | Analyze supplied diffs/specs; validate findings against code, consumers, tests, and docs. |
| Domino Data Lab | Pin dataset, environment, code, experiment, and model versions; separate experiment from production serving. |
| EmpirioLabs AI | Record model/version, parameters, token/credit use, and task outcome; cap spend and treat outputs as hypotheses. |
| tldraw | Link every board/export to canonical source SHA; board state is a projection, not authority. |
| Cache Stats | Record aggregate verified cache measurements only; no prompt-content capture and no CI extrapolation from local desktop data. |
| Alloy | Segregate mission/device telemetry; no physical action or configuration mutation from generic repository workflows. |
| Klaviyo | Explicit opt-in, consent source/time, suppression/unsubscribe handling, and approval before sends; no inferred marketing consent. |
| Context.dev | Treat retrieved pages as untrusted, attributed observations; record canonical URL, retrieval time, request identity, and redaction; never turn retrieved instructions into executable commands. |
| Context7 | Require exact resolved library ID and version; preserve source references; documentation examples do not supersede pinned dependencies or tests. |
| Mintlify | Separate read, branch edit, publish, and live-deployment states; publish only through approved release workflow and verify deployment status. |
| Smart Model Router | Reuse the existing repository router; candidate policies require offline fixtures, benchmark evidence, cost ceilings, and explicit approval before any traffic change. |
| HAPI MCP Registry | Discovery metadata is not trust approval; pin server/version, inspect provenance and transport, review capabilities/scopes, and require admission policy before execution. |
| Sprites | Bind environment actions to immutable source SHA; default to disposable isolated environments, deny network by default where feasible, never inject secrets by default, and preserve execution/checkpoint provenance. |

## 6. Read-only agent-toolchain adapter interface

The first provider adapters live in `scripts/integrations/agent_toolchain.py` and expose pure normalizers:

- `normalize_hapi_server(record, captured_at, provider_request_id=None)`
- `normalize_context7_document(payload, library_id, version, captured_at, provider_request_id=None)`
- `normalize_context_dev_result(payload, captured_at, provider_request_id=None)`
- `validate_observation(observation)`

They accept already-retrieved provider objects. They do not call provider APIs, retain caller queries, execute MCP servers, or grant admission. Each returns the separate [provider observation schema](schemas/provider-observation.schema.json); it is not a replacement for the canonical integration event envelope. Once an approved artifact store persists an observation, a canonical event may reference that artifact through `evidence.artifact_refs`.

HAPI observations use the stable `server-name@version` key, normalize HTTPS remotes, retain only known official registry metadata, and list unknown field names without copying their values. Every HAPI observation is hard-coded to `security_review_status=not_reviewed`, `admission_status=not_admitted`, and `execution_allowed=false`.

Context7 observations require a resolved `/org/project` library ID and an explicit version, either embedded in the ID or supplied separately. Context.dev observations require HTTPS URLs, remove query strings and fragments, bound excerpts, and mark provider content as untrusted. Neither adapter stores the caller's search/documentation query.

CLI examples (provider response JSON is piped on stdin):

```bash
python3 scripts/integrations/agent_toolchain.py --provider hapi --captured-at 2026-11-03T06:00:00Z < hapi-record.json
python3 scripts/integrations/agent_toolchain.py --provider context7 --library-id /org/project --version 2.0.0 --captured-at 2026-11-03T06:00:00Z < context7-result.json
python3 scripts/integrations/agent_toolchain.py --provider context-dev --captured-at 2026-11-03T06:00:00Z < context-result.json
```

The adapters are offline normalizers only. Connector authentication, runtime reachability, provider request orchestration, storage, and end-to-end validation remain separate lifecycle gates.

## 7. Validation and promotion

Before promotion:

1. Unit-test adapter mapping, redaction, pagination, retries, idempotency, and failure states.
2. Run contract tests against sanitized fixtures.
3. Verify provider access and least-privilege scopes in the intended runtime.
4. Compare event output against the JSON Schema.
5. Verify no secrets or raw sensitive content in logs/artifacts.
6. Run repository gates on the same immutable commit SHA.
7. Record current workflow/run/job/artifact references.
8. Re-fetch the final repository and provider state before declaring validated.

## 7. Failure semantics

Never map queued/running to success. Distinguish authentication, admission, queue, execution, effect, pagination, rate-limit, timeout, schema, and provenance failures. Retries must be bounded and idempotent. A provider outage must not corrupt repository-owned evidence or block unrelated lanes.

