# Design Surface Map — Source Inventory

## Intent

Establish a repository-native design documentation estate that maps user-facing product surfaces independently from the architecture taxonomy. Each owned system receives a local `design.md`; cross-system design disciplines live in shared references.

## Repository evidence

- `architecture.md` defines seven architectural responsibility planes and routes readers to owning contracts. Its taxonomy is architectural, not a design-system inventory.
- `docs/icm/CLAUDE.md` routes contributors through source-owned ICM cards and identifies platform, operations, and knowledge surfaces.
- `apps/tribute-dashboard/README.md` and `apps/tribute-dashboard/dashboard.css` provide an existing dashboard design implementation.
- `docs/ops/SHE-DASHBOARD-PRD.md` and `docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md` define SHE requirements and data presentation boundaries.
- `docs/proposals/active/ratatui-tokio-terminal-dashboard/ITEMS.md` defines terminal dashboard behavior and implementation evidence.
- `docs/proposals/active/archwiz-ui-protocol/ITEMS.md` defines ArchWiz UI/client protocol concerns.
- `docs/proposals/active/model-selection-market/DESIGN.md` is the existing Model Selection Market design source.
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` owns agent orchestration behavior.
- `docs/architecture/termux-agentic-hub.md` owns the Termux Agentic Hub capability boundary.
- `docs/integrations/README.md` and `docs/ops/SKILLS-INVENTORY.md` provide developer/integration surface references.
- `docs/ops/CHART-STANDARD`, palette, and interaction references remain individually authoritative where linked.

## Scope

Create a design index, reusable system template, shared design references, and source-grounded design entries for eight repository surfaces. Each entry distinguishes implemented, proposed, and candidate evidence, and links to canonical implementation and contract sources.

## Explicit exclusions

- Reclassifying or rewriting the seven-plane architecture taxonomy.
- Replacing domain specifications, source code, schemas, protocols, or existing design sources.
- Creating new UI behavior, visual assets, component libraries, or runtime code.
- Publishing to external documentation or asset services.
- Declaring inferred design choices as approved product decisions.

## Evidence policy

Every system entry links to its current source of truth. Missing design decisions remain explicit gaps for future work; inferred details are labeled as candidates.
