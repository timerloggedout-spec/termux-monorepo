# NAMING-COLLISION 💥 MAPPING PROTOCOL (2026-11-04)

`[MUSEai]@{role:{naming-collision-map}}` · proActive preparation
(owner commission via main, 2026-11-04).

**Status:** protocol of record for MAPPING collisions. **Authority:**
the Registry lane (naming seat) owns the naming FLOW (coinage →
collision check → issuance → record, SSOT `docs/ops/AGENT-MONIKERS.md`).
This doc changes ∅ in that flow — it standardizes the MAP every
collision pass produces, so passes are comparable, reusable, and
pre-computable before a naming is urgent.

## 1. The map — row schema

One row per (candidate × collision object). A pass = the full row
set for a candidate set, filed inside the issuance record.

| field | content |
|---|---|
| `candidate` | exact string, case-preserved |
| `class` | moniker · brand · unit · vocabulary · handle/slug |
| `surface` | screen id (§2) where the object was found |
| `object` | the colliding/adjacent string + owner (mark, plane, record) |
| `relation` | exact · adjacent · stem · semantic · mechanical |
| `disposition` | §3 class |
| `evidence` | source + date + firsthand seat (counts, not impressions) |
| `mitigation` | distinction / use rule, when disposition ≠ DEAD |

∅ row, ∅ claim: a candidate with no row on a screen reads
NOT_CHECKED on that screen, never "clear".

## 2. Screens — order of record

| # | screen | checks |
|---|---|---|
| S1 | in-fleet SSOT | `AGENT-MONIKERS.md` + `PROFILE-REGISTRY.md` + `config/registration_monikers.json` — exact + stem |
| S2 | repo code search | monorepo + subject repo (e.g. moneyball) — hits classified: record's-own-usage = confirmation, ¬ collision |
| S3 | semantic planes | live plane vocabularies (quota plane set {quota · token · credit · call · rate · slice · share · cap · soft · governor} + per-vocabulary exclusion screens) — stem ∧ semantic fit |
| S4 | live marks (web) | exact string in/near the field (™®©) + adjacencies worth distinguishing |
| S5 | Grimoire round-trip | Linguist `phase_codec`: leet form collides ∅ issued form ∧ ∅ `CANONICAL_TOKEN` of a different sense ∧ plain ASCII ∧ inverse-decodes exactly |
| S6 | mechanical namespace | handles/slugs: taken ⇒ deterministic rename (§3 `RENAMED-MECH`), never improvised |

Screens run S1→S6; a DEAD at any screen still gets its row —
later screens for that candidate = SKIPPED-BY-DEATH, named as such.

## 3. Dispositions

