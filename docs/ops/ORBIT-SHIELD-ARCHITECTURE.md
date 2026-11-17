# ORBIT × SHIELD — provider dispatch and context control

**Status:** observe-only implementation on PR #5544  
**Proposal:** Continuous Capability Evolution Lab (CCEL-007, CCEL-008)  
**Runtime observation boundary:** `scripts/ops/provider_invoke.py`  
**Canonical population source:** `ops/challenge/desk-feed.json` → `dispatch.provider_catalog`

## Purpose and authority boundaries

ORBIT and SHIELD are complementary control policies over existing execution infrastructure:

- **ORBIT** evaluates provider-route candidates using hard eligibility gates followed by separate benefit and risk/cost accumulators. Its decisions are `SELECT`, `DEFER`, or `VETO`.
- **SHIELD** classifies task-context signals as `admit`, `quarantine`, `defer`, or `escalate`, while preserving provenance and enforcing bounded context budgets.
- Existing provider registries, adapter declarations, invocation scripts, context stores, relationship graphs, quota sources, DoE, and ATES remain authoritative. Neither control layer creates a parallel registry, memory store, scheduler, queue, or telemetry ledger.

The first integration is **observe-only**. It does not change the selected provider/model, prompt body, HTTP request count, retry behavior, output file, or invocation result. It does not fan out inference, provision credentials, spend quota, or activate production routing.

## Population facts — keep the denominators separate

The source-of-record dispatch feed and its human mirror distinguish several populations:

| Measure | Recorded value | Meaning |
|---|---:|---|
| Model-lane dispatch keys | 93 | Canonical dispatch class population |
| Invoke wiring | 92 / 93 | Provider keys with a recorded invoke surface; not a success rate |
| Provider × model endpoint floor | 7,341 | Aggregate endpoint census floor, counted at the 2026-11-01 census |
| G4F upstream providers | 160 | Separate G4F catalog population |
| G4F provider/model pairs | 9,588 | Separate G4F universe |
| G4F sandbox-verified pairs | 160 | Sandbox evidence, not Actions or production evidence |
| G4F Actions-verified pairs | 83 / 160 attempted | Actions-egress receipt evidence |

Additional source dimensions must not be silently substituted for these figures:

- The 95 inference-availability records resolve to 93 unique provider names.
- The 2026-11-01 quota-registry snapshot records 91 model records / 89 distinct model providers. That registry count is a different denominator from the 93-key dispatch class population.
- The G4F working catalog's 60 in-repo provider records and its composite adapter route are not the same population as the separate 160-provider / 9,588-pair G4F universe.
- Review and command providers (CodeRabbit, Qodo, Devin, peer-review orchestration) are not native inference endpoints merely because they participate in execution or review workflows.

The G4F Actions receipt identifies run `41457191473` and artifact `13154370032`. The run ended as cancelled after the receipt was written because probe threads held the interpreter open. Therefore 83 is the Actions-verified receipt count; it is **not** a claim that the enclosing workflow concluded successfully or that 83 endpoints are production-admitted.

## ORBIT population projection

Implementation: `scripts/orbit_provider_population.py`.

The projection reads the desk feed and optional `data/g4f-working/working-endpoints.json` evidence. It:

1. Deduplicates provider identities across availability records, the registry bench, and recorded route surfaces.
2. Retains the 92/93 wiring classification and the 7,341 aggregate endpoint floor as separate measures.
3. Preserves G4F universe, sandbox, and Actions evidence as distinct fields, including receipt run/artifact identifiers.
4. Emits provider-route candidates with unknown task-fit, authentication, health, quota, policy, and outcome evidence left null.
5. Performs no provider request, credential lookup, or inference.

**Important unit boundary:** the current ORBIT projection is a provider-route candidate projection. It does not materialize 7,341 individual provider/model candidate rows from an aggregate census floor. Pair-level arbitration requires source-backed per-model endpoint identities and their own route, freshness, credential, authentication, quota, and inference evidence. Provider names and aggregate endpoint counts must never be expanded into fabricated model rows.

A registered G4F adapter route remains visibly distinct from a native provider API route. G4F upstream catalog membership, sandbox success, Actions receipt success, and production admission are separate states.

## ORBIT decision contract

Implementation: `scripts/orbit_arbitration.py`.

- Hard gates run before scoring. A failed hard gate produces `VETO`; unknown required evidence produces `DEFER`.
- Benefit factors and risk/cost factors are separately emitted.
- Missing factors remain null; they are not coerced to zero.
- Duplicate identities are vetoed.
- A truncated candidate population defers the overall decision.
- A tie at the top defers instead of selecting arbitrarily.
- No score can override policy, provenance, credential/authentication, endpoint, quota, health, data-classification, current-SHA, or execution-authority gates.

With the current population projection, the expected result is `DEFER`: the catalog establishes candidate identity and some route wiring, but not task-specific capability, current credentials, authentication, health, quota, execution authority, or measured outcome.

## SHIELD context contract

Implementation: `scripts/shield_context.py`.

- Context is bounded by item and character budgets.
- Source references and content hashes are retained; raw untrusted signal content is not returned in quarantine records.
- Secret-bearing fields and token/credential patterns are quarantined.
- Instruction-override patterns are quarantined even when a source is otherwise marked trusted.
- Critical security/operational signals escalate.
- Missing trust, provenance, relevance, or content does not become admission.

At the provider-invoke boundary, the prompt is supplied to SHIELD as an untrusted signal until an authoritative trust assertion exists. The observe-only integration records disposition, character count, and content hash only. It does **not** replace, redact, rewrite, or block the prompt sent by the existing invocation path; enforcement is a separate future promotion decision.

## Provider-invoke integration

Implementation: `scripts/ops/provider_invoke.py`; contract tests: `tests/test_provider_invoke_control_plane.py`.

Both `INVOKE_VERDICT` and `CATALOG_VERDICT` can carry a compact `control_plane` observation containing:

- population counts and evidence grades;
- ORBIT decision, reason, candidate counts, and policy version;
- SHIELD dispositions, counts, budget, source reference, content hash, and character count.

The observation excludes prompt content, credential values, completion content, provider payloads, and session identifiers. Control-plane observation failures are reported as unavailable and do not abort the existing invocation path.

## Validation and promotion

Focused suites:

```bash
python3 -B -m unittest discover -s tests -p 'test_shield_context.py' -v
python3 -B -m unittest discover -s tests -p 'test_orbit_arbitration.py' -v
python3 -B -m unittest discover -s tests -p 'test_orbit_provider_population.py' -v
python3 -B -m unittest discover -s tests -p 'test_provider_invoke_control_plane.py' -v
```

The Termux smoke workflow runs these focused contracts plus the repository's existing smoke suite. Repository gate, proposal lifecycle, PR scope, and other dual-gate checks remain independent. Only terminal results on the exact current PR head count as validation.

Promotion is not implied by a successful test suite. It requires same-head validation, independent review, and explicit authorization. No merge, route activation, provider fan-out, paid inference, or credential mutation is part of this change.
