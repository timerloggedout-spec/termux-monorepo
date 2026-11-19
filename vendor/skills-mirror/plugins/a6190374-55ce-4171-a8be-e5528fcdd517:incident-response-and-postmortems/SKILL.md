---
name: incident-response-and-postmortems
description: Guides live incident handling and blameless postmortems. Use when production is degraded or down, when alerts fire, when customers report outages, or when you need to capture learning after a serious incident.
---

# Incident Response and Postmortems

## Overview

Production incidents are a different problem than local debugging. Time pressure, incomplete information, and multiple stakeholders require a disciplined loop: assess impact, stabilize, communicate, fix, verify recovery, then learn without blame. This protocol covers the operational response and the post-incident review that prevents repeats.

For local test failures and development-time bugs, use `debugging-and-error-recovery` first. Use this skill when users or SLIs are affected in deployed environments.

## When to Use

- Error budgets burned, SLOs breached, or monitoring shows critical degradation
- On-call page, customer reports of outage, or support escalation
- Data loss, security event, or cascading failure in production
- After a significant incident, when a postmortem is required

## When NOT to Use

- Only failing tests or local dev builds (use `debugging-and-error-recovery`)
- Pre-launch checklists and first-time deploys (use `shipping-and-launch`)

## Process

### Phase 1: Triage (first minutes)

1. **Confirm the incident** — What symptom triggered this? Is it still happening?
2. **Assess severity** — User impact (who, how many), data risk, regulatory/security exposure.
3. **Assign roles** — Incident commander (coordinates), comms (status), technical lead (mitigation). On small teams, one person may wear all hats but must name which hat they are wearing.
4. **Open a war room** — Single chat or call; single source of truth for timeline notes.

### Phase 2: Stabilize

1. **Stop the bleeding** — Roll back, toggle feature flag, scale up, block bad traffic, fail over. Prefer reversible changes.
2. **Preserve evidence** — Snapshot logs, metrics, traces, config versions before they rotate away. Note exact times (UTC) and versions deployed.
3. **Avoid untested fixes in prod** — If a hotfix ships, it must have a defined verification step and rollback.

### Phase 3: Communicate

1. **Internal** — Short, timestamped updates: impact, what we know, what we are doing, ETA if possible.
2. **External** — Status page or customer comms: honest, no speculation, next update time.
3. **Escalate early** — If severity is unclear or mitigation stalls, escalate per runbook.

### Phase 4: Resolve and verify

1. **Confirm recovery** — SLIs, synthetic checks, error rates, key user flows.
2. **Monitor for rebound** — Watch the same signals for a defined window after "fixed."
3. **Document timeline** — Detection → actions → resolution with UTC timestamps.

### Phase 5: Postmortem (after stability returns)

Schedule within a few business days for serious incidents.

1. **Blameless framing** — Focus on systems and process, not individuals.
2. **Timeline** — Factual sequence: change, trigger, amplification, detection, response.
3. **Root causes** — Often multiple (technical + process). Use "five whys" sparingly; prefer contributing factors.
4. **What went well** — Detection, rollback, comms that worked.
5. **What went wrong** — Gaps in tests, monitoring, runbooks, assumptions.
6. **Action items** — Each owned, with due date: monitoring, guardrails, docs, code fixes.

Follow `documentation-and-adrs` if architectural lessons belong in an ADR.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "We're too busy for a postmortem" | Without it, the same incident repeats; the next one costs more. |
| "It was human error" | Humans operate systems you designed. Fix the system: guardrails, automation, checks. |
| "Let's skip the status page" | Silence amplifies panic and support load. Brief, honest updates reduce harm. |
| "I'll hotfix without rollback plan" | The hotfix is another deploy risk. Know how to undo it. |
| "Logs will be enough" | Logs rotate; capture pointers, queries, and screenshots now. |

## Red Flags

- Multiple concurrent undeployed fixes with no single coordinator
- Changing production without recording what changed and when
- Closing the incident before error rates or user-impacting metrics recover
- Postmortem that names people instead of systems and processes
- Action items with no owner or no follow-up verification

## Verification

After incident handling:

- [ ] Users or SLIs are back within agreed targets (or explicit exception documented)
- [ ] Timeline and key decisions recorded with UTC timestamps
- [ ] Evidence pointers saved (dashboard links, log queries, deploy versions)
- [ ] Stakeholders notified that service is restored (or status updated)

After postmortem:

- [ ] Document shared with team; action items tracked in work queue
- [ ] Runbooks or alerts updated where gaps were found
- [ ] Related code or infra changes scheduled if remediation requires implementation
