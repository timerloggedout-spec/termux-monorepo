---
description: "People Council — multi-agent deliberation for talent, performance, comp, L&D, DEI, and people-ops decisions"
argument-hint: "[--help|--brainstorm|--quick|--deep|--auto|--guided|--meet|--audit|--resume|--list|--status|--archive|--cleanup] [DECISION...]"
---

# /people-council — People Multi-Agent Workflow

A people-domain sibling of `/council`. Convene a roster of people specialists — Talent, PeoplePartner, TotalRewards, LearnDev, DEI, PeopleOps — to deliberate on hiring, performance, compensation, career-framework, equity-of-practice, and employment-compliance decisions. Same engine, same workflow, different roster and outputs.

> **Positioning:** This command is **not** for engineering or finance decisions. For software architecture, code, or systems work, use `/council`. For accounting, FP&A, tax, or treasury work (including comp **budget** decisions), use `/finance-council`. See `references/positioning-charter.md` for the rules that keep these councils separate.

## Usage

```
/people-council                              # New session — full workflow (default)
/people-council "Should we open a London hub for engineering hiring next quarter?"
/people-council --brainstorm "Quick gut check"
/people-council --quick "Fast sketch — skip interview, 1 round"
/people-council --deep "Max rigor — full session + mandatory deep audit"
/people-council --auto "Hands-off — no touchpoints"
/people-council --guided "Tight control — approval gates"
/people-council --meet "Discussion only — no action plan"
/people-council --audit "Direct policy / process audit"
/people-council --resume                     # Resume most recent active session
/people-council --list                       # List sessions in workspace
/people-council --help                       # Full help
```

## Theme Configuration

This command is a **themed layer** on the shared deliberation engine at `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`. All workflow logic, session management, and phase orchestration are defined in the engine.

```
THEME_ID:               people-council
THEME_NAME:             People Council
INTAKE_PROMPT:          "What's the people decision?"
AGENT_FILE_PREFIX:      people-
CONDUCTOR_PERSONA:      people-chair
SESSION_DIR_ROOT:       .claude/people-council/sessions/
TEAM_PREFIX:            people-council-
GLOBAL_REGISTRY_PATH:   ~/.claude/people-council/global-registry.json
INDEX_PATH:             .claude/people-council/index.json
CHALLENGE_RULES:        organic
EXTRA_MECHANICS:        (none)
DEFAULT_PROFILE:        balanced
ACTION_PATHS:           A (team execution), I (job-description package), J (employment memo)
```

### Phase Labels

```
PHASE_LABELS:
  phase_0: "What's the people decision?"
  phase_1: "People Council Interview"
  phase_2: "People Council Assembly — Specialist Selection"
  phase_3_round1: "Round 1: Position"
  phase_3_round2: "Round 2: Challenge"
  phase_3_round3: "Round 3: Converge"
  phase_4: "People Council Plan Ready"
  phase_5: "People Council Execution"
```

### Assembly Label

```
ASSEMBLY_LABEL: "People Council Assembly — Specialist Selection"
```

---

## Agent Roster (6 Specialists + Chair)

| # | Agent | Color | Lens | File | Subagent Type |
|---|-------|-------|------|------|---------------|
| 1 | **Talent** | Coral | Recruiting, sourcing, interview-loop design, offer mechanics | `people-talent` | `general-purpose` |
| 2 | **PeoplePartner** | Sage | Employee relations, performance management, manager coaching | `people-peoplepartner` | `general-purpose` |
| 3 | **TotalRewards** | Gold | Compensation bands, equity, benefits, geo differentials | `people-totalrewards` | `general-purpose` |
| 4 | **LearnDev** | Teal | L&D, career frameworks, manager training, skills development | `people-learndev` | `general-purpose` |
| 5 | **DEI** | Plum | Belonging, accessibility, equitable practice design, ERG support | `people-dei` | `general-purpose` |
| 6 | **PeopleOps** | Slate | HRIS, payroll, employment-law compliance, leave administration | `people-peopleops` | `general-purpose` |
| — | **Chair** | Linen | Orchestration, synthesis, facilitation (Maestro) | `people-chair` | *(not spawned)* |

The **Chair** is the conductor's persona for `/people-council`, mirroring how Steward serves `/council` and Comptroller serves `/finance-council`. See `${CLAUDE_PLUGIN_ROOT}/agents/people-chair.md`.

