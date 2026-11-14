---
name: amd-vendor-workflows
description: Route AMD AI, local inference, Instinct serving, workload optimization, and profiler-trace analysis to the appropriate documented workflow. Use when a task explicitly targets AMD hardware or software.
---

# AMD Vendor Workflow Router

Use this entry point to choose an AMD workflow without assuming the current machine has AMD GPU hardware.

## Routing

- LLM serving on AMD Instinct: consult `serving-llms-on-instinct`; verify compatible Instinct hardware, ROCm, driver/runtime versions, and model requirements first.
- Workload optimization: consult `hyperloom-workload-optimizer`; require a successful hardware/runtime preflight before making recommendations dependent on GPU measurements.
- Local/offline application integration: consult `local-ai-app-integration` and `local-ai-use`; verify the configured Lemonade runtime and health endpoint.
- Profiler trace analysis: consult `tracelens-analysis-orchestrator` only when a real trace is available; redact sensitive content before sharing.

## Evidence contract

Record each attempt using `docs/ops/AMD-NVIDIA-SKILL-EXECUTION-RECEIPT.schema.json`. Keep unrun and blocked work distinct from executed and validated work. Never fabricate benchmark values, hardware availability, or execution status.

## Canonical references

- Integration contract: `docs/ops/AMD-NVIDIA-SKILLS-INTEGRATION.md`
- Registry: `docs/ops/amd-skills-registry.json`
- Vendor routing notes: `skills/vendors/amd/README.md`
