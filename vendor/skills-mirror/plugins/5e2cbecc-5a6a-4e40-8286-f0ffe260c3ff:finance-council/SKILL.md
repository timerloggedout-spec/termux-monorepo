---
description: "Finance Council — multi-agent deliberation for finance, audit, FP&A, tax, and treasury decisions"
argument-hint: "[--help|--brainstorm|--quick|--deep|--auto|--guided|--meet|--audit|--resume|--list|--status|--archive|--cleanup] [DECISION...]"
---

# /finance-council — Finance Multi-Agent Workflow

A finance-domain sibling of `/council`. Convene a roster of finance specialists — Controller, Tax, FP&A, Treasurer, Auditor, Capital, RegRep — to deliberate on close, audit, FP&A, tax, and treasury decisions. Same engine, same workflow, different roster and outputs.

> **Positioning:** This command is **not** for engineering decisions. For software architecture, code, or systems work, use `/council`. See `references/positioning-charter.md` for the rules that keep these councils separate.

## Usage

```
/finance-council                              # New session — full workflow (default)
/finance-council "Should we accelerate revenue recognition on annual contracts?"
/finance-council --brainstorm "Quick gut check"
/finance-council --quick "Fast sketch — skip interview, 1 round"
/finance-council --deep "Max rigor — full session + mandatory deep audit"
/finance-council --auto "Hands-off — no touchpoints"
/finance-council --guided "Tight control — approval gates"
/finance-council --meet "Discussion only — no action plan"
/finance-council --audit "Direct ledger / control audit"
/finance-council --resume                     # Resume most recent active session
/finance-council --list                       # List sessions in workspace
/finance-council --help                       # Full help
```

## Theme Configuration

This command is a **themed layer** on the shared deliberation engine at `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`. All workflow logic, session management, and phase orchestration are defined in the engine.

```
THEME_ID:               finance-council
THEME_NAME:             Finance Council
INTAKE_PROMPT:          "What's the financial decision?"
AGENT_FILE_PREFIX:      finance-
CONDUCTOR_PERSONA:      finance-comptroller
SESSION_DIR_ROOT:       .claude/finance-council/sessions/
TEAM_PREFIX:            finance-council-
GLOBAL_REGISTRY_PATH:   ~/.claude/finance-council/global-registry.json
INDEX_PATH:             .claude/finance-council/index.json
CHALLENGE_RULES:        organic
EXTRA_MECHANICS:        (none)
DEFAULT_PROFILE:        balanced
ACTION_PATHS:           A (team execution), G (memo + journal-entries package), H (FP&A handoff)
```

### Phase Labels

```
PHASE_LABELS:
  phase_0: "What's the financial decision?"
  phase_1: "Finance Council Interview"
  phase_2: "Finance Council Assembly — Specialist Selection"
  phase_3_round1: "Round 1: Position"
  phase_3_round2: "Round 2: Challenge"
  phase_3_round3: "Round 3: Converge"
  phase_4: "Finance Council Plan Ready"
  phase_5: "Finance Council Execution"
```

### Assembly Label

```
ASSEMBLY_LABEL: "Finance Council Assembly — Specialist Selection"
```

---

## Agent Roster (7 Specialists + Comptroller)

| # | Agent | Color | Lens | File | Subagent Type |
|---|-------|-------|------|------|---------------|
| 1 | **Controller** | Forest | GAAP/IFRS, journals, reconciliation, monthly close | `finance-controller` | `general-purpose` |
| 2 | **Tax** | Mustard | Federal/state/international tax, transfer pricing | `finance-tax` | `general-purpose` |
| 3 | **FP&A** | Sky | Forecasting, variance analysis, scenario modeling | `finance-fpa` | `general-purpose` |
| 4 | **Treasurer** | Bronze | Cash management, liquidity, working capital, FX | `finance-treasurer` | `general-purpose` |
| 5 | **Auditor** | Onyx | Internal controls, SOX, audit trail, evidence | `finance-auditor` | `general-purpose` |
| 6 | **Capital** | Indigo | Capital allocation, M&A, investor relations | `finance-capital` | `general-purpose` |
| 7 | **RegRep** | Slate | SEC filings, regulatory reporting, disclosures | `finance-regrep` | `general-purpose` |
| — | **Comptroller** | Verdigris | Orchestration, synthesis, facilitation (Maestro) | `finance-comptroller` | *(not spawned)* |

The **Comptroller** is the conductor's persona for `/finance-council`, mirroring how Steward serves `/council`. See `${CLAUDE_PLUGIN_ROOT}/agents/finance-comptroller.md`.

