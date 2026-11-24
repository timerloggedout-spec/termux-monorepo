# Design Surface Map — Work Items

| ID | Priority | Status | Scope | Acceptance evidence |
|---|---:|---|---|---|
| DSM-001 | P1 | executing | Establish the design documentation index, taxonomy, ownership rules, and navigation. | `docs/design/README.md` clearly distinguishes design surfaces from architecture planes and links all system entries. |
| DSM-002 | P1 | executing | Add a reusable per-system `design.md` template and shared cross-system design references. | Template defines user, surface, IA, interaction, visual, accessibility, evidence-state, source, and gap sections; shared docs cite existing sources. |
| DSM-003 | P1 | executing | Create source-grounded design entries for eight mapped systems. | Each entry states evidence status, links canonical sources, records known experience contracts, and marks unknowns as gaps. |
| DSM-004 | P1 | executing | Validate documentation structure, local links, and repository gates. | Link/path checks plus `repo_gate.py` and `termux_smoke.py` outcomes recorded against the final commit SHA. |

## Non-goals

- Rewrite architecture or ICM ownership.
- Replace existing system designs or implementation contracts.
- Introduce product behavior or visual decisions unsupported by source evidence.
- Publish or synchronize external documentation/assets.
