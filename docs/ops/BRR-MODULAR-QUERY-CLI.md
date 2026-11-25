# BRR Modular Query CLI

BRR keeps its existing branch reconciliation inventory and accepts composable selectors for focused, layered analysis. The original `--repo`, `--default-branch`, and `--output-dir` options remain the compatibility baseline.

## Query composition

- Repeat `--query CLAUSE` to add text clauses.
- `--query-mode all` (default) requires every clause; `--query-mode any` accepts any clause.
- Matching is case-insensitive against normalized JSON metadata.

## Profiles and surfaces

Profiles stack and explicit surfaces extend the selected set:

| Profile | Surfaces |
|---|---|
| `reconciliation` | branch, pull-request |
| `delivery` | branch, pull-request, commit, issue, comment, review |
| `architecture` | file, symbol, scope, label |
| `full` | every supported surface |

Repeat `--surface` to select individual surfaces: `branch`, `pull-request`, `commit`, `issue`, `comment`, `review`, `file`, `symbol`, `scope`, and `label`.

## AST and similarity

- `--ast` adds the CRG file and Python symbol surfaces.
- `--similarity` includes existing CRG edges classified as `candidate`; it preserves their candidate classification and evidence.
- Graph-backed surfaces require `--graph-index PATH`, pointing to the canonical CRG index directory containing `nodes.jsonl` and `edges.jsonl`.
- `--max-results N` bounds graph nodes and similarity candidate edges (default: 1000).

BRR consumes existing CRG output. Run the established source/GitHub collectors and compiler to build or refresh that index; the BRR query layer does not create a parallel collector or datastore.

## Example

```sh
python scripts/branch_reconciliation_registry.py \
  --repo owner/repository \
  --default-branch master \
  --profile reconciliation \
  --profile architecture \
  --query "branch-name" \
  --query "module-name" \
  --query-mode all \
  --ast \
  --similarity \
  --graph-index artifacts/context-relationships \
  --max-results 250
```

## Output and authority

The JSON report records selected profiles, surfaces, clauses, query mode, AST/similarity toggles, graph coverage counts, and candidate edges. The Markdown report summarizes the selected scope and counts.

The runner remains read-only. Similarity and co-change remain candidate evidence; query results do not authorize branch promotion, deletion, PR closure, or merging. Human review remains required for promotion.
