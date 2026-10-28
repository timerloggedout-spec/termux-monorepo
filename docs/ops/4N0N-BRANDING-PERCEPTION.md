# 4n0n — Branding-Perception Evaluation

Owner correction (2026-10-27): **`4n0n` SEC is NOT a branding theme. It is a
protocol** — the doxxing-prevention / security protocol in
`docs/ops/4N0N-REGISTRATION-PROTOCOL.md` (moniker fronts every public
artifact; one platform, one moniker; no cross-platform linkage; no personal
identifiers in the record; handles are provisioning facts; forced personal
fields and payment instruments are owner-gated; leak = flag to main chat,
correction owner-directed).

This document is the **separate** evaluation of the protocol's *impact on
branding perceptions* (theming included). It edits nothing in the protocol,
the Linguist substrate, or any registry. It absorbs findings only.

Lane: [MUSEai]@{role:{4n0n-protocol}}

## 1. Avatar attention test

Question (owner): a great avatar was generated in main chat — does it
actually create more attention? Which kind, vs normalizing and blending?

Baseline under test: the main-chat `4n0nS3C` character — faceless hooded
geometric mask, teal/green circuit traces, cipher ring, no text/identity
(PNG, 1,653,799 B, sha256
`cf16da30068a4b59f51eb543457fbba629289ad42ba46f49a5dd9eb8de23e5a3`;
already the preferred G-07 Builder asset via the challenge lane).
An earlier pass in this lane scored the older 1337 circuit-mask avatar
(`builder-avatar-1337.webp`, sha256
`24e7a9f33e17ed8bc07496cb1e8ba7bec30e504ad385dd7c24294cf4950255ff`);
its scores were the same shape and are superseded by the table below.

Blended variant prepared for comparison: muted blue-grey abstract
node-mark — no face, hood, ring, text or neon
(`assets/avatar-blended.png`, 308,660 B, sha256
`65185283d0db0c95e5a9b6b495ac1bde8a386310c625787bffd06a38ef80496c`).
Side-by-side sheet, full size + circular profile crops at 96/48/32 px:
`assets/avatar-comparison.png` (487,011 B, sha256
`773b4350551fa01a81f952ffa61586d56dd165887ce405abc33bb032855641a1`).

| Axis (0–10) | Original `4n0nS3C` | Blended |
|---|---|---|
| Visual stop (scroll) | 9 | 2 |
| Recall / fingerprint | 9 | 2 |
| Tribal anon/hacker signal | 9 | 0 |
| Scrutiny / suspicion | 7–8 | 1 |
| Platform-norm fit | 3 | 9 |
| Thumbnail legibility (circular 32–96 px) | 8 | 3 |
| Personal identifiers | 0 | 0 |

Findings:

- The original creates attention of specific kinds: visual salience
  (face/mask pareidolia, neon ring, hood silhouette survives at 32 px),
  recall (instantly re-recognizable), and tribal signaling — credibility
  in security circles, edge/suspicion in corporate or judging contexts.
- The attention lands on the **pseudonym, not the person** — zero PII in
  either variant. That split is the protocol-vs-branding test.
- The blended variant proves the trade: normalizing removes attention
  *and* memorability. Its mark washes out at thumbnail sizes (legibility
  3) — it blends, but its presence is weak.
- A midpoint exists (the blended abstract at larger scale and deeper
  contrast, still no face/hood/neon); it is recorded, not adopted.
- Reuse warning (protocol, not branding): a distinctive avatar is a
  fingerprint. Reused across platforms it links them — a breach of
  protocol rules 2/3 regardless of how it looks.

## 2. Layered clues — the evaluation unit is the stack

Owner (2026-10-27): when visitors land on our Surfaces there are more
clues — like our `1337_$934k` Grimoire — layered.

A landing visitor receives the whole stack within seconds:

- **Visual:** avatar/theming (above).
- **Naming:** registration monikers (`n0nAwsBuilder`, `n0nDevpost`, …),
  `1337dia590r1c8u1ldr`, `timerloggedout-spec`.
- **Lexical:** `1337_$934k` — phase-codec LEET_MAP (6 chars) and canonical
  tokens (31), CedrLang symbol map (32) and compression mappings (31).
- **World terms:** Grimoire tables (char variants 26, core castings 14,
  protocol terms 11, orchestra crosswalk 16 = 67) plus Delphi / Witness /
  MoneyBall / ICM vocabulary.
- **Structural:** `Role{Moniker}[context]` forms,
  `[MUSEai]@{role:{…}}` signatures, receipts and ledgers.

