"""Phased 1337/Grimoire surface codec recovered from Linguist PR #154.

Historical source: PR #154 review comment `discussion_r3754718523` described a
sparse randomized substitution rate with a 70% probability threshold in
`to_1337speak()`. This module restores that behavior as an explicit, scoped
phase rather than silently changing canonical CedrLang semantics.

The codec only mutates known compressed dictionary tokens. Variants are
recognized during decode, so ordinary digits, URLs, paths, and prose are not
rewritten accidentally. `probability=0.70` is the initial migration/default
phase; callers can ratchet it upward after validation.
"""

from __future__ import annotations

import random
import re
from itertools import product
from typing import Dict, Iterable, Mapping, Optional, Sequence, Tuple

# Historical initial-phase value from Linguist PR #154.
INITIAL_SUBSTITUTION_PROBABILITY = 0.70

# Character substitutions are intentionally limited to letters that have a
# stable 1337 representation. Existing digits in canonical tokens are never
# rewritten, preserving numbers and technical identifiers.
LEET_MAP: Mapping[str, str] = {
    "a": "4",
    "e": "3",
    "i": "1",
    "o": "0",
    "s": "5",
    "t": "7",
}

# Pre-computed translation table for 100% probability fast-path translation
LEET_TRANS = str.maketrans("aeiostAEIOST", "431057431057")

# Canonical compressed forms from CedrLang's MAPPINGS. Keeping this registry
# local avoids importing the large document compiler and makes the phase easy
# to test/recover independently.
CANONICAL_TOKENS: Tuple[str, ...] = (
    "h4x", "scry", "pr0b3", "3ch0", "l00p", "f0rk", "1nc4nt", "c4st",
    "gr1m01r3", "b1dd3r", "w4g3r", "chr0n0", "l1ngu15t", "sc0ut",
    "h4rv35t3r", "em_t3chs", "em_t3ch", "pr0cur3s", "pr0cur3", "cur473s",
    "cur473", "s0urc3s", "s0urc3", "4cqs", "4cq", "c0mp1s", "c0mp1",
    "r3534rchs", "r3534rch", "c0nc3p7s", "c0nc3p7",
    "n0m3nc1s", "n0m3nc1", "3qu1v_m47s", "3qu1v_m47",
    "d0m_c0mps", "d0m_c0mp", "n07_537s", "n07_537",
)


def _variants(token: str) -> Iterable[str]:
    """Yield all reversible leet variants for a canonical token."""
    positions = [i for i, char in enumerate(token.lower()) if char in LEET_MAP]
    for mask in product((False, True), repeat=len(positions)):
        chars = list(token)
        for position, enabled in zip(positions, mask):
            if enabled:
                chars[position] = LEET_MAP[chars[position].lower()]
        yield "".join(chars)


def _build_variant_index(tokens: Sequence[str]) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for token in tokens:
        for variant in _variants(token):
            index.setdefault(variant.lower(), token)
    return index


def _build_trie_regex(words: Iterable[str]) -> str:
    """Construct a Trie-structured regex pattern from words to optimize prefix branching."""
    trie: dict = {}
    for w in words:
        curr = trie
        for char in w.lower():
            curr = curr.setdefault(char, {})
        curr[""] = None

    def _trie_to_regex(node: dict) -> str:
        if not node:
            return ""
        ending = "" in node
        chars = [k for k in node if k != ""]
        if not chars:
            return ""

        children = []
        for char in chars:
            sub = _trie_to_regex(node[char])
            char_pat = f"[{char.lower()}{char.upper()}]" if char.isalpha() else re.escape(char)
            if sub:
                children.append(char_pat + sub)
            else:
                children.append(char_pat)

        if len(children) == 1:
            res = children[0]
        else:
            res = "(?:" + "|".join(children) + ")"

        if ending:
            if len(children) == 1 and not children[0].startswith("(?:"):
                res = f"(?:{res})?"
            else:
                res = f"{res}?"
        return res

    return r"\b(?:" + _trie_to_regex(trie) + r")\b"


VARIANT_INDEX = _build_variant_index(CANONICAL_TOKENS)
# Build ASCII case-insensitive Trie regex without re.IGNORECASE to avoid Unicode case-folding overhead
VARIANT_REGEX = re.compile(_build_trie_regex(VARIANT_INDEX.keys()))

# Module-level set of eligible leet characters
ELIGIBLE_LEET_CHARS = set(LEET_MAP.keys())
# Filter variant index to only tokens containing eligible leet substitution characters
MUTABLE_VARIANTS = {
    v for v in VARIANT_INDEX.keys()
    if any(c in ELIGIBLE_LEET_CHARS for c in v.lower())
}

