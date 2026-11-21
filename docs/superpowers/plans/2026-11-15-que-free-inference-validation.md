# QUE Free Inference Validation Implementation Plan

> **For agentic workers:** Execute this plan task-by-task with the available GitHub branch and CI workflow. Steps use checkbox syntax for tracking.

**Goal:** Make the existing provider invoke path capable of selecting only verified no-cost chat models, while ensuring a missing provider quota counter does not disqualify a separately verified daily-pool arm, and make catalog-only availability evidence explicitly say inference was not attempted.

**Architecture:** Reuse the canonical provider model catalog and existing provider invoke route. Add a small pure selector for no-cost models; do not add another provider registry, quota ledger, poller, scheduler, or router. Keep quota/pool eligibility independent from model pricing and preserve the existing boolean field for compatibility while adding an explicit inference status.

**Tech Stack:** Python 3, pytest, GitHub Actions.

**Spec:** GitHub issue #5454 — QUE full inference-arm validation and activation.

## Global Constraints
- Every configured inference arm must be validated; no quota counter is a universal admission prerequisite.
- Daily-pool/no-provider-quota is distinct from quota-backed, unknown, and exhausted.
- No paid fallback or paid spend in the free-only path.
- Never label an arm ACTIVE without current inference evidence.
- Never expose provider credentials or response bodies in persisted evidence.
- Reuse existing canonical registries and invocation paths.

## Review Focus
- A model whose pricing is unknown must never be selected by free-only mode.
- A free suffix must not accidentally authorize a non-chat model.
- A free-trial model with unverified account entitlement must not be treated as free.
- A daily-pool/no-provider-quota arm with no provider quota counter must remain selectable when its model is independently verified no-cost.
- Catalog success must never be reported as successful inference.

---

### Task 1: Free-only model selection contract

**Files:**
- Create: tests/test_provider_invoke_free_only.py
- Modify: scripts/ops/provider_invoke.py

**Interfaces:**
- Produces: select_free_chat_model(models: list[dict], requested_model: str | None = None) -> str | None
- Consumes: provider_model_catalog.poll(provider, token), existing NON_CHAT_HINTS.

- [ ] Write tests for verified zero-price, free-suffix, verified free-trial, paid/unknown, non-chat, exact-model selection, and daily-pool/no-provider-quota without provider quota counters.
- [ ] Verify the tests fail because select_free_chat_model is not implemented.
- [ ] Implement the pure selector and add --free-only to the existing invocation CLI.
- [ ] In free-only mode, fail closed when no canonical catalog exists, no verified no-cost chat model exists, or an explicitly requested model is not verified no-cost. Never fall back to "default", paid, or unknown pricing.
- [ ] Limit free-only mode to one completion request per selected model; retain existing non-free behavior for callers that do not opt into free-only mode.
- [ ] Run the focused tests and full relevant provider test suite.

### Task 2: Accurate scheduled availability semantics

**Files:**
- Modify: scripts/provider_availability_probe.py
- Modify: tests/test_provider_availability_probe.py

**Interfaces:**
- Adds inference_status with values not_attempted, passed, failed.
- Retains inference_ok boolean for backward compatibility.

- [ ] Add tests asserting catalog-only scheduled observations are not_attempted, not failed.
- [ ] Verify the tests fail before implementation.
- [ ] Populate inference_status from an actual invocation observation only when inference_attempted is true.
- [ ] Keep Gemini and scheduled OpenRouter probes as not_attempted; update the output semantics and console summary.
- [ ] Run focused and full provider tests.

### Task 3: Workflow integration

**Files:**
- Modify: .github/workflows/provider-invoke.yml
- Modify: tests/test_provider_invoke_free_only.py

- [ ] Add a free_only boolean workflow input defaulting to true.
- [ ] Pass --free-only by default for invocation runs; catalog mode remains catalog-only.
- [ ] Test the workflow default and CLI argument wiring.
- [ ] Open a PR and use its CI results as the authoritative verification because this session has no Termux device shell or repository checkout.
