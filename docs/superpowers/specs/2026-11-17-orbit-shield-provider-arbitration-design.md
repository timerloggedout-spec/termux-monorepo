# ORBIT × SHIELD — Provider-Neutral Cognitive Control Design

**Status:** implementation design; operator-directed 2026-11-17  
**Proposal:** continuous-capability-evolution-lab  
**Items:** CCEL-007, CCEL-008  
**Branch:** feat/orbit-shield-provider-arbitration-20261117

## Intent

Replace the narrow Gemini/OpenRouter/Jules mental model with a provider-neutral decision architecture over the repository's existing provider and endpoint population. Add two complementary mechanisms: SHIELD controls what enters an active task context; ORBIT evaluates eligible execution candidates and decides whether to select, defer, or veto. Both reuse existing registries, routing, context storage, DoE, and telemetry owners.

## Grounded current state

- The provider dispatch map records 110 providers across all lanes, 89 distinct model-lane providers, and a 7,341 provider×model endpoint floor in its 2026-11-01 census. These are census figures, not proof that every endpoint is callable today.
- The machine-readable dispatch catalog is `ops/challenge/desk-feed.json` → `dispatch.provider_catalog`; provider/quota records remain in `ops/quota/registry.json`.
- Native inference adapters are distributed across `llm_api_hub/server/research_providers.py`, `provider_extensions.py`, `provider_protocols.py`, `scripts/ops/provider_invoke.py`, the g4f working catalog, and existing catalog/dispatch workflows.
- `scripts/model_router.py`, `scripts/model_router_bootstrap.py`, and `.github/actions/model-router` already implement the runtime selection boundary and AR-18 capability-spine observe envelope.
- `scripts/capability_spine.py` is an existing pure, fail-closed candidate evaluator. `agent-context-store` and the context relationship graph already own durable task continuity and retrieval.

## Goals

1. Represent the complete provider/model population through existing authoritative registries and endpoint catalogs; do not create a competing provider registry.
2. Distinguish provider, provider/model inference endpoint, agent identity, execution adapter, and manager policy.
3. Classify each endpoint by evidence state: discovered, catalog-verified, adapter-registered, credential-present, authentication-verified, inference-verified, blocked, or unknown. A catalog row never implies a callable or healthy inference endpoint.
4. Implement ORBIT as two separately visible accumulators: expected task benefit and expected risk/total cost. Hard eligibility gates precede scoring. Return SELECT, DEFER, or VETO with reasons and provenance.
5. Implement SHIELD as a pure context-admission policy that creates a bounded task capsule and classifies incoming information as admit, quarantine, defer, or escalate.
6. Reuse existing routing, context-store, graph, quota, provider-invoke, DoE, and ATES contracts. Emit compact, secret-free observations.
7. Keep the first rollout observe-only: no provider invocation fan-out, production route changes, paid inference, credential changes, or branch-write authority.

## Non-goals

- No hardcoded three-provider universe or fixed provider hierarchy.
- No new provider/model source-of-truth registry, memory database, scheduler, queue, or telemetry ledger.
- No automatic probing of unconfigured credentialed providers.
- No assumption that all 89 model providers or 7,341 catalog pairs are currently callable.
- No use of agent confidence, public leaderboard rank, nominal price, or speed to override correctness, policy, security, quota, freshness, or provenance gates.
- No raw prompts, completions, secrets, cookies, session IDs, or unrestricted context payloads in telemetry or artifacts.
- No autonomous routing activation, execution fan-out, merge, deployment, or provider-account provisioning.

## Architecture

### Provider and endpoint population

Use the current dispatch feed, quota registry, provider adapter declarations, and live catalog observations as read-only inputs. The experiment unit is a provider×model endpoint identity, not a provider brand alone. Resolve callable transport only through reviewed adapters. Keep provider/model entries with no reviewed inference transport visible as catalog-only or inference-unproven; do not fabricate a URL or fall back to another provider. Credential presence, authentication, quota, catalog freshness, health, and a successful bounded inference are independent evidence fields.