Selection cap: **5 agents max** per session (smaller than engineering's 7 — people deliberations need fewer voices to converge, matching the finance sibling).

> **Roster status:** v1.1 ships the full 6-specialist roster plus Chair. Skills shipped this release: `people-job-description`. Remaining department skills (`people-interview-rubric`, `people-offer-construction`, `people-pip-construction`, `people-er-investigation`, `people-comp-band`, `people-equity-grant-design`, `people-career-ladder`, `people-onboarding-plan`, `people-pay-equity-analysis`, `people-accessibility-review`, `people-employment-memo`, `people-leave-administration`) are tracked for v1.2.

---

## Department Skills Tree

Skills follow the flat plugin layout: `${CLAUDE_PLUGIN_ROOT}/skills/people-<skill>/SKILL.md`. Department routing lives in `${CLAUDE_PLUGIN_ROOT}/references/department-index.md`.

```
${CLAUDE_PLUGIN_ROOT}/skills/
  people-job-description/SKILL.md       # Structured role spec for posting          (v1.1)
  # v1.2 candidates (one or more per remaining department):
  # people-interview-rubric, people-offer-construction,
  # people-pip-construction, people-er-investigation,
  # people-comp-band, people-equity-grant-design,
  # people-career-ladder, people-onboarding-plan,
  # people-pay-equity-analysis, people-accessibility-review,
  # people-employment-memo, people-leave-administration
```

---

## Modifier Rules

### Mandatory Bonuses (+2)

- **Talent** gets +2 for any open-req, sourcing, or interview-design decision
- **PeoplePartner** gets +2 for any performance, ER, or manager-effectiveness decision
- **TotalRewards** gets +2 for any comp, equity, benefits, or geo-differential decision
- **LearnDev** gets +2 for any career-framework, training, or onboarding decision
- **DEI** gets +2 for any pay-equity, accessibility, hiring-practice, or representation decision
- **PeopleOps** gets +2 for any HRIS, payroll, employment-law, leave, or termination decision

### Anti-Redundancy Penalties (-2)

Domain-internal only. No rules cross over to engineering agents (`/council` roster) or finance agents (`/finance-council` roster).

- **Talent vs PeoplePartner** (hiring-vs-mobility overlap): External hiring → penalize PeoplePartner -2. Internal mobility / promotion → penalize Talent -2.
- **TotalRewards vs DEI** (comp-vs-equity overlap): Pay equity analysis → both valid. Pure comp-band design → penalize DEI -2. Pure equitable-practice review → penalize TotalRewards -2.
- **LearnDev vs PeoplePartner** (development-vs-performance overlap): Structured career framework / curriculum → penalize PeoplePartner -2. Individual coaching / performance issue → penalize LearnDev -2.
- **PeopleOps vs DEI** (compliance-vs-inclusion overlap): Pure compliance question → penalize DEI -2. Pure inclusion-practice question → penalize PeopleOps -2.
- **PeopleOps vs Talent** (compliance-vs-funnel overlap): I-9 / right-to-work → penalize Talent -2. Offer construction / interview process → penalize PeopleOps -2.

---

## Challenge Rules (Organic)

Same as `/council` and `/finance-council` — Round 2 tension pairs are identified organically from Round 1 positions. Look for:

- **Direct contradictions** — Talent says hire externally, PeoplePartner says promote internally
- **Resource conflicts** — TotalRewards wants market-rate band, DEI flags pay-equity remediation cost
- **Priority clashes** — PeoplePartner wants direct PIP, PeopleOps flags jurisdiction-specific just-cause documentation
- **Trade-off surfaces** — Talent-optimal sourcing footprint that requires entity / payroll registration PeopleOps flags

Examples of common people tension pairs:
- Talent wants speed-to-hire, PeopleOps flags employment-law steps that can't be skipped
- TotalRewards wants market-rate band, DEI flags pay-equity implications for existing population
- PeoplePartner wants direct PIP, PeopleOps flags jurisdiction-specific just-cause documentation gaps
- LearnDev wants new dual-ladder, TotalRewards flags comp-band re-mapping cost
- DEI wants demographic data collection, PeopleOps flags GDPR / state-specific restrictions
- Talent wants location-flexible hiring, PeopleOps flags entity / payroll registration cost in new states/countries

Select 2-4 tension pairs. Focus on tensions where resolution would change the design.

---

## Phase 5: Agent Task Mapping

When executing via team (Path A), assign tasks based on agent strengths:

- **Talent** — Job descriptions, sourcing strategies, interview-loop designs, offer letters
- **PeoplePartner** — PIP drafts, performance-conversation guides, ER investigation memos, coaching plans
- **TotalRewards** — Comp-band proposals, equity grant designs, benefits comparisons, comp committee materials
- **LearnDev** — Career-ladder docs, manager training curricula, onboarding plans, competency rubrics
- **DEI** — Pay-equity analyses, accessibility audits, ERG charters, inclusion-survey designs
- **PeopleOps** — Employment memos, leave-administration playbooks, HRIS configuration specs, termination checklists

### Theme-Specific Action Paths

In addition to the engine's default paths, `/people-council` supports:

- **Path I — Job-Description Package:** Conductor produces a role spec (responsibilities, success criteria, comp band reference, interview rubric) ready for posting and for the Talent specialist to operationalize into the ATS.
- **Path J — Employment Memo:** Conductor produces an employment-decision memo (situation, options, jurisdiction-specific considerations, recommended path with PeopleOps and PeoplePartner sign-off). Many people decisions also require external legal / finance sign-off; the memo flags this rather than assuming the Chair's facilitation closes it.

---

## Workflow Execution

**Follow all instructions in `${CLAUDE_PLUGIN_ROOT}/commands/_council-engine.md`**, substituting the theme variables defined above. The engine defines the complete Phase 0–5 workflow, session management commands, resume logic, and cleanup procedures.
