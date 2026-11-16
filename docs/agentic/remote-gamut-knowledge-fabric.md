# Remote GAMUT + Knowledge Fabric

## GAMUT

The GAMUT adapter runs remotely on a GitHub-hosted runner behind the `gamut-evaluation` GitHub Environment. The Environment is the credential/optional approval boundary; GitHub Actions is the compute boundary.

This targets **facebookresearch/GAMUT**, the factual-completeness benchmark, not Gamut AI's governance platform. Its evaluator accepts a JSONL response file and an OpenAI-compatible judge endpoint. The benchmark/evaluator is CC-BY-NC-4.0, so this lane remains benchmark-scoped and is never a generic merge gate.

The workflow always runs the upstream evaluator smoke test. A full run is manual and requires the Environment secret `GAMUT_JUDGE_API_KEY`, a response JSONL path, and a judge model. An optional OpenAI-compatible `base_url` is supported.

No Termux execution is required.

## Knowledge fabric

The remote controller enumerates all repositories exposed by the GitHub App installation and creates a redacted repository manifest. The knowledge fabric has three complementary documentation/intelligence surfaces:

1. **wiki-rs** — `sw-vibe-coding/wiki-rs`, used as the coordination/storage adapter boundary.
2. **deepwiki-rs / Litho** — `sopaco/deepwiki-rs` 1.6.0, used as the remote Rust documentation/C4 generation engine.
3. **DevinWiki / DeepWiki** — provider-managed external indexing, probed through `dwiki` when configured.

`wiki-rs` and `deepwiki-rs` are deliberately not treated as substitutes. wiki-rs supplies storage/coordination primitives; deepwiki-rs analyzes repositories and generates architecture documentation. DevinWiki remains an external provider surface.

### wiki-rs

The workflow clones and tests the upstream workspace remotely. Its documented storage model includes ephemeral, browser, export/import, server-file, server-database, and server-Git backends. The initial repository integration remains an adapter boundary: remote validation plus normalized manifest generation. It does not vendor or fork the project.

The eventual write adapter should use the engine's concurrency contract rather than inventing another lock protocol.

### deepwiki-rs / Litho

Litho is a Rust multi-stage documentation engine that analyzes source structure, relationships, and architecture and produces C4-oriented documentation. The workflow pins the released crate to **1.6.0** for the explicit generation lane and also clones the upstream repository to run its workspace tests remotely.

Generation is deliberately an explicit cost/privacy boundary. A scheduled run validates the engine but does not send repository source to an LLM. A manual run may set `generate_deepwiki=true`, choose `current` or `all` repositories, and provide the `DEEPWIKI_LLM_API_KEY` secret plus optional provider base URL/model variables. Generated source-derived documentation is not uploaded as an artifact.

### DevinWiki / DeepWiki

Devin/DeepWiki remains provider-managed. The controller records indexing status only. It does not treat provider output as authorization and does not copy private wiki pages into Git.

Existing `reconcile-devin-wiki-access.yml` remains the App-access assignment controller.

## Scope and boundaries

- No Gamut customization proposal is carried forward.
- No Codespace is required for scheduled evaluation; GitHub-hosted Actions is the reproducible remote boundary.
- Codespaces remain useful for interactive wiki-rs/deepwiki-rs development and debugging.
- Discovery is all-repository by App installation scope; mutation remains separately gated.
- No generated wiki content is automatically committed or published by this lane.
- Secrets and private keys are never written to artifacts.