Counts are from the landed Linguist feed (`linguist-panel-feed/v1`,
PR #1864/#1868): 15 families, 288 entries enumerated, 7,575 total.

Each clue alone is generic (leet, circuits and masks are common). Stacked,
they form a combinatorial fingerprint of the pseudonym/fleet — still zero
PII. Therefore:

- Branding evaluation scores the **cumulative stack per surface**, never
  a single asset. Blending one asset moves total salience only
  marginally; the text/vocabulary layers re-identify the surface at once.
- Real normalization would mean stripping functional vocabulary (the
  codecs are communication infrastructure, not decoration) — out of
  scope for a theming decision.

### Audit — stack level per surface

| Surface | Level | Notes |
|---|---|---|
| Repo landing `README.md` | MAX | L33t/Grimoire contact projection (PR #304: `README.hum.md` → `README.md`, `scripts/cedrlang/render_contact_projections.py`, 24 projections; Grimoire `1337_$934k` matrix landed in README via PR #1642) |
| Pages / dashboard / Linguist panel | HIGH | Theming + rendered mappings + receipts style |
| Submissions / demos | MED | Moniker + provenance/receipts style |
| Third-party profiles | LOW by rule | See §3 |

## 3. Rule — own surfaces layered, third-party isolated

Owner decision (2026-10-27, "Both"):

- **Own Surfaces stay layered and aware** — the full clue stack is
  intentional there.
- **Third-party profiles stay isolated** — the moniker only; the stack
  is not exported. The same stack reused intact off-platform would link
  profiles to each other, which is what protocol rules 2/3 restrict.

## 4. Progressive Δ on the landing README — and the counter question

Early-PR plan (owner-aware): consecutive renderer passes add `rnd` new
L33T mappings, weighted per document, so the landing `README.md` appears
to progressively change (∆). This is a projection-renderer property
(pass/density policy), continuous with PR #304's contact projections and
the notation-sets adaptive-mixing research (NSE-011/012).

Visitor-counter verdict: **do not drive it from a visitor counter.**

- A README-embedded counter cannot separate true visitors from the fleet
  itself, crawlers and caches (GitHub serves README images through its
  camo proxy) — the count would mostly measure us.
- A third-party counter is a tracking pixel on a 4n0n surface and breaks
  the separation in §5 by itself.
- The deterministic driver already exists: the renderer's own pass
  count. If counting is ever wanted, first-party only, on our own Pages.

## 5. Separations — what is absorbed where

| Domain | Absorbs | Never absorbs |
|---|---|---|
| Linguist substrate | Mappings (SSOT, canonical feed) | Presentation, identity rules |
| Projection renderer | Density / pass policy (how much L33t per document) | New mappings, identity rules |
| Surfaces | Presentation only | Mappings, policy, identity |
| 4n0n protocol | Identity rules only | Theming, mappings |
| Branding evaluation (this doc) | Findings only | Edits to any of the above |
| Profile / Moniker registries | Third-party presentation | The own-surface stack |

Collaborative work happens on the **overlaps, through contracts** —
precedent: `linguist-panel-feed/v1` (substrate owns the feed, the
visualization lane owns the render, Web Design owns deploy). An overlap
without a contract is how a finding in one domain silently becomes an
edit in another.

## 6. Avatars are generated characters — video prior planning

Owner (2026-10-27): the avatars could be generated characters — what
happens if there is a video chat later? Tools ready; proper prior
planning.

- One character per moniker, never shared across platforms (same rule as
  the monikers themselves).
- Character pack per character: canonical image, angle/expression sheet,
  palette/silhouette pins, and a **synthetic voice spec** — never cloned
  from the owner; a voice is biometric PII.
- Call routes, in preference order: (1) pre-rendered / scripted clips;
  (2) real-time rig (avatar overlay + TTS) only for low-stakes calls.
  The owner's camera and face are never the fallback.
- Readiness proof (2026-10-27): the `4n0nS3C` still was animated to a
  10.0 s clip (`assets/4n0ns3c-character-test.mp4`, 6,098,748 B, sha256
  `e0277e4d8b703294f5670ab7dd2952fc7dacf271d8128f4986a20ebcdffcd00f`;
  frame at 2 s extracted and visually verified — character holds, ring
  and circuits animate). Caveat: the generator added HUD/binary detail
  in motion — character drift that the pinned character sheet must
  control before any real call.
- No character pack has been built yet; building one is the named next
  step when a call actually looms, not before.

## Status

Evaluation open. No asset adoption changed by this document: the G-07
Builder avatar remains the challenge lane's registry decision; the
blended variant is evidence, not a replacement.
