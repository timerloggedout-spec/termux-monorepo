# Gated Spend Authorizations — protocol of record

Owner spec 2026-11-04 03:32 PT. Custody: Cadence (governor/actuation
layer) = enforcement + reporting mechanics. First application: the Desk.

**Rule:** every limited-resource spend runs under an authorization
object `{resource · objective · cap · release gate · receipts}`.
No authorization, no spend.

## Mandatory elements (owner-named)

1. **PROPOSAL REQUIRED** — no proposal ⇒ no authorization. A proposal
   carries `{objective · competing lanes · estimated spend}` and is
   stamped of record before any authorization can reference it.
2. **ESTIMATED SPEND stamped of record** — the proposal's estimate is
   carried verbatim onto the authorization; actuals reconcile against
   it in every report.
3. **CAPS ENFORCEMENT at the governor/actuation layer** — the cap is
   hard and fail-closed: a release that would push released-total over
   the cap is refused; spend draws only against released funds.
4. **REPORTING** — a hash-chained receipt per release and per spend
   (governor event stream, `que-governor-event/v1`, kind `spend`);
   spend-vs-estimate is reported up per authorization.

## Objects

```json
proposal      {proposal_id, resource, objective, competing_lanes[],
               estimated_spend {amount, unit}, proposed_by, ts,
               state: proposed|authorized|rejected}
authorization {auth_id, proposal_id, resource, objective,
               competing_lanes[], estimated_spend {amount, unit},
               cap {amount, unit},
               release_gate {required_role},
               released_total, spent_total,
               expires_at (resource-bound, e.g. a dated credit),
               overrun_finding (receipt id or null),
               state: active|held|exhausted|expired|revoked|closed,
               authorized_by, ts, receipts[]}
receipt       {receipt_id, auth_id, resource, action:
               authorized|released|spent, amount, cap,
               released_total, spent_total, ts, prev_hash→hash}
```

Roles reuse the actuation layer's table: `owner 3 · desk 2 · lane 1`.
Authorization requires the authorizer's role ≥ the release gate's
`required_role`; each release re-checks the releaser's role against the
gate. Spend records carry a free-text note (what the draw bought).

## Lifecycle (full complement)

```
propose → issue (authorize: cap + gate + expiry stamped)
        → gated release (receipted, tranche by tranche)
        → spend (draw-down tracked against released)
        → reconciliation (estimate-vs-actual, continuous via report)
        → close-out report (terminal)
side exits: overrun ⇒ finding + hold · expiry · revocation
```

- **Issue:** authorization minted only from a `proposed` proposal, by
  a role ≥ the release gate's role; cap, gate, and resource-bound
  `expires_at` are stamped at issue.
- **Gated release:** each tranche re-checks the releaser's role;
  `released_total + release > cap` ⇒ refused (hard cap).
- **Draw-down tracking:** `spent_total + spend > released_total` ⇒
  refused (unreleased funds do not exist); totals + per-receipt
  running balances ride the receipts.
- **Estimate-vs-actual reconciliation:** continuous — `report` renders
  `{estimated · cap · released · spent · remaining_cap ·
  spend_vs_estimate_pct · state · expires_at · overrun_finding}`.
- **Overrun = finding + hold:** the spend that pushes `spent_total`
  past the stamped estimate (the cap still binds absolutely) emits an
  `overrun_finding` receipt and flips the authorization to `held` —
  no further release or spend until a gate-role `unhold`,
  revocation, or close-out.
- **Expiry:** resource-bound (e.g. the first application's credit
  expires ≈ Dec 3 — the Desk stamps the real date at issue); first
  touch past `expires_at` flips state to `expired`, all draws refused.
- **Revocation:** gate-role act; terminal; receipt carries
  `released_unspent`.
- **Close-out report:** gate-role act; terminal; final reconciliation
  `{estimated · cap · released · spent · released_unspent ·
  unreleased_cap · variance_vs_estimate · spend_vs_estimate_pct ·
  overrun_finding · receipts}` sealed by a closeout receipt.
- `spent_total == cap` ⇒ state `exhausted` (draws refused).

## Mechanics of record

`spend_auth.py` (governor custody, beside `governor_actuate.py`):
verbs `propose · authorize · release · spend · unhold · revoke ·
closeout · report`. Store =
`spend-auth.json`; receipts append to the shared governor event stream
and fold into the governor plane with the emitter batches. Verified on
a copied rig (owner rule: synthetic state never touches the live
store): no-proposal authorize refused · under-role release refused ·
over-cap release refused · over-released spend refused · happy path
reconciles (released 120 / spent 95 / estimate 200 ⇒ 47.5%) · expired
authorization refuses draws · overrun spend (150 vs estimate 100)
emits finding rcpt + holds, held spend refused, gate-role unhold
restores · revocation terminal · close-out seals the reconciliation
(variance +50 · 150.0% · released_unspent 350 · unreleased_cap 500).

## First application

The Desk applies this protocol to its limited-resource engagements
(first: the Vultr hackathon credit, parallel lanes competing to
represent the repo — the Desk stamps its own proposal with the real
objective, competing lanes, and estimate; this document invents none).
Each competing lane's draws run as releases + spends under the one
authorization, so the cap binds the field, not per-lane honor.
