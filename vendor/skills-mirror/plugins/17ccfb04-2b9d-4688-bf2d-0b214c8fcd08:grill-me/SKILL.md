---
name: grill-me
description: Intensive questioning (mattpocock-inspired). Exhaustively explore decision tree before finalizing specs. Surface hidden constraints, trade-offs, and anti-patterns. Designed for pre-architect phase to catch requirements drift early.
argument-hint: "[feature description or @spec.json] [@path/to/project] [--depth=shallow|medium|deep] [--focus=requirements|design|constraints]"
allowed-tools: Read, Write
---

# Grill-Me — Exhaustive Requirement Questioning

**Ask every branch of the decision tree.** Before architect generates code,
ensure no hidden constraints, assumptions, or trade-offs are missed.

Prevents expensive rework: catch fuzzy requirements now, not in VERIFY phase.

## When to Use

1. **PLAN stage (pre-architect)** — Feature description is 1–2 sentences; needs expansion
2. **Ambiguous specs** — "Add payment processing" (too vague)
3. **Cross-domain features** — Multiple systems involved (auth + payments + reporting)
4. **High-stakes features** — Compliance, security, or customer-facing changes
5. **Reversible design decisions** — Before committing to architecture

## How It Works

Grill-me asks 4–5 questions per category across 6 categories, prioritized by risk:

### Category 1: SCOPE & CONSTRAINTS (ALWAYS)

**Non-negotiable first.** What are the hard limits?

Questions:
- What data must this feature handle? (size, volume, frequency)
- What are the non-negotiable constraints? (latency, storage, compliance, budget)
- What existing systems must integrate? (APIs, databases, message queues)
- What are the failure modes? (What happens if this breaks?)
- Who are the end users? (What's their tolerance for outages or slowness?)

**Output format:**
```
Scope & Constraints:
- Data volume: [answer]
- Hard constraints: [answer]
- Integration touch points: [answer]
- Failure tolerance: [answer]
- User profile: [answer]
```

### Category 2: DATA MODEL

**What entities and relationships exist?**

Questions:
- What entities are involved? (user, payment, transaction, subscription, etc.)
- What are the relationships? (1:1, 1:many, many:many)
- What fields are required vs. optional? (validation rules)
- What's the cardinality? (Can a user have 0, 1, or many payments?)
- What historical data must we keep? (audit trail, soft deletes, versioning)

**Output format:**
```
Data Model:
- Entities: [list with cardinality]
- Key relationships: [1:many: user → payments]
- Required vs optional: [fields list]
- Historical retention: [what and how long]
```

### Category 3: BEHAVIOR & WORKFLOWS

**What should happen, step-by-step?**

Questions:
- What's the happy path? (user does X, system does Y, user sees Z)
- What happens on failure? (payment declined, network timeout, invalid data)
- What edge cases exist? (zero-dollar payment? negative refund? concurrent requests?)
- What's the user's mental model? (Is this shopping cart or subscription renewal?)
- What notifications/side-effects? (email, webhook, audit log, webhook to external system)

**Output format:**
```
Workflows:
- Happy path: [step-by-step]
- Failures: [error case 1, error case 2, ...]
- Edge cases: [case 1, case 2, ...]
- Notifications: [what gets triggered]
```

### Category 4: INTEGRATION & DEPENDENCIES

**What talks to what?**

Questions:
- What external APIs are involved? (Stripe, Auth0, third-party services)
- What's the sequencing? (Must auth happen before payment? What if auth fails?)
- What's the transaction boundary? (Is this atomic? Can we partial-commit?)
- What happens on downstream failures? (If Stripe is down, do we queue and retry?)
- Do we need polling, webhooks, or async processing?

**Output format:**
```
Dependencies:
- External APIs: [list with required vs. optional]
- Sequencing: [what happens first, second, ...]
- Transaction scope: [atomic or distributed]
- Failure handling: [queue/retry vs. fail-fast]
```

### Category 5: NON-FUNCTIONAL REQUIREMENTS

**Performance, security, maintainability?**

Questions:
- Performance targets? (response time, throughput, SLO)
- Security gates? (PCI compliance, encryption, zero-knowledge, etc.)
- Concurrency model? (sequential, parallel, distributed)
- Monitoring & observability? (metrics, logs, tracing, alerts)
- Testing burden? (Is this feature testable? What's the test scope?)

**Output format:**
```
Non-Functional:
- Performance SLO: [response time, throughput]
- Security compliance: [PCI, encryption, auth, ...]
- Concurrency: [sequential|parallel|distributed]
- Observability: [metrics, logs, traces, alerts]
- Test coverage: [unit, integration, e2e]
```

### Category 6: TRADE-OFFS & ASSUMPTIONS

**The hard questions.**

Questions:
- What are we *not* doing? (Deliberately scoped out)
- What assumptions are we making? (Third-party is reliable, data is valid, etc.)
- What's the cost-benefit? (Is the complexity worth the feature?)
- What could go wrong? (Blind spots, anti-patterns)
- What's the migration path? (If we get this wrong, how do we unwind?)

**Output format:**
```
Trade-offs & Assumptions:
- Out of scope: [what we're NOT doing]
- Key assumptions: [list with confidence]
- Cost-benefit: [what are we paying in complexity?]
- Blind spots: [potential gotchas]
- Rollback plan: [if we need to unwind this]
```

## Usage in one-shot-prompting Pipeline

### Phase: PLAN (pre-architect)

After user provides feature description, run grill-me:

```bash
/grill-me "add payment processing" @./project --depth=deep
```

Output: `requirements-expanded.md` with 30–50 Q&A pairs.

**Next:** Share expanded requirements with user. Allow refinement.
Then: Feed to architect with `--review` flag to see spec draft before code generation.

### Phase: SPEC REVIEW (optional gate)

If spec looks incomplete or risky:

```bash
/grill-me @./spec.json --focus=constraints --depth=medium
```

Output: Questions specifically about hard constraints. Architect re-answers.

## Checklist

- ✅ All 6 categories covered (at minimum, Scope & Data Model)
- ✅ Questions are open-ended, not yes/no
- ✅ Answers are detailed (not single words)
- ✅ Trade-offs explicitly documented
- ✅ Assumptions listed with confidence level (HIGH/MEDIUM/LOW)
- ✅ User has reviewed and confirmed expanded requirements

**[BLOCKED]** If any category has >50% unknown answers → mark uncertain and proceed with caveats. Architect will request clarification during design phase.

## Example: Payment Processing

**BEFORE grill-me:**
> "Add payment processing"

**AFTER grill-me (summary):**
```
Scope: Handle card payments, refunds, multiple currencies, PCI compliance required
Data: Payment, Refund, Transaction entities; audit trail for 7 years
Behavior: Charge card → capture → email receipt; decline → log and notify
Integration: Stripe API; webhook for settlement; sync to reporting DB
Non-functional: <100ms charge response, 99.9% uptime, encrypted storage
Trade-offs: Only credit cards (not ACH), no subscription auto-renew, no dispute handling
```

---

**Adapted from:** mattpocock/skills (decision-tree questioning pattern)

**Last updated:** 2026-05-19
