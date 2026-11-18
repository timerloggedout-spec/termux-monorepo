# 04_promote — execute an eligible documentation update

One job: turn a verified ICM map change into a focused repository update, observe the required validation lifecycle, and promote only when repository-native evidence satisfies FA-ADE.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | [`../03_verify/output/verification-record.md`](../03_verify/output/verification-record.md) | Provides map-specific validation evidence and blockers; created by the prior stage. |
| Reference | [`../../objects/governance/change-control.md`](../../objects/governance/change-control.md) | Defines branch, work-item, gate, and human-only boundaries. |
| Reference | [`../../../../CLAUDE.md`](../../../../CLAUDE.md) | Defines the repository's branch policy, adaptive WAIT, dual gates, and auto-promotion rule. |
| Reference | [`../../../../docs/ARCHW1Z-GATE.md`](../../../../docs/ARCHW1Z-GATE.md) | Defines the two required repository gates. |
| Reference | [`../../_shared/maintenance-rules.md`](../../_shared/maintenance-rules.md) | Preserves documentation-only scope and permission boundaries. |

## Process

1. Confirm the verification record is complete and the diff is documentation-only.
2. Update stable map files and the active proposal item; do not commit per-run output artifacts.
3. Commit on the authorized feature branch with `Implements: <ITEM-ID>` in the commit or PR record.
4. Open or update the review PR as required by the repository workflow; do not target `master-staging` unless root policy declares that lane active.
5. WAIT while checks execute. Inspect jobs, steps, logs, and artifacts; re-fetch the exact PR head SHA and compare it with the verified SHA.
6. Promote when both required gates are green on the current head and the task outcome is verified, subject to the repository's configured permissions and protections.
7. If a required gate fails, the head changes, the outcome is unverified, or policy blocks promotion, record `BLOCKED` with the exact evidence. Do not relabel pending or cancelled checks as success.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Promotion record | `output/promotion-record.md` | Markdown record of commit, PR, current-head checks, promotion state, and unresolved blockers |
| Reviewable update | Authorized feature branch / pull request | Git commit and PR state |

## Automated acceptance

- The registered work-item reference is present.
- The current head matches the SHA whose map-specific and repository validation was inspected.
- Both required gates pass and the task outcome is verified before promotion.
- Promotion state is re-fetched and recorded; `COMMITTED`, `EXECUTED`, `VALIDATED`, and `PROMOTED` remain distinct.

## Human-only boundary

Do not add a routine human approval step here. Stop only when the requested operation requires an authorization listed in `docs/proposals/AGENTIC-PERMISSIONS.md` (credentials/provider login, destructive history operations, protected settings or permission grants, device-side state), or when a genuine policy conflict cannot be resolved. Follow the root FA-ADE auto-promotion rule whenever the repository permits it.
