---
name: nvidia-vendor-workflows
description: Discover and evaluate NVIDIA skills for repository work when CUDA or NVIDIA hardware is relevant. Use for discovery and readiness assessment; do not assume a skill is installed.
---

# NVIDIA Vendor Workflow Router

The upstream catalog is a discovery source, not proof that any catalog entry is installed or runnable.

## Safe adoption flow

1. Select the exact skill path from the NVIDIA catalog.
2. Record the upstream commit or release and inspect its license and dependencies.
3. Check for scripts, package installation, network access, credentials, model downloads, and privileged operations before execution.
4. Verify CUDA/runtime/driver and hardware compatibility, or explicitly document the approved remote environment.
5. Run a small, reproducible smoke test before workload evaluation.
6. Record results with `docs/ops/AMD-NVIDIA-SKILL-EXECUTION-RECEIPT.schema.json`; do not infer performance from vendor claims.

## Evidence contract

Use `discovered`, `installed`, and `selected` as lifecycle states, and `not_run`, `blocked`, `executed`, and `validated` as execution states. Do not report validation without reproducible test evidence.

## Canonical references

- Catalog: https://github.com/NVIDIA/skills/tree/main/skills
- Integration contract: `docs/ops/AMD-NVIDIA-SKILLS-INTEGRATION.md`
- Registry: `docs/ops/nvidia-skills-registry.json`
- Vendor routing notes: `skills/vendors/nvidia/README.md`
