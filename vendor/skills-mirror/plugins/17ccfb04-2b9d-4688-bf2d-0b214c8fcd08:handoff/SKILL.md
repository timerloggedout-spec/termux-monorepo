---
name: handoff
description: Conversation-to-runbook (mattpocock-inspired). Compact handoff document for the next agent or human. Strips conversation context, keeps decisions and artifacts. Use after SHIP phase to hand off to ops or next iteration.
argument-hint: "[@conversation-log or --from-last-output] [@path/to/project] [--format=markdown|json] [--audience=developer|operator|manager]"
allowed-tools: Read, Write
---

# Handoff — Conversation to Runbook

**Strip the conversation. Keep the deliverable.** Transform verbose generation
logs into a compact handoff document suitable for the next agent or human.

Typical reduction: 90% of context, 100% of actionable info retained.

## When to Use

1. **After SHIP phase** — Feature generation complete; hand off to ops/QA
2. **Between iterations** — Multi-phase work; summarize phase 1, pass to phase 2
3. **Human handoff** — Generated code is done; developer takes over maintenance
4. **Cross-agent handoff** — One agent completes, next agent takes over
5. **Escalation document** — Problem encountered; hand off to senior engineer

## How It Works

Handoff generates a compact document with 5 sections:

### Section 1: WHAT WAS BUILT

**One-sentence summary + key artifacts.**

Format:
```
**Feature:** [1-sentence description]

Artifacts:
- [filename]: [purpose]
- [filename]: [purpose]
- [filename]: [purpose]
```

Example:
```
**Feature:** Payment processing with Stripe integration and webhook handlers.

Artifacts:
- payment/models.py: Payment + Refund entities
- payment/views.py: Charge + refund endpoints
- payment/webhooks.py: Stripe webhook handlers
- tests/test_payment.py: 18 test cases
- docs/STRIPE_SETUP.md: Configuration guide
```

### Section 2: HOW TO RUN IT

**Quick start for the next person.**

Format:
```
Prerequisites:
- [dependency or setup step]
- [dependency or setup step]

Setup (5 min):
1. [exact command]
2. [exact command]
3. [exact command]

Verify:
$ [test command]
[expected output or status]
```

Example:
```
Prerequisites:
- Python 3.11+
- Stripe test account (stripe.com/login)
- PostgreSQL 15

Setup (5 min):
1. pip install -r requirements.txt
2. export STRIPE_API_KEY=sk_test_...
3. python manage.py migrate
4. python manage.py runserver

Verify:
$ curl -X POST http://localhost:8000/payment/charge \
  -d '{"amount": 100, "token": "tok_visa"}'
200 OK
```

### Section 3: WHAT WAS TESTED

**Test coverage snapshot.**

Format:
```
Test Summary:
- [category]: [N] tests, all passing

Test Locations:
- [test file]: [N] tests
  - [brief test names or categories]

Known Gaps:
- [gap 1 if any]
- [gap 2 if any]

To Run Tests:
$ [exact test command]
```

Example:
```
Test Summary:
- Unit: 12 tests, all passing
- Integration: 6 tests, all passing

Test Locations:
- tests/test_payment_models.py: 6 tests (entity validation, state transitions)
- tests/test_payment_views.py: 6 tests (endpoint auth, error cases)
- tests/test_webhooks.py: 6 tests (signature validation, idempotency)

Known Gaps:
- Load testing (not in scope)
- Stripe API downtime scenarios (manual test only)

To Run Tests:
$ pytest tests/test_payment.py -v
```

### Section 4: DEPLOYMENT CHECKLIST

**What needs to happen before production.**

Format:
```
Pre-deployment:
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

During deployment:
- [ ] Step 1
- [ ] Step 2

Post-deployment verification:
- [ ] Check [metric or behavior]
- [ ] Check [metric or behavior]

Rollback plan:
[If something goes wrong, what's the fast exit?]
```

Example:
```
Pre-deployment:
- [ ] Create Stripe live API key (not test)
- [ ] Set environment variables in prod (STRIPE_API_KEY, WEBHOOK_SECRET)
- [ ] Run database migrations: alembic upgrade head
- [ ] Run smoke tests against prod DB (staging)

During deployment:
- [ ] Deploy payment service
- [ ] Verify Stripe webhook endpoint URL is configured
- [ ] Monitor error logs for 5 minutes

Post-deployment verification:
- [ ] Test charge endpoint via curl (small amount)
- [ ] Check webhook delivery in Stripe dashboard
- [ ] Verify payments appear in reporting dashboard

Rollback plan:
If payments are failing:
1. Revert code: git revert [commit hash]
2. Restore DB from backup (if needed)
3. Reconfigure webhook endpoint to old handler
4. Test with manual charge
Estimated time: 15 minutes
```

### Section 5: KNOWN ISSUES & NEXT STEPS

**What's done, what's not, what's next.**

Format:
```
✅ Completed:
- [feature or requirement met]
- [feature or requirement met]

⚠️ Known Limitations:
- [limitation 1]
- [limitation 2]

📋 Next Steps (Priority Order):
1. [task 1] (estimated: [time])
2. [task 2] (estimated: [time])
3. [task 3] (estimated: [time])

⚡ Quick Wins (Low effort, high value):
- [task]
- [task]
```

Example:
```
✅ Completed:
- Payment charging via Stripe
- Webhook validation and handling
- 18 test cases with >95% coverage
- Database migrations and schema
- Error handling and logging

⚠️ Known Limitations:
- Only credit cards (no ACH, wire transfer)
- No subscription auto-renewal
- No dispute handling (manual review required)
- Webhook retries are AWS SQS, not Stripe native

📋 Next Steps (Priority Order):
1. Add refund endpoint (estimated: 2h)
2. Implement subscription auto-renewal (estimated: 4h)
3. Add payment analytics dashboard (estimated: 6h)

⚡ Quick Wins (Low effort, high value):
- Add idempotency key validation (1h)
- Improve webhook error messages (30m)
```

## Usage in one-shot-prompting Pipeline

### Phase: SHIP (after critic passes)

When critic gives all-clear:

```bash
/handoff --from-last-output @./project --audience=developer
```

Output: `HANDOFF.md` (compact runbook for next person)

### Phase: HUMAN TAKEOVER

When code generation is complete, generate handoff for human developer:

```bash
/handoff @./project --audience=developer --format=markdown
```

Or for operations team:

```bash
/handoff @./project --audience=operator --format=markdown
```

## Checklist

- ✅ Summary is 1–2 sentences (not a paragraph)
- ✅ All file paths are relative to project root
- ✅ Setup steps are exact commands (copy-paste-able)
- ✅ Test command is documented and runs locally
- ✅ Deployment checklist is complete and ordered
- ✅ Known issues are honest (no spin)
- ✅ Next steps are prioritized
- ✅ Rollback plan is documented with estimated time

**[BLOCKED]** If setup cannot be completed in <10 minutes → document the blocker and mark as "manual step required".

---

**Adapted from:** mattpocock/skills (runbook generation pattern)

**Last updated:** 2026-05-19
