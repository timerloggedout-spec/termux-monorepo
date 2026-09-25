# Work Items — gantt-dependency-phases

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| DPH-000 | P1 | in_review | Canonical phase plan, deterministic lifecycle engine, validation, evidence model, Mermaid/Markdown projection, and unit fixtures. | Invalid graph/identity/check configuration fails closed; evidence evaluation is deterministic; generated views contain no authoritative state. |
| DPH-100 | P1 | in_review | GitHub Project #1 adapter and reconciliation flow. | Live Project discovery works; phase-to-item mapping is explicit; dry run is default; `--apply` is the only mutation path; Project status is a derived view. Live Project writes use the existing Operator-token precedence and require its selected credential to have Projects write permission. |
| DPH-200 | P1 | in_review | Idempotent claim and controlled agent-dispatch handoff. | A ready phase creates at most one claim per plan hash; dispatcher revalidates live state; unapproved/waiting/active phases do not dispatch. |
| DPH-300 | P2 | in_review | Actions workflows, reconciliation report, documentation, and runbooks. | Workflows use minimal permissions and safe triggers; pull-request validation is read-only; manual/scheduled reconciliation cannot auto-merge, close proposals, or update submodules. |
