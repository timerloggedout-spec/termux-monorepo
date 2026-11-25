# Repository architecture entry — work items

**Proposal:** repository-architecture-entry  
**Scope:** documentation navigation, architecture taxonomy, and repository data-flow map.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| REPO-ARCH-001 | Establish root `architecture.md` with ToC, system taxonomy, directory taxonomy, data-flow entities / origins / producers / transformations / stores / consumers, and canonical source links. | Markdown structure and internal links checked; source ownership called out. | Implemented |
| REPO-ARCH-002 | Publish the consolidated Mermaid data-flow source under `docs/ops/diagrams/`. | Mermaid syntax validation and link target verification. | Implemented |
| REPO-ARCH-003 | Register the architecture entry in root collaborator instructions, ICM routing, README navigation, and architecture index. | All entry-point links resolve to the root architecture entry. | Implemented |
| REPO-ARCH-004 | Run repository gates and reconcile any failures before promotion. | `repo_gate.py`, `termux_smoke.py`, and required CI checks pass with recorded SHA. | Pending |
| REPO-ARCH-005 | Add linked modular subsystem maps, paired Markdown / Mermaid views, and update existing Mermaid.ai root diagram in place. | Six detailed maps, six Mermaid sources, root links and stable diagram identity. | Implemented |
| REPO-ARCH-006 | Audit snapshot freshness and dangling/siloed paths, including ArchWiz local data-flow manifest. | Source-backed gap report and timestamp/provenance requirements. | Implemented |
| REPO-ARCH-007 | Establish a central Flywheel navigation hub with nested channel and topic routes that connect verified work concepts to canonical protocols, stores, documents, GitHub issues/PRs, commits, tests, and evidence. Reconcile FLY-005's explicit pointer to FLY-006 and preserve each channel's scope and source-of-truth boundary. | Hub covers registered FLY-001…FLY-006; FLY-005 → FLY-006 pointer resolves to the actual work record; topic routes carry verified artifact links and confidence labels; root architecture and ICM route to the hub; all internal links resolve; no channel payload duplication or parallel relationship database. | Executing |
