# Foundry Local — Local Inference Runtime Pattern

**Category:** `01_Agent_Runtime`  
**Disposition:** runtime experiment candidate · metadata-first

## Source

See `SOURCE.txt`. Pin an immutable source revision before reproducible experiments.

## Pattern to extract

- On-device/local model inference.
- Hardware-aware execution and model selection.
- Native SDK boundaries around a local inference service.
- Explicit runtime and platform qualification.

## Repository adaptation

Treat Foundry Local as an optional inference backend. Run a compatibility matrix for Linux ARM64, Android/Bionic and Termux before integration work. Measure cold-start, memory, throughput, model coverage and task quality against the current inference path.

## Measures

Platform compatibility, install footprint, cold-start, peak memory, tokens/sec, task acceptance, thermal behavior and operational recovery.

## Ownership

CEEL owns concept extraction and experiment evidence. The designated licensing duty owner handles licensing disposition separately.
