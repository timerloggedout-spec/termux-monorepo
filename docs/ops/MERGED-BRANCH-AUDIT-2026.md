# Merged Branch & Development Lane Audit Report (2026)

**Status:** COMPLETE
**Auditor:** Jules (Automated Systems Engineer)
**Date:** 2026-08-17
**SSOT Reference:** `docs/ops/LANE_CONSOLIDATION_SSOT.md`

## 1. Executive Summary
This audit provides visibility into merged branches, open development lanes, and unclosed pull requests across the Termux Monorepo. By aligning these lanes, we prevent code duplication, reduce workflow noise, and maximize ROI on our AI computation budgets. Work tracked under `Implements: RL-19`.
## 2. Lane Alignment Matrix (Open vs. Merged)
| Lane | Hanging Open PR | Merged / Superseding PR | Action Needed |
|---|---|---|---|
| **Lane 1: Performance (Bolt)** | PR #142 / PR #83 | PR #187 / PR #165 | Close hanging PRs as superseded |
| **Lane 2: Security (Sentinel)** | PR #141 / PR #106 | PR #186 / PR #194 | Close hanging PRs as superseded |
| **Lane 3: Reactive PWA (Palette)**| PR #140 / PR #108 | PR #165 / PR #193 | Close hanging PRs as superseded |
| **Lane 4: Team-Orchestration (MoneyBall)**| PR #131 | Built into `src/team_manager.py` | Align roster and verify betting stats |
| **Lane 5: Peer Routing & GHA (Grok/Jules)**| PR #147 / PR #143 | PR #193 / PR #203 | Review mailbox integration state |

## 3. Discrepancies and Skipped Reviews Audit
### [AUDIT-001] PR #142 (Bolt Telemetry Optimization) left hanging after PR #187 merged
- **Type:** Skipped Review / Hanging Open PR
- **Description:** PR #142 remains open and active on branch `bolt-telemetry-optimization-1970989343525795534`, but the underlying feature has already been merged via PR #187 on master-staging.
- **Justification in Git/PR History:** None documented. PR review was effectively bypassed by creating a new rebased PR without formal closure of the original.
- **Remediation Action:** Close PR #142 as superseded by PR #187.

### [AUDIT-002] PR #141 (Sentinel Symlink Safety) left hanging after PR #186 merged
- **Type:** Skipped Review / Hanging Open PR
- **Description:** PR #141 remains open on branch `sentinel-privilege-restrictions-16877168996669109419` while PR #186 was merged to fix Sentinel permissions.
- **Justification in Git/PR History:** None documented. Original reviews on PR #141 were left unanswered or bypassed by merging PR #186.
- **Remediation Action:** Close PR #141 as superseded by PR #186.

### [AUDIT-003] PR #154 (Linguist Overhaul CedrLang v2) left hanging after PR #196 merged
- **Type:** Skipped Review / Hanging Open PR
- **Description:** PR #154 remains open on branch `linguist-agentic-compression-perf-13775007783316480470` while PR #196 was merged to compile CedrLang v2.
- **Justification in Git/PR History:** None documented. Overlapping scope between Linguist branches left PR #154 in a dangling state.
- **Remediation Action:** Close PR #154 as superseded by PR #196.

### [AUDIT-004] PR #174 (DeepSeek integration) premature execution on ACK
- **Type:** Premature Summon / Missed Real Review
- **Description:** Jules triggered an auto-resolve run on CodeRabbit's acknowledgement comment ('I will re-review') rather than waiting for the substantive completed review.
- **Justification in Git/PR History:** Incomplete classification of bot comments led the orchestrator to treat ACK as a real review.
- **Remediation Action:** Update `calculate_lag_index.py` to support v2 disposition schema to block execution on `ack_pending` comments.

### [AUDIT-005] Test import path mismatch in test_sentinel_privileges.py
- **Type:** Test Suite Import Failure
- **Description:** `tests/test_sentinel_privileges.py` attempted to import `deepcli.core` directly instead of `deepcli.deepcli.core`, causing test failures when pytest was invoked without modifying PYTHONPATH.
- **Justification in Git/PR History:** Package structure refactoring created a nested `deepcli/deepcli` module structure while test imports retained legacy flat package paths.
- **Remediation Action:** Resolved by updating `test_sentinel_privileges.py` to import `deepcli.deepcli.core`.

### [AUDIT-006] Context collector relative path resolution and ast-grep missing pre-screen
- **Type:** Unhandled Edge Case / Test Failure
- **Description:** `src/context_collector.py` and `termux-multi-agent/src/context_collector.py` failed during test execution when target paths were outside `Path.home()` or when `ast-grep` was missing.
- **Justification in Git/PR History:** Temporary directory paths during pytest execution fall outside `/home/jules`, causing `ValueError` in `relative_to()`.
- **Remediation Action:** Hardened `_get_cached_signatures` and `assemble_minimized_bundle` to handle non-home subpaths gracefully and added `shutil.which('ast-grep')` pre-screening.

### [AUDIT-007] Mismatched verification contract handling in plan_promotion
- **Type:** Contract Error Handling / Test Failure
- **Description:** `she/promote.py` passed mismatched verification plans to `plan_repair_pr` before validating contract alignment, raising `RepairPRError` instead of `PromotionError`.
- **Justification in Git/PR History:** Validation sequence executed child plan binding after sub-plan construction rather than checking incoming contract preconditions.
- **Remediation Action:** Added early contract validation checks in `plan_promotion` to ensure `PromotionError` is raised directly on contract mismatch.

## 4. Local Git Repository Merges (Recent)
```
No merge commits found in recent logs.
```
