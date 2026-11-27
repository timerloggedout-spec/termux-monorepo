# Starlists — curated repository research sets

**Purpose:** stable human-readable collections for repository discovery, identification, and comparison. The Repository Observatory remains the canonical live source for GitHub ownership/star/watch provenance; this file records curated research intent and classification.

## Rust migration and selective optimization

| Repository | Relationship | Pinned candidate | Research role | Status |
|---|---|---|---|---|
| [timerloggedout-spec/fast-anything_fork](https://github.com/timerloggedout-spec/fast-anything_fork) | Owned fork of `EL4CTEO/fast-anything` | `0.8.0` · `80ab099817b3d07ebe5b5221d4a9c6b881cfd044` | Selective hot-path Rust migration | Candidate; DoE design-only |
| [timerloggedout-spec/rust-anything_fork](https://github.com/timerloggedout-spec/rust-anything_fork) | Owned fork of `erkamyaman/rust-anything` | `3.3.0` · `50d3810b622fdc6cb3aee965fe4c9d4b4f29205b` | Incremental cross-language migration and behavior replay | Candidate; DoE design-only |

### External upstream sources

| Repository | Relationship | Pinned candidate | Research role | Status |
|---|---|---|---|---|
| [EL4CTEO/fast-anything](https://github.com/EL4CTEO/fast-anything) | Upstream of owned fork | Fork comparison snapshot `80ab099817b3d07ebe5b5221d4a9c6b881cfd044` | Selective hot-path Rust migration | Research candidate; star status pending Observatory reconciliation |
| [erkamyaman/rust-anything](https://github.com/erkamyaman/rust-anything) | Upstream of owned fork | Fork comparison snapshot `50d3810b622fdc6cb3aee965fe4c9d4b4f29205b` | Incremental cross-language migration | Research candidate; star status pending Observatory reconciliation |

## Termux-monorepo development note

GitReverse (`filiksyos/gitreverse`) is a process reference for development happening inside `termux-monorepo`. The reference will inform a further Rust.rs implementation/version, initially developed in the existing Rust migration lane. Track the work as an implementation evolution of that lane; add it as a DoE treatment only after its source revision, capability contract, integration boundary and fixture compatibility are pinned. This is a development note, not a separate repository comparison campaign or a starlist candidate.

## Project and tool distinctions

| Repository | Classification | Verified contract / role |
|---|---|---|
| [timerloggedout-spec/repo-story](https://github.com/timerloggedout-spec/repo-story) | Project | Project identity; keep its project scope and roadmap distinct from repository reconstruction utilities. |
| [timerloggedout-spec/repo-replay](https://github.com/timerloggedout-spec/repo-replay) | Tool | Uses session provenance to build a repository from code extracted from chats. |


## Extensible comparison rules

1. Keep repository identity, upstream identity, fork identity, source commit, license and observation date separate.
2. Treat a curated starlist entry as research intent; the Observatory verifies actual GitHub `starred` provenance.
3. Keep capability-incommensurate studies in separate campaigns. Promote new Rust implementation versions into the existing migration lane only after their contract and fixtures are pinned.
4. Pin each source snapshot before execution. Record later upstream changes as a new version/cohort.
5. Promote reusable patterns only after correctness, provenance, security, maintenance and cost evidence passes the existing repository gates.

## Links

- [Repository Observatory](./README.md)
- [Stars | Forks | Watch evaluation](./STARS-FORKS-WATCH.md)
- [Canonical repository index](../../workspace/llm_map/repositories/repository-index.json)
- [Rust migration DoE candidate](../../experiments/doe/rust-migration-tools/README.md)
