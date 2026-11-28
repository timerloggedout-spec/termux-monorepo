# Engineering Reference Templates

**Status:** active reference catalog
**Owner/lane:** Engineering Toolchain Integration + refTemplates
**Canonical metadata:** `docs/ops/ENGINEERING-REFERENCE-SET.json`
**Local workspace:** `refTemplates/engineering/` (gitignored, local-only)

## Purpose

Enroll engineering projects and example artifacts in the existing refTemplates workflow while preserving the repository rule that `refTemplates/` is excluded from Git. The tracked catalog lives under `docs/ops/`; actual shallow clones, examples and source checkouts remain local reference material.

## Source classes

- Upstream application sources: FreeCAD, OpenSCAD, SolveSpace, LibreCAD, KiCad, LibrePCB, QElectroTech, ngspice, Qucs-S, Gmsh, CalculiX, Elmer, OpenFOAM, openEMS, FEniCSx, SALOME, Yosys, OpenROAD, KLayout and Blender.
- Proprietary interoperability targets: Onshape Free and SOLIDWORKS, recorded in the engineering taxonomy but excluded from the FOSS reference baseline.
- Engineering fixtures: native CAD projects, schematics, PCB layouts, footprints/symbol libraries, SPICE decks, meshes, solver cases, RTL, LEF/DEF and GDSII examples.

## Ingestion policy

1. Keep local source checkouts under `refTemplates/engineering/`; use shallow clones and selective submodules.
2. Record the official project URL, resolved upstream repository, commit/tag, license, observed date and checksums in the tracked reference-set manifest before adopting a fixture.
3. Keep references read-only. A copied or adapted model, symbol, footprint, solver deck or RTL block requires a separate source/adaptation record and license review.
4. Retain only the minimal fixtures required for reproducible tests; avoid storing large generated meshes, rendered media or build products in Git.
5. Link reference evidence from the engineering taxonomy, DoE/MVT run receipts and Reverse Engineering crosswalk. Execution and manufacturing authority remain separate approvals.

## Current status

Twenty FOSS tools are catalogued as reference-only; Onshape Free and SOLIDWORKS remain separately classified proprietary products. Upstream repository revisions remain unpinned in this branch; third-party source vendoring remains outside this integration slice.