| disposition | meaning |
|---|---|
| `ISSUED` | ∀ screens clear; name of record |
| `ISSUED-DISTINGUISHED` | adjacent object exists; distinction + mitigation written on the row (e.g. bare form stays the other owner's) |
| `RESERVED-ABSENT` | name held for a class that does not exist yet (e.g. `bookmaker`) — ∅ issuance, ∅ use |
| `CLEARED-NOT-ISSUED` | passed ∀ screens; lost on fit/semantics to the issued candidate |
| `RUNNER-UP` | cleared; stands as considered alternative of record |
| `DEAD-ON-MARK` | live external mark in/near field (S4) |
| `DEAD-ON-PLANE` | stem/semantic collision w/ a fleet plane (S3) despite ∅ external mark |
| `DEAD-ON-SENSE` | established term of art / wrong-sense corpus (S2/S4) |
| `RENAMED-MECH` | mechanical namespace only: collision ⇒ smallest free integer ≥2 (registration monikers v2 derive) ∨ slug bounce V1→V2 (Grimoire slug-safe, never a third improvisation) |

Rules: hits-of-record ≠ collision (S2) · identity ≠ collision
(S5 same-sense canonical overlap, e.g. `w4g3r`) · a colliding
legacy string is never silently swapped — custodians run a
VERSIONED transition, legacy stands in hash-chained history.

## 4. Worked rows — evidence cases

### 4.1 `booktally` — unit (SSOT §Unit-name issuance, PR #4825)

| candidate | surface | object | relation | disposition |
|---|---|---|---|---|
| `soft_quota_token` (legacy) | S3 | quota plane vocab {soft · quota · token} | stem ×3 | DEAD-ON-PLANE (owner misread = the collision in fact) |
| `booktally` | S1/S2/S3/S4/S5 | ∅ exact ∀ | — | **ISSUED** |
| `booktally` | S4 | Tally / Tally Book / TruckTally | adjacent | ISSUED-DISTINGUISHED (one-word compound, unit label only; bare + reversed forms stay theirs) |
| Fortally | S4 | Foretally (forecasting product) | adjacent (homophone) | DEAD-ON-MARK |
| PaperPoints · Jeton | S4 | PaperWagers · payments brand | exact-field | DEAD-ON-MARK |
| Speclet · Tallion | S4/S2 | .NET/EQC speclets · accounting cluster | semantic | DEAD-ON-SENSE |
| Callchit | S3 | `call` = provider/API-call vocab | stem | DEAD-ON-PLANE (∅ mark found — plane kills alone) |
| Specscrip | S3 | scrip = redeemable substitute currency | semantic | DEAD-ON-PLANE |
| Bookchit | ∀ | ∅ | — | RUNNER-UP (parse cost) |

### 4.2 `Stagefoil` — brand (SSOT §Brand issuance, PR #4817)

| candidate | surface | object | relation | disposition |
|---|---|---|---|---|
| AutoDesk (priming label) | S4 | Autodesk | exact-adjacent | DEAD-ON-MARK (internal-only predecessor, survives attributed in the issuance record only) |
| `Stagefoil` | S1/S2/S4 | ∅ exact ∀ | — | **ISSUED** |
| `Stagefoil` | S4 | Stage-Gate® · StageFlow · Stagehand | adjacent | ISSUED-DISTINGUISHED (hyphenated process mark · CRM · agent SDK — string + field distinct) |
| Counterfoil · Claviger · Promptbook · Gatebook · Stubbook · Passus · Chirograph · Sigillum · Cartulary · Muniment · Tablinum · Stagia · Promptuary · Transitus · Recepta · Cuebook · Notula · Schedula · Gradia · Gatewarden/Wicketgate | S4 | live mark each, in/near software | exact/adjacent | DEAD-ON-MARK ×21 |
| Acquittance | ∀ | ∅ | — | CLEARED-NOT-ISSUED (payment-discharge semantics, weak fit) |
| `Stagefoil Desk` | S1 | — | — | RESERVED-ABSENT (normalized form, reserved for a published instance) |

### 4.3 MoneyBall vocabulary (SSOT §MoneyBall vocabulary issuance, PR #4834)

| candidate | surface | object | relation | disposition |
|---|---|---|---|---|
| ∀ issued terms | S3 | quota-plane exclusion screen ⑧ {quota · odds-shaped · real-money · live marks · bare forms} | stem/semantic | ISSUED only outside the screen |
| `tallybook` · `scorebook` | S4/S2 | exact live apps · scoring-surface sense (2 hits) | exact | DEAD-ON-MARK / DEAD-ON-SENSE |
| `cardhand` | S4 | playing-card-hand corpus | semantic | DEAD-ON-SENSE |
| `cardkeeper` | ∀ | ∅ marks; lost to record's own `pool member` | — | CLEARED-NOT-ISSUED |
| `wager` (`w4g3r`) | S5 | CedrLang `CANONICAL_TOKEN`, same sense | exact | ISSUED (identity, ¬ collision) |
| `pool member` (45 hits) | S2 | record's own usage | exact | ISSUED (confirmation, ¬ collision) |
| `bookmaker` · `bookie` (as live role) | S1/S3 | reserved absent class · bare form | — | RESERVED-ABSENT / excluded ⑧ |

### 4.4 Registration monikers — handle class (docs/ops/4N0N-REGISTRATION-PROTOCOL.md)

| candidate | surface | object | relation | disposition |
|---|---|---|---|---|
| derived handle, taken | S6 | existing registry entry | mechanical | RENAMED-MECH (smallest free integer ≥2, v2 derive; v3 = unlinkable SHA-derived codename, stem ∅) |
| slug, taken | S6 | platform namespace | mechanical | RENAMED-MECH (bounce V1 → V2, Grimoire slug-safe; ∅ third improvisation) |
| `Oracle` (in `Archaeo · Oracle`) | S1/S2 | Delphi Oracle (D0 surface) | adjacent | ISSUED-DISTINGUISHED (paired form always in full; bare `Oracle` = Delphi) |

## 5. proActive preparation — use

- Precompute maps for QUEUED namings before they are urgent
  (pending registrations, reserved classes, priming labels in
  circulation) — a priming label in use w/o a map row = an
  unmapped collision risk, flagged at the Desk.
- Issuance PRs file the map rows in the SSOT issuance section
  (the 2026-11-04 issuances already do, in prose — this protocol
  names the schema they follow).
- Reuse: a DEAD row is permanent for its (candidate × object)
  pair; re-checks cite the row + re-verify the object lives.

Registry lane = reviewer of record for this protocol; amendments
ride its gate.
