# Remote GAMUT + Knowledge Fabric

## GAMUT

The GAMUT adapter runs remotely on a GitHub-hosted runner behind the `gamut-evaluation` GitHub Environment. The Environment is the credential/optional approval boundary; GitHub Actions is the compute boundary.

This targets **facebookresearch/GAMUT**, the factual-completeness benchmark, not Gamut AI's governance platform. Its evaluator accepts a JSONL response file and an OpenAI-compatible judge endpoint. The benchmark/evaluator is CC-BY-NC-4.0, so this lane remains benchmark-scoped and is never a generic merge gate.

The workflow always runs the upstream evaluator smoke test. A full run is manual and requires the Environment secret `GAMUT_JUDGE_API_KEY`, a response JSONL path, and a judge model. An optional OpenAI-compatible `base_url` is supported.

No Termux execution is required.

## Knowledge fabric

The remote controller enumerates all repositories exposed by the GitHub App installation, creates a redacted repository manifest, validates the external `sw-vibe-coding/wiki-rs` workspace remotely, and optionally probes Devin/DeepWiki indexing.

The GitHub App token is created with `actions/create-github-app-token`, scoped to the current owner's installation, and is short-lived. No private key, installation token, wiki content, prompt, or provider page body is written to the artifact.

### wiki-rs

`sw-vibe-coding/wiki-rs` is treated as the remote wiki engine/coordination adapter. Its documented architecture includes file, database, Git, browser, and ephemeral storage backends. The initial integration is deliberately an adapter boundary: remote build/test plus normalized manifest generation. It does not vendor or fork the project.

The eventual write adapter should use the engine's concurrency contract rather than inventing another lock protocol.

### DevinWiki / DeepWiki

Devin/DeepWiki remains provider-managed. The controller records indexing status only. It does not treat provider output as authorization and does not copy private wiki pages into Git.

Existing `reconcile-devin-wiki-access.yml` remains the App-access assignment controller.

## Scope

- No Gamut customization proposal is carried forward.
- No Codespace is required for scheduled evaluation; GitHub-hosted Actions is the reproducible remote boundary.
- Codespaces remain useful for interactive wiki-rs development/debugging.
- Discovery is all-repository by App installation scope; mutation remains separately gated.
