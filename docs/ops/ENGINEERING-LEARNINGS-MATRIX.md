# Engineering Toolchain Learnings Matrix

**Status:** proposal
**Owner/lane:** Learnings + Engineering Toolchain Integration
**Canonical for:** evidence-backed reusable learnings from engineering tool discovery and execution
**Review record:** PR for `feat/engineering-toolchain-activation` (review pending)

| Learning class | Capture | Evidence required | Consumers |
|---|---|---|---|
| Install/runtime compatibility | OS, architecture, package source, command path, dependency/runtime constraints | probe receipt, package/version metadata, install source | Termux setup, runner profiles |
| License/access | SPDX/license text, commercial-use conditions, account/card requirements, cloud/publicity limits | official license/pricing terms and review date | FOSS policy, procurement and project intake |
| Format interoperability | import/export paths, fidelity limits, neutral artifact support | round-trip fixtures, hashes and independent parser checks | CAD/EDA/CAE toolchain routing |
| Simulation validity | solver version, mesh, boundary conditions, parameters, convergence and reference comparison | reproducible input deck, output metrics, validation report | DoE/MVT and engineering review |
| Performance/resource | CPU, memory, wall time, disk, energy/thermal when measured | pinned environment and repeated run receipts | runner selection and resource budgets |
| Failure/recovery | exact failure class, reproducible fixture, workaround and residual risk | logs with secrets removed, issue/PR, current SHA | adaptive-wait, QDesk, reliability |
| Safety/physical effect | hazard class, required qualifications, physical-world effect | approved safety review and operator receipt | QDesk escalation and external service gate |

## Learning record contract

Every promoted learning carries: `learning_id`, `tool_id`, `tool_version`, `source_revision`, `observed_at`, `environment_fingerprint`, `task_fingerprint`, `evidence_refs`, `outcome`, `confidence`, `known_limits`, `owner_lane`, `supersedes` (optional) and `validation_state`.

## Promotion

A single run can create an observation. Reusable learning requires reproducibility, source attribution and independent review where the claim affects engineering correctness, safety, licensing or manufacturing. Failed and contradictory observations remain retained. The existing Learnings lane remains the sole memory store for promoted, verified records.
