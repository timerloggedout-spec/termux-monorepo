from abc import ABC, abstractmethod

class ChatBackend(ABC):
    @abstractmethod
    def send_message(self, message: str, context: list[dict]) -> str:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...
