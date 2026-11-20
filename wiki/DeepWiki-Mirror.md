# DeepWiki → GitHub Wiki mirror

## Source

| Source | URL |
|--------|-----|
| Private Devin Wiki | https://app.devin.ai/org/timerloggedout-spec/wiki/timerloggedout-spec/termux-monorepo |
| Public DeepWiki | https://deepwiki.com/timerloggedout-spec/termux-monorepo |

Devin generates structured docs (architecture, modules, diagrams). GitHub Wiki is a separate git repo (`*.wiki.git`) of Markdown pages. There is no official one-click sync; this repo uses a **folder + Action** pattern.

## How the mirror works

1. **Source of truth in-repo:** the `wiki/` directory (Markdown pages).
2. **Publisher:** `.github/workflows/publish-wiki.yml` runs `Andrew-Chen-Wang/github-wiki-action@v5` on pushes to `master` / `master-staging` that touch `wiki/**`, or via **workflow_dispatch**.
3. **Target:** the repository’s GitHub Wiki (`https://github.com/timerloggedout-spec/termux-monorepo/wiki`).

### One-time bootstrap (required)

GitHub only creates the `*.wiki.git` backend after the first wiki page exists:

1. Open the repo → **Wiki** tab.
2. Create any page (e.g. title `Home`, body `bootstrap`).
3. Merge this feature branch (or push `wiki/` to `master`).
4. Run **Actions → Publish wiki → Run workflow** (or push any change under `wiki/`).

If the first Action run fails because the wiki was empty, temporarily set `strategy: init` in the workflow (force-push), run once, then switch back to `strategy: clone`.

## Refreshing content from Devin DeepWiki

Private Devin Wiki pages are not exposed to the public DeepWiki MCP without indexing/auth. Practical refresh paths:

1. **Manual / browser**  
   Open the Devin Wiki, export or copy pages (Chrome “DeepWiki to Markdown” extensions exist), save as `wiki/<Page-Title>.md`.

2. **CLI exporters** (public DeepWiki once indexed)  
   - `dw2md timerloggedout-spec/termux-monorepo -o /tmp/out.md`  
   - Other tools: `deepwiki-to-md`, interactive exporters on GitHub.

3. **Ask Devin**  
   In a Devin session: “Export the current wiki pages for this repo as Markdown files suitable for a GitHub Wiki (Home.md + one file per page).” Commit the result under `wiki/`.

4. **Conventions**  
   - `Home.md` is the landing page (not `README.md`).  
   - Filenames become titles (`My-Page.md` → “My Page”).  
   - Avoid `\ / : * ? " < > |` in titles.  
   - Mermaid fenced blocks usually render.  
   - Prefer relative wiki links: `[Architecture](Architecture)`.

## Steering Devin’s generation

Optional repo file `.devin/wiki.json` (repo notes + optional explicit `pages` list) steers regeneration inside Devin. That does not automatically update this GitHub Wiki; re-export into `wiki/` after regenerating.

## Related

- Workflow: `.github/workflows/publish-wiki.yml`
- Action docs: https://github.com/Andrew-Chen-Wang/github-wiki-action
