# Work Items — gate-admission-optimization

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| GAO-001 | P1 | executing | Canonical Termux surface classifier and downstream PR lane semantics | Shared stdlib predicate covers exact paths and prefixes; manual dispatch and unavailable diff fail closed; non-Termux PRs can classify with repo-gate alone; Termux PRs require smoke evidence; tests cover path and pagination failures. |
| GAO-002 | P1 | executing | Termux workflow admission and bucket-headroom separation | Always-visible Termux check records explicit applicability; smoke runs only for matching paths or manual dispatch; bucket-headroom tests run in a dedicated path-scoped workflow; Termux workflow remains free of package-install and quota-test steps. |
| GAO-003 | P1 | executing | Dangle target-path trigger coverage | Pull-request triggers include reference-bearing source and target roots; baseline, census scopes, rename verifier, and report artifact remain intact; workflow policy tests cover roots. |
| GAO-004 | P1 | executing | Vercel and Devin provider admission boundaries | Historical-corpus-explorer uses `apps/historical-corpus-explorer` as root with affected-project filtering and a project-scoped ignore helper; Vercel provider receipts confirm unrelated-change skips; Devin remains optional until current API entitlement, quota, billing, and referral terms are verified. |
| GAO-005 | P1 | pending | Final validation, review, and promotion handoff | Focused tests and repo-gate pass on one immutable head; conditional Termux disposition is recorded; independent review is dispositioned; PR remains open for Operator merge decision. |

## Disposition

Execution is isolated on `feat/gate-admission-optimization-20261127`. Tasks proceed in small commits, with test-first verification through repository CI.
