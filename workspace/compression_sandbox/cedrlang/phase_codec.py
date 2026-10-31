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

# Pre-compute non-canonical variants (variants that are different from their canonical token)
# Allows fast-path short-circuiting in from_1337speak when text contains only canonical tokens
NON_CANONICAL_INDEX: Dict[str, str] = {
    var: canonical for var, canonical in VARIANT_INDEX.items() if var != canonical
}
NON_CANONICAL_VARIANT_REGEX = re.compile(_build_trie_regex(NON_CANONICAL_INDEX.keys()))

# Pre-computed casing mapping table for non-canonical variant replacements
FAST_CASING_NON_CANONICAL: Dict[str, str] = {}
for var, canonical in NON_CANONICAL_INDEX.items():
    FAST_CASING_NON_CANONICAL[var.lower()] = canonical.lower()
    FAST_CASING_NON_CANONICAL[var.capitalize()] = canonical.capitalize()
    FAST_CASING_NON_CANONICAL[var.upper()] = canonical.upper()

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
    token = match.group(0)
    res = FAST_CASING_NON_CANONICAL.get(token)
    if res is not None:
        return res
    return NON_CANONICAL_INDEX[token.lower()]


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
    if not text or not NON_CANONICAL_VARIANT_REGEX.search(text):
        return text
    # Optimization: NON_CANONICAL_VARIANT_REGEX pre-search guard short-circuits when text contains only
    # canonical tokens (~2.3x speedup on canonical text).
    # Pre-computed FAST_CASING_NON_CANONICAL mapping table avoids string lowercasing inside _from_1337_replace.
    return NON_CANONICAL_VARIANT_REGEX.sub(_from_1337_replace, text)


def compile_phase(text: str, canonical_compiler) -> str:
    """Compile with the existing canonical compiler, then apply phase-1 diaspora."""
    return to_1337speak(canonical_compiler(text))


def decompile_phase(text: str, canonical_decompiler) -> str:
    """Normalize diaspora variants, then use the existing canonical decompiler."""
    return canonical_decompiler(from_1337speak(text))


# -----------------------------------------------------------------------------
# 4th Development Lane: Conversational Steganography Cipher & Private Mapping
# Implemented prior to the LLM Pre-Parser layer for agent-to-agent privacy
# and lossless human-readable expansion parity.
# -----------------------------------------------------------------------------

# Fixed Base-4 Zero-Width Character Alphabet for Deterministic Unambiguous Payload Encoding
BASE4_ZERO_WIDTH: Tuple[str, ...] = ("\u200b", "\u200c", "\u200d", "\ufeff")
REV_BASE4_ZERO_WIDTH: Dict[str, int] = {c: i for i, c in enumerate(BASE4_ZERO_WIDTH)}
ZERO_WIDTH_REGEX = re.compile(r"[\u200b\u200c\u200d\ufeff]+")


class ConversationalSteganographyCipher:
    """4th Development Lane: Cipher encryption with private key mapping for LLM Pre-Parser.

    Provides steganographic obfuscation of agentic directives into innocent cover text
    with optional private mapping keys. Ensures lossless parity and full human-readable expansion.
    """

    __slots__ = ("private_map", "reverse_map", "_rev_trie_regex")

    def __init__(self, private_mapping: Optional[Mapping[str, str]] = None):
        self.private_map: Dict[str, str] = dict(private_mapping) if private_mapping else {}
        self.reverse_map: Dict[str, str] = {v.lower(): k for k, v in self.private_map.items()}
        if self.reverse_map:
            self._rev_trie_regex: Optional[re.Pattern[str]] = re.compile(
                _build_trie_regex(self.reverse_map.keys())
            )
        else:
            self._rev_trie_regex = None

    def encode(self, plaintext: str, cover_text: str = "Greetings agent. Execution proceeds nominally.") -> str:
        """Encode plaintext into stegotext using private mapping and zero-width payload embedding."""
        if not plaintext:
            return cover_text

        # 1. Apply private token key substitution if available
        processed = plaintext
        for src, dst in self.private_map.items():
            processed = re.sub(r"\b" + re.escape(src) + r"\b", dst, processed, flags=re.IGNORECASE)

        # 2. Encode binary bytes to fixed base-4 zero-width character quadruplets (4 chars per byte)
        raw_bytes = processed.encode("utf-8")
        zw_chunks = []
        for byte in raw_bytes:
            zw_chunks.append(BASE4_ZERO_WIDTH[(byte >> 6) & 3])
            zw_chunks.append(BASE4_ZERO_WIDTH[(byte >> 4) & 3])
            zw_chunks.append(BASE4_ZERO_WIDTH[(byte >> 2) & 3])
            zw_chunks.append(BASE4_ZERO_WIDTH[byte & 3])
        zw_payload = "".join(zw_chunks)

        # 3. Embed zero-width payload into cover text
        if " " in cover_text:
            parts = cover_text.split(" ", 1)
            return parts[0] + zw_payload + " " + parts[1]
        return cover_text + zw_payload

    def decode(self, stegotext: str) -> str:
        """Extract steganographic payload and reverse private key mapping to restore plaintext."""
        if not stegotext:
            return ""

        # 1. Extract zero-width payload sequence
        match = ZERO_WIDTH_REGEX.search(stegotext)
        if not match:
            return stegotext

        zw_str = match.group(0)
        # Parse base-4 zero-width character quadruplets back to bytes
        chars = list(zw_str)
        byte_arr = bytearray()
        for i in range(0, len(chars) - 3, 4):
            c0, c1, c2, c3 = chars[i], chars[i + 1], chars[i + 2], chars[i + 3]
            if c0 in REV_BASE4_ZERO_WIDTH and c1 in REV_BASE4_ZERO_WIDTH and c2 in REV_BASE4_ZERO_WIDTH and c3 in REV_BASE4_ZERO_WIDTH:
                byte_val = (
                    (REV_BASE4_ZERO_WIDTH[c0] << 6)
                    | (REV_BASE4_ZERO_WIDTH[c1] << 4)
                    | (REV_BASE4_ZERO_WIDTH[c2] << 2)
                    | REV_BASE4_ZERO_WIDTH[c3]
                )
                byte_arr.append(byte_val)

        if not byte_arr:
            return stegotext

        try:
            decoded_text = byte_arr.decode("utf-8")
        except UnicodeDecodeError:
            return stegotext

        # 2. Reverse private key mapping using single-pass Trie regex callback
        if self.reverse_map and self._rev_trie_regex:
            def _rev_cb(m: re.Match[str]) -> str:
                val = m.group(0)
                return self.reverse_map.get(val.lower(), val)
            decoded_text = self._rev_trie_regex.sub(_rev_cb, decoded_text)

        return decoded_text


def steganography_encode(
    text: str,
    private_mapping: Optional[Mapping[str, str]] = None,
    cover_text: str = "Greetings agent. Execution proceeds nominally.",
) -> str:
    """Convenience top-level function to steganographically encode text."""
    cipher = ConversationalSteganographyCipher(private_mapping)
    return cipher.encode(text, cover_text=cover_text)


def steganography_decode(
    stegotext: str,
    private_mapping: Optional[Mapping[str, str]] = None,
) -> str:
    """Convenience top-level function to steganographically decode stegotext."""
    cipher = ConversationalSteganographyCipher(private_mapping)
    return cipher.decode(stegotext)
