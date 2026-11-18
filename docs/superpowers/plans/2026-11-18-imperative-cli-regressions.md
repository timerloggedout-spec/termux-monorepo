# Imperative CLI regression coverage — AR-33

## Intent and evidence

Issue #5543 identifies `correct` and `recognize` rejected by master at
`e61384641`. Existing draft PR #5425 head
`e645a9c5f7987ddc66fc9e06b8fc4bc24e113436` already adds both verbs.
Aid that branch with behavioral tests instead of a duplicate implementation PR.

## Design and boundaries

Exercise the real checker as a subprocess against isolated temporary Git
repositories and push-event JSON. This verifies subject extraction, vocabulary,
range enumeration, event loading and exit status together, beyond set-membership
assertions. Keep valid scoped subjects distinct from past-tense/non-action wording;
keep negative-first body/instruction rejection active.

Preserve the existing production implementation and dispatch test adjustment.
Use credential-free local Git identity in test repositories only. Keep workflows,
permissions, generated files and prior history untouched. PR #5425 is owner-authored
and requires specific merge consent.

## Execution

1. Register AR-33; read existing checker, tests, related PR patches and guidance.
2. Add CLI tests for both #5543 subjects, ordinary imperative wording,
   past-tense/non-action counterexamples and negative-first text/body.
3. Run tests against master checker to confirm the two reported failures, then
   run against existing PR checker to verify its repair and policy retention.
4. Run focused tests, repository gate, Linux smoke, registry and diff checks.
5. Commit and fast-forward push the existing PR branch; re-fetch exact head,
   checks and reviews. Link #5543 to the repair without premature issue closure.

## Critique

Maintainer: avoid widening vocabulary beyond the existing repair and test public
CLI behavior rather than implementation-only membership.
Adversarial: accepting two genuine verbs must not bypass action-first policy,
accept their past-tense forms, or suppress negative-first body findings.

## Observed validation

- Master checker rejects both reported subjects in real temporary Git ranges (RED).
- Existing PR checker passes all 12 focused tests (GREEN); dispatch suite passes 9 tests.
- Automation documentation catalog check passes.
- Registry validation fails on the existing `qdesk-self-repair` orphan, tracked in
  #5214 and repair PR #5485; this contribution does not alter the registry.
- Staged repository gate and Linux Termux smoke both pass. Cached diff check passes.
- Current-head GitHub checks must be verified separately after push.