# OpenTelemetry Collector

**Role:** neutral telemetry receiver, processor, and exporter pipeline for logs, metrics, and traces.  
**Reported license:** Apache-2.0. **Fit:** P0 interoperability and ingestion boundary.

Use as a transport and processing reference. Keep canonical JSONL/receipts and Git SHA/run identity repository-owned. Implement a thin, testable exporter/adapter from the evidence contract; preserve event digests and schema versions.

Evaluate OTLP/JSONL coverage, redaction, backpressure, retries, event limits, ARM/Linux compatibility, memory/CPU overhead, and export completeness.

**Disposition:** metadata reference; implementation candidate after contract fixtures and environment fingerprinting.
