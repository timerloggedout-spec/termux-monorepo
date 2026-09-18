# Paper2Agent → Agent-Native Knowledge Architecture

**Status:** Research-derived architecture proposal  
**Source date:** 2026-09-16  
**Primary source:** Miao et al., Nature (2026), “Reimagining research papers as interactive and reliable AI agents”  
**Repository:** timerloggedout-spec/termux-monorepo

## Executive summary

The Stanford Paper2Agent work suggests a useful architectural shift for this repository:

> **Do not treat documentation, research, workflows, evidence, and code as passive context. Treat validated knowledge artifacts as typed, provenance-bearing, tool-capable resources that agents can discover and use.**

This does **not** mean turning every Markdown file into an autonomous agent. The transferable idea is the **agent-native knowledge contract**: structured resources, validated capabilities, provenance, reproduction before trust, typed agent interoperability, explicit human context, and evidence-based measurement.

Paper2Agent converts research papers plus associated code/data/workflows into MCP-backed agents. Its workflow uses specialized agents for environment setup, extraction, and testing; it validates tools against reference behavior and excludes tools that repeatedly fail validation. The paper reports that resulting agents can reproduce analyses, answer new questions, and collaborate with other paper agents. citeturn1search0

## 1. Active knowledge artifacts

Our repository already has a large evidence/documentation surface: orchestration specifications, experiment lineage, action/effect records, runtime observations, context-relationship data, skills, and research matrices.

Paper2Agent exposes research output through three MCP-oriented layers:

- **tools** — executable capabilities;
- **resources** — authoritative static/contextual assets;
- **prompts/workflows** — structured procedures for using the resources and tools.

The paper explicitly describes these as the core components of a paper MCP. citeturn1search0

Apply the same separation here:

~~~text
Repository Knowledge Artifact
├── resources
│   ├── source document
│   ├── code / workflow
│   ├── evidence
│   ├── provenance
│   └── decision history
├── capabilities
│   ├── read
│   ├── validate
│   ├── reproduce
│   ├── analyze
│   └── propose
└── procedures
    ├── prompt/workflow
    ├── preconditions
    ├── validation contract
    └── escalation policy
~~~

This is stronger than simply placing more text into an agent context window.

## 2. Reproduce before granting trust

Paper2Agent configures an environment, extracts executable methods, generates tests, runs them against reference behavior, diagnoses failures, and iterates. Tools that repeatedly fail validation are excluded. citeturn1search0

That maps directly onto the repository's existing operating loop:

~~~text
RECON
→ PLAN / MEASURE
→ ACT
→ COMMIT
→ WAIT
→ WATCH
→ VALIDATE
→ RE-FETCH
→ COMPARE
→ CLASSIFY
→ RECORD
→ REPEAT
~~~

The repository already treats queued/in-progress as distinct from validated and promoted states. The Paper2Agent result strengthens the case for making **validation a capability admission gate**, not merely a post-hoc report.

## 3. Provenance survives agent collaboration

Paper2Agent emphasizes traceability back to original code and research sources. Stanford's report also explicitly notes that attribution must survive downstream agent collaboration. citeturn0view0

That reinforces the project's existing distinction:

~~~text
GitHub identity ≠ agent identity
~~~

and its provenance model based on workflow run/job/step, triggering event, issue/PR, SHA, timestamps, provider/model telemetry, session/export provenance, and attribution confidence. fileciteturn0file1L68-L105

A knowledge capsule should therefore carry:

~~~text
artifact_id
source_ref
source_sha
artifact_type
capability_set
validation_receipt
provenance_chain
freshness
confidence
policy_scope
~~~

No agent should silently inherit authority merely because it can read an artifact.

## 4. Human tacit knowledge becomes a first-class resource

Stanford's description highlights an important limitation: automated reconstruction cannot recover every failed experiment, judgment call, or contextual decision, so human authors must supply that missing context. citeturn0view0

For this repository, preserve:

- why a routing policy changed;
- why a workflow was intentionally cancelled;
- why a metric is null instead of zero;
- why a run is classified as model/provider/orchestration/code/environment/network failure;
- why promotion was withheld;
- which assumptions remain unverified.

These should not be buried in chat history.

Proposed resource type:

