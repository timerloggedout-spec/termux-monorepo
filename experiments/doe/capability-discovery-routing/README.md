# Capability Discovery Routing — design-only DoE candidate

**Campaign:** `capability-discovery-routing`  
**State:** proposal-only / not admitted  
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

## Evidence boundary

Each executed run emits one record under `docs/ops/corpus/EXPERIMENT.schema.json`. Pin the configured instance, base/candidate SHAs, catalog hashes, task cohort, evaluator and assignment. Preserve failed, blocked, missing and partial observations.

The indexer and CI evidence build are implementation work. They do not dispatch this campaign. External catalog calls require their own configured credentials and approved budget. Installation, write actions and production promotion remain outside the discovery experiment.
