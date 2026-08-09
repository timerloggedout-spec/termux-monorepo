# NexusCLI

> **A fast, lightweight, Termux-optimized CLI/TUI for agent interactions.**
> Powered by `curl_cffi` and reverse-engineered DeepSeek API endpoints.

---

## 🚀 Features

- **Blazing Fast**: Uses `curl_cffi` for high-performance API calls.
- **Termux Optimized**: Designed for mobile/Termux environments.
- **Lightweight**: No Playwright or heavy dependencies.
- **Phased Architecture**: Modular design for instant execution.
- **Session Management**: Create, list, and manage chat sessions.
- **Interactive Chat**: Real-time streaming responses.
- **Export Capabilities**: Export conversations to Markdown or JSON.

---

## 📦 Installation

### 1. Clone the Repository

```bash
cd ~/termux-monorepo
git checkout vibe/deepcode-cli_phased-fusion_fc54fa
```

### 2. Install Dependencies

```bash
pip install curl_cffi rich
```

### 3. Set Up API Token

```bash
export NEXUSCLI_TOKEN="<insert-token>"
# Or save in config
echo '{"token": "<insert-token>"}' > ~/.nexuscli/config.json
```

---

## 🎯 Usage

### Basic Commands

| Command | Description |
|---------|-------------|
| `nexuscli sessions` | List all sessions |
| `nexuscli new-session` | Create a new session |
| `nexuscli chat --last` | Start interactive chat |
| `nexuscli send --prompt "Hello" --last` | Send a single message |
| `nexuscli export --last --format markdown` | Export session history |

### Examples

```bash
# List all sessions
nexuscli sessions

# Create a new expert session
nexuscli new-session --model expert --save

# Start interactive chat with last session
nexuscli chat --last --thinking

# Send a single message
nexuscli send --prompt "Explain Python decorators" --last

# Export session to Markdown
nexuscli export --last --format markdown --output conversation.md
```

---

## 🏗️ Project Structure

```
nexuscli/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── api.py          # Core API wrapper (reverse-engineered)
├── cli/
│   ├── __init__.py
│   └── main.py         # CLI entry point
├── nexuscli.py         # Launcher script
├── pow_solver.js       # POW solver for API challenges
└── README.md
```

---

## 🔧 Configuration

### Config File

Located at `~/.nexuscli/config.json`:

```json
{
  "token": "<insert-token>",
  "last_session": "<last-session-id>"
}
```

### Environment Variables

- `NEXUSCLI_TOKEN` or `DEEPSEEK_TOKEN`: API token
- `NEXUSCLI_BASE_URL`: Custom API base URL (default: `https://chat.deepseek.com`)

---

## 🤖 API Endpoints

The following endpoints are reverse-engineered and used:

| Endpoint | Description |
|----------|-------------|
| `/api/v0/chat_session/create` | Create a new chat session |
| `/api/v0/chat_session/fetch_page` | Fetch all sessions |
| `/api/v0/chat/history_messages` | Get session history |
| `/api/v0/chat/create_pow_challenge` | Get POW challenge |
| `/api/v0/chat/completion` | Send message (streaming) |
| `/api/v0/file/upload_file` | Upload a file |
| `/api/v0/share/create` | Create a share |
| `/api/v0/share/fork` | Fork a conversation |

---

## 📜 License

MIT License. See [LICENSE](../../LICENSE) for details.

---

## 🙌 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🔗 Related Projects

- [termux-monorepo](https://github.com/timerloggedout-spec/termux-monorepo)
- [deepcli](https://github.com/timerloggedout-spec/termux-monorepo/tree/master/deepcli)
- [multi-ai-cli](https://github.com/timerloggedout-spec/termux-monorepo/tree/master/multi-ai-cli)
- [termux-multi-agent](https://github.com/timerloggedout-spec/termux-monorepo/tree/master/termux-multi-agent)

---

## 🎨 Branding

**NexusCLI** is part of the **Termux Monorepo** ecosystem.

> **"All for One; and, One for All!"** 🚀
