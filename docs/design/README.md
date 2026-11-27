# Design Surface Map

**Purpose:** map how people use the repository's products, operator interfaces, dashboards, terminal experiences, and developer-facing surfaces.

**Authority:** this index routes readers to system-owned design records and canonical source documents. It does not replace architecture, implementation, schemas, protocols, or existing product specifications.

## Design ≠ architecture

[`architecture.md`](../../architecture.md) describes seven architectural responsibility planes: execution/device, agent control/orchestration, provider/integration, evidence/data, intelligence/learning, user surfaces/projections, and governance/delivery.

This directory uses a different organizing axis: **the experience presented to a user or operator**. One design surface can span multiple architecture planes; one architecture plane can support several design surfaces.

## System directory

| System | Design entry | Evidence status | Canonical source anchors |
|---|---|---|---|
| Tribute Dashboard | [systems/tribute-dashboard/design.md](systems/tribute-dashboard/design.md) | Implemented | [README](../../apps/tribute-dashboard/README.md), [CSS](../../apps/tribute-dashboard/dashboard.css) |
| SHE Dashboard | [systems/she-dashboard/design.md](systems/she-dashboard/design.md) | Specified / evolving | [PRD](../ops/SHE-DASHBOARD-PRD.md), [snapshot contract](../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) |
| Terminal Experience | [systems/terminal-experience/design.md](systems/terminal-experience/design.md) | In progress | [proposal items](../proposals/active/ratatui-tokio-terminal-dashboard/ITEMS.md) |
| ArchWiz | [systems/archwiz/design.md](systems/archwiz/design.md) | Proposed / partially implemented | [UI protocol items](../proposals/active/archwiz-ui-protocol/ITEMS.md), [ICM ArchWiz card](../icm/objects/operations/archwiz.md) |
| Termux Agentic Hub | [systems/termux-agentic-hub/design.md](systems/termux-agentic-hub/design.md) | Capability boundary defined | [Hub architecture](../architecture/termux-agentic-hub.md), [ICM platform card](../icm/objects/platform/termux-agentic-hub.md) |
| Agent Orchestration | [systems/agent-orchestration/design.md](systems/agent-orchestration/design.md) | Architecture defined; experience gaps remain | [Agent Team Control Plane](../architecture/AGENT-TEAM-CONTROL-PLANE.md) |
| Model Selection Market | [systems/model-selection-market/design.md](systems/model-selection-market/design.md) | Existing design source | [Canonical DESIGN.md](../proposals/active/model-selection-market/DESIGN.md) |
| Developer Experience | [systems/developer-experience/design.md](systems/developer-experience/design.md) | Candidate surface / source inventory | [Integrations](../integrations/README.md), [skills inventory](../ops/SKILLS-INVENTORY.md) |

Evidence labels:
- **Implemented:** current implementation and design references exist.
- **Specified / evolving:** a product brief or contract defines material parts of the experience.
- **In progress / proposed:** a registered proposal defines the surface or its behavior.
- **Candidate:** source material identifies a relevant surface; a full experience contract remains to be established.

## Shared design references

| Discipline | Reference | Role |
|---|---|---|
| Visual language | [visual-language.md](_shared/visual-language.md) | Existing visual tokens and visual-system ownership |
| Interaction patterns | [interaction-patterns.md](_shared/interaction-patterns.md) | Shared interaction contracts and state vocabulary |
| Accessibility | [accessibility.md](_shared/accessibility.md) | Accessibility requirements and evidence gaps |
| Data visualization | [data-visualization.md](_shared/data-visualization.md) | Charts, snapshots, provenance, freshness, and uncertainty |

Shared references capture reusable conventions and link to their owners. System entries retain local deviations and context.

## Per-system design record

Each system owns a `design.md` following the [template](_template/design.md). The record covers:

1. Purpose, users, and user outcomes.
2. User-facing surfaces and entry points.
3. Information architecture and navigation.
4. Journeys, interactions, and state transitions.
5. Visual language and component references.
6. Accessibility and responsive constraints.
7. Evidence, trust, freshness, and failure states.
8. Canonical sources, ownership, decisions, and open gaps.

## Ownership and source-of-truth rules

- Preserve domain source documents, code, schemas, protocols, and tests as the authority for their respective facts.
- Use each design entry to summarize and link; preserve the owning specification as authoritative.
- Record design decisions with source links and status: **confirmed**, **proposed**, **candidate**, or **unknown**.
- Keep architecture-plane references separate from experience taxonomy.
- Add a system entry when a distinct user/operator experience has an identifiable owner and source trail.
- Keep external products/repositories as linked references until an explicit local ownership decision exists.

## Maintenance

Update a system entry alongside material UX changes in its owning proposal or product contract. Review cross-system references when shared tokens, interaction contracts, or accessibility guidance changes. Use source-backed diffs and validate links before landing.
