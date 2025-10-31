"""Google Gemini API adapter implementation."""

import os
from typing import AsyncIterator, List, Optional

import httpx

from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import (
    AdapterCapabilities,
    LLMConfig,
    LLMResponse,
    Message,
    MessageRole,
    StreamChunk,
)


class GeminiAdapter(BaseLLMAdapter):
    """Adapter for Google Gemini API."""

    def __init__(self, config: LLMConfig):
        """Initialize Gemini adapter."""
        super().__init__(config)
        api_key = config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        self.base_url = config.base_url or "https://generativelanguage.googleapis.com/v1"
        self.timeout = config.timeout
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
        )

    def _validate_config(self) -> None:
        """Validate Gemini-specific configuration."""
        if not self.config.model:
            raise ValueError("Gemini model name is required")
        # Gemini models typically start with gemini-
        if not self.config.model.startswith("gemini-"):
            raise ValueError(
                f"Invalid Gemini model: {self.config.model}. "
                "Expected model name starting with 'gemini-'"
            )

    def normalize_messages(self, messages: List[Message]) -> List[dict]:
        """Convert unified messages to Gemini format."""
        gemini_messages = []
        system_instruction = None

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            elif msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                gemini_messages.append(
                    {
                        "role": "user" if msg.role == MessageRole.USER else "model",
                        "parts": [{"text": msg.content}],
                    }
                )

        return gemini_messages, system_instruction

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse | AsyncIterator[StreamChunk]:
        """Send chat completion request to Gemini."""
        normalized_messages, system_instruction = self.normalize_messages(messages)

        extra_params = self.config.extra_params or {}
        
        # Build request payload
        payload = {
            "contents": normalized_messages,
        }

        if system_instruction:
            payload["system_instruction"] = {
                "parts": [{"text": system_instruction}]
            }

        # Add generation config
        generation_config = {
            "temperature": self.config.temperature,
            **kwargs.get("generation_config", {}),
            **extra_params,
        }
        if self.config.max_tokens:
            generation_config["maxOutputTokens"] = self.config.max_tokens
        
        payload["generationConfig"] = generation_config

        url = f"{self.base_url}/models/{self.config.model}:generateContent"
        if stream:
            url = url.replace("generateContent", "streamGenerateContent")

        params = {"key": self.api_key}

        if stream:
            return self._stream_response(url, params, payload)
        else:
            response = await self.client.post(url, params=params, json=payload)
            response.raise_for_status()
            return self._parse_response(response.json())

    async def _stream_response(
        self, url: str, params: dict, payload: dict
    ) -> AsyncIterator[StreamChunk]:
        """Stream Gemini responses."""
        async with self.client.stream("POST", url, params=params, json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    import json
                    try:
                        data = json.loads(line[6:])  # Remove "data: " prefix
                        if "candidates" in data and len(data["candidates"]) > 0:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                for part in candidate["content"]["parts"]:
                                    if "text" in part:
                                        yield StreamChunk(
                                            content=part["text"],
                                            finished=False,
                                            metadata={
                                                "finish_reason": candidate.get("finishReason"),
                                            },
                                        )
                    except json.JSONDecodeError:
                        continue

    def _parse_response(self, data: dict) -> LLMResponse:
        """Parse Gemini response to unified format."""
        if "candidates" not in data or len(data["candidates"]) == 0:
            raise ValueError("No candidates in Gemini response")

        candidate = data["candidates"][0]
        content_parts = candidate.get("content", {}).get("parts", [])
        
        # Extract text content
        text_content = ""
        for part in content_parts:
            if "text" in part:
                text_content += part["text"]

        # Extract usage information
        usage = None
        if "usageMetadata" in data:
            usage_data = data["usageMetadata"]
            usage = {
                "prompt_tokens": usage_data.get("promptTokenCount", 0),
                "completion_tokens": usage_data.get("candidatesTokenCount", 0),
                "total_tokens": usage_data.get("totalTokenCount", 0),
            }

        return LLMResponse(
            content=text_content,
            model=self.config.model,
            finish_reason=candidate.get("finishReason"),
            usage=usage,
        )

    async def health_check(self) -> bool:
        """Check Gemini API connectivity."""
        try:
            # Try to list models
            url = f"{self.base_url}/models"
            params = {"key": self.api_key}
            response = await self.client.get(url, params=params, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available Gemini models.

        Returns:
            List of available model names.
        """
        try:
            url = f"{self.base_url}/models"
            params = {"key": self.api_key}
            response = await self.client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    # Extract just the model identifier (e.g., "gemini-pro" from "models/gemini-pro")
                    if "/" in model_name:
                        model_name = model_name.split("/")[-1]
                    models.append(model_name)
                return models
            return []
        except Exception:
            return []

    def get_capabilities(self) -> AdapterCapabilities:
        """Get Gemini adapter capabilities."""
        return AdapterCapabilities(
            provider="gemini",
            supports_streaming=True,
            supports_tools=True,  # Gemini supports function calling
            supports_function_calling=True,
            max_context_length=1000000,  # Gemini Pro supports up to 1M tokens
            supported_models=[
                "gemini-pro",
                "gemini-pro-vision",
                "gemini-1.5-pro",
                "gemini-1.5-flash",
            ],
        )

    async def close(self) -> None:
        """Close HTTP client connection."""
        await self.client.aclose()

