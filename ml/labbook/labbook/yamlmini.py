"""A deliberately small YAML subset: block mappings, block sequences,
flow scalar lists/maps, and plain/quoted scalars.

labbook emits its IR in this subset (diffable, assertable — ledger row 6)
and reads project catalogs written in it. The subset is the whole point:
anything outside it is rejected with a named error instead of being
half-parsed (row 7). No external dependency — the fleet's packages are
stdlib-only wherever the evidence allows.
"""

from .errors import LabbookError


# ------------------------------------------------------------------ emit

_PLAIN_OK = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_./<>+-= @:"
)


def _needs_quote(s: str) -> bool:
    if s == "" or s != s.strip():
        return True
    if any(c not in _PLAIN_OK for c in s):
        return True
    if _scalar(s) != s:  # would parse back as non-string
        return True
    return False


def _emit_scalar(v) -> str:
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, int):
        return str(v)
    s = str(v)
    if _needs_quote(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def _is_scalar(v) -> bool:
    return v is None or isinstance(v, (str, int, float, bool))


def dump(value, indent=0) -> str:
    """Serialize a dict/list/scalar tree to the subset. Returns text."""
    pad = "  " * indent
    lines = []
    if isinstance(value, dict):
        if not value:
            return pad + "{}\n"
        for k, v in value.items():
            key = _emit_scalar(str(k))
            if _is_scalar(v):
                lines.append(f"{pad}{key}: {_emit_scalar(v)}")
            elif isinstance(v, list) and all(_is_scalar(x) for x in v):
                flow = ", ".join(_emit_scalar(x) for x in v)
                lines.append(f"{pad}{key}: [{flow}]")
            elif isinstance(v, dict) and not v:
                lines.append(f"{pad}{key}: {{}}")
            elif isinstance(v, list) and not v:
                lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}:")
                lines.append(dump(v, indent + 1).rstrip("\n"))
    elif isinstance(value, list):
        if not value:
            return pad + "[]\n"
        for item in value:
            if _is_scalar(item):
                lines.append(f"{pad}- {_emit_scalar(item)}")
            elif isinstance(item, dict):
                sub = dump(item, indent + 1).splitlines()
                lines.append(f"{pad}- " + sub[0].lstrip())
                lines.extend(sub[1:])
            else:
                lines.append(f"{pad}-")
                lines.append(dump(item, indent + 1).rstrip("\n"))
    else:
        lines.append(pad + _emit_scalar(value))
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ parse


def _scalar(tok: str):
    tok = tok.strip()
    if tok in ("null", "~", ""):
        return None
    if tok == "true":
        return True
    if tok == "false":
        return False
    if tok.startswith('"') and tok.endswith('"') and len(tok) >= 2:
        return tok[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if tok.startswith("'") and tok.endswith("'") and len(tok) >= 2:
        return tok[1:-1].replace("''", "'")
    try:
        return int(tok)
    except ValueError:
        pass
    try:
        return float(tok)
    except ValueError:
        pass
    return tok


def _split_flow(s: str):
    parts, depth, cur, in_q = [], 0, "", False
    for ch in s:
        if ch == '"':
            in_q = not in_q
        if not in_q:
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif ch == "," and depth == 0:
                parts.append(cur)
                cur = ""
                continue
        cur += ch
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts]


def _flow(tok: str):
    tok = tok.strip()
    if tok.startswith("[") and tok.endswith("]"):
        inner = tok[1:-1].strip()
        if not inner:
            return []
        return [_flow(p) if p[:1] in "[{" else _scalar(p) for p in _split_flow(inner)]
    if tok.startswith("{") and tok.endswith("}"):
        inner = tok[1:-1].strip()
        if not inner:
            return {}
        out = {}
        for p in _split_flow(inner):
            k, _, v = p.partition(":")
            out[_scalar(k)] = _flow(v) if v.strip()[:1] in "[{" else _scalar(v)
        return out
    return _scalar(tok)


def _strip_comment(line: str) -> str:
    in_q = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_q = not in_q
        elif ch == "#" and not in_q and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


class _Lines:
    def __init__(self, text):
        self.rows = []
        for raw in text.splitlines():
            line = _strip_comment(raw)
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            self.rows.append((indent, line.strip()))
        self.i = 0

    def peek(self):
        return self.rows[self.i] if self.i < len(self.rows) else (None, None)


def _parse_block(ls: _Lines, indent: int):
    ind, content = ls.peek()
    if ind is None or ind < indent:
        return None
    if content.startswith("- ") or content == "-":
        return _parse_seq(ls, indent)
    return _parse_map(ls, indent)


def _parse_seq(ls: _Lines, indent: int):
    out = []
    while True:
        ind, content = ls.peek()
        if ind != indent or not (content.startswith("- ") or content == "-"):
            break
        rest = content[1:].strip()
        ls.i += 1
        if rest == "":
            out.append(_parse_block(ls, indent + 1))
        elif ":" in rest and not rest.startswith(('"', "'", "[", "{")):
            # Inline first key of a mapping item; following rows at
            # indent+2 belong to the same item.
            item = {}
            k, _, v = rest.partition(":")
            v = v.strip()
            if v:
                item[_scalar(k)] = _flow(v) if v[:1] in "[{" else _scalar(v)
            else:
                item[_scalar(k)] = _parse_block(ls, indent + 3)
            nxt_ind, _ = ls.peek()
            if nxt_ind is not None and nxt_ind > indent:
                more = _parse_block(ls, nxt_ind)
                if isinstance(more, dict):
                    item.update(more)
            out.append(item)
        else:
            out.append(_flow(rest) if rest[:1] in "[{" else _scalar(rest))
    return out


def _parse_map(ls: _Lines, indent: int):
    out = {}
    while True:
        ind, content = ls.peek()
        if ind != indent or content.startswith("- ") or ":" not in content:
            break
        k, _, v = content.partition(":")
        ls.i += 1
        v = v.strip()
        if v:
            out[_scalar(k)] = _flow(v) if v[:1] in "[{" else _scalar(v)
        else:
            nxt_ind, _ = ls.peek()
            if nxt_ind is not None and nxt_ind > indent:
                out[_scalar(k)] = _parse_block(ls, nxt_ind)
            else:
                out[_scalar(k)] = None
    return out


def load(text: str):
    """Parse subset YAML text into Python values."""
    ls = _Lines(text)
    if not ls.rows:
        return None
    value = _parse_block(ls, ls.rows[0][0])
    if ls.i != len(ls.rows):
        raise LabbookError(
            "yaml outside the supported subset",
            value=ls.rows[ls.i][1],
            expected="block mappings/sequences and scalar or flow values",
            fix="rewrite the document in the labbook yaml subset",
        )
    return value
