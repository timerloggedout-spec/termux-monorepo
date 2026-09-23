# Tool Definition Quality Score (TDQS) integration

## Status

**Integrated as an evaluation/observability provider lane.**

TDQS is not a replacement for task correctness, agent throughput, ATES/WTCV,
review evidence, or MoneyBall/3L0. It measures a different object: the quality
of a tool definition exposed to an AI agent.

## Why this belongs here

The Agent Evaluation Framework already evaluates **tools, orchestration
policies, agents, providers/models, and environments**. TDQS is therefore a
natural *tool-definition quality* signal inside the AEF boundary rather than a
router policy or a model leaderboard metric.

The operational placement is:

```text
MCP / connector tool definition
            │
            ▼
   TDQS context extraction
   + deterministic hard gates
            │
            ├───────────────┐
            ▼               ▼
      LLM rubric       schema/annotation
      evaluation       evidence
            │               │
            └───────┬───────┘
                    ▼
              TDQS score
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     tool quality        server coherence
          │                   │
          └─────────┬─────────┘
                    ▼
             AEF / MoneyBall
             evidence record
```

### Separation of concerns

| Layer | Responsibility | Canonical? |
|---|---|---:|
| MCP/connector schema | actual tool contract | **Yes** |
| `she/metrics/tdqs.py` | deterministic TDQS preparation + aggregation | **Yes, locally** |
| external TDQS rubric evaluator | six 1–5 LLM dimensions + justifications | provider/evaluator lane |
| ATES/WTCV/TCV | execution/throughput observations | separate metric family |
| MoneyBall/3L0 | integrated evidence aggregation | downstream |
| Glama | external reference implementation/benchmark surface | external |

## Upstream provenance

The upstream framework is maintained by `glama-ai/tool-definition-quality-score`
and the methodology is published by Glama. The current upstream changelog is
**TDQS v1.3 (2026-09-03)**. v1.3 passes the full `outputSchema` to the tool
scoring evaluator; v1.2 added deterministic integer half-up rounding and the
`definitionBytes` context signal; v1.1 added shadowing risk and invocation-cost
signals.

Reference:

- `glama-ai/tool-definition-quality-score`
- Glama TDQS rationale: `https://glama.ai/blog/2026-04-03-tool-definition-quality-score-tdqs`
- Glama indexing methodology: `https://glama.ai/mcp/methodology`

The user's fork is retained as a research/reference fork:
`timerloggedout-spec/tool-definition-quality-score_fork`.

The fork's changelog currently records v1.1, while the upstream reference has
advanced through v1.3. We therefore track the upstream version explicitly and
do **not** treat the fork as a runtime dependency that silently freezes the
rubric.

## Rubric

TDQS scores six dimensions from 1–5:

| Dimension | Weight |
|---|---:|
| Purpose Clarity | 25% |
| Usage Guidelines | 20% |
| Behavioral Transparency | 20% |
| Parameter Semantics | 15% |
| Conciseness & Structure | 10% |
| Contextual Completeness | 10% |

The deterministic aggregation is implemented locally in
`she/metrics/tdqs.py`. Missing descriptions are a hard gate at 1.0/D; a
purely tautological description caps Purpose Clarity at 2.0. Composite scores
use TDQS v1.2+ integer half-up rounding, not Python's banker rounding.

At server level, definition quality is calculated as 60% mean TDQS + 40%
minimum TDQS. Glama's overall server score then combines definition quality
(70%) with server coherence (30%). These rollups are pure functions so an
evaluator can be swapped without rewriting the measurement layer.

## Deterministic context signals

The local implementation records the structural signals used to ground the
rubric:

- parameter count and required parameter count;
- parameter-description coverage and enum coverage;
- nested-object presence;
- required-field count over the required subtree;
- schema depth;
- union-choice count;
- invocation-cost proxy;
- output-schema presence;
- MCP annotation values;
- meaningful title detection;
- canonical definition byte size;
- deterministic definition input hash.

`input_hash` is the cache/provenance boundary: a changed tool definition is a
new evaluation input. In v1.3 the evaluator must receive the **full output
schema**, not merely a `hasOutputSchema` boolean; the local module records the
schema as part of the hashed definition and leaves LLM evaluation to the
explicit evaluator lane.

## Evaluation record contract

A full TDQS evidence record should retain at least:

```text
tool_identity
server_identity
source_ref
source_sha
definition_input_hash
captured_at
tdqs_spec_version
evaluator_id
evaluator_model
rubric_version
context_signals
dimension_scores
dimension_justifications
flags
tdqs_score
tier
server_definition_quality
server_coherence
server_overall_score
attribution_confidence
```

The evaluator model/version is evidence, not a hidden implementation detail.
This permits re-scoring when the rubric/model pair changes without destroying
historical observations.

## What TDQS must not do

1. It must not become a merge-quality gate by itself.
2. It must not be interpreted as tool behavior correctness.
3. It must not replace execution evidence.
4. It must not be converted into a model leaderboard score without preserving
   the object being measured.
5. It must not silently rewrite a tool description to improve its own score.
6. It must not treat a missing TDQS observation as a zero-quality tool; missing
   evidence remains missing evidence.

## Relationship to the existing measurement stack

```text
Tool definition quality ─────── TDQS
                                      \
Tool execution ───── ATES/WTCV/TCV ────┐
                                      │
Task outcome / correctness ───────────┤
                                      ▼
                             AEF evidence record
                                      │
                                      ▼
                              MoneyBall / 3L0
                                      │
                                      ▼
                           manager/team evolution
```

This keeps the project aligned with the existing principle that integrated
outcome outranks speed and that attribution must remain reconstructable.

## Toolhouse / n8n incorporation

The Toolhouse research lane is **not** a TDQS dependency. The existing
`n8n-nodes-toolhouse_fork` is catalogued as an integration/reference surface;
its Toolhouse API credential remains external and optional. No API key is
required for the TDQS schema-quality lane.

Toolhouse MCP is likewise a reference integration. Its upstream configuration
requires a Toolhouse API key and bundle, so it is not enabled merely because
its repository is forked. Its tool definitions can become TDQS input when a
credentialed MCP capture is later available.

## Acceptance criteria

- deterministic context extraction has focused tests;
- hard gates and rollups are reproducible without network access;
- upstream provenance/version is recorded;
- v1.3 full-output-schema semantics are preserved at the evaluator boundary;
- v1.2 half-up rounding is deterministic;
- TDQS remains distinct from ATES/WTCV and task outcome;
- a future evaluator can attach six dimension scores without changing the
  canonical schema;
- tool/schema observations can be linked to AEF evidence and attribution.
