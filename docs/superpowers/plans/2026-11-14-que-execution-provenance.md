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
- Modify: `scripts/ci/emit_agent_throughput.py`
- Test: `tests/test_emit_agent_throughput.py`

**Interfaces:**
- Input: optional `metadata["execution"]` object.
- Output: normalized `event["execution"]` object on every emitted event.
- Required fields: `controller`, `surface`, `route`, `session_ref`, `adapter_version`, `attribution_method`, `confidence`, `evidence_refs`.

- [ ] Add failing tests for unknown defaults, compliant QUE adapter evidence, rejected QUE seat-browser attribution, and explicit Muse external-computer attribution.
- [ ] Run the focused unittest and verify the new assertions fail because execution provenance is not yet emitted.
- [ ] Implement a closed normalizer and event validator. QUE requires `repo_owned_adapter`, an allowed API/MCP/Web2API/CLI/stdin/DOM route, a non-empty opaque session reference, adapter version, positive confidence, and at least one evidence reference. QUE cannot use `seat_browser`, `external_computer`, or `manual`.
- [ ] Run focused and full relevant tests.
- [ ] Commit as `feat(que): enforce execution provenance contract`.
