# Wagertome / WagerDome — Public Wallet & Participation Lane Blueprint

**Status:** PROPOSAL ONLY · OWNER AUTHORIZATION REQUIRED · NO RUNTIME CHANGE  
**Prepared:** 2026-11-17  
**Target surface:** `apps/tribute-dashboard/wagering-book.html` (canonical existing page; do not create a duplicate `WagerBook.html`)  
**Brand authority:** `Wagertome` = book/record; `WagerDome` = arena/venue mark (held; no arena surface of record yet).  
**Repository:** `timerloggedout-spec/termux-monorepo`

## 1. Executive decision

Upgrade the existing Wagering Book into a clear Wagertome record experience and define a separately governed public-wallet/onboarding lane. Keep the current book publication contract intact.

This document does **not** authorize opening public entries, creating external positions, wallet movement, real-money activity, external wagering, or changing the #407 trading freeze. The current owner ruling (2026-11-02) authorizes a public **read-only** rendering of the private internal ledger and explicitly keeps entries internal, stakes observational, external participation closed, and the public surface without an entry/position path.

Accordingly:

- The existing Wagertome page remains read-only until a superseding owner ruling is recorded.
- WagerDome remains a reserved/held arena mark. No production arena, event, contest, or wager surface is implied by this blueprint.
- Wallet connection, identity binding, participant registration, public submissions, and wallet-linked records are proposed capabilities only. They must not be wired into the current book or deployed before their own authorization and gates pass.
- No private key, seed phrase, recovery phrase, signing key, or custody secret may be requested, transmitted, stored, logged, or handled by this system.

## 2. Authority and source-of-truth hierarchy

| Concern | Authority | Consumer rule |
|---|---|---|
| Book subjects, expectation records, positions, settlements | `ops/agentic-gambling/book/challenges-book.json` + append-only `ledger.jsonl` | These remain the internal records of record |
| Public book projection | `ops/agentic-gambling/book/book-feed.json` | Read-only publication feed; no authority to mutate book state |
| Dashboard projection | `ops/moneyball/wagering-book.json` → `apps/tribute-dashboard/data/wagering-book.json` | Generated projection only; exact mirror parity required |
| Book rendering | `apps/tribute-dashboard/wagering-book.html` | Render supplied values; never infer, score, estimate, settle, or write |
| Wallet ledger | Existing MoneyBall wallet-ledger authority in its owning repository | Read by reference only where authorized; never create a competing wallet ledger |
| Naming | `docs/ops/AGENT-MONIKERS.md` + Registry provenance | Wagertome and WagerDome retain separate meanings |
| Participation policy | Owner ruling + Agentic Gambling Lane charter + DoE gates | New participation is blocked until the authority is explicitly superseded |

No dashboard JSON, browser state, wallet provider response, or third-party index can become the book or wallet source of truth.

## 3. Existing conformity gates — non-regression contract

### B1 — One expectation record per subject
Exactly one expectation record belongs to each subject. Positions cite that subject record. Do not create per-position estimates or parallel probability fields.

### B2 — Basis cited
Every position must name its information basis and source artifact/reference. An uncited basis is invalid and does not open.

### B3 — Settlement from record of record only
Settlement comes only from the subject's named `record_of_record`. Other sources may be evidence legs into the expectation record, never alternate settlement authorities. Settlement remains subject to the existing dual-gate.

### B4 — Private ledger first / publication boundary
Current ruling: the private append-only ledger remains unchanged; entries remain internal; stakes remain observational; external participation remains closed. Public publication is read-only and must expose no entry/position path. Any public wallet or participant write path requires a new, explicit owner ruling and a separate DoE conformity review. This proposal is not that ruling.

### B5 — Rule 9 and significance
Any probability or standing statement must satisfy Rule 9 and the significance standard. Single-leg claims remain HELD; sub-bar claims receive no established standing language. Hidden `metrics_internal.winprob` values remain in their own home and are not republished by the book.

### R1 — Values verbatim
Published values equal the authoritative ledger/book values. The renderer does not calculate, rewrite, round, or re-estimate authoritative values.

### R2 — True state
INTAKE/null priors and posteriors render as held. Null is not zero and must not be interpolated, hidden, or dressed as an estimate.

