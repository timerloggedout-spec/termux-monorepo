# ECC Plan Canvas adoption and demand-driven operations

Status: integration branch. No ECC App reactivation, global CLI installation, or
Platform201 deployment is performed.

## Decisions

1. Retire #175 from operational authority. Preserve it as a historical October 19
   snapshot only. No generic issue is the control-plane hub or state database.
   The cross-domain lane×project record is REPO-TRACKING; the Lane Matrix is the
   narrower PR-disposition projection.
2. Remove the ECC workflow's fixed cron, 6/12-hour debounce windows, manual
   workflow_dispatch, broad PR sweep, and scheduled analyze + doctor cycle.
   Retain authorized issue-label/comment commands and targeted PR harness events.
3. Bind PR audit idempotency to (PR, head SHA, audit kind). New SHAs are eligible
   immediately; duplicate deliveries for one SHA are no-ops. Bind issue/PR command
   idempotency to comment ID or label identity, not elapsed time.
4. Keep the generated Lane Matrix as the PR-disposition board, not a global
   lane×project SSOT. REPO-TRACKING owns the cross-domain lane×project projection.
   Remove ECC's duplicate scheduled Matrix Doctor comments and remove the Lane
   Matrix from the quota-dispatch polling tranche.
5. Adopt the pinned ECC Plan Canvas skill locally. CLI availability is a separate
   runtime preflight; skill presence is not installation evidence.
6. Desk.html / designated GitHub Issues remain HITL authority. Canvas approval
   must be mirrored with artifact SHA-256 before implementation.
7. n8n is the parallel orchestration adapter. Platform201 remains optional hosting,
   not a scheduler or telemetry backend; current access evidence blocks automation.

## Why remove the timer

Issue #1573 establishes a quota-aware dispatch tree, but its ten-minute wake cycle
is still polling. The Lane Matrix was incorrectly attached to the q6 tranche and
therefore inherited a six-hour refresh dependency. Remove that coupling entirely.

The PR-disposition materializer now wakes on pull_request_target lifecycle events.
It coalesces bursts by concurrency cancellation, reads the current open-PR set,
and writes only when the derived artifact changes. There is no ten-minute matrix
poll, six-hour matrix sweep, elapsed-time debounce, or manual dispatch.

The Lane Matrix is not the cross-domain state store. REPO-TRACKING owns the
lane×project projection; domain lifecycle records remain authoritative; lane-events
is execution evidence. #175 is historical only.

## Demand / idempotency

| Surface | Demand | Deduplication |
|---|---|---|
| Harness PR audit | relevant PR open/sync/reopen/ready event | PR + head SHA + audit kind |
| Issue command | authorized member comment | issue + comment ID |
| Issue label request | ECC label event | issue + label identity |
| PR operator command | authorized member comment | PR + comment ID |
| PR disposition | pull_request_target lifecycle event | concurrency coalescing + current-state recomputation |

No time-based suppression applies to new work. New SHAs and new explicit operator
requests are immediately eligible. Matrix inventory is no longer dispatched by
the quota tree. Existing saturation handling and least-privilege permissions
remain. Outbound ECC commands additionally require
repository variable ECC_TOOLS_APP_ENABLED=true; unset/false keeps the lane quiet
while the hosted App is suspended. Reactivation is a separate, measured decision.

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
- ECC matrix-cycle and broad scheduled sweep jobs are absent.
- Lane Matrix has pull_request_target lifecycle events only; no schedule or dispatch.
- Lane Matrix is removed from dispatch_q6 and age does not change disposition.
- Plan Canvas skill has frontmatter, upstream pin, HITL rules, and runtime preflight.
- Run repository dual gates on final PR head SHA. Keep ECC App suspended pending a
  separate measured reactivation decision.

Rollback by reverting the workflow commit. Do not restore a timer or time debounce
as a shortcut; retain event demand and SHA/comment idempotency.
