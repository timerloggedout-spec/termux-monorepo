# ECC Plan Canvas adoption and demand-driven operations

Status: integration branch. No ECC App reactivation, global CLI installation, or
Platform201 deployment is performed.

## Decisions

1. Keep #175 as the durable operator-intent hub. Its October 19 priority snapshot
   is historical; the generated lane board is the live inventory. Do not use
   #175 as a recurring Matrix Doctor comment target.
2. Remove the ECC workflow's fixed cron, 6/12-hour debounce windows, manual
   workflow_dispatch, broad PR sweep, and scheduled analyze + doctor cycle.
   Retain authorized issue-label/comment commands and targeted PR harness events.
3. Bind PR audit idempotency to (PR, head SHA, audit kind). New SHAs are eligible
   immediately; duplicate deliveries for one SHA are no-ops. Bind issue/PR command
   idempotency to comment ID or label identity, not elapsed time.
4. Keep the generated lane board as matrix inventory SSOT. Its dispatch owner is
   quota-dispatch-tree (#1573), not the ECC workflow. Remove ECC's duplicate
   scheduled Matrix Doctor comments to #175.
5. Adopt the pinned ECC Plan Canvas skill locally. CLI availability is a separate
   runtime preflight; skill presence is not installation evidence.
6. Desk.html / designated GitHub Issues remain HITL authority. Canvas approval
   must be mirrored with artifact SHA-256 before implementation.
7. n8n is the parallel orchestration adapter. Platform201 remains optional hosting,
   not a scheduler or telemetry backend; current access evidence blocks automation.

## Why remove the timer

Issue #1573 establishes a quota-aware dispatch tree and says no new top-level cron
entry points. The ECC workflow's cron was a separate fixed schedule. Its event
surfaces already support demand-driven PR/issue actions, so remove the local timer
instead of adding another scheduler.

The lane-matrix sweep is the generated-board writer. Policy identifies the board
as live inventory and #175 as a hub. ECC's matrix-cycle duplicated the board
writer by posting analyze and doctor on #175 on a fixed schedule.

## Demand / idempotency

| Surface | Demand | Deduplication |
|---|---|---|
| Harness PR audit | relevant PR open/sync/reopen/ready event | PR + head SHA + audit kind |
| Issue command | authorized member comment | issue + comment ID |
| Issue label request | ECC label event | issue + label identity |
| PR operator command | authorized member comment | PR + comment ID |
| Matrix inventory | quota-dispatch-tree decision | lane watermark / sweep receipt |

No time-based suppression applies to new work. New SHAs and new explicit
operator requests are immediately eligible. Existing saturation handling and
least-privilege job permissions remain.

## Plan Canvas runtime

Skill: .agents/skills/plan-canvas/SKILL.md
Upstream: affaan-m/ECC@8321021c54d670126ce3b2969d5deb880b4b0c2a

ecc-plan-canvas from ecc-universal must be available in the local interactive
environment. GitHub Actions is headless. If the CLI is absent, use Desk.html /
Issue HITL and record the canvas path as blocked. Do not stack install methods in
one harness.

## Parallel n8n / Platform201

The existing n8n wiring is optional and adapter-only: GitHub remains canonical;
n8n receives sanitized metadata and emits receipts. Add a plan-review workflow
only as a separate least-privilege treatment, with webhook config external to Git.

Platform201 is not n8n. Existing repository evidence describes it as a visual
hosting/deployment graph and records no API token or Actions credential; OAuth
exchange was blocked. Keep a Platform201 blueprint treatment parallel, but do not
deploy or depend on it until authenticated access is independently verified.
Do not spend credits on a placeholder.

## Pre-merge verification

- YAML parses; ECC workflow has no schedule or workflow_dispatch.
- PR audit marker contains head SHA; fixed debounce constants are absent.
- Issue/PR command markers bind to triggering comment/label identity.
- matrix-cycle and broad scheduled sweep jobs are absent.
- Plan Canvas skill has frontmatter, upstream pin, HITL rules, and runtime preflight.
- Run repository dual gates on final PR head SHA. Keep ECC App suspended pending a
  separate measured reactivation decision.

Rollback by reverting the workflow commit. Do not restore a timer or time debounce
as a shortcut; retain event demand and SHA/comment idempotency.
