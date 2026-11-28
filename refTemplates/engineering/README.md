# Engineering Toolchain References

**Role:** read-only upstream reference catalog for engineering tools and reusable examples.
**Machine authority:** `ops/engineering/taxonomy.json` remains the tool/domain SSOT.
**Adoption state:** catalogued references; source revisions are unpinned until a specific template is selected.

## Reference rules

1. Use upstream project documentation and repositories as source authority.
2. Record canonical URL, source repository, observed date, license, version/commit, and checksum when a specific artifact is adopted.
3. Keep this directory metadata-only by default. Add submodules or copied source only through a separate reviewed proposal with license and maintenance evidence.
4. Treat examples, CAD models, footprints, symbols, PCB projects, meshes, solver decks, RTL blocks and macros as untrusted inputs until provenance, license, compatibility and security checks pass.
5. Prefer neutral exchange formats and source-linked manifests. Keep source projects immutable; record local adaptations separately.
6. Never treat a sample model, simulation result or upstream example as a certified engineering design.

## Canonical cross-links

- Tool taxonomy and license/access metadata: [`ops/engineering/taxonomy.json`](../../ops/engineering/taxonomy.json)
- Toolchain matrix: [`docs/ops/ENGINEERING-TOOLCHAIN-MATRIX.md`](../../docs/ops/ENGINEERING-TOOLCHAIN-MATRIX.md)
- Engineering/Reverse Engineering crosswalk: [`docs/ops/ENGINEERING-RE-REFERENCE-MATRIX.md`](../../docs/ops/ENGINEERING-RE-REFERENCE-MATRIX.md)
- Reference manifest: [`references.json`](references.json)

## Initial reference set

The initial set covers FreeCAD, OpenSCAD, SolveSpace, LibreCAD, KiCad, LibrePCB, QElectroTech, ngspice, Qucs-S, Gmsh, CalculiX, Elmer, OpenFOAM, openEMS, FEniCSx, SALOME, Yosys, OpenROAD, KLayout and Blender. Onshape Free and SOLIDWORKS are recorded as proprietary interoperability targets in the taxonomy.
