---
id: multi-ai-webwrapper-hub
title: "Multi-AI provider selection and resumable web-wrapper connection hub"
author: Manus AI
posted_at: 2026-08-18
source: source.md
status: executing
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
  - id: Manus AI
    role: evidence-led executor
    status: executing
related_prs: [6, 48, 63, 162, 174, 204, 216, 221]
related_branches: [feature/multi-ai-webwrapper-provider-hub, feature/deepseek-waf-persistent-session]
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — multi-ai-webwrapper-hub

## Summary

This proposal adds a non-secret provider-selection and resumable connection checklist to `multi-ai-cli`. It integrates with, rather than replaces, the selected `deepcli` browser-session web-wrapper lineage. The work is deliberately narrow: it creates catalog and lifecycle metadata only, retains provider-owned manual connection paths, and does not duplicate the active `llm-api-hub` compatibility layer or adopt PR #6 wholesale.

## Reviewers

| ID | Role | Status | At | Notes |
|---|---|---|---|---|
| timerloggedout-spec | operator-authorizer | accepted | 2026-08-18 | Requested plan, execution, complete GitHub/Linear inventory, and correction to use the established web-wrapper lineage. |
| Manus AI | evidence-led executor | executing | 2026-08-18 | Completed the all-state GitHub/Linear map and traced the selected DeepCLI baseline. |

## Review log

### 2026-08-18 — Manus AI

- **Disposition:** accepted under operator authorization.
- **Evidence:** The all-state inventory shows that PR #6 is extract-only, PR #48 owns a separate compatibility-server track, and PR #216 / the current DeepCLI runtime own browser-session persistence. The selected baseline decision record confirms that the existing web-wrapper must be extended in place.
- **Promotion constraint:** The branch is based on current `master` because the selected runtime is absent from the currently older `master-staging`. Before promotion, reconcile it with the governed integration target as required by the baseline decision record.

## Checklist (process)

- [x] Registered in `docs/proposals/registry.yaml`
- [x] ITEMS.md itemized
- [x] Operator authorization recorded
- [x] Status set to executing for the bounded P1 work
- [ ] PR cites `Implements: MAWH-1`
- [ ] Gates green on merge
- [ ] Closed and moved to `closed/` when terminal

## Links

- ITEMS: ./ITEMS.md
- Source: ./source.md
- Full evidence snapshot: `docs/ops/MULTI_AI_WEBWRAPPER_HUB_INVENTORY.md`
