"""Base adapter interface for all LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional

from app.core.schemas import (
    AdapterCapabilities,
    LLMConfig,
    LLMResponse,
    Message,
    StreamChunk,
)


class BaseLLMAdapter(ABC):
    """Abstract base class for all LLM adapters.

    All LLM provider adapters must implement this interface to ensure
    consistent behavior across different providers.
    """

    def __init__(self, config: LLMConfig):
        """Initialize the adapter with configuration.

        Args:
            config: LLM configuration containing API keys, model, etc.
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate adapter-specific configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse | AsyncIterator[StreamChunk]:
        """Send a chat completion request.

        Args:
            messages: List of messages in the conversation.
            stream: Whether to stream the response.
            **kwargs: Additional provider-specific parameters.

        Returns:
            Either a complete LLMResponse or an async iterator of StreamChunk
            objects if streaming is enabled.

        Raises:
            Exception: If the API request fails.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the adapter can connect to the provider API.

        Returns:
            True if the adapter is healthy and can make requests.
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> AdapterCapabilities:
        """Get adapter capabilities.

        Returns:
            AdapterCapabilities object describing supported features.
        """
        pass

    def normalize_messages(self, messages: List[Message]) -> List[Message]:
        """Normalize messages to ensure consistent format.

        Override this method if provider-specific normalization is needed.

        Args:
            messages: List of messages to normalize.

        Returns:
            Normalized list of messages.
        """
        return messages

    async def close(self) -> None:
        """Clean up resources (close connections, etc.).

        Override if adapter needs cleanup.
        """
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Note: __exit__ in async context managers should be async
        # For now, we'll handle cleanup in close() method
        pass