Selection cap: **5 agents max** per session (smaller than engineering's 7 — finance deliberations need fewer voices to converge).

> **Roster status:** v1.1 ships the full 7-specialist roster plus Comptroller. Skills shipped this release: `finance-reconciliation`, `finance-journal-entries`, `finance-close-checklist`, `finance-variance-analysis`, `finance-tax-research`, `finance-controls-audit`. Remaining department skills (`finance-cash-forecast`, `finance-hedging-proposal`, `finance-provision`, `finance-evidence-package`, `finance-capital-allocation`, `finance-investor-letter`, `finance-disclosure-language`, `finance-segment-reporting`) are tracked for v1.2.

---

## Department Skills Tree

Skills follow the flat plugin layout: `${CLAUDE_PLUGIN_ROOT}/skills/finance-<skill>/SKILL.md`. Department routing lives in `${CLAUDE_PLUGIN_ROOT}/references/department-index.md`.

```
${CLAUDE_PLUGIN_ROOT}/skills/
  finance-reconciliation/SKILL.md       # Account reconciliation procedures        (v1.1)
  finance-journal-entries/SKILL.md      # GAAP/IFRS journal entry preparation       (v1.1)
  finance-close-checklist/SKILL.md      # Monthly/quarterly close orchestration     (v1.1)
  finance-variance-analysis/SKILL.md    # FP&A variance analysis + commentary       (v1.1)
  finance-tax-research/SKILL.md         # Federal/state/intl tax research memo      (v1.1)
  finance-controls-audit/SKILL.md       # SOX 404 controls testing                  (v1.1)
  # v1.2 candidates (one per remaining department):
  # finance-cash-forecast, finance-hedging-proposal, finance-provision,
  # finance-evidence-package, finance-capital-allocation, finance-investor-letter,
  # finance-disclosure-language, finance-segment-reporting
```

---

## Modifier Rules

### Mandatory Bonuses (+2)

- **Controller** gets +2 for any decision involving GAAP/IFRS recognition, the close calendar, or journal entries
- **Tax** gets +2 for any decision with cross-jurisdictional tax exposure or transfer-pricing implications
- **FP&A** gets +2 for any decision requiring forecast revision, scenario modeling, or variance commentary
- **Treasurer** gets +2 for any decision affecting cash runway, liquidity, working capital, or FX exposure
- **Auditor** gets +2 for any decision touching internal controls, SOX scope, or audit evidence
- **Capital** gets +2 for any decision involving capital allocation, M&A, or investor relations
- **RegRep** gets +2 for any decision triggering SEC filings, segment reporting, or material disclosures

### Anti-Redundancy Penalties (-2)

Domain-internal only. No rules cross over to engineering agents (`/council` roster).

- **Controller vs Auditor** (close-vs-controls overlap): Pure recognition/journal question → penalize Auditor -2. Controls effectiveness or evidence → penalize Controller -2.
- **Tax vs Controller** (recognition overlap): Book-tax difference and provision → both valid. Pure book treatment → penalize Tax -2. Pure tax position → penalize Controller -2.
- **FP&A vs Capital** (forecast overlap): Operating forecast → penalize Capital -2. Capital structure / financing scenarios → penalize FP&A -2.
- **Treasurer vs Capital** (capital overlap): Short-term liquidity → penalize Capital -2. Long-term capital structure → penalize Treasurer -2.
- **RegRep vs Auditor** (disclosure overlap): External filings → penalize Auditor -2. Internal controls over disclosure → penalize RegRep -2.

---

## Challenge Rules (Organic)

Same as `/council` — Round 2 tension pairs are identified organically from Round 1 positions. Look for:

- **Direct contradictions** — Controller says capitalize, FP&A says expense
- **Resource conflicts** — Treasurer wants liquidity buffer, Capital wants buyback
- **Priority clashes** — RegRep wants conservative disclosure, Capital wants growth narrative
- **Trade-off surfaces** — Tax-optimal structure that complicates the close

Examples of common finance tension pairs:
- Controller wants conservative recognition, FP&A wants the bookings forecast to land cleanly
- Tax wants entity restructure, Auditor flags control re-scoping cost
- Treasurer wants cash buffer, Capital wants share repurchase
- Auditor wants more documentation, Controller flags close-cycle bandwidth
- RegRep wants enhanced disclosure, Capital flags competitive signaling
- FP&A wants stretch forecast, Controller flags revenue-recognition timing risk

Select 2-4 tension pairs. Focus on tensions where resolution would change the design.

---

## Phase 5: Agent Task Mapping

When executing via team (Path A), assign tasks based on agent strengths:

- **Controller** — Journal entries, reconciliations, close calendar updates, accounting memos
- **Tax** — Tax research memos, provision calculations, transfer-pricing documentation
- **FP&A** — Forecast updates, variance commentary, scenario decks, board materials
- **Treasurer** — Cash forecasts, hedging proposals, working-capital recommendations
- **Auditor** — Controls walkthroughs, evidence collection, SOX narratives, finding remediation
- **Capital** — Capital allocation models, investor-letter drafts, M&A diligence checklists
- **RegRep** — Filing drafts, disclosure language, segment reporting

### Theme-Specific Action Paths

In addition to the engine's default paths, `/finance-council` supports:

- **Path G — Memo + Journal-Entries Package:** Conductor produces a finance memo (decision, rationale, accounting treatment) plus a draft journal-entries worksheet ready to import into the GL.
- **Path H — FP&A Handoff:** Conductor packages forecast revisions and variance commentary for handoff to the FP&A team's modeling environment.

---

## Workflow Execution

**Follow all instructions in `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`**, substituting the theme variables defined above. The engine defines the complete Phase 0–5 workflow, session management commands, resume logic, and cleanup procedures.
