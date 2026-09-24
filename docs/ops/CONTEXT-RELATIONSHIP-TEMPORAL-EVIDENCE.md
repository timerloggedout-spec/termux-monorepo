# Context Relationship Temporal Evidence Contract

**Status:** implemented contract — L2 temporal evidence for the repository-native context relationship graph.

## Purpose

The temporal layer preserves how the relationship corpus was observed over time. It does not replace the canonical L1 graph and does not promote candidates into facts.

Pipeline:

`GitHub/repository source → normalized relationship corpus → temporal snapshots/deltas → SHE/3L0/research projections`

## Canonical artifacts

`workspace/llm_map/context_relationships/` remains the current materialized relationship view.

Temporal evidence is stored beneath:

```text
temporal/
  snapshots/<snapshot_id>/
    manifest.json
    nodes.jsonl
    edges.jsonl
    lineage.json
  lineage.jsonl

temporal-current.json
```

A snapshot is immutable. Replaying an identical observation must not replace its bytes.

## Snapshot identity

A snapshot is deterministically bound to:

- repository;
- source ref;
- source SHA;
- observation timestamp;
- history start page;
- history continuation page.

The resulting stable identifier is `crg-<content hash prefix>`.

## Coverage

Allowed states:

- `COMPLETE`
- `PARTIAL_CONTINUATION_REQUIRED`
- `PARTIAL_BOUNDARY`
- `FAILED`
- `UNVERIFIED`

Historical completeness requires:

`history_window.next_start_page == null`

Node/edge counts do not establish completeness.

## Delta semantics

Each observation compares the prior materialized graph with the new graph and records:

- nodes added/removed/changed;
- edges added/removed/changed;
- relationship reclassification.

A candidate → verified transition is retained as a reclassification event. The prior candidate observation remains historically valid.

## Provenance invariant

Every temporal snapshot retains:

`snapshot → source SHA/ref → collection window → coverage → graph hashes`

The L1 graph remains metadata-only and evidence-backed. The L2 layer adds observation history; it does not store discussion bodies, credentials, browser state, session stores, or other excluded sensitive material.

## Consumer contract

SHE and downstream research may consume:

- snapshot coverage;
- snapshot-to-snapshot deltas;
- relationship trajectories;
- lineage;
- exact graph/evidence identifiers.

Consumers must preserve:

- verified/candidate separation;
- explicit partial coverage;
- unknown attribution;
- immutable historical observations.

## Validation

The temporal contract is covered by `tests/test_context_relationship_temporal.py` for deterministic identity, structural deltas, reclassification, invalid coverage/page rejection, lineage, and immutable snapshot writes.

The normal context-relationship test family remains the required integration gate.
