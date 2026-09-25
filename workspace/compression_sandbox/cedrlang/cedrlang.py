#!/usr/bin/env python3
"""
CedrLang – Agentic Compression Protocol
Minimal token language for LLM↔LLM coordination.
Inspired by caveman prompting, symbolic substitution & minified JSON.

Usage:
  cedrlang compress "Your natural language instruction here"
  cedrlang expand "→cmd:build|args:clean"
  cedrlang stats  # show token savings over baseline
  cedrlang serve  # start filter proxy for deepcli/synthegration
  cedrlang compile <file_or_text> [-o output_file]
  cedrlang decompile <file_or_text> [-o output_file]

Integrate with deepcli: add `--cedr` flag to auto-compress prompts.
"""

import sys
import re
import json
import argparse
from typing import Dict, List, Any, Tuple
from pathlib import Path

SYMBOL_MAP = {
    " leads to ": " → ",
    " results in ": " → ",
    " implies ": " → ",
    " because ": " ← ",
    " therefore ": " ∴ ",
    " since ": " ∵ ",
    " and then ": " ⇒ ",
    " compare ": " vs ",
    " versus ": " vs ",
    " create ": " + ",
    " delete ": " - ",
    " update ": " ~ ",
    " read ": " > ",
    " write ": " < ",
    " execute ": " ! ",
    " query ": " ? ",
    " answer ": " = ",
    " set ": " := ",
    " get ": " . ",
    " if ": " ? ",
    " then ": " ⇒ ",
    " else ": " | ",
    " and ": " ∧ ",
    " or ": " ∨ ",
    " not ": " ¬ ",
    " true ": " T ",
    " false ": " F ",
    " success ": " ✓ ",
    " fail ": " ✗ ",
    " pending ": " … ",
    " error ": " ⚠ ",
    " warning ": " ⚠ ",
}

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "and", "for", "in", "that", "with", "on", "at", "by",
    "this", "these", "those", "it", "they", "we", "you", "he", "she"
}

MAPPINGS = [
    ("transmute", "h4x"),
    ("scry", "scry"),
    ("probe", "pr0b3"),
    ("echo", "3ch0"),
    ("time loop", "l00p"),
    ("branch", "f0rk"),
    ("incantation", "1nc4nt"),
    ("cast", "c4st"),
    ("grimoire", "gr1m01r3"),
    ("bidder", "b1dd3r"),
    ("wager", "w4g3r"),
    ("chronomancer", "chr0n0"),
    ("linguist", "l1ngu15t"),
    ("scout", "sc0ut"),
    ("harvester", "h4rv35t3r"),
    ("emerging technologies", "em_t3chs"),
    ("emerging technology", "em_t3ch"),
    ("procurements", "pr0cur3s"),
    ("procurement", "pr0cur3"),
    ("curations", "cur473s"),
    ("curation", "cur473"),
    ("sourcings", "s0urc3s"),
    ("sourcing", "s0urc3"),
    ("acquisitions", "4cqs"),
    ("acquisition", "4cq"),
    ("compliances", "c0mp1s"),
    ("compliance", "c0mp1"),
]

def capitalize_word(w: str) -> str:
    if " " in w:
        return " ".join(capitalize_word(part) for part in w.split(" "))
    chars = list(w)
    for i, c in enumerate(chars):
        if c.isalpha():
            chars[i] = c.upper()
            break
    return "".join(chars)

def lowercase_word(w: str) -> str:
    return w.lower()

def uppercase_word(w: str) -> str:
    return w.upper()

def is_capitalized(w: str) -> bool:
    for c in w:
        if c.isalpha():
            return c.isupper()
    return False

def apply_casing(src: str, dst: str) -> str:
    if src.isupper():
        return uppercase_word(dst)
    if is_capitalized(src):
        return capitalize_word(dst)
    return lowercase_word(dst)

