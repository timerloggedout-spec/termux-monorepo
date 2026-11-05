---
name: plan-canvas
description: Annotated browser review for local plans and HTML artifacts, with Desk.html / GitHub Issues retained as HITL authority.
metadata:
  version: "1.0.0"
  origin: "ECC"
  upstream: "affaan-m/ECC@8321021c54d670126ce3b2969d5deb880b4b0c2a"
---

# Plan Canvas

Use the ECC Plan Canvas loop for substantial plans, architecture proposals, handoffs,
and visual reports when anchored feedback is materially better than prose comments.

**Authority boundary:** Desk.html or the designated GitHub Issue remains the durable
HITL record. A canvas verdict must be mirrored to that surface with an artifact
SHA-256 before implementation. Canvas approval never overrides repository policy,
branch protection, credentials, dual-gate, or current-SHA requirements.

## Use / do not use

Use for multi-phase plans, trade-offs, diagrams, or local Markdown/HTML artifacts.
Do not use for code-diff review, running web apps, remote URLs, routine triage,
simple edits, or headless CI. Keep the review artifact local and secret-free.

## Runtime preflight

The upstream ecc-plan-canvas CLI is shipped by ecc-universal. Verify it in
the local environment that owns the artifact:

    command -v ecc-plan-canvas
    ecc-plan-canvas --help

Claude plugin fallback:

    node "$CLAUDE_PLUGIN_ROOT/scripts/plan-canvas.js" --help

Skill presence does not prove the CLI is installed. If unavailable, record
BLOCKED: plan-canvas runtime unavailable and use Desk.html / Issue HITL instead.
Do not install global packages or alter a user's runtime without authorization.
GitHub Actions is headless and is not the interactive canvas host.

## Review loop

Create the plan in the lane's established location, normally
.claude/plans/<topic>.plan.md. Do not include credentials, private session state,
or unredacted customer data.

    ecc-plan-canvas open .claude/plans/feature.plan.md
    ecc-plan-canvas await .claude/plans/feature.plan.md

Keep await parked as a background task when supported. Feedback arrives only
while a listener is active; ecc-plan-canvas pending lists queued feedback.

Feedback types:
- chat: freeform message; answer in the canvas.
- annotation: anchored feedback; inspect selector, snippet, and text range.
- verdict: approve or request-changes.

Reply in the canvas and keep listening:

    ecc-plan-canvas await .claude/plans/feature.plan.md --reply "I revised the dependency order."

During long revisions, update activity:

    ecc-plan-canvas typing .claude/plans/feature.plan.md --state thinking
    ecc-plan-canvas typing .claude/plans/feature.plan.md --state typing

Edit the artifact; it live-reloads. Do not re-run open to refresh. Finish with:

    ecc-plan-canvas end .claude/plans/feature.plan.md

request-changes means revise and continue awaiting. approve means the canvas
review is approved, then mirror the verdict to Desk.html / Issue with artifact path,
SHA-256, verdict, platform-supplied reviewer identity, timestamp, and conditions.
If the user ends the session (endedBy: user or sessionEnded: true), stop and do
not reopen unless asked. No active listener means feedback is not yet delivered.

## Diagrams and runtime behavior

Use fenced Mermaid for architecture, sequence, state-machine, ER, or dependency
diagrams when useful. Mermaid may load from a pinned CDN; for air-gapped use set
ECC_PLAN_CANVAS_MERMAID_URL to a trusted local mirror.

Markdown uses the ECC plan template; HTML renders as authored with annotations.
Keep sibling assets beside the artifact. Server defaults: loopback
127.0.0.1:4517, 30-minute idle timeout (ECC_PLAN_CANVAS_IDLE_MS), state under
~/.claude/plan-canvas/ (ECC_PLAN_CANVAS_STATE_DIR). Consume feedback JSON from
await; do not inspect local state files, tight-loop await --timeout-ms, or end
a turn with an open review and no listener.

## Parallel n8n / Platform201 treatment

n8n is the viable parallel adapter because this repository already has ops/n8n/
and a documented sanitized GitHub workflow-run intake. GitHub remains canonical.
n8n may route sanitized plan metadata, notify reviewers, and capture receipts; it
must not become a second evidence ledger. Keep webhook URLs and credentials out
of Git; never send prompts, completions, secrets, or repository tokens.

Platform201 is an optional host/deployment surface, not an assumed workflow engine
or telemetry backend. Current repository evidence records no usable API token /
Actions credential and a blocked OAuth exchange. Do not claim automated deploy or
make it an execution dependency until authenticated access is verified. Keep the
two treatments parallel; neither silently replaces the other.

## Provenance

Upstream: affaan-m/ECC/skills/plan-canvas/SKILL.md, commit
8321021c54d670126ce3b2969d5deb880b4b0c2a (MIT). This local adaptation adds
project HITL, evidence, and adapter boundaries. Review upstream changes explicitly;
do not auto-sync over local policy.
