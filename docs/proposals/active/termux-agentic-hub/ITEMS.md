# Work Items — termux-agentic-hub

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| THUB-001 | P1 | done | Register approved user-owned forks under `refTemplates/smods/` and validate their fixed revisions. | `.gitmodules` and registry agree; all pins resolve; no sensitive state is imported. |
| THUB-002 | P1 | done | Create the single `hub_mcp/` policy package, capability-tier definitions, and adapter map. | Canonical server and adapter roles are explicit; unknown/free-form commands are rejected. |
| THUB-003 | P1 | done | Implement structured job/result schemas, validation, idempotency, expiry, redaction, and Observe-only handlers. | Unit tests reject invalid, expired, replayed, and unapproved jobs; valid Observe jobs produce redacted results. |
| THUB-004 | P1 | done | Add safe GitHub workflows for submodule integrity, job validation, result audit, smoke checks, and fork divergence reporting. | Workflows use explicit minimum permissions; no workflow executes device commands or leaks secrets. |
| THUB-005 | P2 | done | Write BLU B160V Termux bootstrap, service-control, battery, and recovery runbooks. | Runbook covers health check, restart, key-only SSH, and no-public-exposure posture. |
| THUB-006 | P1 | in_review | Run repository gates, prepare review documentation, commit with agent attribution, push the feature branch, and open a PR to `master-staging`. | Pull request #221 is open; scoped gates passed and inherited baseline failures are documented. |
| THUB-007 | P1 | in_progress | Add an extensible GitHub-native suite that measures termux-monorepo development performance from validated repository evidence. SWE-agent and mini-SWE-agent are pinned reference adapters, not the benchmark target; the first repository adapter measures PR lifecycle, review, check, and automation-response signals. | The suite must keep adapters independently versioned and redaction-aware; deterministic repository evidence must run without a model credential; optional reference adapters must reject unbounded workloads and never emit credentials; focused tests plus repository gates must pass when the inherited baseline permits. |