Agent specialists (Jules, Gemini CLI, DeepSeek CI, CodeRabbit, Devin, etc.) remain a separate execution-participant class. They are not converted into model providers. ORBIT may compare a provider endpoint or an agent execution adapter only when its capability/effect contract and provenance are declared.

### SHIELD — context admission

Input: task objective, explicit constraints, source references, task state, permitted effects, current SHA when applicable, and context budget.

Output: a versioned, bounded capsule plus per-signal disposition:
- **admit** — directly relevant, trusted, within budget;
- **quarantine** — potentially relevant but untrusted, injected, conflicting, or not yet validated;
- **defer** — useful but non-urgent or outside the active task;
- **escalate** — a critical dependency, security event, or ambiguity requiring manager/operator attention.

Never admit secrets or session material. Preserve source references and hashes rather than copying whole unrelated histories. Do not create a new durable memory store; use existing context-store and relationship-graph mechanisms for persistence/retrieval. Missing context stays unknown.

### ORBIT — dual-accumulator arbitration

Input: SHIELD capsule and endpoint/specialist candidates.

For each candidate, apply hard gates first: capability fit, declared effect, trusted source/provenance, policy, credential/auth state, endpoint/adapter existence, catalog freshness, health, quota/cooldown, data classification, current-SHA binding where required, and execution authority.

For candidates that pass, compute and expose:
- **benefit accumulator:** task-relevant capability fit, validated repository outcome evidence, task-specific suitability, and expected integration contribution;
- **risk/cost accumulator:** uncertainty, failure/risk exposure, latency, quota/financial cost, context burden, retries, conflict potential, and human intervention.

No scalar score can compensate for a failed hard gate. Return:
- **SELECT** when hard gates pass and the benefit margin over risk/cost exceeds the configured, versioned threshold;
- **DEFER** when evidence, freshness, uncertainty, or margin is insufficient;
- **VETO** when a hard policy, security, authorization, provenance, or execution gate fails.

The decision includes eligible and excluded candidate counts, reasons, both accumulators, margin, policy version, endpoint identity, and evidence references. It must not expose secrets or provider payloads.

### Execution and evidence

The existing model router remains the sole provider/model selection and invocation boundary. This initial slice emits an observe-mode ORBIT recommendation and SHIELD capsule summary; it does not override the selected route. Actual execution and outcomes continue to be recorded through existing invocation receipts, routed-dispatch records, 3L0 intake, and ATES events. Missing evidence is null/unknown, never zero or success.

## Approaches considered

1. **Replace the router with a new central ORBIT service.** Rejected: duplicates routing authority, provider registry, scheduling, and telemetry.
2. **Hardcode an expanded list of ~100 providers into model_router.** Rejected: duplicates the canonical catalog and creates drift; provider count is not endpoint count or proof of inference.
3. **Extend the existing capability-spine observe contract with ORBIT and SHIELD pure decision helpers.** Selected: reuses the current router boundary, AR-18 contract, provider catalogs, and context-store ownership while allowing measured, reversible rollout.

## Acceptance criteria

- Strict tests prove hard-gate failures cannot be ranked or selected.
- Tests prove catalog-only/unconfigured endpoints remain visible but ineligible for invocation.
- Tests prove benefit and risk/cost accumulators are independently exposed and selection/defer/veto transitions are deterministic.
- Tests prove SHIELD denies secrets, quarantines untrusted instructions, bounds context, and preserves source references without copying unrelated content.
- Tests prove existing routing selection remains unchanged in observe mode.
- Existing capability-spine, model-router, provider-invoke, and context-store tests remain green.
- CI verifies proposal registry, repo gate, termux smoke, and targeted tests on the same PR head SHA.
- No production routing, credentials, provider account, paid inference, or durable memory-store changes.

## Implementation decisions left to the builder

Use stdlib-only pure Python helpers consistent with the existing capability spine; strict versioned JSON contracts; bounded candidate/capsule sizes; deterministic tests; and existing CI workflows. If current source data cannot establish an endpoint property, preserve it as unknown and exclude it from invocation eligibility.
