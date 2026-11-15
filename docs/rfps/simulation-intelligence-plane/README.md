# Simulation Intelligence Plane — MiroFish × CAMEL-AI OASIS

Status: parallel proposal / architecture-contract build; not admitted to QUE execution and not production-ready.
Date: 2026-11-14
Canonical proposal: `docs/proposals/active/simulation-intelligence-plane/`
RFP packet: `docs/rfps/simulation-intelligence-plane/`

This lane proposes a reproducible, graph-grounded agent-based simulation capability. It combines the graph-to-agent workflow demonstrated by MiroFish with CAMEL-AI OASIS as the social simulation execution engine, while reusing the repository's existing QUE, Workflow Contract, Integration Intelligence, DoE, ATES, and evidence infrastructure.

It is deliberately parallel to the existing QUE/RFP/Delphi/DoE pipelines. It does not create a second scheduler, proposal registry, event ledger, graph authority, experiment framework, or production router.

## Deliverables

- [RFP](RFP.md) — problem, scope, sourcing, alternatives, requirements and evaluation rubric.
- [DESIGN](DESIGN.md) — architecture, trust boundaries, schemas, lifecycle and integration contracts.
- [ACCEPTANCE](ACCEPTANCE.md) — measurable phase gates and adversarial acceptance tests.
- [STATUS-AND-FINDINGS](STATUS-AND-FINDINGS.md) — evidence, assumptions, decisions and open questions.
- [SOURCES-AND-ALTERNATIVES](SOURCES-AND-ALTERNATIVES.md) — upstream references, alternatives, license and dependency compatibility findings.
- [candidate-queue.json](candidate-queue.json) — canonical role-separated candidate queue, repository-local status and comparison dimensions.
- [Termux ↔ GitHub control boundary](TERMUX-GITHUB-CONTROL-BOUNDARY.md) — defines Termux as the offline-capable local controller for GitHub surfaces, with simulation execution on declared remote workers.
- [DoE design proposal](../../../experiments/doe/sip-001-engine-comparison/DESIGN.md) — staged, role-separated experiment pre-registration; explicitly not admitted or executed.

**RFP intake trigger:** `.github/ISSUE_TEMPLATE/simulation-rfp.yml` (title prefix `[simulation:rfp]`) → QUE `swarm-admission` → `.github/workflows/simulation-rfp-intake.yml` → validated G0 intake receipt queued for brief/evidence freeze. Delphi generation is a separate explicit dispatch after brief/evidence freeze.


## One-sentence concept

A scenario laboratory that converts versioned source evidence and a selected knowledge-graph snapshot into explicitly synthetic agent populations, runs controlled OASIS simulations through a bounded MiroFish-compatible adapter, and returns immutable experiment evidence for DoE/ATES analysis—never silently upgrading simulated behavior into factual corpus knowledge.

## Authority

- QUE: admission, claims, queueing, scheduling and dispatch authority.
- Workflow Contract: declarative task/workflow intent and dependencies.
- DoE: experiment design, factors, cohorts, assignment and comparison.
- Simulation Plane: scenario preparation, graph-to-agent projection, simulation adapter and run evidence packaging.
- OASIS: social-environment execution only.
- MiroFish-compatible workflow: evidence-to-ontology/graph/persona preparation and post-run analysis.
- ATES: deterministic benchmark harness and trace/evaluation reduction.
- Integration Intelligence / CEEL: provider inventory, normalized events, idempotency and evidence references.
- Human review / independent verification: promotion decisions and factual-corpus admission.

No component may infer or assume authority from a successful run, an agent-generated report, a high confidence score, or a provider response.

## Current state

The repository already has substantial reusable infrastructure. This branch adds the proposal and initial contract package only. It does not claim that OASIS, MiroFish, external model providers, or a graph backend have been installed, authenticated, executed, or validated in CI.
