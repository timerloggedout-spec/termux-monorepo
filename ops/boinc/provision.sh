#!/bin/bash
# BOINC fleet provisioning: create-or-lookup project accounts via the
# project Web RPCs and attach the local client.
#
# Credentials come from the environment (never commit them, never put
# them in a repo secret without an owner provisioning decision):
#   BOINC_EMAIL, BOINC_PASSWORD, BOINC_USERNAME   (account identity)
#   GUI_RPC_PASSWORD                              (local client control)
#   BOINC_DATA_DIR                                (client data dir)
# Einstein@Home is lookup-only here: the project refuses RPC account
# creation ("Account creation is done through our Web site").
# SRBase's invite_code is the anti-spam code the project publishes on
# its own homepage/FAQ - a public string, not a credential.
set -u
: "${BOINC_EMAIL:?}" "${BOINC_PASSWORD:?}" "${BOINC_USERNAME:?}" \
  "${GUI_RPC_PASSWORD:?}" "${BOINC_DATA_DIR:?}"
HASH=$(printf '%s%s' "$BOINC_PASSWORD" \
  "$(echo "$BOINC_EMAIL" | tr 'A-Z' 'a-z')" | md5sum | cut -d' ' -f1)

provision() {
  local name="$1" url="$2" mode="$3" invite="${4:-}"
  local resp key
  resp=$(curl -s --max-time 30 -G "$url/lookup_account.php" \
    --data-urlencode "email_addr=$BOINC_EMAIL" \
    --data-urlencode "passwd_hash=$HASH")
  key=$(echo "$resp" | grep -oE '[0-9a-f]{32}' | head -1)
  if [ -z "$key" ] && [ "$mode" = "create" ]; then
    local args=(--data-urlencode "email_addr=$BOINC_EMAIL"
      --data-urlencode "passwd_hash=$HASH"
      --data-urlencode "user_name=$BOINC_USERNAME")
    [ -n "$invite" ] && args+=(--data-urlencode "invite_code=$invite")
    resp=$(curl -s --max-time 30 -G "$url/create_account.php" "${args[@]}")
    key=$(echo "$resp" | grep -oE '[0-9a-f]{32}' | head -1)
  fi
  if [ -z "$key" ]; then
    echo "$name: FAILED: $(echo "$resp" | grep -oE '<error_msg>[^<]*' | head -1)"
    return 1
  fi
  boinccmd --host localhost --passwd "$GUI_RPC_PASSWORD" \
    --project_attach "$url" "$key" >/dev/null 2>&1
  echo "$name: account ok, attach issued"
}

provision numberfields https://numberfields.asu.edu/NumberFields/ create
provision srbase https://srbase.my-firewall.org/sr5/ create pillepalle
provision einstein https://einsteinathome.org lookup
