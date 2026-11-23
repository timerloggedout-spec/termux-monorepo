# Starlists — curated repository research sets

**Purpose:** stable human-readable collections for repository discovery, identification, and comparison. The Repository Observatory remains the canonical live source for GitHub ownership/star/watch provenance; this file records curated research intent and classification.

## Rust migration and selective optimization

| Repository | Relationship | Pinned candidate | Research role | Status |
|---|---|---|---|---|
| [timerloggedout-spec/fast-anything_fork](https://github.com/timerloggedout-spec/fast-anything_fork) | Owned fork of `EL4CTEO/fast-anything` | `0.8.0` · `80ab099817b3d07ebe5b5221d4a9c6b881cfd044` | Selective hot-path Rust migration | Candidate; DoE design-only |
| [timerloggedout-spec/rust-anything_fork](https://github.com/timerloggedout-spec/rust-anything_fork) | Owned fork of `erkamyaman/rust-anything` | `3.3.0` · `50d3810b622fdc6cb3aee965fe4c9d4b4f29205b` | Incremental cross-language migration and behavior replay | Candidate; DoE design-only |

## Repository reconstruction and prompt synthesis

| Repository | Relationship | Pinned candidate | Research role | Status |
|---|---|---|---|---|
| [filiksyos/gitreverse](https://github.com/filiksyos/gitreverse) | External upstream | `main` snapshot `e7f7d2859105aafe16ec4f39c0315c07e6b0eae3` | Turns repository metadata, depth-1 tree and README into a synthetic coding prompt; MIT license verified from upstream LICENSE | Research candidate; star status pending Observatory reconciliation |
| Internal GitReverse implementation | In-progress repository-native implementation | Exact source path and commit pending recon | Custom reconstruction pipeline; Siglary integration/version to be verified | Build-in-progress; comparison candidate |

## Adjacent internal systems — distinct contracts

| Repository | Verified contract | Comparison disposition |
|---|---|---|
| [timerloggedout-spec/repo-replay](https://github.com/timerloggedout-spec/repo-replay) | Reconstructs files from session-chat code extractions using content-addressed objects, provenance pointers, recipes and its own history DAG | Adjacent reconstruction system; distinct from GitReverse's public-repository-to-prompt task |
| [timerloggedout-spec/repo-story](https://github.com/timerloggedout-spec/repo-story) | Narrates PR/repository history from commits, file mutations and authors, with source-commit citations | Adjacent repository-intelligence system; distinct from GitReverse's prompt-synthesis task |

## Extensible comparison rules

1. Keep repository identity, upstream identity, fork identity, source commit, license and observation date separate.
2. Treat a curated starlist entry as research intent; the Observatory verifies actual GitHub `starred` provenance.
3. Keep capability-incommensurate studies in sibling DoE campaigns. Rust runtime outcomes and reconstruction-quality outcomes remain separate.
4. Pin each source snapshot before execution. Record later upstream changes as a new version/cohort.
5. Promote reusable patterns only after correctness, provenance, security, maintenance and cost evidence passes the existing repository gates.

## Links

- [Repository Observatory](./README.md)
- [Stars | Forks | Watch evaluation](./STARS-FORKS-WATCH.md)
- [Canonical repository index](../../workspace/llm_map/repositories/repository-index.json)
- [Rust migration DoE candidate](../../experiments/doe/rust-migration-tools/README.md)
