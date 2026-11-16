# Context7 + Mintlify MCP operating contract

**Status:** ACTIVE guidance for documentation and implementation work  
**Scope:** repository source documentation, current API/framework research, and operator-side Mintlify editing  
**Repository:** `timerloggedout-spec/termux-monorepo`

## Purpose

Use Context7 and Mintlify MCP as complementary tools, not competing sources of truth:

- **Context7** retrieves current, library-specific documentation and examples to inform implementation and docs.
- **Mintlify MCP** inspects and edits the connected documentation deployment, navigation, configuration, comments, analytics, and deployment state where the connected account exposes those capabilities.
- **GitHub** remains the reviewable source of truth for repository changes. A successful MCP edit, preview, or docs deployment does not establish code correctness or replace repository CI.

This document describes an operator workflow. It does not assert that every developer runtime has the same MCP servers, credentials, deployment permissions, or plan entitlements.

## Context7 research protocol

1. **Resolve before querying.** Resolve the official library/product name to a Context7 library ID unless the requester supplied a valid `/org/project` or versioned ID.
2. **Choose the right source.** Prefer the official project/library documentation and the relevant version. If resolution returns several candidates, select by exact name, source reputation, version match, and relevance; record ambiguity when it affects the answer.
3. **Ask a narrow question.** Query one concept at a time (for example, configuration schema, API behavior, migration, or security semantics). Split unrelated concepts into separate calls.
4. **Bind advice to versions.** Record the library ID and version when available. If the repo pins a version, investigate that version instead of assuming latest behavior is compatible.
5. **Verify consequential claims.** For security-sensitive behavior, breaking changes, deployment semantics, or uncertain examples, cross-check primary project documentation and the repository's pinned dependency/configuration.
6. **Use snippets as evidence, not authority over the codebase.** Adapt examples to repository conventions, tests, supported runtimes, and threat model. Do not paste examples blindly.
7. **Preserve provenance.** In substantive implementation or architecture docs, state what was checked, the relevant version/date when material, and any remaining uncertainty. Do not claim a tool ran, a dependency is installed, or an API is available unless observed.

Never send credentials, tokens, personal data, private source code, or confidential prompt contents to a documentation lookup query.

## Mintlify MCP workflow

Use the connected Mintlify MCP for the documentation deployment it can actually access:

1. **Discover scope first.** List deployments and branches when the target is not already known. Confirm the correct subdomain, deploy branch, page path, and permission boundary.
2. **Inspect before editing.** Search for existing pages and duplicate concepts, then read the complete target page. Read navigation/configuration before making structural changes.
3. **Make minimal, coherent edits.** Use body-edit operations for MDX body text. Use structured node operations for page frontmatter/navigation metadata and the configuration operation for site-level `docs.json` settings. Do not treat generated catalogs or previews as editable source.
4. **Preserve source-of-truth boundaries.** For this repository, Git-tracked MDX and `docs.json` are the version-controlled publication inputs. A Mintlify editor change is not considered incorporated into the monorepo until the corresponding change is represented in Git and reviewed.
5. **Verify the patch.** Inspect the diff/status, check links and navigation completeness, and ensure the page's terminology and links match the repository. Keep source diagrams authoritative and generated renders derived.
6. **Use review-first publication.** For material documentation changes, prefer a branch/PR. Do not merge, publish directly to production, or change site-wide settings unless the user explicitly asks to ship that change.
7. **Verify deployment separately.** A saved edit or opened PR is not a live deployment. Check the returned deployment status and report the exact state without promoting preview success into production success.

The connector's visible tools and permissions can vary by connected deployment, account, and plan. Discover capabilities at runtime rather than assuming a fixed tool inventory.

## AI-agent discoverability

For Mintlify-hosted documentation, evaluate these as separate surfaces:

- `docs.json`: navigation, site metadata, and published page structure.
- `/llms.txt`: structured documentation index and agent guidance generated from the configured site.
- `/llms-full.txt` and `/.well-known/llms-full.txt`: full Markdown context surfaces when enabled/available on the deployment.
- Hosted `/mcp`: documentation search MCP surface when enabled for the site.
- Mintlify remote MCP: authenticated operator editing/search surface; distinct from the public docs-search MCP.

When improving discoverability, verify the actual deployed URLs and generated output. Do not assume every endpoint is enabled, every page is public, or hidden/private content is exposed. Consider `markdown.instructions` in `docs.json` only when site-wide agent instructions are useful and can be maintained as a concise, stable contract. Avoid duplicating entire repo governance files into global instructions.

## Quality and security gates

- **Documentation correctness:** primary-source/version check + repository consistency.
- **Navigation correctness:** intended public pages are present in `docs.json`; hidden/private content is not accidentally surfaced.
- **Link correctness:** internal paths and external destinations resolve as intended.
- **Publication correctness:** PR/commit, preview, and production deployment states are reported independently.
- **Engineering correctness:** code tests, security scans, and repository gates remain independent; Mintlify status is not an engineering correctness signal.
- **Credential hygiene:** never commit MCP credentials or private deployment configuration. Keep user-specific/private MCP configuration outside the repository.
- **Evidence discipline:** distinguish `DRAFTED`, `COMMITTED`, `PREVIEWED`, `PUBLISHED`, and `DEPLOYED`; do not collapse them into a single success state.

## Recommended task loop

```text
RECON
  -> resolve current docs (Context7)
  -> inspect repo + published docs (GitHub / Mintlify MCP)
  -> plan minimal change
  -> edit on branch
  -> diff + link/nav validation
  -> repository checks / docs preview
  -> re-fetch resulting state
  -> compare evidence
  -> record outcome
```

## Related repository references

- [Mintlify documentation surface](MINTLIFY.md)
- [Agent team roster](AGENT-TEAM-ROSTER.md)
- [Repository docs configuration](../../docs.json)
- [Codex MCP baseline](../../.codex/config.toml)
