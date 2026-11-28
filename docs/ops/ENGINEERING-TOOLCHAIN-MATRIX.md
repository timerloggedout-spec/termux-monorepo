# Engineering Toolchain Matrix

**Status:** proposal
**Owner/lane:** Engineering Toolchain Integration
**Canonical for:** tool selection, access class, portable artifact and runtime routing matrix
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

## Mechanical design

| Tool | Role | License/access | Main artifacts | Termux posture |
|---|---|---|---|---|
| FreeCAD | Parametric CAD, assemblies, FEM/CAM integration | LGPL FOSS; free local use | FCStd, STEP, IGES, STL, DXF | Remote Linux preferred; device probe required |
| OpenSCAD | Code-defined parametric CAD | GPL FOSS; free local use | SCAD, STL, 3MF, DXF | CLI candidate; probe required |
| SolveSpace | Constraint-based 2D/3D CAD | GPL FOSS; free local use | STEP, DXF, STL | Remote Linux preferred |
| LibreCAD | 2D drafting | GPL FOSS; free local use | DXF | Remote Linux preferred |
| Onshape Free | Cloud parametric CAD | Proprietary free tier; public documents and non-commercial constraints | STEP, IGES, STL, DXF | Browser/cloud; separate access evidence |
| SOLIDWORKS | Commercial CAD interoperability | Proprietary paid product | SLDPRT, SLDASM, STEP, IGES, DXF | Paid target; excluded from free baseline |

## Electronics and electrical design

| Tool | Role | License/access | Main artifacts | Termux posture |
|---|---|---|---|---|
| KiCad | Schematic, PCB, ERC/DRC, manufacturing exports | GPL FOSS; free local use | KICAD_SCH, KICAD_PCB, Gerber, IPC-2581 | CLI/GUI runner; probe required |
| LibrePCB | Schematic and PCB design | GPL FOSS; free local use | project source, Gerber, STEP | CLI/GUI runner; probe required |
| QElectroTech | Electrical diagrams | GPL FOSS; free local use | QET, PDF, SVG | Remote Linux preferred |
| ngspice | Mixed-level/mixed-signal circuit simulation | GPL FOSS; free local use | SPICE decks, RAW, logs | CLI candidate; probe required |
| Qucs-S | Circuit simulation frontend for ngspice/Xyce | GPL FOSS; free local use | QCS, SPICE, S-parameters | Remote Linux preferred |

## Simulation and computational engineering

| Tool | Role | License/access | Main artifacts | Termux posture |
|---|---|---|---|---|
| Gmsh | Geometry and mesh generation | GPL FOSS; free local use | GEO, MSH, UNV | CLI candidate; probe required |
| CalculiX | Structural and thermomechanical FEA | GPL FOSS; free local use | INP, FRD, DAT | Remote runner preferred |
| Elmer | Multiphysics FEM | GPL FOSS; free local use | SIF, VTU | Remote runner preferred |
| OpenFOAM | CFD | GPL FOSS; free local use | OpenFOAM case, VTK | Remote runner preferred |
| openEMS | FDTD electromagnetic simulation | GPL FOSS; free local use | XML, HDF5, S-parameters | Remote runner preferred |
| FEniCSx | PDE/FEM scientific computing | LGPL FOSS; free local use | XDMF, HDF5, VTK | Remote runner preferred |
| SALOME | CAD preparation and meshing | LGPL FOSS; free local use | MED, UNV, STEP | Remote runner preferred |

## Semiconductor and visualization

| Tool | Role | License/access | Main artifacts | Termux posture |
|---|---|---|---|---|
| Yosys | RTL synthesis | ISC FOSS; free local use | Verilog, RTLIL, JSON | CLI/remote runner; probe required |
| OpenROAD | RTL-to-GDS physical design | BSD-3-Clause FOSS; free local use | LEF, DEF, ODB, GDSII | Remote runner preferred |
| KLayout | IC layout and DRC/LVS | GPL FOSS; free local use | GDSII, OASIS, LEF, DEF | Remote Linux preferred |
| Blender | Technical visualization and 3D asset pipeline | GPL FOSS; free local use | BLEND, glTF, USD, STL, OBJ | Existing 3D pipeline; probe required |

## Access and evidence semantics

- `FOSS + local-free`: no subscription or card is required to obtain the application; license obligations and dependency licenses still apply.
- `cloud-free-tier`: proprietary hosted service with a free usage tier; terms, document visibility and commercial restrictions remain explicit.
- `commercial-paid`: paid proprietary product; retained as interoperability target only.
- `detected`: the named executable is present on the probed PATH. This does not prove the application works, has GUI dependencies, or can complete an engineering job.
- `remote-runner-preferred`: heavy GUI/solver workloads use an approved, pinned runner with bounded resources and artifact retention.

The probe currently establishes only executable presence. Tool version, solver correctness, format round-trip, resource use and engineering validity require separate validation receipts.
