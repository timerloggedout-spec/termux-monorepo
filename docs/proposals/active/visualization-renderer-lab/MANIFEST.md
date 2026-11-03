---
id: visualization-renderer-lab
title: "Dashboard surfaces and comparative visualization renderer lane"
author: ChatGPT
posted_at: 2026-11-02
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: [1571]
related_prs: []
related_branches: [research/visualization-renderer-lab]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — visualization-renderer-lab

## Summary

Audit the web surface inventory and introduce an isolated, reproducible comparison lane for D3.js and alternative graph/chart renderers. The canonical dashboard and its committed-feed evidence contracts remain authoritative. This proposal is tracked in-repository at the Operator's explicit direction; Linear issue creation is intentionally skipped.

## Reviewers

| ID | Role | Status | At | Notes |
|----|------|--------|-----|-------|
| timerloggedout-spec | operator-authorizer | accepted | 2026-11-02 | Explicit takeover; Linear usage skipped |

## Review log

### 2026-11-02 — ChatGPT
- Disposition: executing
- Notes: isolated renderer cohort and baseline lab scaffold; no production deployment or data mutation.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [ ] At least one non-author implementation review recorded
- [ ] Shared-fixture renderer implementations complete
- [ ] Gates green on merge
- [ ] Selective promotion reviewed separately

## Links

- Existing visualization RFP: https://github.com/timerloggedout-spec/termux-monorepo/issues/1571
- Telemetry visualization recon: https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/TELEMETRY-VIZ-RECON.md
- ITEMS: ./ITEMS.md
- Source: ./source.md
