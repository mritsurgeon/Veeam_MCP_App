"""API routes for MCP server configuration."""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/settings/mcp", tags=["mcp"])


class MCPServerConfig(BaseModel):
    """MCP server configuration model."""

    name: str
    command: str
    args: List[str] = []
    env: Optional[Dict[str, str]] = None


def get_config_path() -> Path:
    """Get the path to the config file."""
    # Try project root config directory
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.yaml"
    if not config_path.exists():
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        # Create empty config file
        config_path.write_text(yaml.dump({"mcp_servers": {}}))
    return config_path


def load_config() -> Dict:
    """Load configuration from YAML file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return {"mcp_servers": {}}

    with open(config_path, "r") as f:
        config = yaml.safe_load(f) or {}
    
    if "mcp_servers" not in config:
        config["mcp_servers"] = {}
    
    return config


def save_config(config: Dict) -> None:
    """Save configuration to YAML file."""
    config_path = get_config_path()
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


@router.get("/servers", response_model=List[Dict])
async def list_mcp_servers():
    """List all configured MCP servers."""
    config = load_config()
    servers = config.get("mcp_servers", {})
    
    # Convert to list format
    result = []
    for name, server_config in servers.items():
        result.append({
            "name": name,
            "command": server_config.get("command", ""),
            "args": server_config.get("args", []),
            "env": server_config.get("env", {}),
        })
    
    return result


@router.post("/servers")
async def save_mcp_server(server: MCPServerConfig):
    """Save or update an MCP server configuration."""
    config = load_config()
    
    if "mcp_servers" not in config:
        config["mcp_servers"] = {}
    
    # Prepare server config
    server_config = {
        "command": server.command,
        "args": server.args,
    }
    
    if server.env:
        server_config["env"] = server.env
    
    # Save to config
    config["mcp_servers"][server.name] = server_config
    
    try:
        save_config(config)
        return {
            "message": f"MCP server '{server.name}' saved successfully",
            "server": server.dict(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")


@router.delete("/servers/{server_name}")
async def delete_mcp_server(server_name: str):
    """Delete an MCP server configuration."""
    config = load_config()
    
    if "mcp_servers" not in config:
        config["mcp_servers"] = {}
    
    if server_name not in config["mcp_servers"]:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    # Remove server
    del config["mcp_servers"][server_name]
    
    try:
        save_config(config)
        return {"message": f"MCP server '{server_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save config: {str(e)}")


@router.get("/servers/{server_name}")
async def get_mcp_server(server_name: str):
    """Get a specific MCP server configuration."""
    config = load_config()
    
    if "mcp_servers" not in config:
        config["mcp_servers"] = {}
    
    if server_name not in config["mcp_servers"]:
        raise HTTPException(status_code=404, detail=f"MCP server '{server_name}' not found")
    
    server_config = config["mcp_servers"][server_name]
    
    return {
        "name": server_name,
        "command": server_config.get("command", ""),
        "args": server_config.get("args", []),
        "env": server_config.get("env", {}),
    }

