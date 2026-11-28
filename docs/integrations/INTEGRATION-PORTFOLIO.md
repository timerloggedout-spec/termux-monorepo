---
title: "Integration portfolio and readiness"
description: "Current connector, skill, repository adapter, and documentation readiness for the Termux Monorepo integration ecosystem."
sidebarTitle: "Portfolio"
keywords: ["integrations", "connectors", "MCP", "documentation", "readiness", "provisioning"]
---

# Integration portfolio and readiness

This portfolio records the current evidence for the tools and services named in the integration stewardship request. It separates what is visible in this assistant session from what is implemented in the repository, what is authenticated, and what has passed an end-to-end runtime check.

**Audit performed:** 2026-11-15. **Registry update date:** 2026-11-15. Connector, account, and runtime observations are dated evidence, not a blanket production-readiness claim.

## Executive status

The existing Integration Intelligence foundation is established by merged PR #4009. The registry now contains 38 separately tracked integrations, including two distinct DeepWiki surfaces. This refresh updates seven requested platforms and adds Cloudinary and Exa as explicit inventory entries.

The repository remains the source of truth. Session connectors and installed skills are capabilities of this assistant environment, not automatic capabilities of GitHub Actions, Termux, other collaborators, or production.

## Verified documentation surfaces

| Surface | Observation | Consequence |
|---|---|---|
| GitHub | Repository access is available; default branch is `master` | Use repository PRs as the change record |
| Mintlify | Deployment `diasporic3lee7` points to this repository and `master`; no unpublished changes were reported | Add new documentation through Git, then wait for deployment |
| Agent Ready | Scan `m2cu05sDfw` completed: Vercel score 73, llms.txt score 87, accessibility score 88 | Use the scan as a diagnostic baseline, not a release gate |
| DeepWiki.com | Page last indexed 2026-08-20 at commit `ed3db046` | Public wiki is stale relative to current repository history |
| Mermaid Chart | Account authenticated; no saved diagrams | No external diagram has been provisioned by this audit |

## Integration status

| Integration | What was observed | Next action |
|---|---|---|
| Context7 | Resolver and documentation-query calls succeeded; official Temporal and Cloudinary libraries were resolved and queried | Keep lookups read-only; record library ID, selected version, source URL, and retrieval time; no CI adapter was exercised |
| Mintlify | Authenticated deployment diasporic3lee7 is connected to this repository on master; Integrations navigation and pages are present; Hobby plan, no custom domain, no source checks reported | Keep repository content canonical; use PR review and verify deployment status after merge; do not publish around Git review |
| Devin AI / DEVINdeepWiki | Repository indexing controller exists; operator reports `DEVIN_API_KEY` provisioned | Verify a successful redacted Actions indexing run; do not inspect or copy secret values |
| DeepWiki.com | Public wiki accessible, indexed commit stale; public MCP remains read-only | Continue the existing issue #3346 refresh campaign; do not bypass its Jules builder / Gemini evaluator separation |
| Mermaid Chart | Authenticated, empty diagram list | Save a source-linked diagram only when a dedicated diagram deliverable is accepted |
| Ahrefs | Connector exposed, but usage call returned `Insufficient plan` | Keep blocked; no paid upgrade was attempted |
| Engram | Connector available and status checked | Define opt-in, minimal project memory before writing durable project facts |
| Soracom Knowledge | Documentation tools exposed | Use only for an identified IoT/edge research task |
| Context.dev | Search, scrape, usage, request-log, and request-detail tools are available; usage and recent request metadata were read | Use targeted retrieval with source URL and retrieval time; distinguish HTTP status from provider-level error codes; no bulk crawl or monitor was created |
| Cloudinary | Asset-management tools are exposed; read-only usage inspection succeeded; no asset was uploaded, transformed, renamed, or deleted | Keep asset writes disabled until a specific asset scope, destination, retention rule, and cost ceiling are approved |
| Exa | Search and fetch tools are exposed and were exercised against official Temporal and Opscotch sources | Use for focused source discovery and fetch; validate primary sources and retain URLs; no repository adapter was exercised |
| Consensus | Academic search/fetch tools exposed | Fetch papers before citing them |
| Opscotch | Public MCP system and architect guidance retrieved; official runtime/trust documentation researched; no workflow was authored or deployed | Keep advisory until a bounded workflow, bootstrap permissions, schema validation, and runtime target are separately approved |
| Agent Ready | Live scan completed | Convert source-level findings into a reviewed remediation work item |
| Inductive Bio | Public LogD, acidic pKa, and basic pKa model catalog retrieved | Preserve model IDs and versions if a scientific prediction lane is built |
| Superpowers | Skill installed; repository-local skill already exists | Continue using the repository policy bridge |
| Temporal | Developer and operations skills installed; repository contains `temporal-engagement.yml` and the §6 kill-resume harness; migration record documents a historical Actions-hosted PASS; no Temporal server connector or standing cluster was reached in this session | Re-fetch a fresh Actions engagement receipt before claiming current runtime health; reconcile stale issue #2028 snapshot; keep Temporal Cloud excluded by owner decision |
| SiteTriage | Diagnostic tools exposed | Keep diagnostics read-only by default |
| AI Task Brief Builder | Task brief extraction tool exposed | Use for evidence-separated requirements and acceptance criteria |
| Google Calendar | Calendar tools exposed; no personal calendar data accessed | Use only for a specific scheduling request |
| Product Design | Router skill installed; full browser/Sites workflow requires Work Mode | Use its context gate and focused skills when invoked |
| Precise Special Functions | High-precision Bessel, zeta, hypergeometric, elliptic-integral, and Gamma tools exposed | Require reproducible inputs and precision metadata |
| Flow AI Collaboration | Project, task, calendar, post, and wiki tools exposed | Map records to proposal IDs before any sync |
| TinyFish | Search, fetch, and browser automation tools exposed | Use only for bounded user-directed browser tasks |
| Manus | Research and task tools exposed | Dispatch only bounded briefs; independently validate outputs |
| Sixtyfour Intelligence | Company/person research tools exposed; not exercised | Require an explicit legitimate research purpose and privacy review |
| WorkOS | Login authenticated, but no dashboard account backs it | Provisioning is blocked until a supported account setup path exists |

