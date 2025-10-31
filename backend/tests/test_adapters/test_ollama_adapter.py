"""Tests for Ollama adapter."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from app.adapters.ollama_adapter import OllamaAdapter
from app.core.schemas import LLMConfig, Message, MessageRole


@pytest.fixture
def ollama_config():
    """Create Ollama config fixture."""
    return LLMConfig(
        provider="ollama",
        model="llama2",
        base_url="http://localhost:11434",
    )


def test_ollama_adapter_init(ollama_config):
    """Test Ollama adapter initialization."""
    adapter = OllamaAdapter(ollama_config)
    assert adapter.config.model == "llama2"
    assert adapter.base_url == "http://localhost:11434"


def test_ollama_validate_config_missing_model():
    """Test Ollama adapter requires model."""
    config = LLMConfig(
        provider="ollama",
        model="",
        base_url="http://localhost:11434",
    )
    with pytest.raises(ValueError, match="model name is required"):
        OllamaAdapter(config)


def test_ollama_normalize_messages(ollama_config):
    """Test message normalization for Ollama."""
    adapter = OllamaAdapter(ollama_config)

    messages = [
        Message(role=MessageRole.USER, content="Hello"),
        Message(role=MessageRole.ASSISTANT, content="Hi"),
    ]

    normalized = adapter.normalize_messages(messages)
    assert len(normalized) == 2
    assert normalized[0]["role"] == "user"
    assert normalized[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_ollama_chat_completion(ollama_config):
    """Test Ollama chat completion."""
    mock_response_data = {
        "model": "llama2",
        "message": {"content": "Test response", "role": "assistant"},
        "done": True,
        "done_reason": "stop",
        "prompt_eval_count": 10,
        "eval_count": 5,
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        adapter = OllamaAdapter(ollama_config)
        messages = [Message(role=MessageRole.USER, content="Hello")]

        response = await adapter.chat(messages, stream=False)

        assert response.content == "Test response"
        assert response.model == "llama2"
        assert response.usage["total_tokens"] == 15


@pytest.mark.asyncio
async def test_ollama_health_check(ollama_config):
    """Test Ollama health check."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        adapter = OllamaAdapter(ollama_config)
        is_healthy = await adapter.health_check()

        assert is_healthy is True


@pytest.mark.asyncio
async def test_ollama_list_models(ollama_config):
    """Test Ollama list models."""
    mock_response_data = {
        "models": [
            {"name": "llama2"},
            {"name": "mistral"},
        ]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data

        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value = mock_client_instance

        adapter = OllamaAdapter(ollama_config)
        models = await adapter.list_models()

        assert "llama2" in models
        assert "mistral" in models


def test_ollama_capabilities(ollama_config):
    """Test Ollama capabilities."""
    adapter = OllamaAdapter(ollama_config)
    capabilities = adapter.get_capabilities()

    assert capabilities.provider == "ollama"
    assert capabilities.supports_streaming is True
    assert capabilities.supports_tools is False

