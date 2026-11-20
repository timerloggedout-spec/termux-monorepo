# Capability Discovery, Classification and Progressive Activation

**Status:** implemented first slice; external ingestion remains candidate-only.
**Runtime:** `scripts/capabilities/discover.py`
**Taxonomy:** `ops/capability_discovery/taxonomy.json`
**Source registry:** `ops/capability_discovery/sources.json`
**Record contract:** `ops/capability_discovery/record.schema.json`

## Objective

Discover the broad capability universe while keeping model context small. Search nested repository workspaces, all supported skill file forms, vendor directories, external skill catalogs, plugin skill catalogs and tool-action exports. Classify and deduplicate candidates before loading full instructions or tool schemas.

The index is a metadata projection, not a new source of truth. Plugin manifests are indexed without copying server commands, endpoint credentials or complete tool schemas. Canonical files and providers retain ownership of their definitions, permissions, versions and runtime state.

## Nested discovery coverage

The repository scan recognizes:

- `.agents/**/SKILL.md` — agent-loadable skills;
- `.github/**/SKILL.md` — automation and production skills;
- `.claude/**/SKILL.md` — harness-specific skills;
- `docs/**/SKILL.md` — documentation mirrors and operational companions;
- nested `workspace/**/SKILL.md`, `SKILLS.md`, `*.SKILLS`, and `*.skill`;\n- plugin/tool manifests: `plugin.json`, `marketplace.json`, `.mcp.json`, `mcp.json`, `tools.json` and `tool-manifest.json`; only manifest identity, description, version and entry counts are indexed;\n- explicitly allowlisted sibling workspace roots supplied with repeatable `--extra-root` flags; these are tagged `workspace-external` / `unverified` and receive separate external locators;
- `vendor/**` skill definitions, classified as unverified vendor inputs;
- optional JSON exports of session plugin skills and tool actions.

The recursive scan excludes common generated/cache directories and skips symlinks. External roots are opt-in; the scanner does not walk the home directory or sibling workspaces implicitly. It reads skill bodies only to derive a SHA-256 and extract frontmatter metadata; it stores no complete instruction body, tool schema, prompt, credential or completion.

At the current master baseline `57559c9100f9df2868398603410e6ba28783a942`, the recursive tree contained 45 `SKILL.md` paths, one root `SKILLS.md`, zero tracked `.skill` archives and zero workspace-nested skill paths. The scanner broadens future discovery to all nested forms; its result is generated from the checked-out tree, not a manually maintained count.

## Classification model

Each capability receives:

1. **Primary domain** — engineering, testing, delivery, research, data, agentic, design, operations or specialized.
2. **Primary function** — the task-level capability within that domain.
3. **Facets** — cross-cutting properties such as vendor, plugin, MCP, CLI, workflow, credentialed, read-only, write-capable, sensitive or experimental.
4. **Trust state** — repository-canonical, official-vendor, verified-upstream, community-reference, session-observed, unverified or quarantined.
5. **Lifecycle state** — discovered → classified → deduplicated → evaluated → eligible → approved → adopted, with deprecated/rejected terminal branches.
6. **Provenance** — exact source locator, retrieval/capture time, immutable source revision where available, content hash and discovery method.

The initial classifier applies deterministic keyword rules constrained by the versioned taxonomy; specialized domains cover finance, health, legal, regulatory, scientific, media, property, automotive and outdoors. Treat classifications as routing hints, not quality or safety verdicts. Use one primary domain/function and multiple facets. This avoids multiplying duplicate records for a skill that spans several areas. SQLite stores aliases and permission metadata, while the relationship table records exact-content matches and supports future alias/cross-domain edges; the current automatic edge is `content_identical`.

### Identity and deduplication

Canonical identity uses source locator plus package/skill/action identifier. Names alone are insufficient. Content hashes detect changed definitions. Exact content matches create `content_identical` relationship edges while keeping the source records distinct. Keep forks, versions and aliases distinct; link them through relationships rather than silently merging them. Record duplicate candidates and their resolution in the ledger.

