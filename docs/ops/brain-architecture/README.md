# ADE-SYNAPSE — Synthetic Cognitive Architecture

**Status:** architecture proposal and repository mapping  
**Branch:** `feat/ade-synapse-brain-architecture`  
**Canonical registry:** [registry/brain-region-registry.json](registry/brain-region-registry.json)  
**System model:** [models/ade-synapse-model.md](models/ade-synapse-model.md)  
**Evolution plan:** [roadmap/evolution-roadmap.md](roadmap/evolution-roadmap.md)  
**Research lane:** [research/neuro-inspired-patterns.md](research/neuro-inspired-patterns.md)  
**Experiment lane:** [experiments/README.md](experiments/README.md)  
**Proposal lane:** [proposals/README.md](proposals/README.md)  
**Diagram source:** [../diagrams/ade-synapse-brain.mmd](../diagrams/ade-synapse-brain.mmd)

## What is ADE-SYNAPSE?

**ADE-SYNAPSE** means **Synthetic Neuro-Architecture for Planning, Adaptation, Navigation, Sensing, and Evolution**. It is a proposed organizing model for the Agentic Development Environment (ADE): a coordinated system of agents, tools, memory, execution, observability, evaluation, and safety controls.

The brain analogy is a design vocabulary. It does not assert biological equivalence, consciousness, sentience, or human-like subjective experience.

## Why a brain architecture?

The repository already contains several cooperating capabilities: manager-led agent orchestration, dynamic provider routing, GitHub Actions execution, context relationship indexing, quality/throughput measurement, and the SHE evidence/dashboard surface. These are better understood as interacting functional systems than as a single model router.

SYNAPSE makes those relationships explicit, identifies partial coverage, and gives proposed capabilities a safe place to mature without pretending that a document creates an implementation.

## Status vocabulary

| Status | Meaning |
|---|---|
| `existing` | A concrete repository subsystem or documented workflow supports the mapping. |
| `partial` | A related capability exists, but the proposed cognitive function is only partly covered. |
| `proposed` | An architectural lane or capability is recommended; implementation is not established. |
| `research` | An exploratory analogy requiring evidence and a bounded experiment before adoption. |

The registry records both the mapping status and the evidence paths. A mapping is not an implementation claim.

## Directory map

- `registry/` — machine-readable region/network/system registry.
- `models/` — overall system architecture and interaction contracts.
- `roadmap/` — staged capability evolution and acceptance gates.
- `research/` — biological inspiration translated into engineering hypotheses.
- `experiments/` — controlled experiments, metrics, and result receipts.
- `proposals/` — new subsystem proposals and unresolved design decisions.
- `../diagrams/` — canonical Mermaid source; rendered assets remain derived outputs.

## Core design rules

1. **Evidence before status:** only repository paths and observed execution support an `existing` claim.
2. **Quality before speed:** throughput and reward signals never override correctness, review, security, or acceptance.
3. **One shared event language:** agents and adapters emit privacy-safe, versioned evidence rather than inventing incompatible telemetry.
4. **Memory is not authority:** context can inform a decision but cannot grant permissions or override source-of-truth state.
5. **Proposal is not production:** experimental systems remain isolated until validated and explicitly promoted.
6. **No hidden autonomy escalation:** execution, external writes, credentials, merges, and promotion remain subject to existing authority and approval contracts.
7. **Biology is inspiration, not a blueprint:** prefer useful functional abstractions over one-to-one anatomical literalism.

## First architectural synthesis

The system is organized into six cooperating planes:

1. **Executive cognition** — goals, planning, decomposition, manager policy.
2. **Attention and routing** — triage, prioritization, admission, provider/tool selection.
3. **Memory and knowledge** — episodic relationships, semantic registries, provenance.
4. **Action and integration** — specialist agents, adapters, repository changes, CI.
5. **Homeostasis and safety** — telemetry, resource health, security, authority boundaries.
6. **Learning and evolution** — outcome evaluation, controlled policy tournaments, consolidation, retirement.

See the registry for the full region-by-region map and the model for signal flow.
