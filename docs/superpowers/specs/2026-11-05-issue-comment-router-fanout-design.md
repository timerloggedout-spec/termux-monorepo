# Issue Comment Router Fan-out Reduction — Design

**Status:** Approved for bounded implementation by the operator directive on 2026-11-05
**Proposal:** [actions-refinements](../../proposals/active/actions-refinements/MANIFEST.md) — AR-32
**Owner:** ChatGPT
**Target:** `master`

## Intent

Make the existing Issue Comment Router the single top-level entrypoint for the repository's three high-fan-out `issue_comment` paths: Gemini Dispatch, Jules issue mentions, and provider-review feedback relayed to Jules.

The router classifies each comment once and calls the existing target workflows as reusable workflows (`workflow_call`) inside the router run. This removes redundant top-level workflow runs without changing the existing command semantics or invoking a provider for unmatched comments.

## Baseline evidence

A bounded sample of 300 consecutive Actions runs on 2026-11-05 (2026-11-05T23:42:12Z through 23:50:42Z) showed:

| Workflow | issue_comment runs | Skipped | Successful |
|---|---:|---:|---:|
| Gemini Dispatch | 5 | 5 | 0 |
| Jules on Issues | 5 | 5 | 0 |
| Agent review → auto Jules | 12 | 2 | 10 |
| Issue Comment Router | 5 | 0 | 5 |

The router currently listens only to `created`, while Agent review → auto Jules listens to both `created` and `edited`. The 12-versus-5 run-count difference establishes a subscription-coverage mismatch; the run-list API does not expose the comment action, so the exact cause of each difference is not asserted.

The Gemini and Jules target workflows create top-level runs for every issue comment before their job-level command filters skip non-matching comments. The router already creates a top-level run for the same created-comment stream.

## Goals

1. Keep one top-level workflow run per covered issue-comment event.
2. Route only trusted, exact-match commands/provider identities.
3. Execute existing target jobs as reusable workflow calls within the router run.
4. Preserve all existing non-`issue_comment` triggers.
5. Preserve actor allowlists, author-association checks, current-comment revision checks, PR/current-SHA validation, cooldown/control filters, concurrency semantics, and least-privilege permissions.
6. Make the route contract regression-testable in the existing native orchestration gate.

## Non-goals

- No new cron, schedule, polling loop, provider, secret, token, or credential change.
- No new provider invocation class or broader command syntax.
- No automatic Jules session creation beyond the existing trusted `@jules` issue-comment path and existing Jules label path.
- No Gemini invocation except the existing authorized `@gemini-cli` / `@sparkFlux` commands.
- No production-ledger writes or implementation of the current ledger placeholder.
- No direct push, branch mutation, merge, deployment, or issue/comment-to-shell execution.
- No changes to pull-request, review, issue-open, or Jules-label event ownership beyond the existing issue-comment paths.

## Selected architecture

```text
issue_comment created / edited
            |
            v
     Issue Comment Router
       - one classification
       - trusted identity checks
       - comment ID + updated_at
            |
      +-----+-------------------+
      |                         |
      v                         v
 Agent Review reusable     Gemini Dispatch reusable
      |                         |
      +-------------+-----------+
                    |
                    v
             Existing jobs and
             existing provider policy

       @jules on non-PR issue
                    |
                    v
          Jules reusable workflow
          (same API/label policy)
```

The router uses local reusable workflow calls, not `workflow_dispatch` or the Actions REST API. Therefore matched target jobs run within the router's existing workflow run; they do not create another top-level run.

### Route contract

| Route | Accepted event | Gate | Target |
|---|---|---|---|
| Agent review | `issue_comment.created/edited` on a PR | Bot identity in the existing issue-comment allowlist; target revalidates bot identity and provider control/cooldown filters | `agent-review-auto-jules.yml` |
| Gemini | `issue_comment.created` | User actor, OWNER/MEMBER/COLLABORATOR, exact `@gemini-cli` or `@sparkFlux` prefix | `gemini-dispatch.yml` |
| Jules mention | `issue_comment.created` on a non-PR issue | User actor, OWNER/MEMBER/COLLABORATOR, exact `@jules` prefix | `agent-jules-on-issues.yml` |
| Ledger candidate | `issue_comment.created` on a PR | Trusted human plus `Implements:` marker | Classification/receipt only; no write |

The router subscribes to `created` and `edited` because the Agent review target currently accepts both. Gemini and Jules remain created-only, matching their existing triggers.

### Reusable input and provenance contract

Each reusable target receives only:
- `issue_number`;
- `pr_number` where applicable;
- `comment_id`;
- `comment_updated_at`;
- `source_event=issue_comment`.

The target re-fetches the comment from GitHub, verifies that it belongs to the expected issue/PR, compares the current `updated_at` with the event revision, and repeats its own actor/command/provider checks. Comment bodies are not forwarded as workflow inputs. Stale or mismatched revisions are rejected.

### Permissions

- Router top-level permissions are empty; the classifier reads the webhook payload only.
- The reusable workflow caller jobs grant only the permissions already needed by their target jobs.
- No `actions: write` permission is added. No checkout is added to the router.
- Existing provider secrets are passed only to the matching reusable workflow with `secrets: inherit`.

### Compatibility

- `agent-review-auto-jules.yml` keeps direct `pull_request_review` and `pull_request_review_comment` triggers.
- `gemini-dispatch.yml` keeps direct `pull_request`, `issues`, `pull_request_review`, and `pull_request_review_comment` triggers.
- `agent-jules-on-issues.yml` keeps the existing `issues:labeled` path.
- Only the three redundant direct `issue_comment` subscriptions are removed.
- The Jules label workflow and all existing provider/API checks remain unchanged.

## Acceptance criteria

- [ ] Router receives created and edited issue comments with event-specific, non-cancelling concurrency.
- [ ] Router calls the three existing targets through local reusable workflow jobs.
- [ ] Target workflows expose typed `workflow_call` inputs and no longer directly subscribe to `issue_comment`.
- [ ] Target workflows re-fetch and validate the exact comment revision.
- [ ] Existing non-comment triggers remain intact.
- [ ] Unmatched human comments do not start Gemini, Jules, or provider-review target jobs.
- [ ] Trusted commands and provider feedback preserve the existing behavior and security checks.
- [ ] Native orchestration contract tests pass.
- [ ] Repository gate and Termux smoke pass on the same immutable PR head SHA.
- [ ] Post-promotion run sample confirms fewer top-level target runs and no loss of matched route outcomes.

## Rollback

Restore the direct `issue_comment` triggers on the three targets and remove the corresponding reusable calls from the router. No database migration, secret rotation, schedule change, or state migration is required.
