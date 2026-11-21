# Research Astute — Implementation Items

| ID | Item | Priority | Acceptance evidence |
|---|---|---:|---|
| ASTUTE-001 | Define shared experiment, source, evidence, snapshot, and typed graph contracts | P0 | JSON schemas, manifest, registry, referential-integrity validator |
| ASTUTE-002 | Normalize the computational-limits seed as the first experiment package | P0 | manifest, stable source IDs, canonical prerequisite graph, alternate path hypotheses |
| ASTUTE-003 | Specify the shared interactive visualization UX for alternate paths and snapshots | P1 | interaction contract, graph-type renderers, path comparison, deep-link state |
| ASTUTE-004 | Integrate Research Astute validation into the existing research registry workflow | P1 | PR/push path filters, deterministic validation script, passing workflow |
| ASTUTE-005 | Establish authenticated standalone repository provisioning from the reusable research template | P1 | repository creation receipt, seeded repo, source linkage, initial validation |
| ASTUTE-006 | Implement the interactive viewer and graph-type adapters | P1 | tested experiment switching, path overlay/comparison, evidence inspector, accessible fallback |

## Gate order

Manifest and graph contracts → source/path reference validation → existing module adapters → interactive viewer → multi-experiment acceptance → repo-gate → termux-smoke → review and promotion.

## Scope boundary

Each thought experiment remains an independent research project inside the shared platform. The computational-limits project supplies the first example. Physical feasibility, engineering feasibility, and practical utility remain separate assessments.
