# Source Record — qdesk-replica-reconciliation

## 1. Scope and authority

Target repository: `timerloggedout-spec/termux-monorepo`.

Reference project: `timerloggedout-spec/replica_fork`, a fork of `github/replica`.

The intended deliverable is an optional visual extension to the existing QDesk/QUE operating architecture, branded `Q^∆3sk`. It combines selected Contribution Desk and Admin Graph projections with a Browser Quarantine Clerk proposal/access-risk view and stronger release/preview evidence. The initial deliverable is a design and read-only shell. Existing QDesk admission, ranking, claim, deadline, portfolio and DoE machinery remains authoritative.

Existing QDesk lineage already in flight:

- PR #5145: QDesk Observatory + Delphi + DoE self-implementation pipeline; its RFP packet and acceptance matrix own that pipeline design.
- PR #5197: QDesk portfolio decision and delivery report contract/schema.
- PR #5199: deadline closure, alarms, page freshness and QDesk Gantt.
- PR #5330 and #5376: safe admission drain and explicit project-task/provider-dispatch boundary.
- PR #5622: QUE ranking and claim pipeline, including DoE authority for its comparison method.

These are related active work, not assumed merged or runtime-complete. The present proposal is a visual/integration extension only. QDesk UI must link to these existing authorities and preserve their status distinctions.

Authority map:

| Concern | Existing canonical owner | QDesk role |
|---|---|---|
| Proposal intent/status | `docs/proposals/registry.yaml`, proposal MANIFEST/ITEMS/PROCESS | Read-only proposal index and navigation |
| Dependency lifecycle | `docs/agentic/dependency-phases.json`, approvals, deterministic phase engine | Show phase state and evidence |
| Contribution/build traversal | `ops/challenge/desk-feed.json`, desk feed contract | Reuse existing desk projection |
| Admin relationships | `apps/tribute-dashboard/admin-graph.html` plus its source feeds | Reuse selected graph excerpts |
| Page/build identity | `apps/tribute-dashboard/version-manifest.json`, `versioning.js` | Extend current comparison |
| DoE campaigns | `docs/ops/DOE-FAMILY.md`, `DOE-TAXONOMY.md`, `EXPERIMENT.schema.json`, QDesk RFP #5145 and existing campaign records | Display campaign references and results; do not create another DoE pipeline |
| Integrations/capabilities | `docs/integrations/registry.json`, adapter/event contracts, capability opportunity graph | Show source-linked integration status |
| Collaborator identity/provenance | `docs/ops/AGENT-MONIKERS.md`, `BIUDL-EXECUTION-AND-PROVENANCE.md`, session SSOT and capability contracts | Display attributed, confidence-labelled evidence |
| Visual review | Native ICM `docs/icm/_tv/` artifacts and optional-visual-review card | Optional visual projection; source files remain canonical |

QDesk must not introduce another scheduler, phase engine, proposal registry, agent identity registry, experiment ledger, telemetry store, credential store or merge authority.

## 2. Replica native behavior to preserve

The fork README describes an open-source AI prototyping tool built around team design-system guidance, starter apps, a local Copilot canvas, optional hosted Replica Hub for publishing/feedback, and a GitHub build action for Hub publication.

The upstream workflow separates:
- Local prototyping from hosted publication.
- Starter creation from adapting an existing repository.
- Guidance drafting, review and activation.
- Source repository sharing from publishing a Hub Build.
- Preview availability from proof that the current session loaded the canvas.

Native starter catalog:
- `minimal`: small React/TanStack Router app with no component library.
- `coreai`: React Router app with CoreAI components and a Foundry-style shell.

Preserve the app's own router, dependencies, conventions and design-system guidance. Inspect before adapting. Existing files, Git history and remotes remain intact. Local prototyping does not require Hub, Docker, a domain or GitHub repository access. Hosted publishing remains optional and separately authorized.

Replica's shared workflow includes local preview preflight, component mapping, rendered review, test/build checks and explicit publishing steps. Use the Replica canvas when available; a supported local browser preview is a fallback when the host lacks canvas support. Plugin installation, source migration and publishing remain separate authority edges.

License/provenance: the Replica README states MIT. Preserve upstream attribution and license notices; verify bundled asset/font notices before copying individual assets. The fork's README identifies GitHub Design and Microsoft CoreAI Design as creators.


## 2.1. Issue filing and model-provider boundaries

