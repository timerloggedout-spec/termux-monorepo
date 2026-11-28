# Engineering Toolchain Integration — source and relationship record

## Operator scope

The request covers the complete engineering stack previously researched and its active routing through QUE, QDesk, ArchWiz, refTemplates, DoE/MVT, Reverse Engineering, Learnings and matrices.

## Existing repository authorities

| Concern | Canonical authority | Integration decision |
|---|---|---|
| External tool catalog | `docs/integrations/registry.json` | Add one engineering-toolchain integration row; keep all integration states explicit |
| Engineering taxonomy | `ops/engineering/taxonomy.json` | New sibling domain registry |
| Reverse Engineering | `ops/reverse_engineering/taxonomy.json` | Preserve RE-only root and validator; link by artifacts and evidence |
| Device execution | `hub_mcp/policy.py`, `hub_mcp/protocol.py`, `hub_mcp/runner.py` | Add fixed named capabilities; preserve argv-only execution and replay protection |
| Operator surface | `archwiz/TOOL_INDEX.md`, `.agents/skills/` | Add discoverability while preserving the existing executor |
| Queue and review | QUE/QDesk contracts | Reuse existing admission, rank, claim, lease, escalation and Desk |
| Measurement | Agent Evaluation Framework, DoE family, MVT, ATES | Use canonical experiment identity and outcome semantics |
| Learnings | Existing Learnings lane and continuous-improvement policy | Record verified setup and tool behavior only |
| Templates | `refTemplates/` | Pin source/version/license and record adaptation before adoption |

## Tool coverage

Mechanical: FreeCAD, OpenSCAD, SolveSpace, LibreCAD; Onshape Free is a proprietary $0 cloud tier with public-document/non-commercial constraints; its Free-plan card requirement is unconfirmed by the pricing page. SOLIDWORKS for Makers is paid ($48/year or $15/month before tax), personal/non-commercial, and available through paid subscriptions; commercial SOLIDWORKS licensing is separate.

Electronics/electrical: KiCad, LibrePCB, QElectroTech, ngspice and Qucs-S.

Simulation: Gmsh, CalculiX, Elmer, OpenFOAM, openEMS, FEniCSx and SALOME.

Semiconductor: Yosys, OpenROAD and KLayout.

Technical visualization: Blender, linked to the existing 3D asset pipeline.

## refTemplates placement

The repository ignores `refTemplates/` by policy. This proposal keeps upstream project metadata in `docs/ops/ENGINEERING-REFERENCE-SET.json` and uses `refTemplates/engineering/` only as a local, gitignored shallow-clone workspace. Source revisions remain unpinned until a specific reference is adopted through the documented review path.

## FOSS and access policy

Local FOSS applications are free to obtain and run under their respective licenses; commercial-use rights follow each license and upstream dependency. Cloud-free tiers are recorded separately from FOSS. A free tier with public documents or non-commercial limits remains classified as proprietary. The FOSS baseline uses local open-source applications; paid proprietary products serve as interoperability targets. Card requirements are recorded as false, true or unknown from evidence.

## Termux execution model

Termux is the lightweight control plane. The initial hub integration validates the taxonomy and probes command availability without launching GUI applications or running arbitrary commands. FreeCAD, KiCad, full CAD/CAE solvers and semiconductor flows are treated as remote-runner candidates until a device-specific install and resource test proves local suitability.

## Loopy adaptation

The repository-native feedback loop remains authoritative: Observe → Contextualize → Adapt → Implement → Verify → Record → Recompare → Repeat. The six-step Loopy mechanics are applied inside this loop: Observe → Choose → Act → Verify → Record → Repeat. Each run has bounded scope, current-state re-read, measurable progress and a named terminal state: success, clean-no-op, blocked, approval-required, exhausted or stagnated. Loop design remains separate from execution and scheduling.
