#!/usr/bin/env bash
set -u
_p=$(pgrep -f 'hindsight-api --port 8888' | head -1)
KEY=$(tr '\0' '\n' < /proc/$_p/environ | grep '^HINDSIGHT_API_KEY=' | cut -d= -f2-)

echo "--- 1 · retain audit fact ---"
curl -sS --max-time 60 -X POST \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"items":[{"content":"Audit test 2026-10-02: termux-monorepo Hindsight stack operational with gemini-3.1-flash-lite on bank termux-monorepo::primary.","metadata":{"origin":"audit","event":"read-back-test"}}]}' \
  http://localhost:8888/v1/default/banks/termux-monorepo::primary/memories | head -c 400
echo
echo
echo "--- 2 · recall ---"
curl -sS --max-time 30 -X POST \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"query":"What is the audit test about?","top_k":5}' \
  http://localhost:8888/v1/default/banks/termux-monorepo::primary/memories/recall | python3 -m json.tool | head -60
echo
echo "--- 3 · reflect ---"
curl -sS --max-time 90 -X POST \
  -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d '{"query":"Summarize the current state of the Hindsight stack."}' \
  http://localhost:8888/v1/default/banks/termux-monorepo::primary/reflect | python3 -m json.tool | head -40
