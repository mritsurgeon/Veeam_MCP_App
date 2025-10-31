"""Ollama (Local Llama) API adapter implementation."""

import json
from typing import AsyncIterator, List, Optional

import httpx

from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import (
    AdapterCapabilities,
    LLMConfig,
    LLMResponse,
    Message,
    StreamChunk,
)


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama API (local Llama models)."""

    def __init__(self, config: LLMConfig):
        """Initialize Ollama adapter."""
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.timeout = config.timeout
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def _validate_config(self) -> None:
        """Validate Ollama-specific configuration."""
        if not self.config.model:
            raise ValueError("Ollama model name is required")

    def normalize_messages(self, messages: List[Message]) -> List[dict]:
        """Convert unified messages to Ollama format."""
        ollama_messages = []
        for msg in messages:
            ollama_messages.append(
                {
                    "role": msg.role.value,
                    "content": msg.content,
                }
            )
        return ollama_messages

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse | AsyncIterator[StreamChunk]:
        """Send chat completion request to Ollama."""
        normalized_messages = self.normalize_messages(messages)

        extra_params = self.config.extra_params or {}
        params = {
            "model": self.config.model,
            "messages": normalized_messages,
            "stream": stream,
            "options": {
                "temperature": self.config.temperature,
                **kwargs.get("options", {}),
                **extra_params,
            },
        }

        if self.config.max_tokens:
            params["options"]["num_predict"] = self.config.max_tokens

        response = await self.client.post("/api/chat", json=params)

        if response.status_code != 200:
            raise Exception(
                f"Ollama API error: {response.status_code} - {response.text}"
            )

        if stream:
            return self._stream_response(response)
        else:
            return self._parse_response(response.json())

    async def _stream_response(
        self, response: httpx.Response
    ) -> AsyncIterator[StreamChunk]:
        """Stream Ollama responses."""
        async for line in response.aiter_lines():
            if line:
                try:
                    chunk_data = json.loads(line)
                    content = chunk_data.get("message", {}).get("content", "")
                    done = chunk_data.get("done", False)

                    yield StreamChunk(
                        content=content,
                        finished=done,
                        metadata={
                            "model": chunk_data.get("model"),
                            "done_reason": chunk_data.get("done_reason"),
                        },
                    )
                except json.JSONDecodeError:
                    continue

    def _parse_response(self, data: dict) -> LLMResponse:
        """Parse Ollama response to unified format."""
        message = data.get("message", {})
        content = message.get("content", "")

        # Ollama doesn't provide detailed usage info in standard format
        usage = None
        if "eval_count" in data or "prompt_eval_count" in data:
            usage = {
                "prompt_tokens": data.get("prompt_eval_count", 0),
                "completion_tokens": data.get("eval_count", 0),
                "total_tokens": (
                    data.get("prompt_eval_count", 0)
                    + data.get("eval_count", 0)
                ),
            }

        return LLMResponse(
            content=content,
            model=data.get("model", self.config.model),
            finish_reason=data.get("done_reason"),
            usage=usage,
        )

    async def health_check(self) -> bool:
        """Check Ollama API connectivity."""
        try:
            response = await self.client.get("/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available Ollama models.

        Returns:
            List of available model names.
        """
        try:
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception:
            return []

    def get_capabilities(self) -> AdapterCapabilities:
        """Get Ollama adapter capabilities."""
        # Ollama capabilities vary by model, so we provide generic info
        return AdapterCapabilities(
            provider="ollama",
            supports_streaming=True,
            supports_tools=False,  # Ollama doesn't support function calling yet
            supports_function_calling=False,
            max_context_length=None,  # Varies by model
            supported_models=[],  # Dynamic - fetched via list_models()
        )

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.client.aclose()

