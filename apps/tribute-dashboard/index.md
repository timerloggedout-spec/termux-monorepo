---
title: Tribute — Control Surface
description: Evidence and control surface for the upstream contributor lane, projecting repository evidence, receipts, pull requests, and generated status feeds.
last_updated: 2026-11-13
---

# Tribute — Control Surface

> Observe the upstream contributor lane from scout → claim → PR → follow-up → evidence → publication. This dashboard is a projection of repository evidence, not a second source of truth and not a MoneyBall admission score.

## What the dashboard contains

- Live board and KPI summary.
- Receipt-kind and receipt-outcome charts.
- Operator links to lane policy, workflow runs, generated evidence, and dashboard contracts.
- Tribute pull-request ledger with filters.
- Foreign open pull requests by the contributor.
- Tracked evidence receipts and workflow runs.
- Commit-derived lane evolution.
- Publication-lane verification.

The dashboard loads generated status and evidence feeds at runtime. If a feed is missing, stale, or still loading, treat that as an evidence gap rather than success or failure.

## Source of truth

- [termux-monorepo](https://github.com/timerloggedout-spec/termux-monorepo)
- [SHE dashboard PRD](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/SHE-DASHBOARD-PRD.md)
- [Tribute lane contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/TRIBUTE-LANE.md)
- [Dashboard deployment contract](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/TRIBUTE-DASHBOARD.md)

## Related dashboards

- [Lane matrix](https://timerloggedout-spec.github.io/matrix/)
- [Tracking](https://timerloggedout-spec.github.io/tribute/tracking.html)
- [Quota](https://timerloggedout-spec.github.io/tribute/quota.html)
- [Desk](https://timerloggedout-spec.github.io/tribute/desk.html)
- [3L0](https://timerloggedout-spec.github.io/tribute/3l0.html)
- [ATES](https://timerloggedout-spec.github.io/tribute/ates.html)

## Operating principle

Distinguish proposed, committed, executed, validated, and promoted states. A queued run is not completed; a commit is not proof of runtime execution; and a dashboard projection does not replace its source evidence.

## Sitemap

- [Site sitemap](https://timerloggedout-spec.github.io/sitemap.md)
- [Agent discovery index](https://timerloggedout-spec.github.io/llms.txt)
- [Project glossary](https://timerloggedout-spec.github.io/glossary.md)
