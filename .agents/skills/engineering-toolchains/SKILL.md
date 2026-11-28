---
name: engineering-toolchains
description: Discover, route, validate and evaluate FOSS-first mechanical CAD, electronics, electrical, simulation, manufacturing and semiconductor toolchains in termux-monorepo.
---
# Engineering Toolchains

## Canonical sources
- Taxonomy: `ops/engineering/taxonomy.json`
- Validator: `python3 -m ops.engineering.taxonomy validate`
- Read-only tool inventory: `python3 scripts/engineering/toolchain_probe.py --json`
- Toolchain matrix: `docs/ops/ENGINEERING-TOOLCHAIN-MATRIX.md`
- Architecture: `docs/architecture/engineering-domain.md`
- Queue contract: `docs/ops/ENGINEERING-QUE-QDESK-CONTRACT.md`
- Experiment plan: `docs/ops/ENGINEERING-DOE-MVT-PLAN.md`

## Routing
1. Classify discipline, lifecycle stage, input artifact, expected output and verification method.
2. Read tool metadata and current probe evidence. Treat missing runtime evidence as unknown.
3. Prefer FOSS local tools with portable source formats. Record cloud-free-tier limits and commercial-use restrictions.
4. Route GUI-heavy and compute-heavy CAD/EDA/CAE work to an explicitly approved remote Linux runner. Termux remains the control plane and lightweight probe/validator runtime.
5. Preserve native source plus neutral exchange formats such as STEP, DXF, Gerber, IPC-2581, SPICE, MSH, GDSII, glTF and USD.
6. Capture tool version, source/input hashes, environment fingerprint, parameters, output hashes, exit state and validation evidence.
7. Reuse existing QUE/QDesk admission, ranking, claim, lease, escalation and Desk surfaces.
8. Send benchmarkable work through the existing DoE family. Retain repeated arms, failed trials, skipped trials and independent evaluation.
9. Link Reverse Engineering by artifact/firmware/hardware relationships and evidence citations. Keep taxonomy ownership separate.
10. Record verified operational learnings through the existing Learnings lane.

## Execution boundary
The inventory probe is read-only. The Termux Agentic Hub exposes named capabilities only. Tool installation, remote-runner provisioning, manufacturing submission, device programming and physical actuation require their own approved path. A catalog entry is not an installation receipt; a probe pass is not design validation; simulation is not certification.
