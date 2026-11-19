---
name: testing-with-discernment
description: Use when writing, reviewing, or planning tests for any backend code. Forces a "what is worth testing" decision instead of a coverage target. Catches tests that mock the code they claim to test, tests that pass even when the feature is broken, and snapshot tests pretending to be assertions. Apply whenever you are tempted to write a test, and BEFORE marking a bug fix done.
---

# Testing With Discernment

Coverage is not the goal. Confidence is the goal. A 100% covered codebase whose tests all mock the world tells you nothing. A 60% covered codebase with the right tests tells you everything that matters.

## The Discipline

Before adding a test, answer:

1. **What could break here in an interesting way?** Logic with branches, edge cases, state transitions, parsing of external formats, retries, math, money. Test that.
2. **What would the test prevent?** A real regression, a real edge case. If the answer is "nothing specific, just coverage", do not write it.
3. **At what level?** Unit if the thing being tested is pure logic. Integration if it touches the DB, the queue, or the framework. E2E only for the small set of flows that pay rent.
4. **Will it stay fast and deterministic?** No sleep, no network, no time-dependent without freezing time, no random without a seed.

A test that does not answer those is noise. Noise hides signal.

## Where Tests Pay Their Rent

Test densely:

- **Business logic with branches**: pricing, scheduling, eligibility, state machines, retries with backoff, idempotency dedup logic.
- **Parsers and serializers**: anything that consumes external data (CSV, webhook payloads, third-party responses).
- **Boundary code**: validation, authorization decisions, request shaping.
- **Anything that has broken before**: a regression test per bug, forever.

Test thinly or skip:

- **Framework integration plumbing** ("the router routes"). The framework's tests cover this.
- **Getters and setters** with no behavior.
- **Trivial one-liners** with no branching.
- **Boilerplate**: a constructor that assigns fields, a method that delegates.

If you find yourself "writing a test for coverage", stop. Write the production code instead.

## The Pyramid Without Religion

The shape is well-known and roughly right:

- **Many** unit tests. Fast, focused, deterministic. Run them on every save.
- **Several** integration tests. Hit the real DB, the real ORM, the real framework. Run them in CI and locally on demand.
- **Few** end-to-end tests. The small set of customer-visible flows that must not break.

The shape is wrong when teams enforce it religiously ("unit tests must be 80%, integration must be 15%, e2e must be 5%"). The right ratio depends on what your code is. A heavy data-layer app has more integration. A pure-logic library has more unit. Build the shape that matches the risk.

## Integration Over Mocks

For code that touches the DB, an integration test against a real Postgres beats a mocked unit test every time.

- **Mocking the ORM tests the mock.** If the ORM call you wrote does not behave the way the mock said, the test still passes. Your production code breaks anyway.
- **Real DB tests catch real things**: migrations that drift, constraints you forgot, queries that work in dev because they do not under load.
- **Setup cost is real, but bounded.** Use ephemeral containers (testcontainers), transactional rollback per test, or one-shot fixtures. Pay the cost once.

Default position: write integration tests for data-layer code. Mock only what is genuinely outside your control: third-party APIs, time, randomness.

## Tests That Lie

Some tests look green and prove nothing. Spot them.

- **The test that mocks the function it tests.** "I asserted that `chargeCustomer` calls `stripe.charge`." Replaced `stripe.charge` with a mock that records the call. You proved the test setup. The customer is not charged.
- **The snapshot test on everything.** "Match the snapshot." Snapshot becomes the spec. Regenerate when it fails. Untouched for two years.
- **The test that passes even when the feature is removed.** Comment out the production code, run the test. Still green? Test is fake.
- **Coverage with no assertions.** The code runs, no `assert` ever fires. Coverage tool is happy, defect ships.
- **The "it should work" test.** `expect(result).toBeTruthy()` without checking what the result actually is.
- **The mock cascade**. Five mocks chained to make the test pass, more lines of setup than production code. The setup IS the production code by now; the real one is unreachable.

The cure is the inversion question: "If the feature breaks, will this test fail?" If you cannot answer yes with certainty, the test is decoration.

## Bug-First Rule

For every bug worth a fix, the order is:

1. Reproduce as a failing test.
2. Watch it fail for the expected reason.
3. Fix the production code.
4. Watch it pass.
5. Commit the test alongside the fix.

The test becomes the regression net. The bug is not fixed twice.

If the bug is hard to reproduce in a test, that is information: the design makes the bug hard to reach, which usually means it is also hard to detect in prod. See [[debugging-discipline]] for the broader investigation method.

## Speed And Determinism

A slow test suite is an unrun test suite. A flaky test suite is an ignored test suite. Both ship bugs.

- **No `sleep`**. Replace with deterministic waits (poll a condition, react to an event).
- **No network**. Stub at the HTTP boundary or use a recorded fixture.
- **No real time**. Freeze the clock, inject the time provider.
- **No real randomness**. Seed the RNG.
- **Parallelizable.** Tests do not share global state; each one cleans up.
- **Order-independent.** Shuffle the suite; it should still pass.

Flaky tests rot the suite. A flaky test is either fixed today or deleted today.

## The CI Contract

What runs where, and why:

- **Unit + fast integration**: on every push, finishes in a couple of minutes.
- **Full integration**: on pull request, finishes in under ten minutes.
- **E2E**: on main / pre-deploy, finishes in under thirty minutes, and is allowed to be selective (smoke tests for every deploy, full suite nightly).

If the suite is too slow, the team starts skipping it. The fix is splitting, not "we'll run it less".

## Anti-Patterns

- **Coverage as a KPI**. Teams hit the number with tests-of-tests. Track regression escape rate instead.
- **Snapshot tests instead of assertions.** Snapshots are fine for output formatting (HTML, JSON-LD). They are not a substitute for "this function returned the right value".
- **E2E for everything.** A 30-minute E2E suite that runs on every PR is a velocity tax. Use unit + integration for behavior; reserve E2E for the small set of customer-critical paths.
- **Tests that depend on each other.** Test B passes only after Test A ran. Run B alone, it fails. The suite is a house of cards.
- **Production-coupled fixtures.** Loading a 200MB SQL dump for every test. The setup is now the bottleneck.
- **"100% line coverage" myth.** Lines covered != branches covered != bugs caught. Branch coverage is the better proxy, and it is still a proxy.
- **Asserting implementation, not behavior.** "It calls `internalHelper` three times." If the refactor uses a different helper to produce the same result, the test fails for nothing.

## Quick Decision Guide

| Situation | Reflex |
|-----------|--------|
| New business logic with branches | Unit test, one assertion per branch |
| New endpoint | Integration test against real DB |
| New parser / serializer | Property-based test if possible, fixture tests otherwise |
| Bug fix | Failing regression test first, then fix |
| Code talks to a third party | Stub at the HTTP boundary, contract-test the integration separately |
| Code depends on time | Inject a clock; freeze in tests |
| Code is random | Seed it |
| Adding mocks | If you mock the thing you test, write an integration test instead |
| 80% coverage feels mandatory | Track regression rate; ignore the percentage |
| Flaky test | Fix today or delete today |

## See also

- [[debugging-discipline]] for the bug-first investigation method
- [[error-handling-as-design]] for the error paths that deserve tests
- [[idempotency-and-side-effects]] for the replay scenarios that deserve tests
- [[query-discipline]] for data-layer code that deserves integration tests
