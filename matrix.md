---
title: LANE-MATRIX
description: Live board for monorepo pull-request lanes, showing lane assignment, age, reason, and source-backed status. Separate from Tribute.
last_updated: 2026-11-13
---

# LANE-MATRIX

> Live board for the monorepo pull-request lanes. This is a lane-status projection, not a pull request and not the Tribute contributor dashboard.

The HTML dashboard loads its live rows from the generated lane-matrix status data in the termux-monorepo repository. If the page says “Loading matrix” or the feed is unavailable, treat the current state as unobserved rather than guessing.

## What this page shows

- Pull request identifier and title.
- Lane assignment.
- Age in days.
- Recorded reason for the lane assignment.
- Aggregate lane status metrics when the source feed supplies them.

## Source of truth

- [Generated lane matrix status JSON](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/generated/lane-matrix-status.json)
- [Lane matrix operating policy](https://github.com/timerloggedout-spec/termux-monorepo/blob/master/docs/ops/LANE-MATRIX.md)
- [termux-monorepo](https://github.com/timerloggedout-spec/termux-monorepo)

## Related surfaces

- [Tribute operations dashboard](https://timerloggedout-spec.github.io/tribute/)
- [Main site](https://timerloggedout-spec.github.io/)
- [Project glossary](https://timerloggedout-spec.github.io/glossary.md)

## Sitemap

- [Site sitemap](https://timerloggedout-spec.github.io/sitemap.md)
- [Agent discovery index](https://timerloggedout-spec.github.io/llms.txt)
