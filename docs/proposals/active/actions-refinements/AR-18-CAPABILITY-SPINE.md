# AR-18 — Capability–Scope–Specialist Decision Spine

**Status:** Observe-mode implementation.

This record governs the first, reversible phase of the Evolutionary Capability Spine. It introduces a shared decision vocabulary and a secret-free recommendation envelope; it does not invoke a provider, create a branch, alter a provider configuration, or relax an existing writer boundary.

> **Decision rule:** A candidate must pass capability, effect, provenance, policy, availability, quota/cooldown, and current-SHA gates before it can be ranked. A score cannot compensate for a failed gate.

## Relationship register and collection limits

The register was refreshed against `origin/master` at `8648fa72af57acad6afee84c8b67cc842171990f` on 2026-08-22. Issue #192 was open at that point. The generated context graph was not used as current-lineage authority because its recorded ref is `master-staging`, its historical collection ends after page 1, and it reports 14 parser failures. The trusted reconciliation workflow also writes only to `master-staging`; AR-18 therefore records that limit rather than triggering a non-current direct writer.

| Root | Relationship class | Role in AR-18 | Evidence / boundary |
|---|---|---|---|
| Issue #192 | Verified governing root | Owns AR-18 and its review/merge path. | `ITEMS.md`, `MANIFEST.md`, and `ACTION-DECISION-LEDGER.md`. |
| Issue #175 | Verified historical context | OPERATOR priority context, not implementation authority. | Proposal-local `source.md`. |
| `scripts/model_router.py` | Verified source root | Emits observe-mode candidate recommendation while preserving the existing execution selection. | Router tests and local action contract. |
| `.github/actions/model-router/action.yml` | Verified source root | Exposes the bounded decision envelope and one-line summary. | No new permission, secret, or provider call. |
| `gemini-dispatch.yml` | Verified classifier root | Continues to classify/defer events; downstream reusable workflows report the shared decision. | It is not converted into a privileged central dispatcher. |
| `gemini-triage.yml`, `gemini-review.yml`, `gemini-invoke.yml`, `gemini-after-peers.yml` | Verified routing consumers | Publish observe summaries without changing selected provider/model execution. | Existing router outputs remain authoritative during observation. |
| `peer-review-orchestrator.yml` | Verified peer-evidence root | Retains CodeRabbit default, Qodo/Devin opt-ins, cooldown, coalescing, and current-SHA completion rules. | No peer policy change in AR-18. |
| `.github/agentic/provider-command-library.json` and `provider-command-dispatch.yml` | Verified command-authority roots | Declare provider actions and explicit branch-write confirmation. | No free-form command or review-reference composition is added. |
| `agent-review-auto-jules.yml` | Verified implementation-specialist root | Records why review feedback is relayed to Jules when no separately confirmed native provider action exists. | Provider-native branch writes remain impossible to infer from feedback text. |
| Dependency phase evaluator | Verified coordination-evidence root | Future local performance evidence source for readiness and async coordination. | Derived status does not authorize implementation. |
| PR #276, B3, B4/AR-04, B5/A-14 | Explicit hold roots | Regression and scope boundaries. | AR-18 neither retries B3 nor grants writer/dispatch authority. |

## Candidate contract

The AR-18 decision envelope is deliberately bounded and contains only structured routing facts.

| Field group | Included | Excluded |
|---|---|---|
| Identity | Capability, provider/model specialist, declared source. | Tokens, secrets, browser/session data. |
| Eligibility | Availability state, quota headroom, trusted declaration, hard exclusion reason. | Issue, PR, and provider-review bodies. |
| Performance | Historic 3L0 prior, repository-evidence confidence, neutral public-feature prior, component weights. | Fabricated sample counts or unverified benchmark claims. |
| Decision | Observe state, recommendation, runner-up, one-line summary. | Provider command fragments and branch-write instructions. |

The initial scoring policy gives repository-local outcomes 55% influence, evidence confidence/recency 15%, public leaderboard features 15%, and operational availability/headroom 15%. The current 3L0 matrix is treated as a low-confidence historic prior until controlled repository outcome samples are collected. Public leaderboard information remains a feature, not authority.

