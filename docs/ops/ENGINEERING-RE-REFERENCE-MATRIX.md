# Engineering ↔ Reverse Engineering Reference Matrix

**Status:** proposal
**Owner/lane:** Engineering Toolchain Integration + Reverse Engineering
**Canonical for:** cross-domain engineering/RE relationships and reference-source handoffs
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

| Engineering artifact | Related RE surface | Shared evidence | Ownership |
|---|---|---|---|
| PCB, schematic, netlist | Hardware-assisted targets, protocol/format analysis | board revision, netlist hash, bus/protocol observations | Engineering owns design; RE owns behavioral reconstruction |
| Firmware image and boot chain | Firmware/embedded RE | image hash, architecture, extraction/analysis evidence | RE owns firmware analysis; Engineering owns hardware requirements |
| Mechanical CAD and assembly | Hardware-assisted targets | STEP/STL hashes, dimensions, interfaces, teardown observations | Engineering owns design intent; RE owns observed artifact facts |
| FPGA/RTL and bitstream | Firmware, native and hardware-assisted RE | RTL revision, synthesis reports, bitstream hash, device observations | Engineering owns implementation; RE owns reverse analysis |
| Manufacturing outputs | Artifact/format RE | Gerber/GDSII/STEP, fabrication revision, inspection record | Engineering owns source and manufacturing handoff |

## Rules

- Keep `ops/engineering/taxonomy.json` and `ops/reverse_engineering/taxonomy.json` independently validated.
- Express overlaps with explicit cross-domain references and artifact identifiers. Preserve each node's single primary placement in its owning taxonomy.
- Preserve RE evidence vocabulary: observed | inferred | reproduced | contradicted | unknown.
- Link refTemplates by canonical source URL, repository, version/commit, license, observed date and adaptation status.
- Treat refTemplates as read-only references until a specific adaptation is reviewed and adopted.
- Route graph relationships through the Context Relationship Graph; verified links and candidates remain distinct.
