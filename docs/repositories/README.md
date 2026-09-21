# Repository Observatory

The Repository Observatory maintains a provenance-aware index of repositories owned by `timerloggedout-spec` and repositories starred by the authenticated GitHub user.

## Artifacts

- [`matrix.md`](./matrix.md) — generated navigation and category matrix.
- [`repository-index.json`](../../workspace/llm_map/repositories/repository-index.json) — canonical machine-readable index.
- [`repository-observatory.schema.json`](./repository-observatory.schema.json) — JSON Schema for the canonical index contract.
- [`scripts/github/repository_observatory.py`](../../scripts/github/repository_observatory.py) — collector, normalizer, and deterministic classifier.
- [`scripts/github/test_repository_observatory.py`](../../scripts/github/test_repository_observatory.py) — dependency-free unit tests.
- [`.github/workflows/repository-observatory.yml`](../../.github/workflows/repository-observatory.yml) — scheduled/manual publisher and validation gate.

## Production contract

The workflow is intentionally idempotent and delta-oriented. Repository records are canonicalized, hashed with SHA-256, and sorted deterministically. The observation timestamp is retained when the repository snapshot is unchanged, preventing scheduled runs from creating commits solely because the clock changed.

The collector uses bounded pagination (100 pages × 100 records maximum per endpoint), retries transient GitHub API failures with backoff, fails closed on authentication mismatch, and never emits credentials into repository artifacts.

The workflow runs tests before polling, validates the generated artifact shape, publishes an Actions summary, and commits only changes to the canonical JSON or generated Markdown projection.

## Provenance model

A repository can have one or both of these provenance values:

- `owned` — the authenticated user's owned repository.
- `starred` — the authenticated user's starred repository.

The collector preserves both values when a repository belongs to both sets.

## Classification model

Classification is deliberately deterministic. It uses repository name, description, topics, fork/template state, and basic metadata to produce:

- domains
- role
- research value
- integration candidates
- submodule-candidate signal

These are **inferences**, not GitHub facts. They are intended as seeds for later context-relationship and research workflows rather than automatic adoption decisions.

## Security and credentials

The workflow prefers the `REPOSITORY_OBSERVATORY_TOKEN` Actions secret. Configure it as a least-privilege credential capable of reading the authenticated user's starring data. `GITHUB_TOKEN` is retained as a fallback for installations where the endpoint is permitted.

No token, authorization header, or secret value is written to generated artifacts. The authenticated username is checked against `GITHUB_REPOSITORY_OWNER` before collection proceeds.

## Evolution path

1. Add relationship edges to the context-relationship graph.
2. Materialize explicit research-seed records with provenance back to the repository record.
3. Add upstream/fork comparison and change detection.
4. Generate submodule/template/workflow proposals without automatically adopting code.
5. Add optional semantic enrichment behind the deterministic fact layer.

A starred repository is a **research signal**, not an instruction to import, execute, or trust code.
