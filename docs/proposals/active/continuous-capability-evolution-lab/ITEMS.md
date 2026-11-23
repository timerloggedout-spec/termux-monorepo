# ITEMS — continuous-capability-evolution-lab

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| CCEL-001 | P1 | executing | Establish CEEL architecture, boundaries, participant families, and source-of-truth map. | CLAUDE entry points to the design; CEEL reuses Integration Intelligence, DoE, ATES, Delphi and proposal authorities; no parallel control plane. |
| CCEL-002 | P1 | executing | Define capability opportunity graph, strict JSON Schema, seed inventory and deterministic validator. | Graph parses; node IDs unique; edge endpoints resolve; lifecycle/provenance states explicit; tests cover valid, duplicate, unresolved and malformed cases. |
| CCEL-003 | P1 | executing | Register Langfuse, PromptLayer, PostHog and Braintrust as distinct observational candidates and define fair comparison. | Four entries in canonical registry and human catalog; claims remain candidate/unverified; comparison includes native baseline, individual treatments, combinations and interactions. |
| CCEL-004 | P1 | executing | Define event-driven awareness and GitHub-native trigger mapping. | PR/push/release/issues/workflow events map to existing paths; events are primary; bounded cursor reconciliation is fallback; no weekly discovery scheduler. |
| CCEL-005 | P1 | queued | Define DoE campaign admission, execution, analysis and promotion evidence. | Shared cohort/configuration identity, immutable run evidence, randomization/blocking, interaction analysis, uncertainty, costs and fail-closed promotion specified. |
| CCEL-006 | P1 | queued | Document FOSS template inspiration, benefit compounding and evolutionary reuse. | Candidates have disposition and source provenance; reuse/combination measured; Pareto trade-offs and maintenance/security costs visible. |
| CCEL-007 | P1 | executing | Pre-register a fair comparison of fast-anything and rust-anything fork versions against the native baseline; extract a reusable repo-lab pattern from the clf-lab approach without cloning its classifier-specific control plane. | Candidate commits and crate versions pinned; common hot-path scope declared; blocked randomized design and independent correctness cohort specified; canonical experiment records and existing DoE authority reused; automation/fixtures/runner/agent identity gates explicit; no results or admission claim before observed runs. |
| CCEL-008 | P1 | executing | Pre-register a separate, extensible GitReverse reconstruction-quality comparison between upstream `filiksyos/gitreverse`, the in-progress internal implementation, and a structured human-reference baseline; measure Siglary integration only after source verification. | Upstream commit/license pinned; internal path/SHA and Siglary version recorded; matched repository corpus and blinded rubric frozen; source-attributed claims and unsupported-claim rate measured; outputs remain separate from Rust hot-path runtime outcomes; canonical DoE records and existing authority reused; design-only until fixtures, automation and runs exist. |

| MOS-007 | P0 | executing | Implement the root Brain's domain-neutral, versioned specialist extension contract; implement the pure MOSAIC crate and adapter under `archwiz/mosaic_brain/`; register root Brain/MOSAIC scopes and ICM navigation; compose it from the existing host only after host ownership is verified. | `termux-brain` exports a validated typed extension contract; MOSAIC implements it through a one-way path dependency; run/cycle/attempt identity is preserved; contract/domain mismatches fail closed; evidence and recommendation rules are deterministic and tested; CRG scopes and ICM cards are present; generated graph publication remains with the publisher; no root-to-MOSAIC dependency or duplicate registry; host runtime routing remains a separately verified follow-on. |

## Validation

- python3 scripts/integrations/validate_capability_graph.py
- python3 -m unittest discover -s tests -p 'test_capability_opportunity_graph.py' -v
- python3 scripts/integrations/validate_portfolio.py
- python3 scripts/proposals/validate_registry.py
- python3 scripts/ci/repo_gate.py
- python3 scripts/ci/termux_smoke.py

GitHub object creation/retrieval is available in this session; a local checkout and shell runner are not. The PR's Actions runs are the executable validation evidence. Queued/running is not a pass.