## Paper2Agent transfer: extend the existing spine; do not create a second registry

The September 2026 Paper2Agent result is useful here as a capability-discovery and validation pattern, not as a reason to introduce a parallel knowledge-agent registry. The repository already has the correct architectural center: Capability–Scope–Specialist.

The canonical query is:

> Who has the validated capability to perform X under Y constraints with Z evidence?

The answer is a join across existing dynamic sources, not a fixed provider/model list.

Capability identity is therefore a tuple:

capability × scope × task × constraints × specialist × tools/connectors × environment × authority × evidence

Provider and model remain important identity dimensions, but they are only two axes of the candidate population.

### Multiple dynamic matrices

These are projections over existing sources, not independent competing SSOTs:

| Matrix | Rows × columns | Purpose | Existing evidence/source |
|---|---|---|---|
| Capability × Specialist | capability × provider/model/agent | Who can perform the requested role? | llm-peers.yaml, live provider catalog, model-success matrix, agent/integration inventory |
| Capability × Tool/Connector | capability × tool/connector/plugin/MCP surface | What execution/tooling is actually required? | connector manifests, MCP/tool inventories, provider command library, skills inventory |
| Capability × Scope/Authority | capability × effect/authority | What may the candidate do in this scope? | routing policy, command library, writer confirmation, policy gates |
| Capability × Evidence | capability × evidence class/freshness/confidence | What proves the capability is usable now? | workflow runs, task probes, telemetry, validation receipts, provenance |
| Task × Constraint × Specialist | task × constraints × candidate | Which candidate fits this exact job shape? | live catalog + policy + environment + quota/cooldown + current-SHA evidence |
| Manager × Cohort × Sequence | manager policy × candidate cohort × orchestration sequence | Which team composition and coordination policy works? | continuous evaluation, ATES/WTCV/3L0, integrated outcome evidence |

These matrices are intentionally dynamic and multi-dimensional. A candidate can be present in one projection and absent from another because availability, authority, tooling, evidence, or task constraints differ.

### Candidate population: discover, do not enumerate

Do not reduce the population to Gemini / Jules / OpenRouter / DeepSeek. Those names are examples of existing integration/provider/model surfaces, not the roster.

The live population already spans dynamically discovered provider/model catalog entries; Felo/OX Alpha observations; OpenRouter models including newly listed free/zero-price models; OmniRoute aggregation; Gemini model lanes; Jules as an asynchronous implementation specialist; CodeRabbit, Devin, Qodo, Copilot and other review/implementation surfaces where their declared actions and evidence contracts permit; MCP/tool/connector capabilities; repository-local skills and deterministic tools; and future explicitly approved providers and models.

The population must grow or shrink from observed catalogs and declared integration surfaces. Bootstrap priors are not the complete roster.

### Capability admission remains evidence-first

Paper2Agent's reproduce/test/diagnose/repair loop maps onto the existing admission discipline:

DISCOVERED → DECLARED → AVAILABLE → TOOL-BOUND → PROBED → VALIDATED → ADMITTED

Authority remains a separate state:

OBSERVE → READ/QUERY → ANALYZE/REPRODUCE → PROPOSE → PREPARE → SANDBOX WRITE → REPOSITORY WRITE → PROMOTE

Validation of a capability does not grant repository-write or merge authority.

The evidence record should distinguish documented capability; declared connector/tool/plugin availability; authenticated credential presence; live catalog/request evidence; task-probe execution; correctness/result evidence; current-SHA binding; provenance and attribution confidence; quota/cooldown state; and authority/policy state.

A provider 429, 403, timeout, missing credential, or unavailable connector is an admission/provider observation, not a model-quality failure.

### Capability query envelope

The existing AR-18 decision envelope can answer the canonical query without inventing a new capsule type:

