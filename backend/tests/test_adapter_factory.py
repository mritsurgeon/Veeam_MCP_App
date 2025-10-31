"""Tests for adapter factory."""

from unittest.mock import patch

import pytest

from app.adapters import AnthropicAdapter, OllamaAdapter, OpenAIAdapter
from app.core.adapter_factory import AdapterFactory


def test_adapter_factory_get_supported_providers():
    """Test factory returns supported providers."""
    providers = AdapterFactory.get_supported_providers()
    assert "openai" in providers
    assert "anthropic" in providers
    assert "ollama" in providers


def test_adapter_factory_create_openai():
    """Test factory creates OpenAI adapter."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI"):
        config = {
            "api_key": "test-key",
            "model": "gpt-4",
            "base_url": "https://api.openai.com/v1",
        }
        adapter = AdapterFactory.create("openai", config=config)
        assert isinstance(adapter, OpenAIAdapter)


def test_adapter_factory_create_anthropic():
    """Test factory creates Anthropic adapter."""
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic"):
        config = {
            "api_key": "test-key",
            "model": "claude-3-opus-20240229",
            "base_url": "https://api.anthropic.com",
        }
        adapter = AdapterFactory.create("anthropic", config=config)
        assert isinstance(adapter, AnthropicAdapter)


def test_adapter_factory_create_ollama():
    """Test factory creates Ollama adapter."""
    config = {
        "model": "llama2",
        "base_url": "http://localhost:11434",
    }
    adapter = AdapterFactory.create("ollama", config=config)
    assert isinstance(adapter, OllamaAdapter)


def test_adapter_factory_unsupported_provider():
    """Test factory raises error for unsupported provider."""
    with pytest.raises(ValueError, match="Unsupported provider"):
        AdapterFactory.create("unsupported")


@pytest.mark.asyncio
async def test_adapter_factory_register():
    """Test factory can register new adapters."""
    from app.core.base_adapter import BaseLLMAdapter
    from app.core.schemas import LLMConfig

    class CustomAdapter(BaseLLMAdapter):
        def _validate_config(self):
            pass

        async def chat(self, messages, stream=False, **kwargs):
            return {"content": "custom"}

        async def health_check(self):
            return True

        def get_capabilities(self):
            from app.core.schemas import AdapterCapabilities
            return AdapterCapabilities(provider="custom")

    AdapterFactory.register_adapter("custom", CustomAdapter)
    assert "custom" in AdapterFactory.get_supported_providers()

