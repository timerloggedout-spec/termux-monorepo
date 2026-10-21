# Paper2Agent Scientific Factory — Implementation Items

| ID | Item | Priority | Acceptance evidence |
|---|---|---:|---|
| SAF-001 | Define versioned paper manifest schema | P0 | schema validation + fixture |
| SAF-002 | Define claim/method/result graph schema | P0 | valid/invalid fixtures + relationship validation |
| SAF-003 | Define environment/provenance binding | P0 | source SHA + lock + image digest fixture |
| SAF-004 | Define MCP tool/resource/prompt descriptors | P1 | schema fixture + deterministic IDs |
| SAF-005 | Define reference-result comparison contract | P0 | exact, tolerance, statistical, image/table adapter examples |
| SAF-006 | Define scientific evidence event classes | P0 | JSONL examples linked to manifest/run/artifact |
| SAF-007 | Define scientific-agent acceptance certificate | P0 | certificate fixture + state validator |
| SAF-008 | Define scientific-agent registry record | P1 | routability fixture with certificate reference |
| SAF-009 | Add bounded scientific fixture corpus | P1 | deterministic fixture runs |
| SAF-010 | Add sandbox execution prototype | P1 | denied-network/secret-isolation/resource-limit evidence |
| SAF-011 | Add reference reproduction harness | P1 | reference vs generated artifact comparison |
| SAF-012 | Add router admission adapter | P2 | only certificate-qualified agents enter scientific routing |
| SAF-013 | Add manager tournament cohort adapter | P2 | same cohort/evidence schema across policies |

## Gate order

schema → fixtures → validator → bounded reproduction → certificate → registry → router admission.

Do not wire unvalidated scientific agents into production routing.

## First fixture

Start with a synthetic deterministic research fixture: immutable source tree, tiny dataset, deterministic method, expected scalar/table artifact, pinned environment lock, known comparison tolerance, and intentional failure fixture. Only after this contract survives should a real paper/code repository become a cohort.