SYMBOL_REGEXES = {phrase: re.compile(re.escape(phrase), re.IGNORECASE) for phrase in SYMBOL_MAP}
INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
BOLD_PATTERN_2 = re.compile(r'\*\*([^*]+)\*\*')
BOLD_PATTERN_1 = re.compile(r'\*([^*]+)\*')
BOLD_PATTERN_UNDER2 = re.compile(r'__([^_]+)__')
BOLD_PATTERN_UNDER1 = re.compile(r'_([^_]+)_')
PATH_REGEX = re.compile(
    r'\b(?:~?/)?[\w\-]+(?:/[\w\-]+)*\.(?:py|js|json|md|yaml|sh|txt|yml|db|jsonl|wasm|html|cffi)\b|\b/?[\w\-]+/[\w\-\./]+\b'
)
DECIMAL_PATTERN = re.compile(r'\b\d+\.\d+\b')
SPACES_PATTERN = re.compile(r'\s+')
PUNCTUATION_PATTERN = re.compile(r'[.,!?;:]$')
SORTED_MAPPINGS_COMP = sorted(MAPPINGS, key=lambda x: len(x[0]), reverse=True)
SORTED_MAPPINGS_DECOMP = sorted(MAPPINGS, key=lambda x: len(x[1]), reverse=True)
COMP_REGEXES = [(re.compile(r'\b' + re.escape(human) + r'\b', re.IGNORECASE), comp) for human, comp in SORTED_MAPPINGS_COMP]
DECOMP_REGEXES = [(re.compile(r'\b' + re.escape(comp) + r'\b', re.IGNORECASE), human) for human, comp in SORTED_MAPPINGS_DECOMP]

def build_trie_regex(words: List[str]) -> str:
    trie: Dict[str, Any] = {}
    for w in words:
        curr = trie
        for char in w.lower():
            curr = curr.setdefault(char, {})
        curr[""] = None
    def _trie_to_regex(node: Dict[str, Any]) -> str:
        if not node:
            return ""
        ending = "" in node
        chars = [k for k in node if k != ""]
        if not chars:
            return ""
        children = []
        for char in chars:
            sub = _trie_to_regex(node[char])
            if sub:
                children.append(re.escape(char) + sub)
            else:
                children.append(re.escape(char))
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
    return r'\b(?:' + _trie_to_regex(trie) + r')\b'

COMP_DICT = {human.lower(): comp for human, comp in SORTED_MAPPINGS_COMP}
COMP_SINGLE_REGEX = re.compile(build_trie_regex([human for human, _ in SORTED_MAPPINGS_COMP]), re.IGNORECASE)
DECOMP_DICT = {comp.lower(): human for human, comp in SORTED_MAPPINGS_DECOMP}
DECOMP_SINGLE_REGEX = re.compile(build_trie_regex([comp for _, comp in SORTED_MAPPINGS_DECOMP]), re.IGNORECASE)
FAST_CASING_COMP: Dict[str, str] = {}
for human, comp in SORTED_MAPPINGS_COMP:
    FAST_CASING_COMP[human.lower()] = lowercase_word(comp)
    FAST_CASING_COMP[capitalize_word(human)] = capitalize_word(comp)
    FAST_CASING_COMP[human.upper()] = uppercase_word(comp)
FAST_CASING_DECOMP: Dict[str, str] = {}
for human, comp in SORTED_MAPPINGS_DECOMP:
    FAST_CASING_DECOMP[comp.lower()] = lowercase_word(human)
    FAST_CASING_DECOMP[capitalize_word(comp)] = capitalize_word(human)
    FAST_CASING_DECOMP[comp.upper()] = uppercase_word(human)

def compress(text: str, aggressive: bool = True) -> str:
    if not text:
        return ""
    result = text[:]
    for phrase, pattern in SYMBOL_REGEXES.items():
        result = pattern.sub(SYMBOL_MAP[phrase], result)
    if not aggressive:
        return result.strip()
    words = result.split()
    filtered = [w for w in words if w.lower() not in STOPWORDS]
    result = " ".join(filtered)
    result = SPACES_PATTERN.sub(' ', result).strip()
    result = PUNCTUATION_PATTERN.sub('', result)
    return result

def caveman(text: str, max_up: bool = False) -> str:
    t = text.upper() if max_up else text
    for phrase, pattern in SYMBOL_REGEXES.items():
        t = pattern.sub(SYMBOL_MAP[phrase], t)
    words = [w for w in t.split() if w.lower() not in STOPWORDS]
    return SPACES_PATTERN.sub(' ', " ".join(words)).strip()

