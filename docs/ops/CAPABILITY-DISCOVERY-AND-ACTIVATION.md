# Capability Discovery, Classification and Progressive Activation

**Status:** implemented first slice; external ingestion remains candidate-only.
**Runtime:** `scripts/capabilities/discover.py`
**Taxonomy:** `ops/capability_discovery/taxonomy.json`
**Source registry:** `ops/capability_discovery/sources.json`
**Record contract:** `ops/capability_discovery/record.schema.json`

## Objective

Discover the broad capability universe while keeping model context small. Search nested repository workspaces, all supported skill file forms, vendor directories, external skill catalogs, plugin skill catalogs and tool-action exports. Classify and deduplicate candidates before loading full instructions or tool schemas.

The index is a metadata projection, not a new source of truth. Canonical files and providers retain ownership of their definitions, permissions, versions and runtime state.

## Nested discovery coverage

The repository scan recognizes:

- `.agents/**/SKILL.md` — agent-loadable skills;
- `.github/**/SKILL.md` — automation and production skills;
- `.claude/**/SKILL.md` — harness-specific skills;
- `docs/**/SKILL.md` — documentation mirrors and operational companions;
- nested `workspace/**/SKILL.md`, `SKILLS.md`, `*.SKILLS`, and `*.skill`;
- `vendor/**` skill definitions, classified as unverified vendor inputs;
- optional JSON exports of session plugin skills and tool actions.

The recursive scan excludes common generated/cache directories. It reads skill bodies only to derive a SHA-256 and extract frontmatter metadata; it stores no complete instruction body, tool schema, prompt, credential or completion.

At the current master baseline `57559c9100f9df2868398603410e6ba28783a942`, the recursive tree contained 45 `SKILL.md` paths, one root `SKILLS.md`, zero tracked `.skill` archives and zero workspace-nested skill paths. The scanner broadens future discovery to all nested forms; its result is generated from the checked-out tree, not a manually maintained count.

## Classification model

Each capability receives:

1. **Primary domain** — engineering, testing, delivery, research, data, agentic, design, operations or specialized.
2. **Primary function** — the task-level capability within that domain.
3. **Facets** — cross-cutting properties such as vendor, plugin, MCP, CLI, workflow, credentialed, read-only, write-capable, sensitive or experimental.
4. **Trust state** — repository-canonical, official-vendor, verified-upstream, community-reference, session-observed, unverified or quarantined.
5. **Lifecycle state** — discovered → classified → deduplicated → evaluated → eligible → approved → adopted, with deprecated/rejected terminal branches.
6. **Provenance** — exact source locator, retrieval/capture time, immutable source revision where available, content hash and discovery method.

Use one primary domain/function and multiple facets. This avoids multiplying duplicate records for a skill that spans several areas. Store aliases and cross-domain relationships as edges.

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

The SQLite database uses FTS5 when available and a LIKE fallback otherwise. Skill/archive reads are capped at 2 MB per definition to bound resource use. The database and JSONL discovery-event ledger are local generated artifacts under `.cache/`; commit source code, schemas and taxonomy, not the mutable database or per-session exports. CI may upload a dated, sanitized snapshot artifact when required.

## Sources and vendor caution

The source registry declares local, vendor, external-catalog and session-snapshot sources. It records the ingestion mode and auth constraints.

- **skills.sh** exposes paginated leaderboard, fuzzy/semantic search, curated vendor skills, detail/file-tree and partner security-audit endpoints. Search accepts `q` (minimum two characters) and `limit` (1–200); multiword queries use semantic search. The API uses Vercel OIDC bearer authentication, with a documented 600 requests/minute per team/project limit. Detail records include a stable ID and content hash; use that hash for cache invalidation. Audit returns partner results from Gen Agent Trust Hub, Socket, Snyk, Runlayer and ZeroLeaks; a 404 means no audit is available yet. The documented CLI install form is `npx skills add <owner/repo>`; its anonymous telemetry includes skill name, skill files and timestamp by default, with `DISABLE_TELEMETRY=1` as opt-out. Search/audit before install; popularity is not a security review. ([API](https://www.skills.sh/docs/api), [CLI](https://www.skills.sh/docs/cli))
- **Approxination** complements skills.sh with ranked skill search, generation and execution feedback. Its A/B/C/D tool-layer cohort is already governed by `approxination-lane`; hosted calls require the provisioned token and explicit budget. Reuse its lane rather than building a second ranking service.
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
python3 scripts/capabilities/discover.py scan --root .

# Import session-scoped, metadata-only JSON exports when explicitly supplied
python3 scripts/capabilities/discover.py scan --root . \
  --plugin-skills-json /path/to/plugin-skills.json \
  --tool-actions-json /path/to/tool-actions.json

# Return a compact local shortlist
python3 scripts/capabilities/discover.py find "task intent" --limit 8

# Optional read-only skills.sh catalog search (requires a short-lived Vercel OIDC token)
python3 scripts/capabilities/discover.py find "database agent skills" --skills-sh --limit 8

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
