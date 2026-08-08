# 📱 phone-mcp-server

> Turn your Android phone into an MCP server for AI assistants — control SMS, contacts, flashlight, clipboard, and more via Termux.

Your AI assistant can now **send texts, read your call log, toggle your flashlight, take photos, get your GPS location**, and much more — all through your Android phone running [Termux](https://termux.dev).

Built on the [Model Context Protocol (MCP)](https://modelcontextprotocol.io), this server works with any MCP-compatible client: **GitHub Copilot CLI**, **Claude Desktop**, **Cursor**, and others.

## ✨ What Can It Do?

This server exposes **18 tools** that let AI assistants interact with your phone:

| # | Tool | Description |
|---|------|-------------|
| 1 | `send_sms` | Send an SMS text message |
| 2 | `read_sms` | Read recent SMS/MMS messages from inbox |
| 3 | `get_contacts` | Get all contacts (name, number, email) |
| 4 | `get_location` | Get current GPS location |
| 5 | `get_battery` | Get battery level, status, and temperature |
| 6 | `get_clipboard` | Read the phone's clipboard |
| 7 | `set_clipboard` | Set the phone's clipboard content |
| 8 | `take_photo` | Take a photo with front or back camera |
| 9 | `get_call_log` | Get recent call history |
| 10 | `make_call` | Initiate a phone call |
| 11 | `get_wifi_info` | Get WiFi connection details |
| 12 | `flashlight` | Turn the flashlight on/off |
| 13 | `vibrate` | Make the phone vibrate |
| 14 | `send_notification` | Show a notification on the phone |
| 15 | `get_volume` | Get volume levels for all audio streams |
| 16 | `set_volume` | Set volume for a specific audio stream |
| 17 | `record_audio` | Record audio from the microphone |
| 18 | `device_info` | Get comprehensive device info |
| — | `shell` | Run a shell command (with safety filters) |

## 📋 Prerequisites

- **Android phone** (any reasonably modern version)
- **[Termux](https://f-droid.org/en/packages/com.termux/)** — install from F-Droid (not Google Play — the Play Store version is outdated)
- **[Termux:API](https://f-droid.org/en/packages/com.termux.api/)** — install from F-Droid (same source as Termux)
- **Computer and phone on the same WiFi network**

> ⚠️ **Important:** Both Termux and Termux:API must be installed from the **same source** (F-Droid). Mixing sources will cause signature mismatches.

## 🚀 Setup

### 1. Install Termux packages

Open Termux on your phone and run:

```bash
# Update package list
pkg update && pkg upgrade

# Install Node.js and the Termux API bridge
pkg install nodejs-lts termux-api

# Grant Termux:API permissions (run each and accept the prompts)
termux-sms-list          # grants SMS permission
termux-contact-list      # grants contacts permission
termux-location          # grants location permission
termux-camera-photo      # grants camera permission
termux-call-log          # grants call log permission
```

### 2. Clone and install

```bash
# Clone the repo
git clone https://github.com/htekdev/phone-mcp-server.git
cd phone-mcp-server

# Install dependencies
npm install
```

### 3. Start the server

```bash
node server.js
```

You'll see output like:

```
[phone-mcp] ========================================
[phone-mcp]  phone-mcp-server is running!
[phone-mcp]    Local:   http://localhost:3000/mcp
[phone-mcp]    Network: http://192.168.1.42:3000/mcp
[phone-mcp]    Health:  http://192.168.1.42:3000/health
[phone-mcp]    Tools:   18 phone tools via Termux:API
[phone-mcp] ========================================
```

Note the **Network URL** — you'll need it for your MCP client config.

### 4. Verify it's working

From your computer (on the same WiFi), hit the health endpoint:

```bash
curl http://192.168.1.42:3000/health
# {"status":"ok","server":"phone-mcp","version":"1.0.0","uptime":12.3,"tools":18}
```

## 🔌 Connecting to an MCP Client

### GitHub Copilot CLI

Add to your MCP config file (`.github/copilot/mcp.json` in a repo, or global config):

```json
{
  "mcpServers": {
    "phone": {
      "url": "http://192.168.1.42:3000/mcp"
    }
  }
}
```

Replace `192.168.1.42` with your phone's actual IP address.

### Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "phone": {
      "url": "http://192.168.1.42:3000/mcp"
    }
  }
}
```

### Any MCP Client

The server uses **Streamable HTTP transport** on the `/mcp` endpoint. Point any MCP-compatible client at `http://<phone-ip>:3000/mcp`.

## 💡 Usage Examples

Once connected, you can ask your AI assistant things like:

- *"Read my last 5 text messages"*
- *"Send a text to +15551234567 saying I'll be there in 10 minutes"*
- *"What's my battery level?"*
- *"Turn on the flashlight"*
- *"Where is my phone right now?"*
- *"Take a photo with the front camera"*
- *"What WiFi network am I connected to?"*
- *"Show a notification on my phone that says 'Hello from AI'"*
- *"Set my music volume to 8"*
- *"Who called me recently?"*

## ⚙️ Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--port <number>` | `3000` | Server port |
| `--verbose` / `-v` | off | Enable debug logging |
| `PORT` env var | `3000` | Server port (env var) |

```bash
# Custom port
node server.js --port 8080

# Debug mode
node server.js --verbose

# Using env var
PORT=8080 node server.js
```

## 🔒 Security Notes

- The server binds to `0.0.0.0` — any device on your local network can connect.
- The `shell` tool has basic safety filters (blocks `rm -rf /`, `mkfs`, `reboot`, etc.) but is inherently powerful. Consider removing it if you're concerned.
- There is **no authentication** by default. Only run this on trusted networks.
- For production use, consider adding API key authentication via a middleware.

## ⚠️ Known Limitations

- **RCS messages are NOT accessible** — `termux-sms-list` only reads SMS/MMS messages. If your phone uses RCS (Google Messages' default), your recent conversations may not appear.
- **WiFi-only** — your computer and phone must be on the same network. For remote access, you could use a tunnel like [ngrok](https://ngrok.com) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).
- **GPS location can be slow** — the first GPS fix may take 30-60 seconds. Use `provider: "network"` for faster (but less accurate) location.
- **Camera photos** are saved to Termux's internal storage — you'll need to copy them out or use `termux-open` to view them.
- **Termux:API permissions** — each API command needs its Android permission granted on first use. Run the commands manually once to trigger the permission prompts.

## 🏗️ Architecture

```
┌─────────────────────┐     HTTP/MCP      ┌──────────────────┐
│  MCP Client         │ ──────────────▶   │  phone-mcp       │
│  (Copilot CLI,      │                   │  (Express +      │
│   Claude Desktop)   │ ◀──────────────   │   MCP SDK)       │
└─────────────────────┘                   └────────┬─────────┘
                                                   │
                                          execFile("termux-*")
                                                   │
                                          ┌────────▼─────────┐
                                          │  Termux:API      │
                                          │  (Android APIs)  │
                                          └──────────────────┘
```

- **Express** handles HTTP routing
- **@modelcontextprotocol/sdk** provides MCP protocol handling with Streamable HTTP transport
- **Termux:API** bridges to Android system APIs (SMS, contacts, camera, etc.)
- **Zod** validates tool input schemas

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🤝 Contributing

PRs welcome! Some ideas for contributions:

- [ ] Add authentication (API key or bearer token)
- [ ] Support ngrok/tunnel auto-setup for remote access
- [ ] Add more Termux:API tools (TTS, fingerprint, sensors)
- [ ] Add a web dashboard showing connected sessions
- [ ] Support for Termux:Widget shortcuts
- [ ] Docker container for non-Termux environments (if applicable)

---

Built by [Hector Rocha](https://htek.dev) • Made with ❤️ and AI
