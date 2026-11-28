---
description: "Revenue Council — multi-agent deliberation for sales, customer success, support, RevOps, and partnerships decisions"
argument-hint: "[--help|--brainstorm|--quick|--deep|--auto|--guided|--meet|--audit|--resume|--list|--status|--archive|--cleanup] [DECISION...]"
---

# /revenue-council — Revenue Multi-Agent Workflow

A revenue-domain sibling of `/council`. Convene a roster of revenue specialists — AE, SDR, SE, CSM, Support, RevOps, Partnerships — to deliberate on deal mechanics, pipeline, customer success, support, and channel decisions. Same engine, same workflow, different roster and outputs.

> **Positioning:** This command is **not** for engineering, finance, or people decisions. For software architecture or systems work, use `/council`. For accounting / FP&A / treasury, use `/finance-council`. For org / talent / comp-equity, use `/people-council`. See `references/positioning-charter.md` for the rules that keep these councils separate.

## Usage

```
/revenue-council                              # New session — full workflow (default)
/revenue-council "Should we run a 60-day POC for the Acme deal or push to a 30-day paid pilot?"
/revenue-council --brainstorm "Quick gut check"
/revenue-council --quick "Fast sketch — skip interview, 1 round"
/revenue-council --deep "Max rigor — full session + mandatory deep audit"
/revenue-council --auto "Hands-off — no touchpoints"
/revenue-council --guided "Tight control — approval gates"
/revenue-council --meet "Discussion only — no action plan"
/revenue-council --audit "Direct pipeline / forecast audit"
/revenue-council --resume                     # Resume most recent active session
/revenue-council --list                       # List sessions in workspace
/revenue-council --help                       # Full help
```

## Theme Configuration

This command is a **themed layer** on the shared deliberation engine at `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`. All workflow logic, session management, and phase orchestration are defined in the engine.

```
THEME_ID:               revenue-council
THEME_NAME:             Revenue Council
INTAKE_PROMPT:          "What's the revenue decision?"
AGENT_FILE_PREFIX:      revenue-
CONDUCTOR_PERSONA:      revenue-quartermaster
SESSION_DIR_ROOT:       .claude/revenue-council/sessions/
TEAM_PREFIX:            revenue-council-
GLOBAL_REGISTRY_PATH:   ~/.claude/revenue-council/global-registry.json
INDEX_PATH:             .claude/revenue-council/index.json
CHALLENGE_RULES:        organic
EXTRA_MECHANICS:        (none)
DEFAULT_PROFILE:        balanced
ACTION_PATHS:           A (team execution), K (account-plan package), L (deal-room brief), M (QBR deck)
```

### Phase Labels

```
PHASE_LABELS:
  phase_0: "What's the revenue decision?"
  phase_1: "Revenue Council Interview"
  phase_2: "Revenue Council Assembly — Specialist Selection"
  phase_3_round1: "Round 1: Position"
  phase_3_round2: "Round 2: Challenge"
  phase_3_round3: "Round 3: Converge"
  phase_4: "Revenue Council Plan Ready"
  phase_5: "Revenue Council Execution"
```

### Assembly Label

```
ASSEMBLY_LABEL: "Revenue Council Assembly — Specialist Selection"
```

---

## Agent Roster (7 Specialists + Quartermaster)

