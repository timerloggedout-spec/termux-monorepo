# Engineering Domain — CAD, electronics, simulation and making

**Status:** proposal
**Owner/lane:** Engineering Toolchain Integration
**Canonical for:** proposed engineering-domain taxonomy, toolchain stages and execution boundaries
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

## Purpose

Establish Engineering as a first-class domain for mechanical design, electronics, electrical systems, computational simulation, manufacturing and semiconductor development. Engineering and Reverse Engineering retain independent sibling ownership. Shared hardware, firmware, artifact and evidence relationships use explicit cross-domain links.

## Canonical sources

- Machine taxonomy: `ops/engineering/taxonomy.json`
- Validator/query: `ops/engineering/taxonomy.py`
- Read-only Termux probe: `scripts/engineering/toolchain_probe.py`
- Operator matrix: `docs/ops/ENGINEERING-TOOLCHAIN-MATRIX.md`
- Queue contract: `docs/ops/ENGINEERING-QUE-QDESK-CONTRACT.md`
- DoE/MVT plan: `docs/ops/ENGINEERING-DOE-MVT-PLAN.md`
- Cross-domain matrix: `docs/ops/ENGINEERING-RE-REFERENCE-MATRIX.md`
- Learnings matrix: `docs/ops/ENGINEERING-LEARNINGS-MATRIX.md`
- Reference catalog: `docs/ops/ENGINEERING-REFERENCE-SET.json`; local checkout path: `refTemplates/engineering/` (gitignored)
- Remote runner profile: `docs/ops/ENGINEERING-REMOTE-RUNNER-PROFILE.md`
- refTemplates references: `refTemplates/engineering/references.json` (reference-only; pin before adoption)

## Domain hierarchy

- Mechanical engineering: parametric CAD, code-defined CAD, assemblies, technical drafting, tolerancing, CAM and inspection.
- Electronics engineering: schematic capture, PCB layout, circuit simulation, hardware verification and bring-up.
- Electrical engineering: wiring, electrical diagrams, power/control systems and industrial automation.
- Computational engineering: FEA, CFD, electromagnetics, thermal analysis, meshing and multiphysics.
- Manufacturing engineering: additive/subtractive preparation, CNC, 3D printing, PCB fabrication and quality inspection.
- Semiconductor engineering: RTL synthesis, place-and-route, layout, DRC/LVS and GDSII.
- Technical visualization: Blender and interoperable 3D asset derivatives.

## Toolchain principles

1. Source files are authoritative; neutral exports are interchange artifacts.
2. Toolchains express ordered stage handoffs with explicit dependencies and artifacts.
3. Every run binds tool/version, source SHA, input hashes, environment fingerprint, parameters, output hashes, validation and provenance.
4. Tool discovery, local installation, authenticated access, execution, validation and promotion are distinct states.
5. FOSS, proprietary free tiers and paid proprietary products are separate classes.
6. Design and simulation results require separate certification, safety approval and manufacturing authorization.

## Execution topology

```text
QUE admission → QDesk claim / lease → ArchWiz operator context
                         |
                         v
                 Termux Agentic Hub
                 ├─ taxonomy validation
                 ├─ read-only local tool probe
                 └─ approved runner handoff
                         |
                         v
        FOSS CAD / EDA / CAE / RTL toolchain
                         |
                         v
       portable artifacts + validation + provenance
                         |
                         v
            DoE/MVT evaluation → Learnings
```

Termux remains a thin controller. GUI and compute-heavy tools require a separately approved remote Linux runner until local device support is measured. Existing QUE/QDesk and hub authority boundaries remain unchanged.
