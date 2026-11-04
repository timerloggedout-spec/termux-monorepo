# D1 Strands Alternatives Matrix — 2026-11-04

Owner order 2026-11-04 05:23 PT: an AWS alternative for Strands is needed
for D1 (StudySprint). Spec asked of Main + Challenge Manager (Desk);
free-provider recon tasked to Recon; this matrix is kept documented and
maintained by the enumeration lane as findings land.
Clock: descope edit default-fires 21:00 PT · submission freeze
2026-11-04 23:59 PT.

## Governing standard (DoE, of record)

A Strands/AWS claim is proven iff the shipped agent executes with the
model served by Bedrock — real invocation, real account
(constructed-but-never-called = no proof) — and the receipt names
{provider=amazon-bedrock · model id verbatim · region · tools ·
run/commit/sdk}. The #4534 run (Gemini route, gemini-3.5-flash-lite)
is stamped DEFECT under this standard: retained in the trail, never
cited as proof. Judging weights (event Rules): Functionality 35 ·
Innovation 25 · Strands/AWS 15 · Originality 25.

## Spec — Desk (Challenge Manager) answers, 2026-11-04 05:25 PT

- Claim wording = FULL Strands/AWS claim (owner ruling 05:17 PT:
  Strands LIVE IN THE RELEASES — endpoint live Lambda x BedrockModel
  Nova · surfaces opt-in live mode · receipts deployment=true with
  Bedrock fields). Reduced wording = branch (b) descope = claims
  floor only (the default-fire), not the target.
- Evidence form = the DoE conforming receipt ONLY {provider=
  amazon-bedrock · model id verbatim · region · tools · sdk version}
  + run/commit stamps. No other form is accepted for the claim.
- Timing: a conforming receipt by 21:00 PT is THE gate. No receipt
  at 21:00 = (b) executes. A receipt landing 21:00–23:59 could only
  re-open (a) on a fresh D1 ruling inside edit + re-verify margin —
  NOT pre-authorized.
- Editability covers the fields: verified firsthand 2026-11-03 —
  projects editable to the end date, no anti-edit clause in the
  Rules, no provider lock named; claim + endpoint edits already
  exercised post-publish. The binding constraint is the proof
  standard + claim honesty, not event editability.
- Desk stamps: A6 prepaid = card-class = CLOSED (never routed).
  B-class free-provider backends = ruled OUT for the claim by
  AWS-STRANDS-ONLY; B-class survives as transport only, not as an
  alternative row for the claim.

## Spec questions — Main, PENDING (asked 2026-11-04 ~05:25 PT)

- Does the no-card rule and owner-hand steps (P1-class) bound all
  candidates as the Desk answers imply? Any Main-side constraint
  beyond the Desk set?

## Matrix A — AWS routes

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| A1 | BedrockModel swap into the proven #4534 harness, new Free-plan account; model us.amazon.nova-lite-v1:0, region us-east-1 | none for most new customers (AWS start-here, verified 2026-11-04) | P1 signup, owner hand, PENDING | Full receipt standard satisfiable (Bedrock invocation, tools from event stream) | PRIMARY — blocked on P1 only |
| A2 | Lambda x Bedrock Nova hosted shape (AWS schema set, issue #4537) | same account dependency as A1 | same as A1 | Receipt standard satisfiable; hosting is not a spec field | TARGET CLAIM SHAPE per owner ruling 05:17 PT: endpoint live Lambda x BedrockModel Nova, receipts deployment=true; A1 is its proof vehicle |
| A3 | Workshop Studio / Event Engine account | none (event-issued) | event access | Weak: not the owner's account; credentials temporary | NO as proof route — accounts expire at event end, resources auto-deprovisioned (aide probe 2026-11-04, AWS workshop pages) |
| A4 | AWS Activate credits | n/a (post-account) | application, owner hand | None at signup; usage offset only after an account exists | Not a door — possible subsidy after A1; eligibility NOT_ESTABLISHED |
| A5 | Promo / credit codes at signup | n/a | none | None: redemption requires an existing account (AWS Promotional Credit Terms, upd. 2026-09-24) | NO — post-account usage only |
| A6 | Prepaid network card as payment method | card-class | owner decision only | Satisfies a payment step where one exists (AWS re:Post accepted payment methods, upd. 2026-09-30) | CLOSED, never routed (Desk stamp 2026-11-04) — card-class under the fleet no-card rule; gift cards + virtual credit cards are NOT accepted by AWS at all |

## Matrix B — free-provider Strands backends (non-AWS)

Ruled OUT for the claim by AWS-STRANDS-ONLY (Desk spec 2026-11-04):
B-class survives as transport only, not as alternative rows for the
claim. Recon (Recon lane) re-scoped to transport value 2026-11-04.

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| B1 | Gemini model via the fleet Gemini route (Strands native provider) | none (fleet API key provisioned) | none | Honest receipt for a Gemini-served run; cannot satisfy the Bedrock standard | OUT for the claim. Built + ran as #4534 (DEFECT for the AWS claim). Transport/dev-test use only |

## Owner-gated opportunities (defined)

- G1 — P1 Free-plan signup (owner hand, in flow). Unlocks A1/A2.
  Known unknowns are in-flow only: cohort eligibility (the Free plan
  is new-customers-only; an existing or former AWS account makes the
  customer ineligible per the 2026-10-08 Builder article) and the
  class of the Nov-03 Builder-ID shell (G2).
- G2 — Nov-03 Builder-ID shell completion attempt (owner hand).
  Branches: if the shell counts as an existing account, completion
  routes to the Paid plan and a payment step IS reached ("If you are
  ineligible for the Free Tier or Free plan, you'll need to provide
  payment information, and you'll be placed on the Paid plan" — AWS
  start-here); if it is a resumable incomplete signup under the new
  flow, the no-card path may complete without one. Class =
  NOT_ESTABLISHED in public docs; resolves only in flow.
- G3 — AWS Activate application (owner hand, post-account).
  Credit route that can cover third-party Bedrock models; startup
  eligibility for this fleet NOT_ESTABLISHED.
- G4 — Card-class lift (owner decision only). A prepaid or credit
  instrument would satisfy any AWS payment step (gift/VCC excluded by
  AWS itself). Fleet rule: card-gated = closed class absent an
  explicit owner lift. Defined here; not pursued by any lane.
- G5 — Classic AWS account creation (paid path). Long-standing
  owner-approval gate in fleet record; in practice superseded by G1
  if the Free-plan flow completes.

## Maintenance log

- 2026-11-04 ~05:20 PT — aide returns folded in: R3 persistence probe
  (A3), promo-code terms (A5), accepted-payment-methods (A6),
  free-plan flow verification (A1), shell branch logic (G2).
- 2026-11-04 ~05:25 PT — spec asked of Main + Desk; free-provider
  recon tasked to Recon. Rows update as returns land.
- 2026-11-04 05:25 PT — Desk spec answers folded in (claim = FULL;
  receipt-only evidence; 21:00 PT = the gate, late receipt NOT
  pre-authorized to re-open; editability covers the fields). A2
  stamped target claim shape; A6 stamped CLOSED (never routed);
  B-class ruled out for the claim, transport only; Recon re-scoped.
