#!/usr/bin/env python3
"""
CedrLang – Agentic Compression Protocol v2
Minimal token language for LLM↔LLM coordination.
Inspired by caveman prompting, symbolic substitution & minified JSON.

Usage:
  cedrlang compress "Your natural language instruction here"
  cedrlang expand "→cmd:build|args:clean"
  cedrlang stats  # show token savings over baseline
  cedrlang serve  # start filter proxy for deepcli/synthegration
  cedrlang compile <input_file> <output_file>
  cedrlang decompile <input_file> <output_file>
"""

import sys
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

# ------------------------------------------------------------
# 1. Core mapping tables (symbolic & Grimoire substitution)
# ------------------------------------------------------------
SYMBOL_MAP = {
    "leads to": "→",
    "results in": "→",
    "implies": "→",
    "because": "←",
    "therefore": "∴",
    "since": "∵",
    "and then": "⇒",
    "compare": "vs",
    "versus": "vs",
    "create": "+",
    "delete": "-",
    "update": "~",
    "read": ">",
    "write": "<",
    "execute": "!",
    "query": "?",
    "answer": "=",
    "set": ":=",
    "get": ".",
    "if": "?",
    "then": "⇒",
    "else": "|",
    "and": "∧",
    "or": "∨",
    "not": "¬",
    "true": "T",
    "false": "F",
    "success": "✓",
    "fail": "✗",
    "pending": "…",
    "error": "⚠",
    "warning": "⚠",
}

GRIMOIRE_MAP = {
    "ArchWizard": "4rchW1z4rd",
    "Caster": "C4573r",
    "Mana": "M4n4",
    "Spellbook": "Sp3llb00k",
    "Rune": "Run3",
    "Transmute": "Tr4n5mu73",
    "Scry": "5cry",
    "Probe": "Pr0b3",
    "Echo": "3ch0",
    "Grimoire": "Gr1m01r3",
    "Phylactery": "Phyl4c73ry",
    "Bidder": "b1dd3r",
    "Wager": "w4g3r",
    "Branch": "f0rk",
    "Incantation": "1nc4nt",
    "Cast": "c4st",
    "Chronomancer": "chr0n0",
    "Linguist": "l1ngu15t",
    "Scout": "sc0ut",
    "Harvester": "h4rv35t3r",
    "Refactor": "Tr4n5mu73",
    "Review": "5cry",
    "Inspect": "5cry",
    "Test": "Pr0b3",
    "Score": "M4n4",
}

LEET_CHARS = {
    'A': '4', 'a': '4',
    'B': '8', 'b': '8',
    'E': '3', 'e': '3',
    'G': '6', 'g': '9',
    'I': '1', 'i': '1',
    'O': '0', 'o': '0',
    'S': '5', 's': '$',
    'T': '7', 't': '+',
    'Z': '2', 'z': '2'
}

DECOMP_CHARS = {
    '4': 'a', '8': 'b', '3': 'e', '1': 'i', '0': 'o',
    '5': 's', '$': 's', '+': 't', '2': 'z', '7': 't', '9': 'g'
}

# Create reverse mappings for exact expansion lookup
REV_SYMBOL_MAP = {v: k for k, v in SYMBOL_MAP.items()}
REV_GRIMOIRE_MAP = {v: k for k, v in GRIMOIRE_MAP.items()}

# ------------------------------------------------------------
# 2. Helper Utilities & O(N) Translation Engine
# ------------------------------------------------------------
def single_pass_replace(text: str, mapping: Dict[str, str]) -> str:
    """Perform O(N) single-pass substitution of mapped keys."""
    if not text:
        return text
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    pattern_parts = []
    for k in sorted_keys:
        if k[0].isalnum() and k[-1].isalnum():
            pattern_parts.append(r'\b' + re.escape(k) + r'\b')
        else:
            pattern_parts.append(re.escape(k))
    pattern = re.compile("|".join(pattern_parts), re.IGNORECASE)
    lower_mapping = {k.lower(): v for k, v in mapping.items()}
    # Clean padding spacing to keep them token-friendly and readable
    return pattern.sub(lambda m: f" {lower_mapping.get(m.group(0).lower(), m.group(0))} ", text)


def protect_placeholders(text: str) -> Tuple[str, List[str]]:
    """Extract code blocks, inline code, HTML, links, and bold/emphasis to prevent corruption."""
    placeholders = []
    patterns = [
        r'```[\s\S]*?```',
        r'`[^`\n]*?`',
        r'\!?\[[^\]]*?\]\([^\)]*?\)',
        r'</?[a-zA-Z][^>\n]*?>',      # plausible HTML tags restricted to a single line
        r'\*\*[^*\n]+?\*\*',          # bold strictly on single line to prevent spanning across bullets
        r'\*[^*\n]+?\*'               # italics strictly on single line to prevent spanning across bullets
    ]
    combined_pattern = re.compile("|".join(patterns))
    def repl(match):
        val = match.group(0)
        idx = len(placeholders)
        placeholders.append(val)
        return f"__CEDR_PLACE_HOLDER_{idx}__"
    return combined_pattern.sub(repl, text), placeholders


