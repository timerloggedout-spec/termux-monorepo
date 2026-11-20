# Reuse Case: Context Relationship Graph for Linguist Review

## Why This Exists

This review used the repository-native [`context-relationship-graph` skill](../../../.agents/skills/context-relationship-graph/SKILL.md) to reconstruct the decision context for Linguist PR #177 before proposing a change. It is a reusable example for agents reviewing a broad pull request, a disputed architecture decision, related GitHub history, or a potentially stale work item.

> The graph is an evidence aid, not a source of authority. It does not authorize a merge, a Linear update, a secret change, or a repository mutation merely because a relationship was found.

## Reuse Recipe

| Step | Required action | Linguist example |
|---|---|---|
| 1. Establish bounds | Read agent instructions, active proposals, graph scope registry, and index manifest. | The review excluded session stores, credentials, browser state, generated internals, and unbounded history. |
| 2. Start exact | Query the PR, issue, file, symbol, or permalink that is the actual root. | `pr:177` was the root; `pr:126`, `pr:154`, and `issue:117` were verified follow-up roots. |
| 3. Preserve evidence classes | Keep direct API/permalink/index evidence as **verified**; use shared-file history only as **candidate**. | PR #126’s link to issue #117 is verified; PRs #196/#208/#218/#228 are candidate optimization context. |
| 4. Inspect the smallest source set | Read only the cited implementation, test, role, dictionary, and governance files. | `cedrlang.py`, `cid.py`, tests, `LINGUIST_SPEC.md`, Grimoire dictionaries, AGENTS/CLAUDE, and proposal records were assessed. |
| 5. Render only on request | Produce bounded Mermaid only when a person requests visual output. | [`context-pr177.mmd`](context-pr177.mmd) and [`linguist-relationship-summary.mmd`](linguist-relationship-summary.mmd) are source artifacts. |
| 6. Close out precisely | Report the root, verified links, candidate links, history bound, and unresolved decisions. | [`LINGUIST-REVIEW-PACKET.md`](LINGUIST-REVIEW-PACKET.md) records the no-go disposition, successor scope, and gate blockers. |

## Commands

Run from the repository root. Use narrow selectors and state bounds in the resulting report.

```bash
python3 -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --query pr:177 --depth 2 --max-nodes 25 --format markdown

python3 -m archwiz.context_relationships.query \
  --index workspace/llm_map/context_relationships \
  --file-review-timeline workspace/compression_sandbox/cedrlang/cedrlang.py \
  --max-nodes 50 --format markdown
```

The graph may be refreshed only through its trusted publisher or bounded manual reconciliation. Do not hand-edit generated records, persist comment/review bodies, widen a query after a no-match, or represent a candidate as a fact.

## Review and Upgrade Path

An agent seeking to extend the method should first read the skill, [`docs/icm/objects/knowledge/context-relationship-index.md`](../../icm/objects/knowledge/context-relationship-index.md), and the active [Context Relationship Graph proposal](../../proposals/active/context-relationship-graph/MANIFEST.md). Changes to graph code require the dedicated deterministic contract suite before a proposal or workflow change. Review requests or method-improvement proposals should cite this case study, the exact root, and an evidence URL rather than pasting private discussion content.

## Linguist Evidence Links

- [Review packet](LINGUIST-REVIEW-PACKET.md)
- [Agent-contact inventory](agent-contact-inventory.md)
- [Diagram validation](diagram-validation.md)
- [Published follow-up issue #274](https://github.com/timerloggedout-spec/termux-monorepo/issues/274)
- [Proposal research and vote record](../../proposals/active/cedrlang-grimoire-a2a/RESEARCH.md)
