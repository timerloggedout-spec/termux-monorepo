# DoE-Governed Inference Allocation & Selection Contract

**Status:** architecture contract / implementation target  
**Owner:** DoE family  
**Effective clarification:** 2026-11-12  
**Related cohort:** `swarm-routing/v2` (routing-policy cohort identity; not a standalone JSON Schema)

## 1. Authority model

DoE is the sole owner of inference allocation and rotation: design, eligible population, treatment assignment, allocation proportions, endpoint-level statistical tests, stopping, culling and promotion. Rotation is not a global alternation or no-repeat constraint. The active design may repeat an endpoint or distribute traffic unevenly when that is what the registered experiment requires.

Scout is the execution selector. It chooses from the existing eligible provider/model endpoint pool to realize the DoE-assigned treatment. Its decision is constrained by task fit and live capability, credential, catalog, quota, safety and health evidence. Scout does not create the allocation policy or independently promote/cull endpoints.

Managers/requesters specify task requirements. A manager-specific endpoint/model/settings request is a customization request, not an implicit override. It becomes active only under an approved contract and is recorded as a distinct treatment/stratum. Owner and other explicitly authorized exempt roles are represented as exemptions, not silently mixed into ordinary participant constraints.

## 2. Endpoint identity and statistical claims

The unit of endpoint comparison is **provider + execution surface + exact model@version + protocol/endpoint identity**. Configured-instance identity remains separately keyed by the existing DoE `instance_key` tuple (provider, model, prompt hash, tools hash, role, moniker, context).

Every inference endpoint has its own evidence series and significance decision. Provider-family aggregates and pooled means may be reported as descriptive portfolio views, but cannot establish that an individual endpoint is statistically significant.

Before endpoint-level claims, the campaign design must register: primary outcome, null/alternative, test and assumptions, alpha, minimum practically important effect, planned sample/power or sequential boundary, stopping rule, confidence interval, and multiplicity correction across endpoints. Assignment integrity/SRM and task-family blocking must be checked. Until all applicable gates pass, endpoint standing is `NOT_ESTABLISHED`; n>=4 is descriptive only, not a significance threshold.

## 3. Request and contract economics

The standard path uses the active DoE allocation. A custom request must name the delta from the standard treatment (provider, model/version, endpoint, parameters, prompt/tools, topology, latency/SLA, data handling or other dimensions), the requesting manager/role, participant count, contract status and fee basis.

The contract's percentage schedule is explicit and versioned. A baseline representation is:

`effective_customization_pct(n) = base_customization_pct × (1 + participant_compound_rate_pct / 100)^(n - 1)`

The contract must define the denominator to which that percentage applies, the base rate, the participant compounding rate, the count, the resulting percentage, and the settlement/distribution destination. No numeric rate is inferred here. Owner/authorized exemptions are explicit and non-billable only when the contract or owner policy says so. Contracted participants form their own DoE stratum unless the design pre-registers another valid treatment model.

## 4. Canonical selection receipt

`docs/schemas/inference-selection-receipt.schema.json` defines `inference-selection-receipt/v1`. One receipt joins the DoE assignment to Scout's endpoint choice and the actual invocation. It carries:

- DoE campaign/design/version/allocation/stratum;
- task and selector identity;
- manager, request and requester role, plus explicit exemption;
- selected provider, surface, model@version, protocol and endpoint identity;
- eligible-pool snapshot reference and SHA-256;
- assignment method, arm, probability and endpoint test identity;
- optional approved custom contract and fee terms;
- workflow/run/attempt/request/trace/session correlation IDs;
- private-strategy visibility and commitment metadata (never plaintext strategy).

A selection receipt is not a substitute for the existing EXPERIMENT record or the downstream dispatch stamp. It is the canonical selection decision referenced by both. The invocation must verify that the chosen endpoint is the endpoint in the receipt; mismatches are a recorded deviation, not a silent rewrite.

## 5. Participant strategy privacy and lifecycle

Wallets, roles, bidding/ante methods, scripts, AST tactics and trading specifics are participant-owned strategy records. Active strategies remain private. Public evidence carries only a reference, cryptographic commitment, visibility state and release trigger. Plaintext private strategy and credentials must never be placed in this public repository or public feeds.

On cull, the strategy may move from `private_active` to `sealed_culled`; release occurs only when the recorded disclosure policy and authorization permit it. Cull records retain participant identity, wallet balance at cull, pool destination, strategy disposition and evidence lineage. A cull never erases history.

## 6. Runtime integration boundary (current evidence)

The current repository has these distinct components:

