# DeepWiki → GitHub Wiki mirror

## Source boundaries

| Source | Role | Trust boundary |
|---|---|---|
| Private Devin Wiki | Documentation-generation and discovery aid | Private, provider-authenticated; not a GitHub Actions writer |
| Public DeepWiki | Optional public discovery surface | Indexed, source-linked snapshot verified 2026-08-20; validate its source ref and material claims before adoption. |
| In-repository `wiki/` directory | GitHub Wiki publication source | Reviewed repository content |
| GitHub Wiki | Published Markdown projection | Updated only by the managed publisher |

Devin can generate structured documentation, diagrams, and source links. GitHub Wiki is a separate `*.wiki.git` repository. The authoritative mirror mechanism is the reviewed `wiki/` directory and `.github/workflows/publish-wiki.yml`; it does **not** retrieve undocumented private Devin Wiki pages. Public DeepWiki may lag the default branch or refresh on a provider-controlled cadence, so an indexed page is useful for discovery but never replaces current source validation.

## How the managed mirror works

1. Documentation intended for publication is added to `wiki/` through the normal repository review process.
2. A change merged to the repository default branch that touches `wiki/**` runs the managed `Publish wiki` workflow.
3. The workflow publishes `wiki/` to `https://github.com/timerloggedout-spec/termux-monorepo/wiki`.
4. The control-plane reconciler detects repositories reachable by the repository’s established job-scoped operator-token lane and can propose the same publisher as a reviewable PR. It never changes a default branch or merges a PR.

The publisher may be manually dispatched with `dry_run=true` to validate its configuration without modifying GitHub Wiki.

### One-time bootstrap

GitHub creates the `*.wiki.git` backend after the first wiki page exists. If this repository’s Wiki has not yet been initialized, create a page such as `Home` in the Wiki UI, merge the source change, then run **Actions → Publish wiki**. If the first run fails because the Wiki is empty, use `strategy: init` for one reviewed bootstrap run before returning to `strategy: clone`.

## Working with Devin DeepWiki

Devin’s documented `.devin/wiki.json` configuration can steer which pages its generator produces. It is appropriate to use that configuration to improve documentation coverage, but it is not an export or synchronization interface.

A human should review and bring generated content into this repository using one of these evidence-preserving paths:

1. Export or copy the desired Devin Wiki material through an authenticated Devin session, then add normalized Markdown under `wiki/` in a pull request.
2. Ask a Devin session to prepare Markdown files suitable for GitHub Wiki, then review the result and commit the approved pages under `wiki/`.
3. Use a public exporter only while the public DeepWiki repository is actually indexed; preserve the source URL, indexed source reference, and verification date in the pull request.

Do not store Devin API tokens, browser cookies, or exported session state in this repository. Treat agent-generated claims as discovery aids and corroborate material statements with repository source, commits, or issue/PR evidence.

## Credential dependency (recorded 2026-11-01)

The **DeepWiki side** of this surface — Devin's generated wiki and its indexing — depends on **`DEVIN_API_KEY`**, the repository's canonical Devin credential name (allow-listed in `.github/connectors/connector_manager.py`). Indexing writes go through the Devin v3 REST API (`scripts/agentic/devin_wiki_indexing.py` + the reconcile workflow). Owner standing note, 2026-11-01: "Devin API remains required for Wiki etc." — this dependency is standing, not incidental.

Do not conflate the three Devin/DeepWiki credential surfaces:

| Surface | Credential | Mechanism |
|---|---|---|
| Devin Wiki indexing (write) | `DEVIN_API_KEY` | v3 REST indexing API |
| Wiki status probe (fabric) | `DEEPWIKI_TOKEN` | `remote-knowledge-fabric.yml` — `dwiki check` against the Devin MCP endpoint |
| Local wiki generation (fabric) | `DEEPWIKI_LLM_API_KEY` | `deepwiki-rs` in the fabric workflow (+ base-url / model vars) |

This dependency is **distinct from the managed mirror** described above: publishing `wiki/` to GitHub Wiki via `.github/workflows/publish-wiki.yml` needs no Devin credential — it runs on the repository's operator-token lane over reviewed content.

Additional DeepWiki refreshes beyond Devin's built-in cadence are a candidate **webWrapper** vehicle (Swarm ww lead, in parallel) — recorded here as a pointer only; that work is not part of this surface.

## Page conventions

- `Home.md` is the landing page.
- Filenames become page titles (`My-Page.md` becomes “My Page”).
- Avoid `\ / : * ? " < > |` in titles.
- Mermaid fenced blocks generally render.
- Prefer relative wiki links such as `[Architecture](Architecture)`.

## Related

- Managed publisher: `.github/workflows/publish-wiki.yml`
- Repository-surface control plane: `.github/workflows/reconcile-repository-surface.yml`
- Reconciliation design: `docs/agentic/repository-surface-reconciliation.md`
- DeepWiki evidence policy: `docs/agentic/deepwiki-validation.yaml`
