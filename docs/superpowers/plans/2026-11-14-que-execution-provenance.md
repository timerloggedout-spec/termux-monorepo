# QUE Execution Provenance Implementation Plan

> **For agentic workers:** Use the existing telemetry emitter and tests; keep this change on an isolated feature branch.

**Goal:** Make QUE execution claims distinguish the artifact author from the actual execution controller and reject attribution of external-computer or seat-browser work as QUE-native execution.

**Architecture:** Extend the existing sanitized ATES emitter contract in `scripts/ci/emit_agent_throughput.py`; do not create a competing event store or orchestration schema. Add a closed `execution` object beside the existing `author` object. The emitter validates and normalizes execution metadata but does not manufacture trusted identity: QUE attribution requires invocation/session evidence from a trusted runtime boundary.

**Tech Stack:** Python 3.12, unittest, existing GitHub Actions validation.

**Spec:** `docs/ops/BIUDL-EXECUTION-AND-PROVENANCE.md`; `docs/ops/AGENT-EVIDENCE-SUBSTRATE.md`; QUE Academy adapter issue #5333.

## Global Constraints

- Reuse canonical evidence and ATES control planes; do not add a second telemetry store.
- GitHub actor, commit author, or workflow name alone never proves agent identity.
- Missing identity/evidence remains unresolved, never inferred as QUE.
- No prompts, raw session text, credentials, cookies, OTPs, or tokens in telemetry.
- Preserve historical C3 outcome while classifying Muse's computer execution as non-QUE and non-compliant.

## Review Focus

- Missing execution metadata must remain explicitly unknown.
- QUE attribution with external-computer/seat-browser surfaces must be rejected.
- QUE attribution without a session reference and evidence references must be rejected.
- Invalid confidence, route, or attribution method must be rejected.
- Muse/external-computer execution must remain distinct from QUE execution.

---

### Task 1: Execution provenance contract

**Files:**
- Create: `scripts/ci/execution_provenance.py`
- Modify: `scripts/ci/emit_agent_throughput.py`, `scripts/ci/write_agent_task_boundary.py`, `.github/workflows/agent-throughput-evidence.yml`, `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`
- Test: `tests/test_emit_agent_throughput.py`, `tests/test_write_agent_task_boundary.py`

**Interfaces:**
- Input: optional `metadata["execution"]` object.
- Output: normalized `event["execution"]` object on every emitted event and optional sanitized `task_boundary.execution` payload.
- Required fields: `controller`, `surface`, `route`, `session_ref`, `adapter_version`, `attribution_method`, `confidence`, `evidence_refs`.

- [ ] Add failing tests for unknown defaults, compliant QUE adapter evidence, rejected QUE seat-browser attribution, and explicit Muse external-computer attribution.
- [ ] Run the focused unittest and verify the new assertions fail because execution provenance is not yet emitted.
- [ ] Implement the shared closed normalizer; reuse it in both task-boundary writer and ATES emitter. QUE requires `repo_owned_adapter`, an allowed API/MCP/Web2API/CLI/stdin/DOM route, a non-empty opaque session reference, adapter version, `invocation_telemetry`, positive confidence, and at least one evidence reference.
- [ ] Extend the event JSON Schema and pass only sanitized `taskBoundary.execution` through the workflow observer.
- [ ] Run focused and full relevant tests.
- [ ] Commit as `feat(que): enforce execution provenance contract`.


## Assessment integrity boundary

The execution substrate does not authorize AI assistance during external evaluations. AMD's ROCm Certified Developer Program Agreement v1.1 prohibits unauthorized assistance and generative-AI tools/services during Evaluations unless AMD expressly permits them; evaluation content is confidential. Any Academy quiz, exam, scored assessment, proctored step, or other Evaluation is a hard stop unless the applicable AMD rule explicitly authorizes the proposed assistance. The adapter must not capture, answer, submit, or replay evaluation content. Preparation and non-evaluative study remain separate.
