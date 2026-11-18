# Source and architecture reconnaissance

Observed: 2026-11-16
Repository: timerloggedout-spec/termux-monorepo
Target candidate: https://github.com/timerloggedout-spec/Time_forkinto

## 1. Target-source verification

| Check | Result |
|---|---|
| GitHub file/API retrieval for the supplied repository | HTTP 404 |
| GitHub repository search for Time_forkinto | No matching accessible result |
| Repository code search for Time_forkinto in termux-monorepo | No match |
| Exact candidate identity, description, license, default branch, commit | NOT ESTABLISHED |
| Candidate capabilities or suitability | NOT EVALUATED |

A GitHub 404 does not distinguish a missing repository from a private repository or an access/slug problem. The source must be resolved before any technical evaluation. Do not add a fabricated graph node or research seed for an inaccessible candidate.

## 2. Existing discovery and intake surfaces

### Repository Observatory — already exists

- Collector: scripts/github/repository_observatory.py
- Workflow: .github/workflows/repository-observatory.yml
- Canonical index: workspace/llm_map/repositories/repository-index.json
- Human projection: docs/repositories/matrix.md
- Schema: docs/repositories/repository-observatory.schema.json
- Documented provenance includes owned, starred and watching; fork is retained as a role/upstream relationship.
- Deterministic classifications include domains, role, research value, integration candidates and a submodule_candidate inference.
- Snapshot deltas include added, removed and provenance-changed repositories.
- The collector explicitly describes stars/forks/watches as research signals, not adoption orders.

This is an existing sensing layer, not yet proof that every observed candidate is evaluated or routed into CEEL/refTemplates.

### Research-seed intake — already exists