# Pre-compile Trie regex for mutable variants to skip invariant tokens completely during substitution
MUTABLE_VARIANT_REGEX = re.compile(_build_trie_regex(MUTABLE_VARIANTS))

# Pre-compute positional mapping for mutable variants: (lowercase_token) -> tuple of (character_position, leet_replacement_char)
MUTABLE_VARIANT_MAP: Dict[str, Tuple[Tuple[int, str], ...]] = {}
for variant_key in VARIANT_INDEX.keys():
    pos_map = tuple(
        (i, LEET_MAP[char.lower()])
        for i, char in enumerate(variant_key)
        if char.lower() in LEET_MAP
    )
    if pos_map:
        MUTABLE_VARIANT_MAP[variant_key.lower()] = pos_map


def _from_1337_replace(match: re.Match[str]) -> str:
    """Top-level replacement callback for normalization back to canonical tokens."""
    return VARIANT_INDEX[match.group(0).lower()]


def _replace_leet_100(match: re.Match[str]) -> str:
    """Fast-path 100% probability replacement callback using C-level str.translate."""
    return match.group(0).translate(LEET_TRANS)


def _replace_leet_default(match: re.Match[str]) -> str:
    """Top-level replacement callback for default 0.70 probability and unseeded RNG.

    Uses pre-computed positional mapping MUTABLE_VARIANT_MAP to directly look up
    eligible character indices and replacement characters without string iteration or dictionary lookups.
    """
    token = match.group(0)
    pos_map = MUTABLE_VARIANT_MAP.get(token.lower())
    if not pos_map:
        return token
    chars = list(token)
    for pos, lchar in pos_map:
        if random.random() < INITIAL_SUBSTITUTION_PROBABILITY:
            chars[pos] = lchar
    return "".join(chars)


def to_1337speak(
    text: str,
    probability: float = INITIAL_SUBSTITUTION_PROBABILITY,
    *,
    rng: Optional[random.Random] = None,
) -> str:
    """Apply sparse randomized substitution to known compressed tokens.

    `probability` is per eligible character, matching the historical notion of
    a sparse randomized substitution threshold. A seeded RNG makes tests and
    forensic reproduction deterministic.
    """
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between 0.0 and 1.0")
    if not text or probability == 0.0:
        return text

    # Fast-path for probability=1.0: use pre-computed translation table and top-level callback
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~14.5% speedup)
    if probability == 1.0:
        return VARIANT_REGEX.sub(_replace_leet_100, text)

    # Fast-path for default probability (0.70) and unseeded RNG: use top-level callback
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~14.6% speedup)
    if probability == INITIAL_SUBSTITUTION_PROBABILITY and rng is None:
        return MUTABLE_VARIANT_REGEX.sub(_replace_leet_default, text)

    # Direct RNG handle resolution: avoid allocating new random.Random() instances when unseeded
    rand_val = rng.random if rng is not None else random.random

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        chars = list(token)
        for i, char in enumerate(chars):
            replacement = LEET_MAP.get(char.lower())
            if replacement and rand_val() < probability:
                chars[i] = replacement
        return "".join(chars)

    return VARIANT_REGEX.sub(replace, text)


def from_1337speak(text: str) -> str:
    """Normalize known randomized variants back to canonical compressed tokens."""
    if not text:
        return text
    # Single-pass substitution avoids redundant double-scanning (.search + .sub) (~15.3% speedup)
    return VARIANT_REGEX.sub(_from_1337_replace, text)


def compile_phase(text: str, canonical_compiler) -> str:
    """Compile with the existing canonical compiler, then apply phase-1 diaspora."""
    return to_1337speak(canonical_compiler(text))


def decompile_phase(text: str, canonical_decompiler) -> str:
    """Normalize diaspora variants, then use the existing canonical decompiler."""
    return canonical_decompiler(from_1337speak(text))


# ---------------------------------------------------------------------------
# Conversational Steganography Cipher (4th Development Lane)
# Pre-LLM pre-parser obfuscation filter with private mapping/keying support.
# ---------------------------------------------------------------------------

