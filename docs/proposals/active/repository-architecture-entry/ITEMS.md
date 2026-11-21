# Repository architecture entry — work items

**Proposal:** repository-architecture-entry  
**Scope:** documentation navigation, architecture taxonomy, and repository data-flow map.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| REPO-ARCH-001 | Establish root `architecture.md` with ToC, system taxonomy, directory taxonomy, data-flow entities / origins / producers / transformations / stores / consumers, and canonical source links. | Markdown structure and internal links checked; source ownership called out. | Implemented |
| REPO-ARCH-002 | Publish the consolidated Mermaid data-flow source under `docs/ops/diagrams/`. | Mermaid syntax validation and link target verification. | Implemented |
| REPO-ARCH-003 | Register the architecture entry in root collaborator instructions, ICM routing, README navigation, and architecture index. | All entry-point links resolve to the root architecture entry. | Implemented |
| REPO-ARCH-004 | Run repository gates and reconcile any failures before promotion. | `repo_gate.py`, `termux_smoke.py`, and required CI checks pass with recorded SHA. | Pending |
