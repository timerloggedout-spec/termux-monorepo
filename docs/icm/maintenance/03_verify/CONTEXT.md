# 03_verify — validate one proposed map change

One job: verify the proposed documentation change against ICM structure, canonical sources, and repository scope before promotion eligibility.

## Inputs

| Kind | Path | Why |
|---|---|---|
| Working | [`../02_design/output/map-change-proposal.md`](../02_design/output/map-change-proposal.md) | Names the scoped change and expected source set; created by the prior stage. |
| Working | Changed files named by the proposal | The documentation under verification. |
| Reference | [`../../_shared/verification-checklist.md`](../../_shared/verification-checklist.md) | Defines repeatable structural, source, and scope checks. |
| Reference | [`../../CONTEXT.md`](../../CONTEXT.md) | Supplies the cold-walk and universe rules. |
| Governance | [`../../../../CLAUDE.md`](../../../../CLAUDE.md) and [`../../../../docs/ARCHW1Z-GATE.md`](../../../../docs/ARCHW1Z-GATE.md) | Define required validation and FA-ADE progression. |

## Process

1. Confirm the proposal maps to the authorized work item and the actual diff stays within its declared scope.
2. Resolve every relative map link and verify every `verified` card's canonical source citation.
3. Check catalog twins, context contracts, factory/product separation, and first-order effects.
4. Inspect the diff and confirm the documentation-only boundary.
5. Run the smallest relevant map-specific checks, including link, schema, twin, and scope validation.
6. Run local `repo_gate` and `termux_smoke` preflight when the worktree supports them; label these results as worktree preflight.
7. Record commands, results, candidate tree SHA, failures, and baseline blockers in `output/verification-record.md`. Exact-head CI run/check identifiers belong in the promotion record.
8. Classify queued/in-progress jobs as pending and require terminal success for passing status.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Verification record | `output/verification-record.md` | Markdown checklist with command output summaries, SHA/run linkage, and blockers |

## Automated acceptance

- All map-specific structural, link, source, twin, and scope checks pass.
- Map-specific checks pass and local gate preflight is recorded; exact-head repository gates are evaluated and recorded by the promotion stage.
- Verify the task outcome independently; track commit existence and workflow completion as separate state signals.
- Resolve every critical review thread and classify every required-check result.

Complete this stage through recorded evidence. Escalate actual human-only permission or policy boundaries; otherwise repair, re-run the smallest relevant check, and record evidence.
