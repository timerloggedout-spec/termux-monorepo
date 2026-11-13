---
name: termux-mcp-project-steward
description: Operate a constrained Android Termux agentic hub alongside GitHub repository projects for health checks, PR and issue stewardship, lean worktrees, device resource triage, tunnel-aware MCP operations, and safe project reporting.
---

# Termux MCP Project Steward

Use this skill to steward GitHub projects through a connected Android Termux MCP while preserving device resources and repository hygiene.

## Operating modes

- **Read-only:** inspect device health, tunnel availability, Git status, branches, pull requests, issues, checks, and project metadata.
- **Apply:** perform an explicitly requested worktree, file edit, commit, push, pull request, comment, service restart, or scheduled job.
- State the intended write set before apply operations.
- Reserve merges, closures, deletions, force-pushes, credential changes, swap creation, and data clearing for separately authorized operations.

## Preflight

1. Confirm the Termux MCP is available and call `get_device_info`.
2. Confirm the result identifies the Android device and intended project.
3. Inspect the MCP tunnel or SSH route when the task requires it. Treat reverse-tunnel endpoints as temporary runtime state.
4. Keep endpoints, ports, host keys, private keys, tokens, and credentials outside tracked files.
5. Find the repository root and run the tracked resource snapshot when present:

```sh
./scripts/termux-resource-snapshot.sh
```

6. Record the pressure level and relevant figures: available memory, free swap, storage use, and top-process summary.
7. At storage use of 95% or higher, pause nonessential cloning, package installation, cache creation, and artifact generation. Produce a concise pressure report and request remediation approval.

## Lean repository discipline

- Treat the main Termux home checkout as potentially dirty.
- Create a separate Git worktree outside the home checkout for repository edits.
- Keep MCP source checkouts, virtual environments, caches, models, exported sessions, local tunnel state, and generated logs outside tracked worktrees.
- Add source, concise documentation, and small deterministic scripts to Git.
- Use a submodule when the repository must pin and build a reviewed external source dependency.
- Before committing, run `git diff --check`, the smallest relevant test, and `git status --short` in the isolated worktree.

## Daily stewardship workflow

Collect evidence in this order:

1. **Device health:** run the resource snapshot and record `OK`, `PRESSURE`, or a named blocker.
2. **Repository state:** identify the target base branch, active worktrees, tracked changes, oversized artifacts, and relevant untracked files.
3. **GitHub project state:** review open pull requests, requested reviews, failing checks, relevant issues, and stale branches or worktrees.
4. **Prioritization:** select up to five actions, ordered by risk and unblock value.
5. **Output:** use `templates/daily-stewardship-report.md`.

## Local resource sentinel

Use `templates/local-resource-sentinel.sh` as the on-device schedule payload. It invokes the tracked snapshot script and sends a Termux notification when the result is `PRESSURE`.

Schedule the sentinel with the Android job scheduler at a six-hour cadence and when battery state permits. Use a fixed project-scoped job ID and inspect pending jobs before replacing one. Use deterministic device scheduling for deterministic resource checks.

## Daily AI stewardship schedule

Maintain one daily recurring task at a time, at a time selected by the user. Use the Termux MCP and GitHub integration for the read-only workflow above. Keep the schedule self-contained and reserve external writes for a fresh explicit instruction.

## Apply workflow

1. Create a clean worktree from the requested remote base branch.
2. Make the smallest complete change.
3. Run the relevant validation.
4. Commit with the repository identity already configured on the device.
5. Push the feature branch.
6. Create a pull request when requested.
7. Report branch, commit, PR URL, changed files, validation, and remaining device pressure.

## References

- `CLAUDE.md`
- `SKILLS.md`
- `docs/ops/SKILLS-INVENTORY.md`
- `.agents/skills/adaptive-wait/SKILL.md`
- `.agents/skills/adaptive-feedback-cycle/SKILL.md`
- `docs/ops/DO-STATEMENT-MANDATE.md`

## Style

Write instructions as direct DO statements. Use registered Siglary operators only when their meanings remain clear. Keep state claims adjacent to their evidence receipt.
