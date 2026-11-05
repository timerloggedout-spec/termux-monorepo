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

## Spec — Main requirements, 2026-11-04 05:27 PT

Definition: an alternative = another AWS route to the SAME claim;
anything else = a descope candidate. Classes for all rows:
A = AWS-proof · B = claim-shape/descope · C = owner-gated AWS.

- The DoE standard BINDS Classes A/C: BedrockModel actually invoked
  on a real AWS account; receipt {provider=amazon-bedrock · model id
  verbatim · region · tools_called · run id + commit + sdk}.
  Non-Bedrock execution never discharges the AWS claim; Class B rows
  are labelled SDK-seam/non-AWS and carry no Strands/AWS proof
  language.
- Judging target: preserve the Strands/AWS leg (15) FULLY. Partial
  preservation = ranked fallback only, with the evidence basis stated
  (judge credit is never assumed). Loss is accepted ONLY if the
  owner picks descope (b).
- Constraints: no-card stands — card-gated routes are Class C
  listings only, never fleet-attempted. Owner-hand steps are allowed
  P1-class only {single · short · exact step · unlocks stated ·
  latest-time stated}. Every owner-gated row must define {gate type ·
  exact owner action · card/cost · unlock · class · latest time ·
  fallback if refused} — an undefined row is an invalid row.
- Cutoff: conforming receipt by 21:00 PT, else descope (b)
  executes; freeze 23:59 PT absolute.

