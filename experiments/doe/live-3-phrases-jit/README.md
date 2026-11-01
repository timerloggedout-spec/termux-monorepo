# live-3-phrases-jit — JIT phrase-layer factors (LIVE design)

First phrased live campaign. Subject: `scripts/doe/phrase_layer.py`
(JIT layer) over SSOT `timerloggedout-spec/provider-phrases`
`phrases.json` @ pin `a27b8b4eb060` (`ops/phrases` submodule on
master == SSOT head, verified 2026-10-31 by this lane).

SSOT state at design time (firsthand): providers = {deepseek}
only (prefixes 5, suffixes 7, profiles {1337}); `char_variants`
26; `established_vowel_map` {a:4, e:3, i:1, o:0};
`evaluation_dimensions` 8. ∴ every non-DeepSeek route in this
campaign stamps phrases = NOT ESTABLISHED, never a silent skip,
and is ∅ a treatment cell.

Factors (wave 1, full factorial 3×2×4 = 24 cells + control):

- placement ∈ {prefix, suffix, prefix+suffix}
- selection ∈ {first, hash}
- transform ∈ {none, vowels(d0), lower+vowels, upper+vowels}
  — all via `transform()` {casing × sub_scope:vowels × depth 0}
  over SSOT data; `generate_variants()` ids name the levels.

Control = unphrased instance. Phrased ≠ unphrased: composed text
is what gets hashed; stamp {provider, placement, selection,
form, profile, transform, prefix_sha256_12, suffix_sha256_12}
rides the instance stamp. Profile arm (profile=1337) runs as a
separate single arm, ¬ a factorial cell — a profile overrides
both lists, so crossing it with placement confounds.

Gates / exclusions (verified, ¬ assumed):

- sub_scope ∈ {consonants, all} DEFERRED to wave 2: Linguist
  C1/C2 on #2677 (comment 6545916596) — `char_variants_source`
  credit missing ∧ q/v rows = suspected parse artifacts vs the
  canonical dictionary (`harmony_hub/config/grimoire/
  1337_D1CT10N4RY.md`, Linguist-canonical). Wave 1 uses vowels
  scope only (established map, anchor-tested). Wave 2 unlocks
  on SSOT amendment + pin bump; consumption ⇒ notify Linguist
  same-turn; any mapping-key Δ ⇒ flag viz (4ed48ba4) before/with
  the PR.
- selection=rotated: named in SSOT dimensions, ∅ implemented —
  `phrase_layer._pick` falls through to first for any value
  ≠ hash. Excluded from wave 1; ¬ relabelled as first.
- selection=hash is a POLICY contrast: hash picks different
  phrase content per prompt, first fixes content. Stamp shas
  decompose policy vs content post-hoc.

Execution rides a DeepSeek live route named by doe-expert at
admission (DeepSeek-CI dispatch surface); this design ∅
self-dispatches. Responses = host task success/quality under
the host suite's own rule; selection rule pre-registered in
DESIGN.json.
