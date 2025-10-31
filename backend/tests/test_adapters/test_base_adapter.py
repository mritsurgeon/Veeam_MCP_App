"""Tests for base adapter interface."""

import pytest

from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import LLMConfig, Message, MessageRole


class MockAdapter(BaseLLMAdapter):
    """Mock adapter for testing base interface."""

    def _validate_config(self) -> None:
        if not self.config.model:
            raise ValueError("Model is required")

    async def chat(self, messages, stream=False, **kwargs):
        return {"content": "Mock response", "model": self.config.model}

    async def health_check(self) -> bool:
        return True

    def get_capabilities(self):
        from app.core.schemas import AdapterCapabilities

        return AdapterCapabilities(provider="mock", supports_streaming=True)


def test_base_adapter_initialization():
    """Test base adapter can be initialized."""
    config = LLMConfig(provider="test", model="test-model", base_url="http://test")
    adapter = MockAdapter(config)
    assert adapter.config.model == "test-model"


def test_base_adapter_validation():
    """Test base adapter validates config."""
    config = LLMConfig(provider="test", model="", base_url="http://test")
    with pytest.raises(ValueError, match="Model is required"):
        MockAdapter(config)


@pytest.mark.asyncio
async def test_base_adapter_normalize_messages():
    """Test message normalization."""
    config = LLMConfig(provider="test", model="test-model", base_url="http://test")
    adapter = MockAdapter(config)

    messages = [
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi there"),
    ]

    normalized = adapter.normalize_messages(messages)
    assert len(normalized) == 2
    assert normalized[0].content == "Hello"


@pytest.mark.asyncio
async def test_base_adapter_health_check():
    """Test health check method."""
    config = LLMConfig(provider="test", model="test-model", base_url="http://test")
    adapter = MockAdapter(config)

    is_healthy = await adapter.health_check()
    assert is_healthy is True


@pytest.mark.asyncio
async def test_base_adapter_close():
    """Test adapter cleanup."""
    config = LLMConfig(provider="test", model="test-model", base_url="http://test")
    adapter = MockAdapter(config)

    # Should not raise
    await adapter.close()

