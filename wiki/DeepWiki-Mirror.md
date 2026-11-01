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

Owner ruling: **DEVINdeepWiki ≠ DeepWiki.com** — two distinct surfaces, recorded separately. Do not merge their credentials, interfaces, or state.

### Surface A — DEVINdeepWiki (Devin / Cognition)

- **What:** org branch-level wiki material (the private Devin wiki linked from Home).
- **Interfaces:** v3 REST indexing **write** (`scripts/agentic/devin_wiki_indexing.py` + the reconcile workflow); `mcp.devin.ai`.
- **Credentials:** `DEVIN_API_KEY` + `DEVIN_ORG_ID` + `DEVIN_WIKI_EFFORT` (the first is the repository's canonical Devin credential name, allow-listed in `.github/connectors/connector_manager.py`).
- **State** (gate in the register, PR #3323): all three ABSENT firsthand (0 of 66 secrets, 0 of 19 vars) ⇒ the indexing leg is `not_provisioned` and makes **no Devin calls**. The owner manually refreshed repo + branches on 2026-11-01 — the stopgap this automation replaces once provisioned.
- Owner standing note, 2026-11-01: "Devin API remains required for Wiki etc."

### Surface B — DeepWiki.com

- **What:** public repo wiki material (`deepwiki.com/timerloggedout-spec/termux-monorepo`).
- **Interfaces:** web + `mcp.deepwiki.com`, **read-only** (public MCP read tools: `read_wiki_structure` / `read_wiki_contents` / `ask_question`).
- **Credential:** none.

### Collision note — not wiki-surface credentials

- `DEEPWIKI_LLM_API_KEY` = the independent **deepwiki-rs** family (local generation in the fabric workflow) — not a Cognition credential for either surface above.
- `DEEPWIKI_TOKEN` = the fabric probe credential (`remote-knowledge-fabric.yml`, `dwiki check`) — a third distinct item, not a wiki-surface credential.

This dependency set is **distinct from the managed mirror** described above: publishing `wiki/` to GitHub Wiki via `.github/workflows/publish-wiki.yml` needs no Devin credential — it runs on the repository's operator-token lane over reviewed content.

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
