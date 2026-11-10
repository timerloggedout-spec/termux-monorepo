# GitHub Command & Workflow Security Gate

**Status:** Proposal / RFP intake; not yet an enforced production control.  
**Stable ID:** `security.command_workflow_gate`  
**Related:** Delphi Oracle RFP gate; Tier-1 classifier feed; issue #4015 (DoE classifier + fleet-dispatch comparison); issue #4010 (security intake); MoneyBall plane; iOS-Termux fork review.

## Purpose

Create one reusable, deterministic-first security admission gate for code, shell-command plans, GitHub Actions workflows, and generated execution plans. The gate should prevent destructive or privileged operations from reaching an execution boundary without policy evaluation, while preserving a low-friction path for demonstrably safe work.

This is a GitHub-level control for repository changes and automation. It does **not** claim to intercept arbitrary commands executed manually on a developer's phone, workstation, or remote host. Runtime command enforcement requires the execution adapter to call the same policy contract before execution.

## Findings motivating the proposal

The reviewed iOS-Termux code contains a narrow literal-match guard for selected `rm -rf` targets and an SSH warning/hold branch. It does not constitute a general shell policy engine:

- `rm -rf ~/storage` and `rm -rf /` are recognized by the current narrow checks.
- `rm -f important.db` and `rm -rf ~/project` are not covered by those checks.
- Public SSH with no authentication is held, but caller-supplied flags can misrepresent effective authentication; public SSH with `password_auth=true` and no `password_auth_only=true` can bypass the intended hold.
- The SSH brute-force wording is a defensive warning, not a brute-force implementation.
- `sshd` and `ssh` are distinct server/client commands; translation must preserve that distinction.

These are policy-coverage defects, not evidence of malicious intent.

## Ownership and integration boundaries

- **SENTINEL / security policy:** owns policy, severity, protected targets, exceptions, and promotion gates.
- **Tier-1:** owns deterministic classification and classifier registration; reuse the existing single-writer feed and classifier steward.
- **GitHub Actions:** enforces repository and workflow checks; it is not a second issue router.
- **Delphi:** evaluates whether the proposed surface/workflow deserves a bounded trial; it does not become a live model router or production authorization authority.
- **MoneyBall:** reports an explainable score beside the Delphi ballot; it never merges into the ballot aggregate.
- **DeskQUE / AdminGraph:** read-only projections of receipts and relationships; neither becomes a policy authority or direct mutation surface.

Do not create a parallel classifier registry, telemetry SSOT, issue router, or provider router. Reuse existing Tier-1, quota, evidence, and dispatch contracts.

## Classifier family

| ID | Domain | Required signals |
|---|---|---|
| `T1-FS-001` | Destructive filesystem operations | Operation, resolved target, recursion/force flags, protected-root relation, symlink traversal, scope, and reversibility |
| `T1-SSH-001` | SSH exposure and authentication | Effective daemon config, bind/listen scope, authentication methods, key policy, network exposure, and authorization context |
| `T1-SHELL-001` | Shell execution and injection | Parsed command structure, untrusted interpolation, shell metacharacters, nested interpreters, and data/code boundaries |
| `T1-CRED-001` | Credential access and exfiltration | Secret-store reads, environment access, credential-file access, network destinations, and secret-bearing output paths |
| `T1-NET-001` | Network and remote execution | URL/host policy, redirects, DNS/IP resolution, private/metadata address blocking, download-to-execute chains, and callback behavior |
| `T1-GHA-001` | GitHub Actions supply chain | Trigger trust, fork/PR context, token permissions, secrets exposure, action pinning, checkout persistence, and privileged write paths |
| `T1-EXEC-001` | Untrusted execution | Archive extraction, generated artifacts, executable bits, package lifecycle scripts, and sandbox boundary |

Classifier IDs are proposed names until registered through the Tier-1 steward.

## Decision contract

Return a versioned, machine-readable decision:

- `allow`: deterministic policy passes; least privilege and scope are established.
- `review`: ambiguity, elevated impact, missing provenance, or a documented exception requires a human decision.
- `quarantine`: untrusted input or artifact is retained without execution pending analysis.
- `block`: a prohibited action or violated hard invariant is proven.

Every decision includes policy version, classifier versions, subject digest, normalized operation, target/scope, evidence references, rule IDs, rationale, decision time, and review/exception metadata. Never include secret values, raw credentials, or unredacted sensitive command arguments in receipts.

Unknown or unparsable operations fail closed to `review` or `quarantine`; they must not be silently treated as safe.

## Analysis strategy

1. **Structured input first:** prefer an execution-plan representation with executable, argv, environment references, working directory, target resources, network destinations, and declared intent.
2. **Parser/AST analysis:** parse shell syntax and supported language constructs. Do not rely on regex as the primary security boundary.
3. **Deterministic rules:** evaluate protected paths, destructive flags, privilege transitions, SSH exposure, credential flows, network destinations, and GitHub workflow trust.
4. **Static analyzers:** run language-appropriate checks after deterministic admission.
5. **Optional semantic review:** model output is advisory only, never able to override deterministic blocks or grant authorization.
6. **Human review:** required for policy exceptions, privileged changes, and unresolved high-impact findings.

