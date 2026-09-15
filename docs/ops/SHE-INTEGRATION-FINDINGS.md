# SHE / Hex / Historical Corpus / Agent Throughput — Integration Findings

**Status:** collaboration ledger for the current integration phase  
**Tracking:** #522  
**Canonical branch:** `master`  
**Purpose:** consolidate what exists, what was verified, what was only proposed, and what automation now owns.

## 1. Executive finding

The repository already had substantially more of the SHE/observability system than a fresh implementation would suggest. The main gaps were not conceptual contracts; they were provenance closure, historical-corpus continuation, and a clear boundary between repository-native automation and optional external analytics.

This phase therefore does four things:

1. records the actual Hex connector boundary;
2. indexes the SHE contracts and existing `.mmd`/PNG automation lane;
3. converts Historical Corpus continuation from an intentionally operator-only workflow into bounded autonomous current-master continuation;
4. adds a pure quality-aware multi-agent throughput reducer and event contract based on the Gemini ATES proposal.

## 2. Hex — what is actually known

### Connector capability surface

The connected Hex integration exposes:

- project search;
- analysis-thread creation;
- analysis-thread retrieval/status;
- analysis-thread continuation.

A project search was actually invoked during this investigation. The platform returned an explicit plan restriction: MCP server access requires a Team or Enterprise plan.

Therefore **no live Hex project was successfully inspected in this phase**. Connector invocation is not equivalent to workspace access.

### Repository-side Hex implementation

The repository independently contains the Hex/Moneyball contract `3l0.moneyball.v1`, a privacy-preserving sanitizer, validation tests, and a GitHub Actions evidence-artifact lane.

Five canonical datasets are specified:

1. `experiment_run`
2. `agent_task_attempt`
3. `provider_call`
4. `outcome_score`
5. `manager_decision`

The durable execution/evidence authority remains GitHub Actions + the repository corpus. Hex is an analytical consumer.

### ZIP finding

A historical native Hex ZIP remains **UNVERIFIED / NOT ESTABLISHED**.

The repository does prove a GitHub Actions artifact ZIP mechanism whose contents are sanitized evidence (`evidence.ndjson`, `evidence.csv`, `receipt.json`). That artifact is Hex-compatible transport, not proof of a native Hex export.

A candidate ZIP is relevant only if it can be mapped:

`artifact → run/attempt → source SHA → corpus snapshot → contract/schema → derived metric`

The forensic register is `docs/ops/HEX-ARTIFACT-RECOVERY.md` and the capability boundary is `docs/ops/HEX-CAPABILITY-REGISTER.md`.

## 3. SHE Dashboard — where the specification lives

The canonical SHE product surfaces are:

- `docs/ops/SHE-DASHBOARD-PRD.md`
- `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd`
- `docs/ops/SHE-DASHBOARD-INDEX.md`

Related evidence contracts:

- `docs/ops/HISTORICAL-CORPUS-BACKFILL-STATUS.md`
- `docs/ops/CONTEXT-RELATIONSHIP-INDEX.md`
- `docs/ops/EVIDENCE-ENVELOPE.schema.json`
- `docs/ops/ACTION-EFFECT-EVENT.schema.json`
- `docs/ops/HEX-MONEYBALL-INTEGRATION.md`

SHE is a projection, not an evidence source. Partial corpus state is a first-class dashboard state.

## 4. `.mmd` / `.png` lane

There is already an automation lane; this was **not** a new design gap.

Canonical source:

- `docs/ops/diagrams/*.mmd`

Existing generator/validator:

- `scripts/ci/automation_docs.py`

Existing continuous workflow:

- `.github/workflows/automation-docs-continuous-refresh.yml`

Generated metadata:

- `docs/ops/generated/automation-workflow-catalog.json`
- `docs/ops/generated/automation-workflow-catalog.md`
- `docs/ops/generated/automation-diagram-assets.json`

Rendered PNGs are derived assets where present. The `.mmd` source remains authoritative. The lane is intentionally deterministic and source-hash based.

## 5. Historical Corpus — observed state

The canonical master manifest observed in the existing status record contains:

- 8,339 nodes;
- 15,120 edges;
- 13,041 verified edges;
- 2,079 candidate edges;
- 20 issues + 20 PRs in the current history window;
- 282 PR commits;
- 392 PR comments;
- 172 reviews;
- 246 review comments;
- 157 explicit references;
- 9 timeline cross-references;
- `history_window.next_start_page = 2`.

Therefore the canonical corpus is **PARTIAL_CONTINUATION_REQUIRED**, not complete.

A larger `master-staging` corpus also exists, but it was observed as diverged from current master. It is evidence, not a promotion source.

## 6. Historical Corpus — automation correction

The old backfill workflow was intentionally manual and resumed against `master-staging`. That is no longer acceptable for this automated environment because the continuation target can become stale.

