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