Replica supplies an interactive local prototyping loop through the Copilot canvas: users describe a change, inspect the running prototype, and refine it in conversation. Its documented native workflow covers prototype creation, local preview, design guidance, build checks and optional Hub publication/review. The README and local-prototyping guide describe GitHub sign-in and model access through a Copilot plan or a user's own BYOK provider. They do not define a native GitHub issue-submission service or a project-task intake API.

The existing Contribution Desk remains the issue-dispatch surface. Its New dispatch action opens GitHub issue intake, and .github/ISSUE_TEMPLATE/project-task.yml defines the canonical issue-dispatch/v1 payload: Entry, Task/spec, Scope, Done-evidence, Target repo and post-hoc Instance stamps. Filing is the trigger; the existing dispatch system selects providers across its wired endpoints and records the resolved provider/model and run identity after execution.

The proposed QDesk filing portal should provide a guided, template-backed flow over that canonical contract:
1. Collect the existing required fields and validate them against the current issue form contract.
2. Show a rendered issue preview, target repository, dispatch effect and data-sharing notice.
3. Let the user revise the draft and explicitly confirm submission.
4. Submit through GitHub's native issue form or a separately authorized GitHub App/API adapter with repository-scoped issue-write permission.
5. Return the created issue URL and stable intake receipt; preserve idempotency across retries.

For public use, authenticate the submitting GitHub principal and bind the submission to that principal's authorized repository installation. Keep credentials server-side, use least-privilege installation permissions, and record the actor, repository, template version, submitted payload digest and issue URL. The static Replica/QDesk client remains credential-free. The native issue form remains the fallback and canonical filing route until an authenticated portal adapter passes its own review.

Keep model access as a separate choice from issue filing. Replica's documented model path is the Copilot app using either the user's Copilot plan or a user-connected BYOK provider; the selected provider's costs and terms apply. The monorepo also has its own workflow/provider routing, including scripts/model_router.py, .github/actions/model-router, .github/connectors/llm-peers.yaml and quota gates. Those workflow routes and Replica's interactive Copilot session are separate execution planes.

The eventual user-facing model selector should expose only catalogued, capability-eligible choices and record a preference rather than fabricate availability:
- **Automatic (system routing):** use the existing task/role router and its eligible provider/model selection.
- **Organization provider pool:** use organization-managed credentials and organization quota under the repository's existing authorization policy.
- **My provider (BYOK):** use the authenticated user's own provider connection and quota, with provider costs and terms shown before use.
- **Specific provider/model:** show only live, eligible choices for the selected task capability; retain an explicit fallback policy and record the actual resolved provider/model after execution.

Quota ownership follows the credential owner. User-owned BYOK usage is attributed to that user's provider account; organization-owned credentials consume the organization's quota. Keep per-principal credential boundaries, usage attribution, rate-limit state and billing records isolated so an individual user's quota exhaustion leaves the shared organization pool's health unchanged. Keep all API keys outside browser storage, public feeds, issue bodies and prototype source. The user selection contract, credential custody and billing attribution require a dedicated provider-routing review before runtime wiring.

## 3. refTemplates/smods reconciliation

The monorepo's root `CLAUDE.md`, `docs/ops/REFTEMPLATES-CONSOLIDATION.md` and `docs/icm/objects/knowledge/reference-inputs.md` define `refTemplates/smods/` as a narrow, shallow, metadata-first reference lane. References inform the monorepo; they do not operate it or override its governance. Full recursive materialization is explicit and selective.

Relevant references and their bounded QDesk roles:

| Reference | Adoptable pattern | Boundary |
|---|---|---|
| `icm-architect_fork` | Six workspace forms, form selection, restructure audit, file-role classification, walk test | Method/template input; monorepo ICM remains operative |
| `interpretable-context-methodology_fork` | Stage folders, local CONTEXT contracts, small routing catalogs | Use existing ICM paths; avoid duplicate workspace roots |
| `content-agent-routing-promptbase_fork` | Layer 0–3 selective routing, canonical source ownership, one-way dependencies | Adopt routing discipline, not the content business payload |
| `cost-of-remembering_fork` | Filesystem-backed context and cost measurement | Reference evidence only; benchmark claims remain scoped to their study |
| `icm-cctv_fork` | File-backed visual cards, mirror links, separate response artifacts | Optional projection; native files remain authoritative; no renderer/deployment dependency by default |
| `AuditEngine_fork` | Assessment and ethics review patterns | Research input; no live psychometric classification or provider-key custody |
| `GPTmetrics_fork` | Multi-model assessment and response comparison | Research input; no automatic collaborator trust score |
| `lego_fork` | Compose complete sets from available capability pieces | Selection/compatibility model; no partial set promoted as complete |

