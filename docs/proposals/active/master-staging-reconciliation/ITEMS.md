# Work Items — master-staging-reconciliation

| ID | Priority | Status | Work | Acceptance criteria |
|---|---:|---|---|---|
| MSR-001 | P0 | done | Re-fetch canonical refs, compare branch ancestry, inspect open PRs, and record immutable source identities. | Master/staging SHAs, merge base, ahead/behind counts, Termux lane SHA, and seven open PR dispositions are recorded in the reconciliation ledger. |
| MSR-002 | P0 | executing | Scope `termux-smoke` to Termux runtime and device operations. | Workflow path filters and governance contracts route Termux smoke only for Termux-related work; repository gate remains the general baseline. |
| MSR-003 | P1 | executing | Move bucket-headroom contract tests into their own validation workflow. | Termux smoke runs Termux checks only; bucket-headroom tests run in a dedicated workflow on relevant paths. |
| MSR-004 | P0 | done | Define bounded extraction policy for staging-only commits and open PRs. | Each open staging PR has an explicit disposition; source refs remain preserved; branch history remains intact. |
| MSR-005 | P1 | todo | Extract validated staging workstreams onto fresh current-master branches. | Each workstream has an owning proposal item, current-master base, focused tests, reviewable PR, and current-SHA evidence. |
