# CEEL — Concept Adaptation and Competition

**Status:** active research protocol · 2026-11-25  
**Work item:** CCEL-006  
**Authority:** CEEL capability graph + canonical DoE/ATES experiment records

## Objective

Extract reusable concepts from external agent systems, map each concept to one repository capability, then compare the adapted pattern against the native baseline under a frozen cohort. Optimize verified capability gain per unit of runtime cost, latency, failure risk, and maintenance effort.

CEEL records source provenance and capability evidence. The designated licensing duty owner handles licensing determinations; CEEL consumes the owner's disposition/reference as a separate handoff. Security, privacy, runtime qualification, and production admission retain their existing owners and gates.

## Foundry platform boundary

Treat Microsoft Foundry as a managed Azure platform and control plane. Evaluate separately published components as independent source projects: Microsoft Agent Framework, Foundry Local, Agent Governance Toolkit / ACS, and Microsoft Foundry Skills. Keep the managed platform reference separate from the open-source component candidates.

Platform source: https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry

## Candidate disposition

| Candidate | Pattern to extract | Primary refTemplates slot | First experiment | Current state |
|---|---|---|---|---|
| ASSERT | Natural-language behavior specs → test cases; trace-grounded evaluation; portable JSONL evidence | `11_Evaluation_Quality/assert` | Run against the same ATES task cohort as native tests; compare defect detection, evaluator agreement, trace coverage, runtime and review effort | DISCOVERED · source reviewed · local fit unmeasured |
| Agent Governance Toolkit / ACS | Portable policy contract; checkpoints across input/model/state/tool/output; audit evidence | `05_Safety_Observability/agent-governance-toolkit` | Encode one existing policy in native controls and ACS-shaped YAML; compare enforcement parity, bypass resistance and audit completeness | DISCOVERED · source reviewed · local fit unmeasured |
| Microsoft Agent Framework | Typed agent workflow composition, orchestration and middleware patterns | `01_Agent_Runtime/microsoft-agent-framework` | Architecture tournament against current manager/runtime on frozen tasks; preserve current runtime as control | DISCOVERED · source reviewed · runtime unmeasured |
| Foundry Local | Local inference runtime and hardware-aware model execution | `01_Agent_Runtime/foundry-local` | Runtime compatibility matrix: Linux ARM64, Android/Bionic, Termux, model availability, cold-start, memory and task quality | DISCOVERED · Android/Termux compatibility is a hypothesis |
| Microsoft Foundry Skills | Task-specific agent instructions for deployment, evaluation and troubleshooting | `07_Prompt_Context/microsoft-foundry-skills` | Selective skill-pattern extraction; blind-graded task completion and token/context cost against native instructions | DISCOVERED · selective utility unmeasured |
| Foundry E2E Agent Observability Workshop | Trace → evaluation → optimization → red-team feedback loop | `05_Safety_Observability/foundry-e2e-agent-observability-workshop` | Reconstruct the pipeline using native OTel/evidence contracts; compare coverage and operator effort | REFERENCE PATTERN |
| Frontier Week Hack | Build → monitor → evaluate → deploy lifecycle and reusable lab structure | `12_External_Agents/frontier-week-hack` | Harvest individual workflow patterns; compare cycle time and evidence quality | REFERENCE PATTERN |
| Agentic Factory Hack | Multi-agent orchestration and specialist-agent handoffs | `12_External_Agents/agentic-factory-hack` | Compare single-agent, current multi-agent and adapted orchestration on identical tasks | REFERENCE PATTERN |

Source URLs and observation dates live in `docs/integrations/capability-opportunity-graph.json` and each slot's `SOURCE.txt`. Pin the exact source commit/tag before a reproducible experiment. A reproducible revision requires an immutable commit or tag; a branch URL establishes discovery provenance.

## RefTemplates pipeline

```text
GitHub source / release / documentation event
  → refTemplates category inventory
  → provenance + metadata completeness
  → capability-pattern extraction
  → candidate score (metadata readiness only)
  → CEEL capability graph
  → frozen cohort + DoE admission
  → ATES execution + canonical experiment record
  → 3L0 / Moneyball comparison
  → independent review + dual gates
  → promote / hold / reject / supersede
```