The successor workflow now:

1. runs on a bounded schedule as well as explicit dispatch;
2. checks out current `master`;
3. reads `next_start_page` from the canonical manifest;
4. stops cleanly when `next_start_page` is null;
5. runs exactly one bounded continuation window per invocation;
6. validates that the page advanced;
7. records source/manifest/summary hashes in the run evidence;
8. commits only the corpus delta to `master`;
9. uses a master-specific concurrency lock;
10. never reads from or promotes stale `master-staging`.

**Important:** this phase changes the automation. It does not claim that a new Actions backfill run has already executed. Runtime execution remains a separate `EXECUTED` observation.

## 7. ATES / Gemini throughput proposal — adopted selectively

Adopted concepts:

- TCV as a raw reference;
- WTCV as the preferred complexity-aware throughput signal;
- TPV;
- handoff latency;
- action density;
- parallel yield;
- retry penalty index;
- tool execution delay;
- context ingestion efficiency;
- structured JSONL telemetry;
- optional explicit complexity scores;
- optional future AST complexity providers.

Deliberately **not** adopted as a merge gate:

- a hard `MIN_ATES_THRESHOLD`;
- treating time as quality;
- treating line churn as semantic difficulty without validation;
- inventing zeroes for missing token/baseline telemetry.

The new reducer is `she/metrics/agent_throughput.py` and the event schema is `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`.

Policy is documented in `docs/ops/AGENT-THROUGHPUT-METRICS.md`.

## 8. Complexity methodology

The first reducer accepts explicit `complexity_score` so the measurement contract can land without adding a heavy parser dependency to every Actions run.

A deterministic structural fallback is documented:

`C = ln(1 + additions + deletions) × sqrt(files_changed)`

Tree-sitter/Lizard/Radon/language AST implementations are future measurement providers. Before promotion into longitudinal scoring they need versioned fixtures and a variance benchmark. This prevents complexity instrumentation from becoming another proxy that agents can game.

## 9. Candidate observability backends

| Surface | Role | Status |
|---|---|---|
| GitHub Actions JSONL | primary evidence emission | **preferred/free-scope** |
| Langfuse | rich trace adapter | optional experiment |
| Arize Phoenix | local/open tracing adapter | optional parallel experiment |
| Hex | analytics/evidence presentation | **plan-blocked live access** |

The event schema gives all adapters one neutral comparison target.

## 10. Quality / evidence model

Throughput must be read beside:

- test/check outcomes;
- Action→Effect follow-through;
- attribution confidence;
- retries/conflicts;
- human intervention;
- complexity provider/version;
- `COMMITTED` / `EXECUTED` / `VALIDATED` / `PROMOTED` state.

The objective is not maximum activity. It is maximum validated integrated outcome per effort/context/retry/conflict/human-intervention budget.

## 11. Status matrix

| Surface | State | Evidence |
|---|---|---|
| SHE PRD | COMMITTED | `docs/ops/SHE-DASHBOARD-PRD.md` |
| SHE snapshot contract | COMMITTED | `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md` |
| SHE architecture | COMMITTED | `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` |
| SHE index | COMMITTED in this phase | `docs/ops/SHE-DASHBOARD-INDEX.md` |
| `.mmd` automation lane | EXISTING / AUTOMATED | `automation-docs-continuous-refresh.yml` |
| Hex contract | COMMITTED | `HEX-MONEYBALL-INTEGRATION.md` |
| Hex live workspace access | BLOCKED | connector plan restriction |
| Native Hex ZIP | UNVERIFIED | no exact bytes/provenance |
| Hex-compatible Actions ZIP | IMPLEMENTED | `hex-moneyball-evidence.yml` + sanitizer |
| Historical corpus master | PARTIAL | `next_start_page = 2` in status record |
| Historical backfill automation | IMPLEMENTED on branch | current-master bounded continuation workflow |
| Historical backfill runtime | UNEXECUTED in this phase | requires an observed Actions run |
| Agent throughput reducer | IMPLEMENTED on branch | `she/metrics/agent_throughput.py` |
| Agent throughput event schema | IMPLEMENTED on branch | schema JSON |
| ATES merge threshold | REJECTED | quality-first policy |
| Langfuse adapter | CONSIDERED | no dependency added |
| Phoenix adapter | CONSIDERED | no dependency added |
| Render/n8n Blueprint | REFERENCE ONLY | not a runtime dependency |

## 12. Provenance rule for future collaborators

Never collapse these states:

`DESIGNED → COMMITTED → EXECUTED → VALIDATED → PROMOTED`

A repository file proves design/commit state. An Actions run proves execution. Check/job/test evidence proves validation. A production ref proves promotion.

That distinction is mandatory for SHE, Hex recovery, historical backfill, and ATES measurement.
