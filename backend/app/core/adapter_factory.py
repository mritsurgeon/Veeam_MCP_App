"""Factory for creating LLM adapters."""

from typing import Dict, Optional

from app.adapters import AnthropicAdapter, GeminiAdapter, OllamaAdapter, OpenAIAdapter
from app.core.config import get_llm_config
from app.core.schemas import LLMConfig


class AdapterFactory:
    """Factory for creating LLM adapters based on provider name."""

    _adapters = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
        "ollama": OllamaAdapter,
        "gemini": GeminiAdapter,
    }

    @classmethod
    def create(
        cls,
        provider: str,
        config: Optional[Dict] = None,
        model: Optional[str] = None,
    ) -> OpenAIAdapter | AnthropicAdapter | OllamaAdapter | GeminiAdapter:
        """Create an LLM adapter instance.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic', 'ollama').
            config: Optional provider config dict. If None, loads from file.
            model: Optional model name override.

        Returns:
            Initialized adapter instance.

        Raises:
            ValueError: If provider is not supported.
        """
        if provider not in cls._adapters:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported: {list(cls._adapters.keys())}"
            )

        # Load config
        if config is None:
            config = get_llm_config(provider)

        # Override model if provided
        if model:
            config["model"] = model

        # Create LLMConfig
        llm_config = LLMConfig(
            provider=provider,
            **config,
        )

        # Instantiate adapter
        adapter_class = cls._adapters[provider]
        return adapter_class(llm_config)

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported providers.

        Returns:
            List of provider names.
        """
        return list(cls._adapters.keys())

    @classmethod
    def register_adapter(cls, name: str, adapter_class):
        """Register a new adapter class.

        Args:
            name: Provider name.
            adapter_class: Adapter class that inherits from BaseLLMAdapter.
        """
        cls._adapters[name] = adapter_class

