# Hex Capability & Access Register

**Status:** verified connector-surface record  
**Purpose:** prevent future collaborators from confusing a connected tool definition with successful workspace access.

## What was actually available

The connected Hex tool exposes four operations:

| Capability | Tool surface | Current result in this environment |
|---|---|---|
| Search projects | project free-text search | **Plan blocked**: Team or Enterprise required. |
| Create analysis thread | submit an agent-driven analysis question | Available as a connector operation, but workspace access is currently plan blocked. |
| Get analysis thread | retrieve a previously created thread by ID | Available as a connector operation; no usable thread ID was established here. |
| Continue analysis thread | append a message and resume an idle thread | Available as a connector operation; no usable thread ID was established here. |

The most recent attempted project search for `SHE Dashboard Historical Corpus Actions Backfill ATES agent throughput Hex export ZIP` returned the explicit platform response that MCP server access requires a Team or Enterprise plan.

**Therefore:** the assistant did not successfully open or inspect a Hex project in this environment. Invoking the connector is not evidence of workspace access.

## Repository-side Hex capabilities already implemented

Independently of live Hex access, the repository has a Hex-compatible evidence contract:

- Contract: `3l0.moneyball.v1`.
- Five datasets: `experiment_run`, `agent_task_attempt`, `provider_call`, `outcome_score`, `manager_decision`.
- Stable run-attempt/call/score/decision identities.
- Metadata-first privacy boundary.
- Sanitized NDJSON/CSV export plus receipt.
- Validation, reconciliation, freshness, idempotency, contract-drift, calculation-drift, and matcher-quality gates are specified.
- Proposed Hex topology includes Contract Validation, Experiment Ledger Explorer, Moneyball Scorecard, Regression Watch, Issue Observatory, Proposal Decision Observatory, Research Adaptation Radar, and Wolfram Verification Bench.
- Hex remains an analytical/evidence presentation consumer; GitHub Actions is the execution plane and the durable corpus remains authoritative.

See `docs/ops/HEX-MONEYBALL-INTEGRATION.md` for the full data contract and topology.

## SHE relationship

SHE is deliberately useful without Hex. The evidence path is:

`GitHub → Actions → sanitized evidence/corpus → SHE reducers → snapshots → optional Hex`

A native Hex ZIP is not canonical. If a ZIP is recovered, register exact bytes and SHA-256 first, then map:

`artifact → source run/attempt → source SHA → corpus snapshot → schema/contract → derived metric`

Anything that cannot be mapped remains `UNVERIFIED`.

## ZIP interpretation

A ZIP encountered during agent work can be:

1. a GitHub Actions artifact ZIP;
2. a Hex-native export/package;
3. an agent/session archive;
4. an unrelated archive.

The repository currently proves that the Hex-compatible GitHub Actions artifact lane exists; it does not prove that a historical native Hex ZIP was received. Do not classify by filename alone.

## Relevance classes

- `direct` — schema/contract data required by SHE or an existing evidence consumer.
- `supporting` — useful metadata or fixture data that can be reconciled to canonical evidence.
- `historical-lead` — potentially reconstructive but provenance incomplete.
- `unrelated` — no defensible mapping to the evidence plane.
- `unknown` — insufficient evidence to classify.

## Access boundary

No Hex secret, prompt, completion, provider credential, or raw workspace data belongs in this repository. When live Hex access becomes available, record the project identity and export provenance, not credentials.
