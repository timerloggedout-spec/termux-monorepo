# SHE / Hex / Historical Corpus / Agent Throughput — Integration Findings

**Status:** collaboration ledger for the current integration phase  
**Tracking:** #522 / #523 extracts  
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

## 3. SHE Dashboard — where the specification lives

The canonical SHE product surfaces are:

- `docs/ops/SHE-DASHBOARD-PRD.md`
- `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md`
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd`
- `docs/ops/SHE-DASHBOARD-INDEX.md`

SHE is a projection, not an evidence source. Partial corpus state is a first-class dashboard state.

## 4. Historical Corpus — observed state

The canonical master corpus is **PARTIAL_CONTINUATION_REQUIRED**, not complete (`history_window.next_start_page` may be non-null).

A larger `master-staging` corpus also exists, but it is evidence, not a promotion source.

## 5. Historical Corpus — automation correction

The successor workflow:

1. runs on a bounded schedule as well as explicit dispatch;
2. checks out current `master`;
3. reads `next_start_page` from the canonical manifest;
4. stops cleanly when `next_start_page` is null;
5. runs exactly one bounded continuation window per invocation;
6. commits only the corpus delta to `master`;
7. never reads from or promotes stale `master-staging`.

**Important:** automation changes are separate from `EXECUTED` observations.

## 6. ATES / throughput — adopted selectively

Adopted: TCV, WTCV, TPV, handoff latency, action density, parallel yield, RPI, tool delay, CIE, structured JSONL telemetry.

**Not** adopted as a merge gate: hard `MIN_ATES_THRESHOLD`; treating time as quality.

Reducer: `she/metrics/agent_throughput.py`  
Schema: `docs/ops/AGENT-THROUGHPUT-EVENT.schema.json`  
Policy: `docs/ops/AGENT-THROUGHPUT-METRICS.md`

## 7. Quality / evidence model

Throughput must be read beside test/check outcomes, Action→Effect follow-through, attribution confidence, retries/conflicts, human intervention, and `COMMITTED` / `EXECUTED` / `VALIDATED` / `PROMOTED` state.

## 8. Provenance rule

Never collapse: `DESIGNED → COMMITTED → EXECUTED → VALIDATED → PROMOTED`.

A repository file proves design/commit state. An Actions run proves execution. Check evidence proves validation. A production ref proves promotion.
