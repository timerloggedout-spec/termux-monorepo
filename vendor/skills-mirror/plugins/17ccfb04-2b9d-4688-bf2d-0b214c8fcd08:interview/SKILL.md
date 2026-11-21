---
description: "Pre-/refine workflow. When a feature idea is ambiguous, conduct a short structured interview to extract the questions that materially change the spec. Output: a tighter feature statement ready for /refine."
argument-hint: "<vague feature idea in quotes>"
allowed-tools: Read, Grep, Write
destructive: false
read-only: true
---

# /interview — extract the questions that change the answer

The user's idea (`$ARGUMENTS`) is vague enough that you need clarification
before either `/refine` or `/one-shot` can produce a good spec. Your job
is to **ask the smallest number of questions** that, once answered,
remove the ambiguity.

This is conversational, not algorithmic. No tools to spawn, no scripts
to call. You're a senior engineer asking the right questions of a
product owner.

## When to invoke instead of `/refine` directly

Use `/interview` when ANY of these are true:

- The idea is < 10 words ("add notifications", "make it faster")
- Multiple disjoint interpretations are plausible
- Critical sizing / scale / authority dimensions are missing
- The user has used non-domain words ("smart", "automated", "intelligent")
  that obscure what should happen

If the user already provided a 50-word idea with clear scope, skip
`/interview` and go straight to `/refine`.

## Process — three short rounds, maximum 6 questions total

### Round 1: WHO + WHEN (max 2 questions)

These two dimensions matter more than any other. Skip them only if
the user has already answered them.

- **Who's the actor / requester?** (end user · admin · system / cron · external webhook)
- **When does this happen?** (synchronous on user click · async after a webhook · on a schedule · once during onboarding)

### Round 2: WHAT could differ (max 2 questions)

Pick the 2 dimensions that, if you guessed wrong, would make you
re-build it later. Examples:

- **Scale**: "Are we talking 10 events a day, 10/sec, or 10k/sec?"
  (changes choice between sync handler / queue / streaming pipeline)
- **Authority**: "Can the actor do this for any user, or only their own
  data?" (tenancy boundary)
- **Reversibility**: "What if the user changes their mind 10 minutes
  later? Is undo a feature or out of scope?"
- **Source of truth**: "Where does the canonical data live? Our DB,
  Stripe, an external CRM?" (drives sync vs cache vs read-through)
- **Audit / compliance**: "Does someone (legal, ops, support) need to
  see what happened later?" (forces audit log + retention)
- **Failure mode**: "If this fails mid-flight, what should the user
  see — error, silent retry, partial success?"

### Round 3: BOUNDARIES (max 2 questions)

The "explicitly NOT doing" questions — these prevent scope creep later.

- **What's the smallest version that would be useful?** (anchors MVP)
- **Is there a non-feature here?** (e.g. "we DON'T need a UI for this,
  just an API" or "we DON'T need to support partial refunds — full only")

## How to phrase the questions

- **One sentence, no nested clauses.** "How many of these per day?" not
  "I'm wondering, roughly, whether the volume here looks more like..."
- **Offer 2-3 anchor answers** so the user can pick instead of generating
  from scratch. "Closer to a) 100/day, b) 10k/day, or c) 1M+/day?"
- **Never ask "anything else?"** — that's open-ended. Ask the next
  specific thing or stop.
- **Never ask questions you'd answer by reading the code** — if there's
  an existing codebase, scan it FIRST with Grep/Read.

## Output — the refined restatement

After 3-6 questions (or fewer if you got everything in 2), produce
this single artifact:

```markdown
## Refined feature (after interview)

**Original**: <user's vague phrase>

**Restated**:
<one paragraph: who, when, what, scale, auth boundary, failure mode>

**Confirmed assumptions** (from interview):
- <each clarified dimension on one line>

**Now run**:
```bash
/refine "<the precise sharpened feature>"
```
```

Save it to `.refined/{kebab-feature-name}.md` so `/one-shot` can pick
it up if invoked later.

## Hard rules

1. **Maximum 6 questions across all 3 rounds.** Past 6 you're stalling.
   If you still don't know enough, escalate ("This sounds like 2-3
   separate features — let's pick the one most worth building first").
2. **One question per turn.** Wait for an answer before the next one.
3. **Never ask questions where the answer doesn't change the design.**
   Test each candidate question: "If they said A vs B, would I write
   different code?" If no — don't ask.
4. **Never grand-tour: skip questions whose answers were already given.**
   If they said "internal admin tool only" you already know `auth=jwt`
   and tenancy = single; don't re-ask.
5. **Quote the user's words back** when synthesizing — proves you
   listened, surfaces misunderstanding fast.
6. **When stuck between 5 and 6 questions**, prefer NO more questions —
   produce the restatement with the remaining uncertainty marked as an
   open question for `/refine` to bound.

## Examples

### Example 1 — Vague request

User: `/interview "add notifications"`

You: "Notifications about what — and to whom? Pick the closest:
a) the user themselves about their own activity,
b) admin/staff about user events,
c) external systems (webhooks)."

User: "(a)"

You: "Where do they show up — in-app only, email, or both?"

User: "in-app for now, email later"

You: "What kicks them off — a specific action (e.g. user uploads a
file), or a periodic check (e.g. daily summary)?"

User: "every time another user replies to their post"

You produce:

```markdown
## Refined feature (after interview)

**Original**: add notifications

**Restated**:
Add in-app notifications shown to the user (recipient) when ANOTHER
user replies to their post. MVP scope: notifications table, an unread
flag, a /notifications endpoint, in-app delivery only. No email yet
(deferred). Triggered synchronously by the existing
ReplyService.create() — no background job needed unless write volume
demands it later.

**Confirmed assumptions**:
- Recipient: the user themselves (not admin, not external)
- Channel: in-app only (email is "later, not MVP")
- Trigger: another user posting a reply
- Scale: assumed < 1k/day (didn't ask — flag for /refine)

**Now run**:
\`\`\`bash
/refine "Add in-app notifications: each time UserB replies to UserA's
post, a Notification row is created for UserA. GET /notifications shows
unread first. PATCH /notifications/{id}/read marks as read."
\`\`\`
```

### Example 2 — Already clear, abort interview

User: `/interview "Add a webhook receiver at POST /webhooks/stripe that
verifies the Stripe-Signature header, persists the event payload, and
enqueues a job to process it. Use the existing webhook_secret env var."`

You: "This is already concrete enough to go straight to `/one-shot`.
Skipping `/interview`. Want me to invoke `/one-shot` with this directly,
or run `/refine` first to produce the one-pager?"

(That's the right call when the user's input is already sharp — don't
ask questions for the sake of asking.)
