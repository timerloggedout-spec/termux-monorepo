#!/data/data/com.termux/files/usr/bin/bash
# fix-node-bind.sh
# Ensure node binds on 0.0.0.0 and PWA fetches localhost:8080

ROOT="$HOME/commingle-swarm"

# --- Fix node.ts binding ---
NODE_FILE="$ROOT/termux/src/node.ts"
# Replace the server.listen line with explicit 0.0.0.0 binding
sed -i 's/server.listen(8080.*$/server.listen(8080, "0.0.0.0", () => { console.log("Headless node API at http:\\/\\/0.0.0.0:8080"); });/' "$NODE_FILE"

# --- Fix NodeClient.ts base URL ---
CLIENT_FILE="$ROOT/web/src/api/NodeClient.ts"
sed -i 's|const BASE = .*|const BASE = "http://localhost:8080";|' "$CLIENT_FILE"

echo "✔ Applied fixes:"
echo " - Node will bind on 0.0.0.0"
echo " - PWA will fetch from http://localhost:8080"
echo
echo "Next steps:"
echo "1) Restart the node:   ./termux/bin/headless-node.sh"
echo "2) Rebuild the PWA:    cd $ROOT/web && npm run build && npm run serve"
echo "3) Reload Chrome at http://localhost:8088"
