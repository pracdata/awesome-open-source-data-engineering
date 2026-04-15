"""Claude Code plugin system models: manifest, components, marketplace."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "PluginScope",
    "PluginAuthor",
    "PluginUserConfigEntry",
    "PluginChannelDeclaration",
    "PluginManifest",
    "LSPServerConfig",
    "PluginInstallation",
    "MarketplaceEntry",
    "MarketplaceConfig",
]


class PluginScope(StrEnum):
    USER = "user"
    PROJECT = "project"
    LOCAL = "local"
    MANAGED = "managed"


class PluginAuthor(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    email: str | None = None
    url: str | None = None


class PluginUserConfigEntry(BaseModel):
    """A user-configurable value prompted at plugin enable time."""

    model_config = ConfigDict(str_strip_whitespace=True)

    description: str
    sensitive: bool = False


class PluginChannelDeclaration(BaseModel):
    """Channel declaration in a plugin manifest."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    server: str = Field(description="Must match a key in the plugin's mcpServers")
    user_config: dict[str, PluginUserConfigEntry] | None = Field(default=None, alias="userConfig")


class PluginManifest(BaseModel):
    """plugin.json schema — the .claude-plugin/plugin.json file."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True, extra="allow")

    name: str = Field(description="Unique identifier (kebab-case)")
    version: str | None = None
    description: str | None = None
    author: PluginAuthor | None = None
    homepage: str | None = None
    repository: str | None = None
    license: str | None = None
    keywords: list[str] = Field(default_factory=list)

    # Component paths (relative to plugin root, start with './')
    skills: str | list[str] | None = None
    commands: str | list[str] | None = None
    agents: str | list[str] | None = None
    hooks: str | list[str] | dict | None = None
    mcp_servers: str | list[str] | dict | None = Field(default=None, alias="mcpServers")
    output_styles: str | list[str] | None = Field(default=None, alias="outputStyles")
    lsp_servers: str | list[str] | dict | None = Field(default=None, alias="lspServers")

    user_config: dict[str, PluginUserConfigEntry] | None = Field(default=None, alias="userConfig")
    channels: list[PluginChannelDeclaration] | None = None


class LSPServerConfig(BaseModel):
    """Language Server Protocol server configuration."""

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    command: str = Field(description="LSP binary to execute")
    args: list[str] = Field(default_factory=list)
    extension_to_language: dict[str, str] = Field(alias="extensionToLanguage")
    transport: str | None = Field(default=None, description="'stdio' (default) or 'socket'")
    env: dict[str, str] = Field(default_factory=dict)
    initialization_options: dict | None = Field(default=None, alias="initializationOptions")
    settings: dict | None = None
    workspace_folder: str | None = Field(default=None, alias="workspaceFolder")
    startup_timeout: int | None = Field(default=None, alias="startupTimeout")
    shutdown_timeout: int | None = Field(default=None, alias="shutdownTimeout")
    restart_on_crash: bool | None = Field(default=None, alias="restartOnCrash")
    max_restarts: int | None = Field(default=None, alias="maxRestarts")


class PluginInstallation(BaseModel):
    """Record of an installed plugin."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    marketplace: str | None = None
    scope: PluginScope = PluginScope.USER
    version: str | None = None
    enabled: bool = True
    path: str | None = Field(default=None, description="Cache path")


class MarketplaceEntry(BaseModel):
    """An entry in marketplace.json."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    source: str = Field(description="Path to plugin directory relative to marketplace root")
    version: str | None = None
    description: str | None = None
    keywords: list[str] = Field(default_factory=list)


class MarketplaceConfig(BaseModel):
    """marketplace.json schema."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    description: str | None = None
    plugins: list[MarketplaceEntry] = Field(default_factory=list)
