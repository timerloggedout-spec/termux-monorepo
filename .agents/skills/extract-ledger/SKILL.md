---
name: extract-ledger
description: Component-by-component extract of dirty mega-PRs. Triggers on Issue #502, #263, extract-only, or wholesale merge rejection.
---

# Skill: extract-ledger

Never merge dirty mega-PRs wholesale. Partition by directory,
rank by gate-risk, drop hunks already on master, land small green
PRs, then close the parent as superseded-by-extraction.

Ledger: `docs/ops/EXTRACT-LEDGER-502.yaml`.
