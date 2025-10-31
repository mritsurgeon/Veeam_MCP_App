"""Core schemas for messages and responses across all LLM adapters."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message role types for LLM conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """Unified message schema for all LLM providers."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    class Config:
        """Pydantic config."""

        use_enum_values = True


class StreamChunk(BaseModel):
    """Chunk of streaming response."""

    content: str
    finished: bool = False
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """Unified response schema from LLM adapters."""

    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        """Pydantic config."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""

    provider: str
    api_key: Optional[str] = None
    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    extra_params: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic config."""

        extra = "allow"


class AdapterCapabilities(BaseModel):
    """Capabilities of an LLM adapter."""

    provider: str
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_function_calling: bool = False
    max_context_length: Optional[int] = None
    supported_models: List[str] = []

