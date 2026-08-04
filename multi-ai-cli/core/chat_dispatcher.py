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
        """
        Initialize the chat dispatcher.
        
        Parameters:
            session_manager: Optional manager used for session-related operations.
        """
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
        """
        Send a message through the selected provider and optionally harvest code blocks from the response.
        
        Args:
            provider_name: Name of the provider to use.
            message: Message to send.
            session_id: Optional session identifier.
            harvest: Whether to extract and index code blocks from the response.
            **kwargs: Additional arguments passed to the provider.
        
        Returns:
            Dictionary containing the response, provider name, session ID, and, when harvesting is enabled, serialized code blocks.
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
            'session_id': session_id or provider.core.session_id if hasattr(provider, 'core') else None,
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
        """
        Send a message using the session's existing conversation history.
        
        Parameters:
            provider_name (str): Name of the provider to use.
            message (str): Message to send.
            session_id (str, optional): Identifier of the session whose history should be included.
        
        Returns:
            Dict: Response metadata containing the response text, provider name, session ID, and conversation messages.
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
        """
        Retrieve harvested code associated with a content hash from a provider.
        
        Parameters:
            provider_name (str): Name of the provider whose code index to search.
            content_hash (str): Hash identifying the code content.
        
        Returns:
            str | None: The matching code content, or None if no match exists.
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
        """
        Initialize a legacy dispatcher backed by a ChatDispatcher.
        
        Parameters:
        	session_manager: Optional session manager used for session-aware operations.
        """
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
