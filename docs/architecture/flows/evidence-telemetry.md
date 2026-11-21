# Evidence and Telemetry Plane

**Sources:** GitHub PRs/issues/commits/reviews/checks; Actions runs/attempts/jobs/steps/artifacts; admitted agent workflows; selected lane events; Cloudflare webhook events.

**Producers:** PR production ledger → EPS deterministic provenance-bound NDJSON. ATES observes completed admitted runs, sanitizes task-boundary evidence and reduces events. Lane recorder and Receiver Mesh write separate append-only Neon streams.

**Stores:** EPS NDJSON, ATES JSONL/reducer/receipt, Neon lane_events and Neon receiver_events remain separate products.

**Findings:** PR ledger → EPS and admitted workflow_run → ATES → reducer are connected. Jules execution-time ATES is excluded pending attributable receipts. ATES parallel-yield metrics remain null pending comparable serial baseline. Neon streams have separate contracts; unified join is unproven. Privacy excludes prompts, completions, credentials and raw payloads.

**Sources:** [EPS](../../ops/EVIDENCE-PROJECTION-SURFACE.md) · [ATES Phase B](../../ops/AGENT-THROUGHPUT-PHASE-B.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md)
