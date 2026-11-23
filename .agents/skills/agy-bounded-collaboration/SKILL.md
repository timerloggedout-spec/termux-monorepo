---
name: agy-bounded-collaboration
description: Coordinate one issue-scoped Antigravity repository task using thin worktrees, explicit implementer/verifier handoffs, and evidence. Use when preparing or reviewing bounded agy work; never infer device identity or native agent registration from these instructions.
---

# Bounded Antigravity collaboration

1. Read repository governance, the registered proposal item, and `docs/proposals/active/antigravity-cli-provisioning/OPERATIONAL-PLAN.md`. Require that plan's identity gate before any phone-side operation. Never identify a handset by duplicate model labels. Exclude Origin and its backup.
2. Preserve existing High verbosity and auto-approve. Do not edit global settings, authentication, hooks, plugins, daemons, or schedules. Do not launch a model prompt merely to test readiness.
3. Use the existing issue worktree or preview `python3 scripts/antigravity/thin_worktree.py --help`. This is local Git tooling, not an agy integration or sandbox. Use a recorded full commit SHA and new task branch/destination. Inspect the dry-run before `--apply`; enabling Git's shared worktree-config extension requires the additional explicit `--enable-worktree-config` opt-in if absent. Never reset, clean, stash, or overwrite another worker's checkout.
4. Assign three responsibilities: coordinator scopes/accepts; implementer owns the only writable task branch; independent verifier inspects the resulting commit and executes focused tests without silently fixing it. These are handoff roles, not installed native subagents.
5. Copy `templates/task.json` relative to this skill directory into a private task record; replace all placeholders. Keep secrets, authentication/session URLs, device addresses, and unique identifiers out of tracked records. Require task/item, base SHA, allowed paths/actions, owner/verifier, acceptance, and exclusions.
6. Prioritize repository cartography, bounded implementation, independent verification, then documentation synchronization. Add specialists only for actual work. Do not install broad bundles or invent native-agent frontmatter without the installed build's verified contract.
7. Validate focused tests, proposal registry, repo-gate and Termux smoke. Distinguish Linux from native Android/Termux evidence. Report PASS/FAIL/UNKNOWN with commands, exit codes, commit and changed paths. Metadata or file presence never proves discovery, authentication, dispatch, or runtime operation.
8. Return the task result contract. Commit/push only the issue branch when authorized; never merge or enable auto-merge. Review cleanup with the owner; remove only the owned clean worktree using Git without force. Keep partial failures for inspection rather than deleting unfamiliar state.

For device rollout, wait for a verified SSH host key plus matching device-local facts, then observe supported version/help and discovery before deployment. Report repository skill delivery separately from on-device discovery and native-agent dispatch.
