# V0 snapshot manifest — as-found Antigravity provisioning

**Snapshot label:** `AGY-PROVISIONING-V0-AS-FOUND`  
**Recorded date:** 2026-10-23  
**State:** documentary snapshot of available repository evidence; not a newly executed runtime snapshot  
**Parent RFP:** [#1567](https://github.com/timerloggedout-spec/termux-monorepo/issues/1567)

## Purpose and immutability

V0 preserves the rollout as it was found for fair comparison. It is not approved as the target architecture, not proof that initial instructions are correct, and not a claim that all provisioning is complete. Never rewrite this manifest to make a later candidate appear to have been present or validated at snapshot time. Corrections belong in a new versioned manifest or addendum.

## Source provenance

| Item | Recorded value | Interpretation |
|---|---|---|
| Repository | `timerloggedout-spec/termux-monorepo` | Repository containing source records |
| Staging base recorded in PR evidence | `1a5af217f3ef9815ce31068d547ad28b69dd8ac7` | Base used by the current operational follow-up; re-check before any future trial |
| PR | [#1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514) | Open/unmerged operational implementation; not the target design by default |
| PR head branch recorded in evidence | `cue/1497-operational-device2` | Live implementation branch at the time of the cited evidence |
| PR head SHA | `dbb302b5aa4ac21d27de9e34bf16b22914076109` | Historical recorded head; verify current PR head before using it as an immutable source ref |
| Tracking issue | [#1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497) | Operational history and evidence |
| Research/decision lane | [#1567](https://github.com/timerloggedout-spec/termux-monorepo/issues/1567) | MVT / DoE / TLM / Moneyball / Delphi protocol |
| Evidence files at historical PR #1514 head | See immutable path/blob ledger below | Blob SHAs are anchored to historical head `dbb302b5aa4ac21d27de9e34bf16b22914076109`, not current branch names |

**Provenance caveat:** these refs and statuses were recorded in the available issue/PR material. This documentation commit does not assert that the PR head is unchanged now. Before a trial, record the current API-returned head SHA and content hashes for every source file actually used.

### Immutable evidence-file identity ledger

The following paths and blob SHAs were fetched at historical PR #1514 head `dbb302b5aa4ac21d27de9e34bf16b22914076109`. Use these exact identities when reconstructing the recorded baseline; if a future trial uses different content, record the new commit/blob identity separately.

| Repository-relative path | Blob SHA at historical head |
|---|---|
| `docs/proposals/active/antigravity-cli-provisioning/MANIFEST.md` | `eb299d4b860e7a5e41651cb3e3f2df06f695ff65` |
| `docs/proposals/active/antigravity-cli-provisioning/OPERATIONAL-VALIDATION.md` | `6f6e62473273dd02cb9e81a082127e15195b998f` |
| `docs/proposals/active/antigravity-cli-provisioning/FILTERING-VALIDATION.md` | `bd63f421cd25ff2ec46bc3a330ceafbc04d9d7a6` |
| `docs/proposals/active/antigravity-cli-provisioning/SECONDARY-RECOVERY.md` | `46c2d0d2d4e34838cfc53388e410884514d25dc4` |
| `docs/proposals/active/antigravity-cli-provisioning/FILTERING.md` | `3f02060d3f2313d2dd8ed9c1673661f06d2618f4` |

## Environment and authorization context

- Target described in the operational evidence: secondary Termux device `tmx-node-55619bd5`; the separate Origin device `tmx-node-primary` is excluded from the recorded work.
- Existing pinned SSH/sshd collaborator access and in-progress `agy` provisioning are part of the as-found operational context. This record does not retroactively prohibit those activities.
- Operational records report Antigravity CLI 1.4.5 on the secondary, a dedicated secondary worktree, and a controller-side stream filter.
- The records distinguish controller Linux/Python checks from native Android/Termux evidence. A Linux smoke test is not native Termux validation.
- This snapshot authorizes no new SSH session, device command, model request, settings mutation, installation, or scope expansion. Each future trial must state the operator/collaborator authorization it relies on and its precise action boundary.

## As-found implementation surfaces

The current PR's changed-file list included:

- Agent/skill definitions: `.agents/agents/agy-implementer.md`, `.agents/agents/agy-verifier.md`, `.agents/skills/agy-native-pilot/SKILL.md`
- Proposal and operational documentation under `docs/proposals/active/antigravity-cli-provisioning/`
- Controller-side tooling: `scripts/antigravity/access_preflight.py`, `capture.py`, `readiness.py`, `run.py`, `settings.py`, `telemetry.py`
- Secondary recovery and pilot scripts under `scripts/antigravity/`
- Deterministic tests under `tests/test_agy*.py` and `tests/test_antigravity_readiness.py`
- Proposal registry update: `docs/proposals/registry.yaml`

This list is a scope inventory from the recorded PR file list, not a substitute for a fresh diff review.

## Evidence snapshot: observed, failed, and unknown

### Recorded positive observations

- A bounded CLI pilot was reported successful at an earlier checkpoint, with a created output independently checked byte-for-byte.
- Pinned SSH identity and secondary-device identity checks passed during recovery; Origin was not contacted.
- The dedicated secondary SSH service recovery procedure and a supervised-child restart were exercised.
- Controller-side deterministic tests, Bash syntax checks, registry validation, repository gates against the stated staging base, and Linux smoke tests were reported passing at their respective checkpoints.

### Recorded counter-evidence and limitations

- A later implementer stream ended **INCOMPLETE** with producer exit code 255; terminal usage and model/token totals were unknown.
- The sequential verifier completed with exit 0, but its review PASS was contradicted by deterministic tests: quota `NaN` was accepted and returned INCOMPLETE/2 instead of rejection with 64. A controller repair was then reported, with regression cases for `NaN`, `Infinity`, and `-Infinity`.
- Earlier and later test counts differ because they represent different revisions/checkpoints. Never combine them into a single current test count.
- Termux:Boot was installed, but first-launch activation and reboot delivery were unverified.
- Whole-app/Android force-stop recovery was not established.
- Native enumeration/skill UI discovery, internal manifest/tool-restriction loading, nested delegation, and full-repository provisioning remained unverified.
- ShellCheck was unavailable in the recorded environment. Hosted CodeQL/PR checks were not claimed by local gates.
- A successful CLI invocation does not by itself prove that the intended manifest, tool restrictions, or role configuration were loaded.

## Snapshot completeness checklist

Before V0 is used as a reproducible experiment input, a snapshot owner should append a **new** snapshot revision with:

- [ ] Current PR head SHA, base SHA, branch, state, and timestamp retrieved from GitHub.
- [ ] Exact source file paths and blob SHAs for each instruction/config/script under test.
- [ ] Environment inventory: OS/device identity class, Termux/Android version where available, CLI version, runtime/tool versions, and relevant feature availability.
- [ ] Redacted command/fixture IDs and expected outputs; no private prompt, credential, token, host key, or unrelated workspace data.
- [ ] Existing run receipts linked by stable ID and labeled historical/current, native/controller, real/synthetic.
- [ ] Known failures, unavailable checks, and open questions copied forward without being recast as passes.
- [ ] Snapshot hash or signed/immutable artifact location, retention rule, owner, and reviewer.

## Change control

The V0 snapshot is frozen by reference, not by assuming a branch will never move. Prefer immutable commit SHAs and blob SHAs. If a referenced branch changes, retain the old SHA and create a new revision. Do not force-push, reset shared worktrees, or mutate the live operational candidate merely to make the research record tidy.
