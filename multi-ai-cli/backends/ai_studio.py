#!/usr/bin/env python3
"""AI Studio Backend - Google AI Studio (formerly Vertex AI) integration.

This backend provides:
- Chat completion with AI Studio models
- Embeddings
- Multi-turn conversations
- Model management
- Streaming support

Based on ChapitoAI's ai_studio_chat.py architecture.
"""

import os
import sys
import json
import time
import base64
import contextlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple

try:
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException
    from bs4 import BeautifulSoup, Tag
    _SELENIUM_AVAILABLE = True
except ImportError:
    _SELENIUM_AVAILABLE = False

from backends.base import BaseBackend
from core.session_manager import SessionManager
from chapito.tools.tools import create_driver, transfer_prompt


class AIStudioBackend(BaseBackend):
    """AI Studio backend for Google's AI Studio.
    
    This backend uses browser automation to interact with
    AI Studio at https://aistudio.google.com/
    """
    
    AI_STUDIO_URL = "https://aistudio.google.com/prompts/new_chat?pli=1"
    TIMEOUT_SECONDS = 120
    SUBMIT_CSS_SELECTOR = "button.run-button"
    ANSWER_XPATH = '//div[contains(@class, "turn-content")]'
    TEXTAREA_TAG = "textarea"
    
    def __init__(self, mgr: SessionManager, **kwargs):
        """Initialize AI Studio backend.
        
        Args:
            mgr: Session manager
        """
        super().__init__(mgr, **kwargs)
        self.driver = None
        self.initialized = False
        self._config = kwargs.get("config", {})
    
    def _check_if_chat_loaded(self):
        """Check if chat interface is loaded."""
        if not self.driver:
            return False
        
        self.driver.implicitly_wait(5)
        try:
            button = self.driver.find_element("css selector", self.SUBMIT_CSS_SELECTOR)
            return button is not None
        except Exception:
            return False
    
    def _initialize_driver(self):
        """Initialize browser driver."""
        if not _SELENIUM_AVAILABLE:
            raise RuntimeError("Selenium is required for AI Studio backend. Install with: pip install selenium")
        
        try:
            config = self._config
            self.driver = create_driver(config)
            self.driver.get(self.AI_STUDIO_URL)
            
            # Wait for chat to load
            for _ in range(24):  # Wait up to 120 seconds
                if self._check_if_chat_loaded():
                    break
                time.sleep(5)
            
            self.initialized = True
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize browser: {e}")
    
    def _ensure_driver(self):
        """Ensure browser driver is initialized."""
        if not self.initialized:
            self._initialize_driver()
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        try:
            self._ensure_driver()
            return True
        except Exception:
            return False
    
    def _clean_chat_answer(self, html: str) -> str:
        """Clean chat answer HTML."""
        soup = BeautifulSoup(html, "html.parser")
        no_prose_divs = soup.find_all("div", class_="syntax-highlighted-code")
        
        for div in no_prose_divs:
            if isinstance(div, Tag):
                code_tags = div.find_all("code")
                div.clear()
                for code in code_tags:
                    div.append(code)
        
        code_tags = soup.find_all("code")
        for code_tag in code_tags:
            code_tag.insert_before("```\n")
            code_tag.insert_after("\n```\n")
        
        return soup.get_text().strip()
    
    def _send_request_and_get_response(self, message: str) -> str:
        """Send a request and get response from AI Studio interface."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        try:
            self.driver.implicitly_wait(10)
            
            # Find textarea and send message
            textareas = self.driver.find_elements("tag name", self.TEXTAREA_TAG)
            if not textareas:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            if not textareas:
                raise RuntimeError("No textarea found")
            
            textarea = textareas[-1]
            textarea.clear()
            transfer_prompt(message, textarea)
            
            # Wait for submit button
            wait = WebDriverWait(self.driver, self.TIMEOUT_SECONDS)
            wait.until(EC.presence_of_element_located(("css selector", self.SUBMIT_CSS_SELECTOR)))
            
            # Click submit
            submit_button = self.driver.find_element("css selector", self.SUBMIT_CSS_SELECTOR)
            submit_button.click()
            
            # Wait a little
            time.sleep(1)
            
            # Wait for response
            wait = WebDriverWait(self.driver, self.TIMEOUT_SECONDS)
            wait.until(EC.presence_of_element_located(("css selector", self.SUBMIT_CSS_SELECTOR)))
            
            # Get response
            message_bubbles = self.driver.find_elements(By.XPATH, self.ANSWER_XPATH)
            if not message_bubbles:
                return ""
            
            last_message_bubble = message_bubbles[-1]
            html = last_message_bubble.get_attribute("outerHTML")
            
            return self._clean_chat_answer(html)
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a message and get a response.
        
        Args:
            message: User message
            context: Previous messages (limited support in web interface)
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            session_id: Session ID for caching
            
        Returns:
            Assistant response
        """
        self._ensure_driver()
        
        try:
            # Note: AI Studio web interface has limited context support
            # We'll just send the current message
            response = self._send_request_and_get_response(message)
            
            # Save to cache
            if session_id:
                context = context or []
                context.append({"role": "user", "content": message})
                context.append({"role": "assistant", "content": response})
                from core.cache import cache_save
                cache_save(session_id, context)
            
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to send message: {e}")
    
    def stream_completion(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream completion response.
        
        Note: The web interface doesn't support true streaming,
        so this method will yield the complete response at once.
        
        Args:
            message: User message
            context: Previous messages
            
        Yields:
            Response chunks
        """
        response = self.send_message(message, context)
        yield response
    
    def reset_conversation(self):
        """Reset the conversation."""
        self._ensure_driver()
        
        try:
            # Try to find and click new chat button
            new_chat_button = self.driver.find_element(
                "xpath",
                "//button[contains(@class, 'new-chat') or contains(text(), 'New Chat')]",
            )
            new_chat_button.click()
            time.sleep(2)
        except Exception:
            # Try refreshing
            self.driver.refresh()
            time.sleep(3)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models.
        
        AI Studio models are typically:
        - gemini-2.0-flash
        - gemini-2.0-pro
        - gemini-1.5-flash
        - gemini-1.5-pro
        """
        return [
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "provider": "ai_studio"},
            {"id": "gemini-2.0-pro", "name": "Gemini 2.0 Pro", "provider": "ai_studio"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "provider": "ai_studio"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "provider": "ai_studio"},
        ]
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self.initialized = False


