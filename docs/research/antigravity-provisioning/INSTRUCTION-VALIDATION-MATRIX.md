# Provisioning-instruction validation matrix

**Baseline:** `AGY-PROVISIONING-V0-AS-FOUND`  
**Sources:** [PR #1514](https://github.com/timerloggedout-spec/termux-monorepo/pull/1514), [issue #1497](https://github.com/timerloggedout-spec/termux-monorepo/issues/1497), [RFP #1567](https://github.com/timerloggedout-spec/termux-monorepo/issues/1567)  
**Status:** initial triage from recorded evidence; not a fresh device audit.

## Classification rules

- **Verified:** repeatable evidence supports the claim for the stated version and environment.
- **Contradicted:** evidence directly conflicts with the claim.
- **Unverified:** available evidence does not establish it.
- **Proposal:** intended design, not observed capability.

Never generalize controller-Linux results to native Android, a successful command invocation to correct internal configuration loading, or a historical pass to the current source revision.

| ID | Claim | Initial classification | Qualifier / disposition | Evidence boundary | Next validation |
|---|---|---|---|---|---|
| IV-001 | Current rollout is the gold standard. | **Contradicted** | Governance rule rejected | RFP #1567 explicitly defines the rollout as V0, a comparison candidate. | Preserve V0; derive candidates from validated requirements. |
| IV-002 | Recorded secondary CLI version and flags are known. | **Verified** | Scoped to recorded environment/checkpoint | Operational notes report version 1.4.5 and installed help for agent, effort, timeout, output format, print, and agents options. | Capture current version/help and hashes before any future trial. |
| IV-003 | The bounded JSON pilot created the expected artifact. | **Verified** | Historical only | Notes report a single request and independent byte-for-byte output check. | Retain as historical evidence; do not treat it as production-task success. |
| IV-004 | The filter consumed real stream-json. | **Verified** | Scoped to reported controller-side run | Validation notes report actual stream-json through the controller-side filter. | Preserve receipt and source hashes; do not fabricate telemetry. |
| IV-005 | The delegated implementer completed successfully. | **Contradicted** | Receipt incomplete | Receipt was INCOMPLETE, producer exit 255, terminal usage absent and token totals unknown. | Do not infer success; any new run needs its own authorization and hypothesis. |
| IV-006 | Verifier PASS establishes quota correctness. | **Contradicted** | Independent deterministic test contradicted verifier | Deterministic tests found NaN accepted despite a verifier PASS. | Treat tests and review as distinct evidence; test the exact repaired revision. |
| IV-007 | Non-finite quota repair works. | **Verified** | Reported controller-test scope; fresh audit pending | Notes report NaN and ±Infinity regression tests and 93 focused tests passing at that checkpoint. | Confirm current source SHA and rerun focused tests/gates in CI. |
| IV-008 | Boot hook delivery after reboot works. | **Unverified** | — | Package installation was confirmed; first-launch activation and reboot delivery were not. | Owner-authorized native trial with explicit observable result and rollback. |
| IV-009 | Recovery survives whole-app force-stop. | **Unverified** | No guarantee supported by current evidence | Evidence covers a supervised child restart while the service manager survives. | Do not claim support without a separately authorized, observable trial. |
| IV-010 | Native agent/skill discovery works. | **Unverified** | — | Initial enumeration output was empty; explicit agent invocation does not prove discovery. | Version-specific read-only discovery receipt. |
| IV-011 | Internal manifest/tool restrictions load as intended. | **Unverified** | — | Invocation alone is insufficient proof. | Non-destructive allowed/denied contract fixtures. |
| IV-012 | Nested delegation works end-to-end. | **Unverified** | — | Operational notes leave nested dispatch unresolved. | Minimal isolated handoff fixture and bounded output assertions. |
| IV-013 | Full monorepo provisioning is complete. | **Unverified** | Existing evidence only shows a small issue-specific source set transferred to a miniature repository | Notes say only a small issue-specific source set was transferred to a miniature repository. | Separate candidate hypothesis, dependency inventory and isolated trial. |
| IV-014 | Linux smoke proves native Termux compatibility. | **Contradicted** | Platform scope mismatch | Recorded smoke ran on Linux with Termux detection false. | Label platform in every receipt; test native-only claims separately. |
| IV-015 | ShellCheck passed. | **Contradicted** | Tool unavailable in recorded environment | ShellCheck was unavailable; Bash syntax checks were reported. | Run it in CI or retain an explicit unavailable status. |
| IV-016 | Local repo gate proves hosted checks passed. | **Contradicted** | Local/hosted validation are separate evidence | Notes do not claim hosted CodeQL/PR checks from local gates. | Query current PR checks by exact commit SHA. |
| IV-017 | Existing authorized collaborator access is prohibited by this research lane. | **Contradicted** | Existing scope is recorded; no new scope is granted | RFP records existing authorized access and ongoing provisioning; it grants no new scope. | Represent current authorization accurately; approve expansions separately. |
| IV-018 | Multi-factor changes can always be compared cleanly. | **Proposal** | Rejected as default design | RFP calls for factor isolation where practical and comparable budgets/scenarios. | Use diagnostic or factorial/pairwise design with confounders recorded. |
| IV-019 | Convenience can offset a safety failure in scoring. | **Proposal** | Rejected; hard safety gates precede scoring | Mandatory safety gates are pass/fail and cannot be compensated by a weighted score. | Gate first, score eligible candidates second; publish raw metrics and sensitivity. |
| IV-020 | Silence or automated review means Delphi consensus. | **Proposal** | Rejected; absence is not a vote | RFP requires independent ratings and preserved dissent. | Freeze Round 1 packets; record Round 2 revisions, dissent and operator decision. |

## Validation order

1. **Instruction audit:** extract each imperative, precondition, version claim, permission claim, expected mutation, rollback and success criterion.
2. **Version/source audit:** separate official documentation, local observation, inference and proposal.
3. **Safety audit:** record authorized actor, target, allowed actions, data collected, stop conditions and rollback before a trial.
4. **Deterministic contract tests:** cover malformed/missing terminal results, contradictory status versus exit, invalid quotas, artifact privacy, no-retry behavior, and read-only/no-network boundaries where required.
5. **Keep native unknowns unknown:** boot delivery, whole-app recovery, discovery, nested delegation and full-workspace provisioning remain unresolved until evidence exists.
6. **Independent review:** freeze this matrix and receipts before Round 1 scoring; corrections create a new revision.

For each new row record the exact instruction excerpt and path/line, source/version or receipt ID, source SHA, environment, reproduction steps, expected/observed result, confounders, risk if false, next falsifying test, owner, reviewer confidence and disposition. Preserve contradicted claims when later versions fix them; link the successor instead of erasing history.