### R3 — Read-only means read-only
The public book has no entry, position, settlement, transfer, or mutation path. A visual affordance must never imply an action is available when the backend authority does not exist.

### Projection parity
For every refresh:
1. Upstream book feed and generated dashboard projection reconcile by stable subject IDs.
2. Positions, feed settlements, publishability flags, expectation values, settlement source/value, and record-of-record fields match their source.
3. `ops/moneyball/wagering-book.json`, `apps/tribute-dashboard/data/wagering-book.json`, and the checked fixture are byte-identical where the established pipeline requires it.
4. The page fetches only its generated local projection.
5. Freshness is stamped at generation; age greater than 48 hours is visibly STALE.
6. The generator must not silently replace missing or malformed values with zero, healthy, or complete.

## 4. WagerTome experience upgrade

The existing `wagering-book.html` is the canonical implementation target. Do not fork it into a second page.

### 4.1 Product information architecture

- **Wagertome — Book:** authoritative read-only record projection.
- **Subjects:** stable subject ID, label, family, open date, deadline/knowable rule, and named settlement authority.
- **Expectations:** prior, basis, evidence count, posterior, range, and explicit INTAKE/no-estimate state.
- **Positions:** only positions present in the authorized publication feed; show observational unit and cited basis.
- **Settlements:** source, outcome/value, timestamp, and affected positions as supplied.
- **Timeline:** Gantt derived from feed anchors; unknown dates remain open-ended, never invented.
- **Integrity & freshness:** generated-at stamp, 48-hour freshness threshold, source references, subject/position/settlement counts, and parity status.
- **Participation status:** explicit text that external entries and wallet actions are not enabled under the current ruling.

### 4.2 Dynamic counts and completeness

Do not hard-code subject counts in page copy, headings, badges, or empty-state text. Derive displayed counts from the same loaded feed used to render the page. Show source counts alongside rendered counts and flag mismatches. A nonempty page is not proof of completeness.

The current master snapshot observed during this review contains a generated feed timestamp of 2026-11-04 and a 39-subject projection; the page copy still says “all 23 subjects.” Treat this as a confirmed stale-copy/parity defect to correct in the implementation phase, not as evidence that the underlying ledger should be edited.

### 4.3 Accessibility and responsive behavior

- Semantic headings, table captions, column headers, and descriptive status text.
- Keyboard-accessible navigation and no color-only status encoding.
- Gantt has a textual equivalent; horizontal overflow is contained on small screens.
- Respect reduced-motion preferences; no animation may imply live execution or a live market.
- Announce stale/error states accessibly and preserve useful source metadata in the DOM.

## 5. WagerDome arena boundary

WagerDome is the venue/arena brand, not a synonym for the Wagertome record. It is currently held and has no arena surface of record.

A future arena proposal may define:
- seasons and slates;
- event/subject discovery and eligibility;
- participant classes and admission;
- schedules, standings, and result presentation;
- links back to Wagertome subject and settlement records.

It may not create duplicate book records, independent settlement truth, a parallel odds engine, or a second wallet ledger. Arena results must reference the owning subject and its record of record. WagerDome must not appear as a production navigation destination until a surface is registered, reviewed, and released.

## 6. Public wallet lane — proposed architecture

### 6.1 Separation of planes

| Plane | Responsibility | Initial mode |
|---|---|---|
| Public discovery | Explain the product, rules, eligibility, and status | Public read-only |
| Wallet identity | Prove control of an address without custody | Disabled until approved |
| Participant profile | Public display identity and consent/preferences | Disabled until approved |
| Submission/intake | Receive a typed, bounded user proposal or forecast | Disabled until approved |
| Wagertome book | Internal record of record and current authorized public projection | Read-only |
| Wallet ledger | Existing wallet authority and append-only lifecycle records | No writes from dashboard |
| Arena (WagerDome) | Event/season/competition presentation | Held |

A future wallet lane must be a separate service/API boundary and a separately governed data model. It must not write directly to `challenges-book.json`, `ledger.jsonl`, the publication feed, or the dashboard projection.

### 6.2 Wallet connection and onboarding states