def restore_placeholders(text: str, placeholders: List[str]) -> str:
    """Restore originally protected constructs."""
    for idx, val in enumerate(placeholders):
        text = text.replace(f"__CEDR_PLACE_HOLDER_{idx}__", val)
    return text


def is_leet_word(w: str) -> bool:
    """Determine if a word should be decompiled, avoiding numbers, placeholders, decimals/filenames."""
    if "__CEDR_PLACE_HOLDER_" in w:
        return False
    if "." in w or "/" in w or "\\" in w:
        return False
    # Strip any surrounding punctuation to analyze the word core
    clean_w = re.sub(r'[^a-zA-Z0-9$]', '', w)
    if not clean_w or clean_w.isdigit():
        return False
    # Must contain at least one letter or leet-replaced character
    return any(c.isalpha() or c in DECOMP_CHARS for c in clean_w)


def to_1337speak(text: str) -> str:
    """Apply basic 1337 character replacements to standard words sparsely and randomly, preserving line structures."""
    import random
    lines = text.splitlines()
    res_lines = []
    all_symbols = set(SYMBOL_MAP.values()) | set(GRIMOIRE_MAP.values())
    for line in lines:
        words = line.split(" ")
        res_words = []
        for w in words:
            if "__CEDR_PLACE_HOLDER_" in w or w in all_symbols:
                res_words.append(w)
            elif w.isalpha():
                # Sparsely substitute characters with a 70% probability for organic, distinct outputs
                res_words.append("".join(LEET_CHARS.get(c, c) if random.random() < 0.7 else c for c in w))
            else:
                res_words.append(w)
        res_lines.append(" ".join(res_words))
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(res_lines) + suffix


def from_1337speak(text: str) -> str:
    """Reverse 1337 character replacements approximately, preserving line structures."""
    lines = text.splitlines()
    res_lines = []
    all_symbols = set(SYMBOL_MAP.values()) | set(GRIMOIRE_MAP.values())
    for line in lines:
        words = line.split(" ")
        res_words = []
        for w in words:
            if "__CEDR_PLACE_HOLDER_" in w or w in all_symbols:
                res_words.append(w)
            elif is_leet_word(w):
                res_words.append("".join(DECOMP_CHARS.get(c, c) for c in w))
            else:
                res_words.append(w)
        res_lines.append(" ".join(res_words))
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(res_lines) + suffix


# ------------------------------------------------------------
# 3. 6-Line Caveman Stopword Stripper
# ------------------------------------------------------------
def caveman_strip(text: str) -> str:
    p = r'\b(a|an|the|is|are|was|were|be|been|being|to|of|and|for|in|that|with|on|at|by|this|these|those|it|they|we|you|he|she)\b'
    t = re.sub(p, '', text, flags=re.IGNORECASE)
    # preserve line breaks while collapsing redundant spaces
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in t.splitlines()]
    return '\n'.join(lines)


# ------------------------------------------------------------
# 4. Compressor & Expander Interfaces
# ------------------------------------------------------------
def compress(text: str, aggressive: bool = True) -> str:
    """Convert natural language to CedrLang."""
    if not text:
        return ""
    # 1. Protect formatting and markup
    text, placeholders = protect_placeholders(text)
    # 2. Run single-pass symbols & Grimoire translations
    text = single_pass_replace(text, SYMBOL_MAP)
    text = single_pass_replace(text, GRIMOIRE_MAP)
    # 3. Apply Caveman Stripping
    if aggressive:
        text = caveman_strip(text)
    # 4. Convert standard words to 1337speak
    text = to_1337speak(text)
    # 5. Clean up duplicate spacing
    text = re.sub(r'[ \t]+', ' ', text)
    # 6. Restore placeholders
    return restore_placeholders(text, placeholders)


def expand_token(word: str) -> str:
    """Translate symbols/Grimoire exact matches while preserving leading/trailing punctuation."""
    if word in REV_GRIMOIRE_MAP:
        return REV_GRIMOIRE_MAP[word]
    if word in REV_SYMBOL_MAP:
        return REV_SYMBOL_MAP[word]
    # Check with punctuation stripped, but only if it contains alphanumeric characters
    if any(c.isalnum() for c in word):
        m = re.match(r'^([^\w\s]*)(.*?)([^\w\s]*)$', word)
        if m:
            lead, core, trail = m.groups()
            if core in REV_GRIMOIRE_MAP:
                return f"{lead}{REV_GRIMOIRE_MAP[core]}{trail}"
            if core in REV_SYMBOL_MAP:
                return f"{lead}{REV_SYMBOL_MAP[core]}{trail}"
    return word


