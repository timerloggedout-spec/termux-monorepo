---
name: debugging-discipline
description: Use when the user reports something broken, slow, flaky, or wrong in production or staging ("it's slow", "it crashes", "it doesn't work", "we're seeing 500s", "the data is wrong"). Forces an investigation method instead of guessing. Apply BEFORE proposing a fix. Mandatory the moment someone says "in prod".
---

# Debugging Discipline

When something is wrong, the senior reflex is not "I bet I know what it is". It is "let me see the data". Theorizing without measuring is how a 20-minute incident becomes a 4-hour outage with three bad fixes pushed in panic.

## The Discipline

When a symptom is reported, the order is:

1. **Mode**: active incident (mitigate first, root-cause after) or stable bug (investigate fully, fix once).
2. **Define the symptom precisely**: when did it start, who sees it, what fraction, what is the exact behavior, what is expected.
3. **Identify where to look**: which log, which metric, which DB, which trace, which version. Knowing where is half the fight.
4. **Reproduce**: get the failing case in a place you can poke at. Synthetic if needed.
5. **Bisect**: find the smallest input, state, or change that triggers it.
6. **Hypothesize one thing at a time**: predict what you should see if true, look for it, kill or confirm.
7. **Document as you go**: what you saw, what you tried, what you ruled out. Future you and future on-call will thank you.

Skipping steps is how the wrong fix ships.

## Mode One: Active Incident

Customers are affected right now. The order changes.

1. **Stop the bleed**, not "find the cause". Roll back. Flip the feature flag off. Block the malformed traffic. Reduce blast radius.
2. **Communicate** in real time. A short status note every 15 minutes beats silence followed by a postmortem.
3. **Capture state** before any cleanup. Logs, metrics, query plans, threads. Once you restart, the evidence is gone.
4. **Root-cause after mitigation**. The fix-the-cause work happens once customers are no longer hurt.

The temptation in an incident is to investigate first because you "want to do it right". Do not. The right thing is to stop the harm.

## Mode Two: Stable Bug

Not on fire. You have time. Use it.

1. **Reproduce** in dev or in a test, deterministically.
2. **Write a failing test** that pins the bug. See [[testing-with-discernment]]. This is non-negotiable for any bug worth a fix.
3. **Find the root cause**, not the first suspect.
4. **Fix the cause, not the symptom**.
5. **Add the regression test to the suite**. Bug found once, prevented forever.

## Define The Symptom

The first wrong move is treating a vague report as a fact. "It's slow" is not a symptom. Get specific:

- **When did it start?** A timestamp turns into a deploy window, a config change, a third-party announcement, a spike.
- **Who sees it?** All users, one tenant, one role, one region, one device. Specificity narrows the hypothesis space.
- **What fraction?** 100%, 1%, intermittent. "Intermittent" means there is a discriminator you have not found.
- **What is the exact behavior?** Returns 500, hangs, returns the wrong data, returns the right data late. Each one points at a different layer.
- **What is the expected behavior?** Sometimes the bug is in the expectation.

If you cannot answer those in two sentences, the report is not a bug report; it is a request to do the report yourself.

## Where Before What

Before "what is wrong", answer "where would I see it".

- **Latency issue**: APM traces, slow query log, DB CPU, p95/p99 histograms, third-party latency. See [[observability-by-default]].
- **Error spike**: error rate by route, exception breakdown, recent deploy diff.
- **Wrong data**: which row, which write changed it, which job processed it, which user did it. Reconstruct the timeline.
- **Crash / OOM**: pod events, GC logs, heap dump, dmesg / kernel logs.
- **Intermittent**: per-instance metrics (one bad host), per-tenant (one specific data shape), time-of-day (cron interference).

A senior debugger has a map of where each kind of symptom is visible. Build that map first, run queries second.

## Reproduce Or You Are Guessing

A bug you cannot reproduce is not fixed; it is hidden. Reproduction comes in tiers, in order of preference:

