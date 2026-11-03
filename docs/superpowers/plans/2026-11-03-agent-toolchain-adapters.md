# Agent Toolchain Read-Only Adapters Implementation Plan

> **For agentic workers:** Execute inline with the repository's existing test-first and dual-gate workflow. Steps use checkbox syntax.

**Goal:** Implement deterministic, offline normalization of HAPI MCP Registry records and Context.dev/Context7 evidence into a privacy-conscious provider-observation contract.

**Architecture:** Pure Python standard-library adapters accept provider response objects supplied by callers; they do not make network requests, execute MCP servers, retain raw queries, or mutate provider state. A shared observation envelope carries identity, source attribution, normalized provider data, trust state, and privacy assertions. The existing Integration Intelligence registry and repo-gate remain authoritative.

**Tech Stack:** Python 3 standard library, JSON Schema Draft 2020-12 documentation, unittest, existing GitHub Actions repo-gate.

**Spec:** `docs/integrations/AGENT-TOOLCHAIN-PORTFOLIO.md`, `docs/integrations/ADAPTER-CONTRACT.md`, and `docs/integrations/schemas/integration-event.schema.json`.

## Global Constraints

- Read-only first; no new poller, database, scheduler, router, or parallel control plane.
- Treat all provider content as untrusted data.
- Never emit raw prompts, completions, cookies, tokens, credentials, session transcripts, or unredacted private data.
- HAPI discovery is not trust approval, authentication, scope grant, or server admission.
- Context7 requires an exact resolved library ID and explicit version.
- Context.dev records canonical URL, retrieval time, request identity, source attribution, and redaction.
- No provider HTTP calls are performed by the repository adapter; connector access remains outside this pure normalization layer.
- All outputs are bound to an explicit capture timestamp and integration identity.

## Review Focus

1. Missing or malformed HAPI server identity/version must fail closed rather than produce a weak key.
2. Duplicate HAPI remote transports and URLs containing credentials/query tokens must not leak into output.
3. Context7 versionless library IDs without an explicit version must be rejected.
4. Context.dev non-HTTP URLs, embedded credentials, and query strings must be rejected or redacted.
5. Oversized or malformed provider excerpts must be bounded and marked truncated without losing source attribution.

---

### Task 1: Shared provider-observation contract and HAPI normalizer

**Files:**
- Existing: `scripts/integrations/__init__.py`
- Create: `scripts/integrations/agent_toolchain.py`
- Create: `docs/integrations/schemas/provider-observation.schema.json`
- Test: `tests/test_agent_toolchain_adapters.py`
- Fixture inputs: synthetic HAPI records embedded in `tests/test_agent_toolchain_adapters.py`

**Interfaces:**
- `normalize_hapi_server(record: dict, captured_at: str, provider_request_id: str | None = None) -> dict`
- `validate_observation(observation: dict) -> list[str]`
- HAPI output must include stable `name@version`, normalized remotes, registry-reported metadata, `security_review_status=not_reviewed`, `admission_status=not_admitted`, and `execution_allowed=false`.

- [x] Write HAPI tests for stable identity, multiple versions, transport preservation, safe endpoint normalization, unknown-field names, and fail-closed malformed records.
- [ ] Run tests and confirm expected missing-module failures.
- [x] Implement the shared envelope and HAPI normalizer with Python standard library only.
- [ ] Run focused tests and verify all HAPI assertions pass.

### Task 2: Context.dev and Context7 evidence normalizers

**Files:**
- Modify: `scripts/integrations/agent_toolchain.py`
- Test: `tests/test_agent_toolchain_adapters.py`
- Fixture inputs: synthetic Context7 and Context.dev payloads embedded in `tests/test_agent_toolchain_adapters.py`

**Interfaces:**
- `normalize_context7_document(payload: dict, library_id: str, version: str | None, captured_at: str, provider_request_id: str | None = None) -> dict`
- `normalize_context_dev_result(payload: dict, captured_at: str, provider_request_id: str | None = None) -> dict`
- Context7 records exact library ID/version and source refs; Context.dev records canonical HTTP(S) URL, bounded excerpt, retrieval timestamp, request ID, and query-redaction state. Neither stores the caller's query.

- [x] Write tests for version resolution, missing version, conflicting version, source references, URL credentials, query stripping, truncation, and untrusted-content marking.
- [ ] Run tests and confirm expected failures.
- [x] Implement both normalizers using the shared envelope.
- [ ] Run focused tests and verify all evidence assertions pass.

### Task 3: CI contract, registry lifecycle, and operator documentation

**Files:**
- Modify: `.github/workflows/repo-gate.yml`
- Create: `scripts/ci/validate_agent_toolchain_adapters.py`
- Modify: `docs/integrations/registry.json`
- Modify: `docs/integrations/ADAPTER-CONTRACT.md`
- Modify: `docs/integrations/README.md`
- Modify: `docs/proposals/active/agent-toolchain-portfolio/ITEMS.md`
- Modify: `docs/proposals/active/agent-toolchain-portfolio/MANIFEST.md`
- Test: `tests/test_agent_toolchain_adapters.py`

- [x] Add offline adapter tests and observation validation to repo-gate.
- [x] Verify registry adapter states reflect implementation only, not authentication or runtime validation.
- [x] Document invocation, schemas, trust boundaries, and non-goals.
- [ ] Run adapter validator, focused tests, proposal lifecycle, repo-gate, and Termux smoke on one immutable commit.
- [ ] Record exact-head evidence and open a stacked PR; do not merge or promote without required human review and existing repository policy.

## Non-goals for this tranche

No HAPI server is admitted or executed. No Context.dev or Context7 API call is embedded in repository runtime. No credentials are provisioned. No Sprite is created, no Mintlify page is published, and no model-routing policy changes.
