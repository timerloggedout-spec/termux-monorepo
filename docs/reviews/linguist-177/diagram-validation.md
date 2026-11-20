# Context Diagram Validation

**Validated:** 2026-08-20 UTC

Both graph artifacts rendered successfully from Mermaid source.

| Artifact | Bound | Validation finding |
|---|---|---|
| `context-pr177.png` | Exact graph query `pr:177`, depth 2, maximum 25 nodes | The raw bounded graph is readable and demonstrates the root’s verified commit, issue-comment, review, and file-review relationships. It is intentionally dense because it preserves metadata-level review history. |
| `linguist-relationship-summary.png` | Curated evidence summary | The high-level diagram is readable and distinguishes solid verified relationships from dashed candidate relationships. It shows PR #126’s verified link to issue #117, PR #154/#177’s verified file/review links, the exact owner-comment references from #177 to #126/#154, and the deliberately separate CID/CEDARscript candidate scope-mix boundary. |

The summary diagram is an evidence presentation, not a replacement for the generated index. Its verified links cite the corresponding graph outputs and exact GitHub evidence in the final evidence register.
