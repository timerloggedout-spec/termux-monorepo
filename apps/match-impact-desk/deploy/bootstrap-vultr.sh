#!/usr/bin/env bash
set -euo pipefail

: "${MATCHDESK_DOMAIN:?Set MATCHDESK_DOMAIN to the DNS name pointing at this VM}"
: "${MATCHDESK_ADMIN_TOKEN:?Set MATCHDESK_ADMIN_TOKEN to a long random secret}"
if [[ "${#MATCHDESK_ADMIN_TOKEN}" -lt 32 ]]; then echo "MATCHDESK_ADMIN_TOKEN must be at least 32 characters" >&2; exit 1; fi
MATCHDESK_BRANCH="${MATCHDESK_BRANCH:-master}"
REPO_URL="https://github.com/timerloggedout-spec/termux-monorepo.git"
APP_DIR="/opt/match-impact-desk"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (for example: sudo -E ./bootstrap-vultr.sh)" >&2
  exit 1
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y python3 git caddy
id matchdesk >/dev/null 2>&1 || useradd --system --user-group --home "$APP_DIR" --shell /usr/sbin/nologin matchdesk
install -d -o matchdesk -g matchdesk "$APP_DIR/data"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

git clone --depth 1 --filter=blob:none --sparse --branch "$MATCHDESK_BRANCH" "$REPO_URL" "$tmp/repo"
git -C "$tmp/repo" sparse-checkout set apps/match-impact-desk
cp -a "$tmp/repo/apps/match-impact-desk/." "$APP_DIR/"
chown -R matchdesk:matchdesk "$APP_DIR"

umask 077
cat > /etc/match-impact-desk.env <<EOF
MATCHDESK_DB=$APP_DIR/data/matchdesk.sqlite3
MATCHDESK_ADMIN_TOKEN=$MATCHDESK_ADMIN_TOKEN
MATCHDESK_INFERENCE_BASE_URL=${MATCHDESK_INFERENCE_BASE_URL:-}
MATCHDESK_INFERENCE_MODEL=${MATCHDESK_INFERENCE_MODEL:-}
MATCHDESK_INFERENCE_API_KEY=${MATCHDESK_INFERENCE_API_KEY:-}
EOF
chmod 0600 /etc/match-impact-desk.env

install -m 0644 "$APP_DIR/deploy/match-impact-desk.service" /etc/systemd/system/match-impact-desk.service
sed "s/YOUR_DOMAIN/$MATCHDESK_DOMAIN/g" "$APP_DIR/deploy/Caddyfile" > /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable --now match-impact-desk
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy

curl --fail --silent --show-error http://127.0.0.1:8080/health
echo
echo "Match Impact Desk installed. Verify https://$MATCHDESK_DOMAIN/health from an external network."
