#!/usr/bin/env python3
"""Mistral Web Backend - Mistral AI chat interface via web browser automation.

This backend provides integration with Mistral AI's web interface
(https://chat.mistral.ai/) using browser automation.

Note: This backend requires a browser and appropriate drivers (selenium, etc.)
"""

import os
import sys
import json
import time
import base64
from typing import Optional, Dict, Any, List, Union, Generator
from pathlib import Path

from .base import BaseBackend


class MistralWebBackend(BaseBackend):
    """Mistral AI web interface backend.
    
    This backend uses browser automation to interact with Mistral AI's
    web chat interface at https://chat.mistral.ai/
    """
    
    MISTRAL_URL = "https://chat.mistral.ai/"
    TIMEOUT_SECONDS = 120
    SUBMIT_CSS_SELECTOR = 'button[type="submit"]'
    TEXTAREA_CSS_SELECTOR = 'textarea[name="message.text"]'
    ANSWER_CSS_SELECTOR = "div.prose"
    SCROLL_DOWN_CSS_SELECTOR = 'button.disabled\\:pointer-auto[type="button"]'
    
    def __init__(self, mgr, **kwargs):
        """Initialize Mistral web backend.
        
        Args:
            mgr: Session manager
            **kwargs: Additional arguments
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
        try:
            from chapito.tools.tools import create_driver
            
            config = self._config
            self.driver = create_driver(config)
            self.driver.get(self.MISTRAL_URL)
            
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
    
    def _send_request_and_get_response(self, message):
        """Send a request and get response from web interface."""
        if not self.driver:
            raise RuntimeError("Driver not initialized")
        
        import contextlib
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        from bs4 import BeautifulSoup
        
        self.driver.implicitly_wait(10)
        
        # Find textarea and send message
        textarea = self.driver.find_element("css selector", self.TEXTAREA_CSS_SELECTOR)
        
        # Transfer prompt
        textarea.clear()
        textarea.send_keys(message)
        
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
        message_bubbles = self.driver.find_elements("css selector", self.ANSWER_CSS_SELECTOR)
        if not message_bubbles:
            return ""
        
        last_message_bubble = message_bubbles[-1]
        html = last_message_bubble.get_attribute("outerHTML")
        
        # Clean message
        return self._clean_chat_answer(html)
    
    def _clean_chat_answer(self, html):
        """Clean chat answer HTML."""
        from bs4 import BeautifulSoup, Tag
        
        soup = BeautifulSoup(html, "html.parser")
        no_prose_divs = soup.find_all("div", class_="sticky")
        for div in no_prose_divs:
            if isinstance(div, Tag):
                div.clear()
        
        code_tags = soup.find_all("code")
        for code_tag in code_tags:
            code_tag.insert_before("```\n")
            code_tag.insert_after("\n```\n")
        
        return soup.get_text().strip()
    
    def send_message(
        self,
        message: str,
        context: Optional[List[Dict[str, Any]]] = None,
        model: str = "mistral-large",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        session_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send a message and get a response.
        
        Args:
            message: User message
            context: Previous messages for context (not fully supported in web interface)
            model: Model to use (may not be selectable in web interface)
            temperature: Sampling temperature (may not be adjustable in web interface)
            max_tokens: Maximum tokens to generate
            session_id: Session ID for caching
            
        Returns:
            Assistant response
        """
        self._ensure_driver()
        
        try:
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
            context: Previous messages for context
            
        Yields:
            Response chunks
        """
        response = self.send_message(message, context)
        yield response
    
    def reset_conversation(self):
        """Reset the conversation in the web interface."""
        self._ensure_driver()
        
        try:
            # Try to find and click new chat button
            new_chat_button = self.driver.find_element(
                "xpath",
                "//button[contains(@class, 'new-chat') or contains(text(), 'New Chat')]"
            )
            new_chat_button.click()
            time.sleep(2)
        except Exception:
            # Try refreshing
            self.driver.refresh()
            time.sleep(3)
    
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
# Module Exports
# =============================================================================

__all__ = [
    "MistralWebBackend",
]