The future onboarding state machine is:

`NOT_STARTED → DISCLOSURE_SHOWN → CONSENTED → CONNECT_REQUESTED → ADDRESS_VERIFIED → PROFILE_BOUND → ACTIVE`

Terminal/exception states:

`DECLINED`, `DISCONNECTED`, `EXPIRED`, `REVOKED`, `REVIEW_REQUIRED`, `REJECTED`.

Every transition must carry a stable request ID, actor/session reference, timestamp, policy version, and auditable reason. No state may be inferred from a connected browser extension alone.

Proposed verification sequence (not enabled):
1. Explain the exact purpose and data visible to the application before wallet connection.
2. User chooses to continue; no preselected consent.
3. Request address/account exposure only; no transaction request.
4. Issue a short-lived, single-use, domain-bound challenge with nonce and expiry.
5. Verify a standards-based signed message server-side; bind the verified address to the declared chain/network and origin.
6. Persist only the minimum verification receipt and public address data required by the approved policy.
7. Provide disconnect/revoke controls and explain what is retained after disconnect.
8. Require a new challenge for a new address, chain, domain, or expired session.

Never request seed phrases or private keys. Never sign a transaction as part of identity verification. Do not silently switch chains or networks.

### 6.3 Security and privacy controls

- Strict origin/domain binding and anti-phishing display of the canonical domain.
- Single-use nonce, short expiry, replay protection, signature verification, and rate limiting.
- Explicit chain/network allowlist; unsupported networks fail closed.
- No browser-held server secrets, wallet private keys, seed phrases, or signing material.
- No transaction, token approval, transfer, stake, or contract interaction in the onboarding flow.
- Data minimization, retention schedule, deletion/revocation policy, and privacy notice before collection.
- Abuse controls: duplicate identity policy, Sybil resistance review, sanctions/eligibility review where legally required, and appeal path.
- Threat model covers malicious wallet extensions, lookalike domains, replay, signature confusion, chain mismatch, session fixation, CSRF, XSS, compromised RPC, and poisoned metadata.
- Security review and independent verification before any public launch.

### 6.4 Participation semantics

“Participation” must be typed, not a vague catch-all. The future product specification must distinguish:
- wallet identity proof;
- profile creation;
- non-financial forecast/proposal submission;
- challenge/arena entry;
- observational position;
- wallet transfer or on-chain action.

These are separate permissions and separate policy gates. Wallet identity must not automatically confer participant status, entry eligibility, a position, a stake, or a settlement claim. No real-money wagering or external wagering is in scope under the current lane charter.

## 7. API and data contracts — proposal

The following are logical contracts, not deployed endpoints.

| Contract | Purpose | Required controls |
|---|---|---|
| `wallet-challenge/v1` | Issue nonce/challenge | Domain binding, expiry, one-time use, rate limit |
| `wallet-verification-receipt/v1` | Record verified address proof | Signature result, chain ID, address, nonce ref, policy version; never secret material |
| `participant-profile/v1` | User-controlled public profile | Consent, visibility, revocation, minimal fields |
| `participation-intake/v1` | Typed non-financial submission | Idempotency key, schema validation, abuse review, explicit status |
| `wallet-event/v1` | Append-only wallet lifecycle receipt | Actor, event, source, timestamp, policy, previous receipt hash |
| `arena-reference/v1` | Reference a WagerDome event/season | Stable event ID and owning Wagertome subject reference |

Every write endpoint must be authenticated, authorized, idempotent, rate-limited, schema-validated, and produce an immutable receipt. Browser code must never write directly to repository JSON or append-only ledger files.

## 8. Parity and verification matrix

