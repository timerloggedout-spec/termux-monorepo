#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] || { echo "missing .env — copy env.example"; exit 1; }
set -a; . ./.env; set +a
docker compose up -d
sleep 4
curl -fsS http://127.0.0.1:8888/health && echo " ✓ up"