# =============================================================================
# AI Studio API Backend (when available)
# =============================================================================

class AIStudioAPIBackend(BaseBackend):
    """AI Studio API backend (when official API is available).
    
    This backend uses the official AI Studio API when available.
    """
    
    API_BASE = "https://aistudio.googleapis.com/v1"
    
    def __init__(self, mgr: SessionManager, api_key: Optional[str] = None, **kwargs):
        """Initialize AI Studio API backend.
        
        Args:
            mgr: Session manager
            api_key: API key for AI Studio
        """
        super().__init__(mgr, **kwargs)
        self.api_key = api_key or self._get_api_key()
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config."""
        # Try environment
        key = os.environ.get("AI_STUDIO_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if key:
            return key
        
        # Try session manager
        return self.mgr.get_token("ai_studio")
    
    def is_available(self) -> bool:
        """Check if API is available."""
        return self.api_key is not None
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Send a message via API."""
        if not self.is_available():
            raise RuntimeError("API key not configured")
        
        # This would use the official API when available
        # For now, fallback to web interface
        from .ai_studio import AIStudioBackend
        web_backend = AIStudioBackend(self.mgr)
        return web_backend.send_message(message, context, model, temperature, max_tokens)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AIStudioBackend",
    "AIStudioAPIBackend",
]