Other pinned `smods` repositories remain candidates until a task maps them to a QDesk capability contract. At implementation time, read exact gitlink object SHAs from the repository tree and record source URL, commit, license, last verification, role and runtime/reference status. `.gitmodules` alone establishes URLs and tracking configuration, not the checked-out commit identity. Keep pins unchanged in this proposal.

## 4. Existing UI and versioning facts

Verified current repository paths:
- `apps/tribute-dashboard/desk.html` exists.
- `apps/tribute-dashboard/admin-graph.html` exists (lowercase filename).
- `apps/tribute-dashboard/versioning.html` exists.
- `apps/tribute-dashboard/versioning.js` exists.
- `apps/tribute-dashboard/version-manifest.json` exists.
- `ops/challenge/desk-feed.json` exists.
- `apps/tribute-dashboard/data/desk-feed.json` exists.

The Contribution Desk page declares itself a read-only projection of `desk-feed/v1.3` plus `dispatch-state-feed/v1`; dispatch opens a GitHub intake issue. The page says it mutates nothing and does not present internal metrics as win odds. Its pipeline is spec → desk → builder → PR → CI → merge → sync. Preserve these boundaries.

The Admin Graph page is a repository-owned source surface. Its comments describe prepared-not-sent dispatch payloads and visual-only graph pulse. Reuse excerpts/links; do not duplicate its model or imply that visual animation executes work.

The current versioning code:
- Uses stable page IDs.
- Loads a local build manifest and a production manifest.
- Displays version/channel/source SHA.
- Compares page content hashes.
- Shows links to preview and production pages.
- Links source SHAs through GitHub compare when both are present.
- Labels missing hashes as `HASH UNAVAILABLE` and missing source SHAs as unavailable.

The current tracked `version-manifest.json` is `dev+unbuilt`, channel `development`, has empty `source_sha`, `built_at: null`, and null per-page `content_sha256` values. Therefore the comparison surface exists, but this checked-in development manifest does not establish a completed build or comparable preview hashes.

The current comparison is hash/source comparison, not a full screenshot/visual regression, route/interaction, accessibility, API/schema or security comparison. The surface map also records pages such as `admin-graph.html` as feed-timestamp/stale-chip only, with no dedicated per-surface release line. Extend the existing manifest/versioning path and release map; do not create a competing release registry.

## 5. QDesk visual-extension architecture

Brand: `Q^∆3sk`. Proposed page: `apps/tribute-dashboard/Q^∆3sk.html` (subject to URL/path compatibility checks). Stable machine ID: `qdesk`.

QDesk remains the existing operating architecture. The proposed `Q^∆3sk` page is a read-only shell/overview with deep links or embedded read-only regions:
1. Overview and attention queue.
2. Existing Contribution Desk / traversal state.
3. Proposal catalog and public available proposals.
4. Browser Quarantine Clerk.
5. Admin Graph excerpts and provenance drawer.
6. Release Observatory / preview comparison.
7. DoE and automation competition index.
8. Source, freshness and validation evidence.

