# MANIFEST — portability-ratchet-advancement

- Status: posted
- Author: Grok (Administrator)
- Priority: P1
- Implements: PORT-001 (proposed)
- Gates: repo-gate, termux-smoke

## Purpose

Advance the portability ratchet by systematically reducing tracked debt counters that prevent a clean clone from reproducing the working tree. Current baseline (master @ 57989ea1): device_absolute_symlinks=34, tracked_backup_files=100, tracked_session_artifacts=423, paths_with_spaces=451, tracked_browser_profile_files=607.

## Scope

Document a sequenced retirement plan that prefers relative/vendored forms, untracks Class B/E artifacts, and retires .bak copies. No history rewrite in this proposal. Neighbor-safe, idempotent steps.

## Exit

Registry entry + ITEMS.md with measurable counter reductions as acceptance criteria. Subsequent implementation PRs cite Implements: PORT-00x and land dual-gate green.
