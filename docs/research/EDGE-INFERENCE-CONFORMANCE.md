# Edge Inference Conformance

## Purpose

Turn ARM/Linux/Android/Termux local inference into a reproducible evidence lane.

The target is not headline TOPS. The target is energy, memory, latency, throughput,
correctness, portability, and reproducibility under a fixed workload.

## Required run identity

Record device, SoC, RAM, OS/Android version, Termux version when applicable,
runtime/project, runtime commit/version, model identifier and digest, quantization,
backend, accelerator, workload fixture version, and environment fingerprint.

## Measurements

At minimum record time-to-first-token, tokens/sec, peak RSS, resident model memory,
wall time, energy when a power meter is available, temperature/thermal state when
available, output agreement against a reference backend, and failure classification.

Energy measurements must state the measurement method and uncertainty.

## Comparison rule

CPU, GPU, NPU and cloud fallback are comparable only when model, quantization,
prompt/workload, correctness criteria, and output acceptance are held constant.

Vendor TOPS figures are metadata, not measured inference evidence.

## Portability targets

Record each target independently: ARM64 Linux, x86_64 Linux, Android, Termux,
and offline/air-gapped. An untested target must not be marked portable.

## Procurement implication

Prefer hardware that supports reproducible builds, offline execution, inspectable
accelerator paths, stable power measurement, and commodity replacement.

The conformance artifact is JSON/JSONL and remains usable without a dashboard.
