# Multi-AI CLI

A unified command-line interface for interacting with multiple AI providers (Mistral, DeepSeek, etc.) with code harvesting, search, and analysis capabilities.

## Overview

`multi-ai-cli` serves as the **main entry point** for selecting and using different AI providers. It provides:

- **Provider Selection**: Choose between Mistral, DeepSeek, and other AI providers
- **Unified Interface**: Common commands across all providers
- **Code Harvesting**: Extract and collect code from various sources
- **Code Search**: Full-text search across harvested code
- **Code Analysis**: Analyze code structure, complexity, and dependencies
- **Tool Integration**: File, Git, network, and Termux utilities

## Architecture

The system is designed to work **alongside** existing CLIs:

- **`multi-ai-cli`** (this project) - Main entry point and Mistral implementation
- **`deepcli`** - Existing DeepSeek CLI at `~/deepcli/deepcli.py`
- **`deepcli-tui`** - Existing DeepSeek TUI at `~/deepcli-tui/tui.py`

When you select a provider, `multi-ai-cli` either:
1. Uses its native implementation (for Mistral)
2. Calls the existing CLI as a subprocess (for DeepSeek, DeepSeek-TUI)

## Installation

### Prerequisites

- Python 3.8+
- pip

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
multi-ai-cli

# Or use the short form
multi-ai
```

### Provider Selection

```bash
# List available providers
multi-ai-cli provider list

# Select a default provider
multi-ai-cli provider select mistral
multi-ai-cli provider select deepseek

# Run a provider's CLI directly
multi-ai-cli provider run deepseek --help
multi-ai-cli provider run deepseek-tui
```

### Mistral-Specific Commands

```bash
# Create a new session
multi-ai-cli session new

# List all sessions
multi-ai-cli session list

# Select a session
multi-ai-cli session select

# Send a message
multi-ai-cli chat send "Hello, Mistral!"

# View chat history
multi-ai-cli chat history
```

### Code Harvesting

```bash
# Harvest code from a directory
multi-ai-cli harvest code ./src --recursive

# Harvest code from a specific file
multi-ai-cli harvest code myfile.py

# Harvest code from text
multi-ai-cli harvest text myfile.txt
```

### Code Search

```bash
# Search harvested code
multi-ai-cli search code "def hello"

# Search by language
multi-ai-cli search by-language python

# Search with query filter
multi-ai-cli search by-language python --query "class"
```

### Code Analysis

```bash
# Analyze a single file
multi-ai-cli analyze file myfile.py

# Analyze a directory
multi-ai-cli analyze directory ./src --recursive

# Analyze with specific language
multi-ai-cli analyze file myfile.js --language javascript
```

### Tools

```bash
# Extract code from text
multi-ai-cli tools extract "Here's some code: ```python\ndef hello():\n    pass```"

# Show system information
multi-ai-cli tools info

# Clean up temporary files
multi-ai-cli tools cleanup

# Interactive shell
multi-ai-cli shell --interactive
```

## Configuration

The CLI uses a configuration file at `~/.mistralai-cli/config.json`. You can also set environment variables:

- `MISTRALAI_TOKEN`: Your Mistralai API token
- `MULTI_AI_CLI_VERSION`: CLI version (for development)

### Setting up authentication

1. Get your Mistralai API token
2. Set it as environment variable:
   ```bash
   export MISTRALAI_TOKEN="your_token_here"
   ```
3. Or it will be prompted when you first run a command

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
├── backends/             # Backend implementations (existing)
│   ├── __init__.py
│   ├── base.py
│   ├── mistral_web.py
│   └── ...
├── bridge/               # Bridge components (existing)
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
├── cli.py                # Legacy CLI interface (backward compatible)
├── main.py               # Main entry point
├── mistralai_cli.py      # New CLI interface
├── config.yaml           # Configuration
├── setup.py              # Setup script
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

## Integration with Existing Systems

### DeepSeek CLI

The existing DeepSeek CLI at `~/deepcli/deepcli.py` is automatically detected and can be run directly:

```bash
multi-ai-cli provider run deepseek --help
multi-ai-cli provider run deepseek session new
```

### DeepSeek TUI

The existing TUI at `~/deepcli-tui/tui.py` is also available:

```bash
multi-ai-cli provider run deepseek-tui
```

### Aliases

You can add these aliases to your `.zshrc` or `.bashrc`:

```bash
# Multi-AI CLI
alias multi-ai="python3 -m multi_ai_cli.main"
alias multi-ai-cli="python3 -m multi_ai_cli.main"

# Direct provider access
alias deepseek-cli="python3 ~/deepcli/deepcli.py"
alias deepseek-tui="python3 ~/deepcli-tui/tui.py"
```

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

## Key Design Principles

1. **Minimal Overhead**: `multi-ai-cli` adds minimal overhead when calling existing CLIs
2. **Parallel Operation**: Each provider operates independently
3. **Unified Interface**: Common commands work across all providers
4. **Backward Compatibility**: Existing `cli.py` interface is preserved
5. **Extensibility**: Easy to add new providers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License - See LICENSE file for details.

## Support

For issues and questions, please open an issue in the repository.

---

**"All for One; and, .One for All!"**
