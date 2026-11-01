# Orbital Syntax + Foresight: implementation plan

**Status:** actionable research/engineering plan; proposal remains posted pending human review  
**Proposal:** `orbital-syntax-topology-lab`  
**Branch:** `feat/orbital-syntax-topology-lab`  
**Decision principle:** select the best-fit applications and reusable components; do not assume the DefTech reference itself is the product target.

## Executive decision

Build a **reusable, evidence-backed technology landscape explorer** that can present the same canonical records through purpose-specific views. Orbital Syntax is one candidate view, not the whole product. The initial product should help researchers discover, compare, trace, and prioritize technology signals—not merely render an attractive radar.

Do not create a new ForeSight lane, duplicate the evidence spine, or make a visual prototype the source of truth. The existing ForeSight lane is a pointer to related work, not the implementation destination.

## What the reference research supports

- Envisioning describes its radar as an interactive map of emerging technologies, with position reflecting technology maturity and technology descriptions available during exploration. Its documentation says partner radars may use different assessment methods while sharing a navigation structure.
- Envisioning's public methodology emphasizes framing a question, scanning widely, validating signals, sensemaking, scenario analysis, synthesis/storytelling, and strategic application.
- Envisioning's DEFTECH case-study material describes a five-year collaboration with armasuisse and multiple open-source radar installations. A related DEFTECH 2016 page describes 76 emerging technologies assessed for readiness and impact, then synthesized into six scenarios. Treat that as contextual evidence about the broader program, not as a verified description of every detail of the supplied 2015 URL.
- Technology-radar tooling is not the same as a complete foresight workflow. For example, TeraGo generates HTML radars from YAML and tracks changes between periods; Thoughtworks' Build Your Own Radar accepts structured data and renders an interactive radar. These are useful narrow components/patterns to evaluate, not assumed end-to-end solutions.
- Envisioning Signals describes a broader workflow combining scan questions, scored signals, supporting/contradicting sources, multiple visualizations, and shared workspaces. Treat it as a product-pattern reference; do not assume it is open-source or a runtime dependency.

## Best-fit application shortlist

| Application | Best use | Fit | Decision |
|---|---|---:|---|
| Existing ForeSight Radar + Evidence Spine | Canonical records, provenance, confidence, horizons, unresolved questions | Essential | Extend; do not duplicate |
| Custom multi-view explorer | One record model with radar, table, list, tree, graph and optional radial views | Very high | Primary product direction |
| TeraGo | YAML-driven static radar generation and historical change comparison | High for export/benchmark | Evaluate as a bounded FOSS component; verify license, maintenance, and schema fit before adoption |
| Thoughtworks Build Your Own Radar | Quick benchmark for quadrant/ring interaction and structured-data import | High for UX reference | Use for comparative evaluation; not canonical storage |
| Envisioning Signals | End-to-end scanning/sensemaking workflow and source contestation patterns | High as product reference | Study workflow and interaction; don't assume dependency or FOSS availability |
| Orbital Syntax prototype | Nested hierarchical landscape and local-neighborhood navigation | Promising but unproven | Continue as an experimental view behind comparison tests |
| Full commercial foresight suite | Team-wide scanning, scenarios, roadmaps and collaboration | Context-dependent | Do not procure before requirements and gap analysis |

## Product architecture

1. **Canonical record layer:** reuse the existing ForeSight evidence spine and radar schema. A record should retain stable ID, title, source URLs, observed/published dates where known, evidence status, confidence, horizon, dimensions/tags, supporting and contradicting evidence, dependencies, unresolved questions, and revision lineage where supported by the existing schema. Extend schemas only through the repository's established proposal/review process.
2. **Ingestion and curation:** normalize incoming research into candidate records; preserve source context and provenance; deduplicate cautiously; never turn repetition into corroboration; retain contradictory evidence; require human review for high-impact assessments.
3. **Assessment layer:** keep separate dimensions separate. Horizon/maturity is not confidence; confidence is not impact; impact is not strategic priority. Store assessment rationale and assessor/time where the existing contract permits it.
4. **Projection adapters:** define a renderer-neutral view model, then adapters for:
   - radar: maturity/horizon × impact/strategic relevance (only when these fields have documented semantics);
   - table/list: precise scanning, sorting, accessibility, and dense labels;
   - tree: nested categories and enabling technologies;
   - graph: dependencies, convergence, and relationships;
   - orbital: optional multiscale hierarchy and selected-item neighborhood.