1. **Failing automated test.** Pin the bug as code. See [[testing-with-discernment]].
2. **Manual reproduction in dev**, with notes on exact steps.
3. **Repro in staging with a copy of prod data** when the bug needs realistic state.
4. **Synthetic load** when the bug only appears under concurrency.
5. **Production replay** if you have request capture + replay tooling.

If you cannot reproduce, your "fix" is a prayer.

## Bisect

When a bug appeared between two known-good states, bisect.

- **In code**: `git bisect run` with a script that returns 0 if good, 1 if bad. Cuts log-N commits to localize.
- **In data**: bisect the timestamp range, the tenant set, the input space. Find the smallest example that fails.
- **In config / deploys**: bisect the release.

Bisection turns "no idea" into "the change that did it" in minutes, when it applies.

## One Hypothesis At A Time

Change one variable at a time. Predict what you would see if the hypothesis were true. Then look.

- "If the slow query is the cause, the slow query log shows it." Look. See or do not see.
- "If the timeout is the cause, p99 is at the timeout." Look.
- "If a bad deploy is the cause, the symptom started in the deploy window." Check.

Hypotheses are cheap; the discipline is testing them, not multiplying them.

## Bias Killers

The mistakes that come for everyone:

- **Pattern matching ("we saw this last week, must be the same").** Often wrong, always lazy. Treat each incident fresh, then check the resemblance.
- **"It cannot be X".** Look anyway. Especially the things that "cannot" go wrong are the things nobody checks.
- **"Obviously it is the cache."** Obvious is an instinct; instincts are wrong half the time. Verify before fixing.
- **Confirmation bias.** You see what supports your theory; you skim past what does not. Read the data, not your theory.
- **Survivor bias.** "All the requests I see succeed." Yes, because the failing ones do not reach your log.
- **The first-thing-that-changed**. The deploy was 10 minutes ago, so it is the deploy. Sometimes. Often something else changed in the same window. Check.

## Document While You Go

A running log of what you saw, what you tried, what you ruled out is worth more than the fix itself.

- Future you in 3 months hits the same shape; the log shortcuts the work.
- Future on-call hits a related symptom; the log gives them the trail.
- The post-incident review needs the timeline.

Two sentences per step. Not an essay.

## Anti-Patterns

- **Changing things at random.** "Let me try this" without a hypothesis. You make more states to debug, not fewer.
- **Pushing fixes without a reproduction.** You may be lucky and resolve the symptom; you do not know what you actually did.
- **Restarting first.** Restart hides the evidence. Restart only after capturing state.
- **Blaming the network.** It is occasionally the network. Most of the time, the network is fine and the timeout is wrong.
- **Stopping at the first plausible explanation.** A wrong root cause is worse than no root cause; you ship a misfix.
- **"Works on my machine" as a verdict.** It works on your machine because your state is different. Find the state difference.
- **Big-bang fix.** Multiple unrelated changes in one PR after an incident. If one of them is wrong, you do not know which.
- **Skipping the postmortem.** The incident is the data; the postmortem is the learning. Skip the postmortem, repeat the incident.

## Quick Decision Guide

| Situation | Reflex |
|-----------|--------|
| User says "it is slow / broken in prod" | Define the symptom precisely; do not propose a fix yet |
| Customer impact happening now | Mitigate first (roll back, flag off, throttle); root-cause after |
| Bug reproduces locally | Pin it as a failing test before touching the code |
| Bug does not reproduce | You are not done investigating; you are not fixing |
| Two changes happened in the bad window | Bisect (code, data, config) |
| Multiple plausible causes | One hypothesis at a time, predict, verify |
| About to restart the bad pod | Capture state first (logs, metrics, threads) |
| Tempting to push a "quick fix" | Write the regression test first |

## See also

- [[observability-by-default]] for the data that makes investigation possible
- [[testing-with-discernment]] for the bug-first regression test
- [[query-discipline]] when "slow" turns out to be the DB (often)
- [[idempotency-and-side-effects]] when "we ran it twice" turns into "duplicates"
- [[error-handling-as-design]] for what the logs and codes are telling you