The new page is a navigation/projection surface alongside the existing `desk.html`, `qdesk-gantt.html` (PR #5199), `doe.html`, `proposals.html`, `versioning.html` and QDesk portfolio/Observatory work. It does not replace the existing Contribution Desk or the proposed QDesk Gantt.

Start with existing feeds and links. Add a new QDesk index/read-model schema only if the existing feed contracts cannot support the required navigation. Any new read model references canonical object IDs, source paths, source SHAs and generated timestamps; it does not duplicate domain payloads or own lifecycle transitions.

The UI must distinguish observed, derived, inferred and unavailable data. Partial/stale/unverified states remain explicit. It must work as a credential-free static projection and degrade gracefully when optional Replica Hub/canvas is absent.

## 6. Browser Quarantine Clerk threat model

Treat every collaborator as a potential threat actor regardless of permission level or access duration. This is a threat-model assumption, not an accusation about an individual. Read-only, low-privilege and temporary access still carry exposure.

Keep separate:
- Principal identity and attribution confidence.
- Granted capability and resource scope.
- Access duration, expiry and review cadence.
- Risk assessment and residual risk.
- Quarantine state and disposition.

Proposed access record fields (design only):
`grant_id`, `principal_ref`, `resource_scope`, `capabilities[]`, `granted_by`, `approved_by`, `granted_at`, `expires_at`, `review_due_at`, `status`, `policy_version`, `evidence_refs[]`.

Proposed risk record fields:
`risk_id`, `subject_ref`, `threat_model_version`, `attack_surface`, `likelihood`, `impact`, `exposure`, `confidence`, `controls[]`, `residual_risk`, `assessed_at`, `evidence_refs[]`.

Proposed quarantine case fields:
`case_id`, `subject_ref`, `trigger_ref`, `restriction_scope`, `opened_at`, `review_due_at`, `disposition`, `actor_ref`, `evidence_refs[]`.

Public proposal cards expose only approved/sanitized fields: title, purpose, requested capability, proposed access tier, declared duration, risk band, review state and evidence links cleared for public access. Private identities, credentials, browser profiles, session contents and restricted evidence stay out of public feeds.

The Clerk initially observes and recommends. Permission grant/revocation, account changes, browser isolation and quarantine enforcement require their existing authoritative mechanisms and explicit policy/approval. The UI itself does not grant permissions. Use least privilege, short-lived grants, expiry, periodic review, revocation evidence and append-only transition records. Never infer trust from GitHub actor identity alone.

Proposed review bands (assessment states, not direct permission mutations):
- Q0 — routine observation.
- Q1 — additional identity/evidence verification.
- Q2 — capability/scope reduction recommended.
- Q3 — isolated execution recommended.
- Q4 — suspend access through the owning authority and open incident review.

Every band records trigger, confidence, scope, reviewer, next review time and disposition. A risk band is not a trust score, and no single scalar automatically grants or revokes access.

## 7. Release and preview comparison refinement

Reuse `version-manifest.json`, `versioning.js`, `versioning.html`, current deploy workflows and the existing visual-architecture versioning work (PR #4085).

A candidate release should bind:
- stable surface/page ID;
- schema version;
- source ref and full commit SHA;
- build ID/channel/time;
- artifact URI and SHA-256;
- page content SHA-256;
- dependency/template pins;
- test/check evidence;
- preview URL and capture metadata;
- comparison result against a named production baseline.

Comparison layers:
1. Source/manifest/hash diff.
2. Screenshot/visual diff at fixed viewport and state.
3. Route and interaction regression.
4. Accessibility regression.
5. API/schema compatibility.
6. Security/permission delta.
7. Build/test/runtime evidence.

Missing production or preview evidence is `UNAVAILABLE`, not `SAME`. A successful build is not a release. A preview is not production. A tag is not promotion evidence by itself.

Keep schema SemVer, template pin identity and release/build identity separate. A template update creates a new immutable template revision; an experiment treatment change creates a new cohort/version; a release candidate references the exact template and schema versions it used. Preserve superseded manifests and release receipts.

Suggested lifecycle:
`DRAFT → VERSIONED → PREVIEW_BUILT → PREVIEW_COMPARED → VALIDATED → REVIEWED → RELEASE_CANDIDATE → PROMOTED → MONITORED`.
Failure, rejection, supersession and rollback are separate recorded outcomes.

## 8. DoE and automation competition fit

Use the existing DoE family and taxonomy:
- DoE is the umbrella design discipline.
- MVT is a member nested under DoE.
- ATES is the execution harness/measurement layer nested within the family.
- One dispatched/executed run produces one immutable record conforming to `docs/ops/corpus/EXPERIMENT.schema.json`.
- Full factorial and Taguchi L9 generators are implemented; other design classes retain their documented status.
- Quality/correctness precedes time and throughput; ATES is observational and never a merge gate.

The existing QDesk DoE/RFP work (#5145, #5197) and the DoE family own campaign design, decision quality and portfolio comparison. This proposal contributes a candidate visual-integration experiment only after those owners reconcile it. Do not start a competing QDesk campaign ledger.

Do not compare unlike automation categories as if they were direct competitors. Classify candidates by capability contract and existing monorepo taxonomy:
- intake/proposal lifecycle;
- orchestration/dispatch;
- build/fix execution;
- review/quality/security;
- CI/workflow reliability;
- runtime watching/reconciliation;
- telemetry/evidence;
- context/memory/routing;
- templates/composition;
- visual/dashboard projection;
- release/deployment;
- integration/adapters;
- DoE/evaluation.

Use the existing DEVOPS-REGISTER categories, DOE-FAMILY, DOE-TAXONOMY, Integration Intelligence registry and SURFACES-MAP as source taxonomies. Keep one primary placement with cross-membership facets; do not create a new parallel taxonomy. The proposed `Q^∆3sk` page is a visualization/control surface, not a replacement automation engine. In the existing surface taxonomy it belongs primarily to Web & Presentation, with cross-links to Coordination & QUE, Challenges & Entries, and Scoring & Method; keep one primary placement plus explicit facets.

Candidate capability strata for competition (these are proposed comparison groups, not a new official taxonomy):

| Existing capability family | Existing monorepo candidates/surfaces | Valid competition unit |
|---|---|---|
| Intake / portfolio / deadlines | Proposal registry, QDesk portfolio report (#5197), deadline desk (#5199) | Same proposal cohort and requirement-closure task |
| Admission / ranking / claim | QUE admission drain (#5330), project-task boundary (#5376), ranking/claim pipeline (#5622) | Same issue cohort, admission policy and claim contract |
| Dispatch / orchestration | Provider dispatch, dispatch executor, manager policies | Same task class, configured-instance stamps and execution permissions |
| Build / review / quality | Jules, Gemini, DeepSeek, CodeRabbit/Qodo/Devin review lanes | Same PR/task fixture; separate build and review outcomes |
| CI / workflow reliability | Repo gate, Termux smoke, workflow health and Action Effectiveness Ledger | Same change set and gate contract |
| Runtime observation / evidence | Actions watchers, PR evidence, telemetry and feed collectors | Same event cohort; coverage, freshness, false alarms and provenance |
| Context / memory / routing | ICM, selective context routing, cost-of-remembering reference | Same retrieval/task cohort; correctness first, then tokens and latency |
| Visual projection / navigation | Contribution Desk, Admin Graph, ICM CCTV cards | Same operator tasks; findability, error rate and evidence traceability |
| Release / publication | version-manifest, versioning.js, preview/production deploy surfaces | Same candidate SHA and production baseline |
| Access / quarantine | Existing permission/provenance contracts; proposed Clerk | Synthetic adversarial access scenarios until a separately approved enforcement adapter exists |
| DoE / evaluation | doe.py, MVT, ATES and existing DoE family campaigns | Design and measurement methodology; these are the experiment plane, not contestants |

Official category placement remains with the current registers: the DevOps register's L family is DoE evaluation and M is Tribute operations; the visual page's primary surface group is Web & Presentation. QDesk can expose these categories together without flattening their authority or comparing unlike systems.

Proposed bounded factorial design (design-only; no runs claimed; submit as a child/sibling campaign through the existing QDesk DoE owner path):
- Factor A — context routing: existing routing vs ICM selective routing.
- Factor B — visual review: existing page-only review vs file-backed CCTV card projection.
- Factor C — release comparison: current manifest/hash comparison vs manifest + visual + route/interaction evidence.
- Factor D — access review: existing proposal/issue review vs Clerk access/risk/expiry workflow (synthetic fixtures only until an enforcement adapter is separately authorized).

A 2^4 full-factorial design has 16 treatment combinations and matches the implemented generator. Block by task family (proposal intake, collaborator review, release review, graph navigation); randomize order within blocks; use independent tasks for task replication and identify repeated measures separately. Freeze baseline/candidate SHAs, templates, feeds, evaluator, task set and runtime. Set replication count from pilot variance and a predeclared minimum practical effect; do not invent significance from a small pilot.

Primary outcome: verified task completion against a predeclared acceptance rubric. Secondary outcomes: correctness, evidence completeness, permission-scope errors, false-positive/false-negative risk flags, regression rate, time-to-verified, human interventions, retries, context/token use and maintenance burden. Report uncertainty and missingness. Do not use a weighted black-box score or activity volume as the winner criterion. Compare Pareto tradeoffs; ATES remains diagnostic.

Each run uses the existing EXPERIMENT record with baseline/candidate SHA, suite, cohort, treatment/policy, configured-instance identity when applicable, status, outcome, metrics, provenance, confidence and evidence refs. Pre-register design in the existing DoE family before execution. A cherry-picked customization becomes a new version/cohort, never a silent amendment to a running arm.

## 9. Implementation sequence and gates

1. **Reconcile active ownership.** Inspect #5145, #5197, #5199, #5330, #5376, #5622 and the current issue/dispatch/provider contracts. Record file ownership, dependency edges, accepted overlap, supersession candidates and the exact integration point for each feature.
2. **Accept and version the proposal.** Complete operator and independent review, register dependencies, assign item owners, and freeze the accepted scope and baseline commit.
3. **Verify source and provider contracts.** Record exact refTemplates/smods gitlink SHAs and licenses; inspect Replica's pinned source revision; map the current project-task issue form, dispatch route, model router, provider catalog, credential ownership and quota attribution.
4. **Define the QDesk shell and Gantt integration.** Specify the read-only information architecture, stable surface IDs, responsive/accessibility states, deep links, Gantt milestones, dependencies, version-selection controls and source/freshness receipts.
5. **Build the guided issue-filing portal.** Mirror the canonical issue-dispatch/v1 project-task form, provide validation and a reviewable issue preview, then route confirmed submissions through the native GitHub issue form or a separately approved GitHub App/API adapter. Return the created issue and idempotent intake receipt.
6. **Define model choice and quota isolation.** Separate Replica Copilot sessions from repository workflow dispatch. Specify Automatic, Organization provider pool, My provider (BYOK) and eligible specific provider/model choices; bind each choice to its credential owner, authorization, quota, billing attribution, fallback policy and post-run instance stamp.
7. **Implement Clerk and release comparison.** Reuse canonical proposal/access records for sanitized Clerk cards. Extend the existing version-manifest/versioning path with source/build/artifact hashes, visual captures, route/interaction, accessibility, schema/API, security and runtime evidence. Record candidate selection, completion criteria, migration and retirement as explicit version transitions.
8. **Pre-register the DoE and automation comparison.** Submit the bounded 2^4 campaign through the existing DoE owner, freeze baseline/candidate versions and cohort, define blocking/randomization/replication/outcomes, and classify candidates within existing capability families.
9. **Implement the smallest accepted vertical slice.** Compose existing feeds and authorities into the read-only QDesk shell; deliver portal and provider adapters only after their separate security and permission reviews; use synthetic fixtures for Clerk risk scenarios.
10. **Validate the exact candidate.** Run focused contract/security/accessibility tests, build the Replica/local preview, compare preview against the selected baseline, inspect issue receipts, source hashes, artifacts and runtime evidence, and pass repo-gate plus termux-smoke on the exact candidate SHA.
11. **Select, promote and phase out.** Compare completed candidates against the predeclared acceptance criteria; record the selected version and rationale; migrate consumers in bounded batches; retain rollback and lineage receipts; retire superseded versions after consumer migration and post-promotion monitoring.

## 9.1. Execution guardrails

- Keep Replica local prototyping independent from optional Hub hosting and publication.
- Reuse the existing proposal, scheduler, admission, claim, dispatch, provider, quota, DoE and release authorities.
- Keep static visual surfaces credential-free and source-linked.
- Keep collaborator-private data, credentials and browser/session material within their authorized stores.
- Preserve identity attribution confidence and distinguish a GitHub actor from a verified agent principal.
- Treat preview, queued workflow, successful build and ATES observations as evidence inputs; require the declared release gates and task outcome for selection.
- Record every candidate, selection, migration, retirement and rollback with immutable version and evidence references.

## 10. Open evidence items

- Verify exact gitlink commit SHAs for the relevant `refTemplates/smods/` entries from the Git tree before any pin or source update.
- Reconcile with PR #5145, #5197, #5199, #5330, #5376 and #5622 current head/base/check state before adding overlapping files or changing QDesk feed/claim semantics.
- Inspect current `versioning.js` deploy/build workflow and production manifest to establish which production fields are actually populated.
- Inspect the complete desk/admin graph feeds and their owning collectors before composing QDesk.
- Verify the active release automation and existing visual-architecture versioning PR #4085 disposition before changing that contract.
- Confirm the preferred public brand/filename: `Q^∆3sk.html` vs a stable `qdesk.html` URL with `Q^∆3sk` visible branding.
- Identify any existing access-grant/quarantine contract before defining a new schema; the Clerk's initial read-only projection can proceed without one.
