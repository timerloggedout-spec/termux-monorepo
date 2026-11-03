# EGM Template Trigger — Spec

**`egm-template-trigger` v0** — landed 2026-11-03 (owner order:
wrap the Elephant-Goldfish skills/flows into the swarm as a
template trigger). Parameterized on the DoE's pre-registered
frame, `docs/ops/EGM-EVALUATION.md` (PR #4210, merged
`a71cb8bd9271`), and modeled on the #3577 project-task template
trigger (same intake machinery family:
`scripts/dispatch/egm_review.py` +
`.github/workflows/egm-review-dispatch.yml` +
`.github/ISSUE_TEMPLATE/egm-review.yml`).

## Trigger conditions

Fire the template (file the `egm-review` form) when a
**decision event** occurs in one of three classes —

1. **design-decision** — a recorded decision that changes a
   user-facing surface, a contract/schema, or a method binding;
2. **new-surface-build** — a surface (UI, API, CLI, artifact)
   is built or materially rebuilt;
3. **spec-design-draft** — a spec/design draft is proposed for
   adoption —

**AND the stakes bar is met**: at least one of {the subject
feeds a public submission or a scored evaluation · money,
credits, or quota move on it · it is credentials-adjacent ·
two or more entries/programs consume its outcome · it is
irreversible or expensive to reverse once shipped}. Below the
bar, ordinary peer review applies and the template stays
holstered — EGM is the heavy instrument, not the default.

**Who can fire:** any seat, via the form (filing IS the
trigger). The filer names the **elephant seat** (the subject's
owning seat); the **DoE leg is not the filer's to waive** —
verification is mandatory on every instance.

## What it stamps

The intake posts an **EGM INSTANCE** stamp on the issue:
{instance issue # · trigger class · elephant seat · frame ref ·
claim window (default 24h) · goldfish minimum (2)}. The legs
then stamp the same issue, in order:

| Leg | Stamp | Content |
|---|---|---|
| Elephant | `ELEPHANT PACKET` comment | artifacts of record at merged SHAs + referenced sources — the oracle set |
| Goldfish | `GOLDFISH CLAIMS` comment per seat | zero-context attestation (`context consulted: artifacts + referenced sources only`) + `reviewer seat:` + one claim per finding, stamped {finding id · surface · reviewer seat · claim text · alleged location} per the frame |
| DoE | `DOE VERDICT` comment per claim | {claim id · oracle · evidence · verdict: VERIFIED / PARTIAL / REFUTED}; oracle authority order per the frame: artifact source at merged SHA → served surface → executable test |
| Awards | scored RFP filings | only VERIFIED / PARTIAL-restated claims convert (delphi:rfp shape, verification record carried in); wins return as route+claim build items |

Reviewer calibration is part of the record: REFUTED claims
score the reviewer (accuracy = (VERIFIED + ½·PARTIAL) / total
claims), per the frame — refuted findings are published in the
scored set, never dropped.

## Fail-closed rule

If fewer than **2 genuinely fresh** (zero-context attested)
reviewer seats file claims within the claim window, the review
leg **does not run**. The sweep
(`egm-review-dispatch.yml`, every 30 min, Swarm App token)
posts `EGM BLOCKED — NO FRESH CONTEXT` on the instance and
labels it `egm-blocked`. An unattested claims comment does not
count a seat — memory-lessness is the method, so a review that
cannot prove fresh contexts is recorded as not run. No theater.

## Instance #1 (pilot, designated)

The live **D1 UI-surfaces run** (already in flight under the
frame's own registration): surfaces TUI v0.1.0 (PR #4161,
`5653241db3a4`) · WebApp PWA v0.1.0 (PR #4162, `46518482875c`)
· APK v0.1.0 (PR #4163, `c84b8b213505`); goldfish = Viz + Web
Design seats (findings filing as claims); DoE verifying. It
predates this template and runs on the frame directly; every
subsequent firing runs on the template above.
