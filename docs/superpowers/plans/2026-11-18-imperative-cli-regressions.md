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

Preserve the existing dispatch test adjustment and checker policy. Review follow-up
restores baseline imperative verbs without removing the PR's added vocabulary.
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
- Initial PR checker run passes 12 focused tests (GREEN).
- Re-run `node --test tests/test_dispatch_admission.mjs` on 2026-11-19:
  output `tests 9`, `pass 9`, `fail 0`. Checkout HEAD was
  `7727f875563c18c8f470757ad4ec066f3edad711` with the review follow-up edits
  described below; the dispatch file is unchanged from that commit.
- Automation documentation catalog check passes.
- Registry validation fails on the existing `qdesk-self-repair` orphan, tracked in
  #5214 and repair PR #5485; this contribution does not alter the registry.
- Staged repository gate and Linux Termux smoke both pass. Cached diff check passes.
- Current-head GitHub checks must be verified separately after push.

## Review follow-up — 2026-11-19

Verified reviews 4611017601 (dispatch provenance), 4611017609 (lost `guard`)
and 4611017619 (ambient signing). The original CLI rejects `guard` and fails
fixture commits when a temporary global config enables signing with `/bin/false`.
Current master `069a774cd0ab06bc6ea6f8c51bd9e97ca3b895fd` accepts 14 verbs
absent from this PR; preserve those baseline verbs rather than restore just one.
Registry item AR-33 authorizes this tightly scoped checker/tests/docs follow-up.

Tests first: baseline-vocabulary assertion, real guard/guarded CLI cases and
ambient-signing regression. RED: 3 failures / 13 passes for the expected causes.
GREEN: add the 14 baseline verbs and set `commit.gpgSign=false` only in each
temporary fixture repository. Developer global config and real repository signing
remain untouched. No workflow, permission, credential or history changes.

Command: `PYTHONPATH=/home/user/style-test-deps python3 -m pytest -q
tests/test_check_do_statement_style.py` on the same described review working tree:
`16 passed`. Required gates must run on the staged follow-up and remote results
must be tied to the resulting commit separately, not inherited from 7727f8755.