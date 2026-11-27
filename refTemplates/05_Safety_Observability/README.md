# 05_Safety_Observability

Operational telemetry, safety signals, profiling, and investigation references.

| Reference | Primary role | Disposition |
|---|---|---|
| opentelemetry-collector | Vendor-neutral receive/process/export | P0 interoperability reference |
| signoz | OTel-native logs/metrics/traces/APM | P1 UI comparison |
| hyperdx-clickstack | Search-first observability and session replay | P1 UI comparison |
| openobserve | Unified logs/metrics/traces | P1 UI comparison; AGPL review |
| parca | Continuous profiling | P1 profiling candidate |
| pyroscope | Continuous profiling and telemetry correlation | P1 profiling comparison |
| coralogix-comparator | Commercial integrated observability benchmark | Research-only comparator |

Each reference directory contains README and SOURCE metadata. Registration creates no runtime dependency. Canonical JSONL/receipts remain the evidence authority.

Existing category entries: destructive_command_guard, process_triage, rano, system_resource_protection_script.