## Matrix A — AWS routes

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| A1 | BedrockModel swap into the proven #4534 harness, new Free-plan account; model us.amazon.nova-lite-v1:0, region us-east-1 | none for most new customers (AWS start-here, verified 2026-11-04) | P1 signup, owner hand, PENDING (gate G1) | Full receipt standard satisfiable (Bedrock invocation, tools from event stream) | Class A — PRIMARY, blocked on gate G1 only |
| A2 | Lambda x Bedrock Nova hosted shape (AWS schema set, issue #4537) | same account dependency as A1 | same as A1 (gate G1) | Receipt standard satisfiable; hosting is not a spec field | Class A — TARGET CLAIM SHAPE per owner ruling 05:17 PT: endpoint live Lambda x BedrockModel Nova, receipts deployment=true; A1 is its proof vehicle |
| A3 | Workshop Studio / Event Engine account | none (event-issued) | event access | Weak: not the owner's account; credentials temporary | Class A — FAILS the standard (not an own real account; ephemeral): accounts expire at event end, resources auto-deprovisioned (aide probe 2026-11-04, AWS workshop pages) |
| A4 | AWS Activate credits | n/a (post-account) | application, owner hand (gate G3) | None at signup; usage offset only after an account exists | Class C listing — not a door; possible subsidy after A1; eligibility NOT_ESTABLISHED |
| A5 | Promo / credit codes at signup | n/a | none | None: redemption requires an existing account (AWS Promotional Credit Terms, upd. 2026-09-24) | NO row — ruled out entirely (not a class); post-account usage only |
| A6 | Prepaid network card as payment method | card-class | owner decision only (gate G4) | Satisfies a payment step where one exists (AWS re:Post accepted payment methods, upd. 2026-09-30) | Class C listing ONLY, never fleet-attempted (Desk stamp: CLOSED, never routed) — card-class under the fleet no-card rule; gift cards + virtual credit cards are NOT accepted by AWS at all |
| A7 | PartyRock (Bedrock playground apps) | none | none | None for the claim: Bedrock-executed but no hosting of the shipped agent (Recon return 2026-11-04) | Class A — FAILS (cannot execute the shipped agent; auxiliary only) |
| A8 | AWS Studio Lab | n/a | n/a | None — new signups closed 2026-07-30 (Recon return 2026-11-04) | DEAD — ruled out |
| A9 | SageMaker Studio social sign-in on-ramp (What's New 2026-10-15) | none for most (Free-plan flow) | owner-hand social sign-in (P1-class, gate class = G1/G2) | Full receipt standard satisfiable IFF the auto-created Studio execution role holds bedrock:InvokeModel — NOT_ESTABLISHED in public docs (preconfigured perms documented SageMaker-scoped; $100 credits described SageMaker-scoped); settles by a 3-cell in-flow probe (sts identity · list-foundation-models · one tiny Nova invoke) | Class A CANDIDATE — account class ESTABLISHED real (flow creates a new AWS account on the Free plan; not event/temp); sign-in = signer's own social identity (owner's GitHub-bound Builder ID); post-sign-in Studio is a browser IDE, fleet-drivable via live session; end-to-end = pending the ② probe |

## Matrix B — free-provider Strands backends (non-AWS)

Ruled OUT for the claim by AWS-STRANDS-ONLY (Desk spec 2026-11-04):
B-class survives as transport only, not as alternative rows for the
claim. Per Main spec 2026-11-04, Class B rows are descope candidates:
labelled SDK-seam/non-AWS, carrying no Strands/AWS proof language.
Recon (Recon lane) re-scoped to transport value 2026-11-04.

| # | Route | Card gate | Owner gate | Evidence producible | Verdict / status |
|---|-------|-----------|------------|---------------------|------------------|
| B1 | Gemini model via the fleet Gemini route (Strands native provider) | none (fleet API key provisioned) | none | Honest receipt for a Gemini-served run; cannot satisfy the Bedrock standard | OUT for the claim. Built + ran as #4534 (DEFECT for the AWS claim). Transport/dev-test use only |

### Transport inventory (Recon return, 2026-11-04 — dev-test loops and non-claim traffic only)

Receipt honesty for all transport rows: receipts can name {provider
verbatim · model verbatim · tools · run · commit · sdk}; region =
none (non-AWS APIs expose no region — stamp the endpoint, not a
region); execution class is never live-production for claim purposes.

| # | Provider | Free terms / card gate | Strands path | Fleet state |
|---|----------|------------------------|--------------|-------------|
| T1 | Gemini (= B1 route) | free tier volatile (~20 RPD worst case on 2.5-flash lines; Flash-Lite classes larger); no card | native GeminiModel | PROVISIONED (vault key + fleet Actions secret; #4534 live proof) — transport rank 1, already wired |
| T2 | Groq | free plan permanent, no card ("developer tier is free, requires no credit card... rate-limited, not time-limited"); gpt-oss-120b 30 RPM / 1,000 RPD / 200K TPD | OpenAI-compatible endpoint via OpenAIModel/LiteLLM | key provisioned = NOT_ESTABLISHED (registry = metadata only) |
| T3 | OpenRouter | :free models, no card: 20 RPM · 50 RPD shared (1,000 RPD only after a $10 purchase = payment, so the base tier is the free fact) | OpenAI-compatible/LiteLLM | NOT_ESTABLISHED |
| T4 | GitHub Models | no card, rides the existing GitHub identity: low tier 15 RPM/150 RPD · high tier 10/50; ToS = experimentation-only (fits dev-test exactly, bars production transport) | OpenAI-compatible | rides the fleet PAT; models:read scope on the helper token = NOT_ESTABLISHED |
| T5 | Mistral | free (Experiment) tier; exact current limits NOT_ESTABLISHED this pass | native MistralAIModel | PROVISIONED (fleet key verified live, 55 models, 2026-11-02 record) |
| T6 | SambaNova | free tier exists ONLY while no payment method is linked (20 RPM/20 RPD, test-scale); one source flags payment-details-upfront = CONTESTED, treat as fragile | OpenAI-compatible/LiteLLM | NOT_ESTABLISHED |

Closed / ineligible (transport): Cerebras = CLOSED CLASS — free
tier converted Oct 2026 to a card-required trial ($5 credits,
30-day expiry), stamped card-gated, out. Anthropic-direct /
OpenAI-direct = no free API tier exists, transport-ineligible.

## Owner-gated opportunities (Class C — fully defined per Main spec)

Every row defines {gate type · exact owner action · card/cost ·
unlock · class · latest time · fallback if refused}. Working margin
(lane-set, not a spec quote): the conforming receipt must exist by
21:00 PT, so account gates target completion by ~20:00 PT to leave
run + receipt margin.

- G1 — P1 Free-plan signup (unlocks A1/A2). Gate type: owner-hand
  signup, P1-class {single · short · exact step}. Exact action:
  complete the new Builder-ID Free-plan signup (register via
  GitHub/Google/Apple/email, create the Free-plan account).
  Card/cost: no card for most new customers; $0 ($200 credits;
  a $1 verification hold is the documented exception). Unlock:
  a real AWS account — A1 proof run + A2 Lambda endpoint. Class: C.
  Latest time: ~20:00 PT today (receipt gate 21:00 PT). Fallback if
  refused/not completed: descope (b) executes at 21:00 PT.
  In-flow unknowns: cohort eligibility (Free plan is
  new-customers-only; an existing or former account = ineligible,
  Builder article 2026-10-08) and the Nov-03 shell's class (G2).
- G2 — Nov-03 Builder-ID shell completion attempt (may unlock
  A1/A2 without a fresh signup). Gate type: owner-hand in-flow
  attempt, P1-class. Exact action: sign in with the Builder ID and
  resume/complete the Nov-03 shell under the new flow. Card/cost:
  branch-dependent — $0/no card if the shell resumes on the Free
  plan; if it routes to the Paid plan ("you'll need to provide
  payment information, and you'll be placed on the Paid plan" —
  AWS start-here), STOP: completing it then needs gate G4. Unlock:
  possibly a live account with no fresh signup. Class: C. Latest
  time: attempt first (cheapest probe); by ~20:00 PT today.
  Fallback: fresh signup via G1, else descope (b). Shell class =
  NOT_ESTABLISHED in public docs; resolves only in flow.
- G3 — AWS Activate application (subsidy for A4). Gate type:
  owner-hand application, post-account. Exact action: apply for
  AWS Activate with the account linked to the Builder ID.
  Card/cost: no card, no cost. Unlock: credit coverage incl.
  third-party Bedrock models (post-account usage only). Class: C.
  Latest time: only meaningful once G1/G2 lands an account; not on
  today's critical path to the 21:00 PT receipt. Fallback if
  refused/ineligible: A1/A2 proceed on Free-plan credits (Nova is
  first-party; documented as credit-covered). Eligibility for this
  fleet: NOT_ESTABLISHED.
- G4 — Card-class lift (unlocks A6 + the Paid-plan branch of G2/G5).
  Gate type: owner decision + owner-supplied instrument. Exact
  action: the owner provides/uses a prepaid or credit payment
  instrument himself (gift cards + virtual credit cards are not
  accepted by AWS at all). Card/cost: a card IS the instrument;
  cost = any AWS charges beyond credits. Unlock: satisfies any AWS
  payment step (Paid plan). Class: C — listing only, NEVER
  fleet-attempted. Latest time: before the proof run it would
  unlock; ~20:00 PT today. Fallback if refused: G1 free-plan path,
  else descope (b).
- G5 — Classic AWS account creation, paid path. Gate type: owner
  approval + owner-hand classic signup. Exact action: create a
  classic AWS account on the Paid plan with a payment method.
  Card/cost: card required (depends on G4 unless the owner acts
  directly). Unlock: A1/A2 with no Free-plan eligibility
  constraints. Class: C. Latest time: ~20:00 PT today. Fallback:
  descope (b). Note: in practice superseded by G1 if the Free-plan
  flow completes.

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
- 2026-11-04 05:27 PT — Main spec folded in: alternative = another
  AWS route to the same claim; classes A/B/C applied to all rows
  (A3 fails Class A; A5 = no row; A4/A6 = Class C listings; B =
  descope candidates, SDK-seam/non-AWS labels); judging target =
  preserve the 15 leg FULLY (partial = ranked fallback with stated
  evidence basis; loss only on owner-picked descope); owner gates
  G1–G5 redefined to the full field set {gate type · exact action ·
  card/cost · unlock · class · latest time · fallback}.
- 2026-11-04 05:30 PT — Recon free-provider return folded in
  (transport only, per re-scope): transport inventory T1–T6
  (Gemini + Mistral provisioned; Groq/OpenRouter/GitHub Models/
  SambaNova with terms + NOT_ESTABLISHED fleet states), Cerebras
  stamped CLOSED CLASS (card-required trial since Oct 2026),
  Anthropic/OpenAI-direct ineligible (no free API tier), transport
  receipt-honesty rules (region = none, stamp endpoint). AWS-side:
  A7 PartyRock (Class A fails — no agent hosting), A8 Studio Lab
  (dead — signups closed 2026-07-30).
- 2026-11-04 17:04 PT — urgent aide task (owner escalation: (a)
  mandatory, (b) held): Studio on-ramp verification returned to the
  D1 seat — ① social sign-in ESTABLISHED (own identity) · ② role
  Bedrock perms + credit scope NOT_ESTABLISHED, 3-cell in-flow probe
  specified · ③ account class ESTABLISHED real (new Free-plan
  account, not event/temp) · ④ sign-in owner-hand, Studio driving
  fleet-drivable, end-to-end pending ②. Filed as row A9.