Research-template layout scoring remains a separate profile. Capability candidates receive category-aware metadata-readiness scoring. Neither score estimates task efficacy.

## Competition design

### Phase 1 — evaluation × governance

Use a 2×2 design on one frozen cohort:

| Cell | Evaluator treatment | Governance treatment |
|---|---|---|
| A | Native evaluation | Native controls |
| B | ASSERT-derived evaluation pattern | Native controls |
| C | Native evaluation | ACS-derived policy pattern |
| D | ASSERT-derived evaluation pattern | ACS-derived policy pattern |

This design estimates each treatment's main effect and their interaction. Replicate by task and run; randomize assignment within task blocks. Preserve the baseline SHA, candidate SHA, prompt/tool hashes, evaluator version, policy version, runtime fingerprint and task acceptance contract.

### Phase 2 — runtime tournament

Compare current runtime (control) against the adapted Agent Framework architecture on the same tasks. Run Foundry Local as a separate inference-backend factor only after the target device/runtime matrix is available. Keep orchestration and inference-backend effects separable.

### Phase 3 — prompt/context and lifecycle patterns

Compare native instructions against selected Foundry Skill patterns. Compare lifecycle workflow patterns from Frontier Week Hack and the observability workshop against the existing GitHub Actions/OTel/ATES path.

### Outcomes

Primary: verified task acceptance rate under the predeclared contract.

Secondary: regression rate, evaluator agreement, trace completeness, policy violation rate, false-positive/false-negative rate, latency, token/credit cost, cold-start, peak memory, retries, operator interventions, reproducibility, portability, and maintenance effort.

Report uncertainty and missingness. Keep incomparable dimensions separate. Use Pareto analysis across quality, reliability, latency, cost, portability and maintenance. Treat unmeasured outcomes as unknown.

## First runnable adapter

The repository-owned pilot at `experiments/doe/assert_acs_2x2/` executes a deterministic three-case mock-tool cohort through native and ACS-mediated targets. ASSERT scores both runs; a native scorer evaluates the same traces; `scripts/doe/assert_acs_bridge.py` assembles all four evaluator × governance cells into canonical DoE records. The ACS dispatcher emits task-attributed, content-redacted allow/transform/deny receipts. The pilot is adapter conformance evidence, not production-agent efficacy.

Run the pure regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_assert_acs_bridge.py' -v
python3 -m unittest discover -s experiments/doe/assert_acs_2x2/acs -p 'test_policy.py' -v
```

The full provider-backed sequence and artifact commands live in `experiments/doe/assert_acs_2x2/README.md`.

## Admission rules

1. Keep candidates observational until a source revision and testable capability contract are recorded.
2. Adapt concepts through repository-owned interfaces and schemas; keep upstream code outside the implementation path.
3. Preserve the current implementation as the control arm.
4. Use identical task cohorts, runtime constraints and acceptance criteria across arms.
5. Record each dispatched run in the existing `docs/ops/corpus/EXPERIMENT.schema.json` contract.
6. Route licensing disposition to the designated licensing duty owner as a separate responsibility.
7. Promote only after independent review and same-SHA repository gates pass.

## Initial leverage order

1. **ASSERT pattern** — highest immediate leverage: strengthens the evidence loop without replacing the runtime.
2. **ACS pattern** — pairs with ASSERT to measure whether policy controls improve outcomes and auditability.
3. **Agent Framework architecture** — competing runtime pattern, evaluated against the current control.
4. **Foundry Local** — platform-specific inference experiment after Termux/Android compatibility is measured.
5. **Foundry Skills** — selective instruction extraction and blind evaluation.
6. **Three seed repositories** — architecture and workflow references; harvest component patterns rather than importing whole projects.

## Validation state

- Source discovery: COMPLETE for the eight listed candidates.
- ASSERT × ACS adapter: IMPLEMENTED; deterministic mock-tool conformance pilot and four-cell evidence bridge are runnable.
- Capability graph registration: COMPLETE; candidates remain `discovered`.
- RefTemplates metadata slots: IN PROGRESS.
- Category-aware inventory/scoring: IN PROGRESS.
- Executed competition runs: PENDING.
- Runtime compatibility: PENDING.
- Promotion: HOLD until evidence and required gates exist.
