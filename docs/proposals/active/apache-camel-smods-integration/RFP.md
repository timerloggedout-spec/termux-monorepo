# RFP: Apache Camel integration opportunity — governed MCP, event routing, and EIP adapter

- **Proposal ID:** apache-camel-smods-integration
- **Kind:** rfp
- **Priority:** P1
- **Execution:** `true` — proposal-scoped execution is authorized now
- **Target reference lane:** `refTemplates/smods/camel_fork-apache`
- **Current disposition:** metadata candidate; live gitlink and runtime activation remain gated
- **Source repository:** https://github.com/timerloggedout-spec/camel_fork-apache
- **Observed source revision:** `12014575a8f2c71174a8f9f4cbef9a61e25439e8` (2026-11-16)

## 1. Mandate

Evaluate Apache Camel as an integration substrate that can extend the existing Termux agent hub and repository automation without replacing the authorities already in place.

The proposal is to harvest and validate the useful integration patterns from the user-owned `camel_fork-apache` repository, then adapt only the minimum proven surfaces into the `refTemplates/smods` reference lane. Camel is not to become a second scheduler, proposal registry, agent router, telemetry ledger, or source of merge authority.

**Execution true means:** continue bounded, non-destructive research, architecture mapping, fixture design, and isolated compatibility experiments. It does **not** authorize production deployment, credential provisioning, enabling arbitrary route tools, importing the full source tree, or bypassing proposal review and dual gates.

## 2. Evidence baseline

Repository/API inspection on 2026-11-16 established:

- The source repository is public and owned by `timerloggedout-spec`; GitHub reports admin/push access.
- Default branch is `main`; latest observed commit is `12014575a8f2c71174a8f9f4cbef9a61e25439e8`.
- The repository reports a size of 1,561,977 KB. Treat it as a large source repository; do not assume a submodule checkout is lightweight merely because it is shallow.
- Root `pom.xml` identifies Camel `4.24.0-SNAPSHOT`, a Maven multi-module build, and JDK 21 as the minimum build version.
- `LICENSE.txt` contains the Apache License 2.0 text.
- The fork's `.gitmodules` is empty.
- The fork README describes Camel's Java/YAML/XML routes, 350+ connectors, MCP server, LangChain4j/OpenAI components, A2A support, and Kaoto/Karavan visual designers.

The inspected repository metadata does not by itself establish the fork's upstream-parent relationship, Termux/Android runtime compatibility, or the existence of any local custom patches. Those remain explicit verification items.

## 3. Integration opportunities

| Priority | Opportunity | Fit with this repository | Proposed disposition |
|---|---|---|---|
| P0 | Camel CLI MCP (`camel mcp`) | Agent-side catalog, route validation, documentation, security review, and runtime diagnostics | Evaluate as an optional developer/research MCP server; do not make it a mandatory hub dependency |
| P1 | Camel MCP Server component | Exposes selected Camel routes as MCP tools/resources over Streamable HTTP or stdio | Prototype a narrow, allowlisted adapter behind existing `hub_mcp` policy |
| P1 | Enterprise Integration Patterns + connectors | Event routing, transformation, filtering, aggregation, retries, dead-letter handling, and protocol bridging | Extract patterns and test one or two concrete connector use cases; keep GitHub Actions as scheduler/authority |
| P1 | OpenTelemetry integration | Route-level spans and runtime measurements can enrich existing execution evidence | Map trace/run identifiers into the existing evidence plane; no second canonical telemetry store |
| P2 | A2A interoperability | Potential protocol bridge between separately governed agents/services | Run a compatibility spike only after identity, trust, and authorization contracts are defined |
| P2 | Kaoto / Karavan | Visual authoring and review of integration routes | Optional authoring surface; generated route files remain reviewable source |
| P3 | LangChain4j / OpenAI components | Provider-specific AI calls inside Camel routes | Defer; avoid duplicating provider routing and model selection already owned by this repository |

### Important product distinction

There are two different MCP directions:

1. **Camel CLI MCP** gives an AI assistant knowledge and tools to author, validate, diagnose, and inspect Camel integrations.
2. **Camel MCP Server component** publishes explicitly selected routes from an application as MCP tools/resources for external clients.

They are complementary, not interchangeable. The first is the lower-risk initial experiment. The second is the more consequential runtime integration and requires strict tool admission.

## 4. Recommended architecture

```text
GitHub Actions / existing lane authorities
                 |
                 v
        existing hub_mcp policy
                 |
        explicit adapter allowlist
                 |
                 v
       Camel MCP / Camel runtime
                 |
       tagged, bounded route tools
                 |
                 v
   approved APIs / queues / services
                 |
                 v
   existing evidence + OTel/ATES plane
```

Design rules:

- GitHub Actions remains the repository automation scheduler and authority.
- `hub_mcp` remains the policy and adapter boundary; Camel does not gain ambient access to every tool or service.
- Expose only named routes with explicit tags. Untagged/default tool pools stay private.
- Prefer Streamable HTTP with authenticated service identity for remote operation. Use stdio only for a trusted, local parent process.
- Route inputs are schema-validated; outputs are bounded and sanitized.
- Side-effecting operations require idempotency keys, explicit operation identity, and durable outcome receipts.
- A client timeout must not be mistaken for cancellation: Camel documentation notes that a timed-out route may continue running server-side. Treat timeout as an unknown outcome until reconciled.
- Secrets remain in the existing credential boundary; no secret values in route files, fixtures, telemetry, or Git.
- OpenTelemetry spans are correlated into existing run evidence; do not create a competing canonical ledger.

## 5. Fit and non-duplication assessment

