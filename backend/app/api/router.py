"""API routes for chat and LLM operations."""

import os
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.core.adapter_factory import AdapterFactory
from app.core.schemas import Message, LLMResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat completion."""

    provider: str
    messages: list[Message]
    model: Optional[str] = None
    stream: bool = False


@router.post("/chat", response_model=LLMResponse)
async def chat_completion(request: ChatRequest):
    """Send a chat completion request.

    Args:
        request: Chat request containing provider, messages, model, and stream flag.

    Returns:
        LLMResponse or streaming response.
    """
    try:
        # Get API key from environment if available
        env_key = f"{request.provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        
        config = None
        if api_key:
            # Build provider-specific config
            config = {"api_key": api_key}
            if request.provider == "openai":
                config["base_url"] = "https://api.openai.com/v1"
                config["model"] = request.model or "gpt-4"
            elif request.provider == "anthropic":
                config["base_url"] = "https://api.anthropic.com"
                config["model"] = request.model or "claude-3-5-sonnet-20241022"
            elif request.provider == "gemini":
                config["base_url"] = "https://generativelanguage.googleapis.com/v1"
                config["model"] = request.model or "gemini-pro"
            elif request.provider == "ollama":
                config["base_url"] = "http://localhost:11434"
                config["model"] = request.model or "llama2"
                # Ollama doesn't need API key
        
        adapter = AdapterFactory.create(
            request.provider, config=config, model=request.model
        )

        if request.stream:
            # Return SSE stream
            async def generate():
                async for chunk in adapter.chat(request.messages, stream=True):
                    yield {
                        "data": chunk.model_dump_json(),
                    }
            return EventSourceResponse(generate())
        else:
            response = await adapter.chat(request.messages, stream=False)
            await adapter.close()
            return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/providers")
async def list_providers():
    """List all supported LLM providers."""
    providers = AdapterFactory.get_supported_providers()
    return {"providers": providers}


@router.get("/providers/{provider}/health")
async def provider_health(provider: str):
    """Check health of a specific provider."""
    try:
        adapter = AdapterFactory.create(provider)
        is_healthy = await adapter.health_check()
        capabilities = adapter.get_capabilities()
        await adapter.close()

        return {
            "provider": provider,
            "healthy": is_healthy,
            "capabilities": capabilities.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

