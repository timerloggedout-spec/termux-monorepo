# Repository Architecture Flow Modules

Root entry: [architecture.md](../../../architecture.md). Each module pairs a detailed mapping and editable Mermaid source.

| Module | Mapping | Diagram |
|---|---|---|
| Execution and Session Plane

**Origins:** Android/Termux device, hub_mcp capability boundary, CLI/TUI and agent session callers.

**Flow:** callers supply session identity and structured events → ArchWiz DispatchPipeline → Session SSOT and Codex index. The documented Linear route is a log-only sync hint.

**Consumers:** operator cockpit, session continuation, context retrieval and bounded task context.

**Findings:** caller → ArchWiz → Session SSOT/Codex is documented. Device/remote MCP reachability needs deployment evidence. Separate CLI families do not prove a shared session store. Linear hint does not prove a completed write.

**Sources:** [Termux Agentic Hub](../../architecture/termux-agentic-hub.md) · [Session SSOT](../../schemas/session-ssot.md) · [ICM platform cards](../../icm/objects/platform/CONTEXT.md)
 | [execution-session.md](execution-session.md) | [execution-session.mmd](execution-session.mmd) |
| Agent Orchestration and Provider Routing

**Planes:** ephemeral GitHub Actions review/ops; chat completion through llm_api_hub and CLI wrappers; MCP tool execution through hosted/device MCP servers; provider adapters translate external calls into repository event envelopes.

**Flow:** task/role selection → model-router and quota gate → chat or MCP route → scoped adapter → schema/privacy/provenance validation → normalized integration event.

**Findings:** chat and MCP paths are distinct. Hosted MCP, device MCP, Actions and local gateway are separate execution surfaces. Adapter contract is generic; provider promotion state lives in integration registry. Aggregate quota coverage does not prove every provider has a live reader. Provider outputs remain untrusted observations.

**Sources:** [Routing map](../../ops/ROUTING-ORCHESTRATION-MAP.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md) · [Integration catalog](../../integrations/README.md) · [Quota registry](../../ops/QUOTA-REGISTRY.md)
 | [agent-orchestration.md](agent-orchestration.md) | [agent-orchestration.mmd](agent-orchestration.mmd) |
| Evidence and Telemetry Plane

**Sources:** GitHub PRs/issues/commits/reviews/checks; Actions runs/attempts/jobs/steps/artifacts; admitted agent workflows; selected lane events; Cloudflare webhook events.

**Producers:** PR production ledger → EPS deterministic provenance-bound NDJSON. ATES observes completed admitted runs, sanitizes task-boundary evidence and reduces events. Lane recorder and Receiver Mesh write separate append-only Neon streams.

**Stores:** EPS NDJSON, ATES JSONL/reducer/receipt, Neon lane_events and Neon receiver_events remain separate products.

**Findings:** PR ledger → EPS and admitted workflow_run → ATES → reducer are connected. Jules execution-time ATES is excluded pending attributable receipts. ATES parallel-yield metrics remain null pending comparable serial baseline. Neon streams have separate contracts; unified join is unproven. Privacy excludes prompts, completions, credentials and raw payloads.

**Sources:** [EPS](../../ops/EVIDENCE-PROJECTION-SURFACE.md) · [ATES Phase B](../../ops/AGENT-THROUGHPUT-PHASE-B.md) · [Adapter contract](../../integrations/ADAPTER-CONTRACT.md)
 | [evidence-telemetry.md](evidence-telemetry.md) | [evidence-telemetry.mmd](evidence-telemetry.mmd) |
| Context Relationship and Historical Corpus

**Sources:** Git tree/files at pinned SHA; GitHub issues, PRs, commits, reviews, comments and workflow metadata; prior canonical nodes/edges and coverage checkpoints.

**Pipeline:** source_collector.py + github_collector.py → seed_merger.py → compiler.py → build_index.py → canonical JSONL nodes/edges, manifest, reports and checkpoint. Temporal helpers build snapshots, lineage and comparisons.

**Consumers:** ArchWiz context query, bounded agent context deltas, temporal views, Mermaid projections and SHE reducers.

