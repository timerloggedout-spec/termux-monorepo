from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from archwiz.codex import CodexIndex

@dataclass
class ProviderConfig:
    name: str
    model: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

class BaseProvider(ABC):
    """Base interface for all AI providers in the ArchWiz ecosystem."""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.codex = CodexIndex(provider=config.name)

    @abstractmethod
    def send_message(self, message: str, session_id: Optional[str] = None) -> str:
        """Send a message and return the response text."""
        pass

    @abstractmethod
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch session history."""
        pass

    @abstractmethod
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List available sessions."""
        pass

    def harvest_code(self, session_id: str):
        """Harvest code blocks from a session into Codex."""
        history = self.get_history(session_id)
        return self.codex.harvest(session_id, history)
