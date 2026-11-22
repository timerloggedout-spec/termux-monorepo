# Repository architecture entry — work items

**Proposal:** repository-architecture-entry  
**Scope:** architecture navigation, taxonomy, data-flow maps, semantic versioning, and generated documentation evidence.

| ID | Work item | Acceptance evidence | State |
|---|---|---|---|
| REPO-ARCH-001 | Establish root `architecture.md` with ToC, system taxonomy, directory taxonomy, data-flow entities / origins / producers / transformations / stores / consumers, and canonical source links. | Markdown structure and internal links checked; source ownership called out. | Implemented |
| REPO-ARCH-002 | Publish the consolidated Mermaid data-flow source under `docs/ops/diagrams/`. | Mermaid syntax validation and link target verification. | Implemented |
| REPO-ARCH-003 | Register the architecture entry in root collaborator instructions, ICM routing, README navigation, and architecture index. | All entry-point links resolve to the root architecture entry. | Implemented |
| REPO-ARCH-004 | Run repository gates and reconcile any failures before promotion. | `repo_gate.py`, `termux_smoke.py`, and required CI checks pass with recorded SHA. | Pending |
| REPO-ARCH-005 | Add linked modular subsystem maps, paired Markdown / Mermaid views, and update existing Mermaid.ai root diagram in place. | Six detailed maps, six Mermaid sources, root links and stable diagram identity. | Implemented |
| REPO-ARCH-006 | Audit snapshot freshness and dangling/siloed paths, including ArchWiz local data-flow manifest. | Source-backed gap report and timestamp/provenance requirements. | Implemented |
| REPO-ARCH-007 | Establish semantic architecture versioning, deterministic source/render manifest, and automated diagram refresh through the existing documentation workflow. | SemVer gate and changelog validation; focused tests; source/render SHA-256 manifest; architecture flow SVGs; PR evidence artifact; trusted master refresh. | In review |
