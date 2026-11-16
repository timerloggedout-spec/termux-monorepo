# Software Recipe Intelligence — Implementation Backlog

**Status:** research backlog; no implementation or execution admission implied.

| ID | Priority | Work | Deliverable | Exit condition |
|---|---|---|---|---|
| SRI-000 | P0 | Identity, naming and collision census | Name register + issued-name decision | Name Forge/registry review complete; acronym and slug collision checked |
| SRI-001 | P0 | System-wide ownership and deployment census | Architecture recon + source-owner map | Existing Brain/agent/graph/memory/recipe/orchestration systems and authorities mapped |
| SRI-002 | P0 | Recipe prior-art boundary | Repo Replay / Commit Replay compatibility note | Separate planes preserved; no duplicate replay engine |
| SRI-003 | P0 | Neutral Software Recipe Model | Versioned model specification | Atomic/component/workflow/agent/team/integration/experiment/operational recipes represented |
| SRI-004 | P0 | Schema and validator | JSON Schema + positive/negative fixtures | Unknown, stale, disputed, unavailable and evidence classes validated |
| SRI-005 | P1 | Read-only source extraction | Git/docs/manifests/workflow/skill extractors | Every extracted fact has immutable source and extractor provenance |
| SRI-006 | P1 | Structural analysis | Tree-sitter and dependency/call-graph adapters | Parser/version gaps explicit; no syntax-to-semantics overclaim |
| SRI-007 | P1 | Taxonomy and classification baseline | Rules + Naive Bayes/logistic baseline | Held-out precision/recall and calibration reported |
| SRI-008 | P1 | Similarity and duplicate evaluation | Lexical, ingredient, AST, graph and embedding comparison | Precision/recall; similarity never implies equivalence |
| SRI-009 | P1 | CRG and integration-registry adapters | Read-only projections | Owner-approved IDs/edges and publisher path |
| SRI-010 | P1 | Workflow/agent/team recipe representation | Typed workflow/agent/team examples | Roles, tools, handoffs, isolation, provenance and stop states covered |
| SRI-011 | P2 | Contract-aware retrieval/composition | Candidate composer | Reject incompatible or unknown contracts; preserve abstention |
| SRI-012 | P2 | DoE comparison | Preregistered experiment and report | Canonical schema, blocked/held-out design and independent review |
| SRI-013 | P2 | Operational evidence adapters | OTel/CI/ATES/SHE/3L0 references | Evidence linked without duplicating telemetry or experiment stores |
| SRI-014 | P3 | Sandboxed execution research | Separate threat model and safety RFP | Explicit admission, resource/network limits, receipts and independent validation |
| SRI-015 | P3 | Bounded evolution recommendations | Revision proposal generator | Human/independent admission; no self-approval or autonomous promotion |

## Dependency order

```text
SRI-000 + SRI-001
       ↓
SRI-002 → SRI-003 → SRI-004
                       ↓
SRI-005 → SRI-006 → SRI-007 → SRI-008
                       ↓             ↓
                  SRI-009 → SRI-010 → SRI-011
                                      ↓
                                   SRI-012
                                      ↓
                                   SRI-013
                                      ↓
                         separate safety admission
                                      ↓
                              SRI-014 → SRI-015
```

## Loop discipline

Each work item follows RECON → PLAN/MEASURE → ACT → COMMIT → WAIT → WATCH → VALIDATE → RE-FETCH → COMPARE → CLASSIFY → RECORD → REPEAT.

Queued is not success. Committed is not executed. Executed is not validated. Validated is not promoted. Stop on approval-required, blocked, exhausted, stagnated, or a safety violation; do not retry failures merely to obtain a green result.

## Non-goals

No new Brain, graph DB, memory store, scheduler, experiment ledger, integration registry, naming authority, replay engine, secret store, or promotion authority. No recipe execution, external writes, paid inference, production routing, merge, deploy, or permission expansion under this backlog.
