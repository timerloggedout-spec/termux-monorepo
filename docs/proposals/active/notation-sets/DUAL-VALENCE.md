# Dual Valence — notation treatment

**Doctrine (owner, 2026-11-03):** in competitive frames, Threat &&
Opportunity can be the same target — one entity, two valences, with a
conversion operator between them (OSINT + recruiting outreach as
assimilation, ¬ %-pay brokerage). This note is the notation layer only;
the DoE holds the frame/evaluative side.

## Formalism (Linguist call): readings over a fixed object

Valence is not a property of an entity. It is a property of the pair
(entity, frame). Fix the entity E; its **readings** are states:

- `E^T` — the threat reading of E (default frame = house frame;
  a foreign frame's reading is indexed: `E^T_f`)
- `E^O` — the opportunity reading of E

A **dual-valence target** holds both at once:

- `E^{T∧O}` — both readings in force simultaneously; neither discharges
  the other. Writing only one superscript where both hold = collapse
  defect (a single-valence label on a dual-valence target).

The **conversion operator** is a morphism between readings of the same
object — an arrow in the category of readings over E (slice over E):

- `κ_{T→O} : E^T ⇢ E^O`, **object-component = id_E**

κ changes the relationship, not the entity: E is invariant under κ.
The dashed arrow `⇢` is deliberate — κ is neither a homomorphism
between two entities (`→`) nor an isomorphism (`≅`):

- **κ ≠ ≅.** κ is not invertible in-frame. The reverse move is a
  distinct operator `κ'_{O→T}` (escalation), never written `κ⁻¹`.
- **κ composes by ∘.** Conversion pipelines are `κ_n ∘ … ∘ κ_1`;
  associativity is the house (G, ∘) frame law (machine-checked shape:
  NSE-023 packet P-001, PASS).
- **κ carries no price term.** Assimilation is relational, not a
  transaction; a %-pay/brokerage reading of κ is a misread of the glyph.

**Operative vs retained.** Applying κ makes O the operative reading
while T is retained in the record — written `E^{O|T}` (O operative,
T retained as shadow). Simultaneity survives conversion: the pair is
never destroyed, only re-weighted in use.

**ker rule (house rule, carried over).** Every recorded conversion
names `ker κ`: what the T-reading held that the O-reading drops
(e.g. threat-model detail not carried into the outreach stance).
A conversion record = {E · κ · channel/operator · ker κ · provenance}.

## Worked instance — assimilation

Competitor entity X, read both ways: `X^{T∧O}`.
Assimilation conversion: `κ_assim = κ_{T→O}` via OSINT ∘ outreach —
first learn (OSINT stage), then reach out (outreach stage); composed,
they convert the operative reading: `X^{T∧O} →κ_assim X^{O|T}`.
X itself never changed; the relationship did. If outreach fails and
the stance hardens back, that is a new operator `κ'_{O→T}` on record,
not an undo.

## Non-collapse invariants (summary)

1. `E^T ≠ E^O` as states — distinct projections of `E^{T∧O}`.
2. Object invariance: any κ has object-part `id_E`.
3. No silent inversion: `⇢` never upgrades to `≅`; reverse = `κ'`.
4. Conversion without a named `ker κ` is an incomplete record.
5. Frame honesty: a reading without its frame index is the house
   reading by default — say so when it is not.

Seed registry: nomenclature-matrix domain `dual_valence`
(4 concepts · 12 labels · 3 mappings, all candidate) — crosswalks:
κ ↔ category_theory.morphism (slice-over-E arrow) · κ ↔
group_theory.homomorphism (operator-side structure, ker rule) ·
dual-valence target ↔ group_theory.group_action (frame acts, entity
is the fixed carrier).
