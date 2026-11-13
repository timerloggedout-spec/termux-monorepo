# AMD + NVIDIA Agent Skills — vendor import

**Imported:** 2026-11-13  
**Branch:** `feat/vendor-amd-nvidia-skills-2026-11-13`  
**Scope:** Project-loadable Agent Skills under `.agents/skills/`. This is a curated vendor import, not a claim that the repository owns or validates the upstream GPU runtimes.

## AMD — official catalog (MIT)

Upstream: https://github.com/amd/skills  
Catalog: https://rocm.docs.amd.com/projects/amd-skills/en/latest/catalog.html  
Install/update model: `npx skills add amd/skills --list` / `npx skills update`.

Imported skills:

| Skill | Project path | Role |
|---|---|---|
| hyperloom-workload-optimizer | `.agents/skills/hyperloom-workload-optimizer/` | Instinct inference optimization loop |
| serving-llms-on-instinct | `.agents/skills/serving-llms-on-instinct/` | Instinct vLLM/SGLang serving |
| tracelens-analysis-orchestrator | `.agents/skills/tracelens-analysis-orchestrator/` | PyTorch trace analysis and prioritized report |
| local-ai-app-integration | `.agents/skills/local-ai-app-integration/` | Embeddable Lemonade app integration |
| local-ai-use | `.agents/skills/local-ai-use/` | Local inference for agent-side media workflows |

Each imported directory includes the upstream `SKILL.md` and `skill-card.md`. The app-integration, Instinct-serving and TraceLens skills also include their primary `reference.md`. Other optional package assets remain upstream and should be installed from the official catalog before attempting workflows that require them. Do not infer that a host has AMD hardware or ROCm merely because these skills are present.

## NVIDIA — official catalog (CC-BY-4.0 AND Apache-2.0 unless noted)

Upstream: https://github.com/NVIDIA/skills  
Source snapshot commit: `d59805503396547363ff0079c436b1cae496e1af`  
Catalog/install: `npx skills add nvidia/skills --list`.

Imported skills:

| Skill | Project path | Role | Upstream license |
|---|---|---|---|
| compute-sanitizer-diagnose-cuda-bugs | `.agents/skills/compute-sanitizer-diagnose-cuda-bugs/` | CUDA correctness diagnostics | CC-BY-4.0 AND Apache-2.0 |
| tilegym-improve-cutile-kernel-perf | `.agents/skills/tilegym-improve-cutile-kernel-perf/` | cuTile kernel profiling and optimization | CC-BY-4.0 AND Apache-2.0 |
| nemo-mbridge-perf-cuda-graphs | `.agents/skills/nemo-mbridge-perf-cuda-graphs/` | Megatron Bridge CUDA graph performance | Apache-2.0 |

Compute Sanitizer's five tool references and TileGym's six optimization/API/model references are included. NVIDIA source cards are included alongside the skill bodies. NVIDIA signatures and the upstream trust anchor are **not** copied or claimed verified; verify signatures against the upstream NVIDIA trust anchor before treating these as NVIDIA-authenticated vendor artifacts. The upstream catalog documents signature verification and evaluation requirements.

## Integration with Termux Monorepo

- `.agents/skills/` is the project-loadable source of truth; the inventory and short entry are updated in this change.
- AMD Hyperloom/TraceLens and NVIDIA TileGym/Compute Sanitizer become optional specialized lanes around the existing telemetry/evidence plane. Their raw metrics must not silently become canonical MoneyBall/3L0 scores; normalize via explicit versioned adapters and preserve provider/version/provenance.
- ROCm and CUDA are distinct runtime stacks. Never infer cross-vendor portability from a shared skill format. Select the hardware-specific path only after host/device detection.
- NVIDIA CUDA-only instructions do not run on AMD ROCm; AMD ROCm/HIP instructions do not run on NVIDIA CUDA. Use neutral interfaces only at explicit adapter boundaries.
- No GPU benchmark or runtime validation was performed by this import. Import status is `COMMITTED` only after merge; execution/validation/promotion remain separate states.

## Suggested next integration

1. Add AMD ROCm and NVIDIA CUDA environment probes as read-only evidence collectors.
2. Normalize host/GPU/runtime/driver/framework/model/workload fingerprints into the existing execution telemetry schema.
3. Run matched AMD and NVIDIA benchmarks only on actual supported hardware; keep vendor-specific kernel tuning separate.
4. Add correctness gates before throughput comparisons and record raw results plus measurement-provider versions.
5. Evaluate AMD Hyperloom and NVIDIA TileGym/Compute Sanitizer as distinct toolchain lanes, not as interchangeable optimizers.

## Provenance and licensing

The AMD catalog is MIT-licensed. NVIDIA skills carry per-skill licenses listed above and in their skill cards. Preserve those cards and attribution when modifying or redistributing. Upstream repositories remain authoritative; refresh from upstream rather than editing vendor guidance locally without recording a fork.
