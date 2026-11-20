# Capability Discovery Routing — design-only DoE candidate

**Campaign:** `capability-discovery-routing`  
**State:** proposal-only / admission pending  
**Design:** [DESIGN.json](DESIGN.json)  
**DoE matrix:** [dimensions 41–48](../../../docs/ops/DOE-QUESTIONS-MATRIX.md)  
**Capability contract:** [discovery and activation](../../../docs/ops/CAPABILITY-DISCOVERY-AND-ACTIVATION.md)

## Question

Does nested tagging plus metadata-first progressive loading improve relevant-and-safe top-k capability retrieval while reducing context ingestion and unnecessary tool/schema hydration?

## Planned design

Blocked (2^3) factorial:

- source scope: repository-only vs repository + approved catalog snapshots;
- taxonomy depth: flat tags vs nested domain/function/facets;
- context hydration: broad definitions vs metadata-first progressive loading.

Eight fixed tasks × eight arms = 64 planned observations, blocked by task family and difficulty. Exact task cohort and budget require DoE-expert admission.

## Repository baseline sources

The source cohort includes the existing `workspace/llm_map/_TOOL_TAXONOMY/` catalog: 3,388 valid `all_tools.jsonl` records, 104 tags, 25 role profiles, 103 category views and the generator modules. The README count is stale by one (3,387 vs 3,388). The discovery index now imports the JSONL as individual unverified tool records; category/role files remain derived views. The 531-entry `state/` directory is retained as metadata-only provenance and excluded from full context hydration.

Claude export inputs are separately represented by Issue #5657 and importer PR #5667. Their source checksum chain remains unverified because the issue's SHA256SUMS names split parts that are absent from its attachment list, and the issue omits the JSONL inventory required by the importer. The DoE must preserve this source-trust distinction.

## Evidence boundary

Each executed run emits one record under `docs/ops/corpus/EXPERIMENT.schema.json`. Pin the configured instance, base/candidate SHAs, catalog hashes, task cohort, evaluator and assignment. Preserve failed, blocked, missing and partial observations.

The indexer and CI evidence build remain separate from campaign dispatch. External catalog calls require their own configured credentials and approved budget. Installation, write actions and production promotion remain outside the discovery experiment.
