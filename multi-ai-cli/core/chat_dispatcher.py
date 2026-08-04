#!/usr/bin/env python3
"""Chat Dispatcher with Codex harvesting for all providers."""
from typing import List, Dict, Optional, Any
from rich.console import Console

console = Console()


class ChatDispatcher:
    """Dispatches chat messages to providers with automatic code harvesting.
    
    This dispatcher:
    1. Routes messages to the appropriate provider
    2. Automatically harvests code blocks from responses
    3. Indexes harvested code in the provider's Codex
    4. Returns both the response and harvested code blocks
    """
    
    def __init__(self, session_manager=None):
        """Initialize the dispatcher."""
        self.session_manager = session_manager
        self.providers: Dict[str, Any] = {}
        self.codex_enabled = True
    
    def get_provider(self, name: str, **kwargs):
        """Get or create a provider instance."""
        if name not in self.providers:
            from providers import get_provider
            self.providers[name] = get_provider(name, **kwargs)
        return self.providers[name]
    
    def send(self, provider_name: str, message: str, session_id: str = None, harvest: bool = True, **kwargs) -> Dict:
        """Send a message and optionally harvest code blocks.
        
        Args:
            provider_name: Name of the provider
            message: Message to send
            session_id: Optional session ID
            harvest: Whether to harvest code blocks from response
            **kwargs: Additional arguments for the provider
            
        Returns:
            Dictionary with:
            - 'response': The provider's response
            - 'code_blocks': List of harvested code blocks (if harvest=True)
            - 'session_id': The session ID used
        """
        provider = self.get_provider(provider_name)
        
        # Send the message
        if session_id:
            response = provider.send_message(message, session_id=session_id, **kwargs)
        else:
            response = provider.send_message(message, **kwargs)
        
        result = {
            'response': response,
            'provider': provider_name,
            'session_id': session_id or (provider.core.session_id if hasattr(provider, 'core') else None),
        }
        
        # Harvest code blocks if enabled
        if harvest and response and self.codex_enabled:
            # Extract code blocks from the response
            code_blocks = provider.codex.extract_from_messages(
                [{"role": "assistant", "content": response}],
                session_id or "temp",
                "response",
                provider_name
            )
            
            # Index the response
            provider.codex.index_conversation(
                session_id or "temp",
                "response",
                [{"role": "assistant", "content": response}],
                provider_name
            )
            
            result['code_blocks'] = [block.to_dict() for block in code_blocks]
        
        return result
    
    def send_with_history(self, provider_name: str, message: str, session_id: str = None, **kwargs) -> Dict:
        """Send a message with full session history and code harvesting.
        
        Args:
            provider_name: Name of the provider
            message: Message to send
            session_id: Optional session ID
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with response and harvested code
        """
        provider = self.get_provider(provider_name)
        
        # Get session history
        if session_id:
            messages = provider.get_history(session_id)
        else:
            messages = []
        
        # Send the message
        response = provider.send_message(message, session_id=session_id, **kwargs)
        
        # Add response to messages
        messages.append({"role": "user", "content": message})
        messages.append({"role": "assistant", "content": response})
        
        # Harvest and index all messages
        if self.codex_enabled:
            provider.codex.index_conversation(
                session_id or "temp",
                f"Session {session_id[:8] if session_id else 'new'}",
                messages,
                provider_name
            )
        
        return {
            'response': response,
            'provider': provider_name,
            'session_id': session_id,
            'messages': messages,
        }
    
    def harvest_session(self, provider_name: str, session_id: str, title: str = None) -> List[Dict]:
        """Harvest all code blocks from a session.
        
        Args:
            provider_name: Name of the provider
            session_id: Session ID to harvest
            title: Optional session title
            
        Returns:
            List of harvested code blocks
        """
        provider = self.get_provider(provider_name)
        
        # Get session messages
        messages = provider.get_history(session_id)
        
        # Harvest code blocks
        code_blocks = provider.harvest_code(session_id, messages, title)
        
        return [block.to_dict() for block in code_blocks]
    
    def search_code(self, provider_name: str, query: str, language: str = None) -> List[Dict]:
        """Search harvested code blocks for a provider.
        
        Args:
            provider_name: Name of the provider
            query: Search query
            language: Optional language filter
            
        Returns:
            List of search results
        """
        provider = self.get_provider(provider_name)
        return provider.search_code(query, language)
    
    def get_code_by_hash(self, provider_name: str, content_hash: str) -> Optional[str]:
        """Get code by hash from a provider's codex.
        
        Args:
            provider_name: Name of the provider
            content_hash: Content hash
            
        Returns:
            Code content or None
        """
        provider = self.get_provider(provider_name)
        return provider.get_code_by_hash(content_hash)
    
    def get_all_providers(self) -> List[str]:
        """Get list of all available providers."""
        from providers import get_provider_types
        return get_provider_types()
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get all providers with their availability status."""
        from providers import get_available_providers
        return get_available_providers()


# Legacy compatibility
class LegacyChatDispatcher:
    """Legacy dispatcher for backward compatibility."""
    
    def __init__(self, session_manager=None):
        self.dispatcher = ChatDispatcher(session_manager)
    
    def send(self, provider, message, session_id=None):
        """Send message (legacy interface)."""
        result = self.dispatcher.send(provider, message, session_id, harvest=False)
        return result.get('response', '')


# Export both for compatibility
if __name__ == "__main__":
    # Test the dispatcher
    dispatcher = ChatDispatcher()
    
    # Test with Mistral
    print("Testing Mistral provider...")
    try:
        result = dispatcher.send("mistral", "Hello, Mistral!", harvest=True)
        print(f"Response: {result['response'][:100]}")
        print(f"Code blocks: {len(result.get('code_blocks', []))}")
    except Exception as e:
        print(f"Error: {e}")
    
    # List all providers
    print(f"\nAll providers: {dispatcher.get_all_providers()}")
    print(f"Available providers: {dispatcher.get_available_providers()}")
