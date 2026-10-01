#!/usr/bin/env python3
"""Termux Hub - Central router/proxy for multi-provider AI integration.

This module provides the main Hub implementation that:
- Routes requests to appropriate providers (Mistralai, DeepSeek, aiStudio, ChapitoAI, Collab)
- Manages agent sessions
- Handles transport layer (stdio > curl_cffi)
- Provides Termux-specific integration
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, Tuple, Generator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Import transport layers
from ..webwrapper.stdio_transport import StdioTransport, StdioTransportError
from ..webwrapper.curl_cffi_transport import CurlCffiTransport, CurlCffiTransportError

# Import provider backends
try:
    from ..backends.mistralai import MistralAIBackend
    from ..backends.deepseek import DeepSeekBackend
    from ..backends.ai_studio import AIStudioBackend
    from ..backends.chapito import ChapitoBackend
    from ..collab.colab_backend import ColabBackend
    _BACKENDS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some backends not available: {e}")
    _BACKENDS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TermuxHubError(Exception):
    """Exception for Termux Hub errors."""
    pass


class ProviderType(Enum):
    """Supported provider types."""
    MISTRAL = "mistralai"
    DEEPSEEK = "deepseek"
    AI_STUDIO = "ai_studio"
    CHAPITO = "chapito"
    COLLAB = "colab"
    CUSTOM = "custom"


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: str
    provider_type: ProviderType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    proxy: Optional[str] = None
    impersonate: Optional[str] = None
    custom_command: Optional[str] = None
    enabled: bool = True
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionConfig:
    """Configuration for an agent session."""
    session_id: str
    provider: str
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


class TermuxHub:
    """Central Hub for Termux-based multi-provider AI integration.
    
    This class provides:
    - Provider routing and load balancing
    - Session management
    - Transport layer abstraction
    - Termux-specific features
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        default_provider: str = "mistralai",
        enable_logging: bool = True,
    ):
        """Initialize Termux Hub.
        
        Args:
            config_dir: Directory for configuration files
            default_provider: Default provider to use
            enable_logging: Whether to enable logging
        """
        # Configuration
        self.config_dir = Path(config_dir or os.path.expanduser("~/.termux_ai_hub"))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_provider = default_provider
        self.enable_logging = enable_logging
        
        # Provider registry
        self._providers: Dict[str, ProviderConfig] = {}
        self._provider_instances: Dict[str, Any] = {}
        
        # Session management
        self._sessions: Dict[str, SessionConfig] = {}
        self._active_sessions: Dict[str, Any] = {}
        
        # Transport layer
        self._transport: Optional[Union[StdioTransport, CurlCffiTransport]] = None
        
        # Initialize logging
        if self.enable_logging:
            self._setup_logging()
        
        # Load configuration
        self._load_config()
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info(f"Termux Hub initialized with {len(self._providers)} providers")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = self.config_dir / "hub.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
    
    def _load_config(self):
        """Load configuration from file."""
        config_file = self.config_dir / "config.json"
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                
                # Load providers
                for name, provider_config in config.get("providers", {}).items():
                    try:
                        provider_type = ProviderType(provider_config.get("type", "custom"))
                    except ValueError:
                        provider_type = ProviderType.CUSTOM
                    
                    self._providers[name] = ProviderConfig(
                        name=name,
                        provider_type=provider_type,
                        api_key=provider_config.get("api_key"),
                        base_url=provider_config.get("base_url"),
                        timeout=provider_config.get("timeout", 30.0),
                        max_retries=provider_config.get("max_retries", 3),
                        proxy=provider_config.get("proxy"),
                        impersonate=provider_config.get("impersonate"),
                        custom_command=provider_config.get("custom_command"),
                        enabled=provider_config.get("enabled", True),
                        priority=provider_config.get("priority", 0),
                        metadata=provider_config.get("metadata", {}),
                    )
                
                # Load default provider
                self.default_provider = config.get("default_provider", self.default_provider)
                
                logger.info(f"Loaded configuration from {config_file}")
                
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            # Create default configuration
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file."""
        default_config = {
            "default_provider": self.default_provider,
            "providers": {
                "mistralai": {
                    "type": "mistralai",
                    "enabled": True,
                    "priority": 1,
                },
                "deepseek": {
                    "type": "deepseek",
                    "enabled": True,
                    "priority": 2,
                },
                "ai_studio": {
                    "type": "ai_studio",
                    "enabled": True,
                    "priority": 3,
                },
                "chapito": {
                    "type": "chapito",
                    "enabled": True,
                    "priority": 4,
                },
                "colab": {
                    "type": "colab",
                    "enabled": True,
                    "priority": 5,
                },
            },
        }
        
        config_file = self.config_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Created default configuration at {config_file}")
        
        # Load the default config
        self._load_config()
    
    def _initialize_providers(self):
        """Initialize provider instances."""
        if not _BACKENDS_AVAILABLE:
            logger.warning("Backend modules not available, skipping provider initialization")
            return
        
        for name, config in self._providers.items():
            if not config.enabled:
                continue
            
            try:
                if config.provider_type == ProviderType.MISTRAL:
                    self._provider_instances[name] = MistralAIBackend(
                        api_key=config.api_key,
                        base_url=config.base_url,
                        timeout=config.timeout,
                        max_retries=config.max_retries,
                    )
                elif config.provider_type == ProviderType.DEEPSEEK:
                    self._provider_instances[name] = DeepSeekBackend(
                        api_key=config.api_key,
                        base_url=config.base_url,
                        timeout=config.timeout,
                        max_retries=config.max_retries,
                    )
                elif config.provider_type == ProviderType.AI_STUDIO:
                    self._provider_instances[name] = AIStudioBackend(
                        api_key=config.api_key,
                        base_url=config.base_url,
                        timeout=config.timeout,
                        max_retries=config.max_retries,
                    )
                elif config.provider_type == ProviderType.CHAPITO:
                    self._provider_instances[name] = ChapitoBackend(
                        api_key=config.api_key,
                        base_url=config.base_url,
                        timeout=config.timeout,
                        max_retries=config.max_retries,
                    )
                elif config.provider_type == ProviderType.COLLAB:
                    self._provider_instances[name] = ColabBackend(
                        timeout=config.timeout,
                        max_retries=config.max_retries,
                    )
                
                logger.info(f"Initialized provider: {name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize provider {name}: {e}")
    
    def get_provider(self, name: str) -> Any:
        """Get a provider instance by name.
        
        Args:
            name: Provider name
            
        Returns:
            Provider instance
        """
        if name not in self._provider_instances:
            if name in self._providers:
                # Try to initialize on-demand
                self._initialize_provider(name)
            else:
                raise TermuxHubError(f"Provider '{name}' not found")
        
        return self._provider_instances[name]
    
    def _initialize_provider(self, name: str):
        """Initialize a specific provider."""
        if name not in self._providers:
            raise TermuxHubError(f"Provider '{name}' not configured")
        
        config = self._providers[name]
        
        try:
            if config.provider_type == ProviderType.MISTRAL:
                self._provider_instances[name] = MistralAIBackend(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                )
            elif config.provider_type == ProviderType.DEEPSEEK:
                self._provider_instances[name] = DeepSeekBackend(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                )
            elif config.provider_type == ProviderType.AI_STUDIO:
                self._provider_instances[name] = AIStudioBackend(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                )
            elif config.provider_type == ProviderType.CHAPITO:
                self._provider_instances[name] = ChapitoBackend(
                    api_key=config.api_key,
                    base_url=config.base_url,
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                )
            elif config.provider_type == ProviderType.COLLAB:
                self._provider_instances[name] = ColabBackend(
                    timeout=config.timeout,
                    max_retries=config.max_retries,
                )
            
            logger.info(f"Initialized provider on-demand: {name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize provider {name} on-demand: {e}")
            raise TermuxHubError(f"Failed to initialize provider {name}: {e}")
    
    def list_providers(self) -> List[str]:
        """List available providers.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def list_sessions(self) -> List[str]:
        """List active sessions.
        
        Returns:
            List of session IDs
        """
        return list(self._sessions.keys())
    
    def create_session(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[List[str]] = None,
    ) -> str:
        """Create a new agent session.
        
        Args:
            provider: Provider to use (default: self.default_provider)
            model: Model to use
            system_prompt: System prompt for the session
            temperature: Temperature setting
            max_tokens: Maximum tokens
            tools: List of tools to enable
            
        Returns:
            Session ID
        """
        provider = provider or self.default_provider
        
        # Generate session ID
        session_id = f"session_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
        
        # Create session config
        session_config = SessionConfig(
            session_id=session_id,
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools or [],
        )
        
        self._sessions[session_id] = session_config
        
        # Initialize provider session
        try:
            provider_instance = self.get_provider(provider)
            self._active_sessions[session_id] = provider_instance.create_session(
                model=model,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.error(f"Failed to create provider session: {e}")
            del self._sessions[session_id]
            raise TermuxHubError(f"Failed to create session: {e}")
        
        logger.info(f"Created session {session_id} with provider {provider}")
        
        return session_id
    
    def get_session(self, session_id: str) -> SessionConfig:
        """Get session configuration.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session configuration
        """
        if session_id not in self._sessions:
            raise TermuxHubError(f"Session '{session_id}' not found")
        
        return self._sessions[session_id]
    
    def destroy_session(self, session_id: str):
        """Destroy a session.
        
        Args:
            session_id: Session ID
        """
        if session_id not in self._sessions:
            raise TermuxHubError(f"Session '{session_id}' not found")
        
        # Clean up provider session
        if session_id in self._active_sessions:
            try:
                provider_instance = self.get_provider(self._sessions[session_id].provider)
                provider_instance.destroy_session(self._active_sessions[session_id])
            except Exception as e:
                logger.error(f"Failed to clean up provider session: {e}")
        
        del self._sessions[session_id]
        if session_id in self._active_sessions:
            del self._active_sessions[session_id]
        
        logger.info(f"Destroyed session {session_id}")
    
    def send_message(
        self,
        session_id: str,
        message: str,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, Generator[str, None, None]]:
        """Send a message to a session.
        
        Args:
            session_id: Session ID
            message: Message to send
            stream: Whether to stream the response
            **kwargs: Additional arguments for the provider
            
        Returns:
            Response (string or generator for streaming)
        """
        if session_id not in self._sessions:
            raise TermuxHubError(f"Session '{session_id}' not found")
        
        session_config = self._sessions[session_id]
        provider_name = session_config.provider
        
        provider_instance = self.get_provider(provider_name)
        provider_session = self._active_sessions.get(session_id)
        
        try:
            if stream:
                return provider_instance.send_message_stream(
                    provider_session,
                    message,
                    **kwargs,
                )
            else:
                response = provider_instance.send_message(
                    provider_session,
                    message,
                    **kwargs,
                )
                
                # Update last used time
                session_config.last_used = time.time()
                
                return response
                
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise TermuxHubError(f"Failed to send message: {e}")
    
    def route_request(
        self,
        provider: Optional[str] = None,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        action: str = "chat",
        **kwargs,
    ) -> Any:
        """Route a request to the appropriate provider.
        
        Args:
            provider: Provider to use (default: self.default_provider)
            message: Message content
            session_id: Session ID (for existing sessions)
            action: Action type (chat, complete, embed, etc.)
            **kwargs: Additional arguments
            
        Returns:
            Response from the provider
        """
        provider = provider or self.default_provider
        
        if provider not in self._providers:
            raise TermuxHubError(f"Provider '{provider}' not found")
        
        provider_instance = self.get_provider(provider)
        
        try:
            if action == "chat":
                if session_id:
                    return self.send_message(session_id, message or "", **kwargs)
                else:
                    # Create a new session for one-off request
                    new_session_id = self.create_session(provider=provider)
                    response = self.send_message(new_session_id, message or "", **kwargs)
                    self.destroy_session(new_session_id)
                    return response
            
            elif action == "complete":
                return provider_instance.complete(message or "", **kwargs)
            
            elif action == "embed":
                return provider_instance.embed(message or "", **kwargs)
            
            elif action == "list_models":
                return provider_instance.list_models()
            
            elif action == "get_model":
                return provider_instance.get_model(kwargs.get("model_id"))
            
            else:
                raise TermuxHubError(f"Unknown action: {action}")
                
        except Exception as e:
            logger.error(f"Failed to route request: {e}")
            raise TermuxHubError(f"Failed to route request: {e}")
    
    def set_transport(self, transport: Union[StdioTransport, CurlCffiTransport]):
        """Set the transport layer.
        
        Args:
            transport: Transport instance to use
        """
        self._transport = transport
        logger.info(f"Transport set to {type(transport).__name__}")
    
    def get_transport(self) -> Optional[Union[StdioTransport, CurlCffiTransport]]:
        """Get the current transport layer.
        
        Returns:
            Current transport instance or None
        """
        return self._transport
    
    def create_stdio_transport(
        self,
        command: Union[str, List[str]],
        **kwargs,
    ) -> StdioTransport:
        """Create a stdio transport.
        
        Args:
            command: Command to execute
            **kwargs: Additional arguments for StdioTransport
            
        Returns:
            StdioTransport instance
        """
        transport = StdioTransport(command, **kwargs)
        self.set_transport(transport)
        return transport
    
    def create_curl_cffi_transport(
        self,
        base_url: Optional[str] = None,
        **kwargs,
    ) -> CurlCffiTransport:
        """Create a curl_cffi transport.
        
        Args:
            base_url: Base URL for requests
            **kwargs: Additional arguments for CurlCffiTransport
            
        Returns:
            CurlCffiTransport instance
        """
        transport = CurlCffiTransport(base_url=base_url, **kwargs)
        self.set_transport(transport)
        return transport
    
    def add_provider(self, config: ProviderConfig):
        """Add a new provider configuration.
        
        Args:
            config: Provider configuration
        """
        self._providers[config.name] = config
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Added provider: {config.name}")
    
    def remove_provider(self, name: str):
        """Remove a provider.
        
        Args:
            name: Provider name
        """
        if name not in self._providers:
            raise TermuxHubError(f"Provider '{name}' not found")
        
        # Clean up provider instance
        if name in self._provider_instances:
            try:
                self._provider_instances[name].close()
            except Exception:
                pass
            del self._provider_instances[name]
        
        del self._providers[name]
        
        # Save configuration
        self._save_config()
        
        logger.info(f"Removed provider: {name}")
    
    def _save_config(self):
        """Save configuration to file."""
        config_file = self.config_dir / "config.json"
        
        config = {
            "default_provider": self.default_provider,
            "providers": {},
        }
        
        for name, provider_config in self._providers.items():
            config["providers"][name] = {
                "type": provider_config.provider_type.value,
                "api_key": provider_config.api_key,
                "base_url": provider_config.base_url,
                "timeout": provider_config.timeout,
                "max_retries": provider_config.max_retries,
                "proxy": provider_config.proxy,
                "impersonate": provider_config.impersonate,
                "custom_command": provider_config.custom_command,
                "enabled": provider_config.enabled,
                "priority": provider_config.priority,
                "metadata": provider_config.metadata,
            }
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Saved configuration to {config_file}")
    
    def close(self):
        """Close the hub and cleanup resources."""
        # Close all sessions
        for session_id in list(self._sessions.keys()):
            try:
                self.destroy_session(session_id)
            except Exception as e:
                logger.error(f"Failed to close session {session_id}: {e}")
        
        # Close all provider instances
        for name, instance in self._provider_instances.items():
            try:
                instance.close()
            except Exception as e:
                logger.error(f"Failed to close provider {name}: {e}")
        
        self._provider_instances.clear()
        
        # Close transport
        if self._transport:
            try:
                self._transport.close()
            except Exception as e:
                logger.error(f"Failed to close transport: {e}")
            self._transport = None
        
        logger.info("Termux Hub closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "TermuxHub",
    "TermuxHubError",
    "ProviderType",
    "ProviderConfig",
    "SessionConfig",
]