**Findings:** Git/GitHub collectors → compiler → canonical index is connected. COMPLETE requires contiguous page windows from page one; otherwise preserve PARTIAL_CONTINUATION_REQUIRED or UNVERIFIED. Confidence labels verified/derived/inferred/candidate remain distinct. Mermaid graphs are projections, not source evidence. Freshness depends on source SHA, observed_at, checkpoint and coverage.

**Sources:** [CRG contract](../../ops/CONTEXT-RELATIONSHIP-INDEX.md) · [build_index.py](../../../archwiz/context_relationships/build_index.py) · [Temporal evidence](../../ops/CONTEXT-RELATIONSHIP-TEMPORAL-EVIDENCE.md)
 | [context-historical.md](context-historical.md) | [context-historical.mmd](context-historical.mmd) |
| Dashboard, Snapshot and Surface Consumers

**Inputs:** historical corpus/CRG; validated EPS and ATES evidence where configured; operational feeds; Tribute JSON feeds.

**Snapshot path:** SHE pure reducers → snapshot builder → versioned read-only snapshot. Contract requires schema_version, snapshot_id, source_ref, source_sha, generated_at, coverage and corpus manifest SHA. Vercel is the primary interactive surface; Pages and Hex are optional consumers. Tribute consumes a separate committed feed family.

**Findings:** corpus → SHE reducers → snapshot → Vercel is documented. Pages/Hex require current deployment/import evidence. Tribute feeds are a separate projection silo; shared repository does not prove automatic synchronization. Display source_sha, generated_at, coverage and manifest SHA together. Historical views use immutable L2 snapshots.

**Sources:** [SHE architecture](../../ops/SHE-DASHBOARD-ARCHITECTURE.mmd) · [Snapshot contract](../../ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md) · [Tribute feed](../../ops/TRIBUTE-EVIDENCE-FEED.md)
 | [dashboard-snapshots.md](dashboard-snapshots.md) | [dashboard-snapshots.mmd](dashboard-snapshots.mmd) |
| Legacy Local Snapshot Pipeline — Gap Audit

<badge color="danger">Disconnected / requires repair</badge>

**Observed:** archwiz/trace_data_flow.py scans local source directories for data-file path strings and writes $HOME/tmp/data_flow_map.txt. archwiz/build_data_flow_manifest.py reads $HOME/central_index.jsonl and the temporary map, then writes to absolute path $HOME/archwiz/DATA_FLOW_MANIFEST.md. The builder stamps a wall-clock Generated field and indexed-file count. The tracked archwiz/DATA_FLOW_MANIFEST.md blob is zero bytes at observed master SHA 5135731c389c6b1b8ed8332b3415a60f8163c2a1.

**Findings:** output path mismatch; no source SHA/tree SHA/generator version/input digest; substring/basename heuristics create candidate matches, not verified writer edges; temporary map is untracked scratch; central_index.jsonl lacks repo-owned freshness/coverage contract; no verified consumer reaches CRG/SHE/EPS; Generated proves run time, not input freshness.

**Repair contract:** resolve repo root from script location or explicit output path; publish to declared repo-owned generated directory; include generated_at, source_sha, tree_sha, generator_version, input_manifest_sha256, indexed_file_count, mapped_file_count, coverage_status and unmapped_count; classify heuristic matches as candidate; add freshness validation. Connect to CRG/SHE only after provenance and coverage pass.

Actual local generated_at remains unknown; this audit does not infer it.
 | [legacy-snapshot-audit.md](legacy-snapshot-audit.md) | [legacy-snapshot-audit.mmd](legacy-snapshot-audit.mmd) |

Connection vocabulary: connected = source verified; dangling = missing verified producer or consumer; siloed = distinct product with no demonstrated join; contract-only = spec without runtime proof; optional = conditional consumer; stale = outside freshness bound; unknown = evidence unavailable.

Snapshot envelope: source_sha, tree_sha when applicable, generated_at, generator version, input/manifest digest, coverage status and unresolved count. generated_at means actual generator execution time, not audit date or source commit time.