- Research trigger map: docs/ops/RESEARCH-TRIGGERS.md
- Issue parser: scripts/research/research_intake.py
- Observatory issue intake: scripts/github/observatory_intake.py
- Seed records: docs/repositories/research-seeds/*.json
- Existing research issue labels/templates include research:provider and research:service.
- The documented {seed}{starter} record carries source identity, provenance, classification, observed facts, capability signals and integration constraints.

This should remain the intake format. Do not create a competing seed schema.

### CEEL — already owns opportunity discovery

- Proposal: docs/proposals/active/continuous-capability-evolution-lab/
- Specification: docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md
- Canonical capability graph: docs/integrations/capability-opportunity-graph.json
- Graph schema and deterministic validator already exist.
- CEEL's Novel Feature Search explicitly covers internal demand, external change, cross-lane capabilities and measured outcomes.
- Its lifecycle separates discovered, classified, mapped, proposed, admitted, experimentally validated, integration candidate, integrated and monitored states.

This proposal does not create a second capability-discovery system. It closes the handoff from existing Observatory/research-seed signals into CEEL's existing graph and lifecycle.

### Context Relationship Graph

Use CRG to connect candidates to exact repository files, commits, PRs, issues and prior decisions. Keep directly evidenced relationships verified and heuristic similarity/co-change relationships candidate. Do not persist PR/issue/review/comment bodies or infer ownership/causality from names.

## 3. refTemplates and smods — existing promotion surfaces

- refTemplates/00_Index/README.md and SOURCE-MAP.md are the navigation/source map.
- refTemplates/15_Research_Repo_Templates/ is the metadata-first research-template reference class.
- refTemplates/16_Org_Phased/ is the phased organization/enterprise lane.
- refTemplates/smods/ is the live custom-adapted gitlink lane.
- docs/ops/REFTEMPLATES-CONSOLIDATION.md states that the current tree is a narrow slice, full recursive materialization is rare/explicit, and live pins require a reviewed immutable revision and passing gates.
- docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md requires source metadata, shallow gitlinks, resolvable source URLs, no hardcoded keys, inventory checks and dual-gate validation.
- docs/ops/RESEARCH-INTEGRATION-LANE.md distinguishes metadata references, pattern-only reuse and live custom-fork pins. A star is not a clone order.

Therefore the default candidate disposition is metadata/research-only. A new smods/ gitlink is the exceptional path, not the default result of discovery.

## 4. Proposed end-to-end path

Repository Observatory / research issue intake / external change events
                              |
                              v
                  Existing research-seed record
                              |
                              v
             CEEL capability normalization + dedupe
                              |
                              v
            Context Relationship Graph evidence links
                              |
                              v
         Consumer mapping + source/license/security review
                              |
                              v
                Explicit candidate disposition
                   /          |          \
             watch/pattern  15_* metadata  custom fork
                                             |
                                             v
                                     refTemplates/smods
                                  shallow immutable gitlink
                                             |
                                             v
                                   compatibility + dual gate

The existing GitHub event plane is primary. Use current Observatory, issue-intake, integration-portfolio and bounded reconciliation paths. Do not add a weekly discovery cron, second queue, or generic event bus.

## 5. Candidate decision dimensions

For each accessible source, collect facts before scoring:

1. Identity and provenance: canonical upstream, fork parent, exact URL, default branch, observed revision/tag, retrieval timestamp and source type.
2. Capability contract: behavior offered, input/output boundary, dependencies, APIs, workflows, tests and evidence.
3. Internal fit: named consumer, current gap, overlap with existing components, integration owner and measurable expected outcome.
4. Maintenance: release recency, commit/issue activity, maintainer concentration, archive status and compatibility cadence.
5. Trust: license and notices, dependency/advisory review, provenance, build/release integrity, permissions, network egress and data handling.
6. Adoption cost: adaptation/fork delta, upgrade burden, runtime/resource footprint, operational complexity and lock-in.
7. Composition: competing alternatives, complements and interaction hypotheses; compare combinations only where a consumer and testable outcome exist.

Use a Pareto view across capability gain, quality, cost, risk, compatibility and maintenance. Any scalar ranking must disclose weights and sensitivity. Missing data remains unknown, not zero.

## 6. Disposition contract

| Disposition | Destination | Minimum evidence |
|---|---|---|
| Reject / defer | CEEL graph disposition only | Reason, source and reconsideration trigger |
| Watch | Observatory/research-seed reference | Canonical source and provenance |
| Pattern-only | Research note or relevant 15_* slot | Extractable method/pattern, license and source citation |
| Metadata reference | refTemplates/15_Research_Repo_Templates/<slot>/ | README.md, SOURCE.txt, purpose, capability signals, constraints and owner |
| Custom-fork candidate | Separate fork proposal; not yet a gitlink | Proven upstream, justified customization delta, license and maintenance plan |
| Live custom fork | refTemplates/smods/<name>_fork | User-owned fork, immutable reviewed pin, shallow gitlink, source map, compatibility/security tests and dual-gate evidence |

No disposition automatically executes external code, clones a full repository, updates a submodule, creates secrets, or changes production routing.

## 7. Sources inspected

- docs/repositories/README.md
- docs/social/X-OBSERVATORY.md
- scripts/github/repository_observatory.py
- scripts/github/observatory_intake.py
- docs/ops/RESEARCH-TRIGGERS.md
- docs/repositories/research-seeds/gravitee-api-management.json
- docs/repositories/research-seeds/temporalio-temporal-set.json
- docs/superpowers/specs/2026-11-11-continuous-capability-evolution-lab.md
- docs/integrations/CEEL-EVENT-CONTRACT.md
- docs/ops/REFTEMPLATES-CONSOLIDATION.md
- docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md
- docs/ops/RESEARCH-INTEGRATION-LANE.md
- refTemplates/00_Index/README.md
- refTemplates/00_Index/SOURCE-MAP.md
- .gitmodules
- docs/proposals/PROCESS.md
- docs/proposals/AGENTIC-PERMISSIONS.md

The repository's live files are authoritative. The proposal is an implementation plan, not evidence that the bridge or target integration has shipped.
