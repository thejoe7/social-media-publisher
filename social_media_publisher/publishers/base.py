from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..models import PostContent

class BasePublisher(ABC):
    """Abstract Base Class for social media platform publishers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the publisher with an optional global configuration.
        """
        self.config = config or {}

    @abstractmethod
    def login(self, auth_config: Dict[str, Any]) -> bool:
        """
        Log in to the platform using the provided authentication config.
        auth_config usually contains keys like 'cookie_file' or 'profile_path'.
        """
        pass

    @abstractmethod
    def publish(self, content: PostContent) -> bool:
        """
        Publish the content to the platform.
        """
        pass

    def cleanup(self) -> None:
        """
        Clean up resources (close browser, etc.).
        """
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
