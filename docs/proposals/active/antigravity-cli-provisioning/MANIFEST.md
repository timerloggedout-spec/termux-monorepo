---
id: antigravity-cli-provisioning
title: "Antigravity CLI collaborative use cases and initial provisioning"
author: Cue
posted_at: 2026-10-22
source: source.md
status: executing
priority: P2
reviewers: []
related_issues: [1497]
related_prs: [1498, 1514]
related_branches: [cue/1497-antigravity-provisioning, cue/1497-operational-device2]
gates_required: [repo-gate, termux-smoke]
---
# Antigravity CLI provisioning

Deliver the issue-scoped research baseline, collaborative utilization proposal, and readiness inventory. Secondary-only project files and SSH recovery are deployed; full provisioning and production-task success are not claimed.

## Authorization and review log

- Operator explicitly authorized issue-scoped GitHub implementation and pushing all resulting commits; no merge.
- Preserve existing high verbosity and auto-approve; do not launch model prompts, change live settings, touch Device 2 or Origin backup, or include unrelated shared-checkout work.
- Fresh staging base: `1a5af217f3ef9815ce31068d547ad28b69dd8ac7`.
- Linear unavailable; use the documented GitHub fallback and leave tracking unresolved/unmerged.
- Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6334445758

See [ITEMS.md](ITEMS.md), [source.md](source.md), and [PROPOSAL.md](PROPOSAL.md).

## Subsequent operational authorization and evidence

- Operator requested operational secondary provisioning; earlier blanket Device 2 exclusion is superseded only after pinned identity verification. Origin remains excluded; no merge or global settings changes.
- AGY-1497-07/08 registered in issue #1497 before implementation; Linear still unavailable, documented GitHub fallback retained.
- Isolated follow-up branch `cue/1497-operational-device2` preserves concurrent edits in the original issue checkout and the unrelated shared checkout.
- One secondary CLI 1.4.5 pilot succeeded and exact output was independently verified. Native enumeration remains inconclusive. The later recovery restored High; the later bounded implementer/verifier continuation is recorded separately in [FILTERING-VALIDATION.md](FILTERING-VALIDATION.md). Nested dispatch remains unverified.
- Full plan, reviews, changed surfaces and rollback: [OPERATIONAL.md](OPERATIONAL.md). Executed checks and runtime evidence: [OPERATIONAL-VALIDATION.md](OPERATIONAL-VALIDATION.md). Full provisioning is not claimed.

## Approved High-verbosity filtering continuation

- Operator's “Fix it; we decided on programmatic filtering layer” authorizes the narrow saved `low` → `high` correction on freshly identity-verified Device 2, superseding the earlier no-settings-write restriction only for that key. Existing enabled auto-approve and all unrelated settings must remain unchanged. Origin and its backup are still excluded.
- AGY-1497-09 is registered on GitHub #1497; live PR #1514 head confirmed as `cue/1497-operational-device2`, base `master-staging`. Do not push this work to the older provisioning branch by mistake. Do not merge.
- Integrate the existing no-model telemetry prototype as a passive full-private-capture plus concise-steering layer. The owner subsequently authorized exactly one bounded implementer and one sequential verifier; both have run. No additional model prompts or pilot replays are authorized.
- The earlier offline blocker is superseded by [secondary recovery](SECONDARY-RECOVERY.md): pinned SSH recovered and High was restored with approval settings preserved. Project files are live at `~/.local/share/agy-1497-secondary/worktree`. The implementer stream ended INCOMPLETE at transport exit 255, with unknown model/token totals; the verifier's PASS was contradicted by the deterministic quota regression. [Contract](FILTERING.md) and [validation](FILTERING-VALIDATION.md) separate device evidence from production success claims.

## Controller telemetry and archive follow-up

- The owner requested controller-side implementation of immediate sanitized event telemetry, an encrypted archive/JIT path, and an opt-in Hindsight-related outbox; `agy` is not the implementer.
- Scope is limited to code, JSON schemas, synthetic tests, and operational/status documentation on PR #1514. Do not connect to Device 2 or Origin, issue an AGY prompt, use Remote, replay the incomplete stream, or contact Hindsight.
- Hindsight remains disabled by default, with no endpoint or API credential configured. Real archive activation is blocked until an externally supplied age recipient/identity setup is available. No runtime archive, key, payload, transcript, tool data, or session log belongs in Git.
- Recheck PR head/reviews/checks before a scoped push. Keep the PR open and unmerged; do not update the issue body until repository checks pass.
- See [TELEMETRY-PIPELINE.md](TELEMETRY-PIPELINE.md) for the status map, schemas, API/privacy boundary, and remaining activation gates.
