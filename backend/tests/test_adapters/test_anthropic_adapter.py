"""Tests for Anthropic adapter."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.adapters.anthropic_adapter import AnthropicAdapter
from app.core.schemas import LLMConfig, Message, MessageRole


@pytest.fixture
def anthropic_config():
    """Create Anthropic config fixture."""
    return LLMConfig(
        provider="anthropic",
        api_key="test-key",
        model="claude-3-opus-20240229",
        base_url="https://api.anthropic.com",
    )


def test_anthropic_adapter_init(anthropic_config):
    """Test Anthropic adapter initialization."""
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic"):
        adapter = AnthropicAdapter(anthropic_config)
        assert adapter.config.model == "claude-3-opus-20240229"


def test_anthropic_adapter_init_missing_key():
    """Test Anthropic adapter requires API key."""
    config = LLMConfig(
        provider="anthropic",
        model="claude-3-opus-20240229",
        base_url="https://api.anthropic.com",
    )
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API key"):
            AnthropicAdapter(config)


def test_anthropic_validate_config_invalid_model():
    """Test Anthropic adapter validates model name."""
    config = LLMConfig(
        provider="anthropic",
        api_key="test-key",
        model="invalid-model",
        base_url="https://api.anthropic.com",
    )
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic"):
        adapter = AnthropicAdapter(config)
        with pytest.raises(ValueError, match="Invalid Anthropic model"):
            adapter._validate_config()


def test_anthropic_normalize_messages(anthropic_config):
    """Test message normalization for Anthropic."""
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic"):
        adapter = AnthropicAdapter(anthropic_config)

        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a helpful assistant"),
            Message(role=MessageRole.USER, content="Hello"),
        ]

        normalized, system = adapter.normalize_messages(messages)
        assert len(normalized) == 1
        assert system == "You are a helpful assistant"
        assert normalized[0]["role"] == "user"


@pytest.mark.asyncio
async def test_anthropic_chat_completion(anthropic_config):
    """Test Anthropic chat completion."""
    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(text="Test response", type="text")
    ]
    mock_response.model = "claude-3-opus-20240229"
    mock_response.stop_reason = "end_turn"
    mock_response.usage = MagicMock(input_tokens=10, output_tokens=5)

    with patch("app.adapters.anthropic_adapter.AsyncAnthropic") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.messages.create = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        adapter = AnthropicAdapter(anthropic_config)
        messages = [Message(role=MessageRole.USER, content="Hello")]

        response = await adapter.chat(messages, stream=False)

        assert response.content == "Test response"
        assert response.model == "claude-3-opus-20240229"


@pytest.mark.asyncio
async def test_anthropic_health_check(anthropic_config):
    """Test Anthropic health check."""
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.messages.create = AsyncMock()
        mock_client.return_value = mock_client_instance

        adapter = AnthropicAdapter(anthropic_config)
        is_healthy = await adapter.health_check()

        assert is_healthy is True


def test_anthropic_capabilities(anthropic_config):
    """Test Anthropic capabilities."""
    with patch("app.adapters.anthropic_adapter.AsyncAnthropic"):
        adapter = AnthropicAdapter(anthropic_config)
        capabilities = adapter.get_capabilities()

        assert capabilities.provider == "anthropic"
        assert capabilities.supports_streaming is True
        assert capabilities.supports_tools is True
        assert "claude-3-opus-20240229" in capabilities.supported_models

