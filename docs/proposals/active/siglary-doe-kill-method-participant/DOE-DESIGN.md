# DoE pre-registration — kill-method participant contract

**Campaign candidate:** `kill-method-contract-1`  
**Status:** design-only / not admitted / not executed  
**Owner:** DoE family (review required)  
**Parent:** RFP #5514 · draft PR #5517

## Question

Do independently versioned participant/method/schema identity, exact target binding, and deny-by-default dry-run policy reduce unsafe or ambiguous method descriptors without creating a parallel execution authority?

## Scope

Synthetic contract validation only. No workflow cancellation, process signal, participant cull, feature-flag mutation, or production action is executed. Existing mechanisms are source references and method-family examples, not treatment execution.

## Design

A bounded (2^4) factorial over four binary contract safeguards:

| Factor | Off (synthetic negative control) | On (candidate treatment) |
|---|---|---|
| A — version identity | participant/method/schema version omitted or conflated | all three version axes explicit |
| B — target binding | broad/wildcard selector | exact target identity; max_targets = 1 |
| C — authority | implicit/unspecified authority | default deny + explicit approval required |
| D — execution posture | execution-capable descriptor | observe/dry-run only; execution disabled |

All 16 cells are generated as synthetic descriptors and evaluated by a validator. Unsafe cells are never dispatched to a runtime. The all-on cell is the candidate contract; the all-off cell is the negative control. Intermediate cells identify which safeguard catches which failure class.

## Blocks / method families

Block by method family so method-specific semantics are not pooled as if identical:

1. Queue cancellation — queued workflow run only; `in_progress` explicitly forbidden.
2. Worker fault injection — disposable development/test worker only; Temporal kill/resume harness is the reference.
3. DoE participant cull — population lifecycle transition, not process termination; where the agentic-gambling domain applies, cull consequence stays in the same record.
4. Feature-flag control — exact named flag only; no broad configuration mutation.

No family is treated as a synonym for another.

## Outcomes

**Primary**
- unsafe descriptor acceptance rate (must be zero for the all-on treatment);
- ambiguous/unversioned descriptor acceptance rate (must be zero);
- exact-target enforcement rate;
- policy-denial correctness.

**Secondary**
- valid-descriptor false rejection rate;
- evidence/provenance completeness;
- method-family mapping correctness;
- validator latency and schema size.

No quality or production-reliability claim is made from synthetic fixture results.

## Cohort and assignment

- Fixed synthetic fixture cohort, versioned and hash-pinned.
- Full factorial: 16 safeguard combinations per method-family block.
- Deterministic assignment; no model/provider calls.
- Each generated validation run emits exactly one canonical DoE experiment record at `docs/ops/corpus/EXPERIMENT.schema.json` if/when the campaign is admitted and executed.
- Preserve configured-instance identity if any model-assisted evaluator is later introduced; model@version alone is insufficient.

## Stopping / promotion

- Immediate stop on any all-on unsafe acceptance, target widening, unknown-version fallback, or evidence omission.
- Do not infer statistical significance from deterministic exhaustive fixtures.
- Promote only after all-on zero-unsafe-acceptance, acceptable false-rejection rate, clean repository gates, independent review, and owner approval.
- A successful validator test is not authority to execute the represented method.

## Admission status

This document is a pre-registration candidate only. Per `docs/ops/DOE-FAMILY.md`, a proposal alone does not admit a campaign: a committed design record **and run evidence** are required. No DoE result is claimed until those records exist and validate.
