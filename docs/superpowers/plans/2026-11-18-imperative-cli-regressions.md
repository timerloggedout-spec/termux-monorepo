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

### Current-master reconciliation

GitHub reports the review head conflicted with master. Non-mutating merge-tree
confirmed conflicts in the checker vocabulary and dispatch test comment.
Merge master `ab54688a5ba9995c2ba57fae384d68ca7c3c6e51` without rewriting history:
retain the union vocabulary and the PR import-safe entry point; preserve master's
scope-prefix parsing (including colon-containing descriptions) in `subject_verb`.
Dispatch test matches master exactly; its concurrency assertion is already upstream.
Add three real-CLI cases for nested colons and scope-without-space parsing.
Upstream files carried by the merge are not newly authored lane changes; validate
the resulting four-file diff against the merged master before push.

## Real merge-range coverage — 2026-11-20

Initial live head `5f249e687e5cb20238c8ee0be846a23ce7251ac4` has both required
GitHub gates SUCCESS and no new original-head review findings. AR-33 continues
with tests/docs only; production checker and dispatch logic remain untouched.

The previous merge-exclusion tests asserted subprocess arguments. Extend the
existing temporary-Git fixture to create divergent main/side commits and a real
two-parent merge. Its synthetic subject and body deliberately violate style.
Verify synthetic text is excluded, while invalid side-branch subjects, bodies,
and added instructions are still rejected. Assert two parents explicitly.

Maintainer critique: preserve the simple linear fixture by default; avoid changing
production behavior or developer Git config. Adversarial critique: excluding merge
commits must not hide non-merge ancestors or net instruction changes.

Observed working-tree command over head `5f249e687` plus these tests:
`PYTHONPATH=/home/user/style-test-deps python3 -m pytest -q tests/test_check_do_statement_style.py`
returns `23 passed`. A temporary checker mutation removing both `--no-merges`
flags makes the valid merged range fail with synthetic subject and body errors
(RED). Existing checker passes (GREEN). Temporary mutation is outside git.
Required local gates and committed-head checks are recorded separately in the PR.

## Merge ancestry counterexamples — 2026-11-21

Live head `1d1688892b91f601df9867e105ea763be95accb7` passed both required
GitHub gates (runs 44701654759 and 44701654966); no current-head inline review
roots at initial fetch. Continue registered AR-33, tests/docs only.

Maintainer critique: the merge fixture validates side ancestors but has only a
valid mainline commit. Adversarial critique: replacing the full ancestry walk
with first-parent enumeration could silently skip invalid side subjects/bodies.
Allow fixture-local mainline subject/body overrides and add two rejection cases;
the default merge and all linear cases remain unchanged. Synthetic merge text
must remain excluded while both non-merge ancestor paths remain checked.

Focused working-tree command over the initial head:
`PYTHONPATH=/home/user/style-test-deps python3 -m pytest -q tests/test_check_do_statement_style.py`
returns `25 passed`. Temporary checker mutation adding `--first-parent` to both
Git log calls produces false PASS for invalid side subject and invalid side body.
The existing side tests therefore detect that mutation; the new cases cover the
complementary mainline path. Temporary mutation lives outside git and is removed.
No production defect claim: the unchanged checker rejects both paths correctly.
Required local gates and current committed-SHA GitHub results are separate receipts.

## Review-ready evidence — 2026-11-22

AR-33 moves to `in_review`: implementation and behavioral evidence are complete,
not integrated. Preserve the previous failed attempts and pending observations as
historical records rather than rewriting them as successes.

Verified live head `5e9984983f43b85ff04d1ac1717d3a2627ede859`:

- [Repository gate SUCCESS](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/44884232437/job/136785920221).
- [Termux smoke SUCCESS](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/44884232176/job/136785918346).
- No inline review roots with that original commit SHA at initial fetch.
- Prior committed-tree evidence: 25 style cases, 89 combined tests and 90 subtests
  PASS; production checker unchanged by the final ancestry-test contributions.

Related #5496 remains open at `99334c4817ebcf78c8953b07b603ed7d7cf0646c`.
Its [repository gate](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/44046954431/job/133914916513)
and [smoke](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/44046954242/job/133914914017)
are SUCCESS. Smoke appears on the second page of 117 check runs; a first-page
absence is not a missing-gate diagnosis.

Maintainer critique: further tests without a new finding would add churn; record
the verified disposition instead. Adversarial critique: green jobs do not grant
authority or establish integration. Both owner-authored PRs remain unmerged;
#5543 remains open until integration. This documentation follow-up requires its
own local gates and new-head GitHub observation, separate from the SHAs above.