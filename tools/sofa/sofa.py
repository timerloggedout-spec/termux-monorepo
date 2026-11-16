#!/usr/bin/env python3
"""SOFA (Stack Overflow for Agents) MCP helper — custom.stackoverflow-agents.

Typed coverage of all 27 MCP tools (schema snapshot: ../tools-schema.json).
Transport is curl (urllib POSTs to the token endpoint intermittently die with
RemoteDisconnected through the VM egress proxy; curl is reliable).

Usage:
  sofa.py status                       connection identity/scope verify
  sofa.py tools                        list tool names + scope class
  sofa.py describe <tool>              full description + typed params
  sofa.py call <tool> [--k v ...]      call with named args (JSON-coerced)
  sofa.py <tool> [--k v ...]           shorthand for call
  sofa.py refresh                      force refresh_token exchange

Scope classes: READ tools run under the granted scopes (sofa.read +
sofa.identity.read + offline_access). WRITE tools are typed and callable but
the server rejects them until the owner widens scopes (vote/write) — that
widening is owner-gated and intentionally NOT requested by this helper.
Tokens live in ../.tokens.json (0600); values are never printed.
"""
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS_PATH = os.path.join(BASE, ".tokens.json")
SCHEMA_PATH = os.path.join(BASE, "tools-schema.json")
CLIENT_ID = "sofa_dc_BMNUcUHGxLPN5RPrCIxjtQ"
TOKEN_URL = "https://agents.stackoverflow.com/mcp/oauth/token"
MCP_URL = "https://agents.stackoverflow.com/mcp"
RESOURCE = "https://agents.stackoverflow.com/mcp"

READ_TOOLS = {
    "sofa_connection_status", "sofa_guidance", "sofa_session_summary",
    "sofa_attention", "sofa_search", "sofa_get_post", "sofa_my_posts",
    "sofa_get_draft", "sofa_pull_playbook", "sofa_list_related_playbooks",
    "sofa_search_external_links", "sofa_search_link_assessments",
    "sofa_lookup_external_link", "sofa_my_verifications", "sofa_tags",
    "sofa_list_agent_leaderboard",
}


def curl_json(url, headers, body, timeout=60):
    args = ["curl", "-s", "-m", str(timeout), "-X", "POST", url]
    for h in headers:
        args += ["-H", h]
    if isinstance(body, dict) and body.get("__form__"):
        for k, v in body["__form__"].items():
            args += ["--data-urlencode", f"{k}={v}"]
    else:
        args += ["-H", "Content-Type: application/json", "-d", json.dumps(body)]
    for attempt in range(2):
        out = subprocess.run(args, capture_output=True, text=True)
        text = out.stdout.strip()
        if text:
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("data:"):
                    s = s[5:].strip()
                if s.startswith("{"):
                    return json.loads(s)
            return json.loads(text)
    raise RuntimeError(f"empty response from {url} after retries")


def load_tokens():
    with open(TOKENS_PATH) as f:
        return json.load(f)


def save_tokens(tok):
    with open(TOKENS_PATH, "w") as f:
        json.dump(tok, f)
    os.chmod(TOKENS_PATH, 0o600)


def refresh(tok=None):
    tok = tok or load_tokens()
    new = curl_json(TOKEN_URL, ["Content-Type: application/x-www-form-urlencoded"],
                    {"__form__": {"grant_type": "refresh_token",
                                  "refresh_token": tok["refresh_token"],
                                  "client_id": CLIENT_ID, "resource": RESOURCE}})
    if "access_token" not in new:
        raise RuntimeError(f"refresh failed: {str(new)[:200]}")
    tok.update(new)
    tok["obtained_at"] = int(time.time())
    save_tokens(tok)
    return tok


def access_token():
    tok = load_tokens()
    if time.time() > tok.get("obtained_at", 0) + int(tok.get("expires_in", 900)) - 120:
        tok = refresh(tok)
    return tok["access_token"]


def mcp(method, params, rid=1):
    return curl_json(MCP_URL, [f"Authorization: Bearer {access_token()}",
                               "Accept: application/json, text/event-stream"],
                     {"jsonrpc": "2.0", "id": rid, "method": method, "params": params})


def load_schema():
    with open(SCHEMA_PATH) as f:
        return {t["name"]: t for t in json.load(f)}


def param_type(prop):
    if "anyOf" in prop:
        types = [a.get("type", "?") for a in prop["anyOf"]]
        return "|".join(types)
    if "type" in prop:
        t = prop["type"]
        if t == "array":
            items = prop.get("items", {}).get("type", "?")
            return f"array<{items}>"
        return t
    return "?"


def coerce(value):
    try:
        return json.loads(value)
    except Exception:
        return value


def parse_args(argv, tool):
    schema = load_schema()[tool]["inputSchema"]
    props = schema.get("properties", {})
    required = schema.get("required", [])
    out = {}
    it = iter(range(len(argv)))
    i = 0
    while i < len(argv):
        tok = argv[i]
        if not tok.startswith("--"):
            raise SystemExit(f"unexpected positional arg: {tok} (use --name value)")
        key = tok[2:]
        if key not in props:
            raise SystemExit(f"unknown param --{key} for {tool}; see: sofa.py describe {tool}")
        if i + 1 >= len(argv):
            raise SystemExit(f"--{key} needs a value")
        out[key] = coerce(argv[i + 1])
        i += 2
    missing = [r for r in required if r not in out]
    if missing:
        raise SystemExit(f"missing required params for {tool}: {missing}")
    return out


def call_tool(tool, args):
    res = mcp("tools/call", {"name": tool, "arguments": args}, 4)
    if "error" in res:
        print(json.dumps(res["error"], indent=2)[:1500])
        if tool not in READ_TOOLS:
            print(f"note: {tool} is a WRITE-class tool; granted scopes are read/identity only (owner-gated widening).")
        sys.exit(1)
    result = res.get("result", {})
    content = result.get("content", [])
    for c in content:
        if c.get("type") == "text":
            print(c["text"])
    if result.get("structuredContent"):
        print(json.dumps(result["structuredContent"], indent=2)[:3000])
    if result.get("isError"):
        sys.exit(1)


def main():
    schema = load_schema()
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == "refresh":
        tok = refresh()
        print(f"refreshed; expires_in={tok.get('expires_in')}")
    elif cmd == "tools":
        for name in sorted(schema):
            print(f"{name}  [{'READ' if name in READ_TOOLS else 'WRITE-gated'}]")
    elif cmd == "describe":
        t = schema[argv[1]]
        print(t["description"])
        print("\nParams:")
        props = t["inputSchema"].get("properties", {})
        req = set(t["inputSchema"].get("required", []))
        for k, v in props.items():
            print(f"  --{k} ({param_type(v)}){' REQUIRED' if k in req else ''}")
    elif cmd == "status":
        call_tool("sofa_connection_status", {})
    elif cmd == "call":
        tool = argv[1]
        call_tool(tool, parse_args(argv[2:], tool))
    elif cmd in schema:
        call_tool(cmd, parse_args(argv[1:], cmd))
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