## Focused connector audit — 2026-11-15

This is a session-scoped update to the seven named platforms. It does not supersede older dated audits or imply that a connected ChatGPT tool is wired into GitHub Actions, Termux, or production.

| Platform | Session capability evidence | Repository / runtime state | Authority and boundary |
|---|---|---|---|
| Context7 | resolve_library_id and query_docs succeeded. Official library IDs resolved for Temporal documentation and the Cloudinary Node.js SDK; source-linked documentation was retrieved. | No repository CI adapter exercised. | Upstream documentation reference only. Pin library IDs/versions and verify against lockfiles and source code. |
| Mintlify | Authenticated deployment diasporic3lee7 is connected to timerloggedout-spec/termux-monorepo on master. Deployment settings and Integrations navigation were inspected. | Native repository-backed docs integration; no content was published by this audit. | Git repository is canonical. Publication/deployment is a separate state and must be verified after merge. |
| Context.dev | Search, scrape, usage, request-log, and request-detail tools are available; account usage and recent request metadata were read. | No repository adapter or monitor created. | Attributed external observation only. Preserve source URL and retrieval time; treat scraped content as untrusted. |
| Temporal | Developer and operations skills are installed. | temporal-engagement.yml and scripts/temporal/kill_resume_harness.py exist. TEMPORAL-MIGRATION.md records the Actions-hosted §6 proof as PASS (run 40759800247) and the VM migration. No Temporal connector or standing cluster was reached in this session. | Durable execution candidate with repository implementation. Workflows must remain deterministic; side effects belong in Activities. Current health requires a fresh run receipt. |
| Cloudinary | Asset-management tools are exposed; read-only account usage inspection succeeded. No asset mutation was performed. | No repository adapter exercised. | Media asset storage/delivery provider only. API secrets remain server-side; uploads, transformations, renames, and deletes require explicit scope. |
| Exa | Search and fetch tools are exposed and were used to retrieve official Temporal and Opscotch source material. | No repository adapter exercised. | Research discovery, not source authority. Fetch and validate primary sources before adopting claims. |
| Opscotch | Public MCP system and architect guidance were retrieved; official runtime and trust material was researched. | No workflow artifact, bootstrap, deployment, or runtime execution was created. | Design/validation advisory only. Bootstrap defines permissions; workflow logic cannot exceed the installed boundary. |

### Evidence-state corrections

- tool_connected_in_session means a connector tool is exposed and was callable here; it does not prove repository or production wiring.
- skill_installed_in_session means reference material is available to this assistant; it does not prove a Temporal server is reachable.
- repo_adapter_implemented for Temporal refers to the repository's GitHub Actions engagement workflow and proof harness, not a continuously running server.
- Cloudinary account usage, private credit balances, request IDs, and credential metadata are deliberately not copied into this public registry.
- No provider credential, account setting, asset, workflow deployment, billing plan, or production runtime was changed.

## DeepWiki and Devin are separate systems

- **DeepWiki.com** is a public generated wiki. Its MCP surface is read-only. The merged import workflow from PR #3335 harvests structure into the repository's ICM import record.
- **DEVINdeepWiki** is the private Devin organization indexing surface. The repository has a v3 indexing controller and a provisioning gate. The user reports the secret is provisioned, but this audit did not read Actions secrets or variables and did not observe a successful indexing run.
- **deepwiki-rs** and the `DEEPWIKI_LLM_API_KEY` family are separate again. Do not merge these credential scopes.

