---
title: "Integration portfolio and readiness"
description: "Current connector, skill, repository adapter, and documentation readiness for the Termux Monorepo integration ecosystem."
sidebarTitle: "Portfolio"
keywords: ["integrations", "connectors", "MCP", "documentation", "readiness", "provisioning"]
---

# Integration portfolio and readiness

This portfolio records the current evidence for the tools and services named in the integration stewardship request. It separates what is visible in this assistant session from what is implemented in the repository, what is authenticated, and what has passed an end-to-end runtime check.

## Executive status

The existing Integration Intelligence foundation is established by merged PR #4009. The current registry contained eight integrations. This expansion adds the requested portfolio as 24 separately tracked entries, including two distinct DeepWiki surfaces.

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
| Context7 | Documentation resolver/query tools exposed | Pin lookups to installed package versions |
| Mintlify | Connected deployment and navigation inspected | Keep Git as source; expose this portfolio in navigation |
| Devin AI / DEVINdeepWiki | Repository indexing controller exists; operator reports `DEVIN_API_KEY` provisioned | Verify a successful redacted Actions indexing run; do not inspect or copy secret values |
| DeepWiki.com | Public wiki accessible, indexed commit stale; public MCP remains read-only | Continue the existing issue #3346 refresh campaign; do not bypass its Jules builder / Gemini evaluator separation |
| Mermaid Chart | Authenticated, empty diagram list | Save a source-linked diagram only when a dedicated diagram deliverable is accepted |
| Ahrefs | Connector exposed, but usage call returned `Insufficient plan` | Keep blocked; no paid upgrade was attempted |
| Engram | Connector available and status checked | Define opt-in, minimal project memory before writing durable project facts |
| Soracom Knowledge | Documentation tools exposed | Use only for an identified IoT/edge research task |
| Context.dev | Search, scrape, and usage tools available | Record source URL and retrieval time for external research |
| Consensus | Academic search/fetch tools exposed | Fetch papers before citing them |
| Opscotch | Public root guidance retrieved | Load system, architect, and engineer guidance before designing a workflow |
| Agent Ready | Live scan completed | Convert source-level findings into a reviewed remediation work item |
| Inductive Bio | Public LogD, acidic pKa, and basic pKa model catalog retrieved | Preserve model IDs and versions if a scientific prediction lane is built |
| Superpowers | Skill installed; repository-local skill already exists | Continue using the repository policy bridge |
| Temporal | Developer skill installed; no Temporal server connector exposed | Reconcile with existing `temporal-langsmith-adapter` proposal |
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
