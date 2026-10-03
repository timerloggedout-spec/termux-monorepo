"""_v1_events — extract symbolic events from session messages.

Reduces each message (content + thinking_content) to a small set of
symbols that represent system-state transitions. Cheap: regex only,
no model calls.

Public API:
    extract(text) -> list[str]           # symbols in order
    scan_session(path) -> list[dict]     # per-message event records
    scan_dir(path) -> list[dict]         # all sessions in a dir
"""

import re, json, pathlib

# ─── symbol patterns ──────────────────────────────────────────
# Order matters: first match wins per category so we dedupe.
RULES = [
    # destructive operations
    ("KILL_AGENT",    r"gpgconf\s+--kill\s+gpg-agent|pkill\s+.*gpg-agent|kill\s+.*gpg-agent"),
    ("CRED_WRITE",    r">\s*~?/?\.?gnupg/\.2fa-pass|>\.2fa-pass|write.*\.2fa-pass|echo.*\.2fa-pass"),
    ("CRED_READ",     r"cat\s+.*\.2fa-pass|read.*\.2fa-pass|xxd\s+.*\.2fa-pass"),
    ("PUBRING_DELETE", r"rm\s+.*pubring|mv\s+.*pubring|>\.gnupg\.broken"),
    ("PRIVATE_KEY_DELETE", r"rm\s+.*private-keys-v1\.d"),

    # state probes
    ("AGENT_CACHED",  r"S KEYINFO\s+[0-9A-F]{40}\s+D"),   # agent has at least one grip
    ("AGENT_EMPTY",   r"^OK\s*$"),                          # bare OK from KEYINFO --list
    ("PUBRING_EMPTY", r"pubring\.kbx.*32\s*B|pubring.*32B|size.*32.*pubring"),

    # totp operations
    ("TOTP_CALL",     r"pass\s+otp\s+secret/github|gh2fa|gh-code.*totp"),
    ("TOTP_FAIL",     r"pass otp.*(?:rc=[1-9]|len=0|decryption failed|public key)"),
    ("TOTP_OK",       r"pass otp rc=0\s+len=6|TOTP: [0-9]{6}|One-time code \("),
    ("DEVICE_FLOW",   r"gh auth login|github\.com/login/device|One-time code \([A-Z0-9]+-[A-Z0-9]+\)"),
]


def extract(text):
    """Return symbols in order of first appearance."""
    if not text:
        return []
    seen = []
    for sym, pat in RULES:
        if re.search(pat, text, re.M):
            if sym not in seen:
                seen.append(sym)
    return seen


def message_text(m):
    """Join content + thinking_content + fragments[].content for a message.

    Session-store messages carry empty `content` after API refresh; the
    actual reply text lives in `fragments[].content`. Earlier versions
    only read `content`, so events looked empty on live sessions.
    """
    parts = []
    for k in ("content", "thinking_content", "text"):
        v = m.get(k)
        if isinstance(v, str) and v:
            parts.append(v)
    frags = m.get("fragments")
    if isinstance(frags, list):
        for fr in frags:
            if isinstance(fr, dict):
                c = fr.get("content")
                if isinstance(c, str) and c:
                    parts.append(c)
    return "\n".join(parts)


def scan_session(path):
    """Yield {idx, role, symbols} for each message in a session."""
    try:
        raw = json.loads(pathlib.Path(path).read_text())
    except Exception:
        return []
    msgs = raw if isinstance(raw, list) else []
    out = []
    for i, m in enumerate(msgs):
        if not isinstance(m, dict):
            continue
        syms = extract(message_text(m))
        if not syms:
            continue
        out.append({
            "idx": i,
            "role": (m.get("role") or "?").lower(),
            "ts": m.get("inserted_at") or m.get("timestamp"),
            "symbols": syms,
        })
    return out


def scan_dir(path):
    """Scan all session files in a directory."""
    p = pathlib.Path(path)
    for f in p.glob("*.json"):
        recs = scan_session(f)
        if recs:
            yield f.stem, recs
