from abc import ABC, abstractmethod
from typing import Any, Dict

class BasePublisher(ABC):
    """Abstract Base Class for social media platform publishers."""

    @abstractmethod
    def login(self, auth_config: Dict[str, Any]) -> bool:
        """Log in to the platform using the provided authentication config."""
        pass

    @abstractmethod
    def publish(self, content: Dict[str, Any]) -> bool:
        """Publish the content to the platform."""
        pass
