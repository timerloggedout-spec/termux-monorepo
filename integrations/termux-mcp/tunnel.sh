#!/usr/bin/env bash
set -euo pipefail

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared is required but was not found." >&2
  echo "On Termux, install it with: pkg install cloudflared" >&2
  echo "On other platforms, install cloudflared from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/" >&2
  exit 1
fi

# Paste the printed https://*.trycloudflare.com URL into Devin's custom-MCP form (append the server path, see below).
exec cloudflared tunnel --url "http://${TERMUX_MCP_HOST:-127.0.0.1}:${TERMUX_MCP_PORT:-8765}"