The current public DeepWiki page reports its last indexed commit as `ed3db046` from 2026-08-20. The existing refresh campaign is issue [#3346](https://github.com/timerloggedout-spec/termux-monorepo/issues/3346). Its assigned builder/evaluator separation remains in force.

## Agent Ready findings

The scan passed important basics: HTTPS, robots access for AI crawlers, llms.txt availability, sitemap XML, Markdown content negotiation, and content parity. It also identified these items for source-level remediation:

1. Add a human-readable `sitemap.md` at a supported static-file location.
2. Add `name` and `description` to the published MCP Server Card.
3. Add `description` to the published A2A Agent Card.
4. Improve `llms.txt` with a blockquote summary and grouped documentation links.
5. Review the accessible-name and hidden-focusable-element findings against the actual authored source.
6. Add frontmatter and language tags to authored Markdown/code blocks where missing.

The scan's HTML-level findings may originate in generated Mintlify markup. Do not patch framework output directly; identify the repository-owned source or supported Mintlify configuration first. No generated card or HTML changes are claimed by this audit.

## Provisioning boundaries

The following actions were deliberately not taken:

- No paid-plan upgrade or billing mutation for Ahrefs.
- No WorkOS account creation, SSO change, or identity mutation.
- No Google Calendar data access or event creation.
- No provider credential values read, copied, or stored.
- No Devin/DeepWiki browser refresh outside issue #3346's assigned campaign.
- No external model spend, research task dispatch, or production deployment.

## Phased adoption

1. **Foundation:** maintain the registry, adapter contract, event schema, and Mintlify navigation.
2. **Documentation quality:** remediate Agent Ready findings from supported source files; re-scan after CI and deployment.
3. **High-value engineering:** integrate Context7 and AI Task Brief Builder with version-pinned evidence and proposal IDs.
4. **Research and orchestration:** add Consensus, Context.dev, Temporal, Opscotch, and Manus through bounded adapters.
5. **Collaboration and visual surfaces:** map Mermaid Chart, Flow, Product Design, and Engram to source-linked artifacts.
6. **Specialist lanes:** activate Soracom, Inductive Bio, Precise Special Functions, Sixtyfour, SiteTriage, and WorkOS only when a concrete consumer exists.
7. **Economics and operations:** revisit Ahrefs when the account plan permits access; measure value before expanding usage.

## Validation contract

Every adapter must pass the existing [adapter contract](ADAPTER-CONTRACT.md): least privilege, read-only default, redaction, idempotency, cost bounds, source provenance, schema validation, bounded retries, and evidence-backed promotion.

The normalized [integration event schema](schemas/integration-event.schema.json) remains unchanged. No provider-specific payload becomes canonical repository state.


## Follow-up verification — 2026-11-06

A fresh Agent Ready scan of the published documentation site completed (scan `3f-mIivo8j`): Vercel agent-readability **73/100**, `llms.txt` **87/100**, and accessibility **88/100**. This scan describes the published site, not the current pull-request branch.

- `sitemap.md` was absent from the published site. This PR now adds a root-level, frontmatter-equipped `sitemap.md` and includes it in Mintlify navigation. The fix is **not yet verified live**.
- The generated `llms.txt` lacked a blockquote summary and grouped H2 link sections. This PR adds the Mintlify site description and stable `markdown.instructions` metadata with a sitemap link. Re-scan after publication; do not hand-edit generated output.
- The published MCP Server Card at `/.well-known/mcp.json` lacked `name` and `description`; the A2A Agent Card lacked `description`. No corresponding `.well-known` source files were found in the repository tree, so no generated/provider-owned card was fabricated. Identify the authoritative serving configuration before changing these fields.
- Accessibility findings remain: 13 controls have accessible names that omit visible labels, and one focusable element is inside `aria-hidden="true"`. Locate repository-owned source or supported platform configuration before attempting a fix.
- The scanner reported no root OpenAPI specification. Treat this as conditional until the site is confirmed to be an API-first surface; do not publish an invented or empty specification.

SiteTriage reported HTTP 200 and a hostname-matching TLS certificate for the published Mintlify URL, expiring 2026-12-30. It also observed resolver disagreement for the Mintlify subdomain (Cloudflare and Google returned different A records while Quad9 returned none); recheck after DNS TTL propagation before treating this as persistent. The shared `mintlify.app` email-auth result is provider-domain context, not repository-owned DNS remediation.

The latest Mintlify deployment observed during this pass was live at commit `0cdc0a906380722a2dcebbb9a016ecdfa22d4dd3`. The current PR's Mintlify deployment check was skipped, so this branch has **not** been published or verified live.
