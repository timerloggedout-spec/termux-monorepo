# API Impact Review Lane — Design

**Status:** Authorized for implementation under the operator directive "Do EVERYTHING" (2026-11-02)
**Parent:** [Integration Intelligence design](../../superpowers/specs/2026-11-02-integration-intelligence-design.md)
**Proposal:** APII-001

## Intent

Turn API Impact Mapper into a usable, auditable repository workflow for pull requests that change public or integration-facing API contracts. The workflow must detect likely API-surface changes, accept structured findings from the connected API Impact Mapper, validate and normalize those findings, and publish a machine-readable report without giving the provider authority over source code or merge decisions.

## Current repository evidence

- `llm_api_hub/server/app.py` implements the local OpenAI-compatible gateway routes and request/response contracts.
- `llm_api_hub/clients/openai_compat.py` is a public client boundary.
- `llm_api_hub/schemas/openai-chat-completions.example.json` documents request/response shapes.
- `hub_mcp/protocol.py` and `tests/hub_mcp/test_protocol.py` define an MCP-facing protocol boundary.
- `deepcli/investigator/api_map.py` is an existing API surface inventory utility, but its current regex/line heuristic is provider-specific and not a PR impact evidence contract.
- `tests/test_llm_api_hub_server.py` is a repository-native unittest suite for gateway behavior.

## Goals

1. Detect changed API-contract files from a base/head Git diff with a versioned, repository-maintained path policy.
2. Emit a deterministic report even when external analysis is not yet supplied.
3. Accept the three API Impact Mapper result classes (extraction, breaking classification, impact map) as structured input.
4. Validate evidence references, change IDs, impact IDs, classifications, status, source SHA, PR identity, and privacy constraints before accepting a report.
5. Preserve mapper limitations and missing fields; never convert `cannot_determine` into a definitive classification.
6. Publish a PR-scoped JSON artifact and human-readable summary.
7. Keep the workflow read-only, dependency-light, Termux-compatible, and non-blocking until provider-runtime connectivity is independently available and explicitly promoted.

## Non-goals

- Calling the ChatGPT MCP tool directly from GitHub Actions; no provider endpoint or runner credential contract has been established.
- Allowing the mapper to modify files, approve PRs, merge, deploy, or override CI.
- Treating every file named `api` or `schema` as a public API.
- Storing raw prompts, completions, credentials, private user content, or full diffs in the report.
- Claiming complete consumer discovery when only changed files and supplied evidence are available.

## Approaches considered

1. **Direct MCP invocation inside GitHub Actions.** Rejected: the current connector is exposed to this assistant session, not as a documented, authenticated CI endpoint. Inventing an endpoint or copying session credentials would be unsafe and non-reproducible.
2. **Assistant-assisted mapper + repository-owned deterministic report normalizer.** Selected: the assistant retrieves a pinned PR diff, supplies that evidence to API Impact Mapper, and writes its structured results into a report input. Repository code validates the result and CI publishes/validates the artifact. This works with the actual tool boundary today.
3. **Build and operate a separate hosted MCP/API bridge.** Deferred: this adds credential custody, service availability, auth, rate limits, spend, and operational ownership before there is evidence it is necessary.

## Architecture

```
PR base/head + changed paths
       |
       v
deterministic API-surface detector (versioned path policy)
       |
       +---- no API paths ----> NOT_APPLICABLE report
       |
       v
assistant retrieves diff + contract/consumer/test context
       |
       v
API Impact Mapper: extract -> classify -> map
       |
       v
mapper-result JSON input (no raw prompt/session data)
       |
       v
strict normalizer + evidence/ID/SHA/privacy validation
       |
       v
PR-scoped report JSON + Markdown summary
       |
       v
CI artifact + advisory check (no merge authority)
```

## Report states

- `not_applicable`: no configured API surface files changed.
- `analysis_required`: API surface changed but no mapper result supplied.
- `partial`: mapper returned partial/incomplete findings or unresolved classifications.
- `validated`: structured results passed all repository contract checks.
- `invalid`: malformed, stale, mismatched, unsupported, or privacy-unsafe input.

The state `validated` means report structure and evidence links validate; it does not mean the code is compatible or safe. Breaking findings remain explicit.

## API-surface policy

Initial configured surfaces are deliberately narrow and grounded in the current repository:
- `llm_api_hub/server/**`
- `llm_api_hub/clients/**`
- `llm_api_hub/schemas/**`
- `hub_mcp/**`
- `commingle-swarm/web/src/api/**`
- `apps/listinglens/src/schemas.mjs`
- `apps/listinglens/tests/schemas.test.mjs`
- `deepcli/investigator/api_map.py`
- `deepseek-cli/test/api_probe.test.js`
- `_1-Projects/a/yobitrageswap/api/**`

The list is configuration, not a heuristic hidden in code. Expand it only with reviewed evidence.

## Trust and privacy

- The provider result is untrusted input; validate every field and reference.
- Every classification/impact must reference evidence emitted by the mapper result or explicitly supplied repository context.
- The report records repository, PR, base SHA, head SHA, provider name, and capture method.
- Never store source text, raw prompts/completions, tokens, cookies, or private data in the report.
- Redact credentials from exception messages and logs.
- Provider findings are advisory. Human review and repository gates remain authoritative.

## Rollout

1. Land schema, deterministic detector, normalizer, tests, CLI, and assistant skill.
2. Add a non-blocking PR workflow that emits `not_applicable` or `analysis_required` reports and validates supplied report inputs.
3. Run in observation mode; review false positives/negatives.
4. Only after evidence and a real CI-callable provider interface exist, propose a separate promotion to a blocking required check.

## Acceptance

- Termux-compatible standard-library implementation.
- Unit tests cover no API change, API path change, stale SHA, malformed JSON, duplicate IDs, unresolved classification, dangling evidence, unknown impact change, privacy violations, and valid partial/complete reports.
- Workflow never executes provider-returned code or grants write permissions.
- Reports are reproducible from the same diff and input JSON.
- Missing external mapper results are visible as `analysis_required`, not silently treated as success.
