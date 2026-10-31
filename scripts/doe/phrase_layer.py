"""JIT phrase layer — mandatory provider phrases, applied between
prompt construction and model dispatch (owner order, 2026-10-31).

Data SSOT: the `provider-phrases` repo (timerloggedout-spec/
provider-phrases), pinned into this repo as the `ops/phrases`
submodule; `phrases.json` carries per-provider prefix/suffix sets
+ named profiles, verbatim. Owners amend sets there; consumers
bump the pin.

The variables the owner named — placement, selection, when to
use, character substitutes — are explicit parameters here, so a
DoE design can treat them as factors:
  selection: "first" (deterministic head of list) | "hash"
             (stable index from the prompt text hash)
  placement: "prefix" | "suffix" | "prefix+suffix"
  form:      "verbatim" | "leet" (character substitutes applied
             to the inserted phrase text only, never to the task
             prompt itself)
  profile:   a named profile in the provider set (its
             system_prefix / system_suffix override the lists)
  transform: the AUTOMATED mechanism — a data-driven engine over
             the SSOT `char_variants` table + `established_vowel_map`:
             {casing: as-written|upper|lower|title,
              sub_scope: none|vowels|consonants|all,
              sub_depth: variant index}. Ladders EMERGE from the
             parameter cross (e.g. casing=lower x sub_scope=vowels
             generates the "d0" rung for any token) — nothing is
             hand-enumerated per token.
  generate_variants(): emits the ladder for any phrase text
             automatically (casing x substitution cross, deduped,
             stable ids) — designs select generated variant ids
             as factor levels.
  token_forms: MANUAL OVERRIDE escape hatch only (per-token
             verbatim replacement); not the mechanism.

The general rule (owner, 2026-10-31): micro-variables of this
kind — casing ladders, substitution scope/depth, placement,
selection, timing, profile composition, emoji inclusion — are
evaluation dimensions. Any single example (the d0 ladder is one)
stands for the whole kind; designs enumerate the kind's levels
and let runs rank them.

Returns the composed text + a stamp dict; the caller folds the
composed text into its prompt hash, so phrased and unphrased runs
are different configured instances.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# The ESTABLISHED substitution set, read off the 1337 profile's
# own suffixes (provider-phrases phrases.json): only the vowels
# substitute (a->4, e->3, i->1, o->0); every consonant — l
# included ("Bu1ld", not "Bu11d") — stays literal. Anchor:
# leet("Build the Future Now. Make it so.") == the profile's
# established "Bu1ld th3 Futur3 N0w. M4k3 1t s0." (verified by
# test). The wider variant tables in the 1337 dictionary are
# candidate levels, not the established form.
LEET_MAP = {"a": "4", "e": "3", "i": "1", "o": "0"}


def leet(text: str) -> str:
    return "".join(LEET_MAP.get(ch.lower(), ch) if ch.isalpha()
                   else ch for ch in text)


VOWELS = set("aeiou")


def transform(text: str, *, casing: str = "as-written",
              sub_scope: str = "none", sub_depth: int = 0,
              variants: dict | None = None,
              vowel_map: dict | None = None) -> str:
    """Data-driven casing x substitution engine. Substitution
    data comes from the SSOT phrases.json (`char_variants` +
    `established_vowel_map`); callers pass them in from the
    loaded data so the table is never duplicated in code."""
    if casing == "upper":
        text = text.upper()
    elif casing == "lower":
        text = text.lower()
    elif casing == "title":
        text = text.title()
    elif casing != "as-written":
        raise ValueError(f"unknown casing {casing!r}")
    if sub_scope == "none":
        return text
    vm = vowel_map if vowel_map is not None else LEET_MAP
    out = []
    for ch in text:
        low = ch.lower()
        if sub_scope == "vowels":
            out.append(vm.get(low, ch) if low in VOWELS else ch)
        elif sub_scope in ("consonants", "all"):
            if low in VOWELS:
                out.append(vm.get(low, ch) if sub_scope == "all"
                           else ch)
            elif ch.isalpha() and variants and low in variants:
                opts = variants[low]
                out.append(opts[min(sub_depth, len(opts) - 1)])
            else:
                out.append(ch)
        else:
            raise ValueError(f"unknown sub_scope {sub_scope!r}")
    return "".join(out)


def generate_variants(text: str, data: dict) -> list[dict]:
    """Emit the ladder for any phrase automatically: the casing x
    substitution cross, deduped, stable order + ids. Designs use
    the ids as factor levels — generated, never enumerated."""
    variants = data.get("char_variants")
    vowel_map = data.get("established_vowel_map")
    grid = [("verbatim", {}),
            ("upper", {"casing": "upper"}),
            ("lower", {"casing": "lower"}),
            ("vowels", {"sub_scope": "vowels"}),
            ("upper+vowels", {"casing": "upper",
                              "sub_scope": "vowels"}),
            ("lower+vowels", {"casing": "lower",
                              "sub_scope": "vowels"}),
            ("leet-full", {"sub_scope": "all"}),
            ("leet-full-d1", {"sub_scope": "all", "sub_depth": 1})]
    seen, out = set(), []
    for vid, params in grid:
        t = transform(text, variants=variants, vowel_map=vowel_map,
                      **params)
        if t not in seen:
            seen.add(t)
            out.append({"id": vid, "text": t, "params": params})
    return out


def load_sets(phrases_file: str | Path) -> dict:
    return json.loads(Path(phrases_file).read_text())


def find_set(data: dict, model_route: str) -> tuple[str, dict] | None:
    route = model_route.lower()
    for key, pset in (data.get("providers") or {}).items():
        for needle in pset.get("match", []):
            if needle.lower() in route:
                return key, pset
    return None


def _pick(items: list, selection: str, seed: str) -> str:
    if not items:
        return ""
    if selection == "hash":
        idx = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
        return items[idx % len(items)]
    return items[0]


def _apply_token_forms(text: str, token_forms: dict) -> str:
    for token, replacement in token_forms.items():
        text = re.sub(rf"\b{re.escape(token)}\b", replacement, text,
                      flags=re.IGNORECASE)
    return text


def apply_phrases(prompt: str, data: dict, model_route: str, *,
                  selection: str = "first",
                  placement: str = "prefix+suffix",
                  form: str = "verbatim",
                  profile: str | None = None,
                  token_forms: dict | None = None,
                  transform_cfg: dict | None = None) -> tuple[str, dict | None]:
    found = find_set(data, model_route)
    if not found:
        return prompt, None
    key, pset = found
    prefix = suffix = ""
    if profile:
        prof = (pset.get("profiles") or {}).get(profile)
        if not prof:
            raise ValueError(f"profile {profile!r} not in set {key!r}")
        prefix = prof.get("system_prefix", "")
        suffix = prof.get("system_suffix", "")
    else:
        if "prefix" in placement:
            prefix = _pick(pset.get("prefixes", []), selection, prompt)
        if "suffix" in placement:
            suffix = _pick(pset.get("suffixes", []), selection, prompt)
    if form == "leet":
        prefix, suffix = leet(prefix), leet(suffix)
    elif form != "verbatim":
        raise ValueError(f"unknown form {form!r}")
    if transform_cfg:
        kw = {"variants": data.get("char_variants"),
              "vowel_map": data.get("established_vowel_map")}
        prefix = transform(prefix, **{**kw, **transform_cfg})
        suffix = transform(suffix, **{**kw, **transform_cfg})
    if token_forms:
        prefix = _apply_token_forms(prefix, token_forms)
        suffix = _apply_token_forms(suffix, token_forms)
    parts = [p.strip() for p in (prefix, prompt, suffix) if p.strip()]
    stamp = {"provider": key, "selection": selection,
             "placement": placement, "form": form,
             "profile": profile, "token_forms": token_forms or {},
             "transform": transform_cfg or {},
             "prefix_sha256_12": hashlib.sha256(
                 prefix.encode()).hexdigest()[:12] if prefix else None,
             "suffix_sha256_12": hashlib.sha256(
                 suffix.encode()).hexdigest()[:12] if suffix else None}
    return "\n\n".join(parts), stamp
