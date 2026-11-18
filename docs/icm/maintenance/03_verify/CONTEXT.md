# 03_verify — validate one proposed map change

One job: verify the proposed documentation change against ICM structure, canonical sources, and repository scope before it is eligible for promotion.

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
4. Inspect the diff to confirm it contains documentation-only changes and no application-code refactor.
5. Run the smallest relevant documentation checks, then the required repository and Termux smoke gates:
   - `python3 scripts/ci/repo_gate.py`
   - `python3 scripts/ci/termux_smoke.py`
6. Record command results, exact commit SHA, CI run/check identifiers, failures, and baseline blockers in `output/verification-record.md`.
7. Apply adaptive WAIT: inspect jobs/steps/logs/artifacts, re-fetch the current head, and repeat validation if the head changes. Never classify queued/in-progress as pass.

## Outputs

| Artifact | Location | Format |
|---|---|---|
| Verification record | `output/verification-record.md` | Markdown checklist with command output summaries, SHA/run linkage, and blockers |

## Automated acceptance

- All map-specific structural, link, source, twin, and scope checks pass.
- Required repository gates are green on the exact current head, or their failures are clearly classified as pre-existing baseline blockers and promotion remains blocked if policy requires them green.
- The task outcome is verified; commit existence or workflow completion alone is insufficient.
- No unresolved critical review thread or unclassified check failure remains.

No human read-through is required to mark this stage complete. Escalate only an actual human-only permission or policy boundary; otherwise repair, re-run the smallest relevant check, and record evidence.
