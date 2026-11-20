---
name: caveman
description: Token compression mode (mattpocock-inspired). Cuts output ~75% by dropping filler while preserving technical accuracy. Use for long specs, verbose debug logs, or context windows approaching limits. Strips commentary, keeps data.
argument-hint: "[text or @file] [--target-reduction=75] [--preserve-code] [--preserve-errors]"
allowed-tools: Read, Write
---

# Caveman Mode — Token Compression

**Fewer words. Same meaning.** Token optimization by dropping non-technical filler
while preserving all technical accuracy and decision content.

Typical reduction: **~75%** of tokens, zero loss of actionable information.

## When to Use

1. **Long feature specs** — Architect receives 500-line spec, needs to summarize for implementer
2. **Verbose error logs** — Debug logs with repetitive frames; keep unique errors, strip duplicates
3. **Context approaching limits** — If you're over 60% of context window, compress before next turn
4. **Handoff documents** — Convert verbose generation logs to compact runbook

## How It Works

Caveman mode applies 5 compression rules in sequence:

### Rule 1: Drop Commentary & Filler

**Remove:**
- Explanatory phrases ("This is because...", "Note that...", "It's worth mentioning...")
- Hedging language ("might", "could", "possibly", "arguably")
- Redundant transitions ("Furthermore", "Moreover", "In addition")
- Motivational language ("Great!", "Excellent!", "Perfect")

**Keep:**
- All facts, decisions, code
- All error messages, stack traces
- All constraints, requirements

Example:
```
BEFORE (127 tokens):
This is a Django REST API endpoint that serves user data.
It's worth noting that we're using DRF serializers, which is a really nice pattern.
The endpoint might be slow if we don't add pagination, but it's also possible
that we'll optimize later. Moreover, we should consider caching.

AFTER (28 tokens):
Django REST API endpoint serving user data. DRF serializers. Add pagination.
Consider caching.
```

### Rule 2: Compress Repetition

**Remove duplicates across multiple explanations of the same concept.**

Example:
```
BEFORE:
- We use JWT for auth (mentioned 3x in different sections)
- Tokens expire after 24 hours (mentioned 2x)
- Database is PostgreSQL (mentioned 2x)

AFTER:
- JWT auth, 24h token expiry
- PostgreSQL
```

### Rule 3: Bullet Lists Over Prose

Convert prose paragraphs to dense bullet lists. Each bullet = one fact.

Example:
```
BEFORE (95 tokens):
The system processes uploads in the background. It accepts PDFs and images.
Files are validated for size (max 10MB) and type. After validation,
they're stored in S3 with a unique ID. The upload is marked complete when
S3 confirms receipt. Users receive a webhook notification.

AFTER (27 tokens):
- Background processing
- Accept: PDF, images
- Validate: size (max 10MB), type
- Store in S3 (unique ID)
- Mark complete on S3 receipt
- Webhook notification
```

### Rule 4: Code Blocks Verbatim

Never compress actual code. Preserve formatting, comments, logic exactly.

Example:
```
BEFORE (verbatim):
def process_payment(amount: float, token: str) -> PaymentResult:
    """Process payment with Stripe API."""
    result = stripe.Charge.create(amount=amount, source=token)
    return PaymentResult(success=result.status == "succeeded")

AFTER (compressed surrounding text, code block untouched):
✅ Process payment via Stripe

def process_payment(amount: float, token: str) -> PaymentResult:
    result = stripe.Charge.create(amount=amount, source=token)
    return PaymentResult(success=result.status == "succeeded")
```

### Rule 5: Reorder by Priority

Put critical information first. Group by category.

Example:
```
BEFORE (random order):
- Nice-to-have: add caching later
- Critical: must support concurrency
- Implementation detail: uses SQLAlchemy
- Critical: data consistency for financial transactions

AFTER:
Critical:
- Support concurrency
- Data consistency for financial txns
- Implement: SQLAlchemy
- Future: add caching
```

## Usage in one-shot-prompting Pipeline

### Phase: ARCHITECT REVIEW (pre-spec)

When architect generates a long spec, compress before handing to implementer:

```bash
/caveman @./spec.json --preserve-code --target-reduction=75
```

Output: `spec-compressed.json` (same structure, denser content)

### Phase: CRITIC LOOP (debug logs)

When critic encounters verbose error logs from tests:

```bash
/caveman @./test-failure.log --preserve-errors --target-reduction=80
```

Output: unique errors only, stack traces intact, no duplicate frames.

### Anytime: Context Window Check

If transcript is getting long:

```bash
/caveman @./long-summary.md --target-reduction=70
```

Output: same facts, fewer tokens, ready to submit next turn.

## Checklist

- ✅ Technical accuracy unchanged (all facts preserved)
- ✅ No code removed or changed
- ✅ No error messages removed (only duplicates stripped)
- ✅ All constraints, requirements preserved
- ✅ Reduced by target % (default 75%)

**[BLOCKED]** If compression removes factual content → revert and try again with `--target-reduction=50`.

---

**Adapted from:** mattpocock/skills (token-compression pattern)

**Last updated:** 2026-05-19
