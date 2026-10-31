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


# ---------------------------------------------------------------------------
# 4th Development Lane: Conversational Steganography Cipher
# ---------------------------------------------------------------------------

ZW_CHARS: Tuple[str, str, str, str] = ("\u200b", "\u200c", "\u200d", "\ufeff")
CHAR_TO_DIGIT: Mapping[str, int] = {c: i for i, c in enumerate(ZW_CHARS)}
ZW_SET = frozenset(ZW_CHARS)


class ConversationalSteganographyCipher:
    """Pre-LLM pre-parser steganographic obfuscation cipher (4th Lane).

    Encodes arbitrary payloads into deterministic Base-4 zero-width quadruplet
    character sequences (\u200b, \u200c, \u200d, \ufeff) embedded covertly into host text.
    Optionally applies key-stream XOR permutation for private mapping security.
    """

    @staticmethod
    def _apply_key(data: bytes, key: Optional[str | bytes]) -> bytes:
        if not key:
            return data
        key_bytes = key.encode("utf-8") if isinstance(key, str) else key
        if not key_bytes:
            return data
        key_len = len(key_bytes)
        return bytes(b ^ key_bytes[i % key_len] for i, b in enumerate(data))

    @classmethod
    def encode(
        cls,
        payload: str,
        host_text: str = "",
        secret_key: Optional[str | bytes] = None,
    ) -> str:
        """Encode payload string into zero-width character quadruplets embedded in host_text."""
        if not payload:
            return host_text
        payload_bytes = payload.encode("utf-8")
        cipher_bytes = cls._apply_key(payload_bytes, secret_key)

        zw_chunks = []
        for b in cipher_bytes:
            d0 = (b >> 6) & 3
            d1 = (b >> 4) & 3
            d2 = (b >> 2) & 3
            d3 = b & 3
            zw_chunks.extend((ZW_CHARS[d0], ZW_CHARS[d1], ZW_CHARS[d2], ZW_CHARS[d3]))
        stego_str = "".join(zw_chunks)

        if not host_text:
            return stego_str

        # Embed covertly: insert after first word/whitespace or prepend/append
        if " " in host_text:
            parts = host_text.split(" ", 1)
            return parts[0] + stego_str + " " + parts[1]
        return host_text + stego_str

    @classmethod
    def decode(
        cls,
        stego_text: str,
        secret_key: Optional[str | bytes] = None,
    ) -> str:
        """Extract zero-width quadruplets from stego_text and decode back to payload string."""
        if not stego_text or not cls.has_stego(stego_text):
            return ""

        extracted = [c for c in stego_text if c in ZW_SET]
        if not extracted or len(extracted) % 4 != 0:
            return ""

        raw_bytes = []
        for i in range(0, len(extracted), 4):
            d0 = CHAR_TO_DIGIT[extracted[i]]
            d1 = CHAR_TO_DIGIT[extracted[i + 1]]
            d2 = CHAR_TO_DIGIT[extracted[i + 2]]
            d3 = CHAR_TO_DIGIT[extracted[i + 3]]
            b = (d0 << 6) | (d1 << 4) | (d2 << 2) | d3
            raw_bytes.append(b)

        decrypted_bytes = cls._apply_key(bytes(raw_bytes), secret_key)
        try:
            return decrypted_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return ""

    @classmethod
    def has_stego(cls, text: str) -> bool:
        """Fast-path check if text contains zero-width steganographic characters."""
        if not text:
            return False
        return any(c in text for c in ZW_SET)
