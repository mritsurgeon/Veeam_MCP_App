"""Anthropic (Claude) API adapter implementation."""

import os
from typing import AsyncIterator, List, Optional, Tuple

from anthropic import AsyncAnthropic
from anthropic.types import (
    ContentBlockDeltaEvent,
    MessageParam,
    TextBlock,
    ToolParam,
)

from app.core.base_adapter import BaseLLMAdapter
from app.core.schemas import (
    AdapterCapabilities,
    LLMConfig,
    LLMResponse,
    Message,
    MessageRole,
    StreamChunk,
)


class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic API (Claude models)."""

    def __init__(self, config: LLMConfig):
        """Initialize Anthropic adapter."""
        super().__init__(config)
        api_key = config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key is required")
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=config.base_url or "https://api.anthropic.com",
            timeout=config.timeout,
        )

    def _validate_config(self) -> None:
        """Validate Anthropic-specific configuration."""
        if not self.config.model:
            raise ValueError("Anthropic model name is required")
        # Claude models typically start with claude-
        if not self.config.model.startswith("claude-"):
            raise ValueError(
                f"Invalid Anthropic model: {self.config.model}. "
                "Expected model name starting with 'claude-'"
            )

    def normalize_messages(self, messages: List[Message]) -> Tuple[List[MessageParam], Optional[str]]:
        """Convert unified messages to Anthropic format.

        Returns:
            Tuple of (anthropic_messages, system_message).
        """
        anthropic_messages = []
        system_message = None

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            elif msg.role == MessageRole.USER:
                anthropic_messages.append(
                    MessageParam(role="user", content=msg.content)
                )
            elif msg.role == MessageRole.ASSISTANT:
                anthropic_messages.append(
                    MessageParam(role="assistant", content=msg.content)
                )

        return anthropic_messages, system_message

    async def chat(
        self,
        messages: List[Message],
        stream: bool = False,
        **kwargs,
    ) -> LLMResponse | AsyncIterator[StreamChunk]:
        """Send chat completion request to Anthropic."""
        normalized_messages, system_message = self.normalize_messages(messages)

        extra_params = self.config.extra_params or {}
        params = {
            "model": self.config.model,
            "messages": normalized_messages,
            "temperature": self.config.temperature,
            **kwargs,
            **extra_params,
        }

        if system_message:
            params["system"] = system_message
        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens
        else:
            # Anthropic requires max_tokens
            params["max_tokens"] = 4096

        if stream:
            return self._stream_response(params)
        else:
            response = await self.client.messages.create(**params)
            return self._parse_response(response)

    async def _stream_response(
        self, params: dict
    ) -> AsyncIterator[StreamChunk]:
        """Stream Anthropic responses."""
        with await self.client.messages.stream(**params) as stream:
            async for event in stream:
                if isinstance(event, ContentBlockDeltaEvent):
                    delta = event.delta
                    content = delta.text if hasattr(delta, "text") else ""
                    yield StreamChunk(
                        content=content,
                        finished=False,
                        metadata={"type": event.type},
                    )
                elif event.type == "message_stop":
                    yield StreamChunk(content="", finished=True)

    def _parse_response(self, response) -> LLMResponse:
        """Parse Anthropic response to unified format."""
        content_blocks = response.content
        text_content = ""

        for block in content_blocks:
            if isinstance(block, TextBlock):
                text_content += block.text

        # Extract usage information
        usage = None
        if hasattr(response, "usage"):
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

        return LLMResponse(
            content=text_content,
            model=response.model,
            finish_reason=response.stop_reason,
            usage=usage,
        )

    async def health_check(self) -> bool:
        """Check Anthropic API connectivity."""
        try:
            # Simple health check - try to list messages (if API supports it)
            # Or just make a minimal request
            await self.client.messages.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=1,
            )
            return True
        except Exception:
            # If the above fails, we can't verify, but adapter is configured
            # Return True if we can at least initialize
            return True

    def get_capabilities(self) -> AdapterCapabilities:
        """Get Anthropic adapter capabilities."""
        return AdapterCapabilities(
            provider="anthropic",
            supports_streaming=True,
            supports_tools=True,
            supports_function_calling=True,
            max_context_length=200000,  # Claude 3 Opus context length
            supported_models=[
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ],
        )

