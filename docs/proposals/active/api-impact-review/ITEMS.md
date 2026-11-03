# ITEMS — api-impact-review

| ID | Priority | Deliverable | Acceptance evidence | State |
|---|---:|---|---|---|
| APIII-001 | P0 | Read-only, SHA-bound API Impact Review lane with deterministic detection, mapper-result normalization, privacy/evidence validation, PR artifact, assistant skill, and CI workflow | Unit tests cover detector, identity, evidence, uncertainty, privacy, deterministic output, and CLI; repo-gate + Termux smoke pass on same SHA; report artifact records exact PR/base/head | executing |

## Scope boundaries

- The API Impact Mapper is advisory and analyzes supplied material only.
- The workflow has read-only permissions and does not execute provider-returned code.
- Missing mapper output is reported as `analysis_required`; partial findings remain partial.
- Blocking status, hosted MCP bridge, paid API calls, or merge authority are out of scope for this item.
