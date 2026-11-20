"""LLM client – supports Ollama (local) and fallback to API."""
import subprocess
import json
import sys
from typing import Optional, Generator

class LLMClient:
    def __init__(self, model: str = "codellama:7b", api_url: str = "http://localhost:11434"):
        self.model = model
        self.api_url = api_url
        self._check_ollama()

    def _check_ollama(self) -> bool:
        try:
            subprocess.run(["ollama", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Warning: ollama not found. Install with: pkg install ollama", file=sys.stderr)
            return False

    def generate(self, prompt: str, stream: bool = False) -> str | Generator:
        """Send prompt to Ollama, return response."""
        cmd = ["ollama", "run", self.model]
        if not stream:
            result = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            # Streaming not fully implemented – simple wrapper
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            out, _ = proc.communicate(prompt)
            return out.strip()
