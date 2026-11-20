# CNS-06 — Candidate QUE/Brain JSONL bridge

Status: design candidate for QUE owner review. This document defines a reviewable proposal; it does not register a canonical runtime contract.

## Purpose

Connect the provider-neutral Brain kernel to the existing QUE model-assessment seam through a bounded JSONL process boundary. Keep deterministic QUE admission authoritative and run Brain in shadow mode until the QUE owner accepts the interface and fresh Delphi admission is recorded.

## Host ownership

| Plane | Existing owner | Contract |
|---|---|---|
| Issue-form admission | .github/workflows/swarm-admission.yml and scripts/ops/swarm_admission.py | Tier → after → chain → flow; emits swarm-admitted or deferred-by-tier; template-declared route owns execution. |
| Model assessment candidate | docs/proposals/active/que-superagent/LESSONS.md, QSA-P2 | Planned model layer runs only on inferred candidates and judges enabled rules once. |
| QDesk self-repair | .github/workflows/qdesk-self-repair.yml and scripts/que/self_repair.py | Separate scheduled host for failing workflows and stale feeds; preserves its own issue intake and promotion rules. |
| Capability authorization | hub_mcp/policy.py | Named capability policy for local execution. |
| Brain reasoning | brain.rs and brain/ | Provider-neutral typed reasoning; no tool execution or memory persistence. |
| Specialist | archwiz/mosaic_brain/ | methodology_intelligence evaluation through BrainExtension. |
| Receipt | docs/ops/ORCHESTRATION-RECEIPT.schema.json | Canonical orchestration receipt. |

## Candidate wire protocol

- Transport: one UTF-8 JSON object per stdin line; one UTF-8 JSON object per stdout line.
- Diagnostics: stderr only.
- Version: explicit schema field on every request and response.
- Identity: orchestration_id, cycle_id, and attempt_id are required and echoed unchanged.
- Execution: one request per process invocation in the first version; host controls timeout and retry.
- Policy: the QUE host supplies its deterministic admission result and policy version. Brain treats this as context and returns an advisory assessment.
- Authority: the host retains the final admission, routing, dispatch, and promotion decision.
- Failure: malformed input, unsupported schema, identity mismatch, timeout, or process failure produces a host-owned error receipt and preserves the existing QUE decision.

### Request candidate

```json
{
  "schema": "termux-monorepo.brain-host-request/v1",
  "identity": {
    "orchestration_id": "orch-...",
    "cycle_id": "cycle-...",
    "attempt_id": "attempt-..."
  },
  "task": {
    "goal": "Evaluate the declared methodology-intelligence task",
    "mode": "standard",
    "domain_id": "methodology_intelligence",
    "context_budget_tokens": 8192
  },
  "context": [
    {
      "id": "source-...",
      "source_ref": "https://github.com/...",
      "content": "Owner-approved, bounded context",
      "relevance_bps": 9500,
      "estimated_tokens": 128,
      "classification": "internal",
      "evidence": "verified"
    }
  ],
  "admission": {
    "policy_version": "dispatch-tiers/v2@...",
    "strength": "inferred",
    "deterministic_status": "swarm-admitted",
    "tier": 3
  },
  "host": {
    "repository": "timerloggedout-spec/termux-monorepo",
    "commit_sha": "..."
  }
}
```

### Response candidate

```json
{
  "schema": "termux-monorepo.brain-host-response/v1",
  "identity": {
    "orchestration_id": "orch-...",
    "cycle_id": "cycle-...",
    "attempt_id": "attempt-..."
  },
  "run_status": "completed",
  "decision": {
    "status": "ready",
    "reason": "Advisory reasoning completed",
    "evidence_refs": ["source-..."]
  },
  "specialist": {
    "extension_id": "org.termux.mosaic.methodology",
    "domain_id": "methodology_intelligence",
    "contract_version": "termux-monorepo.brain-extension.v1",
    "outcome": "promotion_candidate",
    "evidence_refs": ["experiment:..."]
  },
  "receipt": {
    "schema": "orchestration-receipt/v1",
    "host_run_id": "...",
    "source_commit": "...",
    "evidence_refs": ["source-...", "experiment:..."]
  }
}
```

The field names and enum spellings above are a candidate mapping. The QUE owner must reconcile them with the current Brain Rust types, MOSAIC response types, and canonical receipt schema before implementation.

## Shadow semantics

1. Run the existing deterministic QUE admission evaluator first.
2. Invoke the Brain assessment only for an owner-approved inferred-candidate class.
3. Invoke MOSAIC only when the host supplies the explicit methodology_intelligence domain and the injected PolicyGate returns Ready.
4. Persist the Brain result as an advisory shadow receipt.
5. Keep the original QUE admission stamp, issue labels, template route, dispatch state, and promotion decision authoritative.
6. Compare Brain advice with the existing deterministic/owner outcome; preserve disagreements as evidence for review.

## Contract tests required before host wiring

- Request and response schema version validation.
- Round-trip preservation of orchestration_id, cycle_id, and attempt_id.
- Unknown schema and malformed JSON fail closed with an attributable error receipt.
- Identity mismatch blocks specialist invocation.
- NeedsApproval, Blocked, NeedEvidence, and NeedsReview prevent specialist handoff.
- Ready plus explicit methodology_intelligence routes through the typed MOSAIC extension.
- Brain output leaves the deterministic QUE admission result unchanged.
- Receipt validates against ORCHESTRATION-RECEIPT.schema.json.
- Duplicate request identity is idempotent at the host boundary.
- Timeout and process failure preserve the host's existing admission result.

## Approval and activation gates

- QUE owner confirms the QSA-P2 model-assessment seam and accepts the request/response mapping.
- The owner of qdesk.brain-rs confirms the process and lifecycle contract.
- RFP #5501 receives a fresh Delphi admission; its current filing_grants_execution value remains false.
- Host policy, revocation, timeout, retry, and receipt behavior pass integration tests.
- The first production route remains bounded, read-only, and advisory until separately authorized for execution.

## Source precedent

The Context Relationship Rust accelerator uses JSONL over stdin/stdout while Python retains collection, privacy, schema, and publication authority. This bridge candidate follows that separation and keeps the Brain binary replaceable behind the existing QUE host.