For filesystem operations, classify `rm -f`, `rm -r`, `rm -rf`, `find -delete`, recursive library calls such as `shutil.rmtree`, unlink operations, and shell redirection by the resolved target and context. A temporary-file cleanup can be allowed; destructive access to protected roots or shared storage requires block/review according to policy. Avoid blanket blocking of every `rm -f`.

For SSH, derive effective daemon configuration rather than trusting caller booleans. Public password authentication is blocked; public exposure with unknown auth is review/quarantine; key-only private-network service may be allowed when authorized and evidenced. Defensive brute-force testing is a separate, explicitly scoped, rate-limited, authorized test class—not a production SSH capability.

## GitHub enforcement design

- Reusable workflow called by relevant CI workflows, with a required status check on protected branches once rollout criteria pass.
- Explicit least-privilege `permissions` at workflow/job level.
- Immutable full-SHA pins for third-party Actions; controlled update cadence.
- Scan workflow triggers, fork-origin PR paths, `pull_request_target`, checkout persistence, untrusted expression interpolation, secret exposure, and artifact trust.
- Run secret scanning, actionlint, zizmor, and scoped Semgrep/custom AST rules where compatible with existing tooling.
- Keep untrusted PR code away from privileged tokens and write-capable jobs.
- Produce redacted JSON receipts and concise PR annotations; attach exact commit SHA and run/attempt identity.
- Exceptions require named reviewer, rationale, exact rule/subject, scope, expiry, and evidence. Expired exceptions fail closed.
- Start advisory, then enforce only after baseline and false-positive review; do not silently weaken existing branch protections.

## DoE and MoneyBall protocol

Use issue #4015 as the existing experiment-design lane, not a new router. Pre-register:

- A: current baseline behavior.
- B: deterministic-first structured command and workflow gate.
- C: capability- and quota-aware participant selection after deterministic admission.
- D: independent critique/verification escalation only when risk, uncertainty, or disagreement crosses a pre-registered threshold.

Use synthetic fixtures and replay only; no live attack, destructive command, or real credential testing. Measure safe admission, correct classification, false-positive review/quarantine, missed high-risk operations, duplicate/conflicting dispatches, time-to-resolution, human intervention, provider failures, latency, and actual token/quota use.

MoneyBall axes are fixed at pass intake and recorded in the pass manifest. Use the current starting proposal only as a starting point: fleet-pain relevance 0.30, evidence maturity 0.25, survivability 0.20, inverse adoption cost 0.15, composability 0.10. Record per-axis values, weights, composite, evidence, and unknowns. Report the MoneyBall result beside—not inside—the Delphi ballot aggregate.

### Free inference participant eligibility

A provider/model can participate only if all are evidenced for that invocation:

1. a real invoke endpoint and dispatch-selection route exist;
2. the provider/model is currently available and compatible with the task;
3. exact no-cost entitlement and current quota headroom are verified from an authoritative source;
4. cooldown/rate limits and concurrency are admitted;
5. the invocation is attributable to provider, model, role, run/attempt, policy version, and commit SHA;
6. output is treated as untrusted advisory evidence and cannot authorize or override a deterministic policy decision.

A roster entry, public free-tier claim, or pool allocation alone is not proof of an invoke route, remaining quota, or free entitlement. If any check is missing, record `not_eligible` / `not_established` and use the local deterministic baseline. The existing Delphi RFP gate currently sets `DELPHI_LLM_MAX=0`; this proposal does not change that control.

## Delivery phases

1. **P0 — baseline and contract:** map existing guards, workflows, Tier-1 classifiers, provider routes, quota pools, and current tests; freeze the policy schema and threat model.
2. **P1 — deterministic engine:** implement parser-backed operation normalization and the rule engine with fixture tests for shell and workflow cases.
3. **P2 — GitHub adapter:** reusable workflow, least-privilege checks, action pinning checks, redacted receipts, and required-check rollout plan.
4. **P3 — DoE evaluation:** replay treatments A–D, report per-class metrics and provider eligibility, compare MoneyBall profiles separately from Delphi ballots.
5. **P4 — surfaces and operations:** DeskQUE/AdminGraph read-only projections, operator runbook, exception lifecycle, and rollback.

## Acceptance gates

- Every tested operation has a deterministic normalized representation or an explicit parse-failure outcome.
- Regression corpus covers destructive command variants, path traversal/symlinks, SSH effective config, shell injection, credential-flow patterns, remote execution, and dangerous Actions triggers/permissions.
- Tests prove safe temporary cleanup can pass and protected-root deletion cannot pass.
- Public password SSH cannot bypass the policy by omitting or falsifying a caller flag.
- No untrusted PR job receives privileged write tokens or secrets.
- All third-party Actions in the enforced scope are pinned to immutable SHAs.
- Receipts are redacted, deterministic, tied to exact SHA/run attempt, and replayable.
- Exceptions expire and cannot override hard blocks.
- DoE reports preserve negative results, per-class outcomes, exact cohort and version identity, and quota/availability evidence.
- No production enforcement, live traffic shadow, or promotion occurs solely from a model score or RFP award.

## Explicit non-goals

No direct production deployment, branch-protection mutation, secret rotation, collaborator permission changes, live SSH brute-force testing, destructive command execution, paid inference, automatic merge, or automatic promotion is authorized by this proposal.
