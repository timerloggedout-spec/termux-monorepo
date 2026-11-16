# ITEMS — continuous-capability-evolution-lab

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| CCEL-001 | P1 | executing | Establish CEEL architecture, boundaries, participant families, and source-of-truth map. | CLAUDE entry points to the design; CEEL reuses Integration Intelligence, DoE, ATES, Delphi and proposal authorities; no parallel control plane. |
| CCEL-002 | P1 | executing | Define capability opportunity graph, strict JSON Schema, seed inventory and deterministic validator. | Graph parses; node IDs unique; edge endpoints resolve; lifecycle/provenance states explicit; tests cover valid, duplicate, unresolved and malformed cases. |
| CCEL-003 | P1 | executing | Register Langfuse, PromptLayer, PostHog and Braintrust as distinct observational candidates and define fair comparison. | Four entries in canonical registry and human catalog; claims remain candidate/unverified; comparison includes native baseline, individual treatments, combinations and interactions. |
| CCEL-004 | P1 | executing | Define event-driven awareness and GitHub-native trigger mapping. | PR/push/release/issues/workflow events map to existing paths; events are primary; bounded cursor reconciliation is fallback; no weekly discovery scheduler. |
| CCEL-005 | P1 | queued | Define DoE campaign admission, execution, analysis and promotion evidence. | Shared cohort/configuration identity, immutable run evidence, randomization/blocking, interaction analysis, uncertainty, costs and fail-closed promotion specified. |
| CCEL-006 | P1 | queued | Document FOSS template inspiration, benefit compounding and evolutionary reuse. | Candidates have disposition and source provenance; reuse/combination measured; Pareto trade-offs and maintenance/security costs visible. |

## Validation

- python3 scripts/integrations/validate_capability_graph.py
- python3 -m unittest discover -s tests -p 'test_capability_opportunity_graph.py' -v
- python3 scripts/integrations/validate_portfolio.py
- python3 scripts/proposals/validate_registry.py
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

GitHub object creation/retrieval is available in this session; a local checkout and shell runner are not. The PR's Actions runs are the executable validation evidence. Queued/running is not a pass.
