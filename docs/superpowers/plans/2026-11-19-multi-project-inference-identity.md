# Multi-project inference identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an additive project/task/inference/attempt identity contract to Integration Intelligence for parallel multi-project utilization.

**Architecture:** Extend the shared integration event envelope and project profile schema. Keep scheduling, provider adapters, accounting execution, and 3L0 scoring with their existing owners.

**Tech Stack:** JSON Schema Draft 2020-12, Python, pytest, jsonschema.

**Spec:** `docs/superpowers/specs/2026-11-19-multi-project-inference-identity-design.md`

## Global Constraints

- Keep the existing event `schema_version` at `1.0.0` and preserve legacy event validity.
- Require `project`, `task`, and `inference` on `inference.*` events.
- Require `portfolio_id` and `project_id` together on project profiles that declare either.
- Use stable `inference_id` across retries and unique `attempt_id` per execution attempt.
- Preserve unknown usage as null and preserve explicit measurement/attribution states.
- Reuse the existing Integration Intelligence event envelope and `3l0-intake/v1` mapping.
- Keep prompts, completions, raw tool payloads, secrets, and private transcripts outside telemetry records.

## Review Focus

- Legacy integration events retain their original validation verdict.
- Inference events reject missing project/task/inference identity and missing attempt identity.
- Activity-only and not-established usage reject numeric measurements and currency.
- Project profile IDs require a complete portfolio/project pair.
- Two projects can share a portfolio concurrency group while retaining distinct project queues.

---

### Task 1: Add the inference identity contract

**Files:**
- Modify: `docs/integrations/schemas/integration-event.schema.json`
- Modify: `ops/projects/profile.schema.json`
- Create: `tests/test_inference_execution_contract.py`
- Create: `docs/integrations/INFERENCE-IDENTITY.md`
- Modify: `docs/integrations/README.md`
- Modify: `docs/integrations/registry.json`
- Modify: `docs/integrations/INTEGRATION-REGISTRY.md`
- Modify: `docs/integrations/INTEGRATION-PORTFOLIO.md`
- Modify: `docs/proposals/active/integration-intelligence-superpowers/ITEMS.md`
- Modify: `docs/proposals/active/integration-intelligence-superpowers/MANIFEST.md`

**Interfaces:**
- Consumes: existing Integration Intelligence event envelope, Project Profile schema, and `3l0-intake/v1`.
- Produces: optional `project`, `task`, and `inference` event properties; inference-event conditional requirements; paired project-profile IDs; documented identity and mapping semantics.

- [ ] Write the failing contract tests in `tests/test_inference_execution_contract.py`.
- [ ] Run `python3 -m pytest tests/test_inference_execution_contract.py -q`; confirm the inference fields and paired project IDs fail against the current schemas.
- [ ] Extend the event schema with project, task, inference, usage, queue, concurrency, and priority properties; require the identity objects for `inference.*` events.
- [ ] Extend the project profile schema with paired optional `portfolio_id` and `project_id` fields.
- [ ] Run `python3 -m pytest tests/test_inference_execution_contract.py -q`; expect 9 passing tests.
- [ ] Document identity, retries, parallel queues, privacy, and 3L0 mapping in `docs/integrations/INFERENCE-IDENTITY.md`.
- [ ] Register Codex OTel and ChatGPT Desktop with discovered/planned states; align the human catalog and portfolio date.
- [ ] Link the contract from `docs/integrations/README.md` and register item `IIS-002`.
- [ ] Run `python3 -m pytest tests/test_inference_execution_contract.py -q`.
- [ ] Run `python3 scripts/proposals/validate_registry.py`.
- [ ] Run `python3 scripts/integrations/validate_portfolio.py`.
- [ ] Run `python3 scripts/ci/repo_gate.py`.
- [ ] Run `python3 scripts/ci/termux_smoke.py`.
- [ ] Commit with `Implements: IIS-002` in the commit context.
