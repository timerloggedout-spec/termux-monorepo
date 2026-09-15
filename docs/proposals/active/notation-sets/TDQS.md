# TDQS — Tool Definition Quality Score

**Registry class:** cross-domain research framework / external evaluation notation

**Canonical external owner:** Glama (`glama-ai/tool-definition-quality-score`)

**Local role:** stable reference term for tool-definition quality evidence; not a
canonical replacement for the repository's own AEF/3L0/ATES metrics.

## Definition

**TDQS** evaluates how well an MCP tool definition communicates its purpose,
usage, behavior, parameters, and context to an AI agent.

## Dimensions

`Purpose Clarity · Usage Guidelines · Behavioral Transparency · Parameter Semantics · Conciseness & Structure · Contextual Completeness`

Weights: `25 / 20 / 20 / 15 / 10 / 10`.

## Semantic boundary

```text
TDQS  → tool-definition quality
ATES  → execution/throughput observation
AEF   → evaluation-unit/evidence boundary
3L0   → integrated decision/evidence aggregation
```

Do not alias TDQS to agent quality, model quality, task correctness, or
throughput.

## Provenance

- Glama TDQS rationale: `https://glama.ai/blog/2026-04-03-tool-definition-quality-score-tdqs`
- Glama methodology: `https://glama.ai/mcp/methodology`
- upstream repository: `glama-ai/tool-definition-quality-score`
- project fork: `timerloggedout-spec/tool-definition-quality-score_fork`

## Local implementation

`she/metrics/tdqs.py` implements the deterministic preparation and aggregation
boundary. The full LLM rubric remains an evaluator lane so the model, rubric
version, justifications, and confidence can be retained as explicit evidence.

## Related integration surfaces

- `docs/architecture/AGENT-EVALUATION-FRAMEWORK.md`
- `docs/architecture/TOOL-DEFINITION-QUALITY-SCORE.md`
- `docs/ops/AGENT-OBSERVABILITY-RESEARCH-MATRIX.md`
- `she/metrics/tdqs.py`
- `tests/test_tdqs.py`
- `timerloggedout-spec/n8n-nodes-toolhouse_fork` — Toolhouse/n8n reference integration
- Toolhouse MCP — credentialed external MCP reference, not a local dependency
