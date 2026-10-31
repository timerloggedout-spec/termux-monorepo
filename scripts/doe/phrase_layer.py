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

Returns the composed text + a stamp dict; the caller folds the
composed text into its prompt hash, so phrased and unphrased runs
are different configured instances.
"""
from __future__ import annotations

import hashlib
import json
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


def apply_phrases(prompt: str, data: dict, model_route: str, *,
                  selection: str = "first",
                  placement: str = "prefix+suffix",
                  form: str = "verbatim",
                  profile: str | None = None) -> tuple[str, dict | None]:
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
    parts = [p.strip() for p in (prefix, prompt, suffix) if p.strip()]
    stamp = {"provider": key, "selection": selection,
             "placement": placement, "form": form,
             "profile": profile,
             "prefix_sha256_12": hashlib.sha256(
                 prefix.encode()).hexdigest()[:12] if prefix else None,
             "suffix_sha256_12": hashlib.sha256(
                 suffix.encode()).hexdigest()[:12] if suffix else None}
    return "\n\n".join(parts), stamp
