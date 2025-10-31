"""OpenAI API adapter implementation."""

import os
from typing import AsyncIterator, List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionChunk, ChatCompletionMessageParam

from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import (
    AdapterCapabilities,
    LLMConfig,
    LLMResponse,
    Message,
    MessageRole,
    StreamChunk,
)


class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI API (GPT-4, GPT-3.5, etc.)."""

    def __init__(self, config: LLMConfig):
        """Initialize OpenAI adapter."""
        super().__init__(config)
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=config.base_url or "https://api.openai.com/v1",
            timeout=config.timeout,
        )

    def _validate_config(self) -> None:
        """Validate OpenAI-specific configuration."""
        if not self.config.model:
            raise ValueError("OpenAI model name is required")
        # OpenAI models typically start with gpt-
        if not self.config.model.startswith(("gpt-", "o1-")):
            # Allow custom models for OpenAI-compatible APIs
            pass

    def normalize_messages(self, messages: List[Message]) -> List[ChatCompletionMessageParam]:
        """Convert unified messages to OpenAI format."""
        openai_messages = []
        for msg in messages:
            message_dict: ChatCompletionMessageParam = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            openai_messages.append(message_dict)
        return openai_messages

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse | AsyncIterator[StreamChunk]:
        """Send chat completion request to OpenAI."""
        normalized_messages = self.normalize_messages(messages)

        extra_params = self.config.extra_params or {}
        params = {
            "model": self.config.model,
            "messages": normalized_messages,
            "temperature": self.config.temperature,
            **kwargs,
            **extra_params,
        }
        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        if stream:
            return self._stream_response(params)
        else:
            response = await self.client.chat.completions.create(**params)
            return self._parse_response(response)

    async def _stream_response(
        self, params: dict
    ) -> AsyncIterator[StreamChunk]:
        """Stream OpenAI responses."""
        params["stream"] = True
        stream = await self.client.chat.completions.create(**params)

        async for chunk in stream:
            if isinstance(chunk, ChatCompletionChunk):
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta:
                    content = delta.content or ""
                    tool_calls = delta.tool_calls
                    finished = chunk.choices[0].finish_reason is not None

                    yield StreamChunk(
                        content=content,
                        finished=finished,
                        tool_calls=[
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls or []
                        ]
                        if tool_calls
                        else None,
                        metadata={"model": chunk.model, "id": chunk.id},
                    )

    def _parse_response(self, response) -> LLMResponse:
        """Parse OpenAI response to unified format."""
        choice = response.choices[0]
        message = choice.message

        tool_calls = None
        if message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ]

        return LLMResponse(
            content=message.content or "",
            model=response.model,
            finish_reason=choice.finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
            if response.usage
            else None,
            tool_calls=tool_calls,
        )

    async def health_check(self) -> bool:
        """Check OpenAI API connectivity."""
        try:
            # Simple health check - list models
            await self.client.models.list()
            return True
        except Exception:
            return False

    def get_capabilities(self) -> AdapterCapabilities:
        """Get OpenAI adapter capabilities."""
        return AdapterCapabilities(
            provider="openai",
            supports_streaming=True,
            supports_tools=True,
            supports_function_calling=True,
            max_context_length=128000,  # GPT-4 Turbo context length
            supported_models=[
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-4-32k",
                "gpt-3.5-turbo",
                "o1-preview",
                "o1-mini",
            ],
        )