| # | Agent | Color | Lens | File | Subagent Type |
|---|-------|-------|------|------|---------------|
| 1 | **AE** | Crimson | Deal mechanics, MEDDPICC, negotiation, close-plan choreography | `revenue-ae` | `general-purpose` |
| 2 | **SDR** | Amber | Outbound prospecting, qualification, opening sequences | `revenue-sdr` | `general-purpose` |
| 3 | **SE** | Blue | Technical sales, demos, POC design, technical objections | `revenue-se` | `general-purpose` |
| 4 | **CSM** | Green | Adoption, expansion, churn signals, renewals choreography | `revenue-csm` | `general-purpose` |
| 5 | **Support** | Cyan | Ticket triage, escalation, SLA, knowledge-base health | `revenue-support` | `general-purpose` |
| 6 | **RevOps** | Indigo | Pipeline mechanics, forecast methodology, CRM hygiene, territory design | `revenue-revops` | `general-purpose` |
| 7 | **Partnerships** | Bronze | Channel, alliances, ecosystem co-sell, partner enablement | `revenue-partnerships` | `general-purpose` |
| — | **Quartermaster** | Cobalt | Orchestration, synthesis, facilitation (Maestro) | `revenue-quartermaster` | *(not spawned)* |

The **Quartermaster** is the conductor's persona for `/revenue-council`, mirroring how Steward serves `/council` and Comptroller serves `/finance-council`. See `${CLAUDE_PLUGIN_ROOT}/agents/revenue-quartermaster.md`.