def expand(cedr: str) -> str:
    """Expand CedrLang back to approximate natural language, preserving document layouts."""
    if not cedr:
        return ""
    cedr, placeholders = protect_placeholders(cedr)
    # 1. Decompile character replacements
    cedr = from_1337speak(cedr)
    # 2. Expand symbols & Grimoire mappings via token boundaries
    lines = cedr.splitlines()
    res_lines = []
    for line in lines:
        # Check if line is a markdown list item/bullet to avoid translating bullet marks
        bullet_match = re.match(r'^(\s*[-+*]|\s*\d+\.)\s', line)
        if bullet_match:
            prefix = bullet_match.group(0)
            rest = line[len(prefix):]
            words = rest.split(" ")
            expanded_words = [expand_token(w) for w in words]
            res_lines.append(prefix + " ".join(expanded_words))
        else:
            words = line.split(" ")
            expanded_words = [expand_token(w) for w in words]
            res_lines.append(" ".join(expanded_words))

    suffix = "\n" if cedr.endswith("\n") else ""
    cedr = "\n".join(res_lines) + suffix
    # 3. Clean up spaces and restore placeholders
    cedr = re.sub(r'[ \t]+', ' ', cedr)
    return restore_placeholders(cedr, placeholders).strip()


# ------------------------------------------------------------
# 5. Public helper for external integrations
# ------------------------------------------------------------
def deepcli_filter(prompt: str) -> str:
    """Hook for deepcli – compress user prompt before sending to API."""
    return compress(prompt, aggressive=True)


# ------------------------------------------------------------
# 6. Token counter (using cl100k_base approximation)
# ------------------------------------------------------------
def count_tokens(text: str) -> int:
    """Rough token count using whitespace + punctuation heuristic."""
    tokens = re.findall(r'\b\w+\b|[^\w\s]', text)
    return len(tokens)


def stats_report(original: str, compressed: str) -> Dict[str, Any]:
    orig_tokens = count_tokens(original)
    comp_tokens = count_tokens(compressed)
    savings = ((orig_tokens - comp_tokens) / orig_tokens) * 100 if orig_tokens else 0
    return {
        "original_tokens": orig_tokens,
        "compressed_tokens": comp_tokens,
        "savings_percent": round(savings, 2),
        "original_chars": len(original),
        "compressed_chars": len(compressed)
    }


# ------------------------------------------------------------
# 7. CLI & main
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="CedrLang – Agentic Compression Protocol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compress command
    p_compress = subparsers.add_parser("compress", help="Compress natural language to CedrLang")
    p_compress.add_argument("text", nargs="*", help="Text to compress")
    p_compress.add_argument("--aggressive", action="store_true", default=True, help="Enable stopword stripping (default)")
    p_compress.add_argument("--no-aggressive", dest="aggressive", action="store_false", help="Disable stopword stripping")

    # expand command
    p_expand = subparsers.add_parser("expand", help="Expand CedrLang to approximate English")
    p_expand.add_argument("text", nargs="*", help="CedrLang text to expand")

    # stats command
    p_stats = subparsers.add_parser("stats", help="Show token savings stats")
    p_stats.add_argument("original", help="Original natural language")
    p_stats.add_argument("--compressed", help="Optional compressed text (otherwise compress automatically)")

    # serve command
    p_serve = subparsers.add_parser("serve", help="Read stdin, compress, write stdout (for integration)")

    # compile command
    p_compile = subparsers.add_parser("compile", help="Compile human readable file to CedrLang")
    p_compile.add_argument("input_file", help="Input file path")
    p_compile.add_argument("output_file", help="Output file path")

    # decompile command
    p_decompile = subparsers.add_parser("decompile", help="Decompile CedrLang file to human readable")
    p_decompile.add_argument("input_file", help="Input file path")
    p_decompile.add_argument("output_file", help="Output file path")

    args = parser.parse_args()

    if args.command == "compress":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        result = compress(text, aggressive=args.aggressive)
        print(result)

    elif args.command == "expand":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        result = expand(text)
        print(result)

    elif args.command == "stats":
        original = args.original
        compressed = args.compressed if args.compressed else compress(original)
        stats = stats_report(original, compressed)
        print(json.dumps(stats, indent=2))
        print(f"\n✓ Savings: {stats['savings_percent']}% tokens")

    elif args.command == "serve":
        for line in sys.stdin:
            compressed_line = compress(line.rstrip('\n'), aggressive=True)
            sys.stdout.write(compressed_line + "\n")
            sys.stdout.flush()

    elif args.command in ("compile", "decompile"):
        in_path = Path(args.input_file)
        out_path = Path(args.output_file)
        if not in_path.exists():
            print(f"Error: {in_path} does not exist", file=sys.stderr)
            sys.exit(1)
        content = in_path.read_text(encoding="utf-8")
        if args.command == "compile":
            processed = compress(content, aggressive=True)
        else:
            processed = expand(content)
        out_path.write_text(processed, encoding="utf-8")
        print(f"✓ Processed {in_path} -> {out_path} successfully.")

if __name__ == "__main__":
    main()
