"""API routes for settings and API key management."""

import os
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.adapter_factory import AdapterFactory

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


class APIKeyRequest(BaseModel):
    """Request model for API key operations."""

    provider: str
    api_key: str


class APIKeyResponse(BaseModel):
    """Response model for API key operations."""

    provider: str
    configured: bool
    message: str


class ProviderStatus(BaseModel):
    """Provider status information."""

    provider: str
    configured: bool
    healthy: bool
    available_models: list[str] = []
    error: Optional[str] = None


@router.post("/api-keys", response_model=APIKeyResponse)
async def set_api_key(request: APIKeyRequest):
    """Set API key for a provider.

    In a production app, this would store securely (e.g., encrypted database).
    For now, we'll set it in environment for this session.
    """
    if request.provider not in AdapterFactory.get_supported_providers():
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {request.provider}")

    # Set in environment (session-only)
    env_key = f"{request.provider.upper()}_API_KEY"
    os.environ[env_key] = request.api_key

    return APIKeyResponse(
        provider=request.provider,
        configured=True,
        message=f"API key configured for {request.provider}",
    )


@router.get("/api-keys/{provider}", response_model=Dict[str, bool])
async def check_api_key(provider: str):
    """Check if API key is configured for a provider."""
    if provider not in AdapterFactory.get_supported_providers():
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    env_key = f"{provider.upper()}_API_KEY"
    api_key = os.getenv(env_key)

    return {"configured": api_key is not None and api_key != ""}


@router.get("/providers/status", response_model=list[ProviderStatus])
async def get_providers_status():
    """Get status of all providers (configured, healthy, available models)."""
    providers = AdapterFactory.get_supported_providers()
    statuses = []

    for provider in providers:
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        configured = api_key is not None and api_key != ""

        healthy = False
        available_models = []
        error = None

        if configured:
            try:
                # Try to create adapter and check health
                config = {
                    "api_key": api_key,
                    "model": "default",  # Temporary model
                    "base_url": "",
                }

                # Set appropriate defaults
                if provider == "openai":
                    config["model"] = "gpt-4"
                    config["base_url"] = "https://api.openai.com/v1"
                elif provider == "anthropic":
                    config["model"] = "claude-3-5-sonnet-20241022"
                    config["base_url"] = "https://api.anthropic.com"
                elif provider == "gemini":
                    config["model"] = "gemini-pro"
                    config["base_url"] = "https://generativelanguage.googleapis.com/v1"
                elif provider == "ollama":
                    config["model"] = "llama2"
                    config["base_url"] = "http://localhost:11434"
                    # Ollama doesn't need API key
                    configured = True

                adapter = AdapterFactory.create(provider, config=config)
                healthy = await adapter.health_check()

                # Get available models
                capabilities = adapter.get_capabilities()
                available_models = capabilities.supported_models

                # Some adapters can list models dynamically
                if hasattr(adapter, "list_models"):
                    try:
                        dynamic_models = await adapter.list_models()
                        if dynamic_models:
                            available_models = dynamic_models
                    except Exception:
                        pass

                await adapter.close()

            except Exception as e:
                error = str(e)
                healthy = False

        statuses.append(
            ProviderStatus(
                provider=provider,
                configured=configured,
                healthy=healthy,
                available_models=available_models,
                error=error,
            )
        )

    return statuses


@router.delete("/api-keys/{provider}")
async def delete_api_key(provider: str):
    """Delete API key for a provider."""
    if provider not in AdapterFactory.get_supported_providers():
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    env_key = f"{provider.upper()}_API_KEY"
    if env_key in os.environ:
        del os.environ[env_key]

    return {"message": f"API key removed for {provider}"}