def expand(cedr: str) -> str:
    rev_map = {v.strip(): k.strip() for k, v in SYMBOL_MAP.items()}
    result = cedr
    for sym, phrase in rev_map.items():
        result = result.replace(sym, f" {phrase} ")
    result = SPACES_PATTERN.sub(' ', result)
    return result.strip()

def _sub_cb_comp(m: re.Match[str]) -> str:
    val = m.group(0)
    res = FAST_CASING_COMP.get(val)
    if res is not None:
        return res
    return apply_casing(val, COMP_DICT[val.lower()])

def _sub_cb_decomp(m: re.Match[str]) -> str:
    val = m.group(0)
    res = FAST_CASING_DECOMP.get(val)
    if res is not None:
        return res
    return apply_casing(val, DECOMP_DICT[val.lower()])

def translate_text_raw(text: str, to_compressed: bool) -> str:
    pattern = COMP_SINGLE_REGEX if to_compressed else DECOMP_SINGLE_REGEX
    cb = _sub_cb_comp if to_compressed else _sub_cb_decomp
    return pattern.sub(cb, text)

class LinePlaceholderContext:
    __slots__ = ("placeholders", "to_compressed")
    def __init__(self, to_compressed: bool):
        self.placeholders: List[Tuple[str, str]] = []
        self.to_compressed = to_compressed
    def add_placeholder(self, val: str) -> str:
        ph = f"§§PL_{len(self.placeholders)}§§"
        self.placeholders.append((ph, val))
        return ph
    def raw_match_repl(self, match: re.Match[str]) -> str:
        ph = f"§§PL_{len(self.placeholders)}§§"
        self.placeholders.append((ph, match.group(0)))
        return ph
    def link_repl(self, match: re.Match[str]) -> str:
        text = match.group(1)
        url = match.group(2)
        translated_text = translate_text_raw(text, self.to_compressed)
        return self.add_placeholder(f"[{translated_text}]({url})")
    def bold_repl_2(self, match: re.Match[str]) -> str:
        text = match.group(1)
        translated_text = translate_text_raw(text, self.to_compressed)
        return self.add_placeholder(f"**{translated_text}**")
    def bold_repl_1(self, match: re.Match[str]) -> str:
        text = match.group(1)
        translated_text = translate_text_raw(text, self.to_compressed)
        return self.add_placeholder(f"*{translated_text}*")
    def bold_repl_under2(self, match: re.Match[str]) -> str:
        text = match.group(1)
        translated_text = translate_text_raw(text, self.to_compressed)
        return self.add_placeholder(f"____{translated_text}____")
    def bold_repl_under1(self, match: re.Match[str]) -> str:
        text = match.group(1)
        translated_text = translate_text_raw(text, self.to_compressed)
        return self.add_placeholder(f"_{translated_text}_")

def translate_line(line: str, to_compressed: bool) -> str:
    matcher = COMP_SINGLE_REGEX if to_compressed else DECOMP_SINGLE_REGEX
    if not matcher.search(line):
        return line
    ctx = LinePlaceholderContext(to_compressed)
    if "`" in line:
        line = INLINE_CODE_PATTERN.sub(ctx.raw_match_repl, line)
    if "<" in line:
        line = HTML_TAG_PATTERN.sub(ctx.raw_match_repl, line)
    if "[" in line:
        line = LINK_PATTERN.sub(ctx.link_repl, line)
    if "*" in line:
        line = BOLD_PATTERN_2.sub(ctx.bold_repl_2, line)
        line = BOLD_PATTERN_1.sub(ctx.bold_repl_1, line)
    if "_" in line:
        line = BOLD_PATTERN_UNDER2.sub(ctx.bold_repl_under2, line)
        line = BOLD_PATTERN_UNDER1.sub(ctx.bold_repl_under1, line)
    if "/" in line or "\\" in line or "~" in line or "." in line:
        line = PATH_REGEX.sub(ctx.raw_match_repl, line)
    if "." in line and DECIMAL_PATTERN.search(line):
        line = DECIMAL_PATTERN.sub(ctx.raw_match_repl, line)
    line = translate_text_raw(line, to_compressed)
    for ph, orig in reversed(ctx.placeholders):
        if orig.startswith("____") and orig.endswith("____"):
            content = orig[4:-4]
            orig = f"__{content}__"
        line = line.replace(ph, orig)
    return line

