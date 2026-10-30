#!/usr/bin/env python3
"""Mint a GitHub App installation token (ephemeral, ~1h) — fleet collector pilot.

The app's private key NEVER passes through chat: it is read from a local
PEM file whose path comes from the environment (GITHUB_APP_KEY_FILE).
JWT signing uses the openssl CLI (RS256) — stdlib-only Python.

Usage:
  GITHUB_APP_ID=<id> GITHUB_APP_INSTALLATION_ID=<id> \
  GITHUB_APP_KEY_FILE=<path.pem> python3 github_app_token.py
Prints ONLY token metadata (expires_at) to stdout; the token itself is
written to the file named by GITHUB_APP_TOKEN_OUT when set, else stdout
line 2 (for process capture — never log it).
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.request


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(app_id: str, key_file: str) -> str:
    now = int(time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    payload = b64url(json.dumps(
        {"iat": now - 60, "exp": now + 540, "iss": app_id}).encode())
    signing_input = f"{header}.{payload}".encode()
    proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", key_file],
        input=signing_input, capture_output=True, check=True)
    return f"{header}.{payload}.{b64url(proc.stdout)}"


def main() -> int:
    app_id = os.environ["GITHUB_APP_ID"]
    inst_id = os.environ["GITHUB_APP_INSTALLATION_ID"]
    key_file = os.environ["GITHUB_APP_KEY_FILE"]
    jwt = make_jwt(app_id, key_file)
    req = urllib.request.Request(
        f"https://api.github.com/app/installations/{inst_id}/access_tokens",
        method="POST",
        headers={"Authorization": f"Bearer {jwt}",
                 "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with urllib.request.urlopen(req) as resp:
        body = json.load(resp)
    print(f"expires_at={body['expires_at']}")
    out = os.environ.get("GITHUB_APP_TOKEN_OUT")
    if out:
        with open(out, "w") as fh:
            fh.write(body["token"])
        os.chmod(out, 0o600)
        print(f"token written to {out} (0600) — value never printed")
    else:
        print(body["token"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