~~~text
DecisionRecord
├── decision_id
├── subject
├── decision
├── rationale
├── alternatives_considered
├── evidence_refs[]
├── actor
├── actor_type
├── timestamp
├── confidence
├── supersedes[]
└── review_status
~~~

This complements the existing evidence index and experiment lineage.

## 5. Virtual CSO = governance/orchestration role, not one super-agent

The useful lesson is **not** that the project needs one model that knows everything.

Implement a **Virtual Chief Scientific Officer role** as a governance/orchestration layer over specialized knowledge agents:

~~~text
                 VIRTUAL CSO
                     │
          ┌──────────┼──────────┐
          │          │          │
       DISCOVERY   METHODS    EVIDENCE
          │          │          │
      research    repro/CI    telemetry
       agents      agents      agents
          │          │          │
          └──────────┼──────────┘
                     │
              CONTEXT GRAPH
                     │
              DECISION LEDGER
                     │
              MANAGER POLICY
                     │
              EXECUTION LANES
~~~

The role answers:

- What do we know?
- What evidence supports it?
- Which artifact/capability can answer this?
- Is it fresh and validated?
- Which specialist should act?
- What must be reproduced?
- What remains uncertain?
- What human decision is required?
- What changed after execution?

It is **not** a privileged oracle.

## 6. Knowledge Agent Capsules

Introduce a lightweight **Knowledge Agent Capsule (KAC)** contract.

A KAC is an agent-facing representation of one bounded knowledge domain: a research method, repository subsystem, workflow, experiment cohort, metric definition, graph slice, synchronization domain, or evidence bundle.

Minimum contract:

~~~yaml
kind: knowledge-agent-capsule
schema_version: 1
id: <stable-id>
source:
  uri: <source>
  ref: <branch/tag/sha>
  digest: <optional-content-digest>
capabilities:
  - read
  - analyze
  - validate
  - reproduce
resources:
  - <resource references>
procedures:
  - <workflow references>
validation:
  status: validated|partial|unvalidated|failed
  receipt: <evidence reference>
provenance:
  lineage: []
  attribution_confidence: 0.0
freshness:
  observed_at: <timestamp>
policy:
  read_only: true
  write_authority: none
~~~

The exact schema should be reconciled with the existing notation registry and context-relationship contracts before implementation; this proposal intentionally does not duplicate those schemas.

## 7. Context-relationship graph integration

KAC should become a node class in the existing relationship graph rather than another disconnected index:

~~~text
ResearchPaper
   │
   ├── IMPLEMENTED_BY → Repository
   ├── VALIDATED_BY → Experiment
   ├── EXPOSED_AS → MCP
   ├── USED_BY → Agent
   └── PRODUCES → Evidence

Repository
   │
   ├── EXECUTED_IN → Environment
   ├── OBSERVED_BY → WorkflowRun
   ├── REVIEWED_BY → Review
   └── SUPERSEDES → PriorRevision
~~~

This lets the manager discover relationships, not merely filenames.

## 8. Capability admission

Separate:

~~~text
DISCOVERED
   ↓
PARSED
   ↓
REPRODUCIBLE
   ↓
VALIDATED
   ↓
ADMITTED
   ↓
EXECUTABLE
~~~

A resource may be useful without being executable. A tool may be executable without being trusted for autonomous writes.

This fits the existing distinction between committed, executed, validated, and promoted states. The project has already documented that these states must remain independent. fileciteturn0file2L21-L34

## 9. Typed agent-to-agent collaboration

Paper2Agent demonstrates collaboration by allowing independently represented research methods/data resources to interact. citeturn1search0

Use typed handoffs rather than free-form agent chatter:

~~~json
{
  "handoff_id": "...",
  "from_capsule": "...",
  "to_capsule": "...",
  "objective": "...",
  "inputs": [],
  "constraints": [],
  "evidence_refs": [],
  "expected_output": "...",
  "validation_required": true,
  "write_authority": "none"
}
~~~

Every handoff becomes an observable action/effect candidate and can therefore feed ATES/WTCV/3L0.

## 10. Capability catalog instead of model leaderboard

The routing/index work can evolve from a model catalog into a **capability catalog**.

Instead of only:

~~~text
Gemini
Jules
OpenRouter
DeepSeek
~~~

discover:

~~~text
capability
├── agent/provider candidates
├── validated tools
├── cost
├── latency
├── environment requirements
├── evidence quality
├── historical success
├── attribution confidence
└── policy constraints
~~~

