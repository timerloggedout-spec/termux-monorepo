#!/usr/bin/env python3
"""Owner-side helper for the X Observatory OAuth 2.0 PKCE flow.

Two commands:

  authorize-url  — print the https://x.com/i/oauth2/authorize URL (with a
                   fresh PKCE verifier + state saved to a local state file).
                   The owner opens it signed in as the account, approves,
                   and copies the `code` from the localhost redirect URL.
  exchange CODE  — exchange the code for access + refresh tokens and print
                   ONLY the secret names to store (values go to stdout once,
                   for the owner's own secret-store paste; never log them).

Scopes: bookmark.read like.read tweet.read users.read offline.access
(offline.access is what makes the refresh token — the durable credential —
exist; the access token itself expires in ~2 hours).

App setup (owner, once, at developer.x.com): create a Project + App,
enable OAuth 2.0, app type "Web app, automated app or bot", callback /
redirect URL http://localhost:8765/callback, then read the Client ID
(and Client Secret for a confidential client) from Keys and tokens.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import secrets as _secrets
import sys
import urllib.parse
from pathlib import Path

from x_harvest import post_form

AUTH_URL = "https://x.com/i/oauth2/authorize"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
SCOPES = "bookmark.read like.read tweet.read users.read offline.access"
STATE_FILE = Path.home() / ".x-observatory-oauth.json"


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def authorize_url(client_id: str, redirect_uri: str) -> str:
    verifier = _b64url(_secrets.token_bytes(32))
    challenge = _b64url(hashlib.sha256(verifier.encode()).digest())
    state = _b64url(_secrets.token_bytes(16))
    STATE_FILE.write_text(json.dumps(
        {"verifier": verifier, "state": state, "redirect_uri": redirect_uri}))
    STATE_FILE.chmod(0o600)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return AUTH_URL + "?" + urllib.parse.urlencode(params)


def exchange(code: str, client_id: str, client_secret: str | None,
             poster=post_form) -> dict:
    saved = json.loads(STATE_FILE.read_text())
    form = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": saved["redirect_uri"],
        "code_verifier": saved["verifier"],
        "client_id": client_id,
    }
    return poster(TOKEN_URL, form, client_id, client_secret)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("authorize-url")
    a.add_argument("--client-id", required=True)
    a.add_argument("--redirect-uri", default="http://localhost:8765/callback")
    e = sub.add_parser("exchange")
    e.add_argument("code")
    e.add_argument("--client-id", required=True)
    e.add_argument("--client-secret")
    args = parser.parse_args(argv)
    if args.cmd == "authorize-url":
        print(authorize_url(args.client_id, args.redirect_uri))
        print(f"PKCE state saved to {STATE_FILE} (0600). After approving, the "
              "browser lands on a localhost URL that will not load — copy the "
              "`code` value from its address bar for the exchange step.",
              file=sys.stderr)
        return 0
    out = exchange(args.code, args.client_id, args.client_secret)
    if not out.get("refresh_token"):
        print("ERROR: no refresh_token returned — offline.access scope missing?",
              file=sys.stderr)
        return 1
    print("Store these as GitHub Actions secrets (values shown once, here only):")
    print(f"X_OAUTH2_REFRESH_TOKEN = {out['refresh_token']}")
    print(f"X_OAUTH2_USER_TOKEN = {out.get('access_token', '')}  (optional; expires ~2h, workflow refreshes)")
    print(f"X_CLIENT_ID = {args.client_id}")
    if args.client_secret:
        print("X_CLIENT_SECRET = (the one you just used)")
    STATE_FILE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
