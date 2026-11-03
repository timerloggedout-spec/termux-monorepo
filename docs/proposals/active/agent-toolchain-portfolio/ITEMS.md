# Work Items — agent-toolchain-portfolio

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| ATP-001 | P0 | executing | Extend canonical Integration Intelligence registry and publish capability/authority matrix for Context.dev, Context7, Mintlify, Smart Model Router, HAPI MCP Registry, and Sprites. | Six unique IDs; session/repository/runtime evidence separated; no secret-shaped values; catalog and registry agree; proposal lifecycle validation passes. |
| ATP-002 | P0 | executing | Implement read-only HAPI MCP Registry metadata normalizer and sanitized fixtures. | Stable server/version identity; transport/capabilities/source/freshness fields; unknowns preserved; no server execution or admission; fixture tests cover malformed and stale records. |
| ATP-003 | P0 | executing | Implement Context7 and Context.dev source-evidence contracts. | Context7 requires resolved library ID/version; Context.dev records URL/retrieval time/request identity; provenance and redaction tests pass; no raw session/prompt capture. |
| ATP-004 | P1 | planned | Reconcile Smart Model Router with existing repository routing authorities and build offline policy comparison only if non-duplicative. | Existing router is identified; no second router; deterministic replay fixtures and cost/quality comparison; no live traffic switch or paid inference. |
| ATP-005 | P1 | planned | Build a disposable Sprites validation profile for repository PR checks. | Exact source SHA binding; no default secrets; bounded command/time/resource/network policy; artifacts attributed; cleanup and failure receipts verified. |
| ATP-006 | P1 | planned | Pilot Mintlify documentation authoring on a review branch. | Existing deployment target and navigation inspected; non-sensitive page diff reviewed; publish and live deployment remain separate explicit approval gates. |
| ATP-007 | P1 | executing | Integrate portfolio validation into existing repo-gate/proposal lifecycle. | JSON/YAML parse; duplicate-ID and matrix parity checks; secret-pattern negative tests; exact-head CI evidence; no new scheduler or parallel registry. |

## Disposition

ATP-001 established the portfolio and registry. ATP-002 and ATP-003 now have offline normalizer implementations and contract tests in PR #4086; their exact-head CI and later runtime validation remain outstanding. ATP-004 through ATP-007 remain sequenced follow-on work; no live provider access or external side effect is authorized by these items. The existing Integration Intelligence registry, adapter contract, proposal lifecycle, and repository dual gates remain authoritative.
