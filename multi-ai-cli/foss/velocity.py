"""
Velocity Backend
Terminal-first, completely model-agnostic agentic coding engine.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backends.base import ChatBackend


class VelocityBackend(ChatBackend):
    """
    Velocity - A terminal-first, completely model-agnostic agentic coding engine.
    
    Built specifically for resource-constrained environments where running
    the official Google binary is unfeasible.
    
    Features:
    - Model-agnostic (works with any LLM provider)
    - Terminal-first design
    - Lightweight and fast
    - Supports Ollama, OpenRouter, DeepSeek, and more
    - Built-in code execution and analysis
    """
    
    def __init__(self, 
                 session_manager,
                 model: str = "default",
                 provider: str = "auto",
                 config_path: str = None):
        """
        Initialize Velocity backend.
        
        Args:
            session_manager: Session manager
            model: Model to use
            provider: Provider to use ("auto", "ollama", "openrouter", etc.)
            config_path: Optional path to Velocity config
        """
        self.session_manager = session_manager
        self.model = model
        self.provider = provider
        self.config_path = config_path
        self._client = None
        
    def _get_client(self):
        """Lazy load Velocity client."""
        if self._client is None:
            try:
                # Try to import Velocity
                import velocity
                self._client = velocity.Client(
                    model=self.model,
                    provider=self.provider
                )
            except ImportError:
                # Fall back to generic implementation
                self._client = "generic"
        return self._client
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            client = self._get_client()
            if client == "generic":
                # Check if we can use any provider
                return self._check_generic_available()
            return True
        except Exception:
            return False
    
    def _check_generic_available(self) -> bool:
        """Check if generic implementation is available."""
        # Check for common providers
        providers = ["ollama", "openrouter", "deepseek", "mistral"]
        
        for provider in providers:
            try:
                if provider == "ollama":
                    import subprocess
                    result = subprocess.run(
                        ["ollama", "list"],
                        capture_output=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        return True
                elif provider == "openrouter":
                    if os.environ.get("OPENROUTER_API_KEY"):
                        return True
                elif provider == "deepseek":
                    if os.environ.get("DEEPSEEK_TOKEN"):
                        return True
                elif provider == "mistral":
                    if os.environ.get("MISTRAL_API_KEY"):
                        return True
            except Exception:
                continue
        
        return False
    
    def send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Send a message using Velocity.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        try:
            client = self._get_client()
            
            if client != "generic":
                # Use Velocity client
                messages = []
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": message})
                
                response = client.chat(messages=messages)
                return response.get("content", str(response))
            else:
                # Use generic implementation
                return self._generic_send(message, context)
                
        except Exception as e:
            raise RuntimeError(f"Velocity error: {e}")
    
    def _generic_send(self, message: str, context: List[Dict[str, Any]]) -> str:
        """Generic send implementation."""
        try:
            # Build prompt from context
            prompt_parts = []
            for msg in context:
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                prompt_parts.append(f"{role}: {content}")
            prompt_parts.append(f"USER: {message}")
            prompt_parts.append("ASSISTANT:")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            # Use provider based on configuration
            if self.provider == "auto":
                # Try providers in order
                for provider in ["ollama", "openrouter", "deepseek", "mistral"]:
                    try:
                        return self._send_with_provider(full_prompt, provider)
                    except Exception:
                        continue
                raise RuntimeError("No working provider found")
            else:
                return self._send_with_provider(full_prompt, self.provider)
                
        except Exception as e:
            raise RuntimeError(f"Generic send error: {e}")
    
    def _send_with_provider(self, prompt: str, provider: str) -> str:
        """Send prompt with specific provider."""
        if provider == "ollama":
            import requests
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "top_p": 0.9}
            }
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", str(data))
        
        elif provider == "openrouter":
            import requests
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise RuntimeError("OpenRouter API key required")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
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
        
        elif provider == "deepseek":
            from backends.deepseek import DeepSeekBackend
            backend = DeepSeekBackend(self.session_manager)
            return backend.send_message(prompt)
        
        elif provider == "mistral":
            import requests
            api_key = os.environ.get("MISTRAL_API_KEY")
            if not api_key:
                raise RuntimeError("Mistral API key required")
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 4096
            }
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", str(data))
        
        else:
            raise RuntimeError(f"Unsupported provider: {provider}")
    
    async def async_send_message(self, message: str, context: List[Dict[str, Any]] = None) -> str:
        """
        Async version of send_message.
        
        Args:
            message: The user message/prompt
            context: Optional conversation context
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = []
        
        try:
            client = self._get_client()
            
            if client != "generic":
                messages = []
                for msg in context:
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    messages.append({"role": role, "content": content})
                messages.append({"role": "user", "content": message})
                
                response = await client.async_chat(messages=messages)
                return response.get("content", str(response))
            else:
                # For generic, run in thread pool
                import asyncio
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: self.send_message(message, context)
                )
                
        except Exception as e:
            raise RuntimeError(f"Async Velocity error: {e}")
    
    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a Velocity workflow.
        
        Args:
            name: Workflow name
            steps: List of workflow steps
            
        Returns:
            Workflow definition
        """
        try:
            client = self._get_client()
            
            if client != "generic":
                workflow = client.create_workflow(name=name, steps=steps)
                return workflow.to_dict()
            else:
                # Generic workflow implementation
                return {
                    "name": name,
                    "steps": steps,
                    "provider": "generic",
                    "model": self.model
                }
                
        except Exception as e:
            raise RuntimeError(f"Workflow creation failed: {e}")
    
    def execute_workflow(self, workflow_name: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a Velocity workflow.
        
        Args:
            workflow_name: Name of the workflow
            inputs: Optional inputs for the workflow
            
        Returns:
            Workflow execution result
        """
        if inputs is None:
            inputs = {}
        
        try:
            client = self._get_client()
            
            if client != "generic":
                result = client.execute_workflow(workflow_name=workflow_name, inputs=inputs)
                return result.to_dict()
            else:
                # Generic workflow execution
                # This would execute each step sequentially
                result = {"status": "success", "outputs": {}, "steps": []}
                
                for step in inputs.get("steps", []):
                    step_name = step.get("name", "unknown")
                    step_prompt = step.get("prompt", "")
                    
                    # Execute step
                    step_result = self.send_message(step_prompt)
                    result["steps"].append({
                        "name": step_name,
                        "output": step_result
                    })
                
                return result
                
        except Exception as e:
            raise RuntimeError(f"Workflow execution failed: {e}")
    
    def code_completion(self, prefix: str, language: str = "python") -> Dict[str, Any]:
        """
        Get code completions.
        
        Args:
            prefix: Code prefix to complete
            language: Programming language
            
        Returns:
            Completion suggestions
        """
        try:
            prompt = f"""
Complete the following {language} code:

{prefix}

Provide 3-5 completion suggestions with brief explanations.
"""
            
            response = self.send_message(prompt)
            
            # Parse response into structured format
            return {
                "status": "success",
                "prefix": prefix,
                "language": language,
                "completions": response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "prefix": prefix,
                "language": language
            }