~~~yaml
query:
  capability: review
  task: <bounded task shape>
  scope: <repository|pr|issue|workspace|sandbox>
  constraints:
    - current_sha_required
    - read_only
    - max_latency
    - quota_class
  evidence_required:
    - runtime_validation
    - provenance
    - current_sha
  required_tools:
    - <tool-or-connector>
decision:
  candidates: []
  recommendation: null
  exclusions: []
  evidence_refs: []
~~~

This is a query/projection over the existing capability spine. It must not become a second source of truth.

### Source-of-truth boundaries

AR-18 should consume and correlate, rather than duplicate:

1. Provider/model identity and live access: provider catalog + llm-peers.yaml.
2. Declared capabilities/roles: routing policy + model-success matrix + specialist/integration declarations.
3. Tools/connectors/MCP surfaces: existing connector manifests, tool inventories, skills, and provider command library.
4. Execution evidence: workflow run/job/step/artifact telemetry and task outcomes.
5. Attribution/provenance: existing provenance and context-relationship evidence.
6. Authority: existing command/action contracts and explicit write confirmation.
7. Team outcome: ATES/WTCV/3L0 and integrated acceptance evidence.

No new KAC/agent registry is required for this research transfer.

### P1a — dynamic catalog population adapter (observe-only)

The first implementation increment is now in place without changing execution routing.

- `scripts/model_router.py` keeps the legacy execution roster untouched.
- AR-18 observe mode now appends every currently observed free OpenRouter catalog model to the candidate population.
- A live catalog observation does **not** create a capability declaration.
- A discovered model absent from the role declaration/success matrix is emitted as `unvalidated` and fails the capability gate.
- Candidate output records `validation_status`; population metrics distinguish unvalidated, historic-prior-only, and explicitly validated observations.
- The observe population bound is 64 candidates so the envelope remains bounded while avoiding the old single-digit provider/model illustration.
- Existing provider/model execution selection remains unchanged.

This establishes the required distinction:

`DISCOVERED ≠ DECLARED ≠ VALIDATED ≠ ELIGIBLE`

The next adapter increment should generalize the same normalized population contract to the existing Felo/Omni/provider-catalog artifact rather than introducing another registry.

### Current implementation gap

AR-18 is intentionally observe-only, but its current candidate construction is narrower than the desired dynamic population: model_router.py has bootstrap role lists while the live OpenRouter catalog is already dynamic. That is useful evidence, not a reason to hard-code more names.

The next implementation increment should broaden the existing candidate adapter to consume normalized catalog, integration, tool, and evidence dimensions and emit the same AR-18 envelope. It should not replace the router, create a new registry, or make active-routing changes.

## Specialist-disposition contract

The current feedback relay assigns `independent_implementation_specialist` when trusted substantive provider feedback reaches the Jules lane. This does not assert that CodeRabbit cannot repair its own findings. It records the actual authority condition: the current event does not include a command-library action, a live-SHA dispatch receipt, or the required explicit `confirm_branch_write=true` input. Therefore a native CodeRabbit branch write is not eligible to be inferred from review feedback.

A later native-remediation activation may proceed only when its action exists in the trusted default-branch command library, its target PR and head SHA are validated, it is idempotent, and branch effects retain the existing explicit confirmation. Qodo/Devin review text remains evidence; arbitrary review content and URLs never become CodeRabbit command syntax.

## Rollout and rollback

AR-18 is **observe mode only**. The `capability-spine-observe` action input defaults to `true`; setting it to `false` removes the shadow decision while leaving the existing router selection unchanged. An active-routing promotion requires two bounded observation cycles, measured repository outcomes, deterministic regression tests, and a new ledger decision.

## References

- [Issue #192](https://github.com/timerloggedout-spec/termux-monorepo/issues/192)
- [Issue #175](https://github.com/timerloggedout-spec/termux-monorepo/issues/175)
- [Issue #192 decision ledger](ACTION-DECISION-LEDGER.md)
- [Model routing policy](../../../schemas/routing-priority.yaml)
- [Provider command library](../../../../.github/agentic/provider-command-library.json)
- [Automation decision tree](../../../ops/automation-decision-tree.md)
