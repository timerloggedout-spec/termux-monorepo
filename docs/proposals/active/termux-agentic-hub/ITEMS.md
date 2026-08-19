# Work Items — termux-agentic-hub

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| THUB-001 | P1 | done | Register approved user-owned forks under `refTemplates/smods/` and validate their fixed revisions. | `.gitmodules` and registry agree; all pins resolve; no sensitive state is imported. |
| THUB-002 | P1 | done | Create the single `hub_mcp/` policy package, capability-tier definitions, and adapter map. | Canonical server and adapter roles are explicit; unknown/free-form commands are rejected. |
| THUB-003 | P1 | done | Implement structured job/result schemas, validation, idempotency, expiry, redaction, and Observe-only handlers. | Unit tests reject invalid, expired, replayed, and unapproved jobs; valid Observe jobs produce redacted results. |
| THUB-004 | P1 | done | Add safe GitHub workflows for submodule integrity, job validation, result audit, smoke checks, and fork divergence reporting. | Workflows use explicit minimum permissions; no workflow executes device commands or leaks secrets. |
| THUB-005 | P2 | done | Write BLU B160V Termux bootstrap, service-control, battery, and recovery runbooks. | Runbook covers health check, restart, key-only SSH, and no-public-exposure posture. |
| THUB-006 | P1 | in_review | Run repository gates, prepare review documentation, commit with agent attribution, push the feature branch, and open a PR to `master-staging`. | Pull request #221 is open; scoped gates passed and inherited baseline failures are documented. |
| THUB-007 | P1 | in_progress | Add a GitHub-native, manually dispatched SWE-reference performance-evaluation control plane with a fixed reference revision, bounded benchmark selection, validated/redacted result manifests, immutable artifacts, and an advisory development-automation summary. | The workflow must be disabled from automatic cost-bearing execution; it must reject unbounded workloads, never emit model credentials, validate machine-produced summaries deterministically, and pass focused tests plus repository gates when the inherited baseline permits. |