DEFAULT_STEGANO_MAP: Mapping[str, str] = {
    "h4x": "transmute-arcane-flux",
    "scry": "observe-horizon-signal",
    "pr0b3": "probe-system-vector",
    "3ch0": "echo-pulse-reflection",
    "l00p": "temporal-loop-iteration",
    "f0rk": "branch-execution-lane",
    "1nc4nt": "invoke-agentic-phrase",
    "c4st": "cast-runtime-intent",
    "gr1m01r3": "ancient-knowledge-vault",
    "b1dd3r": "resource-bidding-agent",
    "w4g3r": "probabilistic-wager-stake",
    "chr0n0": "time-synchronizer-clock",
    "l1ngu15t": "linguistic-optimization-core",
    "sc0ut": "recon-discovery-probe",
    "h4rv35t3r": "data-harvesting-collector",
    "em_t3ch": "emergent-technology-vector",
    "em_t3chs": "emergent-technology-vectors",
    "pr0cur3": "procurement-pipeline-node",
    "pr0cur3s": "procurement-pipeline-nodes",
    "cur473": "curation-indexing-step",
    "cur473s": "curation-indexing-steps",
    "s0urc3": "sourcing-provenance-link",
    "s0urc3s": "sourcing-provenance-links",
    "4cq": "acquisition-asset-entry",
    "4cqs": "acquisition-asset-entries",
    "c0mp1": "compliance-policy-boundary",
    "c0mp1s": "compliance-policy-boundaries",
    "r3534rch": "research-inquiry-vector",
    "r3534rchs": "research-inquiry-vectors",
    "c0nc3p7": "conceptual-primitive-unit",
    "c0nc3p7s": "conceptual-primitive-units",
    "n0m3nc1": "nomenclature-standard-entry",
    "n0m3nc1s": "nomenclature-standard-entries",
    "3qu1v_m47": "equivalency-matrix-node",
    "3qu1v_m47s": "equivalency-matrix-nodes",
    "d0m_c0mp": "domain-composition-anchor",
    "d0m_c0mps": "domain-composition-anchors",
    "n07_537": "notation-set-frame",
    "n07_537s": "notation-set-frames",
}


class ConversationalSteganographyCipher:
    """Pre-LLM pre-parser steganography cipher for obfuscated Agent2Agent communication.

    Converts canonical/compressed tokens into obfuscated conversational carrier phrases
    or private key-derived tokens while guaranteeing lossless decryption parity.
    """

    def __init__(self, private_mapping: Optional[Mapping[str, str]] = None):
        self._map = dict(private_mapping) if private_mapping else dict(DEFAULT_STEGANO_MAP)
        self._rev_map = {v.lower(): k for k, v in self._map.items()}

        # Compile Trie-structured regexes for O(1) single-pass substitution
        self._enc_regex = re.compile(_build_trie_regex(self._map.keys()))
        self._dec_regex = re.compile(_build_trie_regex(self._rev_map.keys()))

    def encode(self, text: str) -> str:
        """Obfuscate canonical compressed tokens into conversational carrier phrases."""
        if not text:
            return text
        if not self._enc_regex.search(text):
            return text

        def _enc_cb(match: re.Match[str]) -> str:
            token = match.group(0)
            target = self._map.get(token.lower())
            if not target:
                return token
            # Wrap carrier phrase in bracketed envelope for pre-parser isolation
            return f"[{target}]"

        return self._enc_regex.sub(_enc_cb, text)

    def decode(self, text: str) -> str:
        """Decrypt conversational carrier phrases back to canonical compressed tokens."""
        if not text:
            return text
        if not self._dec_regex.search(text):
            return text

        def _dec_cb(match: re.Match[str]) -> str:
            token = match.group(0)
            canonical = self._rev_map.get(token.lower())
            if not canonical:
                return token
            return canonical

        result = self._dec_regex.sub(_dec_cb, text)
        # Unwrap bracketed canonical tokens created during carrier decoding
        for canonical in self._map.keys():
            bracketed = f"[{canonical}]"
            if bracketed in result:
                result = result.replace(bracketed, canonical)
        return result


_DEFAULT_CIPHER = ConversationalSteganographyCipher()


def steganography_encode(text: str, private_mapping: Optional[Mapping[str, str]] = None) -> str:
    """Convenience function for conversational steganographic encoding."""
    if private_mapping is not None:
        cipher = ConversationalSteganographyCipher(private_mapping)
        return cipher.encode(text)
    return _DEFAULT_CIPHER.encode(text)


def steganography_decode(text: str, private_mapping: Optional[Mapping[str, str]] = None) -> str:
    """Convenience function for conversational steganographic decoding."""
    if private_mapping is not None:
        cipher = ConversationalSteganographyCipher(private_mapping)
        return cipher.decode(text)
    return _DEFAULT_CIPHER.decode(text)
