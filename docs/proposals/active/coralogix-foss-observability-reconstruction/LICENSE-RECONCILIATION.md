# License Reconciliation Record

**Purpose:** fold upstream license findings into the repository's consolidated third-party/legal review. This is technical intake, not legal advice or a final legal opinion.

| Project | Research finding | Review action |
|---|---|---|
| OpenTelemetry Collector | Apache-2.0 | Verify exact tag, NOTICE, and dependency notices |
| SigNoz | MIT core; enterprise paths carry separate terms | Inventory core vs enterprise directories and dependencies at pinned revision |
| HyperDX | MIT reported for repository | Verify current ClickHouse/ClickStack component split and notices |
| OpenObserve | AGPL-3.0 core; enterprise features separately licensed | Review deployment/distribution model and enterprise boundary |
| Parca | Apache-2.0 | Verify NOTICE and bundled dependencies |
| Grafana Pyroscope | AGPL-3.0 | Review deployment model and distribution obligations |
| Langfuse | MIT core; enterprise components carry separate terms | Identify core/EE paths and dependency notices |
| Phoenix | ELv2 | Record source-available terms and permitted use; legal review before redistribution or hosted offering |
| Coralogix | Proprietary commercial service | Procurement, data-processing, retention, and contract review |
| My-Jogyo | MIT reported in prior source review | Verify upstream LICENSE at selected immutable revision |
| Docxology | License unresolved in current repository metadata | Inspect upstream LICENSE/NOTICE before code-level adaptation |

## Required record for each promoted source

Record canonical upstream URL, immutable tag/commit SHA, retrieval date, LICENSE/NOTICE digests, component boundaries/exceptions, dependency/SBOM inventory, modifications/attribution, intended use, legal reviewer/disposition, and license-change recheck trigger.

Preserve each component's actual license boundary. Consolidate notices and obligations in established repository legal materials when location and ownership are confirmed. Keep unresolved status explicit until source inspection completes.
