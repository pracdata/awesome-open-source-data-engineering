"""Plugin manifest and component types for Claude Code plugins."""

from __future__ import annotations

from typing import Any

from pydantic import Field

from agentwarehouses.models.base import BaseModel


class PluginAuthor(BaseModel):
    name: str
    email: str | None = None
    url: str | None = None


class UserConfigField(BaseModel):
    description: str
    sensitive: bool = False


class ChannelDeclaration(BaseModel):
    server: str
    user_config: dict[str, UserConfigField] | None = Field(None, alias="userConfig")


class PluginManifest(BaseModel):
    """Complete plugin.json manifest schema."""

    name: str
    version: str | None = None
    description: str | None = None
    author: PluginAuthor | None = None
    homepage: str | None = None
    repository: str | None = None
    license: str | None = None
    keywords: list[str] | None = None
    skills: str | list[str] | None = None
    commands: str | list[str] | None = None
    agents: str | list[str] | None = None
    hooks: str | list[str] | dict[str, Any] | None = None
    mcp_servers: str | list[str] | dict[str, Any] | None = Field(None, alias="mcpServers")
    output_styles: str | list[str] | None = Field(None, alias="outputStyles")
    lsp_servers: str | list[str] | dict[str, Any] | None = Field(None, alias="lspServers")
    user_config: dict[str, UserConfigField] | None = Field(None, alias="userConfig")
    monitors: str | list[str] | dict[str, Any] | None = None
    channels: list[ChannelDeclaration] | None = None


class LSPServer(BaseModel):
    """LSP server configuration in .lsp.json."""

    command: str
    args: list[str] | None = None
    extension_to_language: dict[str, str] = Field(alias="extensionToLanguage")
    transport: str | None = None
    env: dict[str, str] | None = None
    initialization_options: dict[str, Any] | None = Field(None, alias="initializationOptions")
    settings: dict[str, Any] | None = None
    startup_timeout: int | None = Field(None, alias="startupTimeout")
    shutdown_timeout: int | None = Field(None, alias="shutdownTimeout")
    restart_on_crash: bool | None = Field(None, alias="restartOnCrash")
    max_restarts: int | None = Field(None, alias="maxRestarts")


class PluginDirectory(BaseModel):
    """Represents a plugin's directory structure."""

    name: str
    manifest_path: str = ".claude-plugin/plugin.json"
    skills_dir: str | None = "skills/"
    commands_dir: str | None = "commands/"
    agents_dir: str | None = "agents/"
    hooks_file: str | None = "hooks/hooks.json"
    mcp_file: str | None = ".mcp.json"
    lsp_file: str | None = ".lsp.json"
    bin_dir: str | None = "bin/"
    settings_file: str | None = "settings.json"
