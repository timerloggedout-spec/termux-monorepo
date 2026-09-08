# Repository Observatory

The Repository Observatory maintains a provenance-aware index of repositories owned by `timerloggedout-spec` and repositories starred by the authenticated GitHub user.

## Artifacts

- [`matrix.md`](./matrix.md) — generated navigation and category matrix.
- [`repository-index.json`](../../workspace/llm_map/repositories/repository-index.json) — canonical machine-readable index.
- [`scripts/github/repository_observatory.py`](../../scripts/github/repository_observatory.py) — collector and deterministic classifier.
- [`.github/workflows/repository-observatory.yml`](../../.github/workflows/repository-observatory.yml) — scheduled/manual publisher.

## Provenance model

A repository can have one or both of these provenance values:

- `owned` — the authenticated user's owned repository.
- `starred` — the authenticated user's starred repository.

The collector preserves both values when a repository belongs to both sets.

## Classification model

Classification is deliberately deterministic in the first implementation. It uses repository name, description, topics, fork/template state, and basic metadata to produce:

- domains
- role
- research value
- integration candidates
- submodule-candidate signal

These are **inferences**, not GitHub facts. They are intended as seeds for later context-relationship and research workflows rather than automatic adoption decisions.

## Credential requirement

The workflow prefers the `REPOSITORY_OBSERVATORY_TOKEN` Actions secret. That credential should be a least-privilege token able to read the authenticated user's starring data; the workflow falls back to `GITHUB_TOKEN` for environments where that endpoint is permitted.

The indexer never writes credentials into the generated artifacts.

## Evolution path

The initial implementation is observation-only. Future work can add:

1. relationship edges to the context-relationship graph;
2. research-seed records;
3. upstream/fork comparison;
4. submodule/template/workflow proposals;
5. semantic enrichment behind the deterministic fact layer.

A starred repository is therefore a **research signal**, not an instruction to import or execute code.
