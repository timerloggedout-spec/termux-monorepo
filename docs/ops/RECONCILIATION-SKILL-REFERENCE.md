# Reconciliation Skill Reference

This document mirrors the operational intent of `.github/skills/production-reconciliation/SKILL.md` for discoverability from the operations documentation tree.

**Loop:** RECON → PLAN → IMPLEMENT → COMMIT → WAIT → VALIDATE → RE-FETCH → CLASSIFY → REPEAT.

**Immutable identity:** resolve branch/tag/SHA inputs to commit SHAs before comparison; record merge-base, ahead/behind, changed paths, and UTC timestamps.

**Conflict safety:** diverged or ambiguous graphs stop. No force-push, reset, silent side selection, or evidence deletion.

**Recovery:** classify deletions before restoration. Preserve generated telemetry and provenance; restore authoritative source only when supported by repository history.

**Experiments:** compare candidates using identical suites and a fixed baseline; record experiment ID, candidate SHA, baseline SHA, suite, policy/task/cohort, result, and provenance.

**Coordination:** GitHub is authoritative for Git/PR/check evidence; Linear coordinates work; Notion provides human navigation; Hex analyzes experiments; Vercel supplies deployment evidence. Never treat one platform's success as proof of another's.
