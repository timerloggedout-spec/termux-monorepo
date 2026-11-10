# Implementation backlog — GitHub Command & Workflow Security Gate

This backlog is proposal work, not a claim that implementation has begun.

## P0 — Recon and contracts
- [ ] Map current shell guards, SSH configuration logic, and command translation in iOS-Termux.
- [ ] Inventory existing Tier-1 classifier registrations, feeds, schema contracts, and test harnesses.
- [ ] Inventory relevant GitHub Actions workflows, triggers, permissions, action pins, and trusted/untrusted execution boundaries.
- [ ] Reconcile provider/model pools with actual invocation adapters and current quota evidence.
- [ ] Freeze policy decision schema, threat model, protected-resource policy, and receipt redaction contract.
- [ ] Capture baseline fixture outcomes before implementation.

## P1 — Deterministic policy engine
- [ ] Define normalized execution-plan schema (argv, executable, cwd, environment references, target resources, network destinations, declared intent).
- [ ] Implement parser-backed shell analysis and explicit parse-failure handling.
- [ ] Implement destructive filesystem rules for `rm`, `find -delete`, redirection, and common language APIs.
- [ ] Derive effective SSH daemon configuration and prevent caller-flag bypass.
- [ ] Implement shell injection, credential-flow, network/remote-execution, untrusted-artifact, and GitHub Actions rules.
- [ ] Add regression and adversarial fixtures; no fixture executes destructive behavior.

## P2 — GitHub adapter and evidence
- [ ] Add reusable security-policy workflow with explicit least-privilege permissions.
- [ ] Add immutable action pinning and dangerous-trigger checks.
- [ ] Integrate actionlint, zizmor, secret scanning, and scoped static analysis where repository tooling supports them.
- [ ] Emit redacted, deterministic receipts bound to run/attempt and exact commit SHA.
- [ ] Add exception review, scope, expiry, and audit evidence.
- [ ] Stage advisory → required-check enforcement only after baseline and false-positive review.

## P3 — DoE / MoneyBall evaluation
- [ ] Pre-register fixture corpus, hash, treatments, metrics, replication floor, and stopping rules under issue #4015.
- [ ] Verify endpoint invoke routes, capability, free entitlement, live quota, and cooldown before any model participant is admitted.
- [ ] Run A–D on identical fixture sets; retain raw outcomes and failure classifications.
- [ ] Record per-axis MoneyBall values/weights beside Delphi results.
- [ ] Publish comparative report with negative results and exact SHAs.

## P4 — Operations and surfaces
- [ ] Add read-only DeskQUE queue and AdminGraph relationships from canonical receipts.
- [ ] Document operator runbook, policy update lifecycle, exception expiry, and rollback.
- [ ] Validate on Linux, Android/Termux, and other targets separately; claim only tested portability.
- [ ] Require explicit human security approval before production enforcement or promotion.
