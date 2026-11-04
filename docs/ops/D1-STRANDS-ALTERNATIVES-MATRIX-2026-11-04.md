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

## Spec questions — PENDING (asked 2026-11-04 ~05:25 PT)

- Main: does the Bedrock receipt standard bind every alternative, or
  is the alternative a claim-shape change? Must the Strands/AWS leg
  (15) be preserved fully, partially, or is loss accepted? Do the
  no-card rule and owner-hand steps (P1-class) bound all candidates?
  Deadline: before the 21:00 PT descope default, or editable to the
  freeze?
- Desk (Challenge Manager): claim wording the alternative must
  support on the published pages (full / reduced / none); evidence
  form the event side accepts; whether provider substitution inside
  the edit window is within the editability ruling.

## Matrix A — AWS routes

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| A1 | BedrockModel swap into the proven #4534 harness, new Free-plan account; model us.amazon.nova-lite-v1:0, region us-east-1 | none for most new customers (AWS start-here, verified 2026-11-04) | P1 signup, owner hand, PENDING | Full receipt standard satisfiable (Bedrock invocation, tools from event stream) | PRIMARY — blocked on P1 only |
| A2 | Lambda x Bedrock Nova hosted shape (AWS schema set, issue #4537) | same account dependency as A1 | same as A1 | Receipt standard satisfiable; hosting is not a spec field | Variant of A1 |
| A3 | Workshop Studio / Event Engine account | none (event-issued) | event access | Weak: not the owner's account; credentials temporary | NO as proof route — accounts expire at event end, resources auto-deprovisioned (aide probe 2026-11-04, AWS workshop pages) |
| A4 | AWS Activate credits | n/a (post-account) | application, owner hand | None at signup; usage offset only after an account exists | Not a door — possible subsidy after A1; eligibility NOT_ESTABLISHED |
| A5 | Promo / credit codes at signup | n/a | none | None: redemption requires an existing account (AWS Promotional Credit Terms, upd. 2026-09-24) | NO — post-account usage only |
| A6 | Prepaid network card as payment method | card-class | owner decision only | Satisfies a payment step where one exists (AWS re:Post accepted payment methods, upd. 2026-09-30) | Closed class under the fleet no-card rule unless the owner lifts it; gift cards + virtual credit cards are NOT accepted by AWS at all |

## Matrix B — free-provider Strands backends (non-AWS)

Status: recon tasked to Recon 2026-11-04; rows land on return.

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| B1 | Gemini model via the fleet Gemini route (Strands native provider) | none (fleet API key provisioned) | none | Honest receipt for a Gemini-served run; cannot satisfy the Bedrock standard | Built + ran as #4534; DEFECT for the AWS claim. Value = working agent + honest non-AWS claim; cost = Strands/AWS leg (15) lost or reduced; pairs with the descope branch |

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