| Component | Observed responsibility | Gap |
|---|---|---|
| `scripts/scout_roster.py` | Builds a catalog-derived, observe-only provider/model roster | Not the production selector |
| `scripts/model_router.py` + `.github/actions/model-router` | Selects among role-specific configured candidates after capability/catalog/usage gates | Current candidate pool is a limited configured peer/residual set; no DoE assignment receipt is consumed |
| `scripts/ops/provider_invoke.py` + `.github/workflows/provider-invoke.yml` | Resolves provider endpoint/credentials and model catalog at invocation time; workflow_dispatch currently supplies provider directly | Direct provider input bypasses Scout/DoE assignment; generated stamp omits model, selection, manager/request and correlation fields |
| `llm_api_hub/server/app.py` | Executes caller-specified wrapper/OpenRouter/OpenAI/Anthropic model requests | It is an invocation gateway, not the DoE allocation authority |
| `scripts/dispatch/stamp_fanout.py` | Fans an already formed stamp into 3L0, DoE/MVT/ATES, MoneyBall and desk-feed records | Downstream evidence fan-out; cannot repair a missing selection decision |
| Tribute Desk | Read-only projection of feeds | Must display per-feed freshness and missing receipt state without synthesizing data |

## 7. Implementation sequence and acceptance gates

1. **Freeze the DoE design contract** — update `util-1-provider-rotation` so allocation/rotation authority is DoE, Scout is the bounded selector, endpoint is the comparison unit, and n>=4 remains descriptive only.
2. **Emit the receipt at selection time** — add a DoE assignment interface and Scout selection adapter; no provider invocation may occur without a valid receipt except explicitly marked exempt or observational legacy runs.
3. **Bind invocation to receipt** — pass the exact endpoint identity and receipt ID through `provider-invoke.yml`, `provider_invoke.py`, model-router action and/or llm_api_hub caller; reject endpoint mismatch.
4. **Fan out one canonical decision** — stamp receipt ID/hash and correlation IDs into EXPERIMENT, 3L0, MoneyBall and desk-feed records. Never infer missing fields.
5. **Add statistical validation** — endpoint-specific assignment integrity, SRM, power/sample/uncertainty, effect-size and multiplicity checks; no pooled significance substituted for endpoint significance.
6. **Add custom contracts** — versioned request delta, participant count, compounding percentage schedule, fee basis/distribution, exemptions and separate strata.
7. **Protect participant strategies** — private artifact store plus public commitment metadata; cull-triggered disclosure only under explicit policy.
8. **Add machine drift checks** — compare feed policy, DoE DESIGN, schema, runtime inputs and docs; fail when authority differs or stale no-repeat language reappears.
9. **Verify Tribute freshness** — per-source generated_at/observed_at, stale thresholds, last-success, and NOT_ESTABLISHED rendering per feed; never use one feed's timestamp as another's.
10. **Exercise end-to-end** — fixtures for valid assignment, repeat endpoint allowed, custom contract, exempt owner, unavailable endpoint reassignment, missing receipt, endpoint mismatch, duplicate correlation, underpowered endpoint and privacy leakage. Run repo tests and one bounded non-production invocation before enabling enforcement.

## 8. Explicit non-goals

- No global provider no-repeat rule.
- No fixed provider funnel or permanent provider rank.
- No statistical claim from provider-family pooling when endpoint-level evidence is required.
- No manager hard-pick without a contract.
- No plaintext private strategy, API credential or wallet secret in Git.
- No rewrite of historical dispatches as if they had been assigned by the new contract.


## 9. Tribute Desk freshness audit (verified 2026-11-12)

The page fetches feeds independently and each carries its own `generated_at`. The shared `CK.stampState` threshold is 24 hours. The audit found uneven presentation, corrected in this PR:

| Feed | Observed generated_at (UTC) | Before | After |
|---|---:|---|---|
| Main desk feed (`data/desk-feed.json`) | 2026-11-04T10:26:53Z | Raw timestamp only; no stale state | Explicit fresh/STALE/unknown |
| Dispatch state (`data/dispatch-state-feed.json`) | 2026-11-12T04:17:52Z | Per-feed `CK.stampState` | Retained |
| QUE queue-by-tier (`data/queue-by-tier.json`) | 2026-11-12T10:06:11Z | Per-feed stamp helper | Retained |
| QUE governor (`data/que-governor.json`) | 2026-11-12T10:06:11Z | Timestamp only | Explicit fresh/STALE/unknown |
| QUE priority windows (`data/que-priority-windows.json`) | 2026-11-12T10:06:11Z | No timestamp rendered | Explicit fresh/STALE/unknown |

The ops source and Tribute Desk mirror for the main desk feed are both updated to the corrected DoE policy in this PR. Their existing `generated_at` remains the source snapshot time; it is intentionally **not** falsified to make an old snapshot appear fresh. The page therefore marks the main desk feed STALE until its normal producer republishes it. Missing feed mirrors continue to render unavailable/not-yet-published, never zero or a timestamp borrowed from another feed.

Acceptance: every independently fetched feed displays its own generated timestamp and freshness state; a missing/invalid timestamp reads unknown; no feed borrows another feed's freshness.
