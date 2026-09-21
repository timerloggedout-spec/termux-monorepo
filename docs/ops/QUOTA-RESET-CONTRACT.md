# Quota / Billing Boundary Contract

## Purpose

This contract separates a **machine-time planning anchor** from an authoritative provider/account quota reset.

GitHub Actions usage is governed by the billing cycle of the account that owns the usage. Included Actions minutes reset at the start of the applicable billing cycle; GitHub also documents monthly included-minute resets for the standard plan allowances. Therefore repository automation must **observe provider state rather than infer a quota reset solely from the calendar**.

## Canonical clock

- Machine timestamps: UTC.
- Workflow schedule declarations: explicit `timezone: UTC`.
- Planning anchor: `monthly@00:00Z`.
- Authoritative quota boundary: `observed/account-defined`.
- Scheduler execution time is evidence, not proof that a provider quota has reset.

## Boundary protocol

```text
RECON
  -> PRE_BOUNDARY_OBSERVE
  -> WAIT
  -> POST_BOUNDARY_OBSERVE
  -> REFETCH
  -> COMPARE
  -> CLASSIFY
  -> RECORD
```

### PRE_BOUNDARY_OBSERVE

Record:

- observed UTC timestamp;
- workflow/run identity;
- repository/ref;
- configured planning anchor;
- provider/account billing-cycle status when an authoritative API exposes it;
- Actions usage evidence available to the workflow.

Do not manufacture a remaining-quota number when the provider does not expose one.

### POST_BOUNDARY_OBSERVE

After the expected boundary, refetch the same evidence surface and compare it with the pre-boundary observation.

Classify the result as one of:

- `RESET_OBSERVED`: authoritative evidence shows a new cycle;
- `NO_RESET_OBSERVED`: evidence is authoritative and still identifies the prior cycle;
- `UNKNOWN`: the provider evidence is unavailable or non-authoritative;
- `SCHEDULER_DELAY`: execution happened later than the intended schedule.

`UNKNOWN` is a valid state. It must not be promoted to `RESET_OBSERVED`.

## Scheduling discipline

The observer intentionally uses non-zero minutes:

- `53 23 28-31 * *` — candidate pre-boundary observation; the job acts only when the next UTC date is the first of a month.
- `7 0 1 * *` — post-boundary observation.

This is a **measurement cadence**, not a claim that every GitHub account's billing period begins at 00:00 UTC.

## Integration rules

1. Keep UTC as the repository-wide machine clock.
2. Keep account/provider billing-cycle state authoritative.
3. Keep the monthly UTC anchor as an operational synchronization point only.
4. Never gate a destructive or expensive operation solely on the assumption that quota has reset.
5. Use WAIT → WATCH → REFETCH → COMPARE before classifying the boundary.
6. Preserve the evidence artifact even when the result is `UNKNOWN`.
