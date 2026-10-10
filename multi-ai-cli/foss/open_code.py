"""
OpenCode Backend
Terminal-first, completely model-agnostic agentic coding engine.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backends.base import ChatBackend


class OpenCodeBackend(ChatBackend):
    """
    OpenCode - A terminal-first, completely model-agnostic agentic coding engine.
    
    Features:
    - Built specifically for resource-constrained environments
    - Model-agnostic (Ollama, OpenRouter, DeepSeek, etc.)
    - Lightweight and fast
    - Perfect for environments where running the official Google binary is unfeasible
    
    GitHub: https://github.com/topics/antigravity-ai
    """
    
    def __init__(self, 
                 session_manager,
                 model: str = "default",
                 provider: str = "ollama",
                 base_url: str = None):
        """
        Initialize OpenCode backend.
        
        Args:
            session_manager: Session manager
            model: Model to use
            provider: Provider to use ("ollama", "openrouter", "deepseek", etc.)
            base_url: Optional base URL for provider
        """
        self.session_manager = session_manager
        self.model = model
        self.provider = provider
        self.base_url = base_url
        self._api_key = self._get_api_key()
        
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        # Check environment variables based on provider
        env_vars = {
            "openrouter": "OPENROUTER_API_KEY",
            "deepseek": "DEEPSEEK_TOKEN",
            "ollama": None,  # Ollama doesn't need API key
            "mistral": "MISTRAL_API_KEY",
            "groq": "GROQ_API_KEY",
        }
        
        env_var = env_vars.get(self.provider)
        if env_var:
            api_key = os.environ.get(env_var)
            if api_key:
                return api_key
        
        # Check config from session manager
        api_key = self.session_manager.get("opencode", "api_key")
        if api_key:
            return api_key
        
        # Try provider-specific config
        api_key = self.session_manager.get(self.provider, "api_key")
        if api_key:
            return api_key
        
        return None
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            # Check if we can communicate with the provider
            if self.provider == "ollama":
                # Check if Ollama is running
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            elif self.provider == "openrouter":
                return bool(self._api_key)
            elif self.provider == "deepseek":
                return bool(self._api_key)
            else:
                return True
        except Exception:
            return False
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message using OpenCode.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        try:
            # Build messages for OpenCode
            messages = []
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": message})
            
            # Use provider-specific implementation
            if self.provider == "ollama":
                return self._ollama_chat(messages)
            elif self.provider == "openrouter":
                return self._openrouter_chat(messages)
            elif self.provider == "deepseek":
                return self._deepseek_chat(messages)
            else:
                # Generic implementation
                return self._generic_chat(messages)
                
        except Exception as e:
            raise RuntimeError(f"OpenCode error: {e}")
    
    def _ollama_chat(self, messages: List[Dict[str, Any]]) -> str:
        """Chat with Ollama."""
        try:
            import requests
            
            # Get base URL or use default
            url = self.base_url or "http://localhost:11434"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                f"{url}/api/chat",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("message", {}).get("content", str(data))
            
        except Exception as e:
            raise RuntimeError(f"Ollama chat error: {e}")
    
    def _openrouter_chat(self, messages: List[Dict[str, Any]]) -> str:
        """Chat with OpenRouter."""
        try:
            import requests
            
            if not self._api_key:
                raise RuntimeError("OpenRouter API key required")
            
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4096
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", str(data))
            
        except Exception as e:
            raise RuntimeError(f"OpenRouter chat error: {e}")
    
    def _deepseek_chat(self, messages: List[Dict[str, Any]]) -> str:
        """Chat with DeepSeek."""
        try:
            from backends.deepseek import DeepSeekBackend
            
            backend = DeepSeekBackend(self.session_manager)
            
            # Convert messages to context format
            context = []
            for msg in messages[:-1]:  # All but last
                context.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
            
            # Send the last message
            last_message = messages[-1].get("content", "")
            return backend.send_message(last_message, context)
            
        except Exception as e:
            raise RuntimeError(f"DeepSeek chat error: {e}")
    
    def _generic_chat(self, messages: List[Dict[str, Any]]) -> str:
        """Generic chat implementation."""
        try:
            # Try to use subprocess to call the model directly
            # This is a fallback for custom providers
            
            # Convert messages to text
            prompt = "\n".join(
                f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
                for msg in messages
            )
            
            # Add model specification
            full_prompt = f"Model: {self.model}\n\n{prompt}\n\nAssistant:"
            
            # Use a simple LLM interface
            import requests
            
            # Try different endpoints
            endpoints = [
                "http://localhost:8000/chat",
                "http://localhost:11434/api/generate",
                "http://localhost:8080/v1/chat/completions",
            ]
            
            for endpoint in endpoints:
                try:
                    payload = {
                        "model": self.model,
                        "prompt": full_prompt,
                        "max_tokens": 4096,
                        "temperature": 0.7
                    }
                    
                    response = requests.post(
                        endpoint,
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, dict):
                            return data.get("response", data.get("content", str(data)))
                        else:
                            return str(data)
                except Exception:
                    continue
            
            raise RuntimeError("No working endpoint found")
            
        except Exception as e:
            raise RuntimeError(f"Generic chat error: {e}")
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Execute code using OpenCode.
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution result
        """
        try:
            prompt = f"""
Execute the following {language} code and return the output:

```{language}
{code}
```

If there are errors, explain them. If successful, return the output.
"""
            
            response = self.send_message(prompt)
            
            return {
                "status": "success",
                "output": response,
                "language": language
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "language": language
            }
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code using OpenCode.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis result
        """
        try:
            prompt = f"""
Analyze the following {language} code and provide:

1. **Code Quality**:
   - Style and formatting issues
   - Naming conventions
   - Documentation

2. **Potential Bugs**:
   - Logical errors
   - Edge cases
   - Error handling

3. **Performance**:
   - Time complexity
   - Space complexity
   - Optimizations

4. **Security**:
   - Vulnerabilities
   - Hardcoded secrets
   - Input validation

Code:
```{language}
{code}
```
"""
            
            response = self.send_message(prompt)
            
            return {
                "status": "success",
                "analysis": response,
                "language": language
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "language": language
            }
    
    def generate_code(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate code using OpenCode.
        
        Args:
            prompt: Description of code to generate
            language: Programming language
            
        Returns:
            Generated code
        """
        try:
            full_prompt = f"Generate {language} code for: {prompt}"
            
            response = self.send_message(full_prompt)
            
            return {
                "status": "success",
                "code": response,
                "language": language,
                "prompt": prompt
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "language": language,
                "prompt": prompt
            }
