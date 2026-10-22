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
related_prs: [1498]
related_branches: [cue/1497-antigravity-provisioning]
gates_required: [repo-gate, termux-smoke]
---
# Antigravity CLI provisioning

Deliver the issue-scoped research baseline, collaborative utilization proposal, and offline readiness inventory. Live device provisioning is not claimed.

## Authorization and review log

- Operator explicitly authorized issue-scoped GitHub implementation and pushing all resulting commits; no merge.
- Preserve existing high verbosity and auto-approve; do not launch model prompts, change live settings, touch Device 2 or Origin backup, or include unrelated shared-checkout work.
- Fresh staging base: `1a5af217f3ef9815ce31068d547ad28b69dd8ac7`.
- Linear unavailable; use the documented GitHub fallback and leave tracking unresolved/unmerged.
- Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6334445758
- Subsequent operator authorization: prepare operational collaboration surfaces and attempt Device 2 provisioning only after matching its pinned SSH key and device-local facts. This supersedes the earlier Device 2 exclusion conditionally, never the Origin/backup exclusion. No merge; preserve High verbosity/auto-approve and minimize model use.
- Follow-up registered before implementation: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6335987695. AGY-1497-04/06 remain blocked because SSH closes before host-key exchange. No phone writes or agy prompts executed.
- See [OPERATIONAL-PLAN.md](OPERATIONAL-PLAN.md) for full stages, review findings, thin-worktree adaptation, collaborator handoff, and acceptance/rollback. Repository skill delivery does not establish on-phone discovery or native-agent operation.

See [ITEMS.md](ITEMS.md), [source.md](source.md), and [PROPOSAL.md](PROPOSAL.md).