This is consistent with the existing team-centric objective: evaluate orchestration policies and integrated outcomes rather than treating one model as a permanent primary. fileciteturn0file1L123-L162

## 11. Safety and authority lattice

Paper2Agent explicitly calls for guided and monitored collaboration parameters. citeturn0view0

For this project:

~~~text
L0  OBSERVE
L1  READ / QUERY
L2  ANALYZE / REPRODUCE
L3  PROPOSE
L4  PREPARE PATCH
L5  WRITE IN SANDBOX
L6  WRITE REPOSITORY
L7  PROMOTE / MERGE
~~~

Validation should never automatically imply merge authority.

## 12. Measurement implications

The unit of analysis should increasingly be:

~~~text
manager policy
    ×
knowledge capsules
    ×
agent handoffs
    ×
execution evidence
    ×
integrated outcome
~~~

Useful measures:

- discovery-to-use latency;
- reproduction success;
- validation iterations;
- handoff latency;
- duplicate work;
- conflicting actions;
- evidence completeness;
- attribution confidence;
- context consumed;
- tool reuse;
- human intervention;
- final acceptance;
- rollback/rework.

This is compatible with the project's existing integrated ROI definition rather than a simple cost or model leaderboard. fileciteturn0file1L20-L34

## 13. Implementation sequence

### P0 — contract and graph

1. Define KAC as a schema proposal.
2. Map KAC fields to the existing context-relationship graph.
3. Reuse existing provenance/evidence schemas.
4. Define capability admission states.
5. Define typed handoff events.

### P1 — first capsule pilots

Start with:

- AGENT-TEAM-ORCHESTRATION;
- the runtime watcher/reconciliation skill;
- the action/effect ledger;
- one reproducible research experiment;
- one workflow/evidence bundle.

No autonomous repository writes initially.

### P1 — validation harness

For every executable capability:

~~~text
extract
→ environment
→ reproduce reference
→ test
→ diagnose
→ repair
→ re-test
→ admit or exclude
~~~

This is the most important Paper2Agent pattern to import.

### P2 — agent-to-agent experiments

Run controlled cohorts:

~~~text
method capsule
      +
data/evidence capsule
      ↓
typed handoff
      ↓
analysis
      ↓
validation
      ↓
new evidence
~~~

Compare sequential, parallel, and manager-mediated orchestration using the existing evidence system.

### P2 — Virtual CSO prototype

Implement the CSO as a policy/coordination layer that:

- discovers capsules;
- checks evidence and freshness;
- dispatches specialists;
- records decisions;
- blocks unauthorized writes;
- requires validation for executable claims;
- produces an evidence-indexed synthesis.

## 14. Explicit non-goals

This proposal does **not** recommend:

- turning every document into an autonomous agent;
- allowing agents to self-authorize writes;
- treating generated summaries as authoritative evidence;
- replacing Git history with agent memory;
- collapsing provider/model identity into capability identity;
- using a single dashboard score as proof of scientific correctness;
- claiming Paper2Agent's reported results automatically generalize to software-engineering agents.

The transferable lesson is the architecture: **validated, executable, provenance-bearing knowledge units that can interoperate through a common protocol.**

## Research provenance

Miao, J. et al. *Reimagining research papers as interactive and reliable AI agents*. Nature (2026), published 16 September 2026. DOI: 10.1038/s41586-026-11044-y. citeturn1search0

Stanford Medicine's accompanying report describes the reproduction-first worker-agent process, MCP representation, agent-to-agent collaboration, attribution requirements, and the need for human-supplied tacit context. citeturn0view0

## Relationship to existing project work

This proposal extends—not replaces—the existing team-centric orchestration model. The repository already distinguishes agent identity from GitHub identity, records provenance and attribution confidence, and measures orchestration as an integrated system. fileciteturn0file1L68-L105

It also fits the existing runtime methodology of waiting, watching, validating, re-fetching, comparing, classifying, recording, and repeating. fileciteturn0file2L11-L34

The intended evolution is:

~~~text
static docs
   ↓
structured evidence
   ↓
context graph
   ↓
knowledge capsules
   ↓
validated capabilities
   ↓
typed agent handoffs
   ↓
manager / Virtual CSO
   ↓
measured autonomous team
~~~

**Principle:** make knowledge executable only after making its provenance and validation executable too.