Selection cap: **5 agents max** per session (smaller than engineering's 7 — revenue deliberations need fewer voices to converge, and the seven specialists cleave naturally into pre-sale / post-sale / system tracks that rarely all need to speak).

> **Roster status:** v1.1 ships the full 7-specialist roster plus Quartermaster. Skill shipped this release: `revenue-account-plan` (sample seed). Remaining department skills (`revenue-objection-handling`, `revenue-sequence-draft`, `revenue-discovery-questions`, `revenue-poc-plan`, `revenue-demo-storyboard`, `revenue-qbr-deck`, `revenue-success-plan`, `revenue-incident-comms`, `revenue-escalation-runbook`, `revenue-pipeline-review`, `revenue-territory-design`, `revenue-partner-program`, `revenue-cosell-playbook`) are tracked for v1.2.

> **Color note:** Revenue's Blue (SE) overlaps with engineering's Architect (also Blue), and revenue's Bronze (Partnerships) overlaps with finance's Treasurer (also Bronze). Per `references/positioning-charter.md` §"Sibling Council Rules", colors are scoped to their council and never appear in mixed-roster sessions (which are prohibited). Reuse is therefore allowed; the conductor persona ("Cobalt") is distinct from Steward (Platinum), Comptroller (Verdigris), and Chair (the in-flight people-council Maestro).

---

## Department Skills Tree

Skills follow the flat plugin layout: `${CLAUDE_PLUGIN_ROOT}/skills/revenue-<skill>/SKILL.md`. Department routing lives in `${CLAUDE_PLUGIN_ROOT}/references/department-index.md`.

```
${CLAUDE_PLUGIN_ROOT}/skills/
  revenue-account-plan/SKILL.md           # Account plan with MEDDPICC + whitespace      (v1.1)
  # v1.2 candidates (one or two per remaining department):
  # revenue-objection-handling, revenue-sequence-draft, revenue-discovery-questions,
  # revenue-poc-plan, revenue-demo-storyboard,
  # revenue-qbr-deck, revenue-success-plan,
  # revenue-incident-comms, revenue-escalation-runbook,
  # revenue-pipeline-review, revenue-territory-design,
  # revenue-partner-program, revenue-cosell-playbook
```

---

## Modifier Rules

### Mandatory Bonuses (+2)

- **AE** gets +2 for any individual-deal, negotiation, or close-plan decision
- **SDR** gets +2 for any outbound-program, top-of-funnel, or qualification-process decision
- **SE** gets +2 for any technical-fit, POC, or RFP decision
- **CSM** gets +2 for any post-sale, retention, expansion, or QBR decision
- **Support** gets +2 for any ticketing, SLA, escalation, or self-serve decision
- **RevOps** gets +2 for any pipeline, forecast, CRM, territory, quota, or comp-plan decision
- **Partnerships** gets +2 for any channel, co-sell, marketplace, or alliance decision

### Anti-Redundancy Penalties (-2)

Domain-internal only. No rules cross over to engineering, finance, or people agents.

- **AE vs SDR** (deal-vs-funnel overlap): Pure new-logo deal mechanics → penalize SDR -2. Pure top-of-funnel / qualification → penalize AE -2.
- **AE vs CSM** (sale-vs-retention overlap): Net-new sale → penalize CSM -2. Expansion sale → both valid. Pure renewal → penalize AE -2.
- **SE vs AE** (technical-vs-commercial overlap): Technical objection / POC scoping → penalize AE -2. Commercial negotiation / pricing → penalize SE -2.
- **CSM vs Support** (proactive-vs-reactive overlap): Proactive adoption / expansion → penalize Support -2. Reactive ticket / incident → penalize CSM -2.
- **RevOps vs AE** (system-vs-deal overlap): Process / CRM / forecast methodology → penalize AE -2. Specific in-flight deal → penalize RevOps -2.
- **Partnerships vs AE** (channel-vs-direct overlap): Partner-led deal → both valid. Direct deal → penalize Partnerships -2. Pure partner program design → penalize AE -2.
- **SDR vs Partnerships** (sourcing overlap): Direct outbound → penalize Partnerships -2. Partner-sourced lead motion → penalize SDR -2.

---

## Challenge Rules (Organic)

Same as `/council` — Round 2 tension pairs are identified organically from Round 1 positions. Look for:

- **Direct contradictions** — AE says push close, CSM says customer isn't ready
- **Resource conflicts** — SE wants 60-day POC, AE flags deal-momentum loss
- **Priority clashes** — RevOps wants new mandatory CRM fields, AE flags rep adoption tax
- **Trade-off surfaces** — Partnerships wants co-sell program, AE flags margin compression

Examples of common revenue tension pairs:
- AE wants close-this-quarter; CSM flags the customer isn't ready to onboard at scale
- SDR wants volume; RevOps flags low conversion that suggests targeting fix
- SE wants long POC; AE flags deal-momentum loss
- CSM wants product-feature ask escalated; Support flags throughput cost on engineering team
- RevOps wants new mandatory CRM fields; AE flags rep adoption tax
- Partnerships wants co-sell program; AE flags margin compression vs direct
- Support wants ticket deflection via KB articles; CSM flags reduced relationship-building touchpoints

Select 2-4 tension pairs. Focus on tensions where resolution would change the design.

---

## Phase 5: Agent Task Mapping

When executing via team (Path A), assign tasks based on agent strengths:

- **AE** — Account plans, close plans, MAPs, ROI cases, objection-handling guides
- **SDR** — Outbound sequences, prospecting plays, ICP refinement, MQL/SQL definitions
- **SE** — POC plans, demo storyboards, technical-objection guides, RFP responses
- **CSM** — Onboarding plans, success plans, QBR decks, churn-risk runbooks
- **Support** — Triage rubrics, escalation runbooks, KB content, incident comms templates
- **RevOps** — Pipeline reviews, forecast methodologies, territory plans, comp-plan modifications
- **Partnerships** — Partner program docs, co-sell playbooks, marketplace listings, joint-motion guides

### Theme-Specific Action Paths

In addition to the engine's default paths, `/revenue-council` supports:

- **Path K — Account-Plan Package:** Quartermaster produces an account plan (key contacts, pain map, success criteria, expansion thesis, AE/CSM responsibilities split) ready to drop into the named-account review.
- **Path L — Deal-Room Brief:** Quartermaster produces a deal-room brief for executive engagement (deal context, MEDDPICC scoring, asks of the executive sponsor, risks, requested concessions).
- **Path M — QBR Deck:** Quartermaster produces a QBR deck (outcomes-to-date, success measures, roadmap alignment, expansion thesis) that the CSM and AE present jointly.

---

## Workflow Execution

**Follow all instructions in `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`**, substituting the theme variables defined above. The engine defines the complete Phase 0–5 workflow, session management commands, resume logic, and cleanup procedures.
