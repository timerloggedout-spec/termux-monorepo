#!/usr/bin/env python3
"""Mistral AI Backend - Official Mistral AI API integration.

This backend provides integration with Mistral AI's official API:
- Chat completion (mistral-tiny, mistral-small, mistral-medium, mistral-large)
- Embeddings
- Fine-tuning (future)
- Model management (future)

API Documentation: https://docs.mistral.ai/api/
"""

import os
import sys
import json
import time
import base64
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from pathlib import Path

from .base import BaseBackend
from core.core import get_token, http_post, http_get
from core.cache import cache_load, cache_save


class MistralAIBackend(BaseBackend):
    """Mistral AI API backend.
    
    This backend communicates with Mistral AI's official API endpoints.
    """
    
    API_BASE = "https://api.mistral.ai/v1"
    
    # Model information
    MODELS = {
        "mistral-tiny": {"max_tokens": 32768, "context_window": 32768},
        "mistral-small": {"max_tokens": 32768, "context_window": 32768},
        "mistral-medium": {"max_tokens": 32768, "context_window": 32768},
        "mistral-large": {"max_tokens": 32768, "context_window": 32768},
        "codestral-latest": {"max_tokens": 32768, "context_window": 32768},
    }
    
    def __init__(self, mgr, **kwargs):
        """Initialize Mistral AI backend.
        
        Args:
            mgr: Session manager
            **kwargs: Additional arguments
        """
        super().__init__(mgr, **kwargs)
        self.api_key = self._get_api_key()
        self.base_url = kwargs.get("base_url", self.API_BASE)
    
    def _get_api_key(self) -> Optional[str]:
        """Get Mistral AI API key."""
        # Try environment variable
        key = os.environ.get("MISTRAL_API_KEY")
        if key:
            return key
        
        # Try token file
        token_dir = Path.home() / ".multi-ai-cli" / "tokens"
        mistral_token = token_dir / "mistralai.token"
        if mistral_token.exists():
            try:
                return mistral_token.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        
        # Try session manager
        key = self.mgr.get_token("mistralai")
        if key:
            return key
        
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        return self.api_key is not None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        if not self.is_available():
            return []
        
        try:
            response = http_get(
                f"{self.base_url}/models",
                headers=self._get_headers(),
            )
            if response.get("status") == 200:
                return response.get("data", {}).get("data", [])
        except Exception:
            pass
        
        return list(self.MODELS.keys())
    
    def get_model(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if not self.is_available():
            return {}
        
        try:
            response = http_get(
                f"{self.base_url}/models/{model_name}",
                headers=self._get_headers(),
            )
            if response.get("status") == 200:
                return response.get("data", {})
        except Exception:
            pass
        
        return self.MODELS.get(model_name, {})
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "mistral-large",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a message and get a response.
        
        Args:
            message: User message
            context: Previous messages for context
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            session_id: Session ID for caching
            
        Returns:
            Assistant response
        """
        if not self.is_available():
            raise RuntimeError("Mistral AI API key not configured")
        
        # Build messages array
        messages = []
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        # Build request
        request = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
        }
        
        if max_tokens:
            request["max_tokens"] = max_tokens
        
        # Send request
        response = self._chat_completion(request)
        
        # Extract response
        if response and "choices" in response:
            choice = response["choices"][0]
            content = choice.get("message", {}).get("content", "")
            
            # Save to cache
            if session_id:
                context = context or []
                context.append({"role": "user", "content": message})
                context.append({"role": "assistant", "content": content})
                cache_save(session_id, context)
            
            return content
        
        return ""
    
    def _chat_completion(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make chat completion request."""
        try:
            response = http_post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json_data=request,
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Chat completion failed: {e}")
    
    def stream_completion(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "mistral-large",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream completion response.
        
        Args:
            message: User message
            context: Previous messages for context
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter
            
        Yields:
            Response chunks
        """
        if not self.is_available():
            raise RuntimeError("Mistral AI API key not configured")
        
        # Build messages array
        messages = []
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        # Build request
        request = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": True,
        }
        
        if max_tokens:
            request["max_tokens"] = max_tokens
        
        # Stream response
        try:
            from core.core import curl_requests
            
            session = curl_requests.Session()
            session.headers.update(self._get_headers())
            
            response = session.post(
                f"{self.base_url}/chat/completions",
                json=request,
                stream=True,
            )
            
            for chunk in response.iter_lines():
                if chunk:
                    try:
                        data = json.loads(chunk.decode('utf-8'))
                        if "choices" in data and len(data["choices"]) > 0:
                            choice = data["choices"][0]
                            content = choice.get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            raise RuntimeError(f"Stream completion failed: {e}")
    
    def create_embedding(
        self,
        text: str,
        model: str = "mistral-embed",
        **kwargs
    ) -> List[float]:
        """Create text embedding.
        
        Args:
            text: Text to embed
            model: Embedding model to use
            
        Returns:
            Embedding vector
        """
        if not self.is_available():
            raise RuntimeError("Mistral AI API key not configured")
        
        request = {
            "model": model,
            "input": text,
        }
        
        try:
            response = http_post(
                f"{self.base_url}/embeddings",
                headers=self._get_headers(),
                json_data=request,
            )
            
            if response.get("status") == 200:
                data = response.get("data", {})
                embeddings = data.get("data", [])
                if embeddings:
                    return embeddings[0].get("embedding", [])
        except Exception as e:
            raise RuntimeError(f"Embedding creation failed: {e}")
        
        return []
    
    def create_embeddings(
        self,
        texts: List[str],
        model: str = "mistral-embed",
        **kwargs
    ) -> List[List[float]]:
        """Create embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            model: Embedding model to use
            
        Returns:
            List of embedding vectors
        """
        if not self.is_available():
            raise RuntimeError("Mistral AI API key not configured")
        
        request = {
            "model": model,
            "input": texts,
        }
        
        try:
            response = http_post(
                f"{self.base_url}/embeddings",
                headers=self._get_headers(),
                json_data=request,
            )
            
            if response.get("status") == 200:
                data = response.get("data", {})
                embeddings = data.get("data", [])
                return [e.get("embedding", []) for e in embeddings]
        except Exception as e:
            raise RuntimeError(f"Embedding creation failed: {e}")
        
        return [[] for _ in texts]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "MistralAIBackend",
]
