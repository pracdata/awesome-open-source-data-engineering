"""Model Context Protocol (MCP) server and tool models — targeting MCP SDK v2."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "MCPTransport",
    "MCPServerConfig",
    "MCPToolAnnotations",
    "MCPToolDefinition",
    "MCPToolResult",
    "MCPResource",
    "MCPConfig",
]


class MCPTransport(BaseModel):
    """MCP server transport configuration."""

    model_config = ConfigDict(str_strip_whitespace=True)

    type: str = Field(default="stdio", description="'stdio', 'sse', or 'streamable-http'")


class MCPServerConfig(BaseModel):
    """MCP server configuration (as in .mcp.json or settings.json mcpServers)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    command: str | None = Field(default=None, description="Command to execute for stdio transport")
    args: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    cwd: str | None = None
    url: str | None = Field(default=None, description="URL for HTTP/SSE transport")
    headers: dict[str, str] = Field(default_factory=dict, description="Headers for HTTP transport")
    type: str | None = Field(default=None, description="Transport type override")


class MCPToolAnnotations(BaseModel):
    """MCP tool annotations (MCP SDK v2)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    read_only_hint: bool | None = Field(default=None, alias="readOnlyHint")
    destructive_hint: bool | None = Field(default=None, alias="destructiveHint")
    idempotent_hint: bool | None = Field(default=None, alias="idempotentHint")
    open_world_hint: bool | None = Field(default=None, alias="openWorldHint")
    title: str | None = None


class MCPToolDefinition(BaseModel):
    """An MCP tool definition as registered by a server."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    description: str | None = None
    input_schema: dict[str, Any] = Field(default_factory=dict)
    annotations: MCPToolAnnotations | None = None
    server_name: str | None = Field(default=None, description="Prefixed as mcp__{server}__{name}")


class MCPToolResult(BaseModel):
    """Result returned by an MCP tool call."""

    model_config = ConfigDict(str_strip_whitespace=True)

    content: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Array of {type, text} or {type, data, mimeType} blocks",
    )
    is_error: bool = False


class MCPResource(BaseModel):
    """An MCP resource exposed by a server."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = Field(default=None, alias="mimeType")


class MCPConfig(BaseModel):
    """Full MCP configuration (.mcp.json or settings.json mcpServers section)."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    mcp_servers: dict[str, MCPServerConfig] = Field(default_factory=dict, alias="mcpServers")