def compile_doc(text: str) -> str:
    if not isinstance(text, str) or not text or not COMP_SINGLE_REGEX.search(text):
        return text if isinstance(text, str) else ""
    lines = text.splitlines(keepends=True)
    compiled_lines = []
    in_fenced_code = False
    for line in lines:
        if "```" in line and line.strip().startswith("```"):
            in_fenced_code = not in_fenced_code
            compiled_lines.append(line)
            continue
        if in_fenced_code:
            compiled_lines.append(line)
        else:
            compiled_lines.append(translate_line(line, to_compressed=True))
    return "".join(compiled_lines)

def decompile_doc(text: str) -> str:
    if not isinstance(text, str) or not text or not DECOMP_SINGLE_REGEX.search(text):
        return text if isinstance(text, str) else ""
    lines = text.splitlines(keepends=True)
    decompiled_lines = []
    in_fenced_code = False
    for line in lines:
        if "```" in line and line.strip().startswith("```"):
            in_fenced_code = not in_fenced_code
            decompiled_lines.append(line)
            continue
        if in_fenced_code:
            decompiled_lines.append(line)
        else:
            decompiled_lines.append(translate_line(line, to_compressed=False))
    return "".join(decompiled_lines)

def count_tokens(text: str) -> int:
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

def deepcli_filter(prompt: str) -> str:
    return compress(prompt, aggressive=True)

def main():
    parser = argparse.ArgumentParser(description="CedrLang – Agentic Compression Protocol")
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_compress = subparsers.add_parser("compress", help="Compress natural language to CedrLang")
    p_compress.add_argument("text", nargs="*", help="Text to compress")
    p_compress.add_argument("--aggressive", action="store_true", default=True)
    p_compress.add_argument("--no-aggressive", dest="aggressive", action="store_false")
    p_expand = subparsers.add_parser("expand", help="Expand CedrLang to approximate English")
    p_expand.add_argument("text", nargs="*", help="CedrLang text to expand")
    p_compile = subparsers.add_parser("compile", help="Compile markdown to CedrLang")
    p_compile.add_argument("file_or_text", nargs="*")
    p_compile.add_argument("-o", "--output")
    p_decompile = subparsers.add_parser("decompile", help="Decompile CedrLang markdown")
    p_decompile.add_argument("file_or_text", nargs="*")
    p_decompile.add_argument("-o", "--output")
    p_stats = subparsers.add_parser("stats", help="Show token savings stats")
    p_stats.add_argument("original")
    p_stats.add_argument("--compressed")
    p_serve = subparsers.add_parser("serve", help="Read stdin, compress, write stdout")
    args = parser.parse_args()
    if args.command == "compress":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        print(compress(text, aggressive=args.aggressive))
    elif args.command == "expand":
        text = " ".join(args.text) if args.text else sys.stdin.read().strip()
        if not text:
            print("Error: No input text", file=sys.stderr)
            sys.exit(1)
        print(expand(text))
    elif args.command == "compile":
        input_str = ""
        if args.file_or_text:
            path_candidate = " ".join(args.file_or_text)
            if Path(path_candidate).exists():
                input_str = Path(path_candidate).read_text()
            else:
                input_str = path_candidate
        else:
            input_str = sys.stdin.read()
        if not input_str:
            print("Error: No input text or file", file=sys.stderr)
            sys.exit(1)
        result = compile_doc(input_str)
        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result, end="")
    elif args.command == "decompile":
        input_str = ""
        if args.file_or_text:
            path_candidate = " ".join(args.file_or_text)
            if Path(path_candidate).exists():
                input_str = Path(path_candidate).read_text()
            else:
                input_str = path_candidate
        else:
            input_str = sys.stdin.read()
        if not input_str:
            print("Error: No input text or file", file=sys.stderr)
            sys.exit(1)
        result = decompile_doc(input_str)
        if args.output:
            Path(args.output).write_text(result)
        else:
            print(result, end="")
    elif args.command == "stats":
        original = args.original
        compressed = args.compressed if args.compressed else compress(original)
        stats = stats_report(original, compressed)
        print(json.dumps(stats, indent=2))
        print(f"\n✓ Savings: {stats['savings_percent']}% tokens")
    elif args.command == "serve":
        for line in sys.stdin:
            sys.stdout.write(compress(line.rstrip('\n'), aggressive=True) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
