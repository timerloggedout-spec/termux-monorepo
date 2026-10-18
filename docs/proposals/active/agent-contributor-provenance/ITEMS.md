# Work Items — agent-contributor-provenance

| ID | Priority | Status | Scope | Acceptance criteria |
|---|---:|---|---|---|
| ACP-001 | P1 | in_review | Closed ATES author provenance and workflow/job/PR/issue/SHA linkage. | Schema and emitter reject unknown author fields; actor identity stays separate; model/settings/context remain null unless evidenced; fingerprints only; 11 focused emitter tests pass. |
| ACP-002 | P1 | in_review | Extend the read-only observer to existing provider, manager, scout, orchestrator, and Jules workflow cohorts without counting bridge health as agent work. | Workflow map uses explicit known workflow names; mapped agent IDs appear correctly in summaries; cancelled/unknown workflows are not relabeled success; current-head checks are observed. |
| ACP-003 | P1 | in_review | Curate every citation instance from dated briefs and the existing resource/procurement/radar evidence plus selected operational SSOTs. | Offline deterministic JSONL ledger; source/item context preserved; self-index recursion excluded; malformed JSON/JSONL fails; artifact contains 102 citation instances across 18 source documents on the validated head. |
| ACP-004 | P1 | in_review | Document the integrated P0–P6 acceptance contract and wire validation into existing gates. | Canonical SSOTs linked; 6 briefing validator tests + 6 citation tests + 11 emitter tests pass; repo-gate and termux-smoke success on the same head; review blockers recorded honestly. |

## Disposition

This proposal remains `in_review` while the PR is open and provider-review/check dispositions are being reconciled. Do not close it because code is committed or a workflow is merely queued.
