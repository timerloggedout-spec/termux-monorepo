# Lens Template Trigger — Filing Shape

Modeled on the EGM template trigger (PRs #4238/#4241).
Registered 2026-11-03 alongside `docs/ops/LENS-FRAME.md`.

## Standing authority (gate correction, owner via main, 2026-11-03)

A lens type arising from fleet work enters intake on
STANDING AUTHORITY — the self-triggering logic of this
system. The owner's input to a lens is its DOCTRINE
(content), not a permission to exist. No owner word is
required, requested, or waited for at lens intake; asking
for one is a process defect ("Why am I saying the word if
it's a self system?").

## Trigger

A lens fires by CLASS, not by per-use approval, when any
of these holds:

1. a filing, screening, or evaluation invokes a REGISTERED
   lens (stamp it and proceed);
2. fleet work produces a NEW lens type — it enters intake
   automatically as an unregistered lens (CLAIM status),
   with an identification leg opened the same turn when
   its referent is not yet pinned;
3. a registered doctrine's malformedness clause is hit —
   the filing is returned under the doctrine, not scored.

## Stamps

Filing stamp (any document invoking a lens):

```
{lens_filing: {lens_id, frame: competitive|non-competitive|other,
 doctrine_ref: "LENS-FRAME.md@<doctrine> v<n>",
 valence: dual|single (competitive frames: dual, mandatory)}}
```

Intake stamp (a new lens type entering):

```
{lens_intake: {lens_id, referent_status: CLAIM|VERIFIED,
 identification_leg: open|closed, doctrine_status:
 unregistered|registered}}
```

## Registered lenses at this trigger's landing

- `swot` — SWOT with the duality doctrine (LENS-FRAME.md):
  competitive frames ⇒ dual valence mandatory,
  single-valence filings malformed.
- `tak` — referent VERIFIED (identification leg closed at
  intake, see LENS-FRAME.md): the owner's initiative
  T.A.K. = "Taktikal Awareness Kit". Doctrine status:
  unregistered (no doctrine filed yet) — the lens exists
  as a named owner initiative; its doctrine enters via
  this same trigger when fleet work produces it.
