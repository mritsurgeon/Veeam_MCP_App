"""Tests for OpenAI adapter."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.adapters.openai_adapter import OpenAIAdapter
from app.core.schemas import LLMConfig, Message, MessageRole


@pytest.fixture
def openai_config():
    """Create OpenAI config fixture."""
    return LLMConfig(
        provider="openai",
        api_key="test-key",
        model="gpt-4",
        base_url="https://api.openai.com/v1",
    )


@pytest.fixture
def mock_openai_client():
    """Create mock OpenAI client."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI") as mock:
        yield mock


def test_openai_adapter_init(openai_config):
    """Test OpenAI adapter initialization."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI"):
        adapter = OpenAIAdapter(openai_config)
        assert adapter.config.model == "gpt-4"


def test_openai_adapter_init_missing_key():
    """Test OpenAI adapter requires API key."""
    config = LLMConfig(
        provider="openai",
        model="gpt-4",
        base_url="https://api.openai.com/v1",
    )
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API key"):
            OpenAIAdapter(config)


def test_openai_adapter_validate_config(openai_config):
    """Test OpenAI adapter config validation."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI"):
        # Should not raise
        adapter = OpenAIAdapter(openai_config)
        adapter._validate_config()


def test_openai_normalize_messages(openai_config):
    """Test message normalization for OpenAI."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI"):
        adapter = OpenAIAdapter(openai_config)

        messages = [
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi"),
        ]

        normalized = adapter.normalize_messages(messages)
        assert len(normalized) == 2
        assert normalized[0]["role"] == "user"
        assert normalized[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_openai_chat_completion(openai_config):
    """Test OpenAI chat completion."""
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="Test response", tool_calls=None),
            finish_reason="stop",
        )
    ]
    mock_response.model = "gpt-4"
    mock_response.usage = MagicMock(
        prompt_tokens=10, completion_tokens=5, total_tokens=15
    )

    with patch("app.adapters.openai_adapter.AsyncOpenAI") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.chat.completions.create = AsyncMock(
            return_value=mock_response
        )
        mock_client.return_value = mock_client_instance

        adapter = OpenAIAdapter(openai_config)
        messages = [Message(role=MessageRole.USER, content="Hello")]

        response = await adapter.chat(messages, stream=False)

        assert response.content == "Test response"
        assert response.model == "gpt-4"
        assert response.usage["total_tokens"] == 15


@pytest.mark.asyncio
async def test_openai_health_check(openai_config):
    """Test OpenAI health check."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI") as mock_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.models.list = AsyncMock()
        mock_client.return_value = mock_client_instance

        adapter = OpenAIAdapter(openai_config)
        is_healthy = await adapter.health_check()

        assert is_healthy is True


def test_openai_capabilities(openai_config):
    """Test OpenAI capabilities."""
    with patch("app.adapters.openai_adapter.AsyncOpenAI"):
        adapter = OpenAIAdapter(openai_config)
        capabilities = adapter.get_capabilities()

        assert capabilities.provider == "openai"
        assert capabilities.supports_streaming is True
        assert capabilities.supports_tools is True
        assert "gpt-4" in capabilities.supported_models

