# ITEMS — continuous-capability-evolution-lab

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| CCEL-001 | P1 | executing | Establish CEEL architecture, boundaries, participant families, and source-of-truth map. | CLAUDE entry points to the design; CEEL reuses Integration Intelligence, DoE, ATES, Delphi and proposal authorities; no parallel control plane. |
| CCEL-002 | P1 | executing | Define capability opportunity graph, strict JSON Schema, seed inventory and deterministic validator. | Graph parses; node IDs unique; edge endpoints resolve; lifecycle/provenance states explicit; tests cover valid, duplicate, unresolved and malformed cases. |
| CCEL-003 | P1 | executing | Register Langfuse, PromptLayer, PostHog and Braintrust as distinct observational candidates and define fair comparison. | Four entries in canonical registry and human catalog; claims remain candidate/unverified; comparison includes native baseline, individual treatments, combinations and interactions. |
| CCEL-004 | P1 | executing | Define event-driven awareness and GitHub-native trigger mapping. | PR/push/release/issues/workflow events map to existing paths; events are primary; bounded cursor reconciliation is fallback; no weekly discovery scheduler. |
| CCEL-005 | P1 | queued | Define DoE campaign admission, execution, analysis and promotion evidence. | Shared cohort/configuration identity, immutable run evidence, randomization/blocking, interaction analysis, uncertainty, costs and fail-closed promotion specified. |
| CCEL-006 | P1 | executing | Build category-aware refTemplates capability inventory and comparative scoring; add ASSERT as the first evaluation-pattern experiment; map ACS/Agent Governance Toolkit, Microsoft Agent Framework, Foundry Local, and Foundry Skills as independent concept-adaptation candidates. Keep source provenance, licensing duty, security review, and runtime admission as separate ownership lanes. | Categories 01–14 receive structured inventory; research-template scoring remains distinct from capability scoring; candidates carry source/revision/evidence/disposition; concept adaptations are testable through repository-owned adapters, with pinned upstream SDKs confined to experimental test lanes; benchmark plan compares native baseline, individual treatments, and combinations; results preserve uncertainty, maintenance cost, and Pareto trade-offs; tests cover deterministic inventory and scoring. |

| MOS-007 | P0 | executing | Implement the root Brain's domain-neutral, versioned specialist extension contract; implement the pure MOSAIC crate and adapter under `archwiz/mosaic_brain/`; register root Brain/MOSAIC scopes and ICM navigation; compose it from the existing host only after host ownership is verified. | `termux-brain` exports a validated typed extension contract; MOSAIC implements it through a one-way path dependency; run/cycle/attempt identity is preserved; contract/domain mismatches fail closed; evidence and recommendation rules are deterministic and tested; CRG scopes and ICM cards are present; generated graph publication remains with the publisher; no root-to-MOSAIC dependency or duplicate registry; host runtime routing remains a separately verified follow-on. |

## Validation

- python3 scripts/integrations/validate_capability_graph.py
- python3 -m unittest discover -s tests -p 'test_capability_opportunity_graph.py' -v
- python3 -m unittest discover -s tests -p 'test_refTemplates_capability_inventory.py' -v
- python3 -m unittest discover -s tests -p 'test_assert_acs_bridge.py' -v
- python3 -m unittest discover -s experiments/doe/assert_acs_2x2/acs -p 'test_policy.py' -v
- python3 scripts/doe/assert_acs_bridge.py plan --design experiments/doe/assert_acs_2x2/DESIGN.json --output /tmp/ceel-assert-acs-plan.json
- python3 scripts/integrations/validate_portfolio.py
- python3 scripts/proposals/validate_registry.py
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

GitHub object creation/retrieval is available in this session; a local checkout and shell runner are not. The PR's Actions runs are the executable validation evidence. Queued/running is not a pass.


## CCEL-006 execution record — 2026-11-25

- Branch: `feat/ceel-006-concept-competition-20261125`
- Pull request: #5908
- Candidate references: 8 metadata-first concept adaptations across five refTemplates categories.
- Runnable ASSERT × ACS pilot: `experiments/doe/assert_acs_2x2/` (3 fixed tasks × 4 evaluator/governance cells = 12 planned observations).
- Common reference oracle: pre-registered per-task/per-governance gold labels; the bridge reports evaluator accuracy against the same oracle and governance task-success separately.
- Adapter: `scripts/doe/assert_acs_bridge.py` (plan, assemble, record); native scorer: `experiments/doe/assert_acs_2x2/native_score.py`; ACS mock host and redacted decision receipt: `experiments/doe/assert_acs_2x2/acs/`.
- Pure tests: bridge and policy-dispatcher suites are wired into refTemplates continuous-eval CI.
- Runtime smoke: `.github/workflows/ceel-assert-acs-runtime.yml` builds the ACS SDK at pinned upstream commit `3233be2338816257700a8dbdf531a21b9f359582` and executes allow/transform/deny through HostSession.
- Provider-backed execution: PENDING credentials and a same-cohort ASSERT run; mock adapter conformance is distinct from efficacy.
- Capability graph: 21 nodes, 31 edges; structural validation reports 0 unresolved endpoints or duplicate IDs/edges. The managed Foundry platform is recorded separately from its component projects.
- Inventory: categories 01–14; research-template scoring remains a separate profile under 15_.
- Capability score: metadata readiness only; efficacy remains unmeasured until controlled runs.
- Licensing: designated licensing duty owner retains that responsibility; CEEL records capability/source evidence and the handoff boundary.
- Experiment order: ASSERT × ACS 2×2; then independent runtime, local inference, prompt/context and lifecycle comparisons.
- CI / local test execution: PENDING same-head Actions evidence.