5. **Detail/provenance inspector:** every mark opens a readable record with evidence, dates, status, uncertainty, dependencies, and links. The view must never conceal missing/unknown data or imply false precision.
6. **Exports and reproducibility:** export stable structured data and static HTML/SVG snapshots where useful; record source revision and generation metadata. Avoid a runtime network dependency for the core viewer.
7. **Evaluation:** compare tasks and outcomes, not aesthetic preference alone. Keep the current SHE integration boundary read-only until the proposal is accepted and validation gates pass.

## Delivery phases and exit criteria

### Phase 0 — Requirements and tool decision
- Inspect the actual 2015 radar and any available underlying report/data; distinguish directly observed UI/content from inference.
- Inspect TeraGo and Thoughtworks tool capabilities, license, data model, maintenance and export path.
- Write a concise capability matrix and select build-vs-adapt decisions.
- Exit: documented requirements, source citations, and explicit no-go decisions for unsuitable dependencies.

### Phase 1 — Canonical model and renderer contract
- Map current radar schema/evidence spine fields to a view-model without creating a parallel source of truth.
- Specify stable identity, unknown/missing values, contradictory evidence, filters, sorting, provenance, and revision handling.
- Exit: schema/adapter contract tests and sample fixtures derived from synthetic or properly licensed data.

### Phase 2 — Multi-view baseline
- Implement the same fixture in radar, table/list and tree views first.
- Add keyboard navigation, screen-reader-readable alternatives, mobile layout, search and filters.
- Exit: cross-view record identity is preserved; keyboard and semantic access work; no network calls required for local fixtures.

### Phase 3 — Orbital Syntax and graph comparison
- Add orbital view to the same fixture and canonical view-model.
- Add expansion/collapse, filtering, selected-neighborhood context and density-aware fallback to list/tree.
- Preserve verified/candidate/inferred/unknown/unavailable distinctions.
- Exit: automated geometry/interaction tests pass and participants can complete benchmark tasks in all views.

### Phase 4 — Evaluation and integration decision
- Compare radar, orbital, tree and list on technology lookup, evidence comparison, dependency discovery, uncertainty recognition and horizon-based prioritization.
- Measure completion time, correctness, omissions, confidence calibration, accessibility completion, device class and prior familiarity.
- Include dense labels, incomplete records, contradictory sources, long identifiers and small screens.
- Exit: documented results and a human decision on whether any view merits SHE integration. No view is declared superior without results.

## Initial acceptance tests

- Identical records and filters produce equivalent result sets across views.
- Every displayed claim can be traced to source/evidence metadata or is explicitly marked illustrative.
- Horizon, confidence, impact and priority are never silently conflated.
- Unknown is not converted to zero; missing evidence is not treated as negative evidence.
- Contradictions remain inspectable.
- Geometry is deterministic for stable input; no node is unreachable via keyboard or semantic list.
- Long labels and high-density groups have a non-radial fallback.
- No writes to GitHub/SHE/source systems from the viewer.
- Local demo mode works offline; no external scripts, tracking, or upload.
- Tests, repository gate and Termux smoke are reported with exact commit and outcomes before any merge; do not claim they ran until they actually do.

## Immediate next actions

1. Inspect the 2015 target and supporting DEFTECH/Envisioning materials; capture the actual navigation model and fields rather than merely bookmarking the URL.
2. Evaluate TeraGo and Thoughtworks radar as candidate reusable implementations, then compare their extension cost against a small custom renderer.
3. Inspect the existing radar schema and evidence-spine contracts before proposing field changes.
4. Create one synthetic technology landscape fixture and render it in radar/list/tree/orbital modes.
5. Add automated contract and accessibility tests; keep the prototype isolated and the PR open pending human review.

## Non-goals

- Replacing ForeSight, the evidence spine, SHE, or the context-relationship graph.
- Assuming the orbital view improves reading speed or comprehension.
- Rebuilding a commercial scanning platform before checking existing FOSS tools.
- Automatically importing old radar claims as current facts.
- Merging or integrating without human review and required gates.
