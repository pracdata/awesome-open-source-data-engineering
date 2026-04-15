"""MCP (Model Context Protocol) server configuration types.

Aligned with modelcontextprotocol/sdk-python v2.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class McpScope(str, Enum):
    USER = "user"
    PROJECT = "project"
    LOCAL = "local"


class McpTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    HTTP = "http"
    SDK = "sdk"


class McpStdioConfig(BaseModel):
    """Stdio transport MCP server (most common)."""

    type: Literal["stdio"] | None = None
    command: str
    args: list[str] | None = None
    env: dict[str, str] | None = None
    cwd: str | None = None


class McpSSEConfig(BaseModel):
    """Server-Sent Events transport MCP server."""

    type: Literal["sse"]
    url: str
    headers: dict[str, str] | None = None


class McpHttpConfig(BaseModel):
    """HTTP Streamable transport MCP server."""

    type: Literal["http"]
    url: str
    headers: dict[str, str] | None = None


class McpSdkConfig(BaseModel):
    """In-process SDK MCP server."""

    type: Literal["sdk"]
    name: str
    instance: Any = None


McpServerConfig = McpStdioConfig | McpSSEConfig | McpHttpConfig | McpSdkConfig


class McpDotJson(BaseModel):
    """Schema for .mcp.json project-level MCP server configuration."""

    mcp_servers: dict[str, McpServerConfig] = Field(alias="mcpServers", default_factory=dict)


class McpToolInfo(BaseModel):
    """MCP tool metadata as returned by server discovery."""

    name: str
    description: str | None = None
    input_schema: dict[str, Any] | None = None


class McpServerStatus(BaseModel):
    """Runtime status of an MCP server connection."""

    name: str
    status: Literal["connected", "connecting", "disconnected", "error"]
    error: str | None = None
    scope: McpScope | None = None
    tools: list[McpToolInfo] | None = None


class McpCLICommands(BaseModel):
    """CLI commands for MCP server management."""

    add: str = "claude mcp add {name} -s {scope} -- {command} {args}"
    remove: str = "claude mcp remove {name} -s {scope}"
    list: str = "claude mcp list"
    config_flag: str = "claude --mcp-config {path}"
