# Mistralai Vibe Code webWrapper CLI

A comprehensive command-line interface for interacting with Mistralai's Vibe Code, featuring code harvesting, search, analysis, and integration with DeepSeek/ArchW1z/Synthegration architectures.

## Features

- **Session Management**: Create, list, and manage chat sessions with Mistralai
- **Chat Interface**: Send messages and receive responses with streaming support
- **Code Harvesting**: Extract code from files, directories, and text
- **Code Search**: Full-text search across harvested code with language filtering
- **Code Analysis**: Analyze code structure, complexity, and dependencies
- **Multi-Provider Support**: Compatible with DeepSeek, ArchW1z, Synthegration, and more
- **Termux Integration**: Special utilities for Termux/Android environment
- **Sandboxed Environment**: Safe dev/staging/prod directory structure

## Installation

### Prerequisites

- Python 3.8+
- pip
- Node.js (for POW solver)

### Install from source

```bash
cd multi-ai-cli
git checkout vibe/mistralai-vibe-code-wrapper-6055d2
pip install -e .
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Start the CLI
mistralai-cli

# Or use the legacy interface
python cli.py
```

### Session Management

```bash
# Create a new session
mistralai-cli session new

# List all sessions
mistralai-cli session list

# Select a session
mistralai-cli session select

# Send a message
mistralai-cli chat send "Hello, Mistral!"

# View chat history
mistralai-cli chat history
```

### Code Harvesting

```bash
# Harvest code from a directory
mistralai-cli harvest code ./src --recursive

# Harvest code from a specific file
mistralai-cli harvest code myfile.py

# Harvest code from text
mistralai-cli harvest text myfile.txt
```

### Code Search

```bash
# Search harvested code
mistralai-cli search code "def hello"

# Search by language
mistralai-cli search by-language python

# Search with query filter
mistralai-cli search by-language python --query "class"
```

### Code Analysis

```bash
# Analyze a single file
mistralai-cli analyze file myfile.py

# Analyze a directory
mistralai-cli analyze directory ./src --recursive

# Analyze with specific language
mistralai-cli analyze file myfile.js --language javascript
```

### Tools

```bash
# Extract code from text
mistralai-cli tools extract "Here's some code: ```python\ndef hello():\n    pass```"

# Show system information
mistralai-cli tools info

# Clean up temporary files
mistralai-cli tools cleanup

# Interactive shell
mistralai-cli shell --interactive
```

## Configuration

The CLI uses a configuration file at `~/.mistralai-cli/config.json`. You can also set environment variables:

- `MISTRALAI_TOKEN`: Your Mistralai API token
- `MISTRALAI_CLI_VERSION`: CLI version (for development)

### Setting up authentication

1. Get your Mistralai API token
2. Set it as environment variable:
   ```bash
   export MISTRALAI_TOKEN="your_token_here"
   ```
3. Or add it to your config:
   ```bash
   mistralai-cli session new  # This will prompt for token if not set
   ```

## Architecture

The CLI is built on the following architecture:

### Core Module (`core/`)
- `core.py`: Main API wrapper for Mistralai
- `session_manager.py`: Session management
- `chat_dispatcher.py`: Chat message dispatching
- `cache.py`: Caching utilities

### Harvesters Module (`harvesters/`)
- `code_harvester.py`: Code extraction from files and directories
- `search_engine.py`: Full-text search engine
- `extractor.py`: Code extraction from various formats
- `analyzer.py`: Code analysis and metrics

### Tools Module (`tools/`)
- `file_utils.py`: File operations
- `git_utils.py`: Git operations
- `network_utils.py`: HTTP requests and web operations
- `termux_utils.py`: Termux-specific utilities

### Bridge Module (`bridge/`)
- `mistral_bridge.py`: WebSocket bridge for Mistralai

### Backends Module (`backends/`)
- Various backend implementations for different providers

## Directory Structure

```
multi-ai-cli/
├── core/                  # Core functionality
│   ├── __init__.py
│   ├── core.py           # Main Mistralai API wrapper
│   ├── session_manager.py
│   ├── chat_dispatcher.py
│   └── cache.py
├── harvesters/           # Code harvesting and analysis
│   ├── __init__.py
│   ├── code_harvester.py
│   ├── search_engine.py
│   ├── extractor.py
│   └── analyzer.py
├── tools/                # Utility tools
│   ├── __init__.py
│   ├── file_utils.py
│   ├── git_utils.py
│   ├── network_utils.py
│   └── termux_utils.py
├── backends/             # Backend implementations
│   ├── __init__.py
│   ├── base.py
│   ├── mistral_web.py
│   └── ...
├── bridge/               # Bridge components
│   └── mistral_bridge.py
├── sandbox/              # Sandboxed environment
│   ├── dev/
│   ├── staging/
│   ├── prod/
│   ├── envs/
│   ├── workspace/
│   ├── cache/
│   ├── logs/
│   └── sessions/
├── utils/                # Utility scripts
├── harvesters/           # Legacy harvesters
├── cli.py                # Legacy CLI interface
├── main.py               # Main entry point
├── mistralai_cli.py      # New CLI interface
├── config.yaml           # Configuration
├── setup.py              # Setup script
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## Integration with DeepSeek/ArchW1z/Synthegration

The CLI is designed to be compatible with existing architectures:

- **DeepSeek**: Uses similar POW solving and session management
- **ArchW1z**: Integrates with archwiz dispatch pipeline
- **Synthegration**: Compatible with cli-synthegration workflows

### Deepterm Integration

The CLI uses deepterm for terminal operations and can integrate with:
- `deepterm_fork`: For terminal-based operations
- `deepcli`: For DeepSeek CLI compatibility

## Development

### Setting up development environment

```bash
# Clone the repository
git clone https://github.com/timerloggedout-spec/termux-monorepo.git
cd termux-monorepo/multi-ai-cli

# Create working branch
git checkout -b vibe/mistralai-vibe-code-wrapper-6055d2

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Running tests

```bash
pytest tests/
```

### Building documentation

```bash
# Documentation will be added in future versions
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Acknowledgments

- Built on the `deepcli` architecture from `timerloggedout-spec/termux-monorepo`
- Uses `deepterm` from `timerloggedout-spec/deepterm_fork`
- Inspired by `ChapitoAI` template
- Compatible with DeepSeek, ArchW1z, Synthegration architectures

## Support

For issues and questions, please open an issue in the repository.

---

**"All for One; and, .One for All!"**
