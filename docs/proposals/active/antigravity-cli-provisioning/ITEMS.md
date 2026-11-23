# Antigravity CLI work items — #1497

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-01 | Preserve seed research with provenance and verify key claims | Cue | done | Original seed retained; source-backed corrections separate from reported observations |
| AGY-1497-02 | Collaborative use cases and initial provisioning proposal | Cue | done | Bounded roles, handoff, stages, rollback, high verbosity and auto-approve preserved |
| AGY-1497-03 | Offline readiness inventory, tests, and dual-gate evidence | Cue | done | No prompts/config writes; missing prerequisites explicit; tests and gate outcomes recorded |

Issue: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497
Linear: unavailable (connector requires login); GitHub fallback per docs/LINEAR-AGENT-PROTOCOL.md §8. Do not fabricate TER IDs or merge.

Repository delivery evidence: [VALIDATION.md](VALIDATION.md). Done refers to the registered repository deliverables only; target-host provisioning and model pilots remain unexecuted. Proposal remains open for review and follow-up.

## Operational follow-up authorized by operator

| ID | Work | Owner | Status | Acceptance |
|---|---|---|---|---|
| AGY-1497-04 | Observe Device 2 through pinned identity gate | Cue | blocked | SSH host key and device-local facts match; no Origin access |
| AGY-1497-05 | Adapt thin worktree isolation, task handoff and scoped collaboration skill | Cue | done (repository only) | 14 focused tests, skill/registry and dual gates pass; full plan; no invented native-agent schema |
| AGY-1497-06 | Deploy and verify one bounded Device 2 pilot | Cue | blocked | Identity proven, build discovery confirmed, dispatch/result/verification/teardown evidence |

Registration: https://github.com/timerloggedout-spec/termux-monorepo/issues/1497#issuecomment-6335987695
New operator authorization supersedes the earlier blanket exclusion of Device 2 only after identity is proven. Origin and its backup remain excluded. A failed identity gate does not authorize changes.