| Gate | Required proof | Fail behavior |
|---|---|---|
| Source parity | Stable-ID and field-level comparison against book feed | HOLD refresh |
| Mirror parity | Byte equality: generated feed = dashboard mirror = fixture | Fail CI |
| B1 | Exactly one expectation per subject | Reject projection |
| B2 | Every position has a resolvable basis reference | Position HELD |
| B3 | Settlement source equals subject record of record | Reject settlement |
| B4/R3 | No public mutation/entry/position/transfer path | Block release |
| B5 | No hidden winprob leakage; significance language validated | Reject claim |
| R1/R2 | Verbatim values; nulls preserved as INTAKE | Fail render contract |
| Freshness | Generated-at <= 48h | STALE, never healthy |
| Count reconciliation | Source, generated, mirrored, and rendered counts agree | Surface mismatch |
| Wallet proof | Domain, nonce, expiry, signature, chain, address all verify | Reject identity binding |
| Consent | Explicit, versioned, revocable | No collection/activation |
| Security | Threat-model tests + independent review | HOLD launch |
| Release | Current-head CI, review, owner authorization, DoE pass | No promotion |

Coverage must be reported per requirement class with denominators and evidence references; never collapse unlike gate classes into one percentage.

## 9. Implementation sequence and release gates

**P0 — Reconcile sources (read-only).** Re-fetch master versions and SHAs for the book, feed, ledger, generator, page, tests, lane charter, brand registry, and related MoneyBall wallet-ledger sources. Reconcile the open stale-feed incident and identify the authoritative refresh owner.

**P1 — Wagertome page parity repair (safe under current ruling).** Remove stale hard-coded counts; derive counts from loaded feed; expose source freshness and mismatch state; preserve read-only behavior; add regression tests. Refresh generated artifacts only through the canonical generator and refresh PR contract.

**P2 — Public onboarding specification (design only).** Finalize privacy notice, supported chains, wallet proof standard, retention, identity policy, eligibility, threat model, API owner, and operational support. All remain NOT_ESTABLISHED until sourced and approved.

**P3 — Separate wallet identity pilot (owner-gated).** Only after a new owner authorization, DoE review, security review, and explicit chain/domain allowlist. Address proof only; no transactions or book writes.

**P4 — Non-financial participation intake (owner-gated).** Separate intake store and receipt chain. No positions, stakes, settlement rights, or mutation of the internal book unless separately authorized.

**P5 — WagerDome arena (held).** Register the surface, event taxonomy, eligibility and settlement references. Release only after the venue scope and brand provenance are approved.

**P6 — Broader wallet actions (out of scope here).** Any transfer, token approval, custody, smart contract execution, or wagering requires a separate legal, security, financial, and owner-approved specification. Nothing in this proposal authorizes it.

## 10. Acceptance criteria

- The existing Wagering Book remains the sole public book page; no duplicate WagerBook surface.
- Wagertome and WagerDome naming is consistent with the Registry.
- Page copy never hard-codes subject/position/settlement counts.
- Source/generated/mirror/fixture/render counts reconcile and are visibly auditable.
- All B1–B5 and R1–R3 tests remain passing.
- No external entry, position, settlement, transfer, or mutation path is introduced by the safe page-parity phase.
- Wallet connection is disabled unless a separate authorization is recorded and every identity/security/consent gate passes.
- No secrets or custody material are ever collected.
- WagerDome remains HELD until its own surface is registered and approved.
- No claim of deployment, wallet verification, participant onboarding, or runtime operation is made without observed evidence.

## 11. Source references inspected

- `docs/ops/SURFACES-MAP.md` — surface and brand map; Wagertome record / WagerDome held arena.
- `docs/ops/AGENTIC-GAMBLING-LANE.md` — internal-only scope, no real money/external wagering; participant-wallet invariant and open implementation status.
- `ops/agentic-gambling/book/challenges-book.json` — B1–B5, B4 owner ruling, scope guard and subject records.
- `ops/agentic-gambling/book/book-feed.json` — read-only publication feed.
- `scripts/moneyball/wagering_book_feed.py` — projection generator.
- `apps/tribute-dashboard/wagering-book.html` — existing read-only page.
- `apps/tribute-dashboard/data/wagering-book.json` — generated projection.
- `tests/test_wagering_book_page.py` — source/mirror/fixture parity and page behavior tests.
- Issue #5212 — reports the adjacent stale projection and absent automated refresh workflow; revalidate its current state before implementation.
- Current owner ruling, 2026-11-02 — external entries remain closed and the public surface remains read-only.

**Disposition:** The blueprint is ready for review as a scoped proposal. It is not an authorization to deploy the wallet or participation lane.
