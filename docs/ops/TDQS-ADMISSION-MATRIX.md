# TDQS admission and cross-repository coordination matrix

## Purpose

This is the bridge between the external/reference repositories already forked
by `timerloggedout-spec` and the monorepo's TDQS evaluation lane.

The rule is **capture first, score second**: a fork is a candidate source of
MCP tool definitions, not evidence that its tools have been scored or adopted.

## Current sources

| Source | Role | TDQS disposition | Next integration boundary |
|---|---|---|---|
| `timerloggedout-spec/tool-definition-quality-score_fork` | TDQS specification | **Reference** | track upstream spec/version drift |
| `glama-ai/tool-definition-quality-score` | upstream TDQS | **Canonical external reference** | evaluator/rubric provenance |
| `timerloggedout-spec/rjsf-validator-cfworker_fork` | JSON Schema validation | **Schema-validation provider candidate** | validate captured schemas before scoring |
| `glama-ai/rjsf-validator-cfworker` | upstream JSON Schema validator | **Reference** | edge/JS validation option |
| `timerloggedout-spec/gh-mcp` | GitHub MCP server wrapper | **P1 scoring corpus** | capture `tools/list` under controlled toolsets |
| `timerloggedout-spec/termux-mcp` | Termux/Android MCP | **P1 scoring corpus** | stabilize tool schemas, then capture |
| `timerloggedout-spec/mcp-toolshed_fork` | MCP aggregation + progressive discovery | **P1 server-coherence target** | score meta-tools + discovered tool definitions |
| `timerloggedout-spec/awesome-remote-mcp-servers_fork` | MCP discovery corpus | **Research/discovery** | generate candidate server cohort, do not score list text as tool definitions |
| `timerloggedout-spec/n8n-nodes-toolhouse_fork` | n8n Toolhouse integration | **Credentialed adapter/reference** | capture only when API credential is intentionally provisioned |
| `toolhouseai/toolhouse-mcp` | Toolhouse MCP | **Credentialed external reference** | capture `tools/list` only with authorized Toolhouse bundle/key |
| `timerloggedout-spec/lightport_fork` | OpenAI-compatible provider gateway | **Provider transport lane** | preserve as provider boundary, not TDQS input itself |
| `glama-ai/lightport` | upstream provider gateway | **Reference** | compare provider transport behavior separately |

## Priority cohorts

### P0 — contract fixtures

Use synthetic/local tool definitions to exercise:

- empty/missing descriptions;
- tautological descriptions;
- complete parameter descriptions;
- nested required objects;
- unions and nullable branches;
- output schemas with documented fields;
- annotations;
- sibling-name context;
- definition-byte and input-hash changes.

These are covered by `tests/test_tdqs.py` and do not require credentials.

### P1 — repository-owned MCP surfaces

Start with:

1. `gh-mcp` — large, real-world GitHub tool surface with configurable toolsets;
2. `termux-mcp` — project-owned MCP surface whose schemas are directly relevant
to the monorepo;
3. `mcp-toolshed_fork` — especially valuable for server-level coherence,
progressive discovery, and shadowing-risk experiments.

For each server, retain:

```text
server SHA
capture timestamp
MCP protocol version
server instructions
tools/list payload
selected toolset/discovery state
TDQS spec version
evaluator model/version
input hashes
per-tool scores
server coherence evidence
```

### P2 — external/credentialed sources

Toolhouse and other provider-backed MCP servers remain opt-in. Do not add
placeholder credentials or treat a fork as an authorization grant.

## Progressive discovery / Toolshed rule

`mcp-toolshed_fork` intentionally exposes meta-tools and discovers provider
tools progressively. This matters to TDQS because **server-level coherence is
state-dependent**:

```text
tools/list at admission
        ↓
search_tools / get_tool_schema
        ↓
discovered sibling set
        ↓
TDQS tool evaluation
        ↓
coherence / shadowing evaluation
```

Therefore the capture record must identify the discovery state. Do not compare
a static full-catalog server with a progressive-discovery server as if their
`siblingToolNames` contexts were equivalent.

## Validation rule

JSON Schema validation is a prerequisite observation, not a TDQS score. A
schema that fails validation should be recorded as a schema-contract error and
excluded from normal rubric aggregation until repaired or explicitly admitted
as a negative control.

The Glama `rjsf-validator-cfworker` fork is a reference option for JS/edge
validation. The monorepo does not add it as a Python runtime dependency merely
because it is forked.

## Toolhouse / n8n rule

The existing Toolhouse n8n fork documents an API-token credential and webhook
integration. That is useful architecture evidence, but it does not create a
credential in the monorepo. When a credentialed capture is eventually
available, its `tools/list` output can enter the same TDQS pipeline.

## Scoring boundary

```text
repository / MCP server
        │
        ▼
validated tools/list capture
        │
        ▼
TDQS context signals + inputHash
        │
        ▼
LLM rubric evaluator
        │
        ▼
per-tool TDQS + flags
        │
        ▼
server coherence / shadowing
        │
        ▼
AEF evidence record
        │
        ▼
MoneyBall / 3L0
```

TDQS remains a **tool-definition** signal. Execution correctness, task outcome,
ATES/WTCV/TCV, attribution, and manager quality remain separate evidence
families.
