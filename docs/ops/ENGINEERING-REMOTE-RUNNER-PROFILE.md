# Engineering Remote Runner Profile — FOSS / free / no-card posture

**Status:** design profile; runner not provisioned
**Owner/lane:** Tooling / Delivery Reliability
**Canonical for:** remote execution target selection and cost/data boundaries for engineering toolchains

## Preferred free hosted lane

Use GitHub Actions standard GitHub-hosted Linux runners for public, non-confidential engineering fixtures and small reproducible jobs.

- Standard hosted runners are free for public repositories; self-hosted runner use is also free from GitHub runner-minute charges.
- The documented `ubuntu-latest` x64 standard VM currently provides 4 CPU, 16 GB RAM and 14 GB SSD. Pin a stable image such as `ubuntu-24.04` for reproducible environments instead of relying on a moving `-latest` alias.
- Use standard runners only; larger runners are billed.
- Treat the 14 GB disk and 16 GB memory as hard practical limits for this profile. Large CAD assemblies, full CFD/FEA meshes and large RTL place-and-route workloads need a separately sized host.
- Keep workflows least-privilege and artifact outputs bounded. Public repository workflows must use synthetic or intentionally public engineering inputs; private IP, BOMs, customer data, credentials and proprietary design files stay on an approved private host.

Official references:
- https://docs.github.com/en/actions/concepts/billing-and-usage
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners

## Self-hosted free lane

Use a user-owned Linux workstation or server as a self-hosted runner for confidential data, GUI/desktop applications, large solvers, hardware-in-the-loop fixtures and workloads exceeding hosted runner limits. GitHub does not charge runner-minute fees for self-hosted runners; the owner supplies hardware, power, maintenance, network and physical security.

Required controls:
- dedicated unprivileged runner account and isolated work directory;
- ephemeral or resettable runner where feasible;
- no secrets in job logs or untrusted pull-request execution;
- network egress allowlist and pinned tool images/packages;
- resource ceilings, timeouts and cancellation handling;
- immutable input/output hashes and retained validation receipts;
- separate runner labels for CAD, EDA, CAE and semiconductor workloads;
- explicit owner approval before any job touches physical devices or manufacturing services.

## Tool-to-runner placement

| Workload | Initial runner |
|---|---|
| Taxonomy validation, metadata checks, SPICE fixtures, small OpenSCAD jobs | GitHub-hosted standard Linux |
| KiCad CLI ERC/DRC and small PCB fixtures | GitHub-hosted standard Linux after package/version pin |
| Yosys synthesis and bounded OpenROAD/KLayout examples | GitHub-hosted standard Linux after resource test |
| FreeCAD GUI, assemblies, CAM, large mesh/FEA | Self-hosted Linux; hosted runner only for small headless fixtures |
| OpenFOAM, Elmer, large CalculiX/FEniCS workloads | Self-hosted Linux or explicitly approved research compute |
| Hardware bring-up, device programming, fabrication submission | Dedicated owner-controlled runner with separate approval and safety controls |

## Current blockers

1. Workflow-file changes under `.github/workflows/**` require an Operator PAT or a custom GitHub App with Workflows write permission under `docs/proposals/AGENTIC-PERMISSIONS.md`. This branch therefore adds the issue template and code contracts without adding an execution workflow.
2. The current session has no Termux device-operation function and no verified self-hosted engineering runner.
3. Public runner free usage is not a confidentiality guarantee. Data classification determines whether a job may use a public repository runner.

## Acceptance

Provisioning becomes eligible when the operator-approved workflow permission path and a target runner are available. First pilot: a synthetic KiCad CLI validation fixture plus an ngspice reference circuit, with exact tool versions, environment fingerprint, artifact hashes and independent expected-output checks.
