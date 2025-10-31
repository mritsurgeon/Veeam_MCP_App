"""Configuration management for the application."""

import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Veeam MCP Chat Client"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")


def load_config(config_path: Optional[str] = None) -> Dict:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. Defaults to config/config.yaml.

    Returns:
        Dictionary containing configuration.
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"

    config_path = Path(config_path)

    if not config_path.exists():
        # Return default config structure
        return {
            "llm_providers": {},
            "mcp_servers": {},
        }

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}

    # Expand environment variables in config
    config_str = yaml.dump(config)
    config_str = os.path.expandvars(config_str)
    config = yaml.safe_load(config_str)

    return config


def get_llm_config(provider: str, config: Optional[Dict] = None) -> Dict:
    """Get LLM provider configuration.

    Args:
        provider: Provider name (e.g., 'openai', 'anthropic', 'ollama').
        config: Full config dict. If None, loads from file.

    Returns:
        Dictionary with provider configuration.
    """
    if config is None:
        config = load_config()

    providers = config.get("llm_providers", {})
    provider_config = providers.get(provider, {})

    # Fill in defaults
    defaults = {
        "base_url": {
            "openai": "https://api.openai.com/v1",
            "anthropic": "https://api.anthropic.com",
            "ollama": "http://localhost:11434",
        }.get(provider, ""),
        "timeout": 30,
        "temperature": 0.7,
    }

    return {**defaults, **provider_config}


settings = Settings()

