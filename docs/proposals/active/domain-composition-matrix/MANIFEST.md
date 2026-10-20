---
id: domain-composition-matrix
title: "Domain composition matrix: versioned research database for composition rules"
author: timerloggedout-spec
posted_at: 2026-10-04
source: docs seed on master (schema.sql, seed.json, README.md)
status: posted
priority: P2
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: posted
related_prs: []
related_branches: []
gates_required: [repo-gate]
---

# MANIFEST — domain-composition-matrix

## Summary

Registers the domain composition research database that already exists under `docs/proposals/active/domain-composition-matrix/`. The directory was an orphan: `proposal-lifecycle` run 37189499693 failed with `orphan active dir (not in registry): domain-composition-matrix` because `registry.yaml` did not name it and `MANIFEST.md` / `ITEMS.md` were absent.

This proposal does not claim the seed is validated research. It makes the on-disk layout match the registry contract so push of `docs/proposals/**` can pass `scripts/proposals/validate_registry.py`.

## Scope

- Schema and seed stay research artifacts (`schema.sql`, `seed.json`).
- No runtime authority over notation or execution paths.
- Evidence of closure is a green `proposal-lifecycle` validate-registry job on this SHA.
