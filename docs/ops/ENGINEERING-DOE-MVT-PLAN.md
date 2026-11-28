# Engineering Toolchains — DoE / MVT / ATES Plan

**Status:** proposal
**Owner/lane:** DoE / MVT / ATES + Engineering Toolchain Integration
**Canonical for:** engineering-toolchain experiment design and evidence mapping
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

## Surface ownership

The engineering cohort is enrolled in `docs/ops/AGENT-EVALUATION-LANE-REGISTRY.md` and the repository cross-domain lane feed through `ops/tracking/projects.json`. The registry identifies the lane; the tracking collector alone generates state/last-merge/next projections.

- DoE owns experimental design and factor selection.
- MVT is nested inside the DoE family and records multi-arm comparisons.
- ATES supplies execution discipline and run receipts.
- AEF owns the evaluation unit and task outcome.
- Learnings receives verified setup, compatibility and failure learnings after review.

Each record has one primary home. Cross-surface use is a citation, not a copied payload.

## Experiment factors

Candidate factors include discipline, tool ID/version, execution target, OS/architecture, runner image, source artifact format, task complexity, solver family, parameter set, and validation profile. Fix the task contract hash, environment fingerprint, benchmark version and deterministic scorer within a comparison.

## Outcomes

Primary:
- design/format validation pass rate;
- reproducible output hash or declared deterministic tolerance;
- ERC/DRC/DRC-LVS/mesh-quality or solver convergence verdict;
- requirement coverage and independent engineering review.

Secondary:
- runtime, peak memory, CPU/GPU use, retries, resource pressure and energy where measured;
- output size and portability;
- human intervention and attribution confidence.

## Canonical row identity

Use the existing `cohort × task × arm × repetition` identity. Retain task fingerprint, environment fingerprint, benchmark version, arm-factor hash, trace ID, deterministic verdict, ATES metrics and optional judge score. Preserve failed, skipped, cancelled and inconclusive trials.

## Minimum viable test cohort

1. FreeCAD STEP round-trip and parametric regeneration.
2. OpenSCAD deterministic STL export from pinned source.
3. KiCad schematic/PCB CLI validation plus ERC/DRC fixture.
4. ngspice reference circuit with expected numeric tolerances.
5. Gmsh mesh generation plus quality thresholds.
6. CalculiX/Elmer solver fixture with reference outputs and convergence checks.
7. Yosys synthesis and OpenROAD/KLayout flow on a bounded open RTL fixture.

The cohort is a plan until an execution receipt exists. One successful run does not establish a general tool ranking or production readiness.