| Existing surface | Camel relationship | Boundary |
|---|---|---|
| `hub_mcp/` | Candidate adapter / policy-enforced execution boundary | No parallel registry or authorization policy |
| `termux-mcp-server_fork` | Existing device MCP server can remain the device-control plane | Camel is an optional integration runtime, not a replacement |
| GitHub Actions | Camel may perform bounded integration work invoked by a workflow | No new top-level cron or scheduler |
| ATES / OpenTelemetry | Camel runtime spans can enrich measured execution | Existing event schema and provenance stay canonical |
| Proposal lifecycle / Delphi | Owns approval and evidence for adoption | Camel cannot self-approve, vote, or promote |
| Termux / Android | Potential local runtime, subject to JDK and resource testing | No assumption that full Camel is mobile-safe |

## 6. Termux and build feasibility

The inspected root POM sets JDK 21 as the minimum build version. That is a material environment constraint for the Termux-first hub. Before any local runtime adoption:

1. Confirm the actual Termux device's Java version and available memory/storage using the project's resource snapshot.
2. Test a minimal Camel Main or JBang route outside the production hub.
3. Measure cold start, resident memory, disk footprint, and route throughput.
4. Compare local Termux execution with a container/remote runner.
5. Select the lightest deployment boundary that meets the use case.

Do not clone the full fork into every CI job. A metadata reference and immutable Git SHA are sufficient for research. A live shallow gitlink is a later decision, not a prerequisite for the first POC.

## 7. Scope

### In scope

- Verify fork ancestry, license/NOTICE obligations, branch/revision provenance, and local delta from Apache upstream.
- Map Camel CLI MCP and Camel MCP Server capabilities to existing `hub_mcp` adapters and permission tiers.
- Select one read-only and one side-effecting representative workflow for threat-modelled experiments.
- Define a minimal route fixture and MCP conformance tests.
- Measure Termux/remote runtime feasibility and resource cost.
- Decide whether the fork merits a shallow gitlink at `refTemplates/smods/camel_fork-apache`.

### Out of scope

- Replacing GitHub Actions, the existing hub, provider router, or proposal lifecycle.
- Importing all 350+ components or enabling arbitrary connectors.
- Full recursive submodule initialization in CI.
- Storing credentials or private operational state in the fork or reference metadata.
- Exposing unrestricted SQL, HTTP, shell, filesystem, or route-management tools to agents.
- Production deployment or changes to live services before acceptance and validation.

## 8. Execution plan and gates

1. **Source provenance:** compare fork HEAD with Apache upstream; identify custom commits, local branches, and exact revision.
2. **Capability map:** classify MCP tools, route server, EIPs, connectors, A2A, and observability against existing adapters.
3. **Security contract:** define tool allowlist, identity, authentication, timeout/unknown-outcome behavior, idempotency, output bounds, and secret handling.
4. **Offline POC:** create deterministic route fixtures and MCP contract tests; no external side effects.
5. **Runtime spike:** execute only in an isolated disposable environment; record JDK, memory, startup, and compatibility evidence.
6. **Decision:** adopt patterns, add a shallow gitlink, or retain metadata-only status. Any gitlink must use a reviewed immutable SHA and pass the refTemplates integrity checks and both repository gates.

## 9. Acceptance criteria

- Fork ancestry and custom-delta status are established from Git history, not inferred from the repository name.
- A capability matrix identifies exact Camel feature/module/version and a corresponding repository use case.
- No duplicate scheduler, router, registry, authorization system, or telemetry ledger is introduced.
- MCP exposure is explicit allowlist-only; authentication and stdio trust boundaries are documented.
- Tests prove name-collision rejection, schema validation, output sanitization, bounded calls, timeout reconciliation, and idempotent side-effect handling.
- Termux suitability is measured; unsupported local execution is routed to an isolated runner without being called a Termux success.
- Source metadata, SOURCE-MAP, and any eventual gitlink agree; no credentials or generated runtime state are committed.
- `repo_gate.py`, `termux_smoke.py`, and proposal-lifecycle validation pass on the exact PR SHA before promotion.

## 10. Risks and mitigations

- **Large dependency surface:** keep metadata-first; pin only a reviewed revision and never recursively clone by default.
- **Tool overexposure:** tag allowlist, adapter policy, least privilege, and negative tests.
- **Timeout with continuing side effects:** durable operation IDs, idempotency, and outcome reconciliation.
- **Runtime mismatch:** JDK 21 requirement and explicit Termux resource spike.
- **Architecture duplication:** reuse Actions, `hub_mcp`, ATES, and current credential controls.
- **Upstream/fork drift:** compare fork commits and track the upstream baseline before adapting patches.

## 11. Source references

- User-owned source fork: https://github.com/timerloggedout-spec/camel_fork-apache
- Apache Camel upstream project: https://github.com/apache/camel
- Camel CLI MCP documentation: https://camel.apache.org/manual/camel-jbang-mcp.html
- Camel MCP Server component: https://camel.apache.org/components/next/others/mcp-server.html
- Camel tooling overview: https://camel.apache.org/tooling/
- Apache Camel contributing guide: https://camel.apache.org/camel-core/contributing/index.html
- Existing repository integration lane: `docs/ops/RESEARCH-INTEGRATION-LANE.md`
- Existing reference policy: `docs/ops/REFTEMPLATES-CONSOLIDATION.md` and `docs/ops/REFTEMPLATES-WORKFLOW-HOOKS.md`

## 12. Submission request

Request independent review of the opportunity ranking, the no-duplicate-control-plane architecture, and the gate for a future `smods` gitlink. Execution remains true for bounded proposal work; production integration remains conditional on acceptance and evidence.
