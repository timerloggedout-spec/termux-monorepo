# Timeline Event and Comment Permalink Reconnaissance

## Verified GitHub Timeline Event

The GitHub timeline event at `issues/236#event-10047143951` is a native issue-history entry, not a comment body. GitHub renders it as: **`timerloggedout-spec mentioned this`** and identifies the related target as **`Game Teams #243`**. The event has a stable event permalink and therefore can provide direct evidence for a typed issue-to-issue cross-reference relationship.

## Verified Comment-Permalink Shape

The supplied `issues/164#issuecomment-5295404994` link resolves to a specific comment within issue #164. GitHub exposes comment-level anchor URLs while also retaining the parent issue context. This supports two distinct graph facts: a comment belongs to its parent issue/pull request, and a direct comment permalink can serve as evidence for explicitly extracted internal references.

## Design Consequence

The existing collector must gain a timeline-event collection path in addition to issue-comment and review-comment paths. The event type, actor, target issue/pull request, event URL, and timestamp are structured metadata. The collector should normalize those fields into verified graph evidence without storing conversation bodies. Comment and review permalinks should be parsed as exact reference tokens and represented as first-class comment/review target references where the API exposes the corresponding stable identifier.

## Sources

- https://github.com/timerloggedout-spec/termux-monorepo/issues/236#event-10047143951
- https://github.com/timerloggedout-spec/termux-monorepo/issues/164#issuecomment-5295404994
- https://github.com/timerloggedout-spec/termux-monorepo/issues/164#issuecomment-5250798212

## API-Level Verification

GitHub’s GraphQL issue timeline returns the #236 relationship as a `CrossReferencedEvent` created at `2026-08-18T20:25:39Z`, with actor `timerloggedout-spec` and source issue #243, `Game Teams`. The REST timeline returns the corresponding `cross-referenced` item with the same actor, time, and source issue metadata, but no stable REST event `id`. The graph must therefore treat the typed source/target/time tuple as the canonical event identity and retain the parent issue URL as API evidence; an observed web event anchor may be preserved when supplied but cannot be synthesized from REST data.

Comment `5295404994` belongs to issue #164, has a stable `html_url`, and contains the explicit local issue reference `#215`. Comment `5250798212` also belongs to issue #164 and contains two direct `issuecomment` permalinks. This demonstrates that the collector must parse `#issuecomment-<id>` anchors as exact reference tokens and resolve them to comment nodes, not merely collapse them into their parent issue.
