# Foresight Radar

Horizon classification follows an Armasuisse/Envisioning-style scanning model.

This radar turns the daily briefing into a standing horizon-scanning input for `termux-monorepo`.

| Lane | Meaning | Required treatment |
|---|---|---|
| H0 | Confirmed / already material | Act, integrate, or document |
| H1 | Emerging and credible | Validate, prototype, or procurement-scan |
| H2 | Weak signal | Watch and collect evidence |
| H3 | Speculative | Record only when strategically useful |

## Signal dimensions
Each radar record evaluates:
- enabling technologies
- convergence
- bottlenecks
- strategic dependencies
- inspectable FOSS alternatives
- prototype concepts
- procurement implications
- lock-in exposure
- ARM/Linux/Android/Termux relevance

## Record tags
Every candidate is tagged with one or more dimensions:
- enabling technology
- infrastructure
- compute / accelerator
- memory / storage
- energy / thermal
- agent / orchestration
- security / safety
- developer tooling
- FOSS ecosystem
- science / research
- materials / hardware
- procurement / sovereign capability
- interoperability / standards
- mobile / edge / Termux
- supply-chain / provenance

## Rules
- Never convert H2/H3 into fact through repetition.
- A horizon lane is not a confidence score.
- Confidence is evidence quality; horizon is maturity/temporal significance.
- Claims require primary or authoritative evidence where available.
- Contradictory evidence is retained, not silently averaged away.
- Radar Watch may contain H2/H3 signals omitted from the five-item daily briefing.

## Daily five-item selection
Prefer, in order:
1. breaking material developments;
2. important/deep research;
3. practical tools/opportunities;
4. major developments with durable technical consequences;
5. direct monorepo/procurement relevance.

Do not fill an item merely because a category is empty.

Select five items that maximize information value rather than headline volume.
Prefer independent, primary evidence and diversity across radar dimensions.

Each item records:
1. headline
2. horizon lane
3. concise summary
4. evidence status
5. why it matters
6. practical opportunity / procurement implication
7. relevant Termux-monorepo connection
8. primary sources
9. relevant image
10. confidence and unresolved questions
