# Multi-AI CLI - Development Environment

This directory contains development-specific configurations and scripts for the Multi-AI CLI.

## Structure

- `dev/`: Development environment configurations
- `staging/`: Staging environment configurations
- `prod/`: Production environment configurations

## Development Setup

### Prerequisites

```bash
# Python 3.10+
python --version

# Required packages
pip install click requests curl_cffi python-dotenv

# Optional packages for full functionality
pip install discord.py python-telegram-bot beautifulsoup4
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# Antigravity
GEMINI_API_KEY=your_ai_studio_key
AGY_PROVIDER=gemini

# DeepSeek
DEEPSEEK_TOKEN=your_deepseek_token

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key

# Mistral
MISTRAL_API_KEY=your_mistral_key

# Eigent AI
EIGENT_API_KEY=your_eigent_key
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_backend.py

# With coverage
python -m pytest tests/ --cov=multi_ai_cli --cov-report=html
```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make changes**:
   - Add new backends in `backends/`
   - Add new tools in `tools/`
   - Add new FOSS alternatives in `foss/`

3. **Test changes**:
   ```bash
   python cli.py <command> <args>
   ```

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "Add new feature"
   ```

5. **Push to branch**:
   ```bash
   git push origin feature/new-feature
   ```

## Adding New Backends

To add a new AI backend:

1. Create a new file in `backends/`:
   ```python
   from .base import ChatBackend
   
   class NewBackend(ChatBackend):
       def __init__(self, session_manager):
           self.session_manager = session_manager
           # Initialize backend
           
       def is_available(self) -> bool:
           # Check if backend is available
           return True
           
       def send_message(self, message: str, context: list[dict] = None) -> str:
           # Send message and return response
           return "Response"
   ```

2. Register the backend in `core/chat_dispatcher.py`:
   ```python
   from backends.new_backend import NewBackend
   
   BACKENDS = {
       # ... existing backends
       "new": NewBackend,
   }
   ```

3. Add CLI command in `cli.py` (optional)

## Adding New Tools

To add a new tool:

1. Create a new file in `tools/`:
   ```python
   class NewTool:
       def __init__(self, session_manager = None):
           self.session_manager = session_manager
           
       def execute(self, *args, **kwargs):
           # Tool logic
           return result
   ```

2. Export in `tools/__init__.py`:
   ```python
   from .new_tool import NewTool
   __all__ = ["NewTool"]
   ```

3. Add CLI command in `cli.py`

## Debugging

### Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Interactive Debugging

```python
from core.chat_dispatcher import ChatDispatcher
from core.session_manager import SessionManager

mgr = SessionManager()
dispatcher = ChatDispatcher(mgr)

# Test backend
response = dispatcher.send("deepseek", "Hello, world!")
print(response)
```

### Error Handling

All backends should handle errors gracefully:

```python
try:
    # Backend operation
    response = backend.send_message(prompt)
except Exception as e:
    # Log error
    logging.error(f"Backend error: {e}")
    # Return user-friendly error
    return f"Error: {str(e)}"
```
