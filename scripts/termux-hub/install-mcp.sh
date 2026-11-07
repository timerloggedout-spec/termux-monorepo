#!/data/data/com.termux/files/usr/bin/sh
set -eu

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
REPO_ROOT="${TERMUX_HUB_REPOSITORY:-$HOME_DIR/termux-monorepo}"
MCP_DIR="$HOME_DIR/.local/termux-hub-mcp"
VENV="$MCP_DIR/.venv"

pkg update
pkg install -y python git openssh termux-api

mkdir -p "$MCP_DIR"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$REPO_ROOT/termux_hub/requirements.txt"

install -d -m 700 "$HOME_DIR/.local/bin"
install -m 700 "$REPO_ROOT/termux_hub/mcp_server.py" "$MCP_DIR/mcp_server.py"

cat > "$HOME_DIR/.local/bin/termux-hub-mcp" <<'EOF'
#!/data/data/com.termux/files/usr/bin/sh
set -eu
HOME_DIR="${HOME:-/data/data/com.termux/files/home}"
exec "$HOME_DIR/.local/termux-hub-mcp/.venv/bin/python"   "$HOME_DIR/.local/termux-hub-mcp/mcp_server.py"
EOF
chmod 700 "$HOME_DIR/.local/bin/termux-hub-mcp"

echo "termux_hub_mcp=installed"
echo "entrypoint=$HOME_DIR/.local/bin/termux-hub-mcp"
