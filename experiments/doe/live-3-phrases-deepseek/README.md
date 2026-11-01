# live-3-phrases-deepseek — first phrased live campaign

Work order #1 (doe-expert INIT++, 2026-10-31). SUPERSEDES
`experiments/doe/live-3-phrases-jit/` (generic transform
screening under the seed brief) as THE first-phrased campaign;
that dir's status is updated in the same PR.

Route (one picked by doe-expert at approval; dispatch ∅ until
then):
- PRIMARY: OpenRouter cloud `deepseek/deepseek-r1:free`,
  invoke/review — #2732 reroute, device-free;
  `OPENROUTER_API_KEY` provisioned; model verified in
  `scripts/openrouter_free_catalog.py` (2026-10-31 read).
- ALTERNATE: deepseek-ci comment surface (event-bound, live).

Provider set = deepseek ONLY established (SSOT
`provider-phrases/phrases.json` @ pin `a27b8b4eb060` ==
head; prefixes 5 / suffixes 7 / profile 1337, verbatim from
`harmony_hub/workspace/prompts/prompt_engine.py` +
`harmony_hub/config/prompts/profiles/1337.json`). ∀ other
routes: phrases = NOT ESTABLISHED.

Factors — full factorial 3×3×2 = 18 cells + unphrased control
(= current production posture, reference arm):

- placement ∈ {prefix, suffix, both} ⇒ phrase_layer
  {prefix, suffix, prefix+suffix} ✓ implemented.
- form ∈ {verbatim, vowels, leet-full}, all via `transform()`:
  verbatim = sub_scope none; vowels = sub_scope vowels,
  depth 0 (established map {a4 e3 i1 o0}, anchor-verified);
  leet-full = sub_scope all, depth 0 over `char_variants`
  (CANDIDATE levels, data-driven, ∅ hand-enumerated).
- selection ∈ {fixed-anchor, rotating}: fixed-anchor =
  phrase_layer selection=first (prefixes[0] "You are DeepSeek
  v4-Pro; a 1337 coder…" + suffixes[0] "Build the Future Now.
  Make it so."); rotating = per-task rotation over the set by
  task ordinal (prefix idx = ord mod 5, suffix idx = ord
  mod 7), indices + shas in the stamp.

Suite = live review tasks flowing anyway (∅ synthetic mass,
live-first doctrine). Assignment per task = sha256(PR# +
campaign salt) mod cells, balanced, recorded in the dispatch
stamp before dispatch. Responses (quality proxies, per run):
findings posted · findings actioned (thread resolved ∨
addressed in a later commit) · rework commits ≤7d on the
reviewed PR · gate outcome. Primary = actioned rate.

Gates (evidence, ¬ assumed):
- leet-full cells REGISTERED but dispatch-BLOCKED until
  Linguist C2-v clears: `char_variants[v]` backslash runs
  differ SSOT vs canonical dictionary (#2677 c.6545916596)
  ∧ every deepseek prefix contains "v" ("v4-Pro") ⇒ the
  suspect row is in every leet-full prefix text. C2-q is
  immaterial here (verified: "q" ∈ ∅ phrase texts). Unlock =
  SSOT amendment + pin bump, ∨ doe-expert waiver on record.
  C1 (grimoire source credit) rides the same amendment.
- rotating assignment + per-cell phrase cfg are ∅ in current
  code: `phrase_layer._pick` = {first, hash} only ∧
  `lab_runner` applies ONE design-level `phrase_layer` cfg.
  On the live surface the dispatching lane stamps cell cfg
  per task (stamp = assignment record); a lab_runner
  per-cell extension is a separate code item, ¬ assumed here.
  selection=hash = implemented third policy, reserved.
- Stamps: composed text hashed (phrased ≠ unphrased
  instance); stamp ⊇ {cell, placement, form, selection,
  prefix_idx, suffix_idx, prefix_sha256_12,
  suffix_sha256_12, route}. Mapping-key Δ ⇒ flag viz
  (4ed48ba4) before/with any PR; dictionary consumption ⇒
  notify Linguist same-turn.

Staging (pre-registered): Stage 1 = fixed-anchor slice
(9 cells + control); Stage 2 = rotating crossed in for
Stage-1 survivors + control. Decision rule in DESIGN.json.