## Progressive loading and context budget

```text
task intent
   ↓
local metadata index ──→ nested tags + trust + provenance
   ↓
ranked top-k candidates
   ↓
inspect selected skill/tool source
   ↓
type-specific quality + permission checks
   ↓
authorized execution / experiment / adoption
```

Default behavior returns a small metadata-only shortlist (top 8). Load full skill instructions or tool schemas only for selected candidates. Fetch a tool's schema just before invocation. Use the exact action rather than injecting an entire namespace.

The SQLite database stores aliases, permission metadata, taxonomy hashes and relationship edges; the JSONL event ledger records added, changed and reclassified definitions. It uses FTS5 when available and a LIKE fallback otherwise. Skill/archive reads are capped at 2 MB per definition to bound resource use. The database and JSONL discovery-event ledger are local generated artifacts under `.cache/`; commit source code, schemas and taxonomy, not the mutable database or per-session exports. CI may upload a dated, sanitized snapshot artifact when required.

## Sources and vendor caution

The source registry declares local, vendor, external-catalog and session-snapshot sources. It records the ingestion mode and auth constraints.

- **skills.sh** exposes paginated leaderboard, fuzzy/semantic search, curated vendor skills, detail/file-tree and partner security-audit endpoints. Search accepts `q` (minimum two characters) and `limit` (1–200); multiword queries use semantic search. The API uses short-lived Vercel OIDC bearer authentication, with a documented 600 requests/minute per team/project limit. Read a fresh request-scoped token, refresh expired local tokens, and keep the token out of the repository and ledger. Detail records include a stable ID and content hash; use that hash for cache invalidation. Audit returns partner results from Gen Agent Trust Hub, Socket, Snyk, Runlayer and ZeroLeaks; a 404 means no audit is available yet. The documented CLI install form is `npx skills add <owner/repo>`; its anonymous telemetry includes skill name, skill files and timestamp by default, with `DISABLE_TELEMETRY=1` as opt-out. The local SQLite cache holds fuzzy/semantic search results for 45 seconds and curated results for 5 minutes, aligned with the upstream cache windows; it stores sanitized metadata only. Search/audit before install; popularity is not a security review. ([API](https://www.skills.sh/docs/api), [CLI](https://www.skills.sh/docs/cli))
- **Approxination** complements skills.sh with ranked skill search, generation and execution feedback. Its A/B/C/D tool-layer cohort is already governed by `approxination-lane`; hosted calls require the provisioned token and explicit budget. Reuse its lane rather than building a second ranking service.
- **Anthropic** — `anthropics/skills` is Anthropic's reference implementation. Inspect each skill's license individually; the repository has mixed licensing, including proprietary document skills. ([Repository](https://github.com/anthropics/skills))
- **Microsoft** — `microsoft/skills` includes Azure SDK/AI Foundry skills, agents, AGENTS.md and MCP configurations. Its README labels the repository work in progress; select individual skills rather than loading the entire deep tree. ([Repository](https://github.com/microsoft/skills))
- **Vercel** — `vercel-labs/agent-skills` includes React/Next.js best practices, web-design guidelines and Vercel optimization skills. ([Repository](https://github.com/vercel-labs/agent-skills))
- **Cloudflare** — `cloudflare/skills` bundles skills and a native plugin that installs Cloudflare guidance plus the Cloudflare MCP server. Review plugin manifests and requested MCP scopes. ([Repository](https://github.com/cloudflare/skills))
- **Trail of Bits** — `trailofbits/skills` distributes security analysis, testing and development skills through plugin marketplaces. ([Repository](https://github.com/trailofbits/skills))
- **Hugging Face** — `huggingface/skills` provides Hub, dataset, training and evaluation workflows; its `hf-cli` skill is generated from the installed CLI and is the recommended bootstrap path. ([Repository](https://github.com/huggingface/skills))
- **OpenAI** — use `openai/plugins` for current Codex plugin examples; a plugin can bundle a manifest, skills, MCP config, agents, commands, hooks and assets. The separate `openai/skills` repository is deprecated and points to the plugin repository. ([Plugins](https://github.com/openai/plugins), [deprecated skills](https://github.com/openai/skills))
- **GitHub** — `github/awesome-copilot` is an organization-hosted community collection, not a vendor-supported product contract. ([Repository](https://github.com/github/awesome-copilot))
- **Anthropic plugins** — `anthropics/claude-plugins-official` is now the home of Anthropic's own plugins; third-party submissions are moving to the Claude directory. Anthropic explicitly warns that plugins may include MCP servers, files and software it does not control. `anthropics/knowledge-work-plugins` bundles skills, connectors, slash commands and subagents by job function. ([Official plugins](https://github.com/anthropics/claude-plugins-official), [knowledge-work plugins](https://github.com/anthropics/knowledge-work-plugins))
- **Microsoft plugins** — `microsoft/azure-skills` combines Azure guidance with MCP-backed execution; `microsoft/power-platform-skills` includes build/update/publish workflows. Inspect tool scopes and environment mutation boundaries before authorizing. ([Azure](https://github.com/microsoft/azure-skills), [Power Platform](https://github.com/microsoft/power-platform-skills))
- **AWS** — `aws/agent-toolkit-for-aws` supplies agent tools, knowledge and guardrails for AWS build/deploy/manage tasks. Review IAM and account scopes before enabling write actions. ([Repository](https://github.com/aws/agent-toolkit-for-aws))
- **Google agent tooling** — `google/agents-cli` supplies CLI/skills for Gemini agent development; `google-gemini/gemini-skills` covers Gemini API/SDK practices. ([Agents CLI](https://github.com/google/agents-cli), [Gemini skills](https://github.com/google-gemini/gemini-skills))
- **Google skills/plugins** — `google/skills` publishes Google-product skills and bundles plugins/MCP servers for supported agent harnesses. Search by product and install only the specific skill/plugin after source, permission and revision review. ([Repository](https://github.com/google/skills))
- **Jules** — the supplied PDF is a candidate discovery lead. Current upstream `jules-skills` documents `npx skills add google-labs-code/jules-skills --list` and explicitly says the repository is not an officially supported Google product. The current Jules GitHub action README uses `google-labs-code/jules-invoke@v1` with `JULES_API_KEY`; issue-triggered workflows need user allowlists and PR review. The supplied PDF's `google-labs-code/jules-action@v1` / `GEMINI_API_KEY` example is stale relative to the current README. Treat the PDF as historical source material and verify current action contracts before adapting. ([Jules skills](https://github.com/google-labs-code/jules-skills), [Jules action](https://github.com/google-labs-code/jules-action), [security examples](https://github.com/google-labs-code/jules-action/blob/main/examples/README.md))
- **Loopy** is a bounded-loop skill candidate. The supplied JSON describes Discover, Find, Audit, Adapt, Craft, Run, Debrief, Save and Publish routes, with Observe → Choose → Act → Verify → Record → Repeat and explicit terminal states. Its catalog host is a placeholder in the supplied file; resolve the actual upstream catalog before any live Find/Publish integration.
- **Vendor folders and imported archives** remain untrusted data. Inspect provenance, license, scripts, network access, requested permissions, secret patterns and maintenance before install or execution.

The 2026-11-19 session snapshot contains 545 plugin skill references across 74 packages and 4,716 callable actions (4,706 MCP actions across 123 MCP namespaces, plus core tools). Compact indexes live at `docs/integrations/session-plugin-skill-catalog.json` and `docs/integrations/session-tool-action-catalog.json`. These snapshots intentionally omit full tool schemas and truncate descriptions to compact activation summaries.\n\nSession plugin/tool exports are session-observed snapshots. They do not prove account entitlement, connected status in another runtime, or repository adapter availability. The tool host's live schema remains authoritative.

## Evaluation routing

| Candidate type | Quality / evidence lane | Result |
|---|---|---|
| Skill definition (`SKILL.md`, `*.skill`) | `scripts/ci/evaluate_skills.py` + Skill Evaluation lane | structural definition quality |
| MCP tool definition / action schema | TDQS + `docs/ops/TDQS-ADMISSION-MATRIX.md` | tool-definition quality and server coherence |
| Plugin or external skill package | provenance, license, secret scan, permission review + Skill Evaluation | candidate eligibility |
| Runtime invocation | ATES / WTCV / TCV | execution status and effectiveness |
| Integrated task | deterministic acceptance + independent evidence | outcome, integration, regression and promotion evidence |

Skill quality, TDQS, runtime effectiveness and integrated outcome remain separate. A high-quality definition does not prove successful execution.

## DoE linkage

The new nested discovery factors are registered as dimensions 41–48 in `DOE-QUESTIONS-MATRIX.md`. The design-only campaign `experiments/doe/capability-discovery-routing/DESIGN.json` compares source scope, taxonomy depth and context hydration on fixed task cohorts.

The experiment reuses `docs/ops/corpus/EXPERIMENT.schema.json`. One executed task × treatment × configured instance = one observation. It preserves task-family/difficulty blocks, assignment integrity, interaction analysis, uncertainty, resource cost and permission guardrails.

The campaign is proposal-only until DoE-expert admission, an automation path and configured-instance stamps are verified. Documentation and indexing implementation do not dispatch experiments.

## Commands

```bash
# Build/update local SQLite index and deterministic event-ledger projection
python3 scripts/capabilities/discover.py scan --root .\n\n# Explicitly add selected sibling workspaces; each remains unverified\npython3 scripts/capabilities/discover.py scan --root . --extra-root "$HOME/workspace/project-a" --extra-root "$HOME/workspace/project-b"

# Import session-scoped, metadata-only JSON exports when explicitly supplied
python3 scripts/capabilities/discover.py scan --root . \
  --plugin-skills-json /path/to/plugin-skills.json \
  --tool-actions-json /path/to/tool-actions.json

# Return a compact local shortlist
python3 scripts/capabilities/discover.py find "task intent" --limit 8

# Optional read-only skills.sh catalog search (requires a short-lived Vercel OIDC token)
python3 scripts/capabilities/discover.py find "database agent skills" --skills-sh --owner microsoft --limit 8

# Search the official first-party curated catalog
python3 scripts/capabilities/discover.py find "cloud security" --skills-sh-curated --limit 8

# Focused contract tests
python3 -m unittest tests.test_capability_discovery -v
```

## Acceptance and lifecycle

- Local scan discovers all matching nested paths and labels vendor sources unverified.
- Search returns metadata-only ranked results and supports FTS5 fallback.
- Repeated scans are idempotent; changed content produces a ledger event.
- Session imports retain session-scoped trust and capture date.
- Secret-like content is quarantined; raw content and credentials remain outside the index.
- Skill, TDQS, runtime and outcome evaluation remain type-separated.
- External installs, credential provisioning, write actions, publishing and production promotion stay behind their existing approval gates.

## Reusable task instruction

> Discover capabilities across the full repository and declared external catalogs. Search recursively by tagged domain/function, classify provenance and trust, deduplicate by canonical identity and content hash, and return a metadata-only top-k shortlist. Hydrate only selected definitions. Route skills to Skill Evaluation, tool schemas to TDQS, execution to ATES, and integrated outcomes to DoE/MoneyBall. Update the SQLite projection and evidence ledger, validate the changed source SHA, and preserve approval gates.
