# Microsoft Agent Framework — Runtime Architecture Pattern

**Category:** `01_Agent_Runtime`  
**Disposition:** competing architecture candidate · metadata-first

## Source

See `SOURCE.txt`. Pin an immutable source revision before reproducible experiments.

## Pattern to extract

- Typed agent and workflow composition.
- Middleware and tool-boundary structure.
- Explicit workflow state and orchestration transitions.
- Portable patterns across supported language/runtime surfaces.

## Repository adaptation

Run an architecture tournament against the current manager/runtime. Extract the smallest useful primitives into repository-owned contracts. Preserve current runtime behavior as the control and compare identical tasks, prompts, tools and model configurations.

## Measures

Verified task success, recovery behavior, retries, tool-call correctness, latency, cost, observability, portability and maintenance effort.

## Ownership

CEEL owns concept extraction and experiment evidence. The designated licensing duty owner handles licensing disposition separately.
